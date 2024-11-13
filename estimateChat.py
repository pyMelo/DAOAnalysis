import subprocess
import csv
import numpy as np
import os
import argparse

# Function to run the JavaScript estimation script and parse its output
def run_estimate(contract_path):
    # Run the estimator script
    result = subprocess.run(
        ["node", "estimateBytesize.js", contract_path],
        capture_output=True,
        text=True
    )
    
    # If there’s an error in execution, return 'undefined' for all metrics
    if result.returncode != 0 or "undefined" in result.stdout:
        return {
            "bytesize": "undefined",
            "eth_price": "undefined",
            "gas_fees": "undefined",
            "deploy_cost_eth": "undefined",
            "deploy_cost_usd": "undefined"
        }
    
    # Parse the output by searching for specific keywords in each line
    output_lines = result.stdout.splitlines()
    metrics = {}
    for line in output_lines:
        if "Contract Bytecode Length:" in line:
            metrics["bytesize"] = int(line.split(": ")[-1].split(" ")[0])
        elif "Estimated Gas Units:" in line:
            metrics["gas_fees"] = int(line.split(": ")[-1])
        elif "Gas Price:" in line:
            metrics["gas_price"] = float(line.split(": ")[-1].split(" ")[0])  # Extracts gas price in gwei
        elif "ETH Price:" in line:
            metrics["eth_price"] = float(line.split(": $")[-1].split(" ")[0])  # Extracts ETH price in USD
        elif "Estimated Deployment Cost:" in line:
            metrics["deploy_cost_eth"] = float(line.split(": ")[-1].split(" ")[0])  # Deployment cost in ETH
            metrics["deploy_cost_usd"] = float(line.split("~$")[-1].split(" ")[0])  # Deployment cost in USD

    # Check that all expected metrics were found; otherwise, mark as 'undefined'
    required_keys = ["bytesize", "eth_price", "gas_fees", "deploy_cost_eth", "deploy_cost_usd"]
    for key in required_keys:
        if key not in metrics:
            metrics[key] = "undefined"
    
    return metrics

# Function to calculate averages and standard deviations
def calculate_statistics(metrics_list):
    if any(m["eth_price"] == "undefined" for m in metrics_list):
        return {k: "undefined" for k in metrics_list[0]}, {k: "undefined" for k in metrics_list[0]}
    
    averages = {k: np.mean([metrics[k] for metrics in metrics_list]) for k in metrics_list[0]}
    std_devs = {k: np.std([metrics[k] for metrics in metrics_list]) for k in metrics_list[0]}
    return averages, std_devs

# Main function to iterate over contracts and compute metrics
def main(contracts_directory):
    contracts = [f for f in os.listdir(contracts_directory) if f.endswith(".sol")]
    results = []

    for contract in contracts:
        contract_path = os.path.join(contracts_directory, contract)
        contract_metrics = []

        # Run the estimate for bytecode size once, since it does not need repetition
        single_run_metrics = run_estimate(contract_path)
        
        # If bytesize or other values are undefined, skip additional runs
        if single_run_metrics["bytesize"] == "undefined":
            contract_metrics = [{"bytesize": "undefined", "eth_price": "undefined", "gas_fees": "undefined",
                                 "deploy_cost_eth": "undefined", "deploy_cost_usd": "undefined"}]
            print(f"Contract {contract} encountered an error and was set to 'undefined' for all metrics.")
        else:
            # Run the remaining metrics that need multiple samples
            for _ in range(10):
                metrics = run_estimate(contract_path)
                contract_metrics.append(metrics)
            
            # Calculate averages and standard deviations for metrics other than bytesize
            averages, std_devs = calculate_statistics(contract_metrics)
            averages["bytesize"] = single_run_metrics["bytesize"]  # Set the single-run bytesize
            std_devs["bytesize"] = 0  # Bytesize std deviation is zero since it's a single measurement

            # Append results in desired format
            results.append({
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
            })

            # Print success or failure message for each contract
            if averages["bytesize"] == "undefined":
                print(f"Contract {contract} processed with errors; metrics set to 'undefined'.")
            else:
                print(f"Contract {contract} processed successfully.")

    # Write results to CSV
    with open("contract_estimates.csv", "w", newline="") as csvfile:
        fieldnames = [
            "Contract name", "Bytesize", "Average ETH Price", "STD ETH price",
            "Average Gas Fees", "STD Gas fees", "Average deployment cost (ETH)",
            "STD Deployment cost (ETH)", "Average deployment cost (USD)", "STD Deployment cost (USD)"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("CSV file 'contract_estimates.csv' created successfully.")

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Estimate deployment costs for contracts.")
    parser.add_argument(
        "contracts_directory",
        type=str,
        help="Path to the directory containing the Solidity contract files."
    )
    args = parser.parse_args()
    
    # Run the main function with the specified directory
    main(args.contracts_directory)
