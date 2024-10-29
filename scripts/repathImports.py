import os
import re

def update_imports_in_sol_files(directory):
    """
    This function goes through all .sol files in the specified directory and its subdirectories,
    and updates the import paths by removing directory paths.
    
    Example:
    - Before: import "../../proxy/utils/Initializable.sol";
    - After:  import "./Initializable.sol";
    
    Parameters:
    - directory (str): The path to the root directory containing .sol files.
    """
    # Regular expression to match import statements
    import_regex = re.compile(r'import\s+["\'].*\/([^\/]+\.sol)["\'];')

    # Walk through all files in the specified directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".sol"):
                file_path = os.path.join(root, file)
                
                # Read the content of the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace import statements using the regex
                updated_content = re.sub(import_regex, r'import "./\1";', content)
                
                # If changes were made, write the updated content back to the file
                if updated_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    print(f"Updated imports in: {file_path}")

if __name__ == "__main__":
    # Define the directory containing the Solidity files
    directory_path = "/home/melo/Desktop/DAOProject/contracts"  # Replace with your directory path
    update_imports_in_sol_files(directory_path)
