def load_config(config_path: str = "src/file_manager_config.yml") -> dict:
    """
    Load the configuration from the given path.

    Args:
        config_path (str): The path to the configuration file

    Returns:
        dict: The configuration as a dictionary

    Error Scenarios:
        - If config_path is None or empty: Returns None
        - If config_path is invalid: Returns None
        - If config file is not found: Returns None
        - If config file is not a valid YAML file: Returns None

    Return Scenarios:
        - If config file is valid: Returns the configuration as a dictionary
    """
    import yaml

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def folder_scanner(folder_path: str) -> tuple[list[str], bool]:
    """
    Scan the specified folder and return the list of files along with existence status.

    This method checks if the given folder path exists and returns all files/directories
    within that folder if it does, excluding hidden files (starting with .).
    If the folder doesn't exist, returns an empty list.

    Args:
        folder_path (str): The absolute or relative path to the folder to scan

    Returns:
        tuple[list[str], bool]: A tuple containing:
            - list[str]: List of filenames in the folder if it exists, empty list otherwise
            - bool: True if folder exists, False if it doesn't

    Error Scenarios:
        - If folder_path is None or empty: Returns ([], False)
        - If folder_path doesn't exist: Returns ([], False)
        - If folder_path exists but no read permissions: Returns ([], False)

    Return Scenarios:
        - Successful scan: (['file1.txt', 'file2.jpg'], True)
        - Folder doesn't exist: ([], False)
        - Empty folder: ([], True)
    """
    import os

    if os.path.exists(folder_path):
        files = [f for f in os.listdir(folder_path) if not f.startswith(".")]
        return files, True
    else:
        return [], False


def file_type_identifier(file_path: str) -> tuple[str, bool]:
    """
    Identify and return the file extension from the given file path.

    This method extracts the file extension (without the dot) from a file path.
    For example, for 'document.pdf' it returns 'pdf'.

    Args:
        file_path (str): The path to the file whose type needs to be identified

    Returns:
        tuple[str, bool]: A tuple containing:
            - str: The file extension without the dot (e.g. 'pdf', 'png', 'jpg')
            - bool: True if file extension is found, False otherwise

    Error Scenarios:
        - If file_path is None: Returns ''
        - If file_path is empty string: Returns ''
        - If file_path has no extension: Returns ''
        - If file_path is invalid: Returns ''

    Return Scenarios:
        - Valid file with extension: 'pdf', 'png', 'jpg' etc.
        - File with no extension: ''
        - Hidden file (Unix): '.gitignore' returns ''
        - Multiple dots: 'archive.tar.gz' returns 'gz'
    """
    import os

    if not file_path:
        return "", False
    extension = os.path.splitext(file_path)[1]
    if extension.startswith("."):
        extension = extension[1:]
    return extension.upper(), extension != ""


def folder_creator(folder_path: str, file_type: str = None) -> bool:
    """
    Create new folders for each file type (PDF, JPG, PNG) if they don't exist.

    This method checks if folders for each file type exist at the given base path.
    If they don't exist, it creates directories for each file type.

    Args:
        folder_path (str): The base path where file type folders should be created
        Optional: file_type (str): The file type to create a folder for
    Returns:
        bool: True if any folders were created, False if all already existed

    Error Scenarios:
        - If folder_path is None or empty: Returns False
        - If folder_path is invalid: Returns False
        - If no write permissions: Returns False
        - If file_type is invalid: Returns False

    Return Scenarios:
        - All folders already exist: Returns False
        - Some folders created: Returns True
        - All folders created: Returns True
        - Creation failed: Returns False
    """
    import os

    config = load_config()

    folders_created = False

    if file_type is None:
        file_types = config["file_types"]
    else:
        file_types = [file_type]

    for file_type in file_types:
        type_folder = os.path.join(folder_path, file_type)
        try:
            if not os.path.exists(type_folder):
                os.makedirs(type_folder)
                folders_created = True
        except Exception as e:
            print(f"Error creating folder {type_folder}: {e}")
            continue
    return folders_created


def file_mover(
    source_file_path: str, target_base_path: str, file_type: str
) -> tuple[str, bool]:
    """
    Move the file to the appropriate categorized folder based on file extension.

    Args:
        source_file_path: Path of the file to move
        target_base_path: Base directory where categorized folders will be created
        file_type: File type to move

    Returns:
        tuple[str, bool]: A tuple containing:
            - str: Path of the compressed file if successful, empty string otherwise
            - bool: True if file was moved successfully, False otherwise

    Error Scenarios:
        - If source_file_path doesn't exist: Returns ("", False)
        - If target_base_path is invalid: Returns ("", False)

    Return Scenarios:
        - Successful move & compression: ("/path/to/compressed.jpg", True)
        - File doesn't exist: ("", False)
        - Move failed: ("", False)
    """
    import os
    import shutil

    if not os.path.exists(source_file_path):
        return "", False

    category_folder = os.path.join(target_base_path, file_type)

    if not os.path.exists(category_folder):
        folder_creator(target_base_path, file_type)

    # Get filename and extension
    file_name = os.path.splitext(os.path.basename(source_file_path))[0]
    file_ext = os.path.splitext(source_file_path)[1]
    new_file_path = os.path.join(category_folder, file_name + file_ext)

    try:
        # Move file to category folder
        shutil.move(source_file_path, new_file_path)
        return new_file_path, True
    except Exception:
        return "", False


