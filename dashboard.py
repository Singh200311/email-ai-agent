import streamlit as st
import sqlite3
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import os

DB_FILE = "email_memory.db"

st.set_page_config(page_title="Email AI Agent Dashboard", layout="wide")
st.title("📧 Email AI Agent Dashboard")

# Refresh every 3 seconds
st_autorefresh(interval=3000, key="refresh")

# Show DB path
st.caption(f"Database file: {os.path.abspath(DB_FILE)}")

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM emails ORDER BY processed_at DESC", conn)
    conn.close()
    return df

df = load_data()

# Ensure confidence column exists
if "confidence" not in df.columns:
    df["confidence"] = 1.0  # default for older rows

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
            return ["background-color: #ffcccc" if row["confidence"] < 0.7 else "" for _ in row]
        st.dataframe(df.style.apply(highlight_confidence, axis=1), use_container_width=True)

    with col2:
        st.subheader("📊 Category Distribution")
        chart = df["category"].value_counts()
        st.bar_chart(chart)

    st.subheader("📊 Confidence Distribution")
    st.bar_chart(df["confidence"])