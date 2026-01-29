"""
Consistency Bonus

장기간 안정적인 성과를 보이는 에이전트에 보너스를 부여합니다.
단기 조작으로는 얻을 수 없는 점수입니다.

원칙: "6개월 이상 좋은 성과 유지해야 최고 점수"
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .config_loader import load_config, is_feature_enabled


def calculate_consistency_bonus(
    performance_history: List[Dict[str, Any]],
    reference_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    일관성 보너스를 계산합니다.
    
    Args:
        performance_history: 일별/주별 성과 기록 리스트
            [{
                "date": datetime,
                "success_rate": float,
                "tx_count": int
            }, ...]
        reference_date: 기준 날짜
    
    Returns:
        {
            "bonus_points": int,
            "achieved_tier": str,
            "streak_days": int,
            "details": {...}
        }
    """
    if not is_feature_enabled("consistency"):
        return {
            "bonus_points": 0,
            "achieved_tier": None,
            "streak_days": 0,
            "details": {"enabled": False}
        }
    
    config = load_config("consistency")
    tiers = config.get("tiers", [])
    streak_rules = config.get("streak_rules", {})
    max_bonus = config.get("max_total_bonus", 100)
    
    if reference_date is None:
        reference_date = datetime.utcnow()
    
    # 연속 성공 일수 계산
    streak_info = _calculate_streak(
        performance_history,
        reference_date,
        streak_rules
    )
    
    # 달성 티어 확인
    achieved_tier = None
    bonus_points = 0
    
    for tier in sorted(tiers, key=lambda t: t.get("required_days", 0), reverse=True):
        required_days = tier.get("required_days", 30)
        min_success_rate = tier.get("min_success_rate", 0.8)
        tier_bonus = tier.get("bonus_points", 0)
        
        if streak_info["streak_days"] >= required_days:
            if streak_info["avg_success_rate"] >= min_success_rate:
                achieved_tier = tier.get("name", f"{required_days}d")
                bonus_points = tier_bonus
                break
    
    return {
        "bonus_points": min(bonus_points, max_bonus),
        "achieved_tier": achieved_tier,
        "streak_days": streak_info["streak_days"],
        "avg_success_rate": streak_info["avg_success_rate"],
        "details": {
            "tiers_checked": len(tiers),
            "break_tolerance": streak_rules.get("break_tolerance_days", 3),
            "min_activity_required": streak_rules.get("min_activity_per_week", 5)
        }
    }


def _calculate_streak(
    history: List[Dict],
    reference_date: datetime,
    rules: Dict
) -> Dict[str, Any]:
    """연속 성공 기간을 계산합니다."""
    break_tolerance = rules.get("break_tolerance_days", 3)
    min_activity_per_week = rules.get("min_activity_per_week", 5)
    
    if not history:
        return {"streak_days": 0, "avg_success_rate": 0.0}
    
    # 날짜순 정렬
    sorted_history = sorted(
        history,
        key=lambda x: x.get("date", datetime.min),
        reverse=True
    )
    
    streak_days = 0
    total_success_rate = 0.0
    valid_entries = 0
    consecutive_breaks = 0
    
    current_date = reference_date.date() if isinstance(reference_date, datetime) else reference_date
    
    for entry in sorted_history:
        entry_date = entry.get("date")
        if isinstance(entry_date, datetime):
            entry_date = entry_date.date()
        
        if entry_date is None:
            continue
        
        days_diff = (current_date - entry_date).days
        
        # 간격이 너무 크면 스트릭 끊김
        if days_diff > break_tolerance and consecutive_breaks >= break_tolerance:
            break
        
        success_rate = entry.get("success_rate", 0)
        tx_count = entry.get("tx_count", 0)
        
        # 활동이 충분한지 확인
        if tx_count >= (min_activity_per_week / 7):  # 일 기준
            if success_rate >= 0.7:  # 최소 성공률
                streak_days += 1
                total_success_rate += success_rate
                valid_entries += 1
                consecutive_breaks = 0
            else:
                consecutive_breaks += 1
        else:
            consecutive_breaks += 1
        
        current_date = entry_date
    
    avg_success_rate = total_success_rate / valid_entries if valid_entries > 0 else 0.0
    
    return {
        "streak_days": streak_days,
        "avg_success_rate": avg_success_rate,
        "valid_entries": valid_entries
    }
