import re, requests
import sys

# URL encodée pour éviter les problèmes
url = "https://ade-outils.insa-lyon.fr/ADE-Cal:~ftristant!2025-2026:84f15375bd1e1cd3910ee7278886e3be132a51fe"

try:
    # Ajouter un timeout et headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()  # Lève une exception pour les codes HTTP 4xx/5xx
    
    ics = response.text
    
    if not ics:
        print("Erreur : Le calendrier récupéré est vide")
        sys.exit(1)
        
    events = re.findall(r"BEGIN:VEVENT.*?END:VEVENT", ics, re.DOTALL)
    
    print(f"Nombre d'événements trouvés : {len(events)}")
    
    cleaned_events = []
    for ev in events:
        # Skip unwanted events
        if ("LV1" in ev) or ("LV2" in ev) or (":PCO:" in ev and "4GIPCO4" not in ev) or ":OPT:" in ev:
            continue

        ev = re.sub(r"LOCATION:\d+ - ", "LOCATION:", ev)

        # Rename the specific class to "SHS - TD"
        if "HU:0:S1::S-SERIE2:TD::SERIE2-OPT17" in ev:
            ev = re.sub(r"SUMMARY:.*", "SUMMARY:SHS - TD", ev)
            cleaned_events.append(ev)
            continue

        if ":SHS:" in ev:
            if "HU" not in ev:
                continue
            new_summary = "SUMMARY:SHS"
            ev = re.sub(r"SUMMARY:.*", new_summary, ev)
        elif ":EPS:" in ev:
            if "CDS" in ev:
                new_summary = "SUMMARY:EPS"
                ev = re.sub(r"SUMMARY:.*", new_summary, ev)
            else:
                continue
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

    cleaned_ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//INSALyon//Calendar//FR\n" + "\n".join(cleaned_events) + "\nEND:VCALENDAR"
    
    with open("cleaned_calendar.ics", "w", encoding="utf-8") as f:
        f.write(cleaned_ics)
    
    print(f"Nombre d'événements nettoyés : {len(cleaned_events)}")
    print("Calendrier nettoyé avec succès !")
    
except requests.exceptions.RequestException as e:
    print(f"Erreur réseau : {e}")
    sys.exit(1)
except Exception as e:
    print(f"Erreur inattendue : {e}")
    sys.exit(1)
