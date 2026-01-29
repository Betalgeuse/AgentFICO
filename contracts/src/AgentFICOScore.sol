// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title AgentFICOScore
/// @author AgentFICO Team
/// @notice AI Agent credit scoring system for DeFi protocols
/// @dev Network: Base (Coinbase L2) - Chain ID: 8453 (Mainnet), 84532 (Sepolia)
contract AgentFICOScore {
    // ============ Structs ============

    /// @notice Score structure containing agent credit metrics
    /// @dev overall is calculated as: (txSuccess * 40 + x402Profitability * 40 + erc8004Stability * 20) / 100
    struct Score {
        uint256 overall;            // 0-1000 (40-40-20 weighted calculation)
        uint256 txSuccess;          // 0-100 (40% weight)
        uint256 x402Profitability;  // 0-100 (40% weight)
        uint256 erc8004Stability;   // 0-100 (20% weight)
        uint256 confidence;         // 0-100
        string riskLevel;           // "high", "medium", "low"
        uint256 timestamp;
        string ipfsBreakdown;       // IPFS hash (detailed breakdown)
    }

    /// @notice Risk assessment structure for lending/trading decisions
    struct RiskAssessment {
        uint256 riskLevel;          // 0-100
        uint256 defaultProbability; // 0-100 (%)
        uint256 expectedLoss;       // USDC units
        string[] positiveFactors;
        string[] riskFactors;
    }

    // ============ State Variables ============

    /// @notice Contract owner address
    address public owner;

    /// @notice Current score for each agent
    mapping(address => Score) public scores;

    /// @notice Historical scores for each agent
    mapping(address => Score[]) public scoreHistory;

    /// @notice Last update timestamp for each agent
    mapping(address => uint256) public lastUpdate;

    /// @notice Total number of registered agents
    uint256 public totalAgents;

    // ============ Events ============

    /// @notice Emitted when an agent's score is updated
    /// @param agent The address of the agent
    /// @param overall The overall score (0-1000)
    /// @param timestamp The timestamp of the update
    event ScoreUpdated(address indexed agent, uint256 overall, uint256 timestamp);

    /// @notice Emitted with detailed score breakdown
    /// @param agent The address of the agent
    /// @param txScore Transaction success score (0-100)
    /// @param x402Score X402 profitability score (0-100)
    /// @param erc8004Score ERC8004 stability score (0-100)
    event ScoreBreakdownRecorded(address indexed agent, uint256 txScore, uint256 x402Score, uint256 erc8004Score);

    /// @notice Emitted when ownership is transferred
    /// @param previousOwner The address of the previous owner
    /// @param newOwner The address of the new owner
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    // ============ Errors ============

    /// @notice Thrown when caller is not the owner
    error NotOwner();

    /// @notice Thrown when agent is not registered
    error AgentNotRegistered();

    /// @notice Thrown when score exceeds maximum value
    error ScoreOutOfRange();

    /// @notice Thrown when confidence exceeds maximum value
    error ConfidenceOutOfRange();

    /// @notice Thrown when new owner address is zero
    error InvalidNewOwner();

    /// @notice Thrown when protocol type is invalid
    error InvalidProtocolType();

    // ============ Modifiers ============

    /// @notice Restricts function access to contract owner
    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    // ============ Constructor ============

    /// @notice Initializes the contract with the deployer as owner
    constructor() {
        owner = msg.sender;
        emit OwnershipTransferred(address(0), msg.sender);
    }

    // ============ Core Functions ============

    /// @notice Updates an agent's credit score
    /// @dev Only callable by owner. Calculates overall score using 40-40-20 weighting
    /// @param agent The address of the agent to update
    /// @param txScore Transaction success score (0-100)
    /// @param x402Score X402 profitability score (0-100)
    /// @param erc8004Score ERC8004 stability score (0-100)
    /// @param confidence Confidence level of the score (0-100)
    /// @param riskLevel Risk level string ("high", "medium", "low")
    /// @param ipfsBreakdown IPFS hash containing detailed breakdown
    function updateScore(
        address agent,
        uint256 txScore,
        uint256 x402Score,
        uint256 erc8004Score,
        uint256 confidence,
        string calldata riskLevel,
        string calldata ipfsBreakdown
    ) external onlyOwner {
        // Validate score ranges
        if (txScore > 100 || x402Score > 100 || erc8004Score > 100) {
            revert ScoreOutOfRange();
        }
        if (confidence > 100) {
            revert ConfidenceOutOfRange();
        }

        // Calculate overall score using 40-40-20 weighting
        // Result is in range 0-1000 (each component contributes up to its weight * 10)
        uint256 overall = (txScore * 40 + x402Score * 40 + erc8004Score * 20) / 10;

        // Check if this is a new agent
        if (scores[agent].timestamp == 0) {
            totalAgents++;
        }

        // Create the score
        Score memory newScore = Score({
            overall: overall,
            txSuccess: txScore,
            x402Profitability: x402Score,
            erc8004Stability: erc8004Score,
            confidence: confidence,
            riskLevel: riskLevel,
            timestamp: block.timestamp,
            ipfsBreakdown: ipfsBreakdown
        });

        // Update current score
        scores[agent] = newScore;

        // Add to history
        scoreHistory[agent].push(newScore);

        // Update last update timestamp
        lastUpdate[agent] = block.timestamp;

        // Emit events
        emit ScoreUpdated(agent, overall, block.timestamp);
        emit ScoreBreakdownRecorded(agent, txScore, x402Score, erc8004Score);
    }

    /// @notice Retrieves the full score for an agent
    /// @param agent The address of the agent
    /// @return The complete Score struct for the agent
    function getScore(address agent) external view returns (Score memory) {
        if (scores[agent].timestamp == 0) {
            revert AgentNotRegistered();
        }
        return scores[agent];
    }

    /// @notice Retrieves only the overall score for an agent (gas optimized)
    /// @param agent The address of the agent
    /// @return The overall score (0-1000)
    function getScoreOnly(address agent) external view returns (uint256) {
        if (scores[agent].timestamp == 0) {
            revert AgentNotRegistered();
        }
        return scores[agent].overall;
    }

    /// @notice Retrieves the score history for an agent
    /// @param agent The address of the agent
    /// @param limit Maximum number of recent scores to return
    /// @return Array of Score structs (most recent last)
    function getScoreHistory(address agent, uint256 limit) external view returns (Score[] memory) {
        Score[] storage history = scoreHistory[agent];
        uint256 historyLength = history.length;
        
        if (historyLength == 0) {
            return new Score[](0);
        }

        uint256 returnCount = limit > historyLength ? historyLength : limit;
        Score[] memory result = new Score[](returnCount);
        
        // Return the most recent scores
        uint256 startIndex = historyLength - returnCount;
        for (uint256 i = 0; i < returnCount; i++) {
            result[i] = history[startIndex + i];
        }
        
        return result;
    }

    /// @notice Assesses risk for a specific amount and protocol type
    /// @param agent The address of the agent
    /// @param amountUsdc The amount in USDC units to assess
    /// @param protocolType The type of protocol ("lending", "trading", "payment")
    /// @return assessment The complete RiskAssessment struct
    function assessRisk(
        address agent,
        uint256 amountUsdc,
        string calldata protocolType
    ) external view returns (RiskAssessment memory assessment) {
        if (scores[agent].timestamp == 0) {
            revert AgentNotRegistered();
        }

        Score storage agentScore = scores[agent];
        
        // Base risk level from overall score (inverse relationship)
        // Higher score = lower risk
        uint256 baseRisk = 100 - (agentScore.overall / 10);
        
        // Protocol-specific risk adjustment
        uint256 protocolRisk = 0;
        bytes32 protocolHash = keccak256(bytes(protocolType));
        
        if (protocolHash == keccak256(bytes("lending"))) {
            protocolRisk = 20; // 20% additional risk for lending
        } else if (protocolHash == keccak256(bytes("trading"))) {
            protocolRisk = 10; // 10% additional risk for trading
        } else if (protocolHash == keccak256(bytes("payment"))) {
            protocolRisk = 0; // No additional risk for payment
        } else {
            revert InvalidProtocolType();
        }

        // Calculate final risk level (capped at 100)
        uint256 finalRisk = baseRisk + protocolRisk;
        if (finalRisk > 100) {
            finalRisk = 100;
        }

        // Calculate default probability based on risk level and confidence
        // Lower confidence increases default probability
        uint256 defaultProb = (finalRisk * (100 - agentScore.confidence / 2)) / 100;
        if (defaultProb > 100) {
            defaultProb = 100;
        }

        // Calculate expected loss
        uint256 expectedLoss = (amountUsdc * defaultProb) / 100;

        // Determine positive factors
        string[] memory positiveFactors = new string[](3);
        uint256 positiveCount = 0;
        
        if (agentScore.txSuccess >= 70) {
            positiveFactors[positiveCount] = "High transaction success rate";
            positiveCount++;
        }
        if (agentScore.x402Profitability >= 70) {
            positiveFactors[positiveCount] = "Strong X402 profitability";
            positiveCount++;
        }
        if (agentScore.erc8004Stability >= 70) {
            positiveFactors[positiveCount] = "Excellent ERC8004 stability";
            positiveCount++;
        }

        // Resize positive factors array
        string[] memory trimmedPositive = new string[](positiveCount);
        for (uint256 i = 0; i < positiveCount; i++) {
            trimmedPositive[i] = positiveFactors[i];
        }

        // Determine risk factors
        string[] memory riskFactors = new string[](4);
        uint256 riskCount = 0;
        
        if (agentScore.txSuccess < 50) {
            riskFactors[riskCount] = "Low transaction success rate";
            riskCount++;
        }
        if (agentScore.x402Profitability < 50) {
            riskFactors[riskCount] = "Poor X402 profitability";
            riskCount++;
        }
        if (agentScore.erc8004Stability < 50) {
            riskFactors[riskCount] = "Low ERC8004 stability";
            riskCount++;
        }
        if (agentScore.confidence < 50) {
            riskFactors[riskCount] = "Low confidence in score accuracy";
            riskCount++;
        }

        // Resize risk factors array
        string[] memory trimmedRisk = new string[](riskCount);
        for (uint256 i = 0; i < riskCount; i++) {
            trimmedRisk[i] = riskFactors[i];
        }

        assessment = RiskAssessment({
            riskLevel: finalRisk,
            defaultProbability: defaultProb,
            expectedLoss: expectedLoss,
            positiveFactors: trimmedPositive,
            riskFactors: trimmedRisk
        });
    }

    /// @notice Checks if an agent is registered in the system
    /// @param agent The address of the agent
    /// @return True if the agent has a score record
    function isRegistered(address agent) external view returns (bool) {
        return scores[agent].timestamp != 0;
    }

    /// @notice Returns the total number of registered agents
    /// @return The count of unique agents with scores
    function getTotalAgents() external view returns (uint256) {
        return totalAgents;
    }

    // ============ Admin Functions ============

    /// @notice Transfers ownership of the contract to a new address
    /// @dev Only callable by current owner
    /// @param newOwner The address of the new owner
    function transferOwnership(address newOwner) external onlyOwner {
        if (newOwner == address(0)) {
            revert InvalidNewOwner();
        }
        
        address previousOwner = owner;
        owner = newOwner;
        
        emit OwnershipTransferred(previousOwner, newOwner);
    }
}
