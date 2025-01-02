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

    def run_agent(self, user_input: str, keep_context: bool = False) -> str:
        """
        Run the chatbot agent with the given user input.
        
        Args:
            user_input (str): The user's input text/query
            keep_context (bool, optional): Whether to maintain conversation context. Defaults to False.
            
        Returns:
            str: The chatbot's response
        """
        agent = self.create_agent()
        response = agent.run(user_input, keep_context=keep_context)
        return response

def add_arguments(parser):
    """
    Adds agent-specific arguments to the argument parser.
    """
    parser.add_argument("user_input", nargs='?', help="The user input for the agent system. If not provided, starts interactive mode.")
    parser.add_argument(
        "-k",
        "--keep-context",
        action="store_true",
        help="Keep the conversation context between user inputs.",
    )

# The main_parser is used by the main program to generate help text for this agent.
main_parser = argparse.ArgumentParser(
    description="A basic QA assistant (e.g. chatbot)."
)
add_arguments(main_parser)

def run_interactive_chat(agent=None):
    """
    Run an interactive chat session with the chatbot.
    
    Args:
        agent: An instance of BasicChatbotAgent. If None, a new instance will be created.
    """
    if agent is None:
        agent = BasicChatbotAgent()
        
    print("\nWelcome to the Interactive Chatbot!")
    print("You can start chatting now. Type 'exit' or 'quit' to end the conversation.\n")
    
    while True:
        user_input = input("·>>>: ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("\n\nGoodbye! Have a great day!")
            break
            
        if not user_input:
            continue
            
        result = agent.run_agent(user_input, keep_context=True)
        print(f"\n\n·>: {result}\n")

def main(args=None):
    """
    Main function to run the interactive chatbot.
    """
    if args is None:
        args = main_parser.parse_args()

    agent = BasicChatbotAgent()
    
    if args.user_input is None:
        # No input provided, run interactive mode
        run_interactive_chat(agent)
    else:
        # Single input mode
        result = agent.run_agent(args.user_input, keep_context=args.keep_context)
        print(f"\n·>: {result}\n")

if __name__ == "__main__":
    main()
