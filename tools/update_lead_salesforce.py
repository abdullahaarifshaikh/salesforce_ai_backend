from langchain_core.tools import tool
from core.salesforce_client import get_salesforce_client

@tool
def update_lead(
        search_name: str = None,
        lead_id: str = None,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        company: str = None,
        phone: str = None,
        status: str = None,
        description: str = None
):
    """
    Updates an existing Lead in Salesforce.
    Can find the lead by Name if the ID is not known.
    """
    sf = get_salesforce_client()
    if not sf:
        return {"status": "error", "message": "Could not connect to Salesforce."}

    target_id = lead_id

    if not target_id:
        if not search_name:
            return {"status": "error", "message": "Provide either 'lead_id' or 'search_name'."}

        try:
            query = f"SELECT Id, Name, Company FROM Lead WHERE Name LIKE '%{search_name}%' OR Company LIKE '%{search_name}%' LIMIT 5"
            results = sf.query(query)
            records = results.get('records', [])

            if len(records) == 0:
                return {"status": "not_found", "message": f"No lead found matching '{search_name}'."}

            if len(records) > 1:
                matches = [f"{r['Name']} ({r['Company']})" for r in records]
                return {
                    "status": "ambiguous",
                    "message": f"Found multiple leads matching '{search_name}'.",
                    "matches": matches
                }

            target_id = records[0]['Id']
        except Exception as e:
            return {"status": "error", "message": f"Search failed: {str(e)}"}

    lead_data = {}
    if first_name: lead_data['FirstName'] = first_name
    if last_name: lead_data['LastName'] = last_name
    if email: lead_data['Email'] = email
    if company: lead_data['Company'] = company
    if phone: lead_data['Phone'] = phone
    if status: lead_data['Status'] = status
    if description: lead_data['Description'] = description

    if not lead_data:
        return {"status": "warning", "message": "No new information provided to update."}

    try:
        sf.Lead.update(target_id, lead_data)
        return {
            "status": "success",
            "lead_id": target_id,
            "message": f"Successfully updated lead.",
            "updated_fields": list(lead_data.keys())
        }
    except Exception as e:
        return {"status": "error", "message": f"Salesforce update failed: {str(e)}"}
