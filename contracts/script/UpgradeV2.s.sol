// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/AgentFICOScoreV2.sol";

/// @title UpgradeV2 Script
/// @notice Upgrades existing proxy to new implementation
/// @dev Run with: forge script script/UpgradeV2.s.sol --rpc-url $RPC_URL --broadcast
contract UpgradeV2 is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address proxyAddress = vm.envAddress("PROXY_ADDRESS");
        
        console.log("Upgrading proxy at:", proxyAddress);
        
        vm.startBroadcast(deployerPrivateKey);

        // 1. Deploy new implementation
        AgentFICOScoreV2 newImplementation = new AgentFICOScoreV2();
        console.log("New implementation:", address(newImplementation));

        // 2. Upgrade proxy
        AgentFICOScoreV2 proxy = AgentFICOScoreV2(proxyAddress);
        proxy.upgradeToAndCall(address(newImplementation), "");

        // 3. Verify
        console.log("Upgrade complete!");
        console.log("Version:", proxy.VERSION());

        vm.stopBroadcast();
    }
}
