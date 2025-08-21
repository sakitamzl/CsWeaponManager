from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
import requests


configV1 = Blueprint('configV1', __name__)

database_name = 'BUFF'


@configV1.route('/config_v1/<key1>/<key2>/<value>', methods=['post'])
def updata_config(key1, key2, value):
    sql = f"UPDATE `{database_name}`.`Config` SET  `value` = '{value}' WHERE `key1` = '{key1}' AND `key2` = '{key2}';"
    Date_base().update(sql)
    return '更新成功', 200

@configV1.route('/get_config/<key1>/<key2>', methods=['post'])
def get_yyyp_config(key1, key2):
    sql = f"SELECT value FROM `{database_name}`.`Config` WHERE key1 = '{key1}' and key2 = '{key2}'"
    flag, data = Date_base().select(sql)
    return jsonify(data), 200