def file_compressor(file_path: str) -> tuple[str, bool]:
    """
    Compress the file using the configured compression method for the file type.

    Args:
        file_path: Path of the file to compress

    Returns:
        tuple[str, bool]: A tuple containing:
            - str: Path of the compressed file if successful, empty string otherwise
            - bool: True if file was compressed successfully, False otherwise

    Error Scenarios:
        - If file_path is None or empty: Returns ("", False)
        - If file_path doesn't exist: Returns ("", False)
        - If file_path is invalid: Returns ("", False)
        - If file type is not supported: Returns ("", False)
        - If compression method is not supported: Returns ("", False)
        - If compression fails: Returns ("", False)

    Return Scenarios:
        - Successful compression: ("/path/to/compressed.jpg", True)
        - File doesn't exist: ("", False)
    """
    import os
    from dotenv import load_dotenv
    load_dotenv()

    config = load_config()

    if not os.path.exists(file_path):
        return "", False

    # Get file type and name
    file_type = os.path.splitext(os.path.basename(file_path))[-1].strip(".").upper()
    file_name = os.path.splitext(os.path.basename(file_path))[0]


    # Get compression method from config
    compression_methods = config["compression_method"]
    compression_method = None
    for method in compression_methods:
        if file_type in method:
            compression_method = method[file_type]
            break
    

    if not compression_method:
        return "", False
    

    try:
        compressed_name = f"{file_name}_compressed"
        compressed_name += f'.{file_type.lower()}'
        new_file_path = os.path.join(os.path.dirname(file_path), compressed_name)

        if compression_method == "zip":
            import zipfile

            with zipfile.ZipFile(new_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, os.path.basename(file_path))
            return new_file_path, True
        
        if compression_method == "tinypng":
            print(f"Compressing {file_name}.{file_type.lower()} using tinypng")
            import os
            import tinify
            
            tinify.key = os.getenv("TINYPNG_API_KEY")
            try:
                source = tinify.from_file(file_path)
                compressed = source.to_file(new_file_path)
                # print(f"Compressed {file_path} to {new_file_path}, compression ratio: {os.path.getsize(file_path) / os.path.getsize(new_file_path)}")
                return new_file_path, True
            except Exception as e:
                print(f"Error compressing {file_path} using tinypng: {e}")
                return "", False
            
               
        if compression_method == "convertapi":
            print(f"Compressing {file_name}.{file_type.lower()} using convertapi")
            import requests
            import os
            import base64
            
            convertapi_url = config["convertapi_url"]
  
            with open(file_path, 'rb') as f:
                encoded_file = base64.b64encode(f.read()).decode('utf-8')

            payload = {
                "Parameters": [
                    {
                        "Name": "File",
                        "FileValue": {
                            "Name": file_path.split("/")[-1],
                            "Data": encoded_file
                        }
                    }
                ]
            }
            try:
                api_key = os.getenv("CONVERTAPI_API_KEY")
            except Exception as e:
                print(f"Error getting convertapi api key: {e}")
                return "", False

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(convertapi_url,
                                     json=payload,
                                     headers=headers)

            if response.status_code == 200:
                response_data = response.json()
                if 'Files' in response_data and len(response_data['Files']) > 0:
                    file_data = response_data['Files'][0]['FileData']
                    
                    # Decode the base64 data
                    decoded_data = base64.b64decode(file_data)
                    
                    
                    with open(new_file_path, 'wb') as f:
                        f.write(decoded_data)
                    
                    return new_file_path, True
                
            return "", False

            
        # Add other compression methods as needed

        return "", False

    except Exception:
        return "", False


# if __name__ == "__main__":
#     import os

#     # Get the path to the data folder relative to this script
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     project_root = os.path.dirname(current_dir)
#     data_folder = os.path.join(project_root, "data", "input_folder")
#     print(data_folder)
#     file_path = os.path.join(data_folder, "sample.pdf")
#     print(file_path)
#     compressed_file_path, success = file_compressor(file_path)
#     print(compressed_file_path,success)
# print(data_folder)

# config = load_config(os.path.join(current_dir, "file_manager_config.yml"))

# file_list, _ = folder_scanner(folder_path=data_folder)
# print(file_list)
# for file in file_list:
#     print(file)
#     file_type, _ = file_type_identifier(file_path=os.path.join(data_folder, file))
#     print(file_type)
#     print("--------------------------------")
