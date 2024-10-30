import os
import subprocess
import sys
import re
import csv

def parse_output(contract_name, output, error_message=None):
    """
    Parses the output from the Node.js script to extract the required data.
    
    :param contract_name: The name of the contract file.
    :param output: The output string from the Node.js script.
    :param error_message: Error message, if any.
    :return: A dictionary with the parsed values.
    """
    parsed_data = {
        "Contract Name": contract_name,
        "Bytecode Length": "undefined",
        "Estimated Gas Units": "undefined",
        "Gas Price (Gwei)": "undefined",
        "Priority Fee (Gwei)": "undefined",
        "ETH Price (USD)": "undefined",
        "Deployment Cost (ETH)": "undefined",
        "Deployment Cost (USD)": "undefined",
        "Standard Method": False,
        "Bytesize Method": False,
        "Status": "Error" if error_message else "Success",
        "Error Message": error_message if error_message else ""
    }

    # Parse each field using regex patterns
    if not error_message:
        bytecode_match = re.search(r'Contract Bytecode Length: (\d+) characters', output)
        if bytecode_match:
            parsed_data["Bytecode Length"] = bytecode_match.group(1)

        gas_units_match = re.search(r'Estimated Gas Units: (\d+)', output)
        if gas_units_match:
            parsed_data["Estimated Gas Units"] = gas_units_match.group(1)

        gas_price_match = re.search(r'Gas Price: ([\d.]+) gwei', output)
        if gas_price_match:
            parsed_data["Gas Price (Gwei)"] = gas_price_match.group(1)

        priority_fee_match = re.search(r'Priority Fee: ([\d.]+) gwei', output)
        if priority_fee_match:
            parsed_data["Priority Fee (Gwei)"] = priority_fee_match.group(1)

        eth_price_match = re.search(r'ETH Price: \$(\d+\.\d+) USD', output)
        if eth_price_match:
            parsed_data["ETH Price (USD)"] = eth_price_match.group(1)

        deploy_cost_eth_match = re.search(r'Estimated Deployment Cost: ([\d.]+) ETH', output)
        if deploy_cost_eth_match:
            parsed_data["Deployment Cost (ETH)"] = deploy_cost_eth_match.group(1)

        deploy_cost_usd_match = re.search(r'\(~\$(\d+\.\d+)\sUSD\)', output)
        if deploy_cost_usd_match:
            parsed_data["Deployment Cost (USD)"] = deploy_cost_usd_match.group(1)

        # Determine which estimation method was used based on the output
        if "Standard Method Used: true" in output:
            parsed_data["Standard Method"] = True
        if "Bytesize Method Used: true" in output:
            parsed_data["Bytesize Method"] = True

    return parsed_data

def estimate_cost_for_directory(directory, script_path='estimate_script.js', output_csv='contract_costs.csv'):
    """
    Runs the Node.js script for each .sol file in the given directory and saves the output to a CSV.

    :param directory: Path to the directory containing Solidity contracts.
    :param script_path: Path to the Node.js script that estimates the cost.
    :param output_csv: Path to the CSV file where results will be saved.
    """
    results = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.sol'):
                contract_name = file  # Only take the file name
                contract_path = os.path.join(root, file)
                print(f"\nEstimating deployment cost for: {contract_name}")
                try:
                    # Call the Node.js script using subprocess and capture output
                    result = subprocess.run(
                        ['node', script_path, contract_path],
                        check=True, capture_output=True, text=True
                    )
                    output = result.stdout
                    parsed_data = parse_output(contract_name, output)

                except subprocess.CalledProcessError as e:
                    output = e.stdout if e.stdout else ""
                    error_message = str(e)
                    parsed_data = parse_output(contract_name, output, error_message)

                results.append(parsed_data)

    # Write the results to a CSV file
    with open(output_csv, mode='w', newline='') as csv_file:
        fieldnames = [
            "Contract Name", "Bytecode Length", "Estimated Gas Units",
            "Gas Price (Gwei)", "Priority Fee (Gwei)", "ETH Price (USD)",
            "Deployment Cost (ETH)", "Deployment Cost (USD)", "Standard Method", 
            "Bytesize Method", "Status", "Error Message"
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 estimate_cost_for_directory.py <directory-path>")
        sys.exit(1)
    
    directory_to_scan = sys.argv[1]
    estimate_cost_for_directory(directory_to_scan)
