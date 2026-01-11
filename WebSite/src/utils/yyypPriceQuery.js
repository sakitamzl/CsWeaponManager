/**
 * 悠悠有品实时价格查询工具
 */
import axios from 'axios'
import { apiUrls } from '@/config/api'

/**
 * 实时查询悠悠有品在售底价
 * 
 * @param {string} yyypId - 悠悠有品模板ID
 * @param {string} steamId - Steam ID（可选）
 * @param {boolean} includeList - 是否包含商品列表（可选，默认false）
 * @returns {Promise<Object>} 查询结果
 * 
 * @example
 * const result = await getRealTimeLowestPrice('12345', '76561198XXXXXXXX')
 * console.log(result.data.lowest_price) // "150.50"
 * console.log(result.data.total_count)  // 123
 */
export async function getRealTimeLowestPrice(yyypId, steamId = '', includeList = false) {
  try {
    const response = await axios.post(apiUrls.youpinRealtimeLowestPrice(), {
      yyypId: yyypId,
      steamId: steamId,
      includeList: includeList
    })
    
    if (response.data.success) {
      return {
        success: true,
        data: response.data.data
      }
    } else {
      return {
        success: false,
        message: response.data.message || '查询失败'
      }
    }
  } catch (error) {
    console.error('查询悠悠在售底价失败:', error)
    return {
      success: false,
      message: error.response?.data?.message || error.message || '网络请求失败'
    }
  }
}

/**
 * 批量查询多个饰品的悠悠在售底价
 * 
 * @param {Array<string>} yyypIds - 悠悠有品模板ID数组
 * @param {string} steamId - Steam ID（可选）
 * @returns {Promise<Object>} 批量查询结果
 * 
 * @example
 * const results = await batchGetRealTimeLowestPrice(['12345', '67890'])
 * results.forEach(result => {
 *   console.log(`ID: ${result.yyyp_id}, 价格: ${result.lowest_price}`)
 * })
 */
export async function batchGetRealTimeLowestPrice(yyypIds, steamId = '') {
  const results = []
  
  for (const yyypId of yyypIds) {
    try {
      const result = await getRealTimeLowestPrice(yyypId, steamId, false)
      
      if (result.success) {
        results.push({
          yyyp_id: yyypId,
          ...result.data,
          success: true
        })
      } else {
        results.push({
          yyyp_id: yyypId,
          success: false,
          message: result.message
        })
      }
      
      // 添加延迟避免请求过快
      await new Promise(resolve => setTimeout(resolve, 500))
    } catch (error) {
      results.push({
        yyyp_id: yyypId,
        success: false,
        message: error.message
      })
    }
  }
  
  return results
}

export default {
  getRealTimeLowestPrice,
  batchGetRealTimeLowestPrice
}
