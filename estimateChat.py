import subprocess
import csv
import numpy as np
import os
import argparse

# Function to run the JavaScript estimation script and parse its output
def run_estimate(contract_path):
    result = subprocess.run(
        ["node", "estimateBytesize.js", contract_path],
        capture_output=True,
        text=True
    )

    print("Running estimateBytesize.js with contract path:", contract_path)
    print("Return code:", result.returncode)
    print("Output:", result.stdout)
    print("Error:", result.stderr)
    
    # Initialize metrics with default values
    metrics = {
        "bytesize": "undefined",
        "eth_price": "undefined",
        "gas_fees": "undefined",
        "deploy_cost_eth": "undefined",
        "deploy_cost_usd": "undefined"
    }

    # If there's an execution error, mark all metrics as undefined
    if result.returncode != 0:
        print("Error encountered. Marking metrics as undefined.")
        return metrics

    # Parse the output by searching for specific keywords in each line
    output_lines = result.stdout.splitlines()
    for line in output_lines:
        if "Contract Bytecode Size:" in line:
            metrics["bytesize"] = int(line.split(": ")[-1].split(" ")[0])
        elif "Estimated Gas Units:" in line:
            metrics["gas_fees"] = int(line.split(": ")[-1])
        elif "Gas Price:" in line:
            metrics["gas_price"] = float(line.split(": ")[-1].split(" ")[0])  # Extract gas price in gwei
        elif "ETH Price:" in line:
            metrics["eth_price"] = float(line.split(": $")[-1].split(" ")[0])  # Extract ETH price in USD
        elif "Estimated Deployment Cost:" in line:
            metrics["deploy_cost_eth"] = float(line.split(": ")[-1].split(" ")[0])  # Deployment cost in ETH
            metrics["deploy_cost_usd"] = float(line.split("~$")[-1].split(" ")[0])  # Deployment cost in USD

    # Log parsed metrics for debugging
    print(f"Parsed Metrics: {metrics}")

    return metrics

# Function to calculate averages and standard deviations
def calculate_statistics(metrics_list):
    # Filter out undefined metrics
    filtered_metrics = [
        m for m in metrics_list if all(m[k] != "undefined" for k in m)
    ]
    if not filtered_metrics:
        return {k: "undefined" for k in metrics_list[0]}, {k: "undefined" for k in metrics_list[0]}
    
    # Calculate averages and standard deviations for numeric fields
    averages = {k: np.mean([metrics[k] for metrics in filtered_metrics]) for k in filtered_metrics[0]}
    std_devs = {k: np.std([metrics[k] for metrics in filtered_metrics]) for k in filtered_metrics[0]}
    return averages, std_devs

# Main function to iterate over contracts and compute metrics
def main(contracts_directory, csv_filename):
    contracts = [f for f in os.listdir(contracts_directory) if f.endswith(".sol")]
    results = []

    for contract in contracts:
        contract_path = os.path.join(contracts_directory, contract)
        contract_metrics = []

        # Run the estimate for bytecode size and other metrics 10 times
        for _ in range(10):
            metrics = run_estimate(contract_path)
            contract_metrics.append(metrics)

        # Calculate averages and standard deviations for metrics
        averages, std_devs = calculate_statistics(contract_metrics)

        # Prepare result for the current contract
        result = {
            "Contract name": contract,
            "Bytesize": averages["bytesize"],
            "Average ETH Price": averages["eth_price"],
            "STD ETH price": std_devs["eth_price"],
            "Average Gas Fees": averages["gas_fees"],
            "STD Gas fees": std_devs["gas_fees"],
            "Average deployment cost (ETH)": averages["deploy_cost_eth"],
            "STD Deployment cost (ETH)": std_devs["deploy_cost_eth"],
            "Average deployment cost (USD)": averages["deploy_cost_usd"],
            "STD Deployment cost (USD)": std_devs["deploy_cost_usd"]
        }

        # Append the result
        results.append(result)

        # Print the result that will be written to the CSV
        print(f"CSV Line: {result}")

    # Define the path to save the CSV file
    dataset_dir = "./dataset"
    os.makedirs(dataset_dir, exist_ok=True)  # Create the directory if it doesn't exist
    csv_path = os.path.join(dataset_dir, csv_filename)

    # Write results to CSV
    with open(csv_path, "w", newline="") as csvfile:
        fieldnames = [
            "Contract name", "Bytesize", "Average ETH Price", "STD ETH price",
            "Average Gas Fees", "STD Gas fees", "Average deployment cost (ETH)",
            "STD Deployment cost (ETH)", "Average deployment cost (USD)", "STD Deployment cost (USD)"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"CSV file '{csv_filename}' created successfully in '{dataset_dir}'.")

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Estimate deployment costs for contracts.")
    parser.add_argument(
        "contracts_directory",
        type=str,
        help="Path to the directory containing the Solidity contract files."
    )
    args = parser.parse_args()

    # Prompt the user for the CSV file name
    csv_filename = input("Enter the name for the CSV file (e.g., contract_estimates.csv): ")
    
    # Run the main function with the specified directory and CSV file name
    main(args.contracts_directory, csv_filename)


