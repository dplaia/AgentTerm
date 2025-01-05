from pydantic import BaseModel, Field, field_validator
from .base_agent import BaseAgent  # Import the BaseAgent
import argparse
import asyncio
from rich import print

class ChatResponse(BaseModel):
    text_response: str = Field(description="Your response.")

class ChatbotSettings(BaseModel):
    """Settings for the BasicChatbotAgent"""
    keep_context: bool = Field(
        default=True,
        description="Whether to maintain conversation context between messages"
    )
    default_llm: str = Field(
        default="gemini-2.0-flash-exp",
        description="Default language model to use"
    )

class BasicChatbotAgent(BaseAgent):
    model_type: str = Field(
        default="gemini",
        description="Model type for the chatbot"
    )
    model_name: str = Field(
        default="gemini-2.0-flash-exp",
        description="Model name for the chatbot"
    )

    system_prompt: str = Field(
        default="""You are an AI assistant designed to produce output that is visually appealing and easily readable in a terminal. When formatting your responses, utilize the syntax of the Python `rich` library. This involves using square brackets to enclose formatting tags.
        Here are some examples of how to apply formatting:

        * **Emphasis:** Instead of "This is important", output "[bold]This is important[/]".
        * **Headers/Titles:** Instead of "Section Title:", output "[bold blue]Section Title:[/]".
        * **Warnings:** Instead of "Warning!", output "[bold red]Warning![/]".
        * **Success Messages:** Instead of "Operation successful.", output "[green]Operation successful.[/]".
        * **Lists:** You can use colors for list items like "[cyan]*[/] Item 1".

        Always use the `rich` library's syntax for formatting terminal output to enhance readability.""",
        description="System prompt for the chatbot"
    )

    result_type: type[ChatResponse] = ChatResponse
    settings: ChatbotSettings = Field(
        default_factory=ChatbotSettings,
        description="Agent-specific settings"
    )

    @field_validator('model_type')
    def validate_model_type(cls, v):
        if v not in ["gemini", "openai", "anthropic"]:
            raise ValueError(f"Invalid model_type: {v}. Must be one of: gemini, openai, anthropic")
        return v

    def __init__(self, **data):
        """
        Initialize the BasicChatbotAgent with optional parameters.
        
        Args:
            model_type (str, optional): Model type ('gemini', 'openai', or 'anthropic')
            model_name (str, optional): Name of the model to use
            system_prompt (str, optional): Custom system prompt for the chatbot
            settings (ChatbotSettings, optional): Agent-specific settings
        """
        if 'settings' in data and isinstance(data['settings'], dict):
            data['settings'] = ChatbotSettings(**data['settings'])
        super().__init__(**data)

    async def run_agent(self, user_query: str, keep_context: bool | None = None) -> str:
        """
        Run the chatbot agent with the given user input.
        
        Args:
            user_input (str): The user's input text/query
            keep_context (bool, optional): Whether to maintain conversation context.
                If None, uses the value from settings.
            
        Returns:
            str: The chatbot's response
        """
        # Use settings.keep_context if keep_context is not explicitly provided
        keep_context = keep_context if keep_context is not None else self.settings.keep_context
        
        agent = self.create_agent()
        response = await agent.run(user_query)
        return response.data.text_response

    async def run_interactive_chat(self):
        """
        Run an interactive chat session with the chatbot.
        
        Args:
            agent: An instance of BasicChatbotAgent. If None, a new instance will be created.
        """
        print("\nWelcome to the Interactive Chatbot!")
        print("You can start chatting now. Type 'exit' or 'quit' to end the conversation.\n")
        
        while True:
            user_input = input("·>>>: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\n\nGoodbye! Have a great day!")
                break
                
            if not user_input:
                continue
                
            result = await self.run_agent(user_input, keep_context=True)
            print(f"\n\n·>: {result}\n")

async def main(args=None):
    """
    Main function to run the interactive chatbot.
    """
    agent = BasicChatbotAgent()

    # No input provided, run interactive mode
    await agent.run_interactive_chat()

if __name__ == "__main__":
    asyncio.run(main())
