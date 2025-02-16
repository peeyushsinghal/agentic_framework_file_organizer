import yaml
import os
import requests
from google import genai
from google.genai import types

from prompts import *

# from file_manager import *
import inspect


class AgentFileManager:
    def __init__(
        self, config_path: str = "agentic_config.yml", print_config: bool = False
    ):
        # Get the directory of the current file (agent_file_manager.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # If config_path is relative, make it absolute relative to current directory
        if not os.path.isabs(config_path):
            config_path = os.path.join(current_dir, config_path)

        # load config
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file {config_path} not found")

        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

        if print_config:
            print(self.config)

        # Get the directory containing the config file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(config_path)))
        
        # Convert relative paths to absolute paths
        self.config["functions_file_path"] = os.path.join(base_dir, self.config["functions_file_path"])
        self.config["input_folder_path"] = os.path.join(base_dir, self.config["input_folder_path"])
        self.config["output_folder_path"] = os.path.join(base_dir, self.config["output_folder_path"])

        # Create input and output directories if they don't exist
        os.makedirs(self.config["input_folder_path"], exist_ok=True)
        os.makedirs(self.config["output_folder_path"], exist_ok=True)

        self.model = self.config["llm"]["model"]
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google GEN AI API_KEY is not set in the environment variables"
            )

    def generate_sub_tasks(self):
        try:
            client_generate_sub_tasks = genai.Client(api_key=self.api_key)
        except Exception as e:
            print("Error initializing Google API client:", e)

        response = client_generate_sub_tasks.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                max_output_tokens=self.config["llm"]["max_output_tokens"],
                temperature=self.config["llm"]["temperature"],
                system_instruction=SYSTEM_PROMPT_TEMPLATE,
            ),
            contents=[TASK_INITIATION_TEMPLATE],
        )
        print(response.text)

    def get_functions_list(self) -> list[str]:
        """
        Get a list of all function names defined in the specified Python file.

        Args:
            file_path (str): Path to the Python file to analyze

        Returns:
            list[str]: List of function names found in the file

        Error Scenarios:
            - If file_path doesn't exist: Returns empty list
            - If file_path is not a Python file: Returns empty list
            - If file can't be read: Returns empty list

        Return Scenarios:
            - Successful: Returns list of function names
            - No functions found: Returns empty list
        """
        import ast

        try:
            with open(self.config["functions_file_path"], "r") as file:
                tree = ast.parse(file.read())

            return [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
            ]
        except Exception as e:
            print(f"Error reading file {self.config['functions_file_path']}: {e}")
            return []

    def get_function_information(
        self, functions_list: list[str] = None
    ) -> dict[str, dict]:
        function_information = {}
        if not functions_list:
            functions_list = self.get_functions_list()

        # Import the module containing the functions
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "functions_module", self.config["functions_file_path"]
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for function_name in functions_list:
            # Get the actual function object from the module
            function = getattr(module, function_name)
            function_information[function_name] = {
                "usage": function.__doc__,
                "arguments": str(inspect.signature(function)),
                "return_type": str(inspect.signature(function).return_annotation),
            }
        return function_information

    def generate_sub_tasks_with_functions(
        self, functions_information: dict[str, dict] = None
    ):
        if not functions_information:
            functions_information = self.get_function_information()

        # Initialize Google API client, so that no context is shared with the previous client
        try:
            client_generate_sub_tasks_with_functions = genai.Client(
                api_key=self.api_key
            )
        except Exception as e:
            print("Error initializing Google API client:", e)

        response = client_generate_sub_tasks_with_functions.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                max_output_tokens=self.config["llm"]["max_output_tokens"],
                temperature=self.config["llm"]["temperature"],
                system_instruction=SYSTEM_PROMPT_TEMPLATE_WITH_FUNCTIONS,
            ),
            contents=[
                FUNCTION_INFORMATION_TEMPLATE.format(
                    input_folder_path=self.config["input_folder_path"],
                    output_folder_path=self.config["output_folder_path"],
                    functions_information=functions_information,
                )
            ],
        )
        print(response.text)
        return response.text

    def extract_python_code_from_response(self, response: str) -> str:
        # Extract the python code from the response
        # The python code is the code that is between the ```python and ``` tags
        # If no ```python and ``` tags are found, return the response
        # If multiple ```python and ``` tags are found, return the one in the middle
        # If no ```python and ``` tags are found, return the response
        import re

        code_blocks = re.findall(r"```python\n(.*?)```", response, re.DOTALL)
        if code_blocks:
            return code_blocks[0]
        else:
            return response

    def execute_python_code_safely(self, python_code: str) -> str:
        import importlib.util
        import os, sys  # We need these for path operations

        # Get the current file's directory and add it to sys.path
        current_dir = os.path.dirname(os.path.abspath(self.config["functions_file_path"]))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # Import the module containing the functions
        module_name = os.path.splitext(os.path.basename(self.config["functions_file_path"]))[0]
        spec = importlib.util.spec_from_file_location(
            module_name, self.config["functions_file_path"]
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Create restricted environment with all module attributes
        restricted_locals = {}
        for name in dir(module):
            if not name.startswith('_'):  # Skip private attributes
                restricted_locals[name] = getattr(module, name)

        # Add required modules and variables
        restricted_locals['os'] = os
        restricted_locals['sys'] = sys
        restricted_locals['__file__'] = self.config["functions_file_path"]
        
        # Explicitly add folder_scanner and other functions to globals
        restricted_globals = {
            '__builtins__': {
                '__import__': __import__,
                '__build_class__': __build_class__,
                '__name__': __name__,
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'Exception': Exception,
                'TypeError': TypeError,
                'ValueError': ValueError,
                'AttributeError': AttributeError,
                'FileNotFoundError': FileNotFoundError,
                'OSError': OSError,
            }
        }
        # Add all module functions to globals as well
        restricted_globals.update(restricted_locals)

        # print(f"Debug - Available functions in globals: {list(restricted_globals.keys())}")
        # print(f"Debug - Available functions in locals: {list(restricted_locals.keys())}")

        try:
            exec(python_code, restricted_globals, restricted_locals)
        except Exception as e:
            print(f"Error executing python code: {e}")
            print(f"Available functions: {list(restricted_locals.keys())}")
            return str(e)

        return "Code executed successfully"

    def test_llm(self):
        response = self.client.models.generate_content(
            model=self.model, contents=["What is the meaning of life? succinctly"]
        )

        print(response.text)


if __name__ == "__main__":
    agent_file_manager = AgentFileManager()

    # agent_file_manager.test_llm()
    # agent_file_manager.generate_sub_tasks()
    # functions_list = agent_file_manager.get_functions_list()
    # print(functions_list)
    # functions_information = agent_file_manager.get_function_information()
    # for key, value in functions_information.items():
    #     print(f"function name: {key}")
    #     print(f'function usage: {value["usage"]}')
    #     print(f'function arguments: {value["arguments"]}')
    #     print(f'function return type: {value["return_type"]}')
    #     print('--------------------------------')

    response_text = agent_file_manager.generate_sub_tasks_with_functions()
    python_code = agent_file_manager.extract_python_code_from_response(response_text)
    # print(python_code)

    output = agent_file_manager.execute_python_code_safely(python_code)
    print(output)
