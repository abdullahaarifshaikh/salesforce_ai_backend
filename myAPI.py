import os
import requests
import pytesseract
from PIL import Image
from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
from langchain_core.messages import HumanMessage, SystemMessage
from sarvamai import SarvamAI
import base64

from main import SYSTEM_PROMPT
from config.settings import VERIFY_TOKEN, WHATSAPP_TOKEN, PHONE_NUMBER_ID, SARV_API
from core.workflow import build_workflow

app = FastAPI()
agent_app = build_workflow()

def download_whatsapp_media(media_id: str, extension: str) -> str:
    """Downloads media from WhatsApp and saves it locally."""
    url = f"https://graph.facebook.com/v17.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    
    res = requests.get(url, headers=headers).json()
    media_url = res.get("url")

    if media_url:
        media_res = requests.get(media_url, headers=headers)
        file_path = f"temp_{media_id}{extension}"
        with open(file_path, "wb") as f:
            f.write(media_res.content)
        return file_path
    return None

@app.get("/webhook")
async def verify_webhook(
        hub_mode: str = Query(..., alias="hub.mode"),
        hub_verify_token: str = Query(..., alias="hub.verify_token"),
        hub_challenge: str = Query(..., alias="hub.challenge")
):
    """Verifies the webhook with Meta."""
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    return PlainTextResponse(content="Verification failed", status_code=403)

@app.post("/webhook")
async def receive_message(request: Request):
    """Handles incoming WhatsApp messages."""
    data = await request.json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" in value:
            message_data = value["messages"][0]
            sender_id = message_data["from"]
            msg_type = message_data["type"]
            
            user_input = ""

            if msg_type == "text":
                user_input = message_data["text"]["body"]
                
            elif msg_type == "audio":
                media_id = message_data["audio"]["id"]
                file_path = download_whatsapp_media(media_id, ".ogg")
                if file_path:
                    try:
                        # 1. Transcribe with Sarvam AI
                        client = SarvamAI(api_subscription_key=SARV_API)
                        with open(file_path, "rb") as f:
                            response = client.speech_to_text.transcribe(
                                file=(os.path.basename(file_path), f, "audio/ogg"),
                                model="saaras:v3",
                                mode="transcribe",
                                language_code="unknown"
                            )
                        transcript = response.transcript.strip()

                        if transcript:
                            # 2. Translate to English using Sarvam AI
                            translation_response = client.text.translate(
                                input=transcript,
                                source_language_code="auto",
                                target_language_code="en-IN",
                                speaker_gender="Male",
                                mode="formal",
                                model="mayura:v1"
                            )
                            
                            # Safely extract translated text
                            if hasattr(translation_response, "translated_text"):
                                translated_text = translation_response.translated_text
                            elif isinstance(translation_response, dict):
                                translated_text = translation_response.get("translated_text", transcript)
                            else:
                                translated_text = str(translation_response)
                                
                            user_input = f"[User sent a voice note translated as]: {translated_text}"
                        else:
                            user_input = "[User sent an empty or inaudible voice note]"

                    except Exception as e:
                        print(f"Sarvam AI Error: {e}")
                        user_input = "[Error processing voice note]"
                    finally:
                        os.remove(file_path) # Clean up the audio file

            elif msg_type == "image":
                media_id = message_data["image"]["id"]
                file_path = download_whatsapp_media(media_id, ".jpg")
                if file_path:
                    try:
                        with open(file_path, "rb") as image_file:
                            image_data = base64.b64encode(image_file.read()).decode("utf-8")
                        user_input = [
                            {"type": "text", "text": "I have sent an image. Please extract any relevant business card or lead information from it and perform the necessary CRM actions."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                        ]

                    except Exception as e:
                        print(f"Image Vision Error: {e}")
                        user_input = "[Error processing image for vision]"
                    finally:
                        os.remove(file_path)  # Clean up the image file# Clean up the image file

            if user_input:
                if msg_type == "image":
                    print("Sending image...")
                else:
                    print(f"Input mapped to LLM: {user_input}")
                response = process_with_ai(user_input, sender_id)
                send_whatsapp_message(sender_id, response)

    except Exception as e:
        print(f"Error processing message: {e}")
        return {"status": "error", "error": str(e)}

    return {"status": "received"}


def process_with_ai(user_input: str, sender_id: str) -> str:
    """Sends text to LangGraph and returns the pure text response, using built-in memory."""
    config = {"configurable": {"thread_id": sender_id}}
    result = agent_app.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )
    last_message = result["messages"][-1]
    content = last_message.content
    text_response = ""
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_response += block.get("text", "")
            elif isinstance(block, str):
                text_response += block
    else:
        text_response = str(content)

    return text_response.strip()

def send_whatsapp_message(to_number: str, message_text: str):
    """Sends a text message back to WhatsApp."""
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text}
    }
    requests.post(url, json=payload, headers=headers)
