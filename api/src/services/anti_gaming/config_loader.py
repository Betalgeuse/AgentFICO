"""
Anti-Gaming Config Loader

AgentFICO-Config (Private) 레포에서 계수를 로드합니다.
계수는 비공개로 유지되어 게이밍을 방지합니다.

사용법:
    config = load_config("time_decay")
    weight = get_coefficient("time_decay", "decay_windows.0.weight")
"""

import os
import json
from pathlib import Path
from typing import Any, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# 기본 경로 (배포 환경에서 마운트)
DEFAULT_CONFIG_PATH = os.getenv(
    "AGENTFICO_CONFIG_PATH",
    "/etc/agentfico/config"
)

# 개발 환경용 로컬 경로
LOCAL_CONFIG_PATH = os.getenv(
    "AGENTFICO_LOCAL_CONFIG_PATH",
    str(Path(__file__).parent.parent.parent.parent.parent.parent / "AgentFICO-Config")
)

# 기본값 (config 없을 때 fallback - 실제 값과 다름)
DEFAULT_COEFFICIENTS = {
    "time_decay": {
        "enabled": True,
        "decay_windows": [
            {"days_from": 0, "days_to": 7, "weight": 1.0},
            {"days_from": 7, "days_to": 30, "weight": 0.5},
            {"days_from": 30, "days_to": 90, "weight": 0.3},
            {"days_from": 90, "days_to": None, "weight": 0.1},
        ]
    },
    "anomaly": {
        "enabled": True,
        "detection_methods": {
            "z_score": {"threshold": 3.0}
        }
    },
    "consistency": {
        "enabled": True,
        "tiers": [
            {"required_days": 30, "bonus_points": 20},
            {"required_days": 90, "bonus_points": 50},
            {"required_days": 180, "bonus_points": 100},
        ]
    },
    "tx_quality": {
        "enabled": True,
        "value_thresholds": {
            "dust_usd": 0.01,
            "low_usd": 1.0,
            "medium_usd": 10.0,
        }
    },
    "sybil": {
        "enabled": False
    }
}


def _get_config_path() -> Optional[Path]:
    """설정 파일 경로를 찾습니다."""
    # 1. 환경 변수로 지정된 경로
    if os.path.exists(DEFAULT_CONFIG_PATH):
        return Path(DEFAULT_CONFIG_PATH)
    
    # 2. 로컬 개발 경로
    local_path = Path(LOCAL_CONFIG_PATH)
    if local_path.exists():
        return local_path
    
    # 3. 상대 경로 시도
    relative_path = Path(__file__).parent.parent.parent.parent.parent.parent / "AgentFICO-Config"
    if relative_path.exists():
        return relative_path
    
    return None


@lru_cache(maxsize=10)
def load_config(name: str) -> dict:
    """
    계수 설정을 로드합니다.
    
    Args:
        name: 설정 이름 (time_decay, anomaly, consistency, tx_quality, sybil)
    
    Returns:
        설정 딕셔너리
    """
    config_path = _get_config_path()
    
    if config_path:
        json_file = config_path / "coefficients" / f"{name}.json"
        if json_file.exists():
            try:
                with open(json_file, "r") as f:
                    config = json.load(f)
                    logger.info(f"Loaded anti-gaming config: {name} from {json_file}")
                    return config
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load {json_file}: {e}")
    
    # Fallback to defaults
    logger.warning(f"Using default config for {name} (not production values)")
    return DEFAULT_COEFFICIENTS.get(name, {})


def get_coefficient(config_name: str, key_path: str, default: Any = None) -> Any:
    """
    특정 계수 값을 가져옵니다.
    
    Args:
        config_name: 설정 이름
        key_path: 점(.)으로 구분된 키 경로 (예: "decay_windows.0.weight")
        default: 기본값
    
    Returns:
        계수 값
    """
    config = load_config(config_name)
    
    keys = key_path.split(".")
    value = config
    
    try:
        for key in keys:
            if isinstance(value, list):
                value = value[int(key)]
            elif isinstance(value, dict):
                value = value[key]
            else:
                return default
        return value
    except (KeyError, IndexError, TypeError):
        return default


def is_feature_enabled(feature: str) -> bool:
    """Anti-Gaming 기능이 활성화되어 있는지 확인합니다."""
    # 환경 변수 우선
    env_key = f"AG_{feature.upper()}_ENABLED"
    env_value = os.getenv(env_key)
    if env_value is not None:
        return env_value.lower() in ("true", "1", "yes")
    
    # Config 파일에서 확인
    config = load_config(feature)
    return config.get("enabled", False)


def reload_configs():
    """캐시를 클리어하고 설정을 다시 로드합니다."""
    load_config.cache_clear()
    logger.info("Anti-gaming configs reloaded")
