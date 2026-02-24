// API 配置文件

export const API_CONFIG = {

  // API 基础地址（通过代理访问）
  BASE_URL: '/api',

  // 业务后端地址（Flask backEnd，通常由前端代理到 9001 端口）
  BACKEND_BASE_URL: '/api',

  

  // 爬虫服务器地址（通过代理访问）
  SPIDER_BASE_URL: '/spider',

  

  // API 端点

  ENDPOINTS: {

    // 数据源相关

    DATA_SOURCE: '/dataSourcePageV1/api/datasource',

    DATA_SOURCE_TEST: '/dataSourcePageV1/api/datasource/test',

    DATA_SOURCE_COLLECT: (id) => `/dataSourcePageV1/api/datasource/${id}/collect`,

    DATA_SOURCE_TOGGLE: (id) => `/dataSourcePageV1/api/datasource/${id}/toggle`,

    DATA_SOURCE_BY_ID: (id) => `/dataSourcePageV1/api/datasource/${id}`,

    

    // 购买数据相关（V2 API）

    BUY_DATA_USER_LIST: '/backENDV2/src/web_display/buy/units/filters/getDataUserList',

    

    // 销售数据相关（V2 API）

    SELL_DATA_FILTERED: '/backENDV2/src/web_display/sell/units/data/getSellDataFiltered',

    SELL_STATS_FILTERED: '/backENDV2/src/web_display/sell/units/stats/getSellStatsFiltered',

    SELL_SEARCH_TIME_RANGE: (startDate, endDate) => `/backENDV2/src/web_display/sell/units/data/searchSellByTimeRange/${startDate}/${endDate}`,

    SELL_STATS_TIME_RANGE: (startDate, endDate) => `/backENDV2/src/web_display/sell/units/stats/getSellStatsByTimeRange/${startDate}/${endDate}`,

    SELL_DATA_USER_LIST: '/backENDV2/src/web_display/sell/units/filters/getDataUserList',

    SELL_SEARCH_BY_TYPE_WEAR: '/backENDV2/src/web_display/sell/units/data/searchByTypeAndWear',

    SELL_STATS_BY_TYPE_WEAR: '/backENDV2/src/web_display/sell/units/stats/getStatsByTypeAndWear',

    SELL_WEAPON_TYPES: '/backENDV2/src/web_display/sell/units/filters/getWeaponTypes',

    SELL_FLOAT_RANGES: '/backENDV2/src/web_display/sell/units/filters/getFloatRanges',

    SELL_STATUS_LIST: '/backENDV2/src/web_display/sell/units/filters/getStatusList',

    SELL_STATUS_SUB_LIST: (status) => `/backENDV2/src/web_display/sell/units/filters/getStatusSubList?status=${encodeURIComponent(status)}`,

    SELL_YYYP_PRICE_INFO: (steamHashName) => `/backENDV2/src/web_display/sell/units/price_info/getYyypPriceInfo/${encodeURIComponent(steamHashName)}`,

    BUY_STATS_FILTERED: '/backENDV2/src/web_display/buy/units/stats/getBuyStatsFiltered',

    BUY_DATA_FILTERED: '/backENDV2/src/web_display/buy/units/data/getBuyDataFiltered',

    BUY_COUNT_NUMBER: '/backENDV2/src/web_display/buy/units/data/countBuyNumber',

    BUY_SEARCH_TIME_RANGE: (startDate, endDate) => `/backENDV2/src/web_display/buy/units/data/searchBuyByTimeRange/${startDate}/${endDate}`,

    BUY_STATS_TIME_RANGE: (startDate, endDate) => `/backENDV2/src/web_display/buy/units/stats/getBuyStatsByTimeRange/${startDate}/${endDate}`,

    LENT_STATS_FILTERED: '/webLentPageV1/getLentStatsFiltered',

    LENT_DATA_FILTERED: '/webLentPageV1/getLentDataFiltered',



    // 消息数据相关

    MESSAGE_DATA: (page, limit) => `/webMessageBoxPageV1/getMessageData/${page}/${limit}`,

    MESSAGE_STATS: '/webMessageBoxPageV1/getMessageStats',

    MESSAGE_TYPES: '/webMessageBoxPageV1/getMessageTypes',

    MESSAGE_SEARCH_BY_KEYWORD: '/webMessageBoxPageV1/searchMessageByKeyword',

    MESSAGE_SEARCH_BY_TIME: '/webMessageBoxPageV1/searchMessageByTime',

    MESSAGE_SEARCH_BY_TYPE: '/webMessageBoxPageV1/searchMessageByType',



    // BUFF 消息数据相关（buff_messagebox 表）

    BUFF_MESSAGE_DATA: (page, limit) => `/buff163MessageV1/list/${page}/${limit}`,

    BUFF_MESSAGE_TYPES: '/buff163MessageV1/types',

    

    // Steam市场数据相关

    STEAM_BUY_DATA: (page, limit) => `/webSteamMarketV1/getSteamBuyData/${page}/${limit}`,

    STEAM_BUY_STATS: '/webSteamMarketV1/getSteamBuyStats',

    STEAM_BUY_STATS_BY_SEARCH: (keyword) => `/webSteamMarketV1/getSteamBuyStatsBySearch/${encodeURIComponent(keyword)}`,

    STEAM_BUY_STATS_BY_STATUS: (status) => `/webSteamMarketV1/getSteamBuyStatsByStatus/${status}`,

    STEAM_BUY_DATA_BY_STATUS: (status, page, limit) => `/webSteamMarketV1/getSteamBuyDataByStatus/${status}/${page}/${limit}`,

    STEAM_BUY_SEARCH_BY_NAME: (itemName) => `/webSteamMarketV1/selectSteamBuyWeaponName/${encodeURIComponent(itemName)}`,

    STEAM_BUY_SEARCH_BY_TIME: (startDate, endDate) => `/webSteamMarketV1/searchSteamBuyByTimeRange/${startDate}/${endDate}`,

    STEAM_BUY_STATS_BY_TIME: (startDate, endDate) => `/webSteamMarketV1/getSteamBuyStatsByTimeRange/${startDate}/${endDate}`,

    

    STEAM_SELL_DATA: (page, limit) => `/webSteamMarketV1/getSteamSellData/${page}/${limit}`,

    STEAM_SELL_STATS: '/webSteamMarketV1/getSteamSellStats',

    STEAM_SELL_STATS_BY_SEARCH: (keyword) => `/webSteamMarketV1/getSteamSellStatsBySearch/${encodeURIComponent(keyword)}`,

    STEAM_SELL_STATS_BY_STATUS: (status) => `/webSteamMarketV1/getSteamSellStatsByStatus/${status}`,

    STEAM_SELL_DATA_BY_STATUS: (status, page, limit) => `/webSteamMarketV1/getSteamSellDataByStatus/${status}/${page}/${limit}`,

    STEAM_SELL_SEARCH_BY_NAME: (itemName) => `/webSteamMarketV1/selectSteamSellWeaponName/${encodeURIComponent(itemName)}`,

    STEAM_SELL_SEARCH_BY_TIME: (startDate, endDate) => `/webSteamMarketV1/searchSteamSellByTimeRange/${startDate}/${endDate}`,

    STEAM_SELL_STATS_BY_TIME: (startDate, endDate) => `/webSteamMarketV1/getSteamSellStatsByTimeRange/${startDate}/${endDate}`,

    

    // 武器搜索相关

    SEARCH_WEAPON: (keyword) => `/webSelectWeaponV1/searchWeapon?keyword=${encodeURIComponent(keyword)}`,

    SEARCH_WEAPON_DETAIL: (keyword, exactMatch = false) => `/webSelectWeaponV1/searchWeaponDetail?keyword=${encodeURIComponent(keyword)}${exactMatch ? '&exactMatch=true' : ''}`,

    SEARCH_WEAPON_BY_PRICE_RANGE: '/webSelectWeaponV1/queryWeaponsByPriceRange',  // 按价格区间查询饰品（带在售数量筛选）

    

    // 类型和磨损等级搜索相关

    BUY_WEAPON_TYPES: '/backENDV2/src/web_display/buy/units/filters/getWeaponTypes',

    BUY_FLOAT_RANGES: '/backENDV2/src/web_display/buy/units/filters/getFloatRanges',

    BUY_STATUS_LIST: '/backENDV2/src/web_display/buy/units/filters/getStatusList',

    BUY_STATUS_SUB_LIST: (status) => `/backENDV2/src/web_display/buy/units/filters/getStatusSubList?status=${encodeURIComponent(status)}`,

    BUY_SEARCH_BY_TYPE_WEAR: '/backENDV2/src/web_display/buy/units/data/searchByTypeAndWear',

    BUY_STATS_BY_TYPE_WEAR: '/backENDV2/src/web_display/buy/units/stats/getStatsByTypeAndWear',

    BUY_YYYP_PRICE_INFO: (steamHashName) => `/backENDV2/src/web_display/buy/units/price_info/getYyypPriceInfo/${encodeURIComponent(steamHashName)}`,



    LENT_WEAPON_TYPES: '/webLentPageV1/getWeaponTypes',

    LENT_FLOAT_RANGES: '/webLentPageV1/getFloatRanges',

    LENT_STATUS_LIST: '/webLentPageV1/getStatusList',

    LENT_STATUS_SUB_LIST: (status) => `/webLentPageV1/getStatusSubList?status=${encodeURIComponent(status)}`,

    LENT_PLATFORM_LIST: '/webLentPageV1/getPlatformList',

    LENT_LENTER_LIST: '/webLentPageV1/getLenterList',

    LENT_SEARCH_BY_TYPE_WEAR: '/webLentPageV1/searchByTypeAndWear',

    LENT_STATS_BY_TYPE_WEAR: '/webLentPageV1/getStatsByTypeAndWear',

    

    // 租赁（借入）数据相关
    RENTAL_DATA: (min, max) => `/webRentalV1/getRentalData/${min}/${max}`,
    RENTAL_STATS: '/webRentalV1/getRentalStats',
    RENTAL_DATA_BY_STATUS: (status, min, max) => `/webRentalV1/getRentalDataByStatus/${encodeURIComponent(status)}/${min}/${max}`,
    RENTAL_DATA_BY_STATUS_SUB: (statusSub, min, max) => `/webRentalV1/getRentalDataByStatusSub/${encodeURIComponent(statusSub)}/${min}/${max}`,
    RENTAL_STATS_BY_STATUS_SUB: (statusSub) => `/webRentalV1/getRentalStatsByStatusSub/${encodeURIComponent(statusSub)}`,
    RENTAL_SEARCH_BY_NAME: (itemName) => `/webRentalV1/selectRentalWeaponName/${encodeURIComponent(itemName)}`,
    RENTAL_SEARCH_BY_TIME: (startDate, endDate) => `/webRentalV1/searchRentalByTimeRange/${startDate}/${endDate}`,
    RENTAL_STATS_BY_TIME: (startDate, endDate) => `/webRentalV1/getRentalStatsByTimeRange/${startDate}/${endDate}`,
    RENTAL_COUNT: '/webRentalV1/countRentalNumber',

    // AES工具相关（V2 API - 新版本）

    AES_DECRYPT: '/spiderApiV2/src/web_site/youping/units/settings/dev_tools/aesDecrypt',

    AES_CHECK_LICENSE: '/spiderApiV2/src/web_site/youping/units/settings/dev_tools/aesCheckLicense',

    AES_HEALTH: '/spiderApiV2/src/web_site/youping/units/settings/dev_tools/aesHealth',

    // AES工具相关（V1 API - 已废弃，保留向后兼容）

    AES_DECRYPT_V1: '/aesToolsV1/decrypt',

    AES_CHECK_LICENSE_V1: '/aesToolsV1/check-license',

    AES_HEALTH_V1: '/aesToolsV1/health',



    // 爬虫相关

    // 悠悠有品数据同步（V2 API）
    YOUPIN_SYNC_NEW_DATA: '/spiderApiV2/src/web_site/youping/units/settings/data_source/syncNewData',  // 同步新增数据
    YOUPIN_SYNC_HISTORY_DATA: '/spiderApiV2/src/web_site/youping/units/settings/data_source/syncHistoryData',  // 同步历史数据
    YOUPIN_SYNC_WEAPON_PRICE: '/spiderApiV2/src/web_site/youping/units/settings/dev_tools/syncWeaponPrice',  // 同步价格数据
    YOUPIN_SYNC_WEAPON_TEMPLATES: '/spiderApiV2/src/web_site/youping/units/settings/dev_tools/syncWeaponTemplates',  // 同步武器模板

    YOUPIN_FETCH_ICONS: '/youpin898SelectWeaponV1/fetchWeaponIcons',   // 批量获取饰品图片

    YOUPIN_DOWNLOAD_ICONS: '/spiderApiV2/src/web_site/youping/units/settings/dev_tools/downloadWeaponIcons',   // 下载武器图标资源

    // BUFF数据同步（V2 API）
    BUFF_SYNC_NEW_DATA: '/spiderApiV2/src/web_site/buff/units/settings/data_source/syncNewData',  // 同步新增数据
    BUFF_SYNC_HISTORY_DATA: '/spiderApiV2/src/web_site/buff/units/settings/data_source/syncHistoryData',  // 同步历史数据

    // BUFF消息同步（V2 API）
    BUFF_SYNC_NEW_MESSAGES: '/spiderApiV2/src/web_site/buff/units/settings/buff_message_box/syncNewMessages',  // 同步新消息（增量）
    BUFF_SYNC_HISTORY_MESSAGES: '/spiderApiV2/src/web_site/buff/units/settings/buff_message_box/syncHistoryMessages',  // 同步历史消息（全量）

    // BUFF库存（V2 API）
    BUFF_GET_PRICE: '/spiderApiV2/src/web_site/buff/units/inventory/getBUFFPrice',  // 获取BUFF库存价格

    BUFF_SYNC_TEMPLATES: '/spiderApiV2/src/web_site/buff/units/settings/dev_tools/syncBuffTemplates',  // 同步BUFF饰品映射

    // BUFF商品搜索（V2 API）
    BUFF_GET_COMMODITIES: '/spiderApiV2/src/web_site/buff/units/item_search/on_sale/getCommoditiesByGoodsId',  // 获取BUFF商品在售列表

    // CSFloat 数据同步（V2 API）
    CSFLOAT_SYNC_NEW_DATA: '/spiderApiV2/src/web_site/csfloat/units/settings/data_source/syncNewData',  // CSFloat增量采集
    CSFLOAT_SYNC_HISTORY_DATA: '/spiderApiV2/src/web_site/csfloat/units/settings/data_source/syncHistoryData',  // CSFloat全量采集

    // 完美世界 库存组件（V2 API）
    PW_GET_INVENTORY_COMPONENT: '/spiderApiV2/src/web_site/prefectworld/units/stock_components/get_component/getInventoryComponent',  // 获取库存组件数据
    PW_DEPOSIT_TO_COMPONENT: '/spiderApiV2/src/web_site/prefectworld/units/stock_components/move_component/depositToComponent',  // 存入/取出物品到组件

    // Steam 数据同步（V2 API）
    STEAM_SYNC_NEW_DATA: '/spiderApiV2/src/web_site/steam/units/settings/data_source/syncNewData',  // Steam增量采集
    STEAM_SYNC_HISTORY_DATA: '/spiderApiV2/src/web_site/steam/units/settings/data_source/syncHistoryData',  // Steam全量采集

    // Steam 库存（V2 API）
    STEAM_GET_INVENTORY: '/spiderApiV2/src/web_site/steam/units/inventory/getInventory',  // 获取Steam库存

    // Steam 市场（V2 API）
    STEAM_COLLECT_HASH_NAMES: '/spiderApiV2/src/web_site/steam/units/market/hash_name/collectMarketHashNames',  // 采集Steam市场Hash Names
    STEAM_FETCH_HASH_NAMES: '/spiderApiV2/src/web_site/steam/units/market/hash_name/fetchSteamHashNames',  // 获取Steam饰品哈希（批量）
    STEAM_FETCH_HASH_NAMES_BY_WEAPON: '/spiderApiV2/src/web_site/steam/units/market/hash_name/fetchSteamHashNamesByWeapon',  // 获取Steam饰品哈希（单个武器）
    STEAM_SEARCH_RENAME: '/spiderApiV2/src/web_site/steam/units/mining/search_rename/searchRenameWeapon',  // Steam 改名饰品搜索
    STEAM_BUY_MARKET_ITEM: '/spiderApiV2/src/web_site/steam/units/market/buy/buyMarketItem',  // Steam 市场购买物品

    // Steam 库存挖掘（V2 API）
    STEAM_MINE_INVENTORY: '/spiderApiV2/src/web_site/steam/units/mining/mineInventory',  // 库存挖掘
    STEAM_CANCEL_MINING: '/spiderApiV2/src/web_site/steam/units/mining/cancelMining',  // 取消挖掘

    CSQAQ_MARKET_INDEX: '/spiderApiV2/src/web_site/csqaq/units/home/market_index/getMarketIndex',  // CSQAQ市场指数（V2 API）
    CSQAQ_KLINE: '/spiderApiV2/src/web_site/csqaq/units/data_website/market_overview/getKline',  // CSQAQ K线数据（V2 API）

    CSQAQ_GET_GOODS: '/csqaqSpiderV1/getGoodsList',  // CSQAQ同步获取商品

    CSQAQ_GET_GOODS_ASYNC: '/csqaqSpiderV1/getGoodsListAsync',  // CSQAQ异步获取商品

    CSQAQ_TASK_STATUS: '/csqaqSpiderV1/getTaskStatus',  // CSQAQ获取任务状态

    // 悠悠有品求购供应

    // 悠悠有品商品搜索 - 求购供应相关（新API V2）
    YOUPIN_GET_SUPPLY_LIST: '/spiderApiV2/src/web_site/youping/units/item_search/purchase_order/supply/getSupplyList',  // 获取可供应的库存列表
    YOUPIN_SUBMIT_SUPPLY: '/spiderApiV2/src/web_site/youping/units/item_search/purchase_order/supply/submitSupply',  // 提交供应（查询手续费）
    YOUPIN_CONFIRM_SUPPLY: '/spiderApiV2/src/web_site/youping/units/item_search/purchase_order/supply/confirmSupply',  // 确认供应
    YOUPIN_SEND_OFFER: '/spiderApiV2/src/web_site/youping/units/item_search/purchase_order/supply/sendOffer',  // 发送报价

    // 悠悠有品商品搜索 - ItemSearch页面相关（新API V2，按商品类型组织）
    YYYP_ITEM_SEARCH_ON_SALE_LIST: '/spiderApiV2/src/web_site/youping/units/item_search/on_sale/getCommodityList',  // 在售商品列表
    YYYP_ITEM_SEARCH_ON_SALE_DETAIL: '/spiderApiV2/src/web_site/youping/units/item_search/on_sale/getWeaponDetail',  // 在售商品详情
    YYYP_ITEM_SEARCH_BUY_COMMODITY: '/spiderApiV2/src/web_site/youping/units/item_search/on_sale/buyCommodity',  // 购买在售商品

    YYYP_ITEM_SEARCH_ON_LEASE_LIST: '/spiderApiV2/src/web_site/youping/units/item_search/on_lease/getCommodityList',  // 在租商品列表

    YYYP_ITEM_SEARCH_PRESALE_LIST: '/spiderApiV2/src/web_site/youping/units/item_search/presale/getCommodityList',  // 预售商品列表
    YYYP_ITEM_SEARCH_PRESALE_DETAIL: '/spiderApiV2/src/web_site/youping/units/item_search/presale/getPresaleDetail',  // 预售详情
    YYYP_ITEM_SEARCH_BUY_PRESALE: '/spiderApiV2/src/web_site/youping/units/item_search/presale/buyPresaleCommodity',  // 购买预售商品

    YYYP_ITEM_SEARCH_PURCHASE_ORDER_LIST: '/spiderApiV2/src/web_site/youping/units/item_search/purchase_order/getCommodityList',  // 求购订单列表

    YYYP_ITEM_SEARCH_PRICE_TREND: '/spiderApiV2/src/web_site/youping/units/item_search/price_trend/getPriceTrend',  // 价格走势

    YOUPIN_SELL_INVENTORY_ITEM: '/spiderApiV2/src/web_site/youping/units/inventory/sell/sellInventoryItem',  // 上架单个库存饰品（新版API）

    CSQAQ_TASK_RESULT: '/csqaqSpiderV1/getTaskResult',  // CSQAQ获取任务结果

    CSQAQ_EXPORT: '/csqaqSpiderV1/exportGoods',  // CSQAQ导出商品

    // SteamDT相关（V2 API）
    STEAMDT_MARKET_INDEX: '/spiderApiV2/src/web_site/steamdt/units/home/market_index/getMarketIndex',  // 获取SteamDT大盘指数
    STEAMDT_MARKET_INDEX_HEADLESS: '/spiderApiV2/src/web_site/steamdt/units/home/market_index/getMarketIndexHeadless',  // 获取SteamDT大盘指数（无头浏览器）
    STEAMDT_KLINE: '/spiderApiV2/src/web_site/steamdt/units/data_website/market_overview/getKline',  // 获取SteamDT K线数据
    STEAMDT_HOMEPAGE_DATA: '/steamdtApiV1/api/steamdt/homepage-data',  // 获取SteamDT首页数据（饰品成交额等）



    // Steam登录相关（V2 API）
    STEAM_LOGIN: '/spiderApiV2/src/web_site/steam/units/settings/data_source/auth/login',
    STEAM_LOGIN_VERIFY: '/spiderApiV2/src/web_site/steam/units/settings/data_source/auth/verify',
    STEAM_LOGIN_REFRESH: '/spiderApiV2/src/web_site/steam/units/settings/data_source/auth/refresh',
    STEAM_LOGIN_REFRESH_AUTO: '/spiderApiV2/src/web_site/steam/units/settings/data_source/auth/refresh_auto',
    STEAM_LOGIN_CAPTCHA: (captchaGid) => `/spiderApiV2/src/web_site/steam/units/settings/data_source/auth/captcha/${captchaGid}`,
    STEAM_LOGIN_GENERATE_CODE: '/spiderApiV2/src/web_site/steam/units/settings/data_source/auth/generate_code',
    STEAM_QR_GENERATE: '/spiderApiV2/src/web_site/steam/units/settings/data_source/auth/qrcode/generate',
    STEAM_QR_POLL: '/spiderApiV2/src/web_site/steam/units/settings/data_source/auth/qrcode/poll',

    

    // GetAppToken 相关接口（V2）

    GET_APP_TOKEN_START_BUFF: '/spiderApiV2/src/get_app_token/units/settings/data_source/buff/start_proxy',  // 启动BUFF代理

    GET_APP_TOKEN_STOP_BUFF: '/spiderApiV2/src/get_app_token/units/settings/data_source/buff/stop_proxy',  // 停止BUFF代理

    GET_APP_TOKEN_GET_BUFF_DATA: '/spiderApiV2/src/get_app_token/units/settings/data_source/buff/get_data',  // 获取BUFF数据

    GET_APP_TOKEN_CLEAR_BUFF_DATA: '/spiderApiV2/src/get_app_token/units/settings/data_source/buff/clear_data',  // 清除BUFF数据

    GET_APP_TOKEN_START_YYYP: '/spiderApiV2/src/get_app_token/units/settings/data_source/yyyp/start_proxy',  // 启动悠悠有品代理

    GET_APP_TOKEN_STOP_YYYP: '/spiderApiV2/src/get_app_token/units/settings/data_source/yyyp/stop_proxy',  // 停止悠悠有品代理

    GET_APP_TOKEN_GET_YYYP_DATA: '/spiderApiV2/src/get_app_token/units/settings/data_source/yyyp/get_data',  // 获取悠悠有品数据

    GET_APP_TOKEN_CLEAR_YYYP_DATA: '/spiderApiV2/src/get_app_token/units/settings/data_source/yyyp/clear_data',  // 清除悠悠有品数据

    GET_APP_TOKEN_START_PERFECTWORLD: '/spiderApiV2/src/get_app_token/units/settings/data_source/perfectworld/start_proxy',  // 启动完美世界APP代理

    GET_APP_TOKEN_STOP_PERFECTWORLD: '/spiderApiV2/src/get_app_token/units/settings/data_source/perfectworld/stop_proxy',  // 停止完美世界APP代理

    GET_APP_TOKEN_GET_PERFECTWORLD_DATA: '/spiderApiV2/src/get_app_token/units/settings/data_source/perfectworld/get_data',  // 获取完美世界APP数据

    GET_APP_TOKEN_CLEAR_PERFECTWORLD_DATA: '/spiderApiV2/src/get_app_token/units/settings/data_source/perfectworld/clear_data',  // 清除完美世界APP数据

    GET_APP_TOKEN_START_CSFLOAT: '/spiderApiV2/src/get_app_token/units/settings/data_source/csfloat/start_proxy',  // 启动CsFloat代理

    GET_APP_TOKEN_STOP_CSFLOAT: '/spiderApiV2/src/get_app_token/units/settings/data_source/csfloat/stop_proxy',  // 停止CsFloat代理

    GET_APP_TOKEN_GET_CSFLOAT_DATA: '/spiderApiV2/src/get_app_token/units/settings/data_source/csfloat/get_data',  // 获取CsFloat数据

    GET_APP_TOKEN_CLEAR_CSFLOAT_DATA: '/spiderApiV2/src/get_app_token/units/settings/data_source/csfloat/clear_data',  // 清除CsFloat数据

    GET_APP_TOKEN_PROXY_STATUS: '/spiderApiV2/src/get_app_token/units/settings/data_source/proxy_status',  // 查询代理状态

    GET_APP_TOKEN_HELP: '/spiderApiV2/src/get_app_token/units/settings/data_source/help',  // 获取帮助信息

    

    // ADB工具相关

    ADB_SCAN: '/adbToolsV1/api/adb/scan',  // 扫描局域网设备

    ADB_CONNECT: '/adbToolsV1/api/adb/connect',  // 连接设备

    ADB_DISCONNECT: '/adbToolsV1/api/adb/disconnect',  // 断开设备连接

    ADB_DEVICES: '/adbToolsV1/api/adb/devices',  // 获取ADB设备列表

    ADB_DEVICE_INFO: (serial) => `/adbToolsV1/api/adb/device/${serial}/info`,  // 获取设备信息

    ADB_CERT_STATUS: '/adbToolsV1/api/adb/cert/status',  // 检查证书状态

    ADB_CERT_INSTALL: '/adbToolsV1/api/adb/cert/install',  // 安装证书

    ADB_CERT_UNINSTALL: '/adbToolsV1/api/adb/cert/uninstall',  // 卸载证书

    ADB_CERT_INFO: '/adbToolsV1/api/adb/cert/info',  // 获取证书信息

    ADB_SHELL: (serial) => `/adbToolsV1/api/adb/device/${serial}/shell`,  // 执行Shell命令

    

    // CSQAQ相关

    CSQAQ_UPLOAD_MAPPING: '/csqaqApiV1/api/csqaq/upload-mapping',  // 上传CSQAQ映射文件

    

    // 图片相关

    WEAPON_IMAGE: (imageName) => `/api/v1/images/weapon_image/${imageName}`,  // 获取武器图片

    WEAPON_IMAGE_CHECK: (imageName) => `/api/v1/images/weapon_image/check/${imageName}`,  // 检查武器图片是否存在

    

    // Home页面图表数据（V2 API）

    HOME_INVENTORY_ALL: '/backENDV2/src/web_display/home/units/charts/inventory/all',  // 获取所有库存数据

    HOME_COMPONENTS_ALL: '/backENDV2/src/web_display/home/units/charts/components/all',  // 获取所有库存组件数据

    HOME_BUY_ALL: '/backENDV2/src/web_display/home/units/charts/buy/all',  // 获取所有购入数据

    HOME_SELL_ALL: '/backENDV2/src/web_display/home/units/charts/sell/all',  // 获取所有出售数据

    // Home页面独立API（V2，从其他模块分离）

    HOME_BUY_STATS: '/backENDV2/src/web_display/home/units/buy_stats/getBuyStats',  // 购买统计

    HOME_STEAM_IDS: '/backENDV2/src/web_display/home/units/steam_accounts/steam_ids',  // Steam账号列表

    HOME_INVENTORY_BY_STEAM_ID: (steamId) => `/backENDV2/src/web_display/home/units/inventory/${steamId}`,  // 指定账号库存

    HOME_COMPONENTS_BY_STEAM_ID: (steamId) => `/backENDV2/src/web_display/home/units/components/${steamId}`,  // 指定账号组件

    HOME_STEAMDT_HOMEPAGE_DATA: '/backENDV2/src/web_display/home/units/steamdt/homepage-data',  // SteamDT首页数据

    

    // 正在出售相关

    ON_SALE_YYYP_ACCOUNTS: '/webOnSaleV1/getYYYPAccounts',  // 获取悠悠有品账号列表

    ON_SALE_BUFF_ACCOUNTS: '/webOnSaleV1/getBuffAccounts',  // 获取BUFF账号列表

    ON_SALE_ITEMS: '/webOnSaleV1/getOnSaleItems',  // 获取在售商品列表

    ON_SALE_REMOVE: '/webOnSaleV1/removeFromSale',  // 下架商品

    

    // 悠悠有品租赁相关

    YYYP_GET_LEASE_LIST: '/spiderApiV2/src/web_site/youping/units/on_sale/lent/getLeaseList',  // 获取租赁列表（新API）
    YYYP_GET_SUBLEASE_LIST: '/spiderApiV2/src/web_site/youping/units/on_sale/sublease/getSubleaseList',  // 获取转租列表（新API）
    YYYP_GET_SELL_LIST: '/spiderApiV2/src/web_site/youping/units/on_sale/sell/getSellList',  // 获取出售列表（新API）
    YYYP_GET_RENTED_OUT_LIST: '/spiderApiV2/src/web_site/youping/units/on_sale/rented_out/getRentedOutList',  // 获取已租出列表（新API）
    YYYP_GET_MY_SELL_ORDERS: '/spiderApiV2/src/web_site/youping/units/on_sale/offer_handling/getMySellOrders',  // 获取我的出售订单（报价处理，新API）
    YYYP_GET_MY_BUY_ORDERS: '/spiderApiV2/src/web_site/youping/units/on_sale/offer_handling/getMyBuyOrders',  // 获取我的收货订单（报价处理，新API）
    YYYP_PROCESS_OFFER_BUTTON: '/spiderApiV2/src/web_site/youping/units/on_sale/offer_handling/processOfferButton',  // 处理报价按钮操作（新API）
    YYYP_GET_PURCHASE_ORDERS: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/getPurchaseOrders',  // 获取求购订单（求购中/暂停中，新API）
    YYYP_GET_PENDING_PAYMENT_ORDERS: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/getPendingPaymentOrders',  // 获取待支付订单（新API）
    YYYP_PAUSE_PURCHASE_ORDER: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/purchasing/pauseOrder',  // 暂停求购订单（新API）
    YYYP_OPEN_PURCHASE_ORDER: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/paused/openOrder',  // 开启暂停中的求购订单
    YYYP_DELETE_PURCHASE_ORDER: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/purchasing/deleteOrder',  // 删除求购订单（新API）
    YYYP_GET_ORDER_INFO: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/purchasing/getOrderInfo',  // 获取订单详情（新API）
    YYYP_PRE_UPDATE_CHECK: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/purchasing/preUpdateCheck',  // 修改前置检查（新API）
    YYYP_EDIT_PURCHASE_ORDER: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/purchasing/editOrder',  // 修改求购订单（新API）
    YYYP_QUICK_PRICE_INCREASE: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/purchasing/quickIncrease',  // 一键加价预检查（新API）
    YYYP_CONFIRM_PRICE_INCREASE: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/purchasing/confirmQuickIncrease',  // 确认一键加价（新API）
    YYYP_GET_PURCHASE_RECORDS: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/history/getRecords',  // 获取求购记录（分页）
    YYYP_SEARCH_PURCHASE_TEMPLATE: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/search/queryTemplate',  // 搜索求购饰品模板
    YYYP_GET_TEMPLATE_PURCHASE_INFO: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/search/getTemplateInfo',  // 获取求购发布详情
    YYYP_PRE_PURCHASE_ORDER_CHECK: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/search/preCheck',  // 求购预检查
    YYYP_SAVE_PURCHASE_ORDER: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/search/saveOrder',  // 提交求购订单
    YYYP_GET_PURCHASE_BALANCE: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/search/getBalance',  // 获取求购余额
    YYYP_QUERY_TRANSFER_IN_BALANCE: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/search/queryTransferInBalance',  // 查询钱包可转入余额
    YYYP_CONFIRM_TRANSFER_IN: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/search/confirmTransferIn',  // 确认从钱包转入
    YYYP_CONFIRM_TRANSFER_OUT: '/spiderApiV2/src/web_site/youping/units/on_sale/purchase_request/search/confirmTransferOut',  // 确认转出到钱包
    YYYP_OFF_SHELF: '/spiderApiV2/src/web_site/youping/units/on_sale/sell/offShelf',  // 下架商品（新API）
    YYYP_CANCEL_SUBLEASE: '/spiderApiV2/src/web_site/youping/units/on_sale/sublease/cancelSublease',  // 取消转租（新API）
    YYYP_CHANGE_PRICE: '/spiderApiV2/src/web_site/youping/units/on_sale/sell/changePrice',  // 改价（售卖商品，新API）
    YYYP_BATCH_CHANGE_PRICE: '/spiderApiV2/src/web_site/youping/units/on_sale/sell/batchChangePrice',  // 批量改价（售卖商品，新API）
    YYYP_CHANGE_RENT_PRICE: '/spiderApiV2/src/web_site/youping/units/on_sale/lent/changePrice',  // 改价（租赁/转租，支持单个和批量，新API）
    YYYP_GET_INSTANT_PAYMENT_LIST: '/spiderApiV2/src/web_site/youping/units/on_sale/instant/getInstantPaymentList',  // 获取0CD(秒到账)订单列表（新API）
    YYYP_GET_SUBLEASE_AGREEMENT: '/spiderApiV2/src/web_site/youping/units/on_sale/sublease/getSubleaseAgreement',  // 获取转租协议（新API）
    YYYP_GET_SUBLEASE_DETAIL: '/spiderApiV2/src/web_site/youping/units/on_sale/sublease/getSubleaseDetail',  // 获取转租详情（新API）
    YYYP_RENT_INIT: '/spiderApiV2/src/web_site/youping/units/on_sale/lent/rentInit',  // 获取出租初始化配置（新API）
    YYYP_GET_COMPENSATION_TEXT: '/spiderApiV2/src/web_site/youping/units/on_sale/lent/getCompensationText',  // 获取赔付文本信息（新API）

    // 悠悠有品消息盒子相关（新API V2）
    YYYP_GET_NEW_MESSAGES: '/spiderApiV2/src/web_site/youping/units/settings/yyyp_message_box/getNewMessages',  // 获取新消息（增量采集）
    YYYP_GET_ALL_MESSAGES: '/spiderApiV2/src/web_site/youping/units/settings/yyyp_message_box/getAllMessages',  // 获取所有消息（全量采集）
    YYYP_MARK_MESSAGE_READ: '/spiderApiV2/src/web_site/youping/units/settings/yyyp_message_box/markMessageRead',  // 标记消息为已读
    YYYP_DELETE_MESSAGE: '/spiderApiV2/src/web_site/youping/units/settings/yyyp_message_box/deleteMessage',  // 删除消息

    // 悠悠有品预售相关（新API V2）
    YYYP_GET_PRESALE_LIST: '/spiderApiV2/src/web_site/youping/units/on_sale/presale/getPresaleList',  // 获取预售列表
    YYYP_GET_PRESALE_DETAIL: '/spiderApiV2/src/web_site/youping/units/item_search/presale/getPresaleDetail',  // 获取预售详情
    YYYP_BUY_PRESALE_COMMODITY: '/spiderApiV2/src/web_site/youping/units/item_search/presale/buyPresaleCommodity',  // 购买预售商品

    // 悠悠有品过户相关（新API V2）
    YYYP_GET_TRANSFER_LIST: '/spiderApiV2/src/web_site/youping/units/on_sale/transfer/getTransferList',  // 获取过户列表

    // 悠悠有品转租相关（新API V2）
    YYYP_CHANGE_SUBLEASE_PRICE: '/spiderApiV2/src/web_site/youping/units/on_sale/sublease/changeSubleasePrice',  // 修改转租价格（0CD改价）
    YYYP_SUBLEASE_AUTO_PRICING: '/spiderApiV2/src/web_site/youping/units/on_sale/sublease/autoPricing',  // 转租商品自动定价
    YYYP_SUBLEASE_GET_COMPENSATION_TEXT: '/spiderApiV2/src/web_site/youping/units/on_sale/sublease/getCompensationText',  // 获取转租赔付文本信息
    YYYP_SUBLEASE_GET_BATCH_COMPENSATION_TEXT: '/spiderApiV2/src/web_site/youping/units/on_sale/sublease/getBatchCompensationText',  // 批量获取转租赔付文本信息

    // 悠悠有品出租自动定价（爬虫端）
    YYYP_RENT_AUTO_PRICING: '/spiderApiV2/src/web_site/youping/units/on_sale/lent/autoPricing',

    

    // 登录设置相关

    LOGIN_SETTINGS: '/loginSettingsV1/api/login-settings',  // 获取/保存登录设置

    LOGIN_VERIFY: '/loginSettingsV1/api/login-settings/verify',  // 验证登录



    // 版本更新相关

    UPDATE_CHECK: '/api/update/check',  // 检查更新

    UPDATE_CURRENT_VERSION: '/api/update/current-version',  // 获取当前版本

    UPDATE_DOWNLOAD: '/api/update/download',  // 下载更新包

    UPDATE_CHECK_LOCAL: '/api/update/check-local',  // 检查本地更新包

    UPDATE_APPLY: '/api/update/apply',  // 执行更新

    // 悠悠有品自动购买相关（V2 API）
    AUTO_BUY_RENAMED_WEAPON: '/spiderApiV2/src/web_site/youping/auto_weapon/autoBuyRenamedWeapon',  // 自动购买改名武器
    AUTO_BUY_PENDANT_WEAPON: '/spiderApiV2/src/web_site/youping/auto_weapon/autoBuyPendantWeapon',  // 自动购买挂件武器
    STOP_PENDANT_SEARCH: '/spiderApiV2/src/web_site/youping/auto_weapon/stopPendantSearch',  // 停止挂件搜索
    GET_PENDANT_SEARCH_PROGRESS: '/spiderApiV2/src/web_site/youping/auto_weapon/getPendantSearchProgress',  // 获取挂件搜索进度
    REALTIME_LOWEST_PRICE: '/spiderApiV2/src/web_site/youping/auto_weapon/getRealTimeLowestPrice',  // 实时查询悠悠在售底价

  },

  // 悠悠有品自动购买相关（V2 API） - 顶层配置（向后兼容）
  YOUPIN_AUTO_BUY_RENAMED_WEAPON: '/spiderApiV2/src/web_site/youping/auto_weapon/autoBuyRenamedWeapon',  // 自动购买改名武器
  YOUPIN_AUTO_BUY_PENDANT_WEAPON: '/spiderApiV2/src/web_site/youping/auto_weapon/autoBuyPendantWeapon',  // 自动购买挂件武器
  YOUPIN_STOP_PENDANT_SEARCH: '/spiderApiV2/src/web_site/youping/auto_weapon/stopPendantSearch',  // 停止挂件搜索
  YOUPIN_GET_PENDANT_SEARCH_PROGRESS: '/spiderApiV2/src/web_site/youping/auto_weapon/getPendantSearchProgress',  // 获取挂件搜索进度
  YOUPIN_REALTIME_LOWEST_PRICE: '/spiderApiV2/src/web_site/youping/auto_weapon/getRealTimeLowestPrice',  // 实时查询悠悠在售底价

  // 悠悠有品库存租借相关（V2 API） - 顶层配置（向后兼容）
  YOUPIN_GET_INVENTORY_EXTEND_INFO: '/spiderApiV2/src/web_site/youping/units/inventory/lent/getInventoryExtendInfo',  // 获取库存扩展信息
  YOUPIN_UPLOAD_RENT: '/spiderApiV2/src/web_site/youping/units/inventory/lent/uploadRent'  // 上传租借饰品

}



