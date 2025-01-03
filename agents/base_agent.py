import os
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel  # Or other models if needed
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel

class BaseAgent(ABC, BaseModel):
    """
    Abstract base class for pydantic-ai based agents.
    Subclasses must implement the `run_agent` method.
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

    def get_api_key(self):
        """Retrieves the API key from the environment variable."""
        if self.api_key_env_var is None:
            # Auto-select API key environment variable based on model type
            env_var_mapping = {
                "gemini": "GEMINI_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY"
            }
            self.api_key_env_var = env_var_mapping.get(self.model_type)
            if not self.api_key_env_var:
                raise ValueError(f"Unsupported model type for API key selection: {self.model_type}")

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

    @abstractmethod
    def run_agent(self, *args, **kwargs):
        """
        Abstract method that must be implemented by subclasses to run the agent.
        """
        pass