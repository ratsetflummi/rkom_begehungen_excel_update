import requests
import pandas as pd

URL_PLANIO_ISSUES = 'https://createcheng.planio.de/issues'

def get_begehungsdaten(api_key: str, tracker_ids:str):
    headers = {"X-Redmine-API-Key": api_key, "Content-Type": "application/json"}
    begehungsdaten = []
    offset = 0
    while True:
        # First URL and response
        url = f'{URL_PLANIO_ISSUES}.json?tracker_id={tracker_ids}&limit=100&offset={offset}'
        response = requests.get(url, headers=headers)
        data = response.json()  # First dictionary response

        # Second URL and response
        url = f'{URL_PLANIO_ISSUES}.json?status_id=c&tracker_id={tracker_ids}&limit=100&offset={offset}'
        response2 = requests.get(url, headers=headers)
        data2 = response2.json()  # Second dictionary response

        # Assuming both dictionaries have a key 'issues' which holds lists
        issues1 = data.get('issues', [])
        issues2 = data2.get('issues', [])

        # Combine the lists of issues
        combined_issues = issues1 + issues2

        # Now update the 'issues' key in data1 with the combined issues
        data['issues'] = combined_issues

        # Now 'data1' contains the combined issues from both dictionaries
        if not data["issues"]:
            break
        
        for issue in data['issues']:
            sachstand = ""
            bemerkung = ""
            protokoll = ""
            #print(issue['id'],"\n","\n",issue["status"]['name'],"\n",issue["parent"]['id'],"\n",issue["subject"],"\n",issue["description"])
            #print(issue['id'],"\n",issue["project"]['name'],"\n",issue["tracker"]['name'],"\n",issue["status"]['name'],"\n",issue["parent"]['id'],"\n",issue["subject"],"\n",issue["description"])
            for custom_field in issue["custom_fields"]:
                if custom_field["name"] == "Sachstand" and custom_field["value"] != "":
                    sachstand = sachstand + (custom_field["value"]) + "\n"
                if custom_field["name"] == "Ortstermin" and custom_field["value"] != "":
                    bemerkung = custom_field["name"] + ": " + custom_field["value"] + "\n"
                if custom_field["name"].endswith("Kontaktversuch") and custom_field["value"] != "":
                    bemerkung = bemerkung + custom_field["name"] + ": " + custom_field["value"] + "\n"
                if custom_field["name"] == "Protokoll versendet" and custom_field["value"]:
                    protokoll = "" + custom_field["value"]
            issue_data = {
                'issue_id': issue['id'],
                'address': issue["subject"],
                'status': issue["status"]['name'],
                'sachstand': sachstand,
                'bemerkung': bemerkung,
                'description': issue["description"],
                'protokoll': protokoll,
            }
            # for custom_field in issue.get('custom_fields'):
            #     if custom_field['name'] == nachbesserungsgrund_fieldname:
            #         issue_data.update({'nachbesserungsgrund': '; '.join(custom_field['value'])})
            begehungsdaten.append(issue_data)

        offset += 100
        if offset > data["total_count"]:
            break
    df = pd.DataFrame(data=begehungsdaten)
    #print(df.head(50))
    return df
