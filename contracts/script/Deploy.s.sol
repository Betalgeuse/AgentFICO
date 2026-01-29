// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script, console} from "forge-std/Script.sol";
import {AgentFICOScore} from "../src/AgentFICOScore.sol";

contract DeployAgentFICOScore is Script {
    function setUp() public {}

    function run() public returns (AgentFICOScore) {
        // 환경 변수에서 private key 로드
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        vm.startBroadcast(deployerPrivateKey);
        
        AgentFICOScore agentFICO = new AgentFICOScore();
        
        vm.stopBroadcast();
        
        // 배포 정보 출력
        console.log("AgentFICOScore deployed to:", address(agentFICO));
        console.log("Owner:", agentFICO.owner());
        
        return agentFICO;
    }
}
