// API 配置文件
export const API_CONFIG = {
  // API 基础地址
  BASE_URL: 'http://localhost:9001',
  
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
    
    // 爬虫相关
    YOUPIN_SPIDER: '/youping898SpiderV1/allDate',
    YOUPIN_FULL_SPIDER: '/youping898SpiderV1/NoneData'
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
  
  // 购买数据
  buyData: (page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.BUY_DATA(page, limit)),
  buyStats: () => getApiUrl(API_CONFIG.ENDPOINTS.BUY_STATS),
  
  // 销售数据
  sellData: (page, limit) => getApiUrl(API_CONFIG.ENDPOINTS.SELL_DATA(page, limit)),
  sellStats: () => getApiUrl(API_CONFIG.ENDPOINTS.SELL_STATS),
  
  // 爬虫API
  youpinSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_SPIDER),
  youpinFullSpider: () => getSpiderApiUrl(API_CONFIG.ENDPOINTS.YOUPIN_FULL_SPIDER)
}