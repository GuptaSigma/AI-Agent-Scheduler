import streamlit as st
from datetime import datetime
import pytz
import re

st.set_page_config(page_title="AI Meeting Scheduler", layout="centered")
st.title("🤖 AI Agent Scheduler – Natural Input Based")

def parse_availability(text):
    text = text.lower()
    if "after lunch" in text:
        return "13:00", "18:00"
    match = re.findall(r'(\d{1,2})\s*(am|pm)?\s*(to|-)\s*(\d{1,2})\s*(am|pm)?', text)
    if match:
        h1, p1, _, h2, p2 = match[0]
        h1, h2 = int(h1), int(h2)
        if p1 == "pm" and h1 != 12: h1 += 12
        if p2 == "pm" and h2 != 12: h2 += 12
        return f"{h1:02d}:00", f"{h2:02d}:00"
    return "09:00", "17:00"

timezones = ["Asia/Kolkata", "Europe/Berlin", "America/New_York"]

users = []
for i in range(3):
    st.subheader(f"User {i+1}")
    tz = st.selectbox(f"Timezone {i+1}", timezones, key=f"tz{i}")
    text = st.text_input(f"Availability (e.g., 'after lunch', '10am to 3pm')", key=f"text{i}")
    if text:
        s, e = parse_availability(text)
        users.append({"timezone": tz, "start": s, "end": e})

def to_utc(time_str, tz):
    naive = datetime.strptime(time_str, "%H:%M")
    local = pytz.timezone(tz).localize(datetime.combine(datetime.now().date(), naive.time()))
    return local.astimezone(pytz.utc)

if st.button("Find Common Time") and len(users) == 3:
    try:
        starts = [to_utc(u["start"], u["timezone"]) for u in users]
        ends = [to_utc(u["end"], u["timezone"]) for u in users]
        latest = max(starts)
        earliest = min(ends)
        if latest < earliest:
            st.success(f"✅ Common Meeting Time in UTC: {latest.strftime('%H:%M')} – {earliest.strftime('%H:%M')}")
        else:
            st.warning("❌ No exact overlap found. Try changing inputs.")
    except Exception as e:
        st.error("Error: " + str(e))
