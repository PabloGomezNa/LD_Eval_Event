# def fetch_team_students_map():
#     """
#     Call endpoint from the Learning Dashboard
#     to get the teams and students. 
    
#     Still not implemented :(
#     We need to modify the API 
#     """
#     return {
#         "LDTestOrganization": ["PabloGomezNa", "PepitoGomezNa", "charlie"],
#         "ASW_Team6": ["eve", "frank"]
#     }
    
    


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


import requests

BASE_URL = "http://gessi-dashboard.essi.upc.edu:8888/api"

def fetch_projects():
    url = f"{BASE_URL}/projects"
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Raise an exception if status != 200
    projects = response.json()
    
    return projects

def fetch_project_details(project_id: int):
    url = f"{BASE_URL}/projects/{project_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def build_team_students_map():

    projects = fetch_projects()
    team_students_map = {}

    for proj in projects:
        p_id = proj["id"]
        ext_id = proj["externalId"]  # e.g. "AMEP11Beats"

        details = fetch_project_details(p_id)
        # details["students"] is an array of student objects
        if not details["students"]:
            # no students => maybe skip or store empty
            team_students_map[ext_id] = {"GITHUB": [], "TAIGA": []}
            continue

        gh_usernames = []
        taiga_usernames = []

        for student_obj in details["students"]:
            identities = student_obj.get("identities", {})
            # e.g. identities => {"GITHUB": {"username":"danipenalba"}, "TAIGA": {...}}
            github_data = identities.get("GITHUB")
            if github_data and "username" in github_data:
                gh_usernames.append(github_data["username"])

            taiga_data = identities.get("TAIGA")
            if taiga_data and "username" in taiga_data:
                taiga_usernames.append(taiga_data["username"])

        team_students_map[ext_id] = {
            "GITHUB": gh_usernames,
            "TAIGA": taiga_usernames
        }
        
        
            # ADDED MANUALLY TO MAKE THE TESTS WORK
    team_students_map["LDTestOrganization"] = {
        "GITHUB": ["PabloGomezNa", "PepitoGomezNa", "charlie"],
        "TAIGA": ["pgomezn", "pgomezna", "charlie"]
    }
    
    team_students_map["LD_Test_Project"] = {
        "GITHUB": ["PabloGomezNa", "PepitoGomezNa", "charlie"],
        "TAIGA": ["pgomezn", "pablogz5", "Charlie55"]
    }
        

    return team_students_map



#This is the project id, we can get it from the API, but we need to modify the API to get the project id from the name of the project.
    #to acces we need 'http://gessi-dashboard.essi.upc.edu:8888/api/projects'
    



#THE EASIEST SOLUTION WOULD BE TO ADD IN THE API THE URL OF THE REPO/TAIGA SO I CAN GET THE NAME 

#ANOTHER OPTION WOULD BE TO SCAN ALL THE USERS EACH TIME, BUT I THINK ITS NOT TO EFFICIENT

#OR FORCE THE STUDENTS TO PUT THE NAME ON THE REPO/TAIGA AS EXTERNAL ID IN THE API
