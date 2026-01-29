// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/AgentFICOScore.sol";

/// @title AgentFICOScore Unit Tests
/// @notice Comprehensive tests for AgentFICOScore contract
contract AgentFICOScoreTest is Test {
    AgentFICOScore public agentFICO;
    
    address public owner;
    address public user1;
    address public user2;
    address public agent1;
    address public agent2;

    // Events (re-declare for testing)
    event ScoreUpdated(address indexed agent, uint256 overall, uint256 timestamp);
    event ScoreBreakdownRecorded(address indexed agent, uint256 txScore, uint256 x402Score, uint256 erc8004Score);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    function setUp() public {
        owner = address(this);
        user1 = makeAddr("user1");
        user2 = makeAddr("user2");
        agent1 = makeAddr("agent1");
        agent2 = makeAddr("agent2");
        
        agentFICO = new AgentFICOScore();
    }

    // ============ 1. Initial State Tests ============

    /// @notice Test constructor sets owner correctly
    function test_Constructor_SetsOwner() public view {
        assertEq(agentFICO.owner(), owner);
    }

    /// @notice Test totalAgents is initially 0
    function test_Constructor_TotalAgentsIsZero() public view {
        assertEq(agentFICO.totalAgents(), 0);
    }

    // ============ 2. updateScore Tests ============

    /// @notice Test normal score update
    function test_UpdateScore() public {
        uint256 txScore = 80;
        uint256 x402Score = 70;
        uint256 erc8004Score = 90;
        uint256 confidence = 85;
        string memory riskLevel = "low";
        string memory ipfsHash = "QmTestHash123";

        agentFICO.updateScore(
            agent1,
            txScore,
            x402Score,
            erc8004Score,
            confidence,
            riskLevel,
            ipfsHash
        );

        // Verify the score was stored
        AgentFICOScore.Score memory score = agentFICO.getScore(agent1);
        assertEq(score.txSuccess, txScore);
        assertEq(score.x402Profitability, x402Score);
        assertEq(score.erc8004Stability, erc8004Score);
        assertEq(score.confidence, confidence);
        assertEq(keccak256(bytes(score.riskLevel)), keccak256(bytes(riskLevel)));
        assertEq(keccak256(bytes(score.ipfsBreakdown)), keccak256(bytes(ipfsHash)));
    }

    /// @notice Test updateScore reverts when called by non-owner
    function test_UpdateScore_RevertNotOwner() public {
        vm.prank(user1);
        vm.expectRevert(AgentFICOScore.NotOwner.selector);
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
    }

    /// @notice Test updateScore reverts with invalid txScore (>100)
    function test_UpdateScore_RevertInvalidTxScore() public {
        vm.expectRevert(AgentFICOScore.ScoreOutOfRange.selector);
        agentFICO.updateScore(agent1, 101, 70, 90, 85, "low", "QmTest");
    }

    /// @notice Test updateScore reverts with invalid x402Score (>100)
    function test_UpdateScore_RevertInvalidX402Score() public {
        vm.expectRevert(AgentFICOScore.ScoreOutOfRange.selector);
        agentFICO.updateScore(agent1, 80, 101, 90, 85, "low", "QmTest");
    }

    /// @notice Test updateScore reverts with invalid erc8004Score (>100)
    function test_UpdateScore_RevertInvalidErc8004Score() public {
        vm.expectRevert(AgentFICOScore.ScoreOutOfRange.selector);
        agentFICO.updateScore(agent1, 80, 70, 101, 85, "low", "QmTest");
    }

    /// @notice Test updateScore reverts with invalid confidence (>100)
    function test_UpdateScore_RevertInvalidConfidence() public {
        vm.expectRevert(AgentFICOScore.ConfidenceOutOfRange.selector);
        agentFICO.updateScore(agent1, 80, 70, 90, 101, "low", "QmTest");
    }

    /// @notice Test overall score calculation (40-40-20 weighting)
    function test_UpdateScore_OverallCalculation() public {
        // Test case 1: All maximum (100, 100, 100) => (100*40 + 100*40 + 100*20) / 10 = 1000
        agentFICO.updateScore(agent1, 100, 100, 100, 100, "low", "QmTest");
        assertEq(agentFICO.getScoreOnly(agent1), 1000);

        // Test case 2: All minimum (0, 0, 0) => 0
        agentFICO.updateScore(agent2, 0, 0, 0, 0, "high", "QmTest");
        assertEq(agentFICO.getScoreOnly(agent2), 0);

        // Test case 3: Mixed values (80, 70, 60) => (80*40 + 70*40 + 60*20) / 10 = 720
        address agent3 = makeAddr("agent3");
        agentFICO.updateScore(agent3, 80, 70, 60, 85, "medium", "QmTest");
        uint256 expectedScore = (80 * 40 + 70 * 40 + 60 * 20) / 10;
        assertEq(agentFICO.getScoreOnly(agent3), expectedScore);
        assertEq(expectedScore, 720);

        // Test case 4: Only txSuccess matters (50, 0, 0) => 50*40/10 = 200
        address agent4 = makeAddr("agent4");
        agentFICO.updateScore(agent4, 50, 0, 0, 50, "high", "QmTest");
        assertEq(agentFICO.getScoreOnly(agent4), 200);
    }

    /// @notice Test new agent registration increments totalAgents
    function test_UpdateScore_IncrementsTotalAgents() public {
        assertEq(agentFICO.totalAgents(), 0);
        
        // First agent
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
        assertEq(agentFICO.totalAgents(), 1);
        
        // Second agent
        agentFICO.updateScore(agent2, 60, 50, 70, 75, "medium", "QmTest");
        assertEq(agentFICO.totalAgents(), 2);
        
        // Update existing agent (should NOT increment)
        agentFICO.updateScore(agent1, 85, 75, 95, 90, "low", "QmTest");
        assertEq(agentFICO.totalAgents(), 2);
    }

    /// @notice Test multiple updates for same agent
    function test_UpdateScore_MultipleUpdates() public {
        // First update
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest1");
        assertEq(agentFICO.getScoreOnly(agent1), 780);
        
        // Second update - should overwrite
        agentFICO.updateScore(agent1, 90, 85, 95, 95, "low", "QmTest2");
        assertEq(agentFICO.getScoreOnly(agent1), 890);
        
        AgentFICOScore.Score memory score = agentFICO.getScore(agent1);
        assertEq(keccak256(bytes(score.ipfsBreakdown)), keccak256(bytes("QmTest2")));
    }

    // ============ 3. getScore Tests ============

    /// @notice Test normal getScore return
    function test_GetScore() public {
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTestHash");
        
        AgentFICOScore.Score memory score = agentFICO.getScore(agent1);
        
        assertEq(score.txSuccess, 80);
        assertEq(score.x402Profitability, 70);
        assertEq(score.erc8004Stability, 90);
        assertEq(score.confidence, 85);
        assertEq(keccak256(bytes(score.riskLevel)), keccak256(bytes("low")));
        assertGt(score.timestamp, 0);
    }

    /// @notice Test getScore reverts for unregistered agent
    function test_GetScore_RevertAgentNotRegistered() public {
        vm.expectRevert(AgentFICOScore.AgentNotRegistered.selector);
        agentFICO.getScore(agent1);
    }

    // ============ 4. getScoreOnly Tests ============

    /// @notice Test normal getScoreOnly return
    function test_GetScoreOnly() public {
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
        
        uint256 overall = agentFICO.getScoreOnly(agent1);
        uint256 expectedOverall = (80 * 40 + 70 * 40 + 90 * 20) / 10;
        
        assertEq(overall, expectedOverall);
        assertEq(overall, 780);
    }

    /// @notice Test getScoreOnly reverts for unregistered agent
    function test_GetScoreOnly_RevertAgentNotRegistered() public {
        vm.expectRevert(AgentFICOScore.AgentNotRegistered.selector);
        agentFICO.getScoreOnly(agent1);
    }

    /// @notice Test gas efficiency: getScoreOnly vs getScore
    function test_GetScoreOnly_GasEfficiency() public {
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
        
        uint256 gasStart1 = gasleft();
        agentFICO.getScoreOnly(agent1);
        uint256 gasUsed1 = gasStart1 - gasleft();
        
        uint256 gasStart2 = gasleft();
        agentFICO.getScore(agent1);
        uint256 gasUsed2 = gasStart2 - gasleft();
        
        // getScoreOnly should use less gas than getScore
        assertLt(gasUsed1, gasUsed2, "getScoreOnly should be more gas efficient");
    }

    // ============ 5. getScoreHistory Tests ============

    /// @notice Test getScoreHistory with multiple updates
    function test_GetScoreHistory() public {
        // Add 3 scores with different timestamps
        agentFICO.updateScore(agent1, 70, 60, 80, 75, "medium", "QmTest1");
        vm.warp(block.timestamp + 1 days);
        
        agentFICO.updateScore(agent1, 80, 70, 85, 80, "low", "QmTest2");
        vm.warp(block.timestamp + 1 days);
        
        agentFICO.updateScore(agent1, 90, 80, 90, 85, "low", "QmTest3");
        
        // Get all 3 scores
        AgentFICOScore.Score[] memory history = agentFICO.getScoreHistory(agent1, 10);
        
        assertEq(history.length, 3);
        
        // Verify scores are in chronological order
        assertEq(history[0].txSuccess, 70);
        assertEq(history[1].txSuccess, 80);
        assertEq(history[2].txSuccess, 90);
    }

    /// @notice Test getScoreHistory when limit exceeds actual history
    function test_GetScoreHistory_LimitExceedsActual() public {
        // Add only 2 scores
        agentFICO.updateScore(agent1, 70, 60, 80, 75, "medium", "QmTest1");
        agentFICO.updateScore(agent1, 80, 70, 85, 80, "low", "QmTest2");
        
        // Request 100 but only 2 exist
        AgentFICOScore.Score[] memory history = agentFICO.getScoreHistory(agent1, 100);
        
        assertEq(history.length, 2);
        assertEq(history[0].txSuccess, 70);
        assertEq(history[1].txSuccess, 80);
    }

    /// @notice Test getScoreHistory for unregistered agent returns empty array
    function test_GetScoreHistory_UnregisteredAgent() public {
        AgentFICOScore.Score[] memory history = agentFICO.getScoreHistory(agent1, 10);
        assertEq(history.length, 0);
    }

    /// @notice Test getScoreHistory with limit = 0
    function test_GetScoreHistory_LimitZero() public {
        agentFICO.updateScore(agent1, 70, 60, 80, 75, "medium", "QmTest1");
        agentFICO.updateScore(agent1, 80, 70, 85, 80, "low", "QmTest2");
        
        AgentFICOScore.Score[] memory history = agentFICO.getScoreHistory(agent1, 0);
        assertEq(history.length, 0);
    }

    // ============ 6. assessRisk Tests ============

    /// @notice Test assessRisk for lending protocol (20% additional risk)
    function test_AssessRisk_Lending() public {
        // High score agent (overall = 1000, base risk = 0)
        agentFICO.updateScore(agent1, 100, 100, 100, 100, "low", "QmTest");
        
        AgentFICOScore.RiskAssessment memory risk = agentFICO.assessRisk(agent1, 1000 ether, "lending");
        
        // Base risk = 100 - (1000/10) = 0, Protocol risk = 20
        assertEq(risk.riskLevel, 20);
    }

    /// @notice Test assessRisk for trading protocol (10% additional risk)
    function test_AssessRisk_Trading() public {
        // High score agent (overall = 1000, base risk = 0)
        agentFICO.updateScore(agent1, 100, 100, 100, 100, "low", "QmTest");
        
        AgentFICOScore.RiskAssessment memory risk = agentFICO.assessRisk(agent1, 1000 ether, "trading");
        
        // Base risk = 0, Protocol risk = 10
        assertEq(risk.riskLevel, 10);
    }

    /// @notice Test assessRisk for payment protocol (no additional risk)
    function test_AssessRisk_Payment() public {
        // High score agent (overall = 1000, base risk = 0)
        agentFICO.updateScore(agent1, 100, 100, 100, 100, "low", "QmTest");
        
        AgentFICOScore.RiskAssessment memory risk = agentFICO.assessRisk(agent1, 1000 ether, "payment");
        
        // Base risk = 0, Protocol risk = 0
        assertEq(risk.riskLevel, 0);
    }

    /// @notice Test assessRisk with low score agent
    function test_AssessRisk_LowScoreAgent() public {
        // Low score agent (overall = 0, base risk = 100)
        agentFICO.updateScore(agent1, 0, 0, 0, 100, "high", "QmTest");
        
        AgentFICOScore.RiskAssessment memory risk = agentFICO.assessRisk(agent1, 1000 ether, "payment");
        
        // Base risk = 100 - (0/10) = 100
        assertEq(risk.riskLevel, 100);
    }

    /// @notice Test assessRisk capping at 100
    function test_AssessRisk_CappedAt100() public {
        // Low score agent with lending (should be capped at 100)
        agentFICO.updateScore(agent1, 0, 0, 0, 100, "high", "QmTest");
        
        AgentFICOScore.RiskAssessment memory risk = agentFICO.assessRisk(agent1, 1000 ether, "lending");
        
        // Base risk = 100, Protocol risk = 20, but capped at 100
        assertEq(risk.riskLevel, 100);
    }

    /// @notice Test assessRisk expected loss calculation
    function test_AssessRisk_ExpectedLoss() public {
        agentFICO.updateScore(agent1, 50, 50, 50, 100, "medium", "QmTest");
        
        uint256 amount = 10000 * 1e6; // 10,000 USDC
        AgentFICOScore.RiskAssessment memory risk = agentFICO.assessRisk(agent1, amount, "payment");
        
        // Calculate expected loss: (amount * defaultProbability) / 100
        uint256 expectedLoss = (amount * risk.defaultProbability) / 100;
        assertEq(risk.expectedLoss, expectedLoss);
    }

    /// @notice Test assessRisk reverts for unregistered agent
    function test_AssessRisk_RevertAgentNotRegistered() public {
        vm.expectRevert(AgentFICOScore.AgentNotRegistered.selector);
        agentFICO.assessRisk(agent1, 1000 ether, "lending");
    }

    /// @notice Test assessRisk reverts for invalid protocol type
    function test_AssessRisk_RevertInvalidProtocolType() public {
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
        
        vm.expectRevert(AgentFICOScore.InvalidProtocolType.selector);
        agentFICO.assessRisk(agent1, 1000 ether, "invalid_protocol");
    }

    /// @notice Test assessRisk positive factors
    function test_AssessRisk_PositiveFactors() public {
        // All scores >= 70
        agentFICO.updateScore(agent1, 75, 80, 85, 90, "low", "QmTest");
        
        AgentFICOScore.RiskAssessment memory risk = agentFICO.assessRisk(agent1, 1000 ether, "payment");
        
        assertEq(risk.positiveFactors.length, 3);
    }

    /// @notice Test assessRisk risk factors
    function test_AssessRisk_RiskFactors() public {
        // All scores < 50
        agentFICO.updateScore(agent1, 30, 40, 45, 30, "high", "QmTest");
        
        AgentFICOScore.RiskAssessment memory risk = agentFICO.assessRisk(agent1, 1000 ether, "payment");
        
        assertEq(risk.riskFactors.length, 4);
    }

    // ============ 7. isRegistered Tests ============

    /// @notice Test isRegistered returns true for registered agent
    function test_IsRegistered_True() public {
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
        
        assertTrue(agentFICO.isRegistered(agent1));
    }

    /// @notice Test isRegistered returns false for unregistered agent
    function test_IsRegistered_False() public {
        assertFalse(agentFICO.isRegistered(agent1));
    }

    // ============ 8. transferOwnership Tests ============

    /// @notice Test normal ownership transfer
    function test_TransferOwnership() public {
        agentFICO.transferOwnership(user1);
        
        assertEq(agentFICO.owner(), user1);
    }

    /// @notice Test transferOwnership reverts when called by non-owner
    function test_TransferOwnership_RevertNotOwner() public {
        vm.prank(user1);
        vm.expectRevert(AgentFICOScore.NotOwner.selector);
        agentFICO.transferOwnership(user2);
    }

    /// @notice Test transferOwnership reverts with zero address
    function test_TransferOwnership_RevertZeroAddress() public {
        vm.expectRevert(AgentFICOScore.InvalidNewOwner.selector);
        agentFICO.transferOwnership(address(0));
    }

    /// @notice Test new owner can update scores
    function test_TransferOwnership_NewOwnerCanOperate() public {
        agentFICO.transferOwnership(user1);
        
        vm.prank(user1);
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
        
        assertTrue(agentFICO.isRegistered(agent1));
    }

    /// @notice Test old owner cannot update scores after transfer
    function test_TransferOwnership_OldOwnerCannotOperate() public {
        agentFICO.transferOwnership(user1);
        
        vm.expectRevert(AgentFICOScore.NotOwner.selector);
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
    }

    // ============ 9. Events Tests ============

    /// @notice Test ScoreUpdated event emission
    function test_UpdateScore_EmitsScoreUpdatedEvent() public {
        uint256 expectedOverall = (80 * 40 + 70 * 40 + 90 * 20) / 10;
        
        vm.expectEmit(true, false, false, true);
        emit ScoreUpdated(agent1, expectedOverall, block.timestamp);
        
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
    }

    /// @notice Test ScoreBreakdownRecorded event emission
    function test_UpdateScore_EmitsScoreBreakdownEvent() public {
        vm.expectEmit(true, false, false, true);
        emit ScoreBreakdownRecorded(agent1, 80, 70, 90);
        
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
    }

    /// @notice Test OwnershipTransferred event on constructor
    function test_Constructor_EmitsOwnershipTransferredEvent() public {
        vm.expectEmit(true, true, false, false);
        emit OwnershipTransferred(address(0), address(this));
        
        new AgentFICOScore();
    }

    /// @notice Test OwnershipTransferred event on transfer
    function test_TransferOwnership_EmitsEvent() public {
        vm.expectEmit(true, true, false, false);
        emit OwnershipTransferred(address(this), user1);
        
        agentFICO.transferOwnership(user1);
    }

    // ============ 10. Edge Cases and Additional Tests ============

    /// @notice Test lastUpdate is correctly set
    function test_UpdateScore_SetsLastUpdate() public {
        uint256 timeNow = block.timestamp;
        
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
        
        assertEq(agentFICO.lastUpdate(agent1), timeNow);
    }

    /// @notice Test getTotalAgents function
    function test_GetTotalAgents() public {
        assertEq(agentFICO.getTotalAgents(), 0);
        
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
        assertEq(agentFICO.getTotalAgents(), 1);
        
        agentFICO.updateScore(agent2, 60, 50, 70, 75, "medium", "QmTest");
        assertEq(agentFICO.getTotalAgents(), 2);
    }

    /// @notice Test boundary values for scores
    function test_UpdateScore_BoundaryValues() public {
        // Test minimum values (0)
        agentFICO.updateScore(agent1, 0, 0, 0, 0, "high", "QmTest");
        AgentFICOScore.Score memory score = agentFICO.getScore(agent1);
        assertEq(score.overall, 0);
        assertEq(score.confidence, 0);
        
        // Test maximum values (100)
        agentFICO.updateScore(agent2, 100, 100, 100, 100, "low", "QmTest");
        score = agentFICO.getScore(agent2);
        assertEq(score.overall, 1000);
        assertEq(score.confidence, 100);
    }

    /// @notice Fuzz test for updateScore with valid inputs
    function testFuzz_UpdateScore(
        uint256 txScore,
        uint256 x402Score,
        uint256 erc8004Score,
        uint256 confidence
    ) public {
        // Bound inputs to valid ranges
        txScore = bound(txScore, 0, 100);
        x402Score = bound(x402Score, 0, 100);
        erc8004Score = bound(erc8004Score, 0, 100);
        confidence = bound(confidence, 0, 100);
        
        agentFICO.updateScore(agent1, txScore, x402Score, erc8004Score, confidence, "medium", "QmTest");
        
        uint256 expectedOverall = (txScore * 40 + x402Score * 40 + erc8004Score * 20) / 10;
        assertEq(agentFICO.getScoreOnly(agent1), expectedOverall);
    }

    /// @notice Fuzz test for assessRisk
    function testFuzz_AssessRisk(uint256 amount) public {
        amount = bound(amount, 1, type(uint128).max);
        
        agentFICO.updateScore(agent1, 80, 70, 90, 85, "low", "QmTest");
        
        AgentFICOScore.RiskAssessment memory risk = agentFICO.assessRisk(agent1, amount, "lending");
        
        // Risk level should be between 0 and 100
        assertLe(risk.riskLevel, 100);
        assertGe(risk.riskLevel, 0);
        
        // Default probability should be between 0 and 100
        assertLe(risk.defaultProbability, 100);
    }
}
