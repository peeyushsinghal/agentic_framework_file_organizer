SYSTEM_PROMPT_TEMPLATE = """
You are given a task, you need to sub-divide the task into smaller sub-tasks.
You need to provide a list of sub-tasks that are needed to complete the task in the best possible way.
Keep it simple and concise and provide the list of sub-tasks in a list format and plain text.
"""

TASK_INITIATION_TEMPLATE = """
Task is to scan a folder, move the same type of files to respective folders.
Files are of the type of PDF, PNG, JPG.
Then compress the files within the same folder.
Keep it simple and concise.
"""

SYSTEM_PROMPT_TEMPLATE_WITH_FUNCTIONS = """
You are given a task, you need to sub-divide the task into smaller sub-tasks.
You need to provide a list of sub-tasks that are needed to complete the task in the best possible way.
Keep it simple and concise and provide the list of sub-tasks in a list format and plain text.

You are also given a list of functions and their information.
You need to use the functions to complete the task.
"""

FUNCTION_INFORMATION_TEMPLATE = """
Task is to scan a folder {input_folder_path}, move the same type of files to respective folders within output folder {output_folder_path}.
Only create folders if they don't exist and based on the file type.
Files are likely to be of the type of PDF, PNG, JPG.
Then compress the files within the same folder (i.e. the output folder). 

You are given a list of functions and their information. You need to use the functions to complete the task.
You need to provide the sequence of functions that are needed to complete the task in the best possible way.
Keep it simple and concise.

list of functions:
{functions_information}

Each function in the return argument provide a boolean value to indicate if the function is successful or not.
Use the boolean value to determine if the function is successful or not and provide the python code to complete the sub-tasks by using the functions as per the sequence of functions.
Also, raise appropriate error / exception if the function is not successful.
provide the python code to complete the sub-tasks by using the functions as per the sequence of functions.
Do not use any functions that are not in the list of functions to complete the sub-tasks.
"""
