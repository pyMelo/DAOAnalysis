const fs = require('fs');
const path = require('path');
const ethers = require('ethers');
const axios = require('axios');
const solc = require('solc');
require("dotenv").config();

const contractsRootDir = path.resolve(__dirname, "contracts");

function findImports(importPath) {
    const resolvedPath = path.resolve(contractsRootDir, importPath);
    try {
        if (fs.existsSync(resolvedPath)) {
            return { contents: fs.readFileSync(resolvedPath, 'utf8') };
        } else {
            console.error(`Error: Missing import ${importPath}`);
            return { error: `File not found: ${importPath}` };
        }
    } catch (err) {
        console.error(`Error resolving import: ${err.message}`);
        return { error: `Error resolving import: ${err.message}` };
    }
}

async function estimateDeploymentCost(contractPath) {
    try {
        const fullContractPath = path.resolve(contractsRootDir, contractPath);
        const source = fs.readFileSync(fullContractPath, 'utf8');

        const fileName = path.basename(fullContractPath);
        const input = {
            language: 'Solidity',
            sources: {
                [fileName]: { content: source }
            },
            settings: {
                outputSelection: {
                    '*': { '*': ['*'] }
                }
            }
        };

        const output = JSON.parse(solc.compile(JSON.stringify(input), { import: findImports }));

        // Process warnings and errors
        let reportedByteSize = null;
        if (output.errors && output.errors.length > 0) {
            output.errors.forEach(err => {
                if (err.severity === 'warning') {
                    //console.warn(`Warning: ${err.formattedMessage}`);

                    // Extract the byte size from the warning message
                    const match = err.formattedMessage.match(/Contract code size is (\d+) bytes/);
                    if (match && match[1]) {
                        reportedByteSize = parseInt(match[1], 10); // Convert to integer
                    }
                } else {
                    console.error(`Error: ${err.formattedMessage}`);
                }
            });
        }

        let byteSize = 0; // Default byte size
        let useMinimumGas = false;

        if (output.contracts && fileName in output.contracts) {
            const contractName = Object.keys(output.contracts[fileName])[0];
            const contract = output.contracts[fileName][contractName];
            const bytecode = contract.evm.bytecode.object;

            if (bytecode && bytecode.length > 0) {
                byteSize = bytecode.length / 2;
            } else if (reportedByteSize !== null) {
                byteSize = reportedByteSize;
            } else {
                console.warn("Bytecode not generated. Falling back to minimum gas estimation.");
                useMinimumGas = true; // Use minimum gas if no bytecode or size is available
            }
        } else {
            console.warn("No contract information found. Falling back to minimum gas estimation.");
            useMinimumGas = true;
        }

        console.log(`Contract Bytecode Size: ${byteSize} bytes`);

        const gasPrice = await getGasPriceFromEtherscan();
        const ethPriceUsd = await getEthPriceFromEtherscan();

        // Calculate gas units
        const fixedGasCost = 21000n;
        const gasPerByte = 200n;
        const estimatedGasUnits = useMinimumGas
            ? fixedGasCost // Minimum gas for non-deployable contracts
            : fixedGasCost + (BigInt(byteSize) * gasPerByte);

        // Calculate costs
        const gasCost = gasPrice * estimatedGasUnits;
        const estimatedCostEth = ethers.formatEther(gasCost);
        const estimatedCostUsd = parseFloat(estimatedCostEth) * ethPriceUsd;

        console.log(`Estimated Gas Units: ${estimatedGasUnits.toString()}`);
        console.log(`Gas Price: ${ethers.formatUnits(gasPrice, 'gwei')} gwei`);
        console.log(`ETH Price: $${ethPriceUsd.toFixed(2)} USD`);
        console.log(`Estimated Deployment Cost: ${estimatedCostEth} ETH (~$${estimatedCostUsd.toFixed(2)} USD)`);

    } catch (error) {
        console.error("Compilation error:", error.message);
    }
}

async function getGasPriceFromEtherscan() {
    try {
        const response = await axios.get(`https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=${process.env.ETHERSCAN_API}`);
        const gasPriceGwei = response.data.result.ProposeGasPrice;
        return ethers.parseUnits(gasPriceGwei.toString(), 'gwei');
    } catch (error) {
        console.error("Failed to fetch gas price:", error.message);
        throw error;
    }
}

async function getEthPriceFromEtherscan() {
    try {
        const response = await axios.get(`https://api.etherscan.io/api?module=stats&action=ethprice&apikey=${process.env.ETHERSCAN_API}`);
        if (response.data.status === '1' && response.data.message === 'OK') {
            return parseFloat(response.data.result.ethusd);
        } else {
            throw new Error('Failed to fetch ETH price from Etherscan');
        }
    } catch (error) {
        console.error("Failed to fetch ETH price:", error.message);
        throw error;
    }
}

const contractPath = process.argv[2];
if (!contractPath) {
    console.error('No path to the compiled contract file provided');
    process.exit(1);
}

estimateDeploymentCost(contractPath);
