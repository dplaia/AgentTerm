import os
import json
from typing import Dict, Optional

class LLMConfig:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self._config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load the configuration from the JSON file."""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def get_llm_config(self, llm_name: str) -> Optional[Dict]:
        """Get the configuration for a specific LLM model."""
        for llm in self._config.get("llms", []):
            if llm["name"] == llm_name:
                return llm
        return None

    def get_api_key(self, llm_config: Dict) -> str:
        """Get the API key for a specific LLM configuration."""
        api_key_var = llm_config.get("api_key")
        if not api_key_var:
            raise ValueError(f"API key environment variable not specified for model {llm_config['name']}")
            
        api_key = os.getenv(api_key_var)
        if not api_key:
            raise ValueError(f"{api_key_var} environment variable not set.")
        return api_key

    def get_model_type(self, llm_name: str) -> str:
        """Get the model type for a specific LLM name."""
        llm_config = self.get_llm_config(llm_name)
        if not llm_config:
            raise ValueError(f"No configuration found for LLM: {llm_name}")
        return llm_config["model_type"]

    def get_model_name(self, llm_name: str) -> str:
        """Get the actual model name for a specific LLM configuration."""
        llm_config = self.get_llm_config(llm_name)
        if not llm_config:
            raise ValueError(f"No configuration found for LLM: {llm_name}")
        return llm_config["model"]
