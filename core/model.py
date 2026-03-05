from langchain_google_genai import ChatGoogleGenerativeAI
from tools import tools

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
model_with_tools = model.bind_tools(tools)
