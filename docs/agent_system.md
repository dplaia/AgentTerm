# Agent System Documentation

## Overview

The agent system is a flexible and extensible framework for building and managing AI agents. It uses the PydanticAI library for type-safe AI interactions and supports multiple LLM providers including Gemini, OpenAI, and Anthropic.

## System Architecture

### Core Components

1. **Agent Manager (`main.py`)**
   - Discovers and loads available agents dynamically
   - Manages agent configuration and settings
   - Provides a CLI interface for agent selection and execution
   - Handles LLM selection and configuration

2. **Base Agent (`agents/base_agent.py`)**
   - Abstract base class that defines the agent interface
   - Handles LLM initialization and API key management
   - Provides common functionality for all agents
   - Integrates with PydanticAI for type-safe interactions

3. **Agent Directory (`agents/`)**
   - Contains all agent implementations
   - Each agent is a separate Python module
   - Agents must inherit from `BaseAgent`

## Creating New Agents

### Agent Implementation

To create a new agent, follow these steps:

1. Create a new Python file in the `agents` directory
2. Import and inherit from `BaseAgent`
3. Define required fields:
   - `model_type`: LLM provider ('gemini', 'openai', or 'anthropic')
   - `model_name`: Specific model to use
   - `system_prompt`: Instructions for the LLM
   - `result_type`: Pydantic model defining the expected output

### Example: Basic Chatbot Agent

The `BasicChatbotAgent` (`agents/BasicChatbotAgent.py`) demonstrates a complete agent implementation:

```python
class BasicChatbotAgent(BaseAgent):
    # Model configuration
    model_type: str = "gemini"
    model_name: str = "gemini-2.0-flash-exp"
    
    # Agent-specific settings
    settings: ChatbotSettings
    messages: list  # Conversation history
    
    # Define output structure
    result_type: type[ChatResponse] = ChatResponse
    
    async def run_agent(self, user_query: str, message_history: list = None) -> str:
        # Agent implementation
        ...
```

## Agent Management

### Configuration

- Agents are configured via `config.json`
- LLM API keys are managed through environment variables
- Each agent can have its own settings class

### Discovery and Loading

The system automatically discovers agents in the `agents` directory:
- Scans for Python files
- Imports modules dynamically
- Makes agents available through the CLI interface

### Execution

Agents can be run in two ways:
1. Through the interactive menu system
2. Directly via command line arguments

## Best Practices

1. **Type Safety**
   - Use Pydantic models for input/output validation
   - Define clear result types for agent outputs

2. **Configuration**
   - Keep sensitive information in environment variables
   - Use settings classes for agent-specific configuration

3. **Error Handling**
   - Implement proper validation for model types
   - Handle API errors gracefully

4. **Documentation**
   - Provide clear docstrings for agent classes
   - Document expected inputs and outputs

## Supported LLM Providers

The system supports the following LLM providers:
- Gemini (Google)
- OpenAI (GPT models)
- Anthropic (Claude models)

Each provider requires its own API key set in the appropriate environment variable:
- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
