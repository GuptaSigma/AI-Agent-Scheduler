from datetime import datetime, timedelta
import pytz

def suggest_possible_times(user_times):
    """
    Suggests the nearest possible overlap window between users even if no exact overlap found.
    """
    windows = []
    for user in user_times:
        tz = pytz.timezone(user['timezone'])
        start = datetime.strptime(user['start'], "%H:%M")
        end = datetime.strptime(user['end'], "%H:%M")
        start_utc = tz.localize(datetime.combine(datetime.now().date(), start.time())).astimezone(pytz.utc)
        end_utc = tz.localize(datetime.combine(datetime.now().date(), end.time())).astimezone(pytz.utc)
        windows.append((start_utc, end_utc))
    
    max_start = max([w[0] for w in windows])
    min_end = min([w[1] for w in windows])

    if max_start >= min_end:
        suggestion_start = max_start
        suggestion_end = suggestion_start + timedelta(minutes=30)
        return f"❗ No perfect overlap. Nearest available suggestion:\n🕒 {suggestion_start.strftime('%H:%M')} – {suggestion_end.strftime('%H:%M')} UTC"
    else:
        return f"✅ Common Time Available: {max_start.strftime('%H:%M')} – {min_end.strftime('%H:%M')} UTC"
