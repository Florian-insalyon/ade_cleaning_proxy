import re, requests
import sys
import urllib3

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://ade-outils.insa-lyon.fr/ADE-Cal:~ftristant!2025-2026:84f15375bd1e1cd3910ee7278886e3be132a51fe"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def create_empty_ics():
    with open("cleaned_calendar.ics", "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\nEND:VCALENDAR")

try:
    print("Fetching calendar from INSA...")
    
    response = requests.get(url, headers=headers, timeout=30, verify=False)
    
    print(f"Status code: {response.status_code}")
    print(f"Content length: {len(response.text)} characters")
    
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        create_empty_ics()
        sys.exit(0)
        
    ics = response.text
    
    if not ics or "BEGIN:VCALENDAR" not in ics:
        print("Error: Response doesn't look like a valid ICS file")
        create_empty_ics()
        sys.exit(0)
    
    events = re.findall(r"BEGIN:VEVENT.*?END:VEVENT", ics, re.DOTALL)
    
    cleaned_events = []
    for ev in events:
        # Filtrage général
        if ("LV1" in ev) or ("LV2" in ev) or (":PCO:" in ev and "4GIPCO4" not in ev) or ":OPT:" in ev:
            continue

        # Nettoyage du champ LOCATION
        ev = re.sub(r"LOCATION:\d+ - ", "LOCATION:", ev)

        # Cas spécifique SHS - TD
        if "HU:0:S1::S-SERIE2:TD::SERIE2-OPT17" in ev:
            ev = re.sub(r"SUMMARY:.*", "SUMMARY:SHS - TD", ev)
            cleaned_events.append(ev)
            continue

        # SHS général
        if ":SHS:" in ev:
            if "HU" not in ev:
                continue
            ev = re.sub(r"SUMMARY:.*", "SUMMARY:SHS", ev)

        # EPS général
        elif ":EPS:" in ev:
            if "CDS" in ev:
                ev = re.sub(r"SUMMARY:.*", "SUMMARY:EPS", ev)
            else:
                continue

        # ASO spécifique
        elif "::ASO-HU:" in ev:
            match_aso = re.search(r"::ASO-HU:(TD|CM|TP|EDT)::", ev)
            if match_aso:
                typ = match_aso.group(1)
                new_summary = f"SUMMARY:ASO - {typ}"
                ev = re.sub(r"SUMMARY:.*", new_summary, ev)
            else:
                continue  # ignorer si type non trouvé

        # Autres cours
        else:
            match = re.search(r"::([A-Z]{3,4}):([A-Z]{2,3})::", ev)
            if match:
                code, typ = match.groups()
                if code == "EPS" and typ == "EDT":
                    continue
                elif "4GIPCO4" in ev:
                    new_summary = f"SUMMARY:PCO - {typ}"
                else:
                    new_summary = f"SUMMARY:{code} - {typ}"
                ev = re.sub(r"SUMMARY:.*", new_summary, ev)
        
        cleaned_events.append(ev)

    # Création du fichier ICS final
    cleaned_ics = (
        "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//INSALyon//Calendar//FR\n" +
        "\n".join(cleaned_events) +
        "\nEND:VCALENDAR"
    )
    
    with open("cleaned_calendar.ics", "w", encoding="utf-8") as f:
        f.write(cleaned_ics)
    
    print(f"Success! Processed {len(events)} events, kept {len(cleaned_events)}")
    print("Calendar saved to cleaned_calendar.ics")
    
except requests.exceptions.Timeout:
    print("Error: Request timeout")
    create_empty_ics()
    sys.exit(0)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    create_empty_ics()
    sys.exit(0)
