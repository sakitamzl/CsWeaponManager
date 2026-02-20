import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

export default {
  name: 'MyPurchaseRequest',
  props: {
    steamId: {
      type: String,
      default: ''
    }
  },
  emits: ['update:count'],
  setup(props, { emit }) {
    const loading = ref(false)

    // 子标签页
    const subTabs = ref([
      { value: 'purchasing', label: '求购中' },
      { value: 'paused', label: '暂停中' },
      { value: 'pending_payment', label: '待支付' }
    ])
    const activeSubTab = ref('purchasing')

    // 数据
    const purchasingItems = ref([])  // 求购中
    const pausedItems = ref([])      // 暂停中
    const pendingPaymentItems = ref([])  // 待支付
    const historyItems = ref([])     // 求购记录
    const historyFilter = ref('all') // 历史筛选

    // 修改求购对话框相关状态
    const editDialogVisible = ref(false)
    const currentEditOrderNo = ref('')
    const editOrderData = ref(null)

    // 倒计时定时器
    let countdownTimer = null

    // 计算属性 - 正在求购的所有物品（用于批量处理按钮显示）
    const activePurchaseRequests = computed(() => {
      return [...purchasingItems.value, ...pausedItems.value, ...pendingPaymentItems.value]
    })

    // 计算属性 - 筛选后的历史记录
    const filteredHistoryItems = computed(() => {
      if (historyFilter.value === 'all') {
        return historyItems.value
      }
      return historyItems.value.filter(item => item.status === historyFilter.value)
    })

    // 获取子标签计数
    const getSubTabCount = (tabValue) => {
      switch (tabValue) {
        case 'purchasing':
          return purchasingItems.value.length
        case 'paused':
          return pausedItems.value.length
        case 'pending_payment':
          return pendingPaymentItems.value.length
        default:
          return 0
      }
    }

    // 格式化倒计时
    const formatCountdown = (seconds) => {
      if (seconds <= 0) return '已超时'

      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60

      if (hours > 0) {
        return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
      }
      return `${minutes}:${String(secs).padStart(2, '0')}`
    }

    // 更新倒计时
    const updateCountdowns = () => {
      pendingPaymentItems.value.forEach(item => {
        if (item.remaining_seconds > 0) {
          item.remaining_seconds--
        }
      })
    }

    // 加载求购中订单
    const loadPurchasingOrders = async () => {
      if (!props.steamId) {
        return { success: true, count: 0 }
      }

      try {
        const response = await axios.post(apiUrls.yyypGetPurchaseOrders(), {
          steamId: props.steamId,
          status: 20  // 20 = 求购中
        })

        if (response.data && response.data.code === 200) {
          purchasingItems.value = response.data.data?.orders || []
          return { success: true, count: purchasingItems.value.length }
        } else {
          console.error('加载求购中订单失败:', response.data?.message)
          return { success: false, error: response.data?.message || '未知错误' }
        }
      } catch (error) {
        console.error('加载求购中订单异常:', error)
        return { success: false, error: error.message }
      }
    }

    // 加载暂停中订单
    const loadPausedOrders = async () => {
      if (!props.steamId) {
        return { success: true, count: 0 }
      }

      try {
        const response = await axios.post(apiUrls.yyypGetPurchaseOrders(), {
          steamId: props.steamId,
          status: 30  // 30 = 暂停中
        })

        if (response.data && response.data.code === 200) {
          pausedItems.value = response.data.data?.orders || []
          return { success: true, count: pausedItems.value.length }
        } else {
          console.error('加载暂停中订单失败:', response.data?.message)
          return { success: false, error: response.data?.message || '未知错误' }
        }
      } catch (error) {
        console.error('加载暂停中订单异常:', error)
        return { success: false, error: error.message }
      }
    }

    // 加载待支付订单
    const loadPendingPaymentOrders = async () => {
      if (!props.steamId) {
        return { success: true, count: 0 }
      }

      try {
        const response = await axios.post(apiUrls.yyypGetPendingPaymentOrders(), {
          steamId: props.steamId
        })

        if (response.data && response.data.code === 200) {
          pendingPaymentItems.value = response.data.data?.orders || []
          return { success: true, count: pendingPaymentItems.value.length }
        } else {
          console.error('加载待支付订单失败:', response.data?.message)
          return { success: false, error: response.data?.message || '未知错误' }
        }
      } catch (error) {
        console.error('加载待支付订单异常:', error)
        return { success: false, error: error.message }
      }
    }

    // 根据当前激活的子标签加载对应数据
    const loadCurrentTabData = async () => {
      if (!props.steamId) {
        ElMessage.warning('请选择账号')
        return
      }

      loading.value = true
      try {
        let result = null

        switch (activeSubTab.value) {
          case 'purchasing':
            result = await loadPurchasingOrders()
            break
          case 'paused':
            result = await loadPausedOrders()
            break
          case 'pending_payment':
            result = await loadPendingPaymentOrders()
            break
        }

        if (result && !result.success) {
          ElMessage.error(`加载失败: ${result.error}`)
          emit('update:count', 0)
        } else if (result) {
          // 成功加载，更新总计数
          const totalCount = purchasingItems.value.length + pausedItems.value.length + pendingPaymentItems.value.length
          emit('update:count', totalCount)
        }
      } catch (error) {
        console.error('加载求购数据失败:', error)
        ElMessage.error('加载失败: ' + error.message)
        emit('update:count', 0)
      } finally {
        loading.value = false
      }
    }

    // 获取历史状态类型
    const getHistoryStatusType = (status) => {
      const statusMap = {
        'completed': 'success',
        'cancelled': 'info',
        'timeout': 'danger'
      }
      return statusMap[status] || 'info'
    }

    // 获取历史状态标签
    const getHistoryStatusLabel = (status) => {
      const labelMap = {
        'completed': '已完成',
        'cancelled': '已取消',
        'timeout': '已超时'
      }
      return labelMap[status] || '未知'
    }

    // 批量处理正在求购
    const handleBatchProcessActive = () => {
      ElMessage.info('批量处理功能待开发')
    }

    // 删除求购
    const handleDeleteRequest = async (item) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除求购 "${item.item_name}" 吗？删除后无法恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        loading.value = true
        const response = await axios.post(apiUrls.yyypDeletePurchaseOrder(), {
          steamId: props.steamId,
          orderNo: item.order_no
        })

        if (response.data && response.data.code === 200) {
          ElMessage.success('删除求购成功')
          // 刷新数据
          await loadCurrentTabData()
        } else {
          ElMessage.error(`删除求购失败: ${response.data?.message || '未知错误'}`)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除求购失败:', error)
          ElMessage.error(`删除求购失败: ${error.message}`)
        }
      } finally {
        loading.value = false
      }
    }

    // 执行确认加价（支持递归处理多次确认）
    const executeConfirmPriceIncrease = async (orderNo, newPrice, forceConfirm) => {
      loading.value = true

      try {
        const confirmResponse = await axios.post(apiUrls.yyypConfirmPriceIncrease(), {
          steamId: props.steamId,
          orderNo: orderNo,
          newPrice: newPrice,
          forceConfirm: forceConfirm
        })

        if (confirmResponse.data && confirmResponse.data.code === 200) {
          const confirmResult = confirmResponse.data.data

          // 如果需要再次确认
          if (confirmResult.need_confirm) {
            loading.value = false

            // 显示API返回的msg，让用户再次确认
            let reconfirmMessage = confirmResult.message

            // 在消息后添加新价格信息
            reconfirmMessage = `${reconfirmMessage}\n\n加价后价格: ¥${newPrice}`

            // 替换换行符为<br>
            reconfirmMessage = reconfirmMessage.replace(/\n/g, '<br>')

            // 将新价格标记为红色粗体
            const newPriceStr = String(newPrice)
            const escapedPrice = newPriceStr.replace(/\./g, '\\.')
            const priceRegex = new RegExp(`¥${escapedPrice}(?!\\d)`, 'g')
            reconfirmMessage = reconfirmMessage.replace(
              priceRegex,
              `<span style="color: #f56c6c; font-weight: bold;">¥${newPriceStr}</span>`
            )

            await ElMessageBox.confirm(
              `${reconfirmMessage}<br><br><span style="color: #909399;">价格仅供参考，请仔细核对后确认</span>`,
              '再次确认加价',
              {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning',
                dangerouslyUseHTMLString: true
              }
            )

            // 用户确认后，递归调用，这次设置 forceConfirm=true
            await executeConfirmPriceIncrease(orderNo, newPrice, true)
          } else if (confirmResult.success) {
            // 加价成功
            ElMessage.success(`加价成功！新价格: ¥${newPrice}`)
            // 刷新数据
            await loadCurrentTabData()
          } else {
            // 加价失败
            ElMessage.error(`加价失败: ${confirmResult.message || '未知错误'}`)
          }
        } else {
          ElMessage.error(`加价失败: ${confirmResponse.data?.message || '未知错误'}`)
        }
      } finally {
        loading.value = false
      }
    }

    // 一键加价
    const handleQuickPriceIncrease = async (item) => {
      try {
        loading.value = true

        // 步骤1: 预检查，获取加价信息
        const precheckResponse = await axios.post(apiUrls.yyypQuickPriceIncrease(), {
          steamId: props.steamId,
          orderNo: item.order_no
        })

        loading.value = false

        if (precheckResponse.data && precheckResponse.data.code === 200) {
          const result = precheckResponse.data.data

          if (!result.success) {
            ElMessage.error(`预检查失败: ${result.message || '未知错误'}`)
            return
          }

          const priceData = result.data
          // 构建确认消息
          let confirmMessage = result.message || `确定要为 "${item.item_name}" 加价吗？`

          // 在消息后添加新价格信息（rankFirstPrice）
          confirmMessage = `${confirmMessage}\n\n加价后价格: ¥${priceData.new_price}`

          // 替换换行符为<br>
          confirmMessage = confirmMessage.replace(/\n/g, '<br>')

          // 将新价格（rankFirstPrice）标记为红色粗体
          const newPriceStr = String(priceData.new_price)
          const escapedPrice = newPriceStr.replace(/\./g, '\\.')
          const priceRegex = new RegExp(`¥${escapedPrice}(?!\\d)`, 'g')
          confirmMessage = confirmMessage.replace(
            priceRegex,
            `<span style="color: #f56c6c; font-weight: bold;">¥${newPriceStr}</span>`
          )

          // 步骤2: 弹出确认对话框，显示API返回的msg
          await ElMessageBox.confirm(
            `${confirmMessage}<br><br><span style="color: #909399;">价格仅供参考，请仔细核对后确认</span>`,
            '确认加价',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning',
              dangerouslyUseHTMLString: true
            }
          )

          // 步骤3: 用户确认后，调用确认加价API（可能需要多次确认）
          await executeConfirmPriceIncrease(item.order_no, priceData.new_price, false)
        } else {
          ElMessage.error(`预检查失败: ${precheckResponse.data?.message || '未知错误'}`)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('一键加价失败:', error)
          ElMessage.error(`一键加价失败: ${error.message}`)
        }
      } finally {
        loading.value = false
      }
    }

    // 暂停求购
    const handlePauseRequest = async (item) => {
      try {
        await ElMessageBox.confirm(
          `确定要暂停求购 "${item.item_name}" 吗?`,
          '确认暂停',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        loading.value = true
        const response = await axios.post(apiUrls.yyypPausePurchaseOrder(), {
          steamId: props.steamId,
          orderNo: item.order_no
        })

        if (response.data && response.data.code === 200) {
          ElMessage.success('暂停求购成功')
          // 刷新数据
          await loadCurrentTabData()
        } else {
          ElMessage.error(`暂停求购失败: ${response.data?.message || '未知错误'}`)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('暂停求购失败:', error)
          ElMessage.error(`暂停求购失败: ${error.message}`)
        }
      } finally {
        loading.value = false
      }
    }

    // 恢复求购（用于暂停中列表）
    const handleResumeRequest = async (item) => {
      try {
        await ElMessageBox.confirm(
          `确定要恢复求购 "${item.item_name}" 吗?`,
          '确认恢复',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'success'
          }
        )

        loading.value = true
        const response = await axios.post(apiUrls.yyypPausePurchaseOrder(), {
          steamId: props.steamId,
          orderNo: item.order_no
        })

        if (response.data && response.data.code === 200) {
          ElMessage.success('恢复求购成功')
          // 刷新数据
          await loadCurrentTabData()
        } else {
          ElMessage.error(`恢复求购失败: ${response.data?.message || '未知错误'}`)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('恢复求购失败:', error)
          ElMessage.error(`恢复求购失败: ${error.message}`)
        }
      } finally {
        loading.value = false
      }
    }

    // 修改求购
    const handleEditRequest = async (item) => {
      try {
        loading.value = true

        // 获取订单详情
        const response = await axios.post(apiUrls.yyypGetOrderInfo(), {
          steamId: props.steamId,
          orderNo: item.order_no
        })

        if (response.data && response.data.code === 200) {
          const result = response.data.data

          if (result.success) {
            // 保存订单数据并打开对话框
            editOrderData.value = result.data
            currentEditOrderNo.value = item.order_no
            editDialogVisible.value = true
          } else {
            ElMessage.error(`获取订单详情失败: ${result.message || '未知错误'}`)
          }
        } else {
          ElMessage.error(`获取订单详情失败: ${response.data?.message || '未知错误'}`)
        }
      } catch (error) {
        console.error('获取订单详情失败:', error)
        ElMessage.error(`获取订单详情失败: ${error.message}`)
      } finally {
        loading.value = false
      }
    }

    // 关闭修改对话框
    const handleCloseEditDialog = () => {
      editDialogVisible.value = false
      currentEditOrderNo.value = ''
      editOrderData.value = null
    }

    // 提交修改（两步流程：前置检查 → 确认修改）
    const handleSubmitEdit = async (editData) => {
      try {
        loading.value = true

        // 步骤1：前置检查
        const checkResponse = await axios.post(apiUrls.yyypPreUpdateCheck(), {
          steamId: props.steamId,
          orderNo: currentEditOrderNo.value,
          unitPrice: editData.unitPrice,
          quantity: editData.quantity,
          autoReceived: editData.autoReceived,
          orderData: editOrderData.value
        })

        if (!checkResponse.data || checkResponse.data.code !== 200) {
          ElMessage.error(`前置检查失败: ${checkResponse.data?.message || '未知错误'}`)
          return
        }

        const checkResult = checkResponse.data.data
        if (!checkResult.success) {
          ElMessage.error(`前置检查失败: ${checkResult.message || '未知错误'}`)
          return
        }

        // 步骤2：确认修改
        const editResponse = await axios.post(apiUrls.yyypEditPurchaseOrder(), {
          steamId: props.steamId,
          orderNo: currentEditOrderNo.value,
          unitPrice: editData.unitPrice,
          quantity: editData.quantity,
          autoReceived: editData.autoReceived,
          orderData: editOrderData.value,
          checkData: checkResult.data
        })

        if (editResponse.data && editResponse.data.code === 200) {
          const result = editResponse.data.data
          if (result.success) {
            ElMessage.success('修改求购成功')
            handleCloseEditDialog()
            await loadCurrentTabData()
          } else {
            ElMessage.error(`修改求购失败: ${result.message || '未知错误'}`)
          }
        } else {
          ElMessage.error(`修改求购失败: ${editResponse.data?.message || '未知错误'}`)
        }
      } catch (error) {
        console.error('修改求购失败:', error)
        ElMessage.error(`修改求购失败: ${error.message}`)
      } finally {
        loading.value = false
      }
    }

    // 立即支付
    const handlePayNow = (item) => {
      ElMessage.info(`立即支付: ${item.item_name}`)
      // TODO: 打开支付对话框
    }

    // 查看详情
    const handleViewDetails = (item) => {
      ElMessage.info(`查看详情: ${item.item_name}`)
      // TODO: 打开详情对话框
    }

    // 查看历史详情
    const handleViewHistoryDetails = (item) => {
      ElMessage.info(`查看历史详情: ${item.item_name}`)
      // TODO: 打开历史详情对话框
    }

    // 再次求购
    const handleRepurchase = (item) => {
      ElMessage.info(`再次求购: ${item.item_name}`)
      // TODO: 打开发布求购对话框，自动填充物品信息
    }

    // 监听 steamId 变化，重新加载数据
    watch(() => props.steamId, (newSteamId) => {
      if (newSteamId) {
        // 重置到第一个标签页并加载数据
        activeSubTab.value = 'purchasing'
        loadCurrentTabData()
      }
    }, { immediate: true })

    // 监听子标签切换，每次切换都重新加载对应数据
    watch(activeSubTab, () => {
      if (props.steamId) {
        loadCurrentTabData()
      }
    })

    // 组件挂载时启动倒计时
    onMounted(() => {
      // 启动倒计时定时器
      countdownTimer = setInterval(() => {
        updateCountdowns()
      }, 1000)
    })

    // 组件卸载时清除定时器
    onUnmounted(() => {
      if (countdownTimer) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
    })

    return {
      loading,
      subTabs,
      activeSubTab,
      purchasingItems,
      pausedItems,
      pendingPaymentItems,
      historyItems,
      historyFilter,
      activePurchaseRequests,
      filteredHistoryItems,
      getSubTabCount,
      formatCountdown,
      getHistoryStatusType,
      getHistoryStatusLabel,
      handleBatchProcessActive,
      handleDeleteRequest,
      handleQuickPriceIncrease,
      handlePauseRequest,
      handleResumeRequest,
      handleEditRequest,
      handlePayNow,
      handleViewDetails,
      handleViewHistoryDetails,
      handleRepurchase,
      // 修改对话框相关
      editDialogVisible,
      editOrderData,
      handleCloseEditDialog,
      handleSubmitEdit
    }
  }
}
