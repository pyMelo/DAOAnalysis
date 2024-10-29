import os
import subprocess
import sys

def estimate_cost_for_directory(directory, script_path='estimate-b.js'):
    """
    Runs the Node.js script for each .sol file in the given directory.

    :param directory: Path to the directory containing Solidity contracts.
    :param script_path: Path to the Node.js script that estimates the cost.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.sol'):
                contract_path = os.path.join(root, file)
                print(f"\nEstimating deployment cost for: {contract_path}")
                try:
                    # Call the Node.js script using subprocess and show output directly in the terminal
                    subprocess.run(['node', script_path, contract_path], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error estimating cost for {file}:\n{e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 script_name.py <directory-path>")
        sys.exit(1)
    
    directory_to_scan = sys.argv[1]
    estimate_cost_for_directory(directory_to_scan)
