import os
import glob
import importlib
import argparse
import json
import sys

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
            if run_selected_agent.lower() == "y":
                run_agent(agents, selected_agent_name, config)
        elif selected_option.startswith("Change"):
            setting_name = selected_option.split(" ", 1)[1]
            change_setting(config, setting_name)
        elif selected_option == "Help":
            show_help(agents)
        elif selected_option == "Exit":
            break

def run_agent(agents, agent_name, config, agent_args=None):
    """Runs the specified agent with the given arguments."""
    agent_module = agents.get(agent_name)
    if not agent_module:
        print(f"Agent '{agent_name}' not found.")
        return

    try:
        # Get the agent class dynamically
        agent_class_name = agent_name # agent_name.capitalize() + "Agent" # Assumes class name follows convention
        agent_class = getattr(agent_module, agent_class_name)

        # Instantiate the agent, potentially passing config if needed
        agent_instance = agent_class()

        # Use agent's specific argument parser if available
        if hasattr(agent_module, 'main_parser'):
            agent_parser = agent_module.main_parser
            agent_args = agent_parser.parse_args(agent_args)
        else:
            agent_parser = None
            if agent_args:
                print("Warning: This agent does not accept arguments.")
            agent_args = None

        if hasattr(agent_instance, 'run_agent'):
            # Handle any setup needed before calling run_agent
            # For example, you might need to set attributes based on config or agent_args

            # Execute the run_agent method
            if agent_parser:
                result = agent_instance.run_agent(agent_args)
            else:
                result = agent_instance.run_agent()
        else:
            raise Exception(f"Agent {agent_name} does not have a run_agent method.")

        # Handle the result based on the agent's logic
        # ...

    except Exception as e:
        print(f"Error running agent {agent_name}: {e}")

def main():
    """Main function of the agent manager."""
    config = load_config()
    agents = discover_agents()

    parser = argparse.ArgumentParser(
        description="LLM Agent Manager", add_help=False
    )
    parser.add_argument(
        "agent_name", nargs="?", help="Name of the agent to run"
    )
    parser.add_argument(
        "-m", "--menu", action="store_true", help="Show interactive menu"
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="Show this help message"
    )

    # Peek at the arguments to check for agent-specific help
    args, remaining_args = parser.parse_known_args()

    if args.help:
        if args.agent_name:
            # Handle agent-specific help
            agent_module = agents.get(args.agent_name)
            if agent_module:
                agent_module.main_parser.print_help()
                sys.exit(0)
            else:
                print(f"Agent '{args.agent_name}' not found.")
                sys.exit(1)
        else:
            # Show main program help
            parser.print_help()
            show_help(agents)
            sys.exit(0)
    elif args.menu:
        show_menu(config, agents)
    elif args.agent_name:
        run_agent(agents, args.agent_name, config, remaining_args)
    else:
        # Use BasicChatbotAgent as default
        run_agent(agents, "BasicChatbotAgent", config, None)
 
if __name__ == "__main__":
    main()