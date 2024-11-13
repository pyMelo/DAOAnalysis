import os
import re
from pathlib import Path

def clean_imports(directory):
    """
    Process all .sol files in the given directory and modify their import statements
    to use only the filename with ./ prefix.
    """
    # Get all .sol files in the directory
    sol_files = Path(directory).glob('**/*.sol')
    
    # Patterns for both types of imports, capturing the filename and any symbols
    patterns = [
        # For imports with symbols: import {X} from "path/file.sol";
        (
            r'import\s*({[^}]+})\s*from\s*"([^"]+)"',
            lambda m: f'import {m.group(1)} from "./{os.path.basename(m.group(2))}"'
        ),
        # For direct imports: import "path/file.sol";
        (
            r'import\s*"([^"]+)"',
            lambda m: f'import "./{os.path.basename(m.group(1))}"'
        )
    ]
    
    for sol_file in sol_files:
        try:
            # Read file content
            with open(sol_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified_content = content
            modified = False
            
            # Apply each replacement pattern
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, modified_content)
                if new_content != modified_content:
                    modified = True
                    modified_content = new_content
            
            # If changes were made, write back to file
            if modified:
                with open(sol_file, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                print(f"\nModified: {sol_file}")
                print("Changes made:")
                # Show the changes
                old_imports = re.findall(r'import.*?;', content, re.MULTILINE)
                new_imports = re.findall(r'import.*?;', modified_content, re.MULTILINE)
                for old, new in zip(old_imports, new_imports):
                    print(f"Old: {old.strip()}")
                    print(f"New: {new.strip()}\n")
                    
        except Exception as e:
            print(f"Error processing {sol_file}: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    clean_imports(directory)