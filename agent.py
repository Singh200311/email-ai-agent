import os
import base64
import time
import sqlite3
import requests
import json
from typing import TypedDict
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field, ValidationError

# ----------------------
# LOAD ENV
# ----------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=180)
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar"
]

TOKEN_PATH = "token.json"
DB_FILE = "email_memory.db"

# ----------------------
# STATE
# ----------------------
class EmailState(TypedDict):
    msg_id: str
    email_text: str
    category: str
    summary: str
    confidence: float

# ----------------------
# Pydantic schema for validation
# ----------------------
class EmailAnalysis(BaseModel):
    category: str = Field(..., regex="^(Urgent|Meeting|Finance|Personal|Low Priority)$")
    summary: str
    confidence: float = Field(..., ge=0.0, le=1.0)

# ----------------------
# DATABASE
# ----------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            category TEXT,
            summary TEXT,
            confidence REAL DEFAULT 1.0,
            processed_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def already_processed(msg_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM emails WHERE id=?", (msg_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_to_memory(state: EmailState):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    ist_time = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT OR IGNORE INTO emails
        (id, category, summary, confidence, processed_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        state["msg_id"],
        state["category"],
        state["summary"],
        state.get("confidence", 1.0),
        ist_time
    ))
    conn.commit()
    conn.close()
    return state

# ----------------------
# SLACK
# ----------------------
def slack_node(state: EmailState):
    if not SLACK_WEBHOOK:
        return state
    try:
        text = f"{state['category']} EMAIL\nConfidence: {state['confidence']:.2f}\n\n{state['summary']}"
        requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
    except Exception as e:
        print("Slack error:", e)
    return state

# ----------------------
# OPENAI ANALYSIS
# ----------------------
def analyze_node(state: EmailState):
    try:
        # Few-shot examples for more consistent classification
        system_prompt = """
You are an AI email assistant. Classify emails into: Urgent, Meeting, Finance, Personal, Low Priority.
Return ONLY JSON in this format:
{
  "category": "<category>",
  "summary": "<summary>",
  "confidence": 0-1
}

Example 1:
Email: "Server is down! Need immediate attention!"
Output: {"category": "Urgent", "summary": "Server outage requires immediate action", "confidence": 0.95}

Example 2:
Email: "Let's schedule a call on Thursday to discuss Q2 targets."
Output: {"category": "Meeting", "summary": "Schedule Q2 targets call on Thursday", "confidence": 0.9}

Example 3:
Email: "Please find attached the invoice for last month."
Output: {"category": "Finance", "summary": "Attached invoice for last month", "confidence": 0.9}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": state["email_text"]}
            ]
        )

        raw_result = response.choices[0].message.content.strip()
        data = json.loads(raw_result)
        analysis = EmailAnalysis(**data)

        state["category"] = analysis.category
        state["summary"] = analysis.summary
        state["confidence"] = analysis.confidence

    except (json.JSONDecodeError, ValidationError) as ve:
        print("Validation error:", ve)
        state["category"] = "Low Priority"
        state["summary"] = state["email_text"][:100] + "..."
        state["confidence"] = 0.5

    except Exception as e:
        print("OpenAI error:", e)
        state["category"] = "Low Priority"
        state["summary"] = "AI processing failed."
        state["confidence"] = 0.0

    return state

# ----------------------
# CALENDAR
# ----------------------
def calendar_node(state: EmailState):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
Extract meeting info.
Format:
Title: <title>
Date: <YYYY-MM-DD>
Start Time: <HH:MM>
Duration Minutes: <number>
"""
                },
                {"role": "user", "content": state["email_text"]}
            ]
        )
        result = response.choices[0].message.content
        data = {}
        for line in result.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()

        title = data.get("Title")
        date_str = data.get("Date")
        time_str = data.get("Start Time")
        duration = int(data.get("Duration Minutes", "60"))

        if title and date_str and time_str:
            ist = ZoneInfo("Asia/Kolkata")
            start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=ist)
            end_dt = start_dt + timedelta(minutes=duration)
            event = {"summary": title, "start": {"dateTime": start_dt.isoformat()}, "end": {"dateTime": end_dt.isoformat()}}
            calendar_service.events().insert(calendarId="primary", body=event).execute()
            print("Calendar event created")
    except Exception as e:
        print("Calendar error:", e)

    return state

# ----------------------
# ROUTER
# ----------------------
def route_decision(state: EmailState):
    return state["category"]

# ----------------------
# GOOGLE AUTH
# ----------------------
def authenticate_google():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    gmail_service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    calendar_service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    return gmail_service, calendar_service

# ----------------------
# EMAIL BODY
# ----------------------
def extract_email_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode(errors="ignore")
    else:
        data = payload["body"].get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode(errors="ignore")
    return ""

# ----------------------
# LANGGRAPH
# ----------------------
builder = StateGraph(EmailState)
builder.add_node("analyze", analyze_node)
builder.add_node("slack", slack_node)
builder.add_node("calendar", calendar_node)
builder.add_node("save", save_to_memory)
builder.set_entry_point("analyze")

builder.add_conditional_edges(
    "analyze",
    route_decision,
    {
        "Urgent": "slack",
        "Meeting": "calendar",
        "Finance": "save",
        "Personal": "save",
        "Low Priority": "save",
    }
)

builder.add_edge("slack", "save")
builder.add_edge("calendar", "slack")
builder.add_edge("save", END)
graph = builder.compile()

# ----------------------
# GMAIL RETRY HELPER
# ----------------------
def gmail_request_with_retry(func, *args, retries=5, initial_delay=2, **kwargs):
    delay = initial_delay
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[WARN] Gmail request failed attempt {attempt+1}: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
    raise Exception("Gmail request failed after multiple retries")

# ----------------------
# MAIN LOOP
# ----------------------
if __name__ == "__main__":
    print("🚀 LangGraph Email Agent Started")

    init_db()
    gmail_service, calendar_service = authenticate_google()

    while True:
        try:
            results = gmail_request_with_retry(
                gmail_service.users().messages().list,
                userId="me",
                q="is:unread",
                maxResults=5
            ).execute()

            messages = results.get("messages", [])

            if not messages:
                print("No new emails")
                time.sleep(30)
                continue

            for msg in messages:
                msg_id = msg["id"]

                if already_processed(msg_id):
                    continue

                msg_data = gmail_request_with_retry(
                    gmail_service.users().messages().get,
                    userId="me",
                    id=msg_id,
                    format="full"
                ).execute()

                email_body = extract_email_body(msg_data["payload"])

                state = {
                    "msg_id": msg_id,
                    "email_text": email_body,
                    "category": "",
                    "summary": "",
                    "confidence": 0.0
                }

                graph.invoke(state)

                gmail_request_with_retry(
                    gmail_service.users().messages().modify,
                    userId="me",
                    id=msg_id,
                    body={"removeLabelIds": ["UNREAD"]}
                )

            time.sleep(30)

        except Exception as e:
            print("[ERROR] Main loop error:", e)
            time.sleep(20)