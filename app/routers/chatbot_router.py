from fastapi import APIRouter, Body, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Tuple
import uuid
import time
from datetime import datetime
import asyncio

# Import your BasicChatbotAgent from the agents folder
from agents.BasicChatbotAgent import BasicChatbotAgent

router = APIRouter()

# Dictionary to store chatbot instances and their last activity time
chatbot_instances: Dict[str, Tuple[BasicChatbotAgent, float]] = {}

# Inactivity threshold in seconds (1 hour)
INACTIVITY_THRESHOLD = 3600

class ChatRequest(BaseModel):
    user_input: str
    client_id: str = None

async def cleanup_inactive_instances():
    """
    Background task to remove inactive chatbot instances
    """
    while True:
        try:
            current_time = time.time()
            # Create a list of inactive client IDs
            inactive_clients = [
                client_id for client_id, (_, last_activity) in chatbot_instances.items()
                if current_time - last_activity > INACTIVITY_THRESHOLD
            ]
            
            # Remove inactive instances
            for client_id in inactive_clients:
                del chatbot_instances[client_id]
            
            # Wait for 5 minutes before next cleanup
            await asyncio.sleep(300)
        except Exception as e:
            # Log any errors but don't stop the cleanup task
            print(f"Error in cleanup task: {e}")
            await asyncio.sleep(300)

def update_activity(client_id: str):
    """Update the last activity time for a client"""
    if client_id in chatbot_instances:
        chatbot, _ = chatbot_instances[client_id]
        chatbot_instances[client_id] = (chatbot, time.time())

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Endpoint that takes user input and returns a chatbot response.
    Creates a new chatbot instance if client_id is not provided or doesn't exist.
    """
    # Generate new client ID if none provided
    if not request.client_id:
        request.client_id = str(uuid.uuid4())
    
    # Create new chatbot instance if needed
    if request.client_id not in chatbot_instances:
        chatbot_instances[request.client_id] = (BasicChatbotAgent(), time.time())
    
    # Get the client's chatbot instance and update activity time
    chatbot, _ = chatbot_instances[request.client_id]
    update_activity(request.client_id)
    
    response = await chatbot.run_agent(request.user_input)
    
    return {
        "response": response,
        "client_id": request.client_id
    }

@router.post("/reset")
async def reset_chat(client_id: str):
    """
    Endpoint to reset the conversation context/history for a specific client.
    """
    if client_id not in chatbot_instances:
        raise HTTPException(status_code=404, detail="Client ID not found")
    
    chatbot, _ = chatbot_instances[client_id]
    chatbot.save_messages([])  # Clear the conversation
    update_activity(client_id)
    
    return {"message": "Chatbot context has been reset for the specified client."}

@router.delete("/remove-instance")
async def remove_instance(client_id: str):
    """
    Endpoint to remove a chatbot instance for a specific client.
    """
    if client_id in chatbot_instances:
        del chatbot_instances[client_id]
        return {"message": "Chatbot instance removed successfully"}
    raise HTTPException(status_code=404, detail="Client ID not found")