// 获取完整的 API URL

export const getApiUrl = (endpoint) => {

  return `${API_CONFIG.BASE_URL}${endpoint}`

}



// 获取完整的爬虫 API URL

export const getSpiderApiUrl = (endpoint) => {

  return `${API_CONFIG.SPIDER_BASE_URL}${endpoint}`

}



// 快捷方法

export const apiUrls = {

  // 数据源

  dataSource: () => getApiUrl(API_CONFIG.ENDPOINTS.DATA_SOURCE),

  dataSourceTest: () => getApiUrl(API_CONFIG.ENDPOINTS.DATA_SOURCE_TEST),

  dataSourceCollect: (id) => getApiUrl(API_CONFIG.ENDPOINTS.DATA_SOURCE_COLLECT(id)),

  dataSourceToggle: (id) => getApiUrl(API_CONFIG.ENDPOINTS.DATA_SOURCE_TOGGLE(id)),

  dataSourceById: (id) => getApiUrl(API_CONFIG.ENDPOINTS.DATA_SOURCE_BY_ID(id)),

  updateDataSource: (id) => getApiUrl(API_CONFIG.ENDPOINTS.DATA_SOURCE_BY_ID(id)),  // PUT 更新数据源

  

  // 购买数据（V2 API）

  buyStatsFiltered: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_STATS_FILTERED),

  buyDataFiltered: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_DATA_FILTERED),

  buyCountNumber: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_COUNT_NUMBER),

  buySearchTimeRange: (startDate, endDate) => getApiUrl(API_CONFIG.ENDPOINTS.BUY_SEARCH_TIME_RANGE(startDate, endDate)),

  buyStatsTimeRange: (startDate, endDate) => getApiUrl(API_CONFIG.ENDPOINTS.BUY_STATS_TIME_RANGE(startDate, endDate)),

  buyDataUserList: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_DATA_USER_LIST),

  

  // 销售数据（V2 API）

  sellStatsFiltered: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_STATS_FILTERED),

  sellDataFiltered: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_DATA_FILTERED),

  sellSearchTimeRange: (startDate, endDate) => getApiUrl(API_CONFIG.ENDPOINTS.SELL_SEARCH_TIME_RANGE(startDate, endDate)),

  sellStatsTimeRange: (startDate, endDate) => getApiUrl(API_CONFIG.ENDPOINTS.SELL_STATS_TIME_RANGE(startDate, endDate)),

  sellDataUserList: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_DATA_USER_LIST),

  

  // 租赁数据

  lentStatsFiltered: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_STATS_FILTERED),

  lentDataFiltered: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_DATA_FILTERED),

  

  // 消息数据

  messageData: (page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.MESSAGE_DATA(page, limit)),

  messageStats: () => getApiUrl(API_CONFIG.ENDPOINTS.MESSAGE_STATS),

  messageTypes: () => getApiUrl(API_CONFIG.ENDPOINTS.MESSAGE_TYPES),

  searchMessageByKeyword: () => getApiUrl(API_CONFIG.ENDPOINTS.MESSAGE_SEARCH_BY_KEYWORD),

  searchMessageByTime: () => getApiUrl(API_CONFIG.ENDPOINTS.MESSAGE_SEARCH_BY_TIME),

  searchMessageByType: () => getApiUrl(API_CONFIG.ENDPOINTS.MESSAGE_SEARCH_BY_TYPE),



  // BUFF 消息数据（buff_messagebox）

  buffMessageData: (page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.BUFF_MESSAGE_DATA(page, limit)),

  buffMessageTypes: () => getApiUrl(API_CONFIG.ENDPOINTS.BUFF_MESSAGE_TYPES),

  

  // Steam购买数据

  steamBuyData: (page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_BUY_DATA(page, limit)),

  steamBuyStats: () => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_BUY_STATS),

  steamBuyStatsBySearch: (keyword) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_BUY_STATS_BY_SEARCH(keyword)),

  steamBuyStatsByStatus: (status) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_BUY_STATS_BY_STATUS(status)),

  steamBuyDataByStatus: (status, page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_BUY_DATA_BY_STATUS(status, page, limit)),

  steamBuySearchByName: (itemName) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_BUY_SEARCH_BY_NAME(itemName)),

  steamBuySearchByTime: (startDate, endDate) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_BUY_SEARCH_BY_TIME(startDate, endDate)),

  steamBuyStatsByTime: (startDate, endDate) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_BUY_STATS_BY_TIME(startDate, endDate)),

  

  // Steam销售数据

  steamSellData: (page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_SELL_DATA(page, limit)),

  steamSellStats: () => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_SELL_STATS),

  steamSellStatsBySearch: (keyword) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_SELL_STATS_BY_SEARCH(keyword)),

  steamSellStatsByStatus: (status) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_SELL_STATS_BY_STATUS(status)),

  steamSellDataByStatus: (status, page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_SELL_DATA_BY_STATUS(status, page, limit)),

  steamSellSearchByName: (itemName) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_SELL_SEARCH_BY_NAME(itemName)),

  steamSellSearchByTime: (startDate, endDate) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_SELL_SEARCH_BY_TIME(startDate, endDate)),

  steamSellStatsByTime: (startDate, endDate) => getApiUrl(API_CONFIG.ENDPOINTS.STEAM_SELL_STATS_BY_TIME(startDate, endDate)),

  

  // 类型和磨损等级搜索

  buyWeaponTypes: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_WEAPON_TYPES),

  buyFloatRanges: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_FLOAT_RANGES),

  buyStatusList: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_STATUS_LIST),

  buyStatusSubList: (status) => getApiUrl(API_CONFIG.ENDPOINTS.BUY_STATUS_SUB_LIST(status)),

  buySearchByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_SEARCH_BY_TYPE_WEAR),

  buyStatsByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_STATS_BY_TYPE_WEAR),

  buyYyypPriceInfo: (steamHashName) => getApiUrl(API_CONFIG.ENDPOINTS.BUY_YYYP_PRICE_INFO(steamHashName)),



  sellWeaponTypes: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_WEAPON_TYPES),

  sellFloatRanges: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_FLOAT_RANGES),

  sellStatusList: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_STATUS_LIST),

  sellStatusSubList: (status) => getApiUrl(API_CONFIG.ENDPOINTS.SELL_STATUS_SUB_LIST(status)),

  sellSearchByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_SEARCH_BY_TYPE_WEAR),

  sellStatsByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_STATS_BY_TYPE_WEAR),

  sellYyypPriceInfo: (steamHashName) => getApiUrl(API_CONFIG.ENDPOINTS.SELL_YYYP_PRICE_INFO(steamHashName)),



  lentWeaponTypes: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_WEAPON_TYPES),

  lentFloatRanges: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_FLOAT_RANGES),

  lentStatusList: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_STATUS_LIST),

  lentStatusSubList: (status) => getApiUrl(API_CONFIG.ENDPOINTS.LENT_STATUS_SUB_LIST(status)),

  lentPlatformList: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_PLATFORM_LIST),

  lentLenterList: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_LENTER_LIST),

  lentSearchByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_SEARCH_BY_TYPE_WEAR),

  lentStatsByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_STATS_BY_TYPE_WEAR),

  
  // 租赁（借入）数据
  rentalData: (min, max) => getApiUrl(API_CONFIG.ENDPOINTS.RENTAL_DATA(min, max)),
  rentalStats: () => getApiUrl(API_CONFIG.ENDPOINTS.RENTAL_STATS),
  rentalDataByStatus: (status, min, max) => getApiUrl(API_CONFIG.ENDPOINTS.RENTAL_DATA_BY_STATUS(status, min, max)),
  rentalDataByStatusSub: (statusSub, min, max) => getApiUrl(API_CONFIG.ENDPOINTS.RENTAL_DATA_BY_STATUS_SUB(statusSub, min, max)),
  rentalStatsByStatusSub: (statusSub) => getApiUrl(API_CONFIG.ENDPOINTS.RENTAL_STATS_BY_STATUS_SUB(statusSub)),
  rentalSearchByName: (itemName) => getApiUrl(API_CONFIG.ENDPOINTS.RENTAL_SEARCH_BY_NAME(itemName)),
  rentalSearchByTime: (startDate, endDate) => getApiUrl(API_CONFIG.ENDPOINTS.RENTAL_SEARCH_BY_TIME(startDate, endDate)),
  rentalStatsByTime: (startDate, endDate) => getApiUrl(API_CONFIG.ENDPOINTS.RENTAL_STATS_BY_TIME(startDate, endDate)),
  rentalCount: () => getApiUrl(API_CONFIG.ENDPOINTS.RENTAL_COUNT),

  

  // 武器搜索

  searchWeapon: (keyword) => getApiUrl(API_CONFIG.ENDPOINTS.SEARCH_WEAPON(keyword)),

  searchWeaponDetail: (keyword, exactMatch = false) => getApiUrl(API_CONFIG.ENDPOINTS.SEARCH_WEAPON_DETAIL(keyword, exactMatch)),

  searchWeaponByPriceRange: () => getApiUrl(API_CONFIG.ENDPOINTS.SEARCH_WEAPON_BY_PRICE_RANGE),

  

  // 爬虫API

  // AES工具相关
  aesDecrypt: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.AES_DECRYPT),
  aesCheckLicense: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.AES_CHECK_LICENSE),
  aesHealth: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.AES_HEALTH),

  // 悠悠有品数据同步（V2 API）
  youpinSyncNewData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_SYNC_NEW_DATA),
  youpinSyncHistoryData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_SYNC_HISTORY_DATA),
  youpinSyncWeaponPrice: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_SYNC_WEAPON_PRICE),
  youpinSyncWeaponTemplates: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_SYNC_WEAPON_TEMPLATES),

  fetchWeaponIcons: () => getApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_FETCH_ICONS),
  downloadWeaponIcons: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_DOWNLOAD_ICONS),
  buffSyncNewData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_SYNC_NEW_DATA),
  buffSyncHistoryData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_SYNC_HISTORY_DATA),
  buffSyncNewMessages: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_SYNC_NEW_MESSAGES),
  buffSyncHistoryMessages: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_SYNC_HISTORY_MESSAGES),
  buffGetPrice: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_GET_PRICE),

  buffSyncTemplates: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_SYNC_TEMPLATES),
  buffGetCommodities: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_GET_COMMODITIES),

  steamSyncNewData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_SYNC_NEW_DATA),
  steamSyncHistoryData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_SYNC_HISTORY_DATA),
  steamGetInventory: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_GET_INVENTORY),
  steamCollectHashNames: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_COLLECT_HASH_NAMES),
  steamFetchHashNames: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_FETCH_HASH_NAMES),
  steamFetchHashNamesByWeapon: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_FETCH_HASH_NAMES_BY_WEAPON),
  steamMineInventory: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_MINE_INVENTORY),
  steamCancelMining: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_CANCEL_MINING),

  csqaqMarketIndex: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_MARKET_INDEX),
  csqaqKline: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_KLINE),

  csqaqGetGoods: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_GET_GOODS),

  csqaqGetGoodsAsync: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_GET_GOODS_ASYNC),

  csqaqTaskStatus: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_TASK_STATUS),

  csqaqTaskResult: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_TASK_RESULT),

  csqaqExport: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_EXPORT),

  autoBuyRenamedWeapon: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.AUTO_BUY_RENAMED_WEAPON),

  

  // 悠悠有品实时查询API

  youpinRealtimeLowestPrice: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_REALTIME_LOWEST_PRICE),

  // 悠悠有品求购供应API

  youpinGetSupplyList: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_GET_SUPPLY_LIST),

  youpinSubmitSupply: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_SUBMIT_SUPPLY),

  youpinConfirmSupply: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_CONFIRM_SUPPLY),

  youpinSendOffer: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_SEND_OFFER),

  youpinSellInventoryItem: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_SELL_INVENTORY_ITEM),



  // Steam登录API

  steamLogin: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_LOGIN),
  steamLoginVerify: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_LOGIN_VERIFY),
  steamLoginRefresh: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_LOGIN_REFRESH),
  steamLoginRefreshAuto: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_LOGIN_REFRESH_AUTO),
  steamLoginCaptcha: (captchaGid) => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_LOGIN_CAPTCHA(captchaGid)),
  steamLoginGenerateCode: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_LOGIN_GENERATE_CODE),
  steamQRGenerate: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_QR_GENERATE),
  steamQRPoll: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_QR_POLL),

  

  // GetAppToken API

  getAppTokenStartBuff: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_START_BUFF),

  getAppTokenStopBuff: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_STOP_BUFF),

  getAppTokenGetBuffData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_GET_BUFF_DATA),

  getAppTokenClearBuffData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_CLEAR_BUFF_DATA),

  getAppTokenStartYyyp: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_START_YYYP),

  getAppTokenStopYyyp: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_STOP_YYYP),

  getAppTokenGetYyypData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_GET_YYYP_DATA),

  getAppTokenClearYyypData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_CLEAR_YYYP_DATA),

  getAppTokenStartPerfectWorld: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_START_PERFECTWORLD),

  getAppTokenStopPerfectWorld: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_STOP_PERFECTWORLD),

  getAppTokenGetPerfectWorldData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_GET_PERFECTWORLD_DATA),

  getAppTokenClearPerfectWorldData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_CLEAR_PERFECTWORLD_DATA),

  getAppTokenStartCsfloat: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_START_CSFLOAT),

  getAppTokenStopCsfloat: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_STOP_CSFLOAT),

  getAppTokenGetCsfloatData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_GET_CSFLOAT_DATA),

  getAppTokenClearCsfloatData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_CLEAR_CSFLOAT_DATA),

  csfloatSyncNewData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSFLOAT_SYNC_NEW_DATA),

  csfloatSyncHistoryData: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSFLOAT_SYNC_HISTORY_DATA),

  pwGetInventoryComponent: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.PW_GET_INVENTORY_COMPONENT),

  pwDepositToComponent: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.PW_DEPOSIT_TO_COMPONENT),

  getAppTokenProxyStatus: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_PROXY_STATUS),

  getAppTokenHelp: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_HELP),

  

  // ADB工具API

  adbScan: () => getApiUrl(API_CONFIG.ENDPOINTS.ADB_SCAN),

  adbConnect: () => getApiUrl(API_CONFIG.ENDPOINTS.ADB_CONNECT),

  adbDisconnect: () => getApiUrl(API_CONFIG.ENDPOINTS.ADB_DISCONNECT),

  adbDevices: () => getApiUrl(API_CONFIG.ENDPOINTS.ADB_DEVICES),

  adbDeviceInfo: (serial) => getApiUrl(API_CONFIG.ENDPOINTS.ADB_DEVICE_INFO(serial)),

  adbCertStatus: () => getApiUrl(API_CONFIG.ENDPOINTS.ADB_CERT_STATUS),

  adbCertInstall: () => getApiUrl(API_CONFIG.ENDPOINTS.ADB_CERT_INSTALL),

  adbCertUninstall: () => getApiUrl(API_CONFIG.ENDPOINTS.ADB_CERT_UNINSTALL),

  adbCertInfo: () => getApiUrl(API_CONFIG.ENDPOINTS.ADB_CERT_INFO),

  adbShell: (serial) => getApiUrl(API_CONFIG.ENDPOINTS.ADB_SHELL(serial)),

  

  // 登录设置API

  loginSettings: () => getApiUrl(API_CONFIG.ENDPOINTS.LOGIN_SETTINGS),

  loginVerify: () => getApiUrl(API_CONFIG.ENDPOINTS.LOGIN_VERIFY),

  

  // CSQAQ API

  csqaqUploadMapping: () => getApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_UPLOAD_MAPPING),

  

  // 图片API

  weaponImage: (imageName) => getApiUrl(API_CONFIG.ENDPOINTS.WEAPON_IMAGE(imageName)),

  weaponImageCheck: (imageName) => getApiUrl(API_CONFIG.ENDPOINTS.WEAPON_IMAGE_CHECK(imageName)),

  

  // Home页面图表数据API（V2）

  homeInventoryAll: () => getApiUrl(API_CONFIG.ENDPOINTS.HOME_INVENTORY_ALL),

  homeComponentsAll: () => getApiUrl(API_CONFIG.ENDPOINTS.HOME_COMPONENTS_ALL),

  homeBuyAll: () => getApiUrl(API_CONFIG.ENDPOINTS.HOME_BUY_ALL),

  homeSellAll: () => getApiUrl(API_CONFIG.ENDPOINTS.HOME_SELL_ALL),

  // Home页面独立API（V2）

  homeBuyStats: () => getApiUrl(API_CONFIG.ENDPOINTS.HOME_BUY_STATS),

  homeSteamIds: () => getApiUrl(API_CONFIG.ENDPOINTS.HOME_STEAM_IDS),

  homeInventoryBySteamId: (steamId) => getApiUrl(API_CONFIG.ENDPOINTS.HOME_INVENTORY_BY_STEAM_ID(steamId)),

  homeComponentsBySteamId: (steamId) => getApiUrl(API_CONFIG.ENDPOINTS.HOME_COMPONENTS_BY_STEAM_ID(steamId)),

  homeSteamdtHomepageData: () => getApiUrl(API_CONFIG.ENDPOINTS.HOME_STEAMDT_HOMEPAGE_DATA),

  

  // 正在出售API

  getYYYPAccounts: () => getApiUrl(API_CONFIG.ENDPOINTS.ON_SALE_YYYP_ACCOUNTS),

  getBuffAccounts: () => getApiUrl(API_CONFIG.ENDPOINTS.ON_SALE_BUFF_ACCOUNTS),

  getOnSaleItems: () => getApiUrl(API_CONFIG.ENDPOINTS.ON_SALE_ITEMS),

  removeFromSale: () => getApiUrl(API_CONFIG.ENDPOINTS.ON_SALE_REMOVE),

  

  // 悠悠有品租赁API

  yyypGetLeaseList: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_LEASE_LIST),
  yyypGetSubleaseList: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_SUBLEASE_LIST),
  yyypGetPresaleList: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_PRESALE_LIST),
  yyypGetSellList: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_SELL_LIST),
  getRentedOutList: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_RENTED_OUT_LIST),
  yyypGetMySellOrders: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_MY_SELL_ORDERS),  // 获取我的出售订单
  yyypGetMyBuyOrders: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_MY_BUY_ORDERS),  // 获取我的收货订单
  yyypProcessOfferButton: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_PROCESS_OFFER_BUTTON),  // 处理报价按钮操作
  yyypGetPurchaseOrders: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_PURCHASE_ORDERS),  // 获取求购订单（求购中/暂停中）
  yyypGetPendingPaymentOrders: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_PENDING_PAYMENT_ORDERS),  // 获取待支付订单
  yyypPausePurchaseOrder: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_PAUSE_PURCHASE_ORDER),  // 暂停求购订单
  yyypOpenPurchaseOrder: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_OPEN_PURCHASE_ORDER),  // 开启暂停中的求购订单
  yyypDeletePurchaseOrder: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_DELETE_PURCHASE_ORDER),  // 删除求购订单
  yyypGetOrderInfo: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_ORDER_INFO),  // 获取订单详情
  yyypPreUpdateCheck: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_PRE_UPDATE_CHECK),  // 修改前置检查
  yyypEditPurchaseOrder: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_EDIT_PURCHASE_ORDER),  // 修改求购订单
  yyypQuickPriceIncrease: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_QUICK_PRICE_INCREASE),  // 一键加价预检查
  yyypConfirmPriceIncrease: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_CONFIRM_PRICE_INCREASE),  // 确认一键加价
  yyypGetPurchaseRecords: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_PURCHASE_RECORDS),  // 获取求购记录
  yyypSearchPurchaseTemplate: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_SEARCH_PURCHASE_TEMPLATE),  // 搜索求购饰品模板
  yyypGetTemplatePurchaseInfo: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_TEMPLATE_PURCHASE_INFO),  // 获取求购发布详情
  yyypPrePurchaseOrderCheck: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_PRE_PURCHASE_ORDER_CHECK),  // 求购预检查
  yyypSavePurchaseOrder: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_SAVE_PURCHASE_ORDER),  // 提交求购订单
  yyypGetPurchaseBalance: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_PURCHASE_BALANCE),  // 获取求购余额
  yyypQueryTransferInBalance: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_QUERY_TRANSFER_IN_BALANCE),  // 查询钱包可转入余额
  yyypConfirmTransferIn: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_CONFIRM_TRANSFER_IN),  // 确认从钱包转入
  yyypConfirmTransferOut: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_CONFIRM_TRANSFER_OUT),  // 确认转出到钱包
  yyypOffShelf: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_OFF_SHELF),
  yyypCancelSublease: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_CANCEL_SUBLEASE),
  yyypChangePrice: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_CHANGE_PRICE),  // 售卖商品改价
  yyypBatchChangePrice: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_BATCH_CHANGE_PRICE),  // 售卖商品批量改价
  yyypChangeRentPrice: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_CHANGE_RENT_PRICE),  // 租赁/转租改价（支持单个和批量）
  yyypGetInstantPaymentList: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_INSTANT_PAYMENT_LIST),  // 获取0CD订单列表
  yyypGetSubleaseAgreement: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_SUBLEASE_AGREEMENT),  // 获取转租协议
  yyypGetSubleaseDetail: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_SUBLEASE_DETAIL),  // 获取转租详情
  yyypRentInit: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_RENT_INIT),  // 获取出租初始化配置
  yyypGetCompensationText: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_COMPENSATION_TEXT),  // 获取赔付文本信息
  yyypGetPresaleDetail: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_PRESALE_DETAIL),  // 获取预售详情
  yyypBuyPresaleCommodity: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_BUY_PRESALE_COMMODITY),  // 购买预售商品
  yyypRentAutoPricing: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_RENT_AUTO_PRICING),

  // 悠悠有品消息盒子API（新API V2）
  yyypGetNewMessages: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_NEW_MESSAGES),  // 获取新消息（增量采集）
  yyypGetAllMessages: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_ALL_MESSAGES),  // 获取所有消息（全量采集）
  yyypMarkMessageRead: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_MARK_MESSAGE_READ),  // 标记消息为已读
  yyypDeleteMessage: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_DELETE_MESSAGE),  // 删除消息

  // 悠悠有品预售API（新API V2）
  yyypGetPresaleList: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_PRESALE_LIST),  // 获取预售列表

  // 悠悠有品过户API（新API V2）
  yyypGetTransferList: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_GET_TRANSFER_LIST),  // 获取过户列表

  // 悠悠有品转租API（新API V2）
  yyypChangeSubleasePrice: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_CHANGE_SUBLEASE_PRICE),  // 修改转租价格（0CD改价）
  yyypSubleaseAutoPricing: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_SUBLEASE_AUTO_PRICING),  // 转租商品自动定价
  yyypSubleaseGetCompensationText: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_SUBLEASE_GET_COMPENSATION_TEXT),  // 获取转租赔付文本信息
  yyypSubleaseGetBatchCompensationText: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_SUBLEASE_GET_BATCH_COMPENSATION_TEXT),  // 批量获取转租赔付文本信息

  // SteamDT API
  steamdtMarketIndex: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAMDT_MARKET_INDEX),
  steamdtMarketIndexHeadless: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAMDT_MARKET_INDEX_HEADLESS),
  steamdtKline: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAMDT_KLINE),
  steamdtHomepageData: () => getApiUrl(API_CONFIG.ENDPOINTS.STEAMDT_HOMEPAGE_DATA),



  // 版本更新API

  checkUpdate: () => getApiUrl(API_CONFIG.ENDPOINTS.UPDATE_CHECK),  // 检查更新

  getCurrentVersion: () => getApiUrl(API_CONFIG.ENDPOINTS.UPDATE_CURRENT_VERSION),  // 获取当前版本

  downloadUpdate: () => getApiUrl(API_CONFIG.ENDPOINTS.UPDATE_DOWNLOAD),  // 下载更新包

  checkLocalUpdate: () => getApiUrl(API_CONFIG.ENDPOINTS.UPDATE_CHECK_LOCAL),  // 检查本地更新包

  applyUpdate: () => getApiUrl(API_CONFIG.ENDPOINTS.UPDATE_APPLY),  // 执行更新

}

