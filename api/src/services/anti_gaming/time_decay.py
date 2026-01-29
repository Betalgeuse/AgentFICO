"""
Time Decay Factor

최근 활동에 더 높은 가중치를 부여합니다.
과거 좋은 기록만으로 점수를 유지할 수 없게 합니다.

원칙: "지속적인 좋은 성과가 필요"
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .config_loader import load_config, is_feature_enabled


def apply_time_decay(
    transactions: List[Dict[str, Any]],
    reference_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    트랜잭션에 시간 기반 가중치를 적용합니다.
    
    Args:
        transactions: 트랜잭션 리스트 (각각 timestamp 필드 포함)
        reference_date: 기준 날짜 (기본: 현재)
    
    Returns:
        {
            "weighted_success_rate": float,
            "decay_applied": bool,
            "window_stats": {...}
        }
    """
    if not is_feature_enabled("time_decay"):
        return {
            "weighted_success_rate": _calculate_simple_success_rate(transactions),
            "decay_applied": False,
            "window_stats": {}
        }
    
    config = load_config("time_decay")
    decay_windows = config.get("decay_windows", [])
    min_tx_per_window = config.get("min_transactions_per_window", 3)
    no_activity_penalty = config.get("no_activity_penalty", 0.9)
    
    if reference_date is None:
        reference_date = datetime.utcnow()
    
    # 윈도우별로 트랜잭션 분류
    window_txs = {i: [] for i in range(len(decay_windows))}
    
    for tx in transactions:
        tx_date = _parse_timestamp(tx.get("timestamp"))
        if tx_date is None:
            continue
        
        days_ago = (reference_date - tx_date).days
        
        for i, window in enumerate(decay_windows):
            days_from = window.get("days_from", 0)
            days_to = window.get("days_to")
            
            if days_to is None:
                days_to = float("inf")
            
            if days_from <= days_ago < days_to:
                window_txs[i].append(tx)
                break
    
    # 가중 평균 계산
    total_weighted_success = 0.0
    total_weight = 0.0
    window_stats = {}
    
    for i, window in enumerate(decay_windows):
        txs = window_txs[i]
        weight = window.get("weight", 1.0)
        window_name = window.get("name", f"window_{i}")
        
        if len(txs) >= min_tx_per_window:
            success_count = sum(1 for tx in txs if tx.get("success", True))
            success_rate = success_count / len(txs) if txs else 0
            
            total_weighted_success += success_rate * weight * len(txs)
            total_weight += weight * len(txs)
            
            window_stats[window_name] = {
                "tx_count": len(txs),
                "success_rate": success_rate,
                "weight": weight,
                "contribution": success_rate * weight
            }
        else:
            window_stats[window_name] = {
                "tx_count": len(txs),
                "success_rate": None,
                "weight": weight,
                "contribution": 0,
                "note": "insufficient_data"
            }
    
    # 최근 활동 없으면 페널티
    recent_window = window_txs.get(0, [])
    if len(recent_window) < min_tx_per_window:
        total_weighted_success *= no_activity_penalty
        window_stats["penalty"] = {
            "type": "no_recent_activity",
            "factor": no_activity_penalty
        }
    
    weighted_success_rate = total_weighted_success / total_weight if total_weight > 0 else 0
    
    return {
        "weighted_success_rate": min(1.0, max(0.0, weighted_success_rate)),
        "decay_applied": True,
        "window_stats": window_stats,
        "total_transactions": len(transactions)
    }


def _calculate_simple_success_rate(transactions: List[Dict]) -> float:
    """단순 성공률 계산 (Time Decay 없이)"""
    if not transactions:
        return 0.0
    success_count = sum(1 for tx in transactions if tx.get("success", True))
    return success_count / len(transactions)


def _parse_timestamp(ts: Any) -> Optional[datetime]:
    """다양한 형식의 타임스탬프를 파싱"""
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, (int, float)):
        return datetime.utcfromtimestamp(ts)
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None
