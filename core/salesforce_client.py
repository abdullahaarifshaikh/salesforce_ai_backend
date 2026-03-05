from simple_salesforce import Salesforce
from config.settings import SF_USERNAME, SF_PASSWORD, SF_TOKEN

def get_salesforce_client():
    """Establishes a connection to Salesforce."""
    try:
        sf = Salesforce(
            username=SF_USERNAME,
            password=SF_PASSWORD,
            security_token=SF_TOKEN,
        )
        return sf
    except Exception as e:
        print(f"Salesforce Connection Error: {e}")
        return None
