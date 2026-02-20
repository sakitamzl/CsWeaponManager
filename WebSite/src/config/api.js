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

    

    // 购买数据相关

    BUY_DATA: (page, limit) => `/webBuyV1/getBuyData/${page}/${limit}`,

    BUY_STATS: '/webBuyV1/getBuyStats',

    BUY_SOURCE_LIST: '/webBuyV1/getSourceList',

    BUY_DATA_BY_SOURCE: (source, page, limit) => `/webBuyV1/getBuyDataBySource/${encodeURIComponent(source)}/${page}/${limit}`,

    BUY_STATS_BY_SOURCE: (source) => `/webBuyV1/getBuyStatsBySource/${encodeURIComponent(source)}`,

    BUY_DATA_USER_LIST: '/webBuyV1/getDataUserList',

    BUY_DATA_BY_USER: (user, page, limit) => `/webBuyV1/getBuyDataByDataUser/${encodeURIComponent(user)}/${page}/${limit}`,

    BUY_STATS_BY_USER: (user) => `/webBuyV1/getBuyStatsByDataUser/${encodeURIComponent(user)}`,

    

    // 销售数据相关

    SELL_DATA: (page, limit) => `/webSellV1/getSellData/${page}/${limit}`,

    SELL_STATS: '/webSellV1/getSellStats',

    SELL_SOURCE_LIST: '/webSellV1/getSourceList',

    SELL_DATA_BY_SOURCE: (source, page, limit) => `/webSellV1/getSellDataBySource/${encodeURIComponent(source)}/${page}/${limit}`,

    SELL_STATS_BY_SOURCE: (source) => `/webSellV1/getSellStatsBySource/${encodeURIComponent(source)}`,

    BUY_STATS_FILTERED: '/webBuyV1/getBuyStatsFiltered',

    BUY_DATA_FILTERED: '/webBuyV1/getBuyDataFiltered',

    SELL_STATS_FILTERED: '/webSellV1/getSellStatsFiltered',

    SELL_DATA_FILTERED: '/webSellV1/getSellDataFiltered',

    LENT_STATS_FILTERED: '/webLentPageV1/getLentStatsFiltered',

    LENT_DATA_FILTERED: '/webLentPageV1/getLentDataFiltered',

    SELL_DATA_USER_LIST: '/webSellV1/getDataUserList',

    

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

    BUY_WEAPON_TYPES: '/webBuyPageV1/getWeaponTypes',

    BUY_FLOAT_RANGES: '/webBuyPageV1/getFloatRanges',

    BUY_STATUS_LIST: '/webBuyPageV1/getStatusList',

    BUY_STATUS_SUB_LIST: (status) => `/webBuyPageV1/getStatusSubList?status=${encodeURIComponent(status)}`,

    BUY_SEARCH_BY_TYPE_WEAR: '/webBuyPageV1/searchByTypeAndWear',

    BUY_STATS_BY_TYPE_WEAR: '/webBuyPageV1/getStatsByTypeAndWear',

    BUY_YYYP_PRICE_INFO: (steamHashName) => `/webBuyV1/getYyypPriceInfo/${encodeURIComponent(steamHashName)}`,



    SELL_WEAPON_TYPES: '/webSellPageV1/getWeaponTypes',

    SELL_FLOAT_RANGES: '/webSellPageV1/getFloatRanges',

    SELL_STATUS_LIST: '/webSellPageV1/getStatusList',

    SELL_STATUS_SUB_LIST: (status) => `/webSellPageV1/getStatusSubList?status=${encodeURIComponent(status)}`,

    SELL_SEARCH_BY_TYPE_WEAR: '/webSellPageV1/searchByTypeAndWear',

    SELL_STATS_BY_TYPE_WEAR: '/webSellPageV1/getStatsByTypeAndWear',

    

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

    AES_DECRYPT: '/spiderApiV2/youping/units/settings/dev_tools/aesDecrypt',

    AES_CHECK_LICENSE: '/spiderApiV2/youping/units/settings/dev_tools/aesCheckLicense',

    AES_HEALTH: '/spiderApiV2/youping/units/settings/dev_tools/aesHealth',

    // AES工具相关（V1 API - 已废弃，保留向后兼容）

    AES_DECRYPT_V1: '/aesToolsV1/decrypt',

    AES_CHECK_LICENSE_V1: '/aesToolsV1/check-license',

    AES_HEALTH_V1: '/aesToolsV1/health',



    // 爬虫相关

    // 悠悠有品数据同步（V2 API）
    YOUPIN_SYNC_NEW_DATA: '/spiderApiV2/youping/units/settings/data_source/syncNewData',  // 同步新增数据
    YOUPIN_SYNC_HISTORY_DATA: '/spiderApiV2/youping/units/settings/data_source/syncHistoryData',  // 同步历史数据
    YOUPIN_SYNC_WEAPON_PRICE: '/spiderApiV2/youping/units/settings/dev_tools/syncWeaponPrice',  // 同步价格数据
    YOUPIN_SYNC_WEAPON_TEMPLATES: '/spiderApiV2/youping/units/settings/dev_tools/syncWeaponTemplates',  // 同步武器模板

    YOUPIN_FETCH_ICONS: '/youpin898SelectWeaponV1/fetchWeaponIcons',   // 批量获取饰品图片

    YOUPIN_DOWNLOAD_ICONS: '/spiderApiV2/youping/units/settings/dev_tools/downloadWeaponIcons',   // 下载武器图标资源

    BUFF_SPIDER: '/buffSpiderV1/NewData',

    BUFF_FULL_SPIDER: '/buffSpiderV1/allDate',

    BUFF_SYNC_TEMPLATES: '/buffSpiderV1/syncBuffTemplates',  // 同步BUFF饰品映射

    CSFLOAT_SPIDER: '/csfloatSpiderV1/NewData',

    CSFLOAT_FULL_SPIDER: '/csfloatSpiderV1/NoneData',

    STEAM_SPIDER: '/steamSpiderV1/getNewData',  // Steam增量采集（获取新数据）

    STEAM_FULL_SPIDER: '/steamSpiderV1/NoneData',  // Steam全量采集

    STEAM_COLLECT_HASH_NAMES: '/steamSpiderV1/collectMarketHashNames',  // 采集Steam市场Hash Names

    STEAM_FETCH_HASH_NAMES: '/steamSpiderV1/fetchSteamHashNames',  // 获取Steam饰品哈希（批量）

    STEAM_FETCH_HASH_NAMES_BY_WEAPON: '/steamSpiderV1/fetchSteamHashNamesByWeapon',  // 获取Steam饰品哈希（单个武器）

    STEAM_SEARCH_RENAME: '/steamSpiderV1/searchRenameWeapon',  // Steam 改名饰品搜索

    STEAM_BUY_MARKET_ITEM: '/steamSpiderV1/buyMarketItem',  // Steam 市场购买物品

    CSQAQ_MARKET_INDEX: '/csqaqSpiderV1/getMarketIndex',  // CSQAQ市场指数

    CSQAQ_GET_GOODS: '/csqaqSpiderV1/getGoodsList',  // CSQAQ同步获取商品

    CSQAQ_GET_GOODS_ASYNC: '/csqaqSpiderV1/getGoodsListAsync',  // CSQAQ异步获取商品

    CSQAQ_TASK_STATUS: '/csqaqSpiderV1/getTaskStatus',  // CSQAQ获取任务状态

    // 悠悠有品求购供应

    // 悠悠有品商品搜索 - 求购供应相关（新API V2）
    YOUPIN_GET_SUPPLY_LIST: '/spiderApiV2/youping/units/item_search/purchase_order/supply/getSupplyList',  // 获取可供应的库存列表
    YOUPIN_SUBMIT_SUPPLY: '/spiderApiV2/youping/units/item_search/purchase_order/supply/submitSupply',  // 提交供应（查询手续费）
    YOUPIN_CONFIRM_SUPPLY: '/spiderApiV2/youping/units/item_search/purchase_order/supply/confirmSupply',  // 确认供应
    YOUPIN_SEND_OFFER: '/spiderApiV2/youping/units/item_search/purchase_order/supply/sendOffer',  // 发送报价

    // 悠悠有品商品搜索 - ItemSearch页面相关（新API V2，按商品类型组织）
    YYYP_ITEM_SEARCH_ON_SALE_LIST: '/spiderApiV2/youping/units/item_search/on_sale/getCommodityList',  // 在售商品列表
    YYYP_ITEM_SEARCH_ON_SALE_DETAIL: '/spiderApiV2/youping/units/item_search/on_sale/getWeaponDetail',  // 在售商品详情
    YYYP_ITEM_SEARCH_BUY_COMMODITY: '/spiderApiV2/youping/units/item_search/on_sale/buyCommodity',  // 购买在售商品

    YYYP_ITEM_SEARCH_ON_LEASE_LIST: '/spiderApiV2/youping/units/item_search/on_lease/getCommodityList',  // 在租商品列表

    YYYP_ITEM_SEARCH_PRESALE_LIST: '/spiderApiV2/youping/units/item_search/presale/getCommodityList',  // 预售商品列表
    YYYP_ITEM_SEARCH_PRESALE_DETAIL: '/spiderApiV2/youping/units/item_search/presale/getPresaleDetail',  // 预售详情
    YYYP_ITEM_SEARCH_BUY_PRESALE: '/spiderApiV2/youping/units/item_search/presale/buyPresaleCommodity',  // 购买预售商品

    YYYP_ITEM_SEARCH_PURCHASE_ORDER_LIST: '/spiderApiV2/youping/units/item_search/purchase_order/getCommodityList',  // 求购订单列表

    YYYP_ITEM_SEARCH_PRICE_TREND: '/spiderApiV2/youping/units/item_search/price_trend/getPriceTrend',  // 价格走势

    YOUPIN_SELL_INVENTORY_ITEM: '/spiderApiV2/youping/units/inventory/sell/sellInventoryItem',  // 上架单个库存饰品（新版API）

    CSQAQ_TASK_RESULT: '/csqaqSpiderV1/getTaskResult',  // CSQAQ获取任务结果

    CSQAQ_EXPORT: '/csqaqSpiderV1/exportGoods',  // CSQAQ导出商品

    // SteamDT相关
    STEAMDT_MARKET_INDEX: '/steamdtSpiderV1/getMarketIndex',  // 获取SteamDT大盘指数
    STEAMDT_HOMEPAGE_DATA: '/steamdtApiV1/api/steamdt/homepage-data',  // 获取SteamDT首页数据（饰品成交额等）



    // Steam登录相关

    STEAM_LOGIN: '/steamLoginV1/login',

    STEAM_LOGIN_VERIFY: '/steamLoginV1/verify',

    STEAM_LOGIN_REFRESH: '/steamLoginV1/refresh',

    STEAM_LOGIN_CAPTCHA: (captchaGid) => `/steamLoginV1/captcha/${captchaGid}`,

    STEAM_LOGIN_GENERATE_CODE: '/steamLoginV1/generate_code',

    STEAM_QR_GENERATE: '/steamLoginV1/qrcode/generate',

    STEAM_QR_POLL: '/steamLoginV1/qrcode/poll',

    

    // GetAppToken 相关接口

    GET_APP_TOKEN_START_BUFF: '/getAppTokenV1/start_buff_proxy',  // 启动BUFF代理

    GET_APP_TOKEN_STOP_BUFF: '/getAppTokenV1/stop_buff_proxy',  // 停止BUFF代理

    GET_APP_TOKEN_GET_BUFF_DATA: '/getAppTokenV1/get_buff_data',  // 获取BUFF数据

    GET_APP_TOKEN_CLEAR_BUFF_DATA: '/getAppTokenV1/clear_buff_data',  // 清除BUFF数据

    GET_APP_TOKEN_START_YYYP: '/getAppTokenV1/start_yyyp_proxy',  // 启动悠悠有品代理

    GET_APP_TOKEN_STOP_YYYP: '/getAppTokenV1/stop_yyyp_proxy',  // 停止悠悠有品代理

    GET_APP_TOKEN_GET_YYYP_DATA: '/getAppTokenV1/get_yyyp_data',  // 获取悠悠有品数据

    GET_APP_TOKEN_CLEAR_YYYP_DATA: '/getAppTokenV1/clear_yyyp_data',  // 清除悠悠有品数据

    GET_APP_TOKEN_START_PERFECTWORLD: '/getAppTokenV1/start_perfectworld_proxy',  // 启动完美世界APP代理

    GET_APP_TOKEN_STOP_PERFECTWORLD: '/getAppTokenV1/stop_perfectworld_proxy',  // 停止完美世界APP代理

    GET_APP_TOKEN_GET_PERFECTWORLD_DATA: '/getAppTokenV1/get_perfectworld_data',  // 获取完美世界APP数据

    GET_APP_TOKEN_CLEAR_PERFECTWORLD_DATA: '/getAppTokenV1/clear_perfectworld_data',  // 清除完美世界APP数据

    GET_APP_TOKEN_START_CSFLOAT: '/getAppTokenV1/start_csfloat_proxy',  // 启动CsFloat代理

    GET_APP_TOKEN_STOP_CSFLOAT: '/getAppTokenV1/stop_csfloat_proxy',  // 停止CsFloat代理

    GET_APP_TOKEN_GET_CSFLOAT_DATA: '/getAppTokenV1/get_csfloat_data',  // 获取CsFloat数据

    GET_APP_TOKEN_CLEAR_CSFLOAT_DATA: '/getAppTokenV1/clear_csfloat_data',  // 清除CsFloat数据

    GET_APP_TOKEN_PROXY_STATUS: '/getAppTokenV1/proxy_status',  // 查询代理状态

    GET_APP_TOKEN_HELP: '/getAppTokenV1/help',  // 获取帮助信息

    

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

    

    // Home页面图表数据相关

    HOME_INVENTORY_ALL: '/webHomeChartsV1/inventory/all',  // 获取所有库存数据

    HOME_COMPONENTS_ALL: '/webHomeChartsV1/components/all',  // 获取所有库存组件数据

    HOME_BUY_ALL: '/webHomeChartsV1/buy/all',  // 获取所有购入数据

    HOME_SELL_ALL: '/webHomeChartsV1/sell/all',  // 获取所有出售数据

    

    // 正在出售相关

    ON_SALE_YYYP_ACCOUNTS: '/webOnSaleV1/getYYYPAccounts',  // 获取悠悠有品账号列表

    ON_SALE_BUFF_ACCOUNTS: '/webOnSaleV1/getBuffAccounts',  // 获取BUFF账号列表

    ON_SALE_ITEMS: '/webOnSaleV1/getOnSaleItems',  // 获取在售商品列表

    ON_SALE_REMOVE: '/webOnSaleV1/removeFromSale',  // 下架商品

    

    // 悠悠有品租赁相关

    YYYP_GET_LEASE_LIST: '/spiderApiV2/youping/units/on_sale/lent/getLeaseList',  // 获取租赁列表（新API）
    YYYP_GET_SUBLEASE_LIST: '/spiderApiV2/youping/units/on_sale/sublease/getSubleaseList',  // 获取转租列表（新API）
    YYYP_GET_SELL_LIST: '/spiderApiV2/youping/units/on_sale/sell/getSellList',  // 获取出售列表（新API）
    YYYP_GET_RENTED_OUT_LIST: '/spiderApiV2/youping/units/on_sale/rented_out/getRentedOutList',  // 获取已租出列表（新API）
    YYYP_GET_MY_SELL_ORDERS: '/spiderApiV2/youping/units/on_sale/offer_handling/getMySellOrders',  // 获取我的出售订单（报价处理，新API）
    YYYP_GET_MY_BUY_ORDERS: '/spiderApiV2/youping/units/on_sale/offer_handling/getMyBuyOrders',  // 获取我的收货订单（报价处理，新API）
    YYYP_PROCESS_OFFER_BUTTON: '/spiderApiV2/youping/units/on_sale/offer_handling/processOfferButton',  // 处理报价按钮操作（新API）
    YYYP_GET_PURCHASE_ORDERS: '/spiderApiV2/youping/units/on_sale/purchase_request/getPurchaseOrders',  // 获取求购订单（求购中/暂停中，新API）
    YYYP_GET_PENDING_PAYMENT_ORDERS: '/spiderApiV2/youping/units/on_sale/purchase_request/getPendingPaymentOrders',  // 获取待支付订单（新API）
    YYYP_PAUSE_PURCHASE_ORDER: '/spiderApiV2/youping/units/on_sale/purchase_request/purchasing/pauseOrder',  // 暂停求购订单（新API）
    YYYP_RESUME_PURCHASE_ORDER: '/spiderApiV2/youping/units/on_sale/purchase_request/purchasing/resumeOrder',  // 恢复求购订单（新API）
    YYYP_DELETE_PURCHASE_ORDER: '/spiderApiV2/youping/units/on_sale/purchase_request/purchasing/deleteOrder',  // 删除求购订单（新API）
    YYYP_EDIT_PURCHASE_ORDER: '/spiderApiV2/youping/units/on_sale/purchase_request/purchasing/editOrder',  // 修改求购订单（新API）
    YYYP_QUICK_PRICE_INCREASE: '/spiderApiV2/youping/units/on_sale/purchase_request/purchasing/quickIncrease',  // 一键加价预检查（新API）
    YYYP_CONFIRM_PRICE_INCREASE: '/spiderApiV2/youping/units/on_sale/purchase_request/purchasing/confirmQuickIncrease',  // 确认一键加价（新API）
    YYYP_OFF_SHELF: '/spiderApiV2/youping/units/on_sale/sell/offShelf',  // 下架商品（新API）
    YYYP_CANCEL_SUBLEASE: '/spiderApiV2/youping/units/on_sale/sublease/cancelSublease',  // 取消转租（新API）
    YYYP_CHANGE_PRICE: '/spiderApiV2/youping/units/on_sale/sell/changePrice',  // 改价（售卖商品，新API）
    YYYP_BATCH_CHANGE_PRICE: '/spiderApiV2/youping/units/on_sale/sell/batchChangePrice',  // 批量改价（售卖商品，新API）
    YYYP_CHANGE_RENT_PRICE: '/spiderApiV2/youping/units/on_sale/lent/changePrice',  // 改价（租赁/转租，支持单个和批量，新API）
    YYYP_GET_INSTANT_PAYMENT_LIST: '/spiderApiV2/youping/units/on_sale/instant/getInstantPaymentList',  // 获取0CD(秒到账)订单列表（新API）
    YYYP_GET_SUBLEASE_AGREEMENT: '/spiderApiV2/youping/units/on_sale/sublease/getSubleaseAgreement',  // 获取转租协议（新API）
    YYYP_GET_SUBLEASE_DETAIL: '/spiderApiV2/youping/units/on_sale/sublease/getSubleaseDetail',  // 获取转租详情（新API）
    YYYP_RENT_INIT: '/spiderApiV2/youping/units/on_sale/lent/rentInit',  // 获取出租初始化配置（新API）
    YYYP_GET_COMPENSATION_TEXT: '/spiderApiV2/youping/units/on_sale/lent/getCompensationText',  // 获取赔付文本信息（新API）

    // 悠悠有品消息盒子相关（新API V2）
    YYYP_GET_NEW_MESSAGES: '/spiderApiV2/youping/units/settings/yyyp_message_box/getNewMessages',  // 获取新消息（增量采集）
    YYYP_GET_ALL_MESSAGES: '/spiderApiV2/youping/units/settings/yyyp_message_box/getAllMessages',  // 获取所有消息（全量采集）
    YYYP_MARK_MESSAGE_READ: '/spiderApiV2/youping/units/settings/yyyp_message_box/markMessageRead',  // 标记消息为已读
    YYYP_DELETE_MESSAGE: '/spiderApiV2/youping/units/settings/yyyp_message_box/deleteMessage',  // 删除消息

    // 悠悠有品预售相关（新API V2）
    YYYP_GET_PRESALE_LIST: '/spiderApiV2/youping/units/on_sale/presale/getPresaleList',  // 获取预售列表
    YYYP_GET_PRESALE_DETAIL: '/spiderApiV2/youping/units/item_search/presale/getPresaleDetail',  // 获取预售详情
    YYYP_BUY_PRESALE_COMMODITY: '/spiderApiV2/youping/units/item_search/presale/buyPresaleCommodity',  // 购买预售商品

    // 悠悠有品过户相关（新API V2）
    YYYP_GET_TRANSFER_LIST: '/spiderApiV2/youping/units/on_sale/transfer/getTransferList',  // 获取过户列表

    // 悠悠有品转租相关（新API V2）
    YYYP_CHANGE_SUBLEASE_PRICE: '/spiderApiV2/youping/units/on_sale/sublease/changeSubleasePrice',  // 修改转租价格（0CD改价）
    YYYP_SUBLEASE_AUTO_PRICING: '/spiderApiV2/youping/units/on_sale/sublease/autoPricing',  // 转租商品自动定价
    YYYP_SUBLEASE_GET_COMPENSATION_TEXT: '/spiderApiV2/youping/units/on_sale/sublease/getCompensationText',  // 获取转租赔付文本信息
    YYYP_SUBLEASE_GET_BATCH_COMPENSATION_TEXT: '/spiderApiV2/youping/units/on_sale/sublease/getBatchCompensationText',  // 批量获取转租赔付文本信息

    // 悠悠有品出租自动定价（爬虫端）
    YYYP_RENT_AUTO_PRICING: '/spiderApiV2/youping/units/on_sale/lent/autoPricing',

    

    // 登录设置相关

    LOGIN_SETTINGS: '/loginSettingsV1/api/login-settings',  // 获取/保存登录设置

    LOGIN_VERIFY: '/loginSettingsV1/api/login-settings/verify',  // 验证登录



    // 版本更新相关

    UPDATE_CHECK: '/api/update/check',  // 检查更新

    UPDATE_CURRENT_VERSION: '/api/update/current-version',  // 获取当前版本

    UPDATE_DOWNLOAD: '/api/update/download',  // 下载更新包

    UPDATE_EXTRACT: '/api/update/extract',  // 解压更新包

    // 悠悠有品自动购买相关（V2 API）
    AUTO_BUY_RENAMED_WEAPON: '/spiderApiV2/youping/auto_weapon/autoBuyRenamedWeapon',  // 自动购买改名武器
    AUTO_BUY_PENDANT_WEAPON: '/spiderApiV2/youping/auto_weapon/autoBuyPendantWeapon',  // 自动购买挂件武器
    STOP_PENDANT_SEARCH: '/spiderApiV2/youping/auto_weapon/stopPendantSearch',  // 停止挂件搜索
    GET_PENDANT_SEARCH_PROGRESS: '/spiderApiV2/youping/auto_weapon/getPendantSearchProgress',  // 获取挂件搜索进度
    REALTIME_LOWEST_PRICE: '/spiderApiV2/youping/auto_weapon/getRealTimeLowestPrice',  // 实时查询悠悠在售底价

  },

  // 悠悠有品自动购买相关（V2 API） - 顶层配置（向后兼容）
  YOUPIN_AUTO_BUY_RENAMED_WEAPON: '/spiderApiV2/youping/auto_weapon/autoBuyRenamedWeapon',  // 自动购买改名武器
  YOUPIN_AUTO_BUY_PENDANT_WEAPON: '/spiderApiV2/youping/auto_weapon/autoBuyPendantWeapon',  // 自动购买挂件武器
  YOUPIN_STOP_PENDANT_SEARCH: '/spiderApiV2/youping/auto_weapon/stopPendantSearch',  // 停止挂件搜索
  YOUPIN_GET_PENDANT_SEARCH_PROGRESS: '/spiderApiV2/youping/auto_weapon/getPendantSearchProgress',  // 获取挂件搜索进度
  YOUPIN_REALTIME_LOWEST_PRICE: '/spiderApiV2/youping/auto_weapon/getRealTimeLowestPrice',  // 实时查询悠悠在售底价

  // 悠悠有品库存租借相关（V2 API） - 顶层配置（向后兼容）
  YOUPIN_GET_INVENTORY_EXTEND_INFO: '/spiderApiV2/youping/units/inventory/lent/getInventoryExtendInfo',  // 获取库存扩展信息
  YOUPIN_UPLOAD_RENT: '/spiderApiV2/youping/units/inventory/lent/uploadRent'  // 上传租借饰品

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

  

  // 购买数据

  buyData: (page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.BUY_DATA(page, limit)),

  buyStats: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_STATS),

  buySourceList: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_SOURCE_LIST),

  buyDataBySource: (source, page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.BUY_DATA_BY_SOURCE(source, page, limit)),

  buyStatsBySource: (source) => getApiUrl(API_CONFIG.ENDPOINTS.BUY_STATS_BY_SOURCE(source)),

  buyStatsFiltered: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_STATS_FILTERED),

  buyDataFiltered: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_DATA_FILTERED),

  buyDataUserList: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_DATA_USER_LIST),

  

  // 销售数据

  sellData: (page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.SELL_DATA(page, limit)),

  sellStats: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_STATS),

  sellDataUserList: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_DATA_USER_LIST),

  sellDataBySource: (source, page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.SELL_DATA_BY_SOURCE(source, page, limit)),

  sellStatsFiltered: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_STATS_FILTERED),

  sellDataFiltered: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_DATA_FILTERED),

  

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
  buffSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_SPIDER),

  buffFullSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_FULL_SPIDER),

  buffSyncTemplates: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_SYNC_TEMPLATES),

  steamSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_SPIDER),

  steamFullSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_FULL_SPIDER),

  steamCollectHashNames: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_COLLECT_HASH_NAMES),

  steamFetchHashNames: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_FETCH_HASH_NAMES),

  steamFetchHashNamesByWeapon: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_FETCH_HASH_NAMES_BY_WEAPON),

  csqaqMarketIndex: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_MARKET_INDEX),

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

  csfloatSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSFLOAT_SPIDER),

  csfloatFullSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSFLOAT_FULL_SPIDER),

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

  

  // Home页面图表数据API

  homeInventoryAll: () => getApiUrl(API_CONFIG.ENDPOINTS.HOME_INVENTORY_ALL),

  homeComponentsAll: () => getApiUrl(API_CONFIG.ENDPOINTS.HOME_COMPONENTS_ALL),

  homeBuyAll: () => getApiUrl(API_CONFIG.ENDPOINTS.HOME_BUY_ALL),

  homeSellAll: () => getApiUrl(API_CONFIG.ENDPOINTS.HOME_SELL_ALL),

  

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
  yyypResumePurchaseOrder: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_RESUME_PURCHASE_ORDER),  // 恢复求购订单
  yyypDeletePurchaseOrder: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_DELETE_PURCHASE_ORDER),  // 删除求购订单
  yyypEditPurchaseOrder: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_EDIT_PURCHASE_ORDER),  // 修改求购订单
  yyypQuickPriceIncrease: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_QUICK_PRICE_INCREASE),  // 一键加价预检查
  yyypConfirmPriceIncrease: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YYYP_CONFIRM_PRICE_INCREASE),  // 确认一键加价
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
  steamdtHomepageData: () => getApiUrl(API_CONFIG.ENDPOINTS.STEAMDT_HOMEPAGE_DATA),



  // 版本更新API

  checkUpdate: () => getApiUrl(API_CONFIG.ENDPOINTS.UPDATE_CHECK),  // 检查更新

  getCurrentVersion: () => getApiUrl(API_CONFIG.ENDPOINTS.UPDATE_CURRENT_VERSION),  // 获取当前版本

  downloadUpdate: () => getApiUrl(API_CONFIG.ENDPOINTS.UPDATE_DOWNLOAD),  // 下载更新包

  extractUpdate: () => getApiUrl(API_CONFIG.ENDPOINTS.UPDATE_EXTRACT),  // 解压更新包

}

