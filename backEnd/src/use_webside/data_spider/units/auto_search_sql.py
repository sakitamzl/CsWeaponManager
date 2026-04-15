# -*- coding: utf-8 -*-
"""
auto_search_weapon 表的纯 SQL 辅助（供 data_spider 路由使用）
行转 API 字典逻辑与 AutoSearchWeaponModel.to_dict 保持一致。
"""
import json
from typing import Any, Dict, List, Optional, Tuple

from src.db_manager.database import DatabaseManager
from src.db_manager.index.model import AutoSearchWeaponModel

AUTO_SEARCH_TABLE = "auto_search_weapon"

# 与模型字段顺序一致，便于 SELECT 结果按元组下标解析
_SELECT_COLUMNS: Tuple[str, ...] = (
    "id", "steam_id", "config_id", "data_type", "weapon_id", "weapon_name",
    "commodity_id", "commodity_no", "price", "lowest_price", "spread",
    "abrade", "paint_seed", "name_tag", "seller_name", "pendant_count",
    "pendant_details", "asset_id", "steam_hash_name", "commission_fee",
    "price_diff", "pendant_total_price", "price_diff_percentage", "total_count",
    "status", "created_at", "updated_at",
)

SELECT_AUTO_SEARCH_SQL = f"SELECT {', '.join(_SELECT_COLUMNS)} FROM {AUTO_SEARCH_TABLE}"


def row_tuple_to_api_dict(row: Tuple[Any, ...]) -> Dict[str, Any]:
    d = dict(zip(_SELECT_COLUMNS, row))
    pendants_raw = d.get("pendant_details")
    pendants: List[Any] = []
    if pendants_raw:
        if isinstance(pendants_raw, (bytes, bytearray)):
            pendants_raw = pendants_raw.decode("utf-8", errors="ignore")
        if isinstance(pendants_raw, str):
            try:
                pendants = json.loads(pendants_raw)
            except (json.JSONDecodeError, TypeError):
                pendants = []
        elif isinstance(pendants_raw, list):
            pendants = pendants_raw

    weapon_id_value = d.get("weapon_id")
    weapon_name_value = d.get("weapon_name")
    if (
        weapon_name_value
        and isinstance(weapon_name_value, str)
        and weapon_name_value.isdigit()
        and weapon_id_value
        and isinstance(weapon_id_value, str)
        and not weapon_id_value.isdigit()
    ):
        weapon_id_value, weapon_name_value = weapon_name_value, weapon_id_value

    return {
        "id": d.get("id"),
        "configId": d.get("config_id"),
        "dataType": d.get("data_type"),
        "weaponId": weapon_id_value,
        "weaponName": weapon_name_value,
        "commodityId": d.get("commodity_id"),
        "commodityNo": d.get("commodity_no"),
        "listing_id": d.get("commodity_id"),
        "listingId": d.get("commodity_id"),
        "price": d.get("price"),
        "lowestPrice": d.get("lowest_price"),
        "spread": d.get("spread"),
        "abrade": d.get("abrade"),
        "paintSeed": d.get("paint_seed"),
        "nameTag": d.get("name_tag"),
        "sellerName": d.get("seller_name"),
        "assetId": d.get("asset_id"),
        "steamHashName": d.get("steam_hash_name"),
        "steam_hash_name": d.get("steam_hash_name"),
        "commissionFee": d.get("commission_fee"),
        "priceDiff": d.get("price_diff"),
        "pendantCount": d.get("pendant_count") or 0,
        "pendantTotalPrice": d.get("pendant_total_price") or 0,
        "priceDiffPercentage": d.get("price_diff_percentage") or 0,
        "totalCount": d.get("total_count") or 0,
        "pendants": pendants,
        "status": d.get("status"),
        "createdAt": d.get("created_at"),
        "updatedAt": d.get("updated_at"),
    }


def insert_from_search_result(db: DatabaseManager, **kwargs) -> int:
    """使用与 create_from_search_result 相同的字段逻辑，执行 INSERT，返回 lastrowid。"""
    record = AutoSearchWeaponModel.create_from_search_result(**kwargs)
    columns: List[str] = []
    params: List[Any] = []
    for name in AutoSearchWeaponModel.get_fields():
        if name == "id":
            continue
        v = getattr(record, name, None)
        if v is not None and (not isinstance(v, str) or v.strip() != ""):
            columns.append(name)
            params.append(v)
    placeholders = ", ".join(["?"] * len(params))
    col_sql = ", ".join(f"[{c}]" for c in columns)
    sql = f"INSERT INTO {AUTO_SEARCH_TABLE} ({col_sql}) VALUES ({placeholders})"
    return int(db.execute_insert(sql, tuple(params)) or 0)


def select_rows_to_api_dicts(
    db: DatabaseManager,
    where_and_order_sql: str,
    params: Tuple[Any, ...],
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    where_and_order_sql 示例：\"data_type = ? ORDER BY spread ASC, id DESC\"
    （与原先 AutoSearchWeaponModel.find_all 的 where 参数写法一致）
    """
    sql = f"{SELECT_AUTO_SEARCH_SQL} WHERE {where_and_order_sql}"
    qparams: List[Any] = list(params)
    if limit is not None:
        sql += " LIMIT ?"
        qparams.append(limit)
        # 与 BaseModel.find_all 一致：offset 为 0 时不拼 OFFSET
        if offset:
            sql += " OFFSET ?"
            qparams.append(offset)
    rows = db.execute_query(sql, tuple(qparams))
    return [row_tuple_to_api_dict(r) for r in rows] if rows else []


def count_rows(db: DatabaseManager, where_sql: str, params: Tuple[Any, ...]) -> int:
    sql = f"SELECT COUNT(*) FROM {AUTO_SEARCH_TABLE} WHERE {where_sql}"
    result = db.execute_query(sql, params)
    return int(result[0][0]) if result and result[0] else 0


def select_one_by_id(db: DatabaseManager, item_id: int) -> Optional[Dict[str, Any]]:
    sql = f"{SELECT_AUTO_SEARCH_SQL} WHERE id = ? LIMIT 1"
    rows = db.execute_query(sql, (item_id,))
    if not rows:
        return None
    return row_tuple_to_api_dict(rows[0])
