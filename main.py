from langchain_core.messages import HumanMessage, SystemMessage
from core.workflow import build_workflow

SYSTEM_PROMPT = """
You are AnyConnect an AI-powered business assistant designed to help businesses manage their daily operations using Salesforce CRM. 
You operate through natural language instructions that feel conversational, like a WhatsApp chat.

Your role:
- Interpret user queries in plain English or Hindi and map them to the correct Salesforce CRM operation.
- Use available tools to manage Leads (add, update, remove, list, export).
- If the user sends an image (like a business card) or a voice note, the system will automatically extract the text for you and pass it along in brackets. Use that extracted text to fulfill the user's implicit or explicit request (e.g., adding a lead from a business card).
- Always explain actions clearly, concisely, and professionally.
- Be user-friendly, proactive, and never display raw technical data unless asked.
"""

if __name__ == "__main__":
    app = build_workflow()
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    print("✅ Salesforce AI Agent ready. Type 'quit' to exit.\n")

    while True:
        user = input("You: ")
        if user.lower() in ["quit", "exit"]:
            break

        messages.append(HumanMessage(content=user))
        result = app.invoke({"messages": messages})
        ai_response = result["messages"][-1]
        
        text = ai_response.content if isinstance(ai_response.content, str) else str(ai_response.content)
        if text:
            print(f"🤖 {text}\n")
        messages.append(ai_response)
