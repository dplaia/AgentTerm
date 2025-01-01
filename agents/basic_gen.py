from pydantic import BaseModel, Field
from .base_agent import BaseAgent  # Import the BaseAgent
import argparse

class ChatResponse(BaseModel):
    text_response: str = Field(description="Your response.")

class BasicChatbotAgent(BaseAgent):
    model_name: str = "gemini-2.0-flash-exp"  # You can override if needed
    system_prompt: str = """You are a helpful and friendly chatbot assistant. You provide clear, concise, and accurate responses to user queries.
        You maintain a conversational tone while being informative and professional."""
    result_type: type[str] = str

def add_arguments(parser):
    """
    Adds agent-specific arguments to the argument parser.
    """
    parser.add_argument("task_description", help="The task description for the agent system.")

# The main_parser is used by the main program to generate help text for this agent.
main_parser = argparse.ArgumentParser(
    description="A basic QA assistant (e.g. chatbot)."
)
add_arguments(main_parser)

def main(args=None):
    """
    Main function to run the interactive chatbot.
    """
    print("\nWelcome to the Interactive Chatbot!")
    print("You can start chatting now. Type 'exit' or 'quit' to end the conversation.\n")

    agent = BasicChatbotAgent()
    
    while True:
        user_input = input(">>>: ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("\nGoodbye! Have a great day!")
            break
            
        if not user_input:
            continue
            
        result = agent.run_agent(user_input, keep_context=True)
        print(f"\n>: {result.data}\n")

if __name__ == "__main__":
    main()
