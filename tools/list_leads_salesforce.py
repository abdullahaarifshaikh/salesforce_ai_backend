from langchain_core.tools import tool
from core.salesforce_client import get_salesforce_client

@tool
def list_leads(limit: int = 5, search_term: str = None):
    """
    Retrieves a list of Leads from Salesforce CRM.
    """
    sf = get_salesforce_client()
    if not sf:
        return {"status": "error", "message": "Could not connect to Salesforce."}

    try:
        query = "SELECT Id, FirstName, LastName, Company, Email, Phone, Status FROM Lead"
        if search_term:
            query += f" WHERE Name LIKE '%{search_term}%' OR Company LIKE '%{search_term}%'"
        
        query += f" ORDER BY CreatedDate DESC LIMIT {limit}"

        results = sf.query(query)
        leads = results.get('records', [])

        if not leads:
            return {"status": "not_found", "message": "No leads found."}

        clean_leads = []
        for lead in leads:
            if 'attributes' in lead:
                del lead['attributes']
            clean_leads.append(lead)

        return {"status": "success", "count": len(clean_leads), "leads": clean_leads}

    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch leads: {str(e)}"}
