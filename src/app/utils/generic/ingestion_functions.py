import ast

def user_text_prompt_ingestion(file_path: str):
    '''takes a python list text file that breaks up user prompts and structures them in a list'''


    with open(file_path, "r", encoding="utf-8") as file:
        file_contents = file.read()
        python_list = ast.literal_eval(file_contents)

    return python_list

def model_context_ingestion(file_path:str, 
                            context_type:str):
    
    if context_type == 'request_classification':
        with open(file_path, "r", encoding="utf-8") as file:
        
            file_contents = file.read()
        return file_contents

