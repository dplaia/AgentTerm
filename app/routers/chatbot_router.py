from fastapi import APIRouter, Body
from pydantic import BaseModel

# Import your BasicChatbotAgent from the agents folder
# Adjust the path if needed (e.g., from agents.BasicChatbotAgent)
from agents.BasicChatbotAgent import BasicChatbotAgent

router = APIRouter()

# Create a global instance of your agent
chatbot_agent = BasicChatbotAgent()

# A simple Pydantic model for the request body
class ChatRequest(BaseModel):
    user_input: str

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Endpoint that takes user input and returns a chatbot response.
    """
    # If you want to preserve context, the agent has stored messages by default,
    # so you can call `run_agent` directly.
    response = await chatbot_agent.run_agent(request.user_input)
    return {"response": response}


@router.post("/reset")
async def reset_chat():
    """
    Endpoint to reset the conversation context/history.
    """
    chatbot_agent.save_messages([])  # Clear the conversation
    return {"message": "Chatbot context has been reset."}
