from pydantic import BaseModel, Field, field_validator
from app.agents.base_agent import BaseAgent
from app.config.llm_config import LLMConfig
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel

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
        self._agent = self.create_agent()
    
    model_type: str = Field(
        default="gemini",
        description="Model type for the chatbot"
    )
    model_name: str = Field(
        default="gemini-2.0-flash-exp",
        description="Model name for the chatbot"
    )
    messages: list = Field(
        default_factory=list,
        description="Store conversation message history"
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

    def get_messages(self) -> list:
        """
        Get the current message history.
        
        Returns:
            list: The conversation history
        """
        return self.messages

    def save_messages(self, messages: list):
        """
        Save the message history.
        
        Args:
            messages (list): The messages to save
        """
        self.messages = messages

    def get_api_key(self):
        """Retrieves the API key using the LLMConfig."""
        config = LLMConfig()
        llm_config = config.get_llm_config(self.model_name)
        return config.get_api_key(llm_config)

    def get_model(self):
        """Creates and returns the LLM model using the configuration."""
        config = LLMConfig()
        model_type = config.get_model_type(self.model_name)
        model_name = config.get_model_name(self.model_name)
        api_key = self.get_api_key()
        base_url = config.get_base_url(self.model_name)

        model_mapping = {
            "gemini": GeminiModel,
            "openai": OpenAIModel,
            "anthropic": AnthropicModel
        }

        model_class = model_mapping.get(model_type)
        if not model_class:
            raise ValueError(f"Unsupported model type: {model_type}")

        if model_type == "openai" and base_url:
            return model_class(model_name, api_key=api_key, base_url=base_url)
        else:
            return model_class(model_name, api_key=api_key)

    async def run_agent(self, user_query: str, save_message_history: bool = True) -> str:
        """
        Run the chatbot agent with the given user input.
        
        Args:
            user_input (str): The user's input text/query
            message_history (bool, optional): Whether to use message history (default: True)

        Returns:
            str: The chatbot's response
        """
        try:
            response = await self._agent.run(user_query, message_history=self.messages if save_message_history else [])

            # Save the message history
            if save_message_history:
                self.save_messages(response.all_messages())
                #print(response.all_messages())
            # Convert string literals to actual newlines
            cleaned_response = eval(repr(response.data.text_response).replace('\\\\n', '\\n')).strip()
            return cleaned_response
        except Exception as e:
            raise e

