"""
SteamMarket API 模块
层级蓝图注册：
- 从 settings/API.py 接收前缀 /backENDV2/src/use_webside/settings
- 注册所有 Steam市场 路由，添加 /steam_market/units/xxx 路径段
最终路径示例：
  /backENDV2/src/use_webside/settings/steam_market/units/buy/getBuyGameNames
  /backENDV2/src/use_webside/settings/steam_market/units/sell/getSellGameNames
"""
from flask import Blueprint
from .units.steam_market_handler import SteamMarketBuy, SteamMarketSell, SteamMarketCombined

steam_market_blueprint = Blueprint('steam_market_v2', __name__)

# ==================== Buy ====================
steam_market_blueprint.route('/steam_market/units/buy/getBuyGameNames', methods=['GET'])(SteamMarketBuy.get_buy_game_names)
steam_market_blueprint.route('/steam_market/units/buy/getBuyData/<int:min>/<int:max>', methods=['GET'])(SteamMarketBuy.get_buy_data)
steam_market_blueprint.route('/steam_market/units/buy/searchBuyByName/<itemName>', methods=['GET'])(SteamMarketBuy.search_buy_by_name)
steam_market_blueprint.route('/steam_market/units/buy/getBuyDataByGameName/<gameName>/<int:min>/<int:max>', methods=['GET'])(SteamMarketBuy.get_buy_data_by_game_name)
steam_market_blueprint.route('/steam_market/units/buy/getBuyStats', methods=['GET'])(SteamMarketBuy.get_buy_stats)
steam_market_blueprint.route('/steam_market/units/buy/getBuyStatsBySearch/<itemName>', methods=['GET'])(SteamMarketBuy.get_buy_stats_by_search)
steam_market_blueprint.route('/steam_market/units/buy/getBuyStatsByGameName/<gameName>', methods=['GET'])(SteamMarketBuy.get_buy_stats_by_game_name)
steam_market_blueprint.route('/steam_market/units/buy/searchBuyByTimeRange/<startDate>/<endDate>', methods=['GET'])(SteamMarketBuy.search_buy_by_time_range)
steam_market_blueprint.route('/steam_market/units/buy/getBuyStatsByTimeRange/<startDate>/<endDate>', methods=['GET'])(SteamMarketBuy.get_buy_stats_by_time_range)

# ==================== Sell ====================
steam_market_blueprint.route('/steam_market/units/sell/getSellGameNames', methods=['GET'])(SteamMarketSell.get_sell_game_names)
steam_market_blueprint.route('/steam_market/units/sell/getSellData/<int:min>/<int:max>', methods=['GET'])(SteamMarketSell.get_sell_data)
steam_market_blueprint.route('/steam_market/units/sell/searchSellByName/<itemName>', methods=['GET'])(SteamMarketSell.search_sell_by_name)
steam_market_blueprint.route('/steam_market/units/sell/getSellDataByGameName/<gameName>/<int:min>/<int:max>', methods=['GET'])(SteamMarketSell.get_sell_data_by_game_name)
steam_market_blueprint.route('/steam_market/units/sell/getSellStats', methods=['GET'])(SteamMarketSell.get_sell_stats)
steam_market_blueprint.route('/steam_market/units/sell/getSellStatsBySearch/<itemName>', methods=['GET'])(SteamMarketSell.get_sell_stats_by_search)
steam_market_blueprint.route('/steam_market/units/sell/getSellStatsByGameName/<gameName>', methods=['GET'])(SteamMarketSell.get_sell_stats_by_game_name)
steam_market_blueprint.route('/steam_market/units/sell/searchSellByTimeRange/<startDate>/<endDate>', methods=['GET'])(SteamMarketSell.search_sell_by_time_range)
steam_market_blueprint.route('/steam_market/units/sell/getSellStatsByTimeRange/<startDate>/<endDate>', methods=['GET'])(SteamMarketSell.get_sell_stats_by_time_range)

# ==================== Combined ====================
steam_market_blueprint.route('/steam_market/units/combined/getSteamMarketStats', methods=['GET'])(SteamMarketCombined.get_steam_market_stats)
