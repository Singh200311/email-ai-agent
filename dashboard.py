import streamlit as st
import pandas as pd
from pymongo import MongoClient
from streamlit_autorefresh import st_autorefresh
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["email_agent"]
collection = db["emails"]

st.set_page_config(page_title="Email AI Agent Dashboard", layout="wide")
st.title("📧 Email AI Agent Dashboard")

# Refresh every 3 seconds
st_autorefresh(interval=3000, key="refresh")

st.caption("Database: MongoDB Atlas")

def load_data():
    emails = list(collection.find({}, {"_id": 0}))
    df = pd.DataFrame(emails)

    if not df.empty:
        df = df.sort_values(by="processed_at", ascending=False)

    return df

df = load_data()

# Ensure confidence column exists
if not df.empty and "confidence" not in df.columns:
    df["confidence"] = 1.0

# ---------- STATS ----------
if not df.empty:
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Emails", len(df))
    col2.metric("Urgent", len(df[df["category"] == "Urgent"]))
    col3.metric("Meetings", len(df[df["category"] == "Meeting"]))
    col4.metric("Finance", len(df[df["category"] == "Finance"]))
    col5.metric("Low Confidence", len(df[df["confidence"] < 0.7]))

st.divider()

# ---------- MAIN TABLE ----------
if df.empty:
    st.warning("No emails processed yet.")
else:

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📬 Processed Emails")

        def highlight_confidence(row):
            return [
                "background-color: #ffcccc" if row["confidence"] < 0.7 else ""
                for _ in row
            ]

        st.dataframe(
            df.style.apply(highlight_confidence, axis=1),
            use_container_width=True
        )

    with col2:
        st.subheader("📊 Category Distribution")
        chart = df["category"].value_counts()
        st.bar_chart(chart)

    st.subheader("📊 Confidence Distribution")
    st.bar_chart(df["confidence"])