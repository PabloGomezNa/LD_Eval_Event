def fetch_team_students_map():
    """
    Call endpoint from the Learning Dashboard
    to get the teams and students. 
    
    Still not implemented :(
    We need to modify the API 
    """
    return {
        "LDTestOrganization": ["PabloGomezNa", "PepitoGomezNa", "charlie"],
        "ASW_Team6": ["eve", "frank"]
    }
    
    

import requests





'''
http://gessi-dashboard.essi.upc.edu:8888/api/projects

[{"id":180,"externalId":"AMEP11Beats","name":"AMEP11Beats","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},"students":null},
{"id":186,"externalId":"AMEP11ChopChop","name":"AMEP11ChopChop","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},"students":null},
{"id":179,"externalId":"AMEP11UniMatch","name":"AMEP11UniMatch","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},"students":null},
{"id":181,"externalId":"AMEP12Academy4All","name":"AMEP12Academy4All","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},"students":null},
{"id":182,"externalId":"AMEP21Cano3","name":"AMEP21Cano3","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},"students":null},
{"id":185,"externalId":"AMEP21Krunkillos","name":"AMEP21Krunkillos","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},"students":null},
{"id":177,"externalId":"AMEP21Sportifiers","name":"AMEP21Sportifiers","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},"students":null},
{"id":184,"externalId":"AMEP21SportifyCoach","name":"AMEP21SportifyCoach","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},"students":null},
{"id":183,"externalId":"AMEP22GoRace","name":"AMEP22GoRace","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},"students":null},
{"id":178,"externalId":"AMEP22TicketMonsterTM","name":"AMEP22TicketMonsterTM","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},"students":null},
{"id":187,"externalId":"it12d","name":"it12d","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},"students":null}]


http://gessi-dashboard.essi.upc.edu:8888/api/projects/180

{"id":180,"externalId":"AMEP11Beats","name":"AMEP11Beats","description":"No description specified","logo":null,"active":true,"backlogId":null,"isGlobal":false,"anonymized":false,"identities":{},
"students":
    [{"id":771,"name":"Sergio Conde","identities":{"GITHUB":{"username":"Sergioo1313","student":null,"data_source":"GITHUB"},"TAIGA":{"username":"sergioo1313","student":null,"data_source":"TAIGA"}},"project":null},
    {"id":769,"name":"Jordi Sancho","identities":{"GITHUB":{"username":"JordiSanchoo","student":null,"data_source":"GITHUB"},"TAIGA":{"username":"jordisanchoo","student":null,"data_source":"TAIGA"}},"project":null},
    {"id":768,"name":"Aymane El Hisati","identities":{"GITHUB":{"username":"KaizoIncc","student":null,"data_source":"GITHUB"},"TAIGA":{"username":"MrStickers","student":null,"data_source":"TAIGA"}},"project":null},
    {"id":770,"name":"Carlos Sancho","identities":{"GITHUB":{"username":"CarlosSanchoo","student":null,"data_source":"GITHUB"},"TAIGA":{"username":"CarlosSanchoo","student":null,"data_source":"TAIGA"}},"project":null},
    {"id":772,"name":"Ariel Medina","identities":{"GITHUB":{"username":"Ar1e1","student":null,"data_source":"GITHUB"},"TAIGA":{"username":"Ari3l","student":null,"data_source":"TAIGA"}},"project":null},
    {"id":767,"name":"Daniel Peñalba","identities":{"GITHUB":{"username":"danipenalba","student":null,"data_source":"GITHUB"},"TAIGA":{"username":"danipenalba","student":null,"data_source":"TAIGA"}},"project":null}]}
'''


import requests, json

base_url = "http://gessi-dashboard.essi.upc.edu:8888/api"
projects = requests.get(f"{base_url}/projects").json()

result = {}

for project in projects:
    team_name = project["externalId"]
    project_id = project["id"]

    # Fetch the details of each project to get the students
    project_details = requests.get(f"{base_url}/projects/{project_id}").json()

    students_list = []
    for st in project_details.get("students", []):
        identities = st.get("identities", {})
        gh_user = identities.get("GITHUB", {}).get("username", "")
        tg_user = identities.get("TAIGA", {}).get("username", "")
        students_list.append({
            "github_username": gh_user,
            "taiga_username": tg_user
        })

    result[team_name] = students_list

# Turn the dictionary into JSON
json_data = json.dumps(result, indent=2)
print(json_data)


#This is the project id, we can get it from the API, but we need to modify the API to get the project id from the name of the project.
    #to acces we need 'http://gessi-dashboard.essi.upc.edu:8888/api/projects'
    
    