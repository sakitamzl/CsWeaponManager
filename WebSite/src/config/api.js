// API 配置文件
export const API_CONFIG = {
  // API 基础地址
  BASE_URL: '/api',
  
  // 爬虫服务器地址
  SPIDER_BASE_URL: 'http://127.0.0.1:9002',
  
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
    
    // 销售数据相关
    SELL_DATA: (page, limit) => `/webSellV1/getSellData/${page}/${limit}`,
    SELL_STATS: '/webSellV1/getSellStats',
    
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
    SEARCH_WEAPON_DETAIL: (keyword) => `/webSelectWeaponV1/searchWeaponDetail?keyword=${encodeURIComponent(keyword)}`,
    
    // 类型和磨损等级搜索相关
    BUY_WEAPON_TYPES: '/webBuyPageV1/getWeaponTypes',
    BUY_FLOAT_RANGES: '/webBuyPageV1/getFloatRanges',
    BUY_STATUS_LIST: '/webBuyPageV1/getStatusList',
    BUY_SEARCH_BY_TYPE_WEAR: '/webBuyPageV1/searchByTypeAndWear',
    BUY_STATS_BY_TYPE_WEAR: '/webBuyPageV1/getStatsByTypeAndWear',
    
    SELL_WEAPON_TYPES: '/webSellPageV1/getWeaponTypes',
    SELL_FLOAT_RANGES: '/webSellPageV1/getFloatRanges',
    SELL_STATUS_LIST: '/webSellPageV1/getStatusList',
    SELL_SEARCH_BY_TYPE_WEAR: '/webSellPageV1/searchByTypeAndWear',
    SELL_STATS_BY_TYPE_WEAR: '/webSellPageV1/getStatsByTypeAndWear',
    
    LENT_WEAPON_TYPES: '/webLentPageV1/getWeaponTypes',
    LENT_FLOAT_RANGES: '/webLentPageV1/getFloatRanges',
    LENT_STATUS_LIST: '/webLentPageV1/getStatusList',
    LENT_SEARCH_BY_TYPE_WEAR: '/webLentPageV1/searchByTypeAndWear',
    LENT_STATS_BY_TYPE_WEAR: '/webLentPageV1/getStatsByTypeAndWear',
    
    // 爬虫相关
    YOUPIN_SPIDER: '/youping898SpiderV1/newData',
    YOUPIN_FULL_SPIDER: '/youping898SpiderV1/NoneData',
    YOUPIN_SYNC_TEMPLATES: '/youping898SpiderV1/syncWeaponTemplates',  // 同步悠悠有品饰品映射
    BUFF_SPIDER: '/buffSpiderV1/NewData',
    BUFF_FULL_SPIDER: '/buffSpiderV1/allDate',
    BUFF_SYNC_TEMPLATES: '/buffSpiderV1/syncBuffTemplates',  // 同步BUFF饰品映射
    STEAM_SPIDER: '/steamSpiderV1/getNewData',  // Steam增量采集（获取新数据）
    STEAM_FULL_SPIDER: '/steamSpiderV1/NoneData',  // Steam全量采集
    STEAM_COLLECT_HASH_NAMES: '/steamSpiderV1/collectMarketHashNames',  // 采集Steam市场Hash Names
    CSQAQ_GET_GOODS: '/csqaqSpiderV1/getGoodsList',  // CSQAQ同步获取商品
    CSQAQ_GET_GOODS_ASYNC: '/csqaqSpiderV1/getGoodsListAsync',  // CSQAQ异步获取商品
    CSQAQ_TASK_STATUS: '/csqaqSpiderV1/getTaskStatus',  // CSQAQ获取任务状态
    CSQAQ_TASK_RESULT: '/csqaqSpiderV1/getTaskResult',  // CSQAQ获取任务结果
    CSQAQ_EXPORT: '/csqaqSpiderV1/exportGoods',  // CSQAQ导出商品
    AUTO_BUY_RENAMED_WEAPON: '/youping898SpiderV1/auto_buy_renamed_weapon',  // 自动购买改名饰品
    
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
    GET_APP_TOKEN_PROXY_STATUS: '/getAppTokenV1/proxy_status',  // 查询代理状态
    GET_APP_TOKEN_HELP: '/getAppTokenV1/help',  // 获取帮助信息
  }
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
  
  // 销售数据
  sellData: (page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.SELL_DATA(page, limit)),
  sellStats: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_STATS),
  
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
  buySearchByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_SEARCH_BY_TYPE_WEAR),
  buyStatsByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_STATS_BY_TYPE_WEAR),
  
  sellWeaponTypes: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_WEAPON_TYPES),
  sellFloatRanges: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_FLOAT_RANGES),
  sellStatusList: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_STATUS_LIST),
  sellSearchByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_SEARCH_BY_TYPE_WEAR),
  sellStatsByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_STATS_BY_TYPE_WEAR),
  
  lentWeaponTypes: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_WEAPON_TYPES),
  lentFloatRanges: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_FLOAT_RANGES),
  lentStatusList: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_STATUS_LIST),
  lentSearchByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_SEARCH_BY_TYPE_WEAR),
  lentStatsByTypeWear: () => getApiUrl(API_CONFIG.ENDPOINTS.LENT_STATS_BY_TYPE_WEAR),
  
  // 武器搜索
  searchWeapon: (keyword) => getApiUrl(API_CONFIG.ENDPOINTS.SEARCH_WEAPON(keyword)),
  searchWeaponDetail: (keyword) => getApiUrl(API_CONFIG.ENDPOINTS.SEARCH_WEAPON_DETAIL(keyword)),
  
  // 爬虫API
  youpinSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_SPIDER),
  youpinFullSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_FULL_SPIDER),
  youpinSyncTemplates: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_SYNC_TEMPLATES),
  buffSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_SPIDER),
  buffFullSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_FULL_SPIDER),
  buffSyncTemplates: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.BUFF_SYNC_TEMPLATES),
  steamSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_SPIDER),
  steamFullSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_FULL_SPIDER),
  steamCollectHashNames: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.STEAM_COLLECT_HASH_NAMES),
  csqaqGetGoods: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_GET_GOODS),
  csqaqGetGoodsAsync: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_GET_GOODS_ASYNC),
  csqaqTaskStatus: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_TASK_STATUS),
  csqaqTaskResult: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_TASK_RESULT),
  csqaqExport: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.CSQAQ_EXPORT),
  autoBuyRenamedWeapon: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.AUTO_BUY_RENAMED_WEAPON),
  
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
  getAppTokenProxyStatus: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_PROXY_STATUS),
  getAppTokenHelp: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.GET_APP_TOKEN_HELP),
}
