// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";

/// @title AgentFICOScoreV2
/// @author AgentFICO Team
/// @notice Upgradeable AI Agent credit scoring system for DeFi protocols
/// @dev UUPS Proxy pattern for upgradeability. Network: Base (Chain ID: 8453/84532)
contract AgentFICOScoreV2 is 
    Initializable, 
    UUPSUpgradeable, 
    OwnableUpgradeable,
    ReentrancyGuardUpgradeable 
{
    // ============ Structs ============

    /// @notice Score structure containing agent credit metrics
    struct Score {
        uint256 overall;            // 0-1000 (40-40-20 weighted calculation)
        uint256 txSuccess;          // 0-100 (40% weight)
        uint256 x402Profitability;  // 0-100 (40% weight)
        uint256 erc8004Stability;   // 0-100 (20% weight)
        uint256 confidence;         // 0-100
        uint8 riskLevel;            // 1-5 (gas optimized from string)
        uint256 timestamp;
        bool antiGamingApplied;     // Whether anti-gaming adjustments were applied
    }

    /// @notice Risk assessment structure for lending/trading decisions
    struct RiskAssessment {
        uint256 riskLevel;          // 0-100
        uint256 defaultProbability; // 0-100 (%)
        uint256 expectedLoss;       // USDC units
    }

    // ============ Constants ============

    uint256 public constant VERSION = 2;
    uint256 public constant MAX_SCORE = 100;
    uint256 public constant MAX_OVERALL = 1000;
    
    // Risk levels
    uint8 public constant RISK_EXCELLENT = 1;  // 850+
    uint8 public constant RISK_GOOD = 2;       // 750-849
    uint8 public constant RISK_AVERAGE = 3;    // 650-749
    uint8 public constant RISK_BELOW_AVG = 4;  // 550-649
    uint8 public constant RISK_POOR = 5;       // <550

    // Update cooldown for user-triggered updates
    uint256 public constant USER_UPDATE_COOLDOWN = 1 hours;

    // ============ State Variables ============

    /// @notice Current score for each agent
    mapping(address => Score) public scores;

    /// @notice Historical scores count for each agent
    mapping(address => uint256) public scoreHistoryCount;

    /// @notice Last update timestamp for each agent
    mapping(address => uint256) public lastUpdate;

    /// @notice Total number of registered agents
    uint256 public totalAgents;

    /// @notice Fee for user-triggered score update (in wei)
    uint256 public userUpdateFee;

    /// @notice Accumulated fees ready for withdrawal
    uint256 public accumulatedFees;

    /// @notice Authorized oracles that can update scores
    mapping(address => bool) public authorizedOracles;

    // ============ Events ============

    event ScoreUpdated(
        address indexed agent, 
        uint256 overall, 
        uint8 riskLevel,
        bool antiGamingApplied,
        address indexed updatedBy
    );
    
    event UserTriggeredUpdate(
        address indexed agent,
        address indexed requester,
        uint256 feePaid
    );

    event OracleAuthorized(address indexed oracle, bool authorized);
    event UserUpdateFeeChanged(uint256 oldFee, uint256 newFee);
    event FeesWithdrawn(address indexed to, uint256 amount);

    // ============ Errors ============

    error ScoreOutOfRange();
    error ConfidenceOutOfRange();
    error AgentNotRegistered();
    error UnauthorizedOracle();
    error UpdateCooldownActive();
    error InsufficientFee();
    error WithdrawalFailed();
    error ZeroAddress();

    // ============ Modifiers ============

    modifier onlyAuthorized() {
        if (msg.sender != owner() && !authorizedOracles[msg.sender]) {
            revert UnauthorizedOracle();
        }
        _;
    }

    // ============ Initializer (replaces constructor) ============

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract (called once during proxy deployment)
    /// @param initialOwner The address of the initial owner
    function initialize(address initialOwner) public initializer {
        if (initialOwner == address(0)) revert ZeroAddress();
        
        __Ownable_init(initialOwner);
        __UUPSUpgradeable_init();
        __ReentrancyGuard_init();
        
        userUpdateFee = 0.001 ether; // Default fee: 0.001 ETH
    }

    // ============ UUPS Required ============

    /// @notice Authorizes contract upgrades (only owner)
    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}

    // ============ Core Functions ============

    /// @notice Updates an agent's credit score (owner/oracle only)
    /// @param agent The address of the agent to update
    /// @param txScore Transaction success score (0-100)
    /// @param x402Score X402 profitability score (0-100)
    /// @param erc8004Score ERC8004 stability score (0-100)
    /// @param confidence Confidence level of the score (0-100)
    /// @param antiGamingApplied Whether anti-gaming adjustments were applied
    function updateScore(
        address agent,
        uint256 txScore,
        uint256 x402Score,
        uint256 erc8004Score,
        uint256 confidence,
        bool antiGamingApplied
    ) external onlyAuthorized {
        _updateScore(agent, txScore, x402Score, erc8004Score, confidence, antiGamingApplied, msg.sender);
    }

    /// @notice Batch update multiple agents' scores (gas efficient)
    /// @param agents Array of agent addresses
    /// @param txScores Array of transaction success scores
    /// @param x402Scores Array of X402 profitability scores
    /// @param erc8004Scores Array of ERC8004 stability scores
    /// @param confidences Array of confidence levels
    /// @param antiGamingFlags Array of anti-gaming applied flags
    function batchUpdateScores(
        address[] calldata agents,
        uint256[] calldata txScores,
        uint256[] calldata x402Scores,
        uint256[] calldata erc8004Scores,
        uint256[] calldata confidences,
        bool[] calldata antiGamingFlags
    ) external onlyAuthorized {
        uint256 length = agents.length;
        require(
            length == txScores.length &&
            length == x402Scores.length &&
            length == erc8004Scores.length &&
            length == confidences.length &&
            length == antiGamingFlags.length,
            "Array length mismatch"
        );

        for (uint256 i = 0; i < length; i++) {
            _updateScore(
                agents[i],
                txScores[i],
                x402Scores[i],
                erc8004Scores[i],
                confidences[i],
                antiGamingFlags[i],
                msg.sender
            );
        }
    }

    /// @notice User-triggered score update (pays fee)
    /// @param agent The address of the agent to update
    /// @dev User pays gas + fee, oracle will update off-chain and call updateScore
    function requestScoreUpdate(address agent) external payable nonReentrant {
        if (msg.value < userUpdateFee) revert InsufficientFee();
        
        // Check cooldown (skip if never updated - lastUpdate is 0)
        uint256 lastUpdateTime = lastUpdate[agent];
        if (lastUpdateTime > 0 && block.timestamp < lastUpdateTime + USER_UPDATE_COOLDOWN) {
            revert UpdateCooldownActive();
        }

        accumulatedFees += msg.value;
        
        emit UserTriggeredUpdate(agent, msg.sender, msg.value);
        
        // Actual score update will be done by oracle listening to this event
    }

    /// @notice Internal score update logic
    function _updateScore(
        address agent,
        uint256 txScore,
        uint256 x402Score,
        uint256 erc8004Score,
        uint256 confidence,
        bool antiGamingApplied,
        address updatedBy
    ) internal {
        if (txScore > MAX_SCORE || x402Score > MAX_SCORE || erc8004Score > MAX_SCORE) {
            revert ScoreOutOfRange();
        }
        if (confidence > MAX_SCORE) {
            revert ConfidenceOutOfRange();
        }

        // Calculate overall score using 40-40-20 weighting
        uint256 overall = (txScore * 40 + x402Score * 40 + erc8004Score * 20) / 10;

        // Determine risk level
        uint8 riskLevel = _calculateRiskLevel(overall);

        // Check if new agent
        if (scores[agent].timestamp == 0) {
            totalAgents++;
        }

        // Update score
        scores[agent] = Score({
            overall: overall,
            txSuccess: txScore,
            x402Profitability: x402Score,
            erc8004Stability: erc8004Score,
            confidence: confidence,
            riskLevel: riskLevel,
            timestamp: block.timestamp,
            antiGamingApplied: antiGamingApplied
        });

        scoreHistoryCount[agent]++;
        lastUpdate[agent] = block.timestamp;

        emit ScoreUpdated(agent, overall, riskLevel, antiGamingApplied, updatedBy);
    }

    /// @notice Calculate risk level from overall score
    function _calculateRiskLevel(uint256 overall) internal pure returns (uint8) {
        if (overall >= 850) return RISK_EXCELLENT;
        if (overall >= 750) return RISK_GOOD;
        if (overall >= 650) return RISK_AVERAGE;
        if (overall >= 550) return RISK_BELOW_AVG;
        return RISK_POOR;
    }

    // ============ View Functions ============

    /// @notice Retrieves the full score for an agent
    function getScore(address agent) external view returns (Score memory) {
        if (scores[agent].timestamp == 0) revert AgentNotRegistered();
        return scores[agent];
    }

    /// @notice Retrieves only the overall score (gas optimized)
    function getScoreOnly(address agent) external view returns (uint256) {
        if (scores[agent].timestamp == 0) revert AgentNotRegistered();
        return scores[agent].overall;
    }

    /// @notice Assesses risk for a specific amount and protocol type
    /// @param agent The address of the agent
    /// @param amountUsdc The amount in USDC units
    /// @param protocolRiskBps Additional protocol risk in basis points (100 = 1%)
    function assessRisk(
        address agent,
        uint256 amountUsdc,
        uint256 protocolRiskBps
    ) external view returns (RiskAssessment memory) {
        if (scores[agent].timestamp == 0) revert AgentNotRegistered();

        Score storage s = scores[agent];
        
        // Base risk from score (inverse): score 1000 -> risk 0, score 0 -> risk 100
        uint256 baseRisk = 100 - (s.overall / 10);
        
        // Add protocol risk (convert bps to percentage)
        uint256 finalRisk = baseRisk + (protocolRiskBps / 100);
        if (finalRisk > 100) finalRisk = 100;

        // Calculate expected loss with full precision (multiply all before divide)
        // Formula: expectedLoss = amountUsdc * finalRisk * (200 - confidence) / 20000
        // This combines: (finalRisk/100) * ((200-confidence)/200) * amountUsdc
        uint256 expectedLoss = (amountUsdc * finalRisk * (200 - s.confidence)) / 20000;

        // Default probability for display (percentage)
        uint256 defaultProb = (finalRisk * (200 - s.confidence)) / 200;
        if (defaultProb > 100) defaultProb = 100;

        return RiskAssessment({
            riskLevel: finalRisk,
            defaultProbability: defaultProb,
            expectedLoss: expectedLoss
        });
    }

    /// @notice Check if agent is registered
    function isRegistered(address agent) external view returns (bool) {
        return scores[agent].timestamp != 0;
    }

    /// @notice Get time until next user-triggered update is allowed
    function getUpdateCooldown(address agent) external view returns (uint256) {
        uint256 nextUpdate = lastUpdate[agent] + USER_UPDATE_COOLDOWN;
        if (block.timestamp >= nextUpdate) return 0;
        return nextUpdate - block.timestamp;
    }

    // ============ Admin Functions ============

    /// @notice Set authorized oracle status
    function setOracle(address oracle, bool authorized) external onlyOwner {
        if (oracle == address(0)) revert ZeroAddress();
        authorizedOracles[oracle] = authorized;
        emit OracleAuthorized(oracle, authorized);
    }

    /// @notice Set user update fee
    function setUserUpdateFee(uint256 newFee) external onlyOwner {
        uint256 oldFee = userUpdateFee;
        userUpdateFee = newFee;
        emit UserUpdateFeeChanged(oldFee, newFee);
    }

    /// @notice Withdraw accumulated fees
    function withdrawFees(address payable to) external onlyOwner nonReentrant {
        if (to == address(0)) revert ZeroAddress();
        
        uint256 amount = accumulatedFees;
        accumulatedFees = 0;
        
        (bool success, ) = to.call{value: amount}("");
        if (!success) revert WithdrawalFailed();
        
        emit FeesWithdrawn(to, amount);
    }

    /// @notice Disable upgradeability permanently (make contract immutable)
    /// @dev WARNING: This is irreversible!
    function renounceUpgradeability() external onlyOwner {
        // After calling this, _authorizeUpgrade will always revert
        // because owner will be address(0)
        _transferOwnership(address(0));
    }
}
