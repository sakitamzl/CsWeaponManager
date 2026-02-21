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
      { value: 'pending_payment', label: '待支付' },
      { value: 'history', label: '求购记录' }
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

    // 求购记录分页状态
    const historyPage = ref(1)
    const historyHasMore = ref(true)
    const historyLoading = ref(false)

    // 求购中分页状态
    const purchasingPage = ref(1)
    const purchasingHasMore = ref(true)
    const purchasingLoading = ref(false)

    // 暂停中分页状态
    const pausedPage = ref(1)
    const pausedHasMore = ref(true)
    const pausedLoading = ref(false)

    // 发布求购：搜索状态
    const searchKeyword = ref('')
    const searchResults = ref([])
    const searchLoading = ref(false)

    // 发布求购：对话框状态
    const publishDialogVisible = ref(false)
    const publishDialogData = ref(null)

    // 求购余额
    const purchaseBalance = ref(null)
    const balanceLoading = ref(false)

    // 从钱包转入对话框
    const transferInDialogVisible = ref(false)
    const transferInAvailableYuan = ref(0)

    // 转出到钱包对话框
    const transferOutDialogVisible = ref(false)

    // 倒计时定时器
    let countdownTimer = null

    // 计算属性 - 正在求购的所有物品（用于批量处理按钮显示）
    const activePurchaseRequests = computed(() => {
      return [...purchasingItems.value, ...pausedItems.value, ...pendingPaymentItems.value]
    })

    // 计算属性 - 筛选后的历史记录（按 API 数字状态码过滤）
    const filteredHistoryItems = computed(() => {
      if (historyFilter.value === 'all') return historyItems.value
      const statusCodeMap = { 'completed': 40, 'deleted': 1 }
      const targetStatus = statusCodeMap[historyFilter.value]
      if (targetStatus === undefined) return historyItems.value
      return historyItems.value.filter(item => item.status === targetStatus)
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
        case 'history':
          return historyItems.value.length
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

    // 加载更多求购中订单（无限滚动追加）
    const loadMorePurchasing = async () => {
      if (purchasingLoading.value || !purchasingHasMore.value) return
      if (!props.steamId) return

      purchasingLoading.value = true
      try {
        const response = await axios.post(apiUrls.yyypGetPurchaseOrders(), {
          steamId: props.steamId,
          status: 20,
          pageIndex: purchasingPage.value
        })

        if (response.data && response.data.code === 200) {
          const result = response.data.data
          purchasingItems.value = [...purchasingItems.value, ...(result.orders || [])]
          purchasingHasMore.value = result.has_more || false
          purchasingPage.value++
        } else {
          purchasingHasMore.value = false
          console.error('加载求购中订单失败:', response.data?.message)
        }
      } catch (error) {
        console.error('加载求购中订单异常:', error)
        purchasingHasMore.value = false
      } finally {
        purchasingLoading.value = false
      }
    }

    // 重置求购中列表
    const resetPurchasing = () => {
      purchasingItems.value = []
      purchasingPage.value = 1
      purchasingHasMore.value = true
    }

    // 加载更多暂停中订单（无限滚动追加）
    const loadMorePaused = async () => {
      if (pausedLoading.value || !pausedHasMore.value) return
      if (!props.steamId) return

      pausedLoading.value = true
      try {
        const response = await axios.post(apiUrls.yyypGetPurchaseOrders(), {
          steamId: props.steamId,
          status: 30,
          pageIndex: pausedPage.value
        })

        if (response.data && response.data.code === 200) {
          const result = response.data.data
          pausedItems.value = [...pausedItems.value, ...(result.orders || [])]
          pausedHasMore.value = result.has_more || false
          pausedPage.value++
        } else {
          pausedHasMore.value = false
          console.error('加载暂停中订单失败:', response.data?.message)
        }
      } catch (error) {
        console.error('加载暂停中订单异常:', error)
        pausedHasMore.value = false
      } finally {
        pausedLoading.value = false
      }
    }

    // 重置暂停中列表
    const resetPaused = () => {
      pausedItems.value = []
      pausedPage.value = 1
      pausedHasMore.value = true
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
        switch (activeSubTab.value) {
          case 'purchasing':
            resetPurchasing()
            await loadMorePurchasing()
            break
          case 'paused':
            resetPaused()
            await loadMorePaused()
            break
          case 'pending_payment': {
            const result = await loadPendingPaymentOrders()
            if (result && !result.success) {
              ElMessage.error(`加载失败: ${result.error}`)
              emit('update:count', 0)
              return
            }
            break
          }
          case 'history':
            resetHistory()
            await loadMoreHistory()
            break
        }
        const totalCount = purchasingItems.value.length + pausedItems.value.length + pendingPaymentItems.value.length
        emit('update:count', totalCount)
      } catch (error) {
        console.error('加载求购数据失败:', error)
        ElMessage.error('加载失败: ' + error.message)
        emit('update:count', 0)
      } finally {
        loading.value = false
      }
    }

    // 无限滚动：路由到当前标签对应的加载器
    const loadMoreCurrentTab = () => {
      if (activeSubTab.value === 'purchasing') loadMorePurchasing()
      else if (activeSubTab.value === 'paused') loadMorePaused()
      else if (activeSubTab.value === 'history') loadMoreHistory()
    }

    // 当前标签是否禁用滚动加载
    const currentTabScrollDisabled = computed(() => {
      if (activeSubTab.value === 'purchasing') return !purchasingHasMore.value || purchasingLoading.value
      if (activeSubTab.value === 'paused') return !pausedHasMore.value || pausedLoading.value
      if (activeSubTab.value === 'history') return !historyHasMore.value || historyLoading.value
      return true
    })

    // 获取历史状态类型（按 API 状态码）
    const getHistoryStatusType = (status) => {
      const statusMap = { 40: 'success', 20: 'warning', 1: 'danger' }
      return statusMap[status] || 'info'
    }

    // 加载更多求购记录（无限滚动）
    const loadMoreHistory = async () => {
      if (historyLoading.value || !historyHasMore.value) return
      if (!props.steamId) return

      historyLoading.value = true
      try {
        const response = await axios.post(apiUrls.yyypGetPurchaseRecords(), {
          steamId: props.steamId,
          pageIndex: historyPage.value
        })

        if (response.data && response.data.code === 200) {
          const result = response.data.data
          historyItems.value = [...historyItems.value, ...(result.records || [])]
          historyHasMore.value = result.has_more || false
          historyPage.value++
        } else {
          historyHasMore.value = false
        }
      } catch (error) {
        console.error('加载求购记录失败:', error)
        historyHasMore.value = false
      } finally {
        historyLoading.value = false
      }
    }

    // 重置求购记录（切换账号时调用）
    const resetHistory = () => {
      historyItems.value = []
      historyPage.value = 1
      historyHasMore.value = true
    }

    // 搜索求购饰品模板
    const handleSearchTemplate = async () => {
      if (!searchKeyword.value.trim()) {
        ElMessage.warning('请输入搜索关键词')
        return
      }
      if (!props.steamId) {
        ElMessage.warning('请选择账号')
        return
      }

      searchLoading.value = true
      searchResults.value = []
      try {
        const response = await axios.post(apiUrls.yyypSearchPurchaseTemplate(), {
          steamId: props.steamId,
          keyWords: searchKeyword.value.trim()
        })

        if (response.data && response.data.code === 200) {
          searchResults.value = response.data.data?.items || []
          if (searchResults.value.length === 0) {
            ElMessage.info('未找到相关饰品')
          }
        } else {
          ElMessage.error(`搜索失败: ${response.data?.message || '未知错误'}`)
        }
      } catch (error) {
        console.error('搜索饰品失败:', error)
        ElMessage.error(`搜索失败: ${error.message}`)
      } finally {
        searchLoading.value = false
      }
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

    // 开启求购（用于暂停中列表）
    const handleResumeRequest = async (item) => {
      try {
        await ElMessageBox.confirm(
          `确定要开启求购 "${item.item_name}" 吗?`,
          '确认开启',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'success'
          }
        )

        loading.value = true
        const response = await axios.post(apiUrls.yyypOpenPurchaseOrder(), {
          steamId: props.steamId,
          orderNo: item.order_no
        })

        if (response.data && response.data.code === 200) {
          const result = response.data.data
          if (result.success) {
            ElMessage.success('开启求购成功')
            await loadCurrentTabData()
          } else {
            ElMessage.error(`开启求购失败: ${result.message || '未知错误'}`)
          }
        } else {
          ElMessage.error(`开启求购失败: ${response.data?.message || '未知错误'}`)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('开启求购失败:', error)
          ElMessage.error(`开启求购失败: ${error.message}`)
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

        // 余额检查：只要 needPaymentAmount 超过当前余额就拦截
        const needAmount = parseFloat(checkResult.data?.needPaymentAmount || 0)
        const currentBalance = purchaseBalance.value ? purchaseBalance.value.balance_yuan : 0
        if (needAmount > currentBalance) {
          ElMessage.warning(
            `求购余额不足（需 ¥${needAmount.toFixed(2)}，当前余额 ¥${currentBalance.toFixed(2)}），请先转入求购余额`
          )
          await handleTransferIn()
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

    // 从搜索结果发布求购：获取发布详情并打开对话框
    const handlePublishRequest = async (item) => {
      if (!props.steamId) {
        ElMessage.warning('请选择账号')
        return
      }

      loading.value = true
      try {
        const response = await axios.post(apiUrls.yyypGetTemplatePurchaseInfo(), {
          steamId: props.steamId,
          templateId: item.id
        })

        if (response.data && response.data.code === 200) {
          publishDialogData.value = response.data.data
          publishDialogVisible.value = true
        } else {
          ElMessage.error(`获取发布详情失败: ${response.data?.message || '未知错误'}`)
        }
      } catch (error) {
        console.error('获取发布详情失败:', error)
        ElMessage.error(`获取发布详情失败: ${error.message}`)
      } finally {
        loading.value = false
      }
    }

    // 提交发布求购（两步：预检查 → 确认 → 提交）
    const handleSubmitPublish = async (submitData) => {
      const { unitPrice, quantity, autoReceived, templateData } = submitData
      const purchasePrice = parseFloat(unitPrice)
      const purchaseNum = parseInt(quantity)
      const totalAmount = purchasePrice * purchaseNum
      const incrementServiceCode = autoReceived ? [1001] : []

      const ti = templateData.template_info

      // 步骤1：预检查
      loading.value = true
      try {
        const preCheckResponse = await axios.post(apiUrls.yyypPrePurchaseOrderCheck(), {
          steamId: props.steamId,
          orderData: {
            specialStyleObj: {},
            isCheckMaxPrice: false,
            templateHashName: ti.template_hash_name,
            totalAmount,
            referencePrice: ti.reference_price,
            purchasePrice,
            purchaseNum,
            discountAmount: 0,
            minSellPrice: parseFloat(ti.min_sell_price),
            maxPurchasePrice: parseFloat(ti.max_purchase_price),
            templateId: String(ti.template_id),
            incrementServiceCode
          }
        })

        loading.value = false

        if (!preCheckResponse.data || preCheckResponse.data.code !== 200) {
          ElMessage.error(`预检查失败: ${preCheckResponse.data?.message || '未知错误'}`)
          return
        }

        const preCheckResult = preCheckResponse.data.data

        // 余额检查：needPaymentAmount 与当前求购余额比较
        const needAmount = parseFloat(preCheckResult.needPaymentAmount)
        const currentBalance = purchaseBalance.value ? purchaseBalance.value.balance_yuan : 0
        if (needAmount > currentBalance) {
          ElMessage.warning(
            `求购余额不足（需 ¥${needAmount.toFixed(2)}，当前余额 ¥${currentBalance.toFixed(2)}），请先转入求购余额`
          )
          await handleTransferIn()
          return
        }

        // 步骤2：确认弹框
        await ElMessageBox.confirm(
          `确定发布求购吗？<br>` +
          `单价：<span style="color:#F56C6C;font-weight:bold;">¥${purchasePrice}</span>，` +
          `数量：<span style="font-weight:bold;">${purchaseNum}</span><br>` +
          `需支付：<span style="color:#F56C6C;font-weight:bold;">¥${preCheckResult.needPaymentAmount}</span>`,
          '确认发布求购',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
            dangerouslyUseHTMLString: true
          }
        )

        // 步骤3：提交订单
        loading.value = true
        const saveResponse = await axios.post(apiUrls.yyypSavePurchaseOrder(), {
          steamId: props.steamId,
          orderData: {
            templateId: ti.template_id,
            templateHashName: ti.template_hash_name,
            commodityName: ti.commodity_name,
            referencePrice: ti.reference_price,
            minSellPrice: ti.min_sell_price,
            maxPurchasePrice: ti.max_purchase_price,
            purchasePrice,
            purchaseNum,
            needPaymentAmount: preCheckResult.needPaymentAmount,
            incrementServiceCode,
            totalAmount: preCheckResult.totalAmount,
            templateName: preCheckResult.templateName,
            priceDifference: preCheckResult.priceDifference,
            discountAmount: 0,
            payConfirmFlag: false,
            repeatOrderCancelFlag: false
          }
        })

        if (saveResponse.data && saveResponse.data.code === 200) {
          const saveResult = saveResponse.data.data
          ElMessage.success(`发布求购成功！订单号：${saveResult.orderNo}`)
          publishDialogVisible.value = false
          // 刷新求购中列表
          resetPurchasing()
          await loadMorePurchasing()
          if (activeSubTab.value !== 'purchasing') {
            activeSubTab.value = 'purchasing'
          }
        } else {
          ElMessage.error(`提交求购失败: ${saveResponse.data?.message || '未知错误'}`)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('发布求购失败:', error)
          ElMessage.error(`发布求购失败: ${error.message}`)
        }
      } finally {
        loading.value = false
      }
    }

    // 查看市场（从搜索结果）
    const handleViewMarket = (item) => {
      ElMessage.info(`查看市场: ${item.item_name}`)
      // TODO: 打开市场列表页面
    }

    // 获取求购余额
    const fetchPurchaseBalance = async () => {
      if (!props.steamId) return
      balanceLoading.value = true
      try {
        const response = await axios.post(apiUrls.yyypGetPurchaseBalance(), {
          steamId: props.steamId
        })
        if (response.data && response.data.code === 200) {
          purchaseBalance.value = response.data.data
        } else {
          console.error('获取求购余额失败:', response.data?.message)
        }
      } catch (error) {
        console.error('获取求购余额异常:', error)
      } finally {
        balanceLoading.value = false
      }
    }

    // 从钱包余额转入：打开对话框前先查询可用余额
    const handleTransferIn = async () => {
      if (!props.steamId) {
        ElMessage.warning('请选择账号')
        return
      }

      loading.value = true
      try {
        const queryResponse = await axios.post(apiUrls.yyypQueryTransferInBalance(), {
          steamId: props.steamId
        })

        if (!queryResponse.data || queryResponse.data.code !== 200) {
          ElMessage.error(`查询余额失败: ${queryResponse.data?.message || '未知错误'}`)
          return
        }

        transferInAvailableYuan.value = queryResponse.data.data.available_yuan
        transferInDialogVisible.value = true
      } catch (error) {
        ElMessage.error(`查询余额失败: ${error.message}`)
      } finally {
        loading.value = false
      }
    }

    // 确认转入（由 TransferInDialog emit）
    const handleTransferInConfirm = async (transferMoney) => {
      transferInDialogVisible.value = false
      loading.value = true
      try {
        const confirmResponse = await axios.post(apiUrls.yyypConfirmTransferIn(), {
          steamId: props.steamId,
          transferMoney
        })

        if (confirmResponse.data && confirmResponse.data.code === 200) {
          ElMessage.success(`成功转入 ¥${parseFloat(transferMoney).toFixed(2)} 到求购余额`)
          await fetchPurchaseBalance()
        } else {
          ElMessage.error(`转入失败: ${confirmResponse.data?.message || '未知错误'}`)
        }
      } catch (error) {
        ElMessage.error(`转入失败: ${error.message}`)
      } finally {
        loading.value = false
      }
    }

    // 转出到钱包：打开对话框
    const handleTransferOut = () => {
      if (!props.steamId) {
        ElMessage.warning('请选择账号')
        return
      }
      if (!purchaseBalance.value || purchaseBalance.value.balance_yuan <= 0) {
        ElMessage.warning('求购余额不足，无法转出')
        return
      }
      transferOutDialogVisible.value = true
    }

    // 确认转出（由 TransferOutDialog emit）
    const handleTransferOutConfirm = async (transferMoney) => {
      transferOutDialogVisible.value = false
      loading.value = true
      try {
        const confirmResponse = await axios.post(apiUrls.yyypConfirmTransferOut(), {
          steamId: props.steamId,
          transferMoney
        })

        if (confirmResponse.data && confirmResponse.data.code === 200) {
          ElMessage.success(`成功转出 ¥${parseFloat(transferMoney).toFixed(2)} 到钱包`)
          await fetchPurchaseBalance()
        } else {
          ElMessage.error(`转出失败: ${confirmResponse.data?.message || '未知错误'}`)
        }
      } catch (error) {
        ElMessage.error(`转出失败: ${error.message}`)
      } finally {
        loading.value = false
      }
    }

    // 监听 steamId 变化，重新加载数据
    watch(() => props.steamId, (newSteamId) => {
      if (newSteamId) {
        // 重置到第一个标签页并加载数据
        activeSubTab.value = 'purchasing'
        resetPaused()
        loadCurrentTabData()
        // 重置求购记录，触发无限滚动重新加载
        resetHistory()
        // 加载求购余额
        fetchPurchaseBalance()
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
      loadCurrentTabData,
      getSubTabCount,
      formatCountdown,
      getHistoryStatusType,
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
      handleSubmitEdit,
      // 求购记录无限滚动
      historyLoading,
      historyHasMore,
      loadMoreHistory,
      // 求购中/暂停中无限滚动
      purchasingLoading,
      purchasingHasMore,
      pausedLoading,
      pausedHasMore,
      loadMoreCurrentTab,
      currentTabScrollDisabled,
      // 发布求购：搜索
      searchKeyword,
      searchResults,
      searchLoading,
      handleSearchTemplate,
      handlePublishRequest,
      handleViewMarket,
      // 发布求购对话框
      publishDialogVisible,
      publishDialogData,
      handleSubmitPublish,
      // 求购余额
      purchaseBalance,
      balanceLoading,
      fetchPurchaseBalance,
      handleTransferIn,
      handleTransferOut,
      // 从钱包转入对话框
      transferInDialogVisible,
      transferInAvailableYuan,
      handleTransferInConfirm,
      // 转出到钱包对话框
      transferOutDialogVisible,
      handleTransferOutConfirm
    }
  }
}
