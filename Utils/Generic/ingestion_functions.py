import ast

def user_text_prompt_ingestion(file_path):
    '''takes a python list text file that breaks up user prompts and structures them in a list'''


    with open(file_path, "r", encoding="utf-8") as file:
        file_contents = file.read()
        python_list = ast.literal_eval(file_contents)

    return python_list

def model_context_ingestion(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        file_contents = file.read()

    return file_contents
