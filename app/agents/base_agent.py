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
    Subclasses must implement the `run_agent`, `get_api_key`, and `get_model` methods.
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

    @abstractmethod
    def get_api_key(self):
        """Retrieves the API key. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_model(self):
        """Creates and returns the LLM model. Must be implemented by subclasses."""
        pass

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