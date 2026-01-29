"""
Transaction Quality Assessment

모든 트랜잭션이 동등하지 않습니다.
의미 있는 트랜잭션만 인정하여 스팸을 방지합니다.

원칙: "더스트 스팸 = 효과 없음"
"""

from typing import List, Dict, Any
from .config_loader import load_config, is_feature_enabled


# 알려진 DeFi 프로토콜 컨트랙트 (샘플)
KNOWN_DEFI_CONTRACTS = {
    # Uniswap V3
    "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45": "uniswap",
    "0xe592427a0aece92de3edee1f18e0157c05861564": "uniswap",
    # Aave V3
    "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2": "aave",
    # 1inch
    "0x1111111254eeb25477b68fb85ed929f73a960582": "1inch",
}


def assess_transaction_quality(
    transactions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    트랜잭션의 품질을 평가합니다.
    
    Args:
        transactions: 트랜잭션 리스트
            [{
                "hash": str,
                "from": str,
                "to": str,
                "value": float (USD),
                "success": bool,
                "contract_address": str (optional)
            }, ...]
    
    Returns:
        {
            "quality_score": float (0-100),
            "weighted_success_rate": float,
            "diversity_bonus": float,
            "penalties": {...}
        }
    """
    if not is_feature_enabled("tx_quality"):
        return {
            "quality_score": 50.0,  # 중립
            "weighted_success_rate": _simple_success_rate(transactions),
            "diversity_bonus": 0,
            "penalties": {},
            "enabled": False
        }
    
    config = load_config("tx_quality")
    value_thresholds = config.get("value_thresholds", {})
    value_weights = config.get("value_weights", {})
    interaction_types = config.get("interaction_types", {})
    diversity_config = config.get("diversity_bonus", {})
    repetition_config = config.get("repetition_penalty", {})
    
    if not transactions:
        return {
            "quality_score": 0,
            "weighted_success_rate": 0,
            "diversity_bonus": 0,
            "penalties": {}
        }
    
    total_quality_weight = 0.0
    total_success_weight = 0.0
    unique_protocols = set()
    contract_counts = {}
    
    for tx in transactions:
        # 1. 금액 기반 가중치
        value_weight = _get_value_weight(
            tx.get("value", 0),
            value_thresholds,
            value_weights
        )
        
        # 2. 상호작용 유형 가중치
        interaction_weight = _get_interaction_weight(
            tx,
            interaction_types
        )
        
        # 3. 프로토콜 추적
        protocol = _identify_protocol(tx)
        if protocol:
            unique_protocols.add(protocol)
        
        # 4. 반복 추적
        contract = tx.get("to", "").lower()
        contract_counts[contract] = contract_counts.get(contract, 0) + 1
        
        # 종합 가중치
        tx_weight = value_weight * interaction_weight
        total_quality_weight += tx_weight
        
        if tx.get("success", True):
            total_success_weight += tx_weight
    
    # 다양성 보너스
    diversity_bonus = 0
    if diversity_config.get("enabled", False):
        min_protocols = diversity_config.get("min_unique_protocols", 3)
        if len(unique_protocols) >= min_protocols:
            bonus_per = diversity_config.get("bonus_per_protocol", 2)
            max_bonus = diversity_config.get("max_bonus", 10)
            diversity_bonus = min(
                (len(unique_protocols) - min_protocols + 1) * bonus_per,
                max_bonus
            )
    
    # 반복 페널티
    repetition_penalty = 0
    if repetition_config.get("enabled", False):
        threshold = repetition_config.get("same_contract_threshold", 10)
        penalty_per = repetition_config.get("penalty_per_repeat", 0.05)
        max_penalty = repetition_config.get("max_penalty_percent", 30) / 100
        
        for contract, count in contract_counts.items():
            if count > threshold:
                repetition_penalty += (count - threshold) * penalty_per
        
        repetition_penalty = min(repetition_penalty, max_penalty)
    
    # 최종 점수 계산
    base_quality = (total_quality_weight / len(transactions)) * 100 if transactions else 0
    weighted_success = total_success_weight / total_quality_weight if total_quality_weight > 0 else 0
    
    quality_score = base_quality + diversity_bonus - (repetition_penalty * 100)
    quality_score = max(0, min(100, quality_score))
    
    return {
        "quality_score": quality_score,
        "weighted_success_rate": weighted_success,
        "diversity_bonus": diversity_bonus,
        "unique_protocols": len(unique_protocols),
        "penalties": {
            "repetition": repetition_penalty * 100
        },
        "stats": {
            "total_transactions": len(transactions),
            "avg_value_weight": total_quality_weight / len(transactions) if transactions else 0
        }
    }


def _get_value_weight(
    value_usd: float,
    thresholds: Dict,
    weights: Dict
) -> float:
    """금액 기반 가중치 반환"""
    dust = thresholds.get("dust_usd", 0.01)
    low = thresholds.get("low_usd", 1.0)
    medium = thresholds.get("medium_usd", 10.0)
    high = thresholds.get("high_usd", 100.0)
    
    if value_usd < dust:
        return weights.get("dust", 0.05)
    elif value_usd < low:
        return weights.get("low", 0.3)
    elif value_usd < medium:
        return weights.get("medium", 0.7)
    else:
        return weights.get("high", 1.0)


def _get_interaction_weight(tx: Dict, interaction_types: Dict) -> float:
    """상호작용 유형 가중치 반환"""
    from_addr = tx.get("from", "").lower()
    to_addr = tx.get("to", "").lower()
    
    # 자기 자신에게 전송
    if from_addr == to_addr:
        return interaction_types.get("self_transfer", {}).get("weight", 0.1)
    
    # DeFi 프로토콜
    if to_addr in KNOWN_DEFI_CONTRACTS:
        return interaction_types.get("defi_interaction", {}).get("weight", 1.0)
    
    # 컨트랙트 상호작용 (input data 있음)
    if tx.get("input") and tx.get("input") != "0x":
        return interaction_types.get("contract_interaction", {}).get("weight", 0.7)
    
    # 단순 전송
    return interaction_types.get("simple_transfer", {}).get("weight", 0.4)


def _identify_protocol(tx: Dict) -> str:
    """트랜잭션이 어떤 프로토콜과 상호작용하는지 식별"""
    to_addr = tx.get("to", "").lower()
    return KNOWN_DEFI_CONTRACTS.get(to_addr)


def _simple_success_rate(transactions: List[Dict]) -> float:
    """단순 성공률"""
    if not transactions:
        return 0.0
    success = sum(1 for tx in transactions if tx.get("success", True))
    return success / len(transactions)
