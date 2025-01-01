import os
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel  # Or other models if needed
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel

class BaseAgent(BaseModel):
    """
    Base class for pydantic-ai based agents.
    """
    model_type: str = Field(
        default="gemini", description="Model type, either 'gemini', 'openai', or 'anthropic'"
    )
    model_name: str = Field(
        default="gemini-2.0-flash-exp", description="Model name"
    )
    system_prompt: str = Field(
        default="", description="Default system prompt"
    )
    result_type: type[BaseModel] = Field(
        default=None, description="Result type"
    )
    api_key_env_var: str = Field(
        default=None, description="API key environment variable name"
    )
    examples_file: str = Field(
        default=None, description="Path to file containing examples for the LLM"
    )

    def get_api_key(self):
        """Retrieves the API key from the environment variable."""
        api_key = os.getenv(self.api_key_env_var)
        if not api_key:
            raise ValueError(f"{self.api_key_env_var} environment variable not set.")
        return api_key

    def get_model(self):
        """Creates and returns the LLM model."""
        if self.model_type == "gemini":
            return GeminiModel(self.model_name, api_key=self.get_api_key())
        elif self.model_type == "openai":
            return OpenAIModel(self.model_name, api_key=self.get_api_key())
        elif self.model_type == "anthropic":
            return AnthropicModel(self.model_name, api_key=self.get_api_key())
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def create_agent(self):
        """Creates and returns the pydantic-ai Agent."""
        if not self.result_type:
            raise ValueError("result_type must be defined in the derived class.")

        return Agent(
            self.get_model(),
            result_type=self.result_type,
            system_prompt=self.system_prompt,
        )

    def run_agent(self, user_input: str):
        """
        Runs the agent with the given user input.
        Adds examples to the user input, if a file is specified in self.examples_file.
        """
        agent = self.create_agent()
        if self.examples_file:
            examples_path = os.path.join(os.path.dirname(__file__), self.examples_file)
            if os.path.exists(examples_path):
                with open(examples_path, 'r') as file:
                    examples = file.read()
                user_input += examples
            else:
                print(f"Warning: Examples file not found: {examples_path}")
        
        return agent.run_sync(user_input)