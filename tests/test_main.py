import pytest
import os
import json
from unittest.mock import patch, MagicMock
from main import (
    discover_agents,
    load_config,
    save_config,
    show_help,
    select_llm,
    select_agent,
    show_menu,
    run_agent,
    main,
)

from agents.BasicChatbotAgent import BasicChatbotAgent, ChatbotSettings
import asyncio

# Mock data for testing
MOCK_CONFIG = {
    "llms": [
        {
            "name": "test-llm",
            "api_key": "test_api_key",
            "model_type": "openai",
            "model": "gpt-3.5-turbo",
        }
    ],
    "agents": [
        {
            "name": "BasicChatbotAgent",
            "settings": {"keep_context": True, "default_llm": "test-llm"},
        }
    ],
    "current_llm": "test-llm",
    "test_setting": "test_value",
}

MOCK_AGENTS = {
    "BasicChatbotAgent": MagicMock(),  # We'll mock the actual agent module
}

# Fixtures
@pytest.fixture
def temp_config_file(tmp_path):
    """Creates a temporary config file for testing."""
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        json.dump(MOCK_CONFIG, f)
    return str(config_file)

@pytest.fixture
def mock_discover_agents():
    """Mocks the discover_agents function."""
    with patch("main.discover_agents", return_value=MOCK_AGENTS):
        yield

@pytest.fixture
def mock_input_selection():
    """Mocks user input for selection functions."""
    with patch("builtins.input", side_effect=["1"]):
        yield

# Test Cases

# Agent Discovery
def test_discover_agents_success(tmp_path, monkeypatch):
    """Tests that agents are discovered and imported correctly."""
    # Create dummy agent files
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "TestAgent1.py").write_text("class TestAgent1: pass")
    (agents_dir / "TestAgent2.py").write_text("class TestAgent2: pass")
    (agents_dir / "base_agent.py").write_text("class BaseAgent: pass")
    (agents_dir / "__init__.py").touch()

    # Patch the AGENTS_DIR to use the temporary directory
    monkeypatch.setattr("main.AGENTS_DIR", str(agents_dir))

    discovered_agents = discover_agents()

    assert "TestAgent1" in discovered_agents
    assert "TestAgent2" in discovered_agents
    assert "base_agent" not in discovered_agents # Ensure base_agent is excluded
    assert len(discovered_agents) == 2

