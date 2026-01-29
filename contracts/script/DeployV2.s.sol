// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/AgentFICOScoreV2.sol";
import "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

/// @title DeployV2 Script
/// @notice Deploys AgentFICOScoreV2 with UUPS Proxy
/// @dev Run with: forge script script/DeployV2.s.sol --rpc-url $RPC_URL --broadcast --verify
contract DeployV2 is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);
        
        console.log("Deployer:", deployer);
        console.log("Chain ID:", block.chainid);
        
        vm.startBroadcast(deployerPrivateKey);

        // 1. Deploy implementation
        AgentFICOScoreV2 implementation = new AgentFICOScoreV2();
        console.log("Implementation deployed at:", address(implementation));

        // 2. Encode initialize call
        bytes memory initData = abi.encodeWithSelector(
            AgentFICOScoreV2.initialize.selector,
            deployer  // initialOwner
        );

        // 3. Deploy proxy
        ERC1967Proxy proxy = new ERC1967Proxy(
            address(implementation),
            initData
        );
        console.log("Proxy deployed at:", address(proxy));

        // 4. Verify deployment
        AgentFICOScoreV2 score = AgentFICOScoreV2(address(proxy));
        console.log("Owner:", score.owner());
        console.log("Version:", score.VERSION());
        console.log("User Update Fee:", score.userUpdateFee());

        vm.stopBroadcast();

        // Output for documentation
        console.log("\n=== DEPLOYMENT SUMMARY ===");
        console.log("Network:", _getNetworkName());
        console.log("Implementation:", address(implementation));
        console.log("Proxy (use this):", address(proxy));
        console.log("Owner:", deployer);
    }

    function _getNetworkName() internal view returns (string memory) {
        if (block.chainid == 8453) return "Base Mainnet";
        if (block.chainid == 84532) return "Base Sepolia";
        if (block.chainid == 31337) return "Anvil Local";
        return "Unknown";
    }
}
