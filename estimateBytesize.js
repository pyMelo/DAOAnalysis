const fs = require('fs');
const path = require('path');
const ethers = require('ethers');
const axios = require('axios');
const solc = require('solc');
require("dotenv").config();

const contractsRootDir = path.resolve(__dirname, "contracts");
const etherscanApiKey = process.env.ETHERSCAN_API;
const provider = new ethers.JsonRpcProvider('https://cloudflare-eth.com');

function findImports(importPath) {
    const fileName = path.basename(importPath);
    const resolvedPath = path.resolve(contractsRootDir, fileName);

    try {
        if (fs.existsSync(resolvedPath)) {
            const content = fs.readFileSync(resolvedPath, 'utf8');
            return { contents: content };
        } else {
            return { error: `File not found: ${fileName}` };
        }
    } catch (err) {
        return { error: `Error reading file: ${err.message}` };
    }
}

async function getEthPriceFromEtherscan() {
    try {
        const response = await axios.get(`https://api.etherscan.io/api?module=stats&action=ethprice&apikey=${etherscanApiKey}`);
        if (response.data.status === '1' && response.data.message === 'OK') {
            return parseFloat(response.data.result.ethusd);
        } else {
            throw new Error('Failed to fetch ETH price from Etherscan');
        }
    } catch (error) {
        throw error;
    }
}

async function getGasPriceFromEtherscan() {
    try {
        const response = await axios.get(`https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=${etherscanApiKey}`);
        const gasPriceGwei = response.data.result.ProposeGasPrice;
        return ethers.parseUnits(gasPriceGwei.toString(), 'gwei');
    } catch (error) {
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
            output.errors.forEach(err => console.error(err.formattedMessage));
            throw new Error("Compilation failed with errors.");
        }

        const contractName = Object.keys(output.contracts[fileName])[0];
        const contract = output.contracts[fileName][contractName];
        const bytecode = contract.evm.bytecode.object;


        console.log(`Contract Bytecode Length: ${bytecode.length} characters`);

        const byteSize = bytecode.length / 2;
        const gasPrice = await getGasPriceFromEtherscan();
        const ethPriceUsd = await getEthPriceFromEtherscan();

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
        
    } catch (error) {
        console.log("Compilation had an error");
        console.log(error)
        console.log("undefined");
    }
}

const contractPath = process.argv[2];
if (!contractPath) {
    console.error('No path to the compiled contract file provided');
    throw new Error('No path to the compiled contract file');
}

estimateDeploymentCost(contractPath);
