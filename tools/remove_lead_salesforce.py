from langchain_core.tools import tool
from core.salesforce_client import get_salesforce_client

@tool
def remove_lead(search_name: str = None, lead_id: str = None):
    """
    Deletes an existing Lead from Salesforce CRM.
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
                    "message": f"Found multiple matches.",
                    "matches": matches
                }

            target_id = records[0]['Id']
        except Exception as e:
            return {"status": "error", "message": f"Search failed: {str(e)}"}

    try:
        sf.Lead.delete(target_id)
        return {
            "status": "success",
            "lead_id": target_id,
            "message": f"Successfully deleted lead: {search_name or target_id}"
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to delete Salesforce lead: {str(e)}"}
