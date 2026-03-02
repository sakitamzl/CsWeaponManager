import os
import logging
from flask import Flask
from flask_cors import CORS
from src.config.config_v1 import configV1
from src.web_side.webSide.web.index_page import indexPage
from src.web_side.webSide.web.select_weapon import webSelectWeaponV1
from src.web_side.webSide.steamMarket import webSteamMarketV1

from src.web_side.webSide.sys_message_page import webSysMessagePageV1

from src.web_side.webSide.settings.search_pendant_config_api import search_pendant_config_bp
from src.web_side.webSide.settings.auto_search_weapon_api import search_rename_bp
from src.web_side.CSQAQ.csqaq_api import csqaqApiV1
from src.web_side.SteamDT.steamdt_api import steamdtApiV1
from src.web_side.data_webside.item_search import itemSearchApiV1
from src.db_manager import init_database
from src.Unites.auto_process.task_scheduler import get_scheduler

from src.API import backendV2_blueprint

# 当前版本号
CURRENT_VERSION = '2.4.2'

app = Flask(__name__)
CORS(app)

def blankEndApi():
    # print("Blank End API Start")
    # 只在主进程中初始化数据库，避免Flask debug模式重复初始化
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # 初始化数据库
        if not init_database():
            print("❌ 数据库初始化失败，程序退出")
            return
    
    # v2 API
    app.register_blueprint(backendV2_blueprint, url_prefix='/backENDV2')  # Home V2 API（逐层传递）

    app.register_blueprint(configV1, url_prefix = '/configV1')
    app.register_blueprint(indexPage, url_prefix = '/indexPage')
    app.register_blueprint(webSelectWeaponV1, url_prefix = '/webSelectWeaponV1')
    app.register_blueprint(webSteamMarketV1, url_prefix = '/webSteamMarketV1')
    app.register_blueprint(webSysMessagePageV1, url_prefix = '/api')


    # 挂件搜索配置进度保存 API
    app.register_blueprint(search_pendant_config_bp)
    app.register_blueprint(search_rename_bp)  # 改名饰品搜索API
    app.register_blueprint(csqaqApiV1, url_prefix='/csqaqApiV1')  # CSQAQ API
    app.register_blueprint(steamdtApiV1, url_prefix='/steamdtApiV1')  # SteamDT API
    app.register_blueprint(itemSearchApiV1, url_prefix='/itemSearchApiV1')  # 饰品搜索API
    
    # 禁用 werkzeug 的 HTTP 请求日志
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # 启动任务调度器 (只在主进程中启动)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = get_scheduler()
        scheduler.start()
        print("✅ 任务调度器已启动")
    
    app.run(debug=True, port=9001, host='0.0.0.0')

if __name__ == '__main__':
    blankEndApi()

