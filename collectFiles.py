import os
import shutil
import sys

def collect_sol_files(source_dir, target_dir):
    """
    Collects all .sol files from the source directory and its subdirectories
    and moves them to a target directory.
    
    Parameters:
    - source_dir (str): The path to the root directory to search for .sol files.
    - target_dir (str): The path to the directory where all collected .sol files will be moved.
    """
    # Create the target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Walk through the source directory and all subdirectories
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".sol"):
                # Construct the full path to the source file
                source_file = os.path.join(root, file)
                # Construct the full path to the target file
                target_file = os.path.join(target_dir, file)
                
                # Move or copy the file to the target directory
                shutil.move(source_file, target_file)
                print(f"Moved: {source_file} -> {target_file}")

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python collect_sol_files.py <source_directory> <target_directory>")
        sys.exit(1)

    # Get the source and target directories from command-line arguments
    source_directory = sys.argv[1]
    target_directory = sys.argv[2]

    # Run the file collection function
    collect_sol_files(source_directory, target_directory)
