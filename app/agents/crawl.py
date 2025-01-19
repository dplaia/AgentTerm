from pydantic import BaseModel, Field
from .base_agent import BaseAgent  # Import the BaseAgent
import argparse


def add_arguments(parser):
    """
    Adds agent-specific arguments to the argument parser.
    """
    parser.add_argument("task_description", help="The task description for the agent system.")

# The main_parser is used by the main program to generate help text for this agent.
main_parser = argparse.ArgumentParser(
    description="An agent that generates code for LLM agent systems using pydanticAI."
)
add_arguments(main_parser)

def main(args=None, config=None):
    """
    Main function to run the agent.
    """
    if args is None:
        args = main_parser.parse_args()


    
    output_file = "agent_system_template.py"

    # Save the code to a file
    with open(output_file, "w") as f:
        f.write(result.data.code.replace('\\n', '\n'))

    print(f"Code saved to {output_file}")

if __name__ == "__main__":
    main()