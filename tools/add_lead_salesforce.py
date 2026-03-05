from langchain_core.tools import tool
from core.salesforce_client import get_salesforce_client

@tool
def add_lead(
        last_name: str,
        company: str,
        first_name: str = None,
        email: str = None,
        phone: str = None,
        description: str = None
):
    """
    Creates a new Lead in Salesforce CRM.

    Use this tool whenever the user wants to add a lead, prospect, or customer inquiry.
    """
    sf = get_salesforce_client()
    if not sf:
        return {"status": "error", "message": "Could not connect to Salesforce."}

    # Prepare the data payload
    lead_data = {
        'LastName': last_name,
        'Company': company,
        'Status': 'Open - Not Contacted'
    }

    if first_name: lead_data['FirstName'] = first_name
    if email: lead_data['Email'] = email
    if phone: lead_data['Phone'] = phone
    if description: lead_data['Description'] = description

    try:
        # Create the record
        result = sf.Lead.create(lead_data)
        if result.get('success'):
            return {
                "status": "success",
                "lead_id": result.get('id'),
                "message": f"Lead added to Salesforce successfully. ID: {result.get('id')}"
            }
        else:
            return {"status": "error", "details": result.get('errors')}

    except Exception as e:
        return {"status": "error", "message": str(e)}