def test_discover_agents_import_error(tmp_path, monkeypatch):
    """Tests that agent import errors are handled."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    # Create a dummy agent file with invalid syntax
    (agents_dir / "InvalidAgent.py").write_text("this is invalid syntax")
    (agents_dir / "__init__.py").touch()

    monkeypatch.setattr("main.AGENTS_DIR", str(agents_dir))

    # Mock print to capture error output
    with patch("builtins.print") as mock_print:
        discovered_agents = discover_agents()

    assert "InvalidAgent" not in discovered_agents
    mock_print.assert_called_with(
        f"Error importing InvalidAgent: invalid syntax (<unknown>, line 1)"
    )

# Configuration Loading and Saving
def test_load_config_success(temp_config_file, monkeypatch):
    """Tests that the config file is loaded correctly."""
    monkeypatch.setattr("main.CONFIG_FILE", os.path.basename(temp_config_file))
    config = load_config()
    assert config == MOCK_CONFIG

def test_save_config_success(temp_config_file, monkeypatch):
    """Tests that the config file is saved correctly."""
    monkeypatch.setattr("main.CONFIG_FILE", os.path.basename(temp_config_file))
    new_config = MOCK_CONFIG.copy()
    new_config["test_setting"] = "new_value"
    save_config(new_config)
    with open(temp_config_file, "r") as f:
        saved_config = json.load(f)
    assert saved_config == new_config

# Agent Execution (BasicChatbotAgent)
@pytest.mark.asyncio
async def test_basic_chatbot_agent_initialization_default():
    """Tests initialization of BasicChatbotAgent with default settings."""
    agent = BasicChatbotAgent()
    assert agent.model_type == "gemini"
    assert agent.model_name == "gemini-2.0-flash-exp"
    assert agent.settings.keep_context == True
    assert agent.settings.default_llm == "gemini-2.0-flash-exp"

@pytest.mark.asyncio
async def test_basic_chatbot_agent_initialization_custom():
    """Tests initialization of BasicChatbotAgent with custom settings."""
    custom_settings = ChatbotSettings(keep_context=False, default_llm="test-llm")
    agent = BasicChatbotAgent(
        model_type="openai",
        model_name="gpt-3.5-turbo",
        settings=custom_settings
    )
    assert agent.model_type == "openai"
    assert agent.model_name == "gpt-3.5-turbo"
    assert agent.settings.keep_context == False
    assert agent.settings.default_llm == "test-llm"

@pytest.mark.asyncio
async def test_basic_chatbot_agent_run_agent_valid_response():
    """Tests that run_agent returns a valid response."""
    agent = BasicChatbotAgent()
    mock_response = MagicMock()
    mock_response.data.text_response = "Test response"

    # Mock the agent's internal methods
    agent.create_agent = MagicMock()
    agent.create_agent.return_value.run = MagicMock(return_value=mock_response)

    response = await agent.run_agent("Test query")
    assert response == "Test response"

@pytest.mark.asyncio
async def test_basic_chatbot_agent_run_agent_keep_context():
    """Tests that run_agent respects keep_context setting."""
    agent = BasicChatbotAgent(settings=ChatbotSettings(keep_context=True))
    mock_response = MagicMock()
    mock_response.data.text_response = "Test response"

    # Mock the agent's internal methods
    agent.create_agent = MagicMock()
    agent.create_agent.return_value.run = MagicMock(return_value=mock_response)

    # Test with keep_context=True (explicitly provided)
    await agent.run_agent("Query 1", keep_context=True)
    agent.create_agent.return_value.run.assert_called_with("Query 1")

    # Test with keep_context=False (explicitly provided)
    await agent.run_agent("Query 2", keep_context=False)
    agent.create_agent.return_value.run.assert_called_with("Query 2")

    # Test with keep_context=None (using default from settings)
    await agent.run_agent("Query 3")
    agent.create_agent.return_value.run.assert_called_with("Query 3")

    # Now change settings and test again
    agent.settings.keep_context = False
    await agent.run_agent("Query 4")
    agent.create_agent.return_value.run.assert_called_with("Query 4")

@pytest.mark.asyncio
async def test_basic_chatbot_agent_run_interactive_chat(monkeypatch):
    """Tests the interactive chat mode."""
    # Mock user input and print
    inputs = ["Hello", "How are you?", "exit"]
    monkeypatch.setattr("builtins.input", lambda _: inputs.pop(0))
    prints = []
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: prints.append(" ".join(map(str, args))))

    agent = BasicChatbotAgent()

    # Mock the run_agent method
    async def mock_run_agent(query, keep_context):
        return f"Response to: {query}"

    agent.run_agent = mock_run_agent

    await agent.run_interactive_chat()

    assert "Welcome to the Interactive Chatbot!" in prints[0]
    assert "Goodbye! Have a great day!" in prints[-1]
    # You can add more assertions to check the interaction flow

def test_basic_chatbot_agent_invalid_model_type():
    """Tests that invalid model types are handled."""
    with pytest.raises(ValueError) as e:
        BasicChatbotAgent(model_type="invalid-model")
    assert "Invalid model_type: invalid-model." in str(e.value)

def test_basic_chatbot_agent_get_api_key(monkeypatch):
    """Tests that the API key is correctly retrieved."""
    monkeypatch.setenv("TEST_API_KEY", "test_key_value")
    agent = BasicChatbotAgent(api_key_env_var="TEST_API_KEY")
    assert agent.get_api_key() == "test_key_value"

    # Test auto-selection of API key environment variable
    monkeypatch.setenv("GEMINI_API_KEY", "gemini_key")
    agent = BasicChatbotAgent(model_type="gemini")
    assert agent.get_api_key() == "gemini_key"

    monkeypatch.setenv("OPENAI_API_KEY", "openai_key")
    agent = BasicChatbotAgent(model_type="openai")
    assert agent.get_api_key() == "openai_key"

    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic_key")
    agent = BasicChatbotAgent(model_type="anthropic")
    assert agent.get_api_key() == "anthropic_key"

    # Test missing API key
    monkeypatch.delenv("TEST_API_KEY", raising=False)
    agent = BasicChatbotAgent(api_key_env_var="TEST_API_KEY")
    with pytest.raises(ValueError) as e:
        agent.get_api_key()
    assert "TEST_API_KEY environment variable not set." in str(e.value)

def test_basic_chatbot_agent_get_model():
    """Tests that the correct LLM model is created."""
    agent = BasicChatbotAgent(model_type="gemini", model_name="gemini-pro")
    agent.get_api_key = MagicMock(return_value="dummy_key")  # Mock API key retrieval
    model = agent.get_model()
    assert isinstance(model, GeminiModel)

    agent.model_type = "openai"
    agent.model_name = "gpt-4"
    model = agent.get_model()
    assert isinstance(model, OpenAIModel)

    agent.model_type = "anthropic"
    agent.model_name = "claude-2"
    model = agent.get_model()
    assert isinstance(model, AnthropicModel)

    # Test invalid model type
    agent.model_type = "invalid"
    with pytest.raises(ValueError) as e:
        agent.get_model()
    assert "Unsupported model type: invalid" in str(e.value)

def test_basic_chatbot_agent_create_agent():
    """Tests that create_agent returns a valid Agent."""
    agent = BasicChatbotAgent(result_type=ChatResponse)
    agent.get_model = MagicMock()  # Mock model creation
    pydantic_agent = agent.create_agent()
    assert isinstance(pydantic_agent, Agent)

    # Test missing result_type
    agent.result_type = None
    with pytest.raises(ValueError) as e:
        agent.create_agent()
    assert "result_type must be defined in the derived class." in str(e.value)

# Menu and User Input
def test_show_menu_structure(temp_config_file, mock_discover_agents, mock_input_selection, monkeypatch):
    """Tests that the main menu displays correct options."""
    monkeypatch.setattr("main.CONFIG_FILE", os.path.basename(temp_config_file))
    config = load_config()

    with patch("main.select_llm") as mock_select_llm, \
            patch("main.select_agent") as mock_select_agent, \
            patch("main.change_setting") as mock_change_setting, \
            patch("main.show_help") as mock_show_help, \
            patch("builtins.input", side_effect=["5"]):  # Choose "Exit"
        show_menu(config, MOCK_AGENTS)

    # Assert that the correct functions were called based on user input
    assert mock_select_llm.call_count == 0
    assert mock_select_agent.call_count == 0
    assert mock_change_setting.call_count == 0
    assert mock_show_help.call_count == 0

def test_select_llm_success(temp_config_file, mock_input_selection, monkeypatch):
    """Tests that selecting an LLM updates the config."""
    monkeypatch.setattr("main.CONFIG_FILE", os.path.basename(temp_config_file))
    config = load_config()
    select_llm(config)
    assert config["current_llm"] == "test-llm"

def test_select_agent_success(mock_discover_agents, mock_input_selection):
    """Tests that selecting an agent returns the agent name."""
    selected_agent = select_agent(MOCK_AGENTS)
    assert selected_agent == "BasicChatbotAgent"

def test_show_help_output(mock_discover_agents, monkeypatch):
    """Tests the output of the show_help function."""
    prints = []
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: prints.append(" ".join(map(str, args))))

    # Mock the main_parser attribute for the agent
    MOCK_AGENTS["BasicChatbotAgent"].main_parser = MagicMock()
    MOCK_AGENTS["BasicChatbotAgent"].main_parser.description = "Test Agent Description"

    show_help(MOCK_AGENTS)

    assert "Available Agents:" in prints[0]
    assert "BasicChatbotAgent: Test Agent Description" in prints[1]

def test_get_selection_from_list_valid_input(monkeypatch):
    """Tests get_selection_from_list with valid input."""
    options = ["Option 1", "Option 2", "Option 3"]
    monkeypatch.setattr("builtins.input", lambda _: "2")  # Simulate user entering "2"
    choice = get_selection_from_list(options, "Select:")
    assert choice == "Option 2"

def test_get_selection_from_list_invalid_input(monkeypatch):
    """Tests get_selection_from_list with invalid input."""
    options = ["Option 1", "Option 2", "Option 3"]
    inputs = ["invalid", "5", "1"]  # First two are invalid, third is valid
    monkeypatch.setattr("builtins.input", lambda _: inputs.pop(0))
    prints = []
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: prints.append(" ".join(map(str, args))))

    choice = get_selection_from_list(options, "Select:")

    assert choice == "Option 1"
    assert "Invalid input. Please enter a number." in prints[-2]
    assert "Invalid choice. Please enter a number from the list." in prints[-1]

# CLI Tests
@patch("main.run_agent")
@patch("main.show_menu")
@patch("main.load_config", return_value=MOCK_CONFIG)
@patch("main.discover_agents", return_value=MOCK_AGENTS)
def test_main_no_args(mock_discover_agents, mock_load_config, mock_show_menu, mock_run_agent):
    """Tests running the script with no arguments."""
    main()
    mock_run_agent.assert_called_once_with(
        MOCK_AGENTS, "BasicChatbotAgent", MOCK_CONFIG, None
    )
    mock_show_menu.assert_not_called()

@patch("main.run_agent")
@patch("main.show_menu")
@patch("main.load_config", return_value=MOCK_CONFIG)
@patch("main.discover_agents", return_value=MOCK_AGENTS)
def test_main_menu_option(mock_discover_agents, mock_load_config, mock_show_menu, mock_run_agent):
    """Tests running the script with --menu."""
    main(menu=True, input_query="Test query")
    mock_show_menu.assert_called_once_with(MOCK_CONFIG, MOCK_AGENTS)
    mock_run_agent.assert_not_called()

@patch("main.run_agent")
@patch("main.show_menu")
@patch("main.load_config", return_value=MOCK_CONFIG)
@patch("main.discover_agents", return_value=MOCK_AGENTS)
def test_main_agent_option(mock_discover_agents, mock_load_config, mock_show_menu, mock_run_agent):
    """Tests running the script with --agent."""
    main(agent_name="BasicChatbotAgent", input_query="Test query")
    mock_run_agent.assert_called_once_with(
        MOCK_AGENTS, "BasicChatbotAgent", MOCK_CONFIG, ["Test query"]
    )
    mock_show_menu.assert_not_called()

@patch("main.run_agent")
@patch("main.show_menu")
@patch("main.load_config", return_value=MOCK_CONFIG)
@patch("main.discover_agents", return_value=MOCK_AGENTS)
def test_main_input_query(mock_discover_agents, mock_load_config, mock_show_menu, mock_run_agent):
    """Tests running the script with an input query."""
    main(input_query="Test query")
    mock_run_agent.assert_called_once_with(
        MOCK_AGENTS, "BasicChatbotAgent", MOCK_CONFIG, ["Test query"]
    )
    mock_show_menu.assert_not_called()