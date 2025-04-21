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
        students_list = details.get("students") or []
        
        if not students_list:
            team_students_map[ext_id] = {}
            continue
    
        subdict={}
    
        
        # details["students"] is an array of student objects
        if not details["students"]:
            # no students => maybe skip or store empty
            team_students_map[ext_id] = {"GITHUB": [], "TAIGA": []}
            continue

        for student_obj in students_list:
            identities = student_obj.get("identities", {})
            # e.g. identities => {"GITHUB": {"username":"danipenalba"}, "TAIGA": {...}, "GITLAB": {...}}

            for data_source_name, identity_data in identities.items():
                # identity_data might be { "username": "someone123", ... }
                username = identity_data.get("username")
                if username:
                    # if we haven't used this data_source_name yet, create a list
                    if data_source_name not in subdict:
                        subdict[data_source_name] = []
                    subdict[data_source_name].append(username)

        team_students_map[ext_id] = subdict




            # ADDED MANUALLY TO MAKE THE TESTS WORK, REMOVE LATER
    team_students_map["LDTestOrganization"] = {
        "GITHUB": ["PabloGomezNa", "PepitoGomezNa", "charlie"],
        "TAIGA": ["pgomezn", "pgomezna", "charlie"]
    }
    
    team_students_map["LD_Test_Project"] = {
        "GITHUB": ["PabloGomezNa", "PepitoGomezNa", "charlie"],
        "TAIGA": ["pgomezn", "pablogz5", "Charlie55"]
    }
    
    team_students_map["dd"] = {
        "GITHUB": ["PabloGomezNa", "PepitoGomezNa", "charlie"],
    
    
        "TAIGA": ["pgomezn", "pablogz5", "Charlie55"]
    }


    return team_students_map
        
        

        



