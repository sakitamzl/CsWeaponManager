import { ref, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

export default {
  name: 'OfferProcessing',
  props: {
    steamId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const loading = ref(false)
    const sellOrders = ref([])
    const countdownTimers = ref(new Map())

    // 格式化倒计时显示
    const formatCountdown = (seconds) => {
      if (!seconds || seconds <= 0) return '已过期'
      
      const days = Math.floor(seconds / 86400)
      const hours = Math.floor((seconds % 86400) / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      
      if (days > 0) {
        return `${days}天 ${hours}小时 ${minutes}分钟`
      } else if (hours > 0) {
        return `${hours}小时 ${minutes}分钟 ${secs}秒`
      } else if (minutes > 0) {
        return `${minutes}分钟 ${secs}秒`
      } else {
        return `${secs}秒`
      }
    }

    // 启动倒计时
    const startCountdown = (item) => {
      if (!item.remaining_seconds) return
      
      // 清除旧的定时器
      if (countdownTimers.value.has(item.id)) {
        clearInterval(countdownTimers.value.get(item.id))
      }
      
      // 创建新的定时器
      const timer = setInterval(() => {
        const index = sellOrders.value.findIndex(i => i.id === item.id)
        if (index > -1 && sellOrders.value[index].remaining_seconds > 0) {
          sellOrders.value[index].remaining_seconds--
        } else {
          clearInterval(timer)
          countdownTimers.value.delete(item.id)
        }
      }, 1000)
      
      countdownTimers.value.set(item.id, timer)
    }

    // 停止倒计时
    const stopCountdown = (itemId) => {
      if (countdownTimers.value.has(itemId)) {
        clearInterval(countdownTimers.value.get(itemId))
        countdownTimers.value.delete(itemId)
      }
    }

    // 停止所有倒计时
    const stopAllCountdowns = () => {
      countdownTimers.value.forEach((timer) => {
        clearInterval(timer)
      })
      countdownTimers.value.clear()
    }

    // 加载报价订单数据
    const loadOfferOrders = async () => {
      if (!props.steamId) {
        ElMessage.warning('请选择账号')
        return
      }

      loading.value = true
      try {
        const response = await axios.post(apiUrls.yyypGetMySellOrders(), {
          steamId: props.steamId,
          code: '1',
          subCode: '1-4',  // 获取待确认报价
          whetherDark: true
        })

        if (response.data && response.data.success) {
          // 转换报价订单数据格式
          const orderData = response.data.data?.orders || []
          sellOrders.value = orderData.map(order => {
            return {
              id: order.offer_id,
              order_no: order.order_no,
              item_name: order.item_name,
              steam_hash_name: order.item_hash_name,
              weapon_type: order.item_type,
              float_range: order.exterior,
              platform: 'yyyp',
              trade_type: 'offer',
              // 报价特有字段
              offer_id: order.offer_id,
              offer_type: order.offer_type,
              order_status: order.order_status,
              countdown_desc: order.countdown_desc,
              countdown_timestamp: order.countdown_timestamp,
              current_time: order.current_time,
              surplus_countdown: order.surplus_countdown,
              remaining_seconds: order.remaining_seconds,  // 剩余秒数
              end_countdown_desc: order.end_countdown_desc,  // 截止时间描述
              buttons: order.buttons,
              icon_url: order.icon_url,
              rarity: order.rarity,
              rarity_color: order.rarity_color,
              exterior_color: order.exterior_color
            }
          })

          const totalCount = response.data.data?.total_count || 0
          ElMessage.success(`加载成功，共 ${totalCount} 个待确认报价`)
          
          // 为每个订单启动倒计时
          sellOrders.value.forEach(item => {
            if (item.remaining_seconds) {
              startCountdown(item)
            }
          })
        } else {
          ElMessage.error(response.data?.message || '加载失败')
        }
      } catch (error) {
        console.error('加载报价订单失败:', error)
        ElMessage.error('加载失败: ' + error.message)
      } finally {
        loading.value = false
      }
    }

    // 处理报价按钮操作
    const handleOfferButton = async (item, button) => {
      try {
        if (!props.steamId) {
          ElMessage.error('无法获取Steam ID')
          return
        }

        const response = await axios.post(apiUrls.yyypProcessOfferButton(), {
          steamId: props.steamId,
          action: button.action,
          offerId: button.offer_id,
          orderNo: button.order_no
        })

        if (response.data && response.data.success) {
          ElMessage.success(button.name + '成功')
          // 重新加载数据
          await loadOfferOrders()
        } else {
          ElMessage.error(response.data?.message || button.name + '失败')
        }
      } catch (error) {
        console.error('处理报价按钮失败:', error)
        ElMessage.error('操作失败: ' + error.message)
      }
    }

    // 监听 steamId 变化，重新加载数据
    watch(() => props.steamId, (newSteamId) => {
      if (newSteamId) {
        stopAllCountdowns()
        loadOfferOrders()
      }
    }, { immediate: true })

    // 组件卸载时清理定时器
    onUnmounted(() => {
      stopAllCountdowns()
    })

    return {
      loading,
      sellOrders,
      formatCountdown,
      handleOfferButton
    }
  }
}
