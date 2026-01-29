// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/AgentFICOScoreV2.sol";
import "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

/// @title AgentFICOScoreV2 Unit Tests
/// @notice Comprehensive tests for UUPS upgradeable AgentFICOScoreV2 contract
contract AgentFICOScoreV2Test is Test {
    AgentFICOScoreV2 public implementation;
    AgentFICOScoreV2 public score;
    ERC1967Proxy public proxy;
    
    address public owner;
    address public oracle;
    address public user1;
    address public agent1;
    address public agent2;

    // Events
    event ScoreUpdated(address indexed agent, uint256 overall, uint8 riskLevel, bool antiGamingApplied, address indexed updatedBy);
    event UserTriggeredUpdate(address indexed agent, address indexed requester, uint256 feePaid);
    event OracleAuthorized(address indexed oracle, bool authorized);
    event UserUpdateFeeChanged(uint256 oldFee, uint256 newFee);
    event FeesWithdrawn(address indexed to, uint256 amount);

    function setUp() public {
        owner = makeAddr("owner");
        oracle = makeAddr("oracle");
        user1 = makeAddr("user1");
        agent1 = makeAddr("agent1");
        agent2 = makeAddr("agent2");

        // Deploy implementation
        implementation = new AgentFICOScoreV2();

        // Deploy proxy with initialization
        bytes memory initData = abi.encodeWithSelector(
            AgentFICOScoreV2.initialize.selector,
            owner
        );
        proxy = new ERC1967Proxy(address(implementation), initData);
        
        // Cast proxy to AgentFICOScoreV2
        score = AgentFICOScoreV2(address(proxy));

        // Fund user1 for fee tests
        vm.deal(user1, 10 ether);
    }

    // ============ 1. Initialization Tests ============

    function test_Initialize_SetsOwner() public view {
        assertEq(score.owner(), owner);
    }

    function test_Initialize_SetsDefaultFee() public view {
        assertEq(score.userUpdateFee(), 0.001 ether);
    }

    function test_Initialize_SetsVersion() public view {
        assertEq(score.VERSION(), 2);
    }

    function test_Initialize_TotalAgentsIsZero() public view {
        assertEq(score.totalAgents(), 0);
    }

    function test_Initialize_RevertZeroAddress() public {
        AgentFICOScoreV2 newImpl = new AgentFICOScoreV2();
        bytes memory initData = abi.encodeWithSelector(
            AgentFICOScoreV2.initialize.selector,
            address(0)
        );
        vm.expectRevert(AgentFICOScoreV2.ZeroAddress.selector);
        new ERC1967Proxy(address(newImpl), initData);
    }

    function test_Initialize_CannotReinitialize() public {
        vm.expectRevert();
        score.initialize(user1);
    }

    // ============ 2. updateScore Tests ============

    function test_UpdateScore_ByOwner() public {
        vm.prank(owner);
        score.updateScore(agent1, 80, 70, 90, 85, true);

        AgentFICOScoreV2.Score memory s = score.getScore(agent1);
        assertEq(s.txSuccess, 80);
        assertEq(s.x402Profitability, 70);
        assertEq(s.erc8004Stability, 90);
        assertEq(s.confidence, 85);
        assertTrue(s.antiGamingApplied);
    }

    function test_UpdateScore_ByOracle() public {
        // Authorize oracle
        vm.prank(owner);
        score.setOracle(oracle, true);

        // Oracle updates score
        vm.prank(oracle);
        score.updateScore(agent1, 75, 65, 85, 80, false);

        AgentFICOScoreV2.Score memory s = score.getScore(agent1);
        assertEq(s.txSuccess, 75);
        assertFalse(s.antiGamingApplied);
    }

    function test_UpdateScore_RevertUnauthorized() public {
        vm.prank(user1);
        vm.expectRevert(AgentFICOScoreV2.UnauthorizedOracle.selector);
        score.updateScore(agent1, 80, 70, 90, 85, true);
    }

    function test_UpdateScore_RevertScoreOutOfRange() public {
        vm.startPrank(owner);
        
        vm.expectRevert(AgentFICOScoreV2.ScoreOutOfRange.selector);
        score.updateScore(agent1, 101, 70, 90, 85, true);

        vm.expectRevert(AgentFICOScoreV2.ScoreOutOfRange.selector);
        score.updateScore(agent1, 80, 101, 90, 85, true);

        vm.expectRevert(AgentFICOScoreV2.ScoreOutOfRange.selector);
        score.updateScore(agent1, 80, 70, 101, 85, true);

        vm.stopPrank();
    }

    function test_UpdateScore_RevertConfidenceOutOfRange() public {
        vm.prank(owner);
        vm.expectRevert(AgentFICOScoreV2.ConfidenceOutOfRange.selector);
        score.updateScore(agent1, 80, 70, 90, 101, true);
    }

    function test_UpdateScore_OverallCalculation() public {
        vm.startPrank(owner);

        // (100*40 + 100*40 + 100*20) / 10 = 1000
        score.updateScore(agent1, 100, 100, 100, 100, true);
        assertEq(score.getScoreOnly(agent1), 1000);

        // (0*40 + 0*40 + 0*20) / 10 = 0
        score.updateScore(agent2, 0, 0, 0, 0, false);
        assertEq(score.getScoreOnly(agent2), 0);

        // (80*40 + 70*40 + 60*20) / 10 = 720
        address agent3 = makeAddr("agent3");
        score.updateScore(agent3, 80, 70, 60, 85, true);
        assertEq(score.getScoreOnly(agent3), 720);

        vm.stopPrank();
    }

    function test_UpdateScore_RiskLevelCalculation() public {
        vm.startPrank(owner);

        // Score 850+ = RISK_EXCELLENT (1)
        score.updateScore(agent1, 90, 90, 80, 85, true);
        assertEq(score.getScore(agent1).riskLevel, score.RISK_EXCELLENT());

        // Score 750-849 = RISK_GOOD (2)
        address agent3 = makeAddr("agent3");
        score.updateScore(agent3, 80, 80, 70, 85, true);
        assertEq(score.getScore(agent3).riskLevel, score.RISK_GOOD());

        // Score 650-749 = RISK_AVERAGE (3)
        address agent4 = makeAddr("agent4");
        score.updateScore(agent4, 70, 70, 60, 85, true);
        assertEq(score.getScore(agent4).riskLevel, score.RISK_AVERAGE());

        // Score 550-649 = RISK_BELOW_AVG (4)
        address agent5 = makeAddr("agent5");
        score.updateScore(agent5, 60, 60, 50, 85, true);
        assertEq(score.getScore(agent5).riskLevel, score.RISK_BELOW_AVG());

        // Score <550 = RISK_POOR (5)
        address agent6 = makeAddr("agent6");
        score.updateScore(agent6, 50, 50, 40, 85, true);
        assertEq(score.getScore(agent6).riskLevel, score.RISK_POOR());

        vm.stopPrank();
    }

    function test_UpdateScore_IncrementsTotalAgents() public {
        vm.startPrank(owner);

        assertEq(score.totalAgents(), 0);
        
        score.updateScore(agent1, 80, 70, 90, 85, true);
        assertEq(score.totalAgents(), 1);
        
        score.updateScore(agent2, 60, 50, 70, 75, false);
        assertEq(score.totalAgents(), 2);
        
        // Update existing agent - should NOT increment
        score.updateScore(agent1, 85, 75, 95, 90, true);
        assertEq(score.totalAgents(), 2);

        vm.stopPrank();
    }

    function test_UpdateScore_EmitsEvent() public {
        vm.prank(owner);
        
        uint256 expectedOverall = (80 * 40 + 70 * 40 + 90 * 20) / 10; // 780
        uint8 expectedRiskLevel = 2; // RISK_GOOD (750-849)
        
        vm.expectEmit(true, true, false, true);
        emit ScoreUpdated(agent1, expectedOverall, expectedRiskLevel, true, owner);
        
        score.updateScore(agent1, 80, 70, 90, 85, true);
    }

    // ============ 3. batchUpdateScores Tests ============

    function test_BatchUpdateScores() public {
        address[] memory agents = new address[](3);
        agents[0] = agent1;
        agents[1] = agent2;
        agents[2] = makeAddr("agent3");

        uint256[] memory txScores = new uint256[](3);
        txScores[0] = 80;
        txScores[1] = 70;
        txScores[2] = 60;

        uint256[] memory x402Scores = new uint256[](3);
        x402Scores[0] = 75;
        x402Scores[1] = 65;
        x402Scores[2] = 55;

        uint256[] memory erc8004Scores = new uint256[](3);
        erc8004Scores[0] = 90;
        erc8004Scores[1] = 80;
        erc8004Scores[2] = 70;

        uint256[] memory confidences = new uint256[](3);
        confidences[0] = 85;
        confidences[1] = 80;
        confidences[2] = 75;

        bool[] memory antiGamingFlags = new bool[](3);
        antiGamingFlags[0] = true;
        antiGamingFlags[1] = false;
        antiGamingFlags[2] = true;

        vm.prank(owner);
        score.batchUpdateScores(agents, txScores, x402Scores, erc8004Scores, confidences, antiGamingFlags);

        assertEq(score.totalAgents(), 3);
        assertEq(score.getScore(agent1).txSuccess, 80);
        assertEq(score.getScore(agent2).txSuccess, 70);
        assertEq(score.getScore(agents[2]).txSuccess, 60);
    }

    function test_BatchUpdateScores_RevertArrayLengthMismatch() public {
        address[] memory agents = new address[](2);
        agents[0] = agent1;
        agents[1] = agent2;

        uint256[] memory txScores = new uint256[](3); // Wrong length
        txScores[0] = 80;
        txScores[1] = 70;
        txScores[2] = 60;

        uint256[] memory x402Scores = new uint256[](2);
        uint256[] memory erc8004Scores = new uint256[](2);
        uint256[] memory confidences = new uint256[](2);
        bool[] memory antiGamingFlags = new bool[](2);

        vm.prank(owner);
        vm.expectRevert("Array length mismatch");
        score.batchUpdateScores(agents, txScores, x402Scores, erc8004Scores, confidences, antiGamingFlags);
    }

    // ============ 4. requestScoreUpdate Tests ============

    function test_RequestScoreUpdate() public {
        vm.prank(user1);
        
        vm.expectEmit(true, true, false, true);
        emit UserTriggeredUpdate(agent1, user1, 0.001 ether);
        
        score.requestScoreUpdate{value: 0.001 ether}(agent1);

        assertEq(score.accumulatedFees(), 0.001 ether);
    }

    function test_RequestScoreUpdate_RevertInsufficientFee() public {
        vm.prank(user1);
        vm.expectRevert(AgentFICOScoreV2.InsufficientFee.selector);
        score.requestScoreUpdate{value: 0.0001 ether}(agent1);
    }

    function test_RequestScoreUpdate_RevertCooldown() public {
        // First, owner updates the score to set lastUpdate
        vm.prank(owner);
        score.updateScore(agent1, 80, 70, 90, 85, true);

        // User tries to request update immediately - should fail due to cooldown
        vm.prank(user1);
        vm.expectRevert(AgentFICOScoreV2.UpdateCooldownActive.selector);
        score.requestScoreUpdate{value: 0.001 ether}(agent1);
    }

    function test_RequestScoreUpdate_AfterCooldown() public {
        // First update
        vm.prank(owner);
        score.updateScore(agent1, 80, 70, 90, 85, true);

        // Warp past cooldown (1 hour)
        vm.warp(block.timestamp + 1 hours + 1);

        // Now user can request update
        vm.prank(user1);
        score.requestScoreUpdate{value: 0.001 ether}(agent1);

        assertEq(score.accumulatedFees(), 0.001 ether);
    }

    function test_RequestScoreUpdate_ExcessFee() public {
        vm.prank(user1);
        score.requestScoreUpdate{value: 0.01 ether}(agent1); // 10x the required fee

        assertEq(score.accumulatedFees(), 0.01 ether);
    }

    // ============ 5. getScore / getScoreOnly Tests ============

    function test_GetScore() public {
        vm.prank(owner);
        score.updateScore(agent1, 80, 70, 90, 85, true);

        AgentFICOScoreV2.Score memory s = score.getScore(agent1);
        
        assertEq(s.txSuccess, 80);
        assertEq(s.x402Profitability, 70);
        assertEq(s.erc8004Stability, 90);
        assertEq(s.confidence, 85);
        assertTrue(s.antiGamingApplied);
        assertGt(s.timestamp, 0);
    }

    function test_GetScore_RevertAgentNotRegistered() public {
        vm.expectRevert(AgentFICOScoreV2.AgentNotRegistered.selector);
        score.getScore(agent1);
    }

    function test_GetScoreOnly() public {
        vm.prank(owner);
        score.updateScore(agent1, 80, 70, 90, 85, true);

        uint256 overall = score.getScoreOnly(agent1);
        assertEq(overall, 780); // (80*40 + 70*40 + 90*20) / 10
    }

    function test_GetScoreOnly_RevertAgentNotRegistered() public {
        vm.expectRevert(AgentFICOScoreV2.AgentNotRegistered.selector);
        score.getScoreOnly(agent1);
    }

    // ============ 6. assessRisk Tests ============

    function test_AssessRisk() public {
        vm.prank(owner);
        score.updateScore(agent1, 80, 70, 90, 80, true); // Overall: 780

        // Test with 1000 USDC and 200 bps (2%) protocol risk
        AgentFICOScoreV2.RiskAssessment memory risk = score.assessRisk(agent1, 1000e6, 200);

        // Base risk = 100 - (780/10) = 22
        // Final risk = 22 + (200/100) = 24
        assertEq(risk.riskLevel, 24);
        
        // defaultProb = (24 * (200 - 80)) / 200 = (24 * 120) / 200 = 14
        assertEq(risk.defaultProbability, 14);
    }

    function test_AssessRisk_HighScoreAgent() public {
        vm.prank(owner);
        score.updateScore(agent1, 100, 100, 100, 100, true); // Overall: 1000

        AgentFICOScoreV2.RiskAssessment memory risk = score.assessRisk(agent1, 1000e6, 0);

        // Base risk = 100 - (1000/10) = 0
        assertEq(risk.riskLevel, 0);
        assertEq(risk.defaultProbability, 0);
        assertEq(risk.expectedLoss, 0);
    }

    function test_AssessRisk_LowScoreAgent() public {
        vm.prank(owner);
        score.updateScore(agent1, 0, 0, 0, 0, false); // Overall: 0

        AgentFICOScoreV2.RiskAssessment memory risk = score.assessRisk(agent1, 1000e6, 0);

        // Base risk = 100 - (0/10) = 100
        assertEq(risk.riskLevel, 100);
        // defaultProb = (100 * (200 - 0)) / 200 = 100
        assertEq(risk.defaultProbability, 100);
    }

    function test_AssessRisk_RiskCappedAt100() public {
        vm.prank(owner);
        score.updateScore(agent1, 0, 0, 0, 50, false); // Overall: 0

        // Very high protocol risk (5000 bps = 50%)
        AgentFICOScoreV2.RiskAssessment memory risk = score.assessRisk(agent1, 1000e6, 5000);

        // Base risk = 100, protocol risk = 50, but capped at 100
        assertEq(risk.riskLevel, 100);
    }

    function test_AssessRisk_ExpectedLossCalculation() public {
        vm.prank(owner);
        score.updateScore(agent1, 50, 50, 50, 50, true); // Overall: 500

        uint256 amount = 10000e6; // 10,000 USDC
        AgentFICOScoreV2.RiskAssessment memory risk = score.assessRisk(agent1, amount, 0);

        // Base risk = 100 - 50 = 50
        // defaultProb = (50 * (200 - 50)) / 200 = (50 * 150) / 200 = 37
        // expectedLoss = (10000e6 * 50 * 150) / 20000 = 3750e6
        assertEq(risk.expectedLoss, 3750e6);
    }

    function test_AssessRisk_RevertAgentNotRegistered() public {
        vm.expectRevert(AgentFICOScoreV2.AgentNotRegistered.selector);
        score.assessRisk(agent1, 1000e6, 200);
    }

    // ============ 7. isRegistered / getUpdateCooldown Tests ============

    function test_IsRegistered() public {
        assertFalse(score.isRegistered(agent1));

        vm.prank(owner);
        score.updateScore(agent1, 80, 70, 90, 85, true);

        assertTrue(score.isRegistered(agent1));
    }

    function test_GetUpdateCooldown() public {
        // Unregistered agent - cooldown is based on lastUpdate which is 0
        // getUpdateCooldown returns: if block.timestamp >= 0 + 1 hours => 0, else 1 hour - timestamp
        // Since block.timestamp starts at 1, it returns 1 hour - 1 = 3599
        // But for unregistered agent with no lastUpdate, we allow first request
        
        // Register agent first
        vm.prank(owner);
        score.updateScore(agent1, 80, 70, 90, 85, true);

        // Should have ~1 hour cooldown (minus 1 second because timestamp advanced)
        uint256 cooldown = score.getUpdateCooldown(agent1);
        assertGt(cooldown, 0);
        assertLe(cooldown, 1 hours);

        // Warp 30 minutes
        vm.warp(block.timestamp + 30 minutes);
        cooldown = score.getUpdateCooldown(agent1);
        assertLe(cooldown, 30 minutes + 1); // Allow 1 second tolerance

        // Warp past cooldown
        vm.warp(block.timestamp + 31 minutes);
        assertEq(score.getUpdateCooldown(agent1), 0);
    }

    // ============ 8. Admin Functions Tests ============

    function test_SetOracle() public {
        vm.prank(owner);
        
        vm.expectEmit(true, false, false, true);
        emit OracleAuthorized(oracle, true);
        
        score.setOracle(oracle, true);

        assertTrue(score.authorizedOracles(oracle));
    }

    function test_SetOracle_Revoke() public {
        vm.startPrank(owner);
        score.setOracle(oracle, true);
        assertTrue(score.authorizedOracles(oracle));

        score.setOracle(oracle, false);
        assertFalse(score.authorizedOracles(oracle));
        vm.stopPrank();
    }

    function test_SetOracle_RevertNotOwner() public {
        vm.prank(user1);
        vm.expectRevert();
        score.setOracle(oracle, true);
    }

    function test_SetOracle_RevertZeroAddress() public {
        vm.prank(owner);
        vm.expectRevert(AgentFICOScoreV2.ZeroAddress.selector);
        score.setOracle(address(0), true);
    }

    function test_SetUserUpdateFee() public {
        vm.prank(owner);
        
        vm.expectEmit(false, false, false, true);
        emit UserUpdateFeeChanged(0.001 ether, 0.005 ether);
        
        score.setUserUpdateFee(0.005 ether);

        assertEq(score.userUpdateFee(), 0.005 ether);
    }

    function test_SetUserUpdateFee_RevertNotOwner() public {
        vm.prank(user1);
        vm.expectRevert();
        score.setUserUpdateFee(0.005 ether);
    }

    function test_WithdrawFees() public {
        // Accumulate some fees
        vm.prank(user1);
        score.requestScoreUpdate{value: 0.01 ether}(agent1);

        uint256 ownerBalanceBefore = owner.balance;

        vm.prank(owner);
        
        vm.expectEmit(true, false, false, true);
        emit FeesWithdrawn(payable(owner), 0.01 ether);
        
        score.withdrawFees(payable(owner));

        assertEq(score.accumulatedFees(), 0);
        assertEq(owner.balance, ownerBalanceBefore + 0.01 ether);
    }

    function test_WithdrawFees_RevertNotOwner() public {
        vm.prank(user1);
        vm.expectRevert();
        score.withdrawFees(payable(user1));
    }

    function test_WithdrawFees_RevertZeroAddress() public {
        vm.prank(owner);
        vm.expectRevert(AgentFICOScoreV2.ZeroAddress.selector);
        score.withdrawFees(payable(address(0)));
    }

    // ============ 9. Upgrade Tests ============

    function test_UpgradeToAndCall() public {
        // Deploy new implementation
        AgentFICOScoreV2 newImpl = new AgentFICOScoreV2();

        vm.prank(owner);
        score.upgradeToAndCall(address(newImpl), "");

        // Contract should still work
        vm.prank(owner);
        score.updateScore(agent1, 80, 70, 90, 85, true);
        assertEq(score.getScoreOnly(agent1), 780);
    }

    function test_UpgradeToAndCall_RevertNotOwner() public {
        AgentFICOScoreV2 newImpl = new AgentFICOScoreV2();

        vm.prank(user1);
        vm.expectRevert();
        score.upgradeToAndCall(address(newImpl), "");
    }

    function test_RenounceUpgradeability() public {
        vm.prank(owner);
        score.renounceUpgradeability();

        // Owner should now be address(0)
        assertEq(score.owner(), address(0));

        // Cannot upgrade anymore
        AgentFICOScoreV2 newImpl = new AgentFICOScoreV2();
        vm.expectRevert();
        score.upgradeToAndCall(address(newImpl), "");
    }

    function test_RenounceUpgradeability_RevertNotOwner() public {
        vm.prank(user1);
        vm.expectRevert();
        score.renounceUpgradeability();
    }

    // ============ 10. State Persistence After Upgrade ============

    function test_StatePersistenceAfterUpgrade() public {
        // Add some data
        vm.startPrank(owner);
        score.updateScore(agent1, 80, 70, 90, 85, true);
        score.updateScore(agent2, 60, 50, 70, 75, false);
        score.setOracle(oracle, true);
        score.setUserUpdateFee(0.005 ether);
        vm.stopPrank();

        // User requests update
        vm.prank(user1);
        vm.warp(block.timestamp + 2 hours);
        score.requestScoreUpdate{value: 0.005 ether}(agent1);

        // Save state before upgrade
        uint256 totalAgentsBefore = score.totalAgents();
        uint256 agent1ScoreBefore = score.getScoreOnly(agent1);
        uint256 agent2ScoreBefore = score.getScoreOnly(agent2);
        uint256 feesBefore = score.accumulatedFees();
        bool oracleAuthorizedBefore = score.authorizedOracles(oracle);
        uint256 userFeeBefore = score.userUpdateFee();

        // Upgrade
        AgentFICOScoreV2 newImpl = new AgentFICOScoreV2();
        vm.prank(owner);
        score.upgradeToAndCall(address(newImpl), "");

        // Verify state persisted
        assertEq(score.totalAgents(), totalAgentsBefore);
        assertEq(score.getScoreOnly(agent1), agent1ScoreBefore);
        assertEq(score.getScoreOnly(agent2), agent2ScoreBefore);
        assertEq(score.accumulatedFees(), feesBefore);
        assertEq(score.authorizedOracles(oracle), oracleAuthorizedBefore);
        assertEq(score.userUpdateFee(), userFeeBefore);
    }

    // ============ 11. Fuzz Tests ============

    function testFuzz_UpdateScore(
        uint256 txScore,
        uint256 x402Score,
        uint256 erc8004Score,
        uint256 confidence
    ) public {
        txScore = bound(txScore, 0, 100);
        x402Score = bound(x402Score, 0, 100);
        erc8004Score = bound(erc8004Score, 0, 100);
        confidence = bound(confidence, 0, 100);

        vm.prank(owner);
        score.updateScore(agent1, txScore, x402Score, erc8004Score, confidence, true);

        uint256 expectedOverall = (txScore * 40 + x402Score * 40 + erc8004Score * 20) / 10;
        assertEq(score.getScoreOnly(agent1), expectedOverall);
    }

    function testFuzz_AssessRisk(uint256 amount, uint256 protocolRiskBps) public {
        amount = bound(amount, 1, type(uint128).max);
        protocolRiskBps = bound(protocolRiskBps, 0, 10000);

        vm.prank(owner);
        score.updateScore(agent1, 80, 70, 90, 85, true);

        AgentFICOScoreV2.RiskAssessment memory risk = score.assessRisk(agent1, amount, protocolRiskBps);

        assertLe(risk.riskLevel, 100);
        assertLe(risk.defaultProbability, 100);
    }

    function testFuzz_RequestScoreUpdate(uint256 fee) public {
        fee = bound(fee, 0.001 ether, 1 ether);
        vm.deal(user1, fee);

        vm.prank(user1);
        score.requestScoreUpdate{value: fee}(agent1);

        assertEq(score.accumulatedFees(), fee);
    }

    // ============ 12. Edge Cases ============

    function test_UpdateScore_BoundaryValues() public {
        vm.startPrank(owner);

        // Minimum values
        score.updateScore(agent1, 0, 0, 0, 0, false);
        AgentFICOScoreV2.Score memory s = score.getScore(agent1);
        assertEq(s.overall, 0);
        assertEq(s.riskLevel, score.RISK_POOR());

        // Maximum values
        score.updateScore(agent2, 100, 100, 100, 100, true);
        s = score.getScore(agent2);
        assertEq(s.overall, 1000);
        assertEq(s.riskLevel, score.RISK_EXCELLENT());

        vm.stopPrank();
    }

    function test_AssessRisk_ZeroAmount() public {
        vm.prank(owner);
        score.updateScore(agent1, 50, 50, 50, 50, true);

        AgentFICOScoreV2.RiskAssessment memory risk = score.assessRisk(agent1, 0, 0);
        assertEq(risk.expectedLoss, 0);
    }

    function test_ScoreHistoryCount() public {
        vm.startPrank(owner);

        assertEq(score.scoreHistoryCount(agent1), 0);

        score.updateScore(agent1, 80, 70, 90, 85, true);
        assertEq(score.scoreHistoryCount(agent1), 1);

        score.updateScore(agent1, 85, 75, 95, 90, true);
        assertEq(score.scoreHistoryCount(agent1), 2);

        score.updateScore(agent1, 90, 80, 100, 95, true);
        assertEq(score.scoreHistoryCount(agent1), 3);

        vm.stopPrank();
    }
}
