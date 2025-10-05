import re, requests

# Fetch your ADE ICS link
url = "https://ade-outils.insa-lyon.fr/ADE-Cal:~ftristant!2025-2026:84f15375bd1e1cd3910ee7278886e3be132a51fe"
ics = requests.get(url).text

# Split into VEVENT blocks
events = re.findall(r"BEGIN:VEVENT.*?END:VEVENT", ics, re.DOTALL)
cleaned_events = []

for ev in events:
    if "LV1" in ev or "LV2" in ev:
        continue

    # Extract short code and type (TD, TP, CM, etc.)
    match = re.search(r"::([A-Z]{3,4}):([A-Z]{2,3})::", ev)
    if match:
        code, typ = match.groups()
        new_summary = f"SUMMARY:{code} - {typ}"
        ev = re.sub(r"SUMMARY:.*", new_summary, ev)
    cleaned_events.append(ev)

# Rebuild ICS
cleaned_ics = "BEGIN:VCALENDAR\n" + "\n".join(cleaned_events) + "\nEND:VCALENDAR"

# Write output
with open("cleaned_calendar.ics", "w", encoding="utf-8") as f:
    f.write(cleaned_ics)
