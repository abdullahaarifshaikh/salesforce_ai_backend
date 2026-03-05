from .add_lead_salesforce import add_lead
from .update_lead_salesforce import update_lead
from .remove_lead_salesforce import remove_lead
from .list_leads_salesforce import list_leads
from .export_leads_excel import export_leads_to_excel

tools = [
    add_lead,
    update_lead,
    remove_lead,
    list_leads,
    export_leads_to_excel
]
