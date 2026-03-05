import pandas as pd
import os
from langchain_core.tools import tool
from core.salesforce_client import get_salesforce_client

@tool
def export_leads_to_excel(filename: str = "leads_export.xlsx", search_term: str = None):
    """
    Fetches leads from Salesforce and exports them to a local Excel (.xlsx) file.
    """
    sf = get_salesforce_client()
    if not sf:
        return {"status": "error", "message": "Could not connect to Salesforce."}

    try:
        query = "SELECT Id, FirstName, LastName, Company, Email, Phone, Status, CreatedDate FROM Lead"
        if search_term:
            query += f" WHERE Name LIKE '%{search_term}%' OR Company LIKE '%{search_term}%'"
        
        query += " ORDER BY CreatedDate DESC"

        results = sf.query_all(query)
        records = results.get('records', [])

        if not records:
            return {"status": "not_found", "message": "No leads found to export."}

        data = []
        for r in records:
            if 'attributes' in r: del r['attributes']
            data.append(r)

        df = pd.DataFrame(data)

        if not filename.endswith('.xlsx'):
            filename += '.xlsx'

        df.to_excel(filename, index=False)
        full_path = os.path.abspath(filename)

        return {
            "status": "success",
            "message": f"Successfully exported {len(data)} leads to Excel.",
            "file_path": full_path
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to export Excel: {str(e)}"}
