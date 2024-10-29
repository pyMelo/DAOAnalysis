const fs = require('fs');
const path = require('path');
const ethers = require('ethers');
const axios = require('axios');
const solc = require('solc');
require("dotenv").config();

// Define your contracts root directory
const contractsRootDir = path.resolve(__dirname, "contracts");
const etherscanApiKey = process.env.ETHERSCAN_API; 
const provider = new ethers.JsonRpcProvider('https://cloudflare-eth.com');

// Utility function to read all Solidity files and their content
function findImports(importPath) {
    const fileName = path.basename(importPath);
    const resolvedPath = path.resolve(contractsRootDir, fileName);

    try {
        if (fs.existsSync(resolvedPath)) {
            const content = fs.readFileSync(resolvedPath, 'utf8');
            return { contents: content };
        } else {
            console.error(`File not found: ${fileName} in contracts directory`);
            return { error: `File not found: ${fileName}` };
        }
    } catch (err) {
        console.error(`Error reading file: ${err.message}`);
        return { error: `Error reading file: ${err.message}` };
    }
}

async function getEthPrice() {
    try {
        const response = await axios.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd');
        return response.data.ethereum.usd;
    } catch (error) {
        console.error("Error fetching Ethereum price:", error);
        throw error;
    }
}

async function getGasPriceFromEtherscan() {
    try {
        console.log("Fetching current gas price from Etherscan...");
        const response = await axios.get(`https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=${etherscanApiKey}`);
        const gasPriceGwei = response.data.result.ProposeGasPrice;
        // Use ethers.parseUnits instead of utils.parseUnits
        const gasPriceWei = ethers.parseUnits(gasPriceGwei.toString(), 'gwei');
        return gasPriceWei;
    } catch (error) {
        console.error("Error fetching gas price from Etherscan:", error);
        throw error;
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

        if (output.errors && output.errors.length > 0) {
            output.errors.forEach(err => {
                console.error(err.formattedMessage);
            });
            throw new Error("Compilation failed with errors.");
        }

        const contractName = Object.keys(output.contracts[fileName])[0];
        const contract = output.contracts[fileName][contractName];
        const bytecode = contract.evm.bytecode.object;

        console.log(`Contract Bytecode Length: ${bytecode.length} characters`);

        try {
            const deployTransaction = { data: '0x' + bytecode };
            const estimatedGasUnits = await provider.estimateGas(deployTransaction);
            const feeData = await provider.getFeeData();
            const gasPrice = feeData.gasPrice;
            const priorityFee = feeData.maxPriorityFeePerGas || ethers.parseUnits('0', 'gwei');
            const ethPriceUsd = await getEthPrice();
            
            const effectiveGasPrice = gasPrice + priorityFee;
            const gasCost = effectiveGasPrice * estimatedGasUnits;
            const estimatedCostEth = ethers.formatEther(gasCost);
            const estimatedCostUsd = parseFloat(estimatedCostEth) * ethPriceUsd;

            console.log(`Estimated Gas Units: ${estimatedGasUnits.toString()}`);
            console.log(`Gas Price: ${ethers.formatUnits(gasPrice, 'gwei')} gwei`);
            console.log(`Priority Fee: ${ethers.formatUnits(priorityFee, 'gwei')} gwei`);
            console.log(`ETH Price: $${ethPriceUsd} USD`);
            console.log(`Estimated Deployment Cost: ${estimatedCostEth} ETH (~$${estimatedCostUsd.toFixed(2)} USD)`);
        } catch (err) {
            console.error("Error estimating gas, falling back to bytecode size estimation...");

            const byteSize = bytecode.length / 2;
            console.log(`Compiled contract: ${contractName}`);
            console.log(`Contract Bytecode Length: ${byteSize} bytes`);
    
            const gasPrice = await getGasPriceFromEtherscan();
            const ethPriceUsd = await getEthPrice();
    
            const fixedGasCost = 21000n;
            const gasPerByte = 200n;
            
            const estimatedGasUnits = fixedGasCost + (BigInt(byteSize) * gasPerByte);
            const gasCost = gasPrice * estimatedGasUnits;
            const estimatedCostEth = ethers.formatEther(gasCost);
            const estimatedCostUsd = parseFloat(estimatedCostEth) * ethPriceUsd;
    
            console.log(`Estimated Gas Units: ${estimatedGasUnits.toString()}`);
            console.log(`Gas Price: ${ethers.formatUnits(gasPrice, 'gwei')} gwei`);
            console.log(`ETH Price: $${ethPriceUsd} USD`);
            console.log(`Estimated Deployment Cost: ${estimatedCostEth} ETH (~$${estimatedCostUsd.toFixed(2)} USD)`);
        }
    } catch (error) {
        console.error("Error during contract compilation or estimation:", error);
        throw error;
    }
}

const contractPath = process.argv[2];
if (!contractPath) {
    console.error('No path to the compiled contract file provided');
    throw new Error('No path to the compiled contract file');
}

estimateDeploymentCost(contractPath);