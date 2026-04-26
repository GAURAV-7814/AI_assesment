import os
import requests
import urllib.parse

def search_college_scorecard(school_name: str) -> dict:
    """
    Search for a college using the US Dept of Education College Scorecard API.
    Input Requirements: Provide a JSON object with the key 'school_name'.
    If 'the best' or 'top' schools are asked, use this tool to search for institutional data.
    """
    api_key = os.getenv("DATAGOV_API_KEY")
    if not api_key:
        return {"error": "DATAGOV_API_KEY not configured in environment variables."}

    base_url = "https://api.data.gov/ed/collegescorecard/v1/schools"
    
    # We look for schools matching the name. 
    # API docs: school.name is the field for the institution name.
    encoded_name = urllib.parse.quote(school_name)
    query_url = f"{base_url}?api_key={api_key}&school.name={encoded_name}&fields=school.name,school.city,school.state,latest.admissions.admission_rate.overall,latest.cost.attendance.academic_year,latest.student.size"
    
    try:
        response = requests.get(query_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return {"message": f"No data found for school: {school_name}"}
        
        # Take the first match for simplicity
        school_data = results[0]
        
        return {
            "name": school_data.get("school.name"),
            "location": f"{school_data.get('school.city')}, {school_data.get('school.state')}",
            "acceptance_rate": school_data.get("latest.admissions.admission_rate.overall"),
            "attendance_cost": school_data.get("latest.cost.attendance.academic_year"),
            "enrollment_size": school_data.get("latest.student.size")
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch data from College Scorecard API: {str(e)}"}
