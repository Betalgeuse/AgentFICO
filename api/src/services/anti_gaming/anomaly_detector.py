"""
Anomaly Detection

급격한 행동 변화를 탐지하여 게이밍 시도를 방지합니다.

원칙: "급격한 변화 = 의심"
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import statistics
from .config_loader import load_config, is_feature_enabled


def detect_anomaly(
    agent_address: str,
    current_metrics: Dict[str, Any],
    historical_metrics: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    에이전트의 현재 메트릭이 이상한지 탐지합니다.
    
    Args:
        agent_address: 에이전트 주소
        current_metrics: 현재 기간의 메트릭
        historical_metrics: 과거 메트릭 리스트
    
    Returns:
        {
            "is_anomaly": bool,
            "anomaly_score": float (0-1),
            "flags": [...],
            "penalty_factor": float
        }
    """
    if not is_feature_enabled("anomaly"):
        return {
            "is_anomaly": False,
            "anomaly_score": 0.0,
            "flags": [],
            "penalty_factor": 1.0
        }
    
    config = load_config("anomaly")
    detection_methods = config.get("detection_methods", {})
    penalties = config.get("penalties", {})
    patterns = config.get("patterns", {})
    
    flags = []
    anomaly_scores = []
    
    # Z-Score 기반 탐지
    if detection_methods.get("z_score", {}).get("enabled", False):
        z_result = _check_z_score(
            current_metrics,
            historical_metrics,
            detection_methods["z_score"]
        )
        if z_result["is_anomaly"]:
            flags.append(z_result)
            anomaly_scores.append(z_result["score"])
    
    # 변화율 기반 탐지
    if detection_methods.get("rate_of_change", {}).get("enabled", False):
        roc_result = _check_rate_of_change(
            current_metrics,
            historical_metrics,
            detection_methods["rate_of_change"]
        )
        if roc_result["is_anomaly"]:
            flags.append(roc_result)
            anomaly_scores.append(roc_result["score"])
    
    # 패턴 기반 탐지
    if patterns.get("tx_burst", {}):
        burst_result = _check_tx_burst(
            current_metrics,
            patterns["tx_burst"]
        )
        if burst_result["is_anomaly"]:
            flags.append(burst_result)
            anomaly_scores.append(burst_result["score"])
    
    # 종합 판단
    is_anomaly = len(flags) > 0
    avg_anomaly_score = statistics.mean(anomaly_scores) if anomaly_scores else 0.0
    
    # 페널티 계산
    penalty_factor = 1.0
    if is_anomaly:
        immediate_penalty = penalties.get("immediate_penalty_percent", 10) / 100
        penalty_factor = 1.0 - (immediate_penalty * avg_anomaly_score)
    
    return {
        "is_anomaly": is_anomaly,
        "anomaly_score": avg_anomaly_score,
        "flags": flags,
        "penalty_factor": max(0.5, penalty_factor),  # 최소 50%는 유지
        "flag_duration_days": penalties.get("flag_duration_days", 14) if is_anomaly else 0
    }


def _check_z_score(
    current: Dict,
    historical: List[Dict],
    config: Dict
) -> Dict:
    """Z-Score 기반 이상 탐지"""
    threshold = config.get("threshold", 3.0)
    min_samples = config.get("min_samples", 10)
    
    if len(historical) < min_samples:
        return {"is_anomaly": False, "type": "z_score", "score": 0}
    
    # 트랜잭션 수 기준
    historical_tx_counts = [m.get("tx_count", 0) for m in historical]
    current_tx_count = current.get("tx_count", 0)
    
    if len(historical_tx_counts) < 2:
        return {"is_anomaly": False, "type": "z_score", "score": 0}
    
    mean = statistics.mean(historical_tx_counts)
    stdev = statistics.stdev(historical_tx_counts)
    
    if stdev == 0:
        return {"is_anomaly": False, "type": "z_score", "score": 0}
    
    z_score = (current_tx_count - mean) / stdev
    
    is_anomaly = abs(z_score) > threshold
    normalized_score = min(1.0, abs(z_score) / (threshold * 2))
    
    return {
        "is_anomaly": is_anomaly,
        "type": "z_score",
        "score": normalized_score if is_anomaly else 0,
        "z_score": z_score,
        "threshold": threshold,
        "metric": "tx_count"
    }


def _check_rate_of_change(
    current: Dict,
    historical: List[Dict],
    config: Dict
) -> Dict:
    """변화율 기반 이상 탐지"""
    max_weekly_increase = config.get("max_weekly_increase_percent", 30)
    
    if not historical:
        return {"is_anomaly": False, "type": "rate_of_change", "score": 0}
    
    # 가장 최근 historical과 비교
    prev = historical[-1] if historical else {}
    
    prev_success_rate = prev.get("success_rate", 0.5)
    current_success_rate = current.get("success_rate", 0.5)
    
    if prev_success_rate > 0:
        change_percent = ((current_success_rate - prev_success_rate) / prev_success_rate) * 100
    else:
        change_percent = 0
    
    is_anomaly = change_percent > max_weekly_increase
    normalized_score = min(1.0, change_percent / (max_weekly_increase * 2)) if is_anomaly else 0
    
    return {
        "is_anomaly": is_anomaly,
        "type": "rate_of_change",
        "score": normalized_score,
        "change_percent": change_percent,
        "threshold": max_weekly_increase
    }


def _check_tx_burst(current: Dict, config: Dict) -> Dict:
    """트랜잭션 버스트 탐지"""
    max_tx_count = config.get("max_tx_count", 100)
    window_hours = config.get("window_hours", 24)
    
    current_tx_count = current.get("tx_count_24h", current.get("tx_count", 0))
    
    is_anomaly = current_tx_count > max_tx_count
    normalized_score = min(1.0, current_tx_count / (max_tx_count * 2)) if is_anomaly else 0
    
    return {
        "is_anomaly": is_anomaly,
        "type": "tx_burst",
        "score": normalized_score,
        "tx_count": current_tx_count,
        "threshold": max_tx_count,
        "window_hours": window_hours
    }
