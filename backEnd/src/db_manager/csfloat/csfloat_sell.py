from typing import Any, Dict, List

from ..base_model import BaseModel


class CsFloatSellModel(BaseModel):
    """CSFloat 销售记录表模型。"""

    @classmethod
    def get_table_name(cls) -> str:
        return "csfloat_sell"

    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "ID": {"type": "TEXT", "primary_key": True, "not_null": True},
            "contract_id": {"type": "TEXT", "not_null": False, "default": None},
            "weapon_name": {"type": "TEXT", "not_null": False, "default": None},
            "weapon_type": {"type": "TEXT", "not_null": False, "default": None},
            "item_name": {"type": "TEXT", "not_null": False, "default": None},
            "weapon_float": {"type": "REAL", "not_null": False, "default": None},
            "float_range": {"type": "TEXT", "not_null": False, "default": None},
            "price": {"type": "REAL", "not_null": False, "default": None},  # 人民币价格(CNY)
            "us_price": {"type": "REAL", "not_null": False, "default": None},  # 美元价格(USD)
            "price_original": {"type": "REAL", "not_null": False, "default": None},
            "buyer_name": {"type": "TEXT", "not_null": False, "default": None},
            "buyer_id": {"type": "TEXT", "not_null": False, "default": None},
            "seller_name": {"type": "TEXT", "not_null": False, "default": None},
            "seller_id": {"type": "TEXT", "not_null": False, "default": None},
            "state": {"type": "TEXT", "not_null": False, "default": None},
            "state_sub": {"type": "TEXT", "not_null": False, "default": None},
            "created_at": {"type": "DATETIME", "not_null": False, "default": None},
            "accepted_at": {"type": "DATETIME", "not_null": False, "default": None},
            "verified_at": {"type": "DATETIME", "not_null": False, "default": None},
            "trade_url": {"type": "TEXT", "not_null": False, "default": None},
            "trade_token": {"type": "TEXT", "not_null": False, "default": None},
            "steam_offer_id": {"type": "TEXT", "not_null": False, "default": None},
            "steam_offer_state": {"type": "TEXT", "not_null": False, "default": None},
            "verification_mode": {"type": "TEXT", "not_null": False, "default": None},
            "inventory_check_status": {"type": "INTEGER", "not_null": False, "default": None},
            "icon_url": {"type": "TEXT", "not_null": False, "default": None},
            "market_hash_name": {"type": "TEXT", "not_null": False, "default": None},
            "data_user": {"type": "TEXT", "not_null": False, "default": None},
            "from": {"type": "TEXT", "not_null": False, "default": "csfloat"},
            "role": {"type": "TEXT", "not_null": False, "default": "seller"},
        }

    @classmethod
    def get_indexes(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": "csfloat_sell_idx",
                "columns": [
                    "item_name",
                    "weapon_float",
                    "price",
                    "buyer_name",
                    "buyer_id",
                    "state",
                    "data_user",
                ],
            },
            {
                "name": "csfloat_sell_created_idx",
                "columns": ["created_at", "data_user"],
            },
        ]

    @classmethod
    def find_not_end_status(cls, data_user: str):
        return cls.find_all(
            "state NOT IN ('已完成', '已取消') AND data_user = ?", (data_user,)
        )

    @classmethod
    def get_latest_order(cls, data_user: str):
        records = cls.find_all(
            "data_user = ? ORDER BY created_at DESC", (data_user,), limit=1
        )
        return records[0] if records else None

