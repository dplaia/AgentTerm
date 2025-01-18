import os
import glob
import importlib
import json
import argparse
from rich import print
from typing import Optional
from typing_extensions import Annotated
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.application import create_app_session
from prompt_toolkit.application.current import get_app
import asyncio
from agents.BasicChatbotAgent import BasicChatbotAgent

# Constants
AGENTS_DIR = "agents"
CONFIG_FILE = "config.json"

def discover_agents():
    """Finds and imports agent modules from the agents directory."""
    agent_files = glob.glob(os.path.join(AGENTS_DIR, "*.py"))
    agents = {}
    for agent_file in agent_files:
        module_name = os.path.splitext(os.path.basename(agent_file))[0]
        try:
            module = importlib.import_module(f"{AGENTS_DIR}.{module_name}")
            agents[module_name] = module
        except Exception as e:
            print(f"Error importing {module_name}: {e}")
    return agents

def load_config():
    """Loads configuration from config.json."""
    config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
    with open(config_path, "r") as f:
        config = json.load(f)
    return config

def save_config(config):
    """Saves the configuration to config.json."""
    config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

def show_help(agents):
    """Displays help information for available agents."""
    print("Available Agents:")
    for agent_name, module in agents.items():
        if agent_name == "base_agent":
            # Skip the BaseAgent module
            continue

        if hasattr(module, "main"):
            # Get help text from the agent's main function
            try:
                parser = module.main_parser
                help_text = (
                    parser.description
                    if parser.description
                    else "No description available."
                )
            except Exception:
                help_text = "No help text defined."

            print(f"  {agent_name}: {help_text}")
        else:
            print(f"  {agent_name}: No main function found.")

def select_llm(config):
    """Allows the user to select an LLM from the configuration."""
    llms = config.get("llms", [])
    if not llms:
        print("No LLMs configured.")
        return

    llm_names = [llm["name"] for llm in llms]
    selected_llm_name = get_selection_from_list(llm_names, "Select LLM:")

    # Update the currently selected LLM
    config["current_llm"] = selected_llm_name
    save_config(config)
    print(f"Selected LLM: {selected_llm_name}")

def change_setting(config, setting_name):
    """Allows the user to change a setting (generic function)."""
    # You'll need to customize this based on your specific settings
    # ... (Implementation for changing a setting) ...

def select_agent(agents):
    """Allows the user to select an agent from the discovered agents."""
    agent_names = list(agents.keys())
    selected_agent_name = get_selection_from_list(agent_names, "Select Agent:")

    return selected_agent_name

def get_selection_from_list(options, prompt):
    """Gets a selection from a list of options using a simple cross-platform menu."""
    print(prompt)
    for i, option in enumerate(options):
        print(f"{i + 1}. {option}")

    while True:
        try:
            choice = int(input("Enter your choice: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Please enter a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def show_menu(config, agents):
    """Displays the main menu."""
    options = ["Select LLM", "Select Agent"]
    # Add other settings to the options list
    for setting_name in config.keys():
        if setting_name not in ["llms", "current_llm"]:
            options.append(f"Change {setting_name}")
    options.extend(["Help", "Exit"])

    while True:
        selected_option = get_selection_from_list(options, "Main Menu:")

        if selected_option == "Select LLM":
            select_llm(config)
        elif selected_option == "Select Agent":
            selected_agent_name = select_agent(agents)
            print(f"Selected Agent: {selected_agent_name}")
            run_selected_agent = input(
                f"Run agent {selected_agent_name} now? (y/n): "
            )
            # if run_selected_agent.lower() == "y":
            #     asyncio.run(run_agent(agents, selected_agent_name, config))
        elif selected_option.startswith("Change"):
            setting_name = selected_option.split(" ", 1)[1]
            change_setting(config, setting_name)
        elif selected_option == "Help":
            show_help(agents)
        elif selected_option == "Exit":
            break

async def run_agent(agents, agent_name, config, agent_args=None):
    """Runs the specified agent with the given arguments."""
    agent_module = agents.get(agent_name)
    if not agent_module:
        print(f"Agent '{agent_name}' not found.")
        return

    try:
        # Get the agent class dynamically
        agent_class_name = agent_name
        agent_class = getattr(agent_module, agent_class_name)

        # Get agent settings from config if available
        agent_config = next(
            (
                agent
                for agent in config.get("agents", [])
                if agent["name"] == agent_name
            ),
            None,
        )

        # Instantiate the agent with settings from config
        if agent_config and "settings" in agent_config:
            agent_instance = agent_class(settings=agent_config["settings"])
        else:
            agent_instance = agent_class()

        if hasattr(agent_instance, "run_agent"):
            if agent_args:
                result = await agent_instance.run_agent(agent_args[0])
                print(f"\n·>: {result}\n")
            else:
                # Start interactive mode
                await run_interactive_chat(agent_instance)
        else:
            raise Exception(
                f"Agent {agent_name} does not have a run_agent method."
            )

    except Exception as e:
        print(f"Error running agent {agent_name}: {e}")

async def run_interactive_chat(agent=None):
    """
    Run an interactive chat session with the chatbot.

    Args:
        agent: An instance of BasicChatbotAgent. If None, a new instance will be created.
    """
    # Create a prompt session with custom style
    style = Style.from_dict(
        {
            "prompt": "#00aa00 bold",
        }
    )
    session = PromptSession(style=style)

    print("\nWelcome to the Interactive Chatbot!")
    print(
        "You can start chatting now. Type 'exit' or 'quit' to end the conversation.\n"
    )

    if agent is None:
        # Create a default agent if none was provided
        
        agent = BasicChatbotAgent()

    while True:
        try:
            # Use prompt_toolkit's async prompt
            user_input = await session.prompt_async("·>>>: ")
            user_input = user_input.strip()

            if user_input.lower() in ["exit", "quit"]:
                print("\n\nConversation ended.")
                break

            if user_input.lower() in ["reset", "clear"]:
                # clear terminal
                print("\033c")
                # Clear the message history
                if agent:
                    agent.save_messages([])
                continue

            response = await agent.run_agent(user_input)
            print(f"\n{response}\n")

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

def main():
    """Main function of the agent manager."""
    parser = argparse.ArgumentParser(description="Agent Terminal")
    parser.add_argument("input_query", nargs="?", help="Input query for the agent")
    parser.add_argument("--agent", "-a", help="Name of the agent")
    parser.add_argument("--menu", action="store_true", help="Display the main menu")
    
    args = parser.parse_args()

    async def async_main():
        try:
            config = load_config()
            agents = discover_agents()

            if not agents:
                print("[red]No agents found in the agents directory.[/red]")
                return

            if args.menu:
                show_menu(config, agents)
                return

            if args.agent:
                await run_agent(agents, args.agent, config, args.input_query)
            elif args.input_query:
                await run_agent(agents, "BasicChatbotAgent", config, args.input_query)
            else:
                # Run interactive chat when no arguments are provided
                with create_app_session():
                    await run_interactive_chat()

        except Exception as e:
            print(f"[red]Error: {str(e)}[/red]")

    # Get the current event loop or create a new one
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(async_main())
    finally:
        loop.close()

if __name__ == "__main__":
    main()