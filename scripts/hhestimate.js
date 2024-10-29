// Import required packages
const hre = require("hardhat");

async function main() {
  // Specify the contract path and its name
  const contractPath = "contracts/src/token/ERC20/governance/GovernanceERC20.sol"; // Change to your contract's path
  const contractName = "GovernanceERC20"; // Change to your contract's name

  // Compile the contract
  await hre.run('compile');

  // Retrieve the compiled contract bytecode using the path and name
  const contractFactory = await hre.ethers.getContractFactory(contractName, {
    path: contractPath
  });

  const bytecode = contractFactory.bytecode;

  // Calculate the base cost for the bytecode
  const bytecodeSize = (bytecode.length - 2) / 2; // Subtract '0x' and divide by 2 to get byte length
  const baseDeploymentGas = bytecodeSize * 200;

  console.log(`Contract bytecode size (in bytes): ${bytecodeSize}`);
  console.log(`Base gas cost for bytecode: ${baseDeploymentGas}`);

  // Estimate full deployment gas including constructor execution
  const estimatedGas = await hre.ethers.provider.estimateGas({
    data: bytecode
  });

  console.log(`Estimated deployment gas (with constructor execution): ${estimatedGas}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
