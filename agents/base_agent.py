import os
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel  # Or other models if needed

class BaseAgent(BaseModel):
    """
    Base class for pydantic-ai based agents.
    """
    model_name: str = "gemini-2.0-flash-exp"  # Default model
    system_prompt: str = "" # default system prompt
    result_type: type[BaseModel] = None
    api_key_env_var: str = "GEMINI_API_KEY"  # Default API key environment variable name
    examples_file: str = None # path to file containing examples for the LLM

    def get_api_key(self):
        """Retrieves the API key from the environment variable."""
        api_key = os.getenv(self.api_key_env_var)
        if not api_key:
            raise ValueError(f"{self.api_key_env_var} environment variable not set.")
        return api_key

    def get_model(self):
        """Creates and returns the LLM model."""
        return GeminiModel(self.model_name, api_key=self.get_api_key())

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