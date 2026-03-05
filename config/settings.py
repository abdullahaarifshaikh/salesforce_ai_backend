from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Salesforce Configuration
SF_USERNAME = os.getenv("SF_USERNAME")
SF_PASSWORD = os.getenv("SF_PASSWORD")
SF_TOKEN = os.getenv("SF_TOKEN")

# Google API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# WhatsApp Configuration
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "YOUR_LONG_ACCESS_TOKEN_HERE")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "YOUR_PHONE_NUMBER_ID_HERE")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "1234")

# Sarvam AI
SARV_API = os.getenv("SARV_API")
