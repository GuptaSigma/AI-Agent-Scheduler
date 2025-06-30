from datetime import datetime
import pytz
import re

# Step 1: LLM-style natural input parser
def parse_availability(natural_input):
    natural_input = natural_input.lower()
    time_pattern = re.findall(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', natural_input)
    
    if "after lunch" in natural_input:
        return "13:00", "18:00"
    elif "after" in natural_input:
        match = re.search(r'after (\d{1,2}) ?(am|pm)', natural_input)
        if match:
            hour = int(match.group(1))
            period = match.group(2)
            if period == "pm" and hour != 12:
                hour += 12
            return f"{hour:02d}:00", "18:00"
    elif "free till" in natural_input or "free until" in natural_input:
        match = re.search(r'(till|until) (\d{1,2}) ?(am|pm)', natural_input)
        if match:
            hour = int(match.group(2))
            period = match.group(3)
            if period == "pm" and hour != 12:
                hour += 12
            return "08:00", f"{hour:02d}:00"
    elif len(time_pattern) == 2:
        start_hour = int(time_pattern[0][0])
        end_hour = int(time_pattern[1][0])
        if time_pattern[0][2] == "pm" and start_hour != 12:
            start_hour += 12
        if time_pattern[1][2] == "pm" and end_hour != 12:
            end_hour += 12
        return f"{start_hour:02d}:00", f"{end_hour:02d}:00"
    return "09:00", "17:00"

# Step 2: Time conversion and scheduler
def to_utc(time_str, tz_str):
    local = pytz.timezone(tz_str)
    naive_time = datetime.strptime(time_str, "%H:%M")
    today = datetime.now()
    local_dt = local.localize(datetime.combine(today.date(), naive_time.time()))
    return local_dt.astimezone(pytz.utc)

def find_common_slot(users):
    utc_ranges = []
    for user in users:
        start, end = parse_availability(user["input"])
        start_utc = to_utc(start, user["timezone"])
        end_utc = to_utc(end, user["timezone"])
        utc_ranges.append((start_utc, end_utc))

    latest_start = max([r[0] for r in utc_ranges])
    earliest_end = min([r[1] for r in utc_ranges])

    if latest_start < earliest_end:
        return latest_start, earliest_end
    else:
        return None, None

# Step 3: Define users with natural input + timezone
users = [
    {"name": "User1", "timezone": "Asia/Kolkata", "input": "Available 3pm to 8pm"},
    {"name": "User2", "timezone": "Europe/Berlin", "input": "Available 12pm to 6pm"},
    {"name": "User3", "timezone": "America/New_York", "input": "Free after 8am"}
]



# Run scheduler
start, end = find_common_slot(users)
if start:
    print(f"✅ Common Meeting Time in UTC: {start.strftime('%H:%M')} – {end.strftime('%H:%M')}")
else:
    print("❌ No common meeting time found.")
