from pydantic import BaseModel, Field
from .base_agent import BaseAgent  # Import the BaseAgent
import argparse

class Response(BaseModel):
    code: str = Field(description="The code for the agent system.")

class CodeGeneratorAgent(BaseAgent):
    model_name: str = "gemini-2.0-flash-exp"  # You can override if needed
    system_prompt: str = """You are an expert in building LLM agent systems.
        After given a task description, you will use the pydanticAI framework to design an agent system by writing the code for the agent system.
        Make sure that you make use of all features of PydanticAI in the best way possible.
        If you are not sure how to implement the certain features, tools or functions, add some comments to the code to explain what could be done.
        """
    result_type: type[BaseModel] = Response
    examples_file: str = "extented_agent_system_examples.txt" # path is relative to the agent1.py file

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

    agent = CodeGeneratorAgent()
    result = agent.run_agent(args.task_description)
    
    output_file = "agent_system_template.py"

    # Save the code to a file
    with open(output_file, "w") as f:
        f.write(result.data.code.replace('\\n', '\n'))

    print(f"Code saved to {output_file}")

if __name__ == "__main__":
    main()