import re, requests

url = "https://ade-outils.insa-lyon.fr/ADE-Cal:~ftristant!2025-2026:84f15375bd1e1cd3910ee7278886e3be132a51fe"
ics = requests.get(url).text

events = re.findall(r"BEGIN:VEVENT.*?END:VEVENT", ics, re.DOTALL)
cleaned_events = []

for ev in events:
    # Skip LV1, LV2, and generic :PCO: events (but keep 4GIPCO4)
    if ("LV1" in ev) or ("LV2" in ev) or (":PCO:" in ev and "4GIPCO4" not in ev):
        continue
    # Skip :OPT: events entirely
    if ":OPT:" in ev:
        continue

    match = re.search(r"::([A-Z]{3,4}):([A-Z]{2,3})::", ev)
    if match:
        code, typ = match.groups()
        # Special cases: rename "EPS - EDT" to "EPS" and "SHS - EDT" to "SHS"
        if code == "EPS" and typ == "EDT":
            new_summary = "SUMMARY:EPS"
        elif code == "SHS" and typ == "EDT":
            new_summary = "SUMMARY:SHS"
        # Keep "4GIPCO4 - TA" as-is (no change)
        elif "4GIPCO4" in ev:
            new_summary = f"SUMMARY:PCO - {typ}"  # Force "PCO - TA" format
        else:
            new_summary = f"SUMMARY:{code} - {typ}"  # Default format
        ev = re.sub(r"SUMMARY:.*", new_summary, ev)

    cleaned_events.append(ev)

cleaned_ics = "BEGIN:VCALENDAR\n" + "\n".join(cleaned_events) + "\nEND:VCALENDAR"

with open("cleaned_calendar.ics", "w", encoding="utf-8") as f:
    f.write(cleaned_ics)
