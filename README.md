# AI Email Agent

An intelligent **AI-powered email assistant** that reads Gmail messages, analyzes them using an LLM, and provides insights through a real-time dashboard.

---

# Overview

The **AI Email Agent** automatically processes unread Gmail messages and performs the following tasks:

* Classifies emails into categories:

  * `Urgent`
  * `Meeting`
  * `Finance`
  * `Personal`
  * `Low Priority`
* Generates a concise **AI summary** of each email.
* Assigns a **confidence score (0–1)** to the classification.
* Sends **Slack notifications** for urgent emails.
* Extracts meeting details and creates **Google Calendar events**.
* Stores processed emails in **MongoDB Atlas**.
* Displays insights through a **Streamlit dashboard**.

---

# Architecture

Gmail API
↓
AI Agent (LangGraph + OpenAI)
↓
MongoDB Atlas (Email Memory)
↓
Streamlit Dashboard (Analytics)

---

# Features

* AI-powered **email classification**
* **Structured JSON validation** using Pydantic
* **Few-shot prompting** for consistent predictions
* **Confidence scoring** with fallback handling
* **Slack notifications** for urgent emails
* **Automatic Google Calendar event creation**
* **MongoDB Atlas database for persistent storage**
* **Real-time Streamlit dashboard**

---

# Tech Stack

* Python
* OpenAI API
* LangGraph
* Gmail API
* Google Calendar API
* MongoDB Atlas
* Streamlit
* Slack Webhooks

---

# Project Structure

```
email-ai-agent
│
├── agent.py              # Main AI email processing agent
├── dashboard.py          # Streamlit analytics dashboard
├── db.py                 # MongoDB database connection
├── requirements.txt
├── README.md
│
├── .env                  # Environment variables (not committed)
├── credentials.json      # Google API credentials (not committed)
├── token.json            # OAuth token (auto-generated)
│
├── venv/
└── __pycache__/
```

---

# Prerequisites

* Python **3.10+**
* Gmail account
* Google Cloud project with Gmail API enabled
* Google Calendar API enabled
* MongoDB Atlas database
* OpenAI API key
* Slack webhook URL (optional)

---

# Installation

### 1 Clone the repository

```
git clone <your-repo-url>
cd email-ai-agent
```

### 2 Create virtual environment

```
python -m venv venv
source venv/bin/activate
```

Windows:

```
venv\Scripts\activate
```

---

### 3 Install dependencies

```
pip install -r requirements.txt
```

---

### 4 Create `.env` file

```
OPENAI_API_KEY=your_openai_api_key
MONGO_URI=your_mongodb_connection_string
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

---

### 5 Add Google credentials

Download `credentials.json` from **Google Cloud Console** and place it in the root folder.

---

# Running the AI Agent

Start the email processing agent:

```
python agent.py
```

The agent will:

* Fetch unread Gmail messages
* Analyze them using the AI model
* Save results to MongoDB
* Send Slack alerts for urgent emails
* Create calendar events for meeting emails

---

# Running the Dashboard

Start the Streamlit dashboard:

```
streamlit run dashboard.py
```

Open the dashboard:

```
http://localhost:8501
```

The dashboard shows:

* Total emails processed
* Category distribution
* Confidence score distribution
* Processed email table

---

# Security Notes

Do **NOT commit** the following files:

```
.env
credentials.json
token.json
```

These contain sensitive credentials.

---

# Future Improvements

* Email reply automation
* Email sentiment analysis
* Priority prediction
* Multi-user email agents
* Cloud deployment (AWS / GCP)

---

# License

MIT License
