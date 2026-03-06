<<<<<<< HEAD
# AI Email Agent

LangGraph AI agent that reads Gmail, analyzes emails, and shows insights in a Streamlit dashboard.
=======
# email-ai-agent
>>>>>>> b484380ba3de1fefd4e3e61a9c94895e4544069a
# Email AI Agent

## Description

This project is an **Email AI Agent** that:

* Automatically reads your unread Gmail messages.
* Classifies emails into categories: `Urgent`, `Meeting`, `Finance`, `Personal`, `Low Priority`.
* Summarizes emails and assigns a **confidence score** (0-1).
* Sends notifications to Slack for urgent emails.
* Extracts meeting info and creates events in Google Calendar.
* Saves all processed emails in a local SQLite database (`email_memory.db`).

The project also includes a **Streamlit dashboard** to visualize processed emails, category distribution, and confidence scores.

---

## Features

* **Structured JSON validation** for email classification.
* **Few-shot prompting** for consistent AI predictions.
* **Confidence scoring** with fallbacks for errors.
* Integration with **Slack** and **Google Calendar**.
* **Persistent storage** using SQLite.
* **Real-time dashboard** using Streamlit.

---

## Prerequisites

1. Python 3.10+ installed.
2. A Gmail account with API access.
3. Google Cloud project with `credentials.json` for Gmail and Calendar API.
4. Slack webhook URL (optional, for notifications).
5. OpenAI API key.

---

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd <repo-folder>
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

> **requirements.txt** should include:

```
openai
python-dotenv
google-api-python-client
google-auth
google-auth-oauthlib
pydantic
requests
langgraph
streamlit
streamlit-autorefresh
```

4. Create a `.env` file in the root folder:

```text
OPENAI_API_KEY=your_openai_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url (optional)
```

5. Add `credentials.json` from Google Cloud in the root folder.

---

## Running the Agent Locally

1. Initialize the database (optional, agent auto-creates it):

```bash
python agent.py
```

2. The agent will start reading unread Gmail messages every 30 seconds.
3. Processed emails are saved in `email_memory.db`.
4. Slack notifications and calendar events are triggered based on email category.

> Note: The agent will create `token.json` on first run for Google API authentication.

---

## Running the Dashboard Locally

1. Start the Streamlit dashboard:

```bash
streamlit run dashboard.py
```

2. Open the local URL provided by Streamlit (usually `http://localhost:8501`).
3. The dashboard shows:

   * Total emails processed
   * Emails by category
   * Confidence distribution
   * Table of processed emails

---

## Important Notes

* **Do not commit** `.env` or `credentials.json` to GitHub.
* Ensure Gmail API and Calendar API are enabled in your Google Cloud project.
* Slack notifications require a valid webhook URL.
* Free hosting options for continuous running include **Replit** for the agent and **Streamlit Cloud** for the dashboard.

---

## License

MIT License
