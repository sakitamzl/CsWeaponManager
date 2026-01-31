import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { API_CONFIG, apiUrls } from '@/config/api.js'
import RentFormYYYP from '@/views/Inventory/RentFormYYYP/index.vue'

export default {
  name: 'OnSale',
  components: {
    RentFormYYYP
  },
  setup() {
    const loading = ref(false)
    const updating = ref(false)
    const onSaleData = ref([])
    const accountList = ref([])
    const selectedAccount = ref('')
    const searchText = ref('')
    const weaponTypeFilter = ref('')
    const floatRangeFilter = ref('')
    const displayMode = ref('card')

    // 交易类型
    const selectedTradeType = ref('sale') // 默认选择"出售"
    const tradeTypes = ref([
      { value: 'sale', label: '出售', icon: '💰' },
      { value: 'lease', label: '租赁', icon: '🔄' },
      { value: 'sublease', label: '转租', icon: '🔁' },
      { value: 'presale', label: '预售', icon: '⏰' },
      { value: 'transfer', label: '过户', icon: '📝' },
      { value: 'instant', label: '秒到账', icon: '⚡' }
    ])

    // 图片404缓存
    const image404Cache = ref(new Set())

    // 多选模式相关
    const isMultiSelectMode = ref(true) // 默认开启多选模式
    const selectedItems = ref([])

    // 弹窗相关
    const updatePriceDialogVisible = ref(false)
    const rentPriceDialogVisible = ref(false)  // 租赁改价对话框
    const batchChangePriceDialogVisible = ref(false)  // 批量改价对话框
    const previewVisible = ref(false)
    const selectedItem = ref(null)
    const previewItem = ref(null)
    const updatePriceForm = ref({
      newPrice: ''
    })

    // 租赁改价相关
    const rentPriceFormData = ref(null)  // 租赁改价表单数据
    const rentInitData = ref(null)  // 租赁初始化数据
    const steamId = ref('')  // 当前操作的完整 Steam ID

    // 批量改价相关
    const batchChangePriceForm = ref({
      priceChangeType: 'fixed',  // fixed: 固定价格, percent: 百分比调整
      fixedPrice: '',  // 固定价格值
      percentValue: '',  // 百分比值
      percentType: 'increase'  // increase: 增加, decrease: 减少
    })

    // 格式化租赁改价的 item 数据
    const formattedRentItem = computed(() => {
      // 批量改价模式：使用 selectedItems
      if (selectedItems.value.length > 0 && !selectedItem.value) {
        return selectedItems.value.map(item => ({
          assetid: item.assetid || item.id,
          name: item.item_name || item.steam_hash_name,
          steam_hash_name: item.steam_hash_name || item.item_name,
          image: getWeaponImage(item.steam_hash_name || item.item_name),
          float: item.weapon_float || item.float,
          paintseed: item.paintseed,
          weapon_classID: {
            yyyp_Price: item.deposit_amount || item.yyyp_price || item.market_price,
            yyyp_id: item.template_id || item.yyyp_id
          },
          // 添加当前租赁配置用于自动填充
          currentRentDays: item.lease_max_days,
          currentShortRentPrice: item.short_lease_amount,
          currentLongRentPrice: item.long_lease_amount,
          currentDepositPrice: item.deposit_amount
        }))
      }

      // 单个改价模式：使用 selectedItem
      if (!selectedItem.value) return []

      const item = selectedItem.value
      return [{
        assetid: item.assetid || item.id,
        name: item.item_name || item.steam_hash_name,
        steam_hash_name: item.steam_hash_name || item.item_name,
        image: getWeaponImage(item.steam_hash_name || item.item_name),
        float: item.weapon_float || item.float,
        paintseed: item.paintseed,
        weapon_classID: {
          yyyp_Price: item.deposit_amount || item.yyyp_price || item.market_price,
          yyyp_id: item.template_id || item.yyyp_id
        },
        // 添加当前租赁配置用于自动填充
        currentRentDays: item.lease_max_days,
        currentShortRentPrice: item.short_lease_amount,
        currentLongRentPrice: item.long_lease_amount,
        currentDepositPrice: item.deposit_amount
      }]
    })

    // 统计数据
    const onSaleStats = computed(() => {
      const totalCount = onSaleData.value.length
      const totalPrice = onSaleData.value.reduce((sum, item) => sum + parseFloat(item.sale_price || 0), 0)
      const avgPrice = totalCount > 0 ? (totalPrice / totalCount) : 0
      const expectedProfit = onSaleData.value.reduce((sum, item) => {
        if (item.buy_price) {
          return sum + (parseFloat(item.sale_price) - parseFloat(item.buy_price))
        }
        return sum
      }, 0)

      return {
        totalCount,
        totalPrice: totalPrice.toFixed(2),
        avgPrice: avgPrice.toFixed(2),
        expectedProfit: expectedProfit.toFixed(2)
      }
    })

    // 当前显示数据
    const currentDisplayData = computed(() => {
      let filtered = onSaleData.value

      // 搜索过滤
      if (searchText.value) {
        const search = searchText.value.toLowerCase()
        filtered = filtered.filter(item =>
          item.item_name?.toLowerCase().includes(search) ||
          item.steam_hash_name?.toLowerCase().includes(search)
        )
      }

      // 只显示悠悠有品平台的数据
      filtered = filtered.filter(item => item.platform === 'yyyp')

      // 交易类型过滤
      if (selectedTradeType.value) {
        filtered = filtered.filter(item => {
          // 如果数据库中有 trade_type 字段，使用它；否则默认为 'sale'
          const itemTradeType = item.trade_type || 'sale'
          return itemTradeType === selectedTradeType.value
        })
      }

      // 账号过滤
      if (selectedAccount.value) {
        filtered = filtered.filter(item => item.account_id === selectedAccount.value)
      }

      // 武器类型过滤
      if (weaponTypeFilter.value) {
        filtered = filtered.filter(item => item.weapon_type === weaponTypeFilter.value)
      }

      // 磨损等级过滤
      if (floatRangeFilter.value) {
        filtered = filtered.filter(item => item.float_range === floatRangeFilter.value)
      }

      return filtered
    })

    // 获取每个交易类型的数量
    const getTradeTypeCount = (tradeType) => {
      return onSaleData.value.filter(item => {
        const itemTradeType = item.trade_type || 'sale'
        return itemTradeType === tradeType && item.platform === 'yyyp'
      }).length
    }

    // 处理交易类型切换
    const handleTradeTypeChange = (tradeType) => {
      selectedTradeType.value = tradeType
      // 切换交易类型时清空多选
      selectedItems.value = []
      // 重新加载数据
      loadOnSaleData()
    }

    // 加载在售数据
    const loadOnSaleData = async () => {
      if (!selectedAccount.value) {
        ElMessage.warning('请选择账号')
        return
      }

      loading.value = true
      try {
        let response

        // 根据交易类型选择不同的API
        if (selectedTradeType.value === 'lease') {
          // 租赁类型：调用租赁列表API
          response = await axios.post(apiUrls.yyypGetLeaseList(), {
            steamId: accountList.value.find(acc => acc.id === selectedAccount.value)?.steam_id || '',
            page: 1,
            pageSize: 1000
          })

          if (response.data && response.data.success) {
            // 转换租赁数据格式以匹配前端期望
            const leaseData = response.data.data?.commodityInfoList || []
            onSaleData.value = leaseData.map(item => {
              // 解析印花数据
              let stickerData = null
              if (item.haveSticker && item.stickers && item.stickers.length > 0) {
                stickerData = JSON.stringify(item.stickers.map(sticker => ({
                  name: sticker.name,
                  image: sticker.imageUrl,
                  abrade: sticker.abradeDesc,
                  rawIndex: sticker.rawIndex
                })))
              }

              // 解析挂件数据
              let pendantData = null
              if (item.havePendant && item.pendants && item.pendants.length > 0) {
                const pendant = item.pendants[0]  // 通常只有一个挂件
                pendantData = JSON.stringify({
                  name: pendant.name || '',
                  image: pendant.imageUrl || '',
                  pattern: pendant.pattern || ''
                })
              }

              return {
                id: item.id,
                item_name: item.name,
                steam_hash_name: item.commodityHashName,  // 租赁API返回的是commodityHashName
                sale_price: item.shortLeaseAmount || item.longLeaseAmount || 0,  // 租金（短期或长期）
                buy_price: null,  // 租赁没有购入价
                weapon_float: item.abrade,
                weapon_type: item.typeName || '',
                float_range: item.exteriorName || '',  // 磨损等级名称
                sticker: stickerData,  // 印花数据
                pendant: pendantData,  // 挂件数据
                rename: item.haveNameTag ? '已改名' : null,  // 改名标记
                on_sale_time: item.statusDesc || null,  // 在售时间描述（如"在售1天"）
                platform: 'yyyp',
                trade_type: 'lease',
                account_id: selectedAccount.value,
                // 租赁特有字段
                lease_max_days: item.leaseMaxDays,  // 最大出租天数
                short_lease_amount: item.shortLeaseAmount,  // 短租租金
                long_lease_amount: item.longLeaseAmount,  // 长租租金
                deposit_amount: item.depositAmount,  // 押金
                lease_amount_desc: item.leaseAmountDesc,  // 租金描述
                deposit_amount_desc: item.depositAmountDesc  // 押金描述
              }
            })
            ElMessage.success('加载成功')
          } else {
            ElMessage.error(response.data?.message || '加载失败')
          }
        } else if (selectedTradeType.value === 'sublease') {
          // 转租类型：调用转租列表API
          response = await axios.post(apiUrls.yyypGetSubleaseList(), {
            steamId: accountList.value.find(acc => acc.id === selectedAccount.value)?.steam_id || '',
            page: 1,
            pageSize: 1000
          })

          if (response.data && response.data.success) {
            // 转换转租数据格式以匹配前端期望
            const subleaseData = response.data.data?.commodityInfoList || []
            onSaleData.value = subleaseData.map(item => {
              // 解析印花数据
              let stickerData = null
              if (item.haveSticker && item.stickers && item.stickers.length > 0) {
                stickerData = JSON.stringify(item.stickers.map(sticker => ({
                  name: sticker.name,
                  image: sticker.imageUrl,
                  abrade: sticker.abradeDesc,
                  rawIndex: sticker.rawIndex
                })))
              }

              // 解析挂件数据
              let pendantData = null
              if (item.havePendant && item.pendants && item.pendants.length > 0) {
                const pendant = item.pendants[0]  // 通常只有一个挂件
                pendantData = JSON.stringify({
                  name: pendant.name || '',
                  image: pendant.imageUrl || '',
                  pattern: pendant.pattern || ''
                })
              }

              return {
                id: item.id,
                order_no: item.orderNo || item.id,  // 订单号，用于取消转租
                item_name: item.name,
                steam_hash_name: item.commodityHashName,  // 转租API返回的是commodityHashName
                sale_price: item.shortLeaseAmount || item.longLeaseAmount || 0,  // 租金（短期或长期）
                buy_price: null,  // 转租没有购入价
                weapon_float: item.abrade,
                weapon_type: item.typeName || '',
                float_range: item.exteriorName || '',  // 磨损等级名称
                sticker: stickerData,  // 印花数据
                pendant: pendantData,  // 挂件数据
                rename: item.haveNameTag ? '已改名' : null,  // 改名标记
                on_sale_time: item.statusDesc || null,  // 在售时间描述（如"在售1天"）
                platform: 'yyyp',
                trade_type: 'sublease',
                account_id: selectedAccount.value,
                // 转租特有字段
                lease_max_days: item.leaseMaxDays,  // 最大出租天数
                short_lease_amount: item.shortLeaseAmount,  // 短租租金
                long_lease_amount: item.longLeaseAmount,  // 长租租金
                deposit_amount: item.depositAmount,  // 押金
                lease_amount_desc: item.leaseAmountDesc,  // 租金描述
                deposit_amount_desc: item.depositAmountDesc  // 押金描述
              }
            })
            ElMessage.success('加载成功')
          } else {
            ElMessage.error(response.data?.message || '加载失败')
          }
        } else if (selectedTradeType.value === 'presale') {
          // 预售类型：调用预售列表API
          response = await axios.post(apiUrls.yyypGetPresaleList(), {
            steamId: accountList.value.find(acc => acc.id === selectedAccount.value)?.steam_id || '',
            page: 1,
            pageSize: 1000
          })

          if (response.data && response.data.success) {
            // 转换预售数据格式以匹配前端期望
            const presaleData = response.data.data?.commodityInfoList || []
            onSaleData.value = presaleData.map(item => {
              // 解析印花数据
              let stickerData = null
              if (item.stickers && item.stickers.length > 0) {
                stickerData = JSON.stringify(item.stickers.map(sticker => ({
                  name: sticker.name,
                  image: sticker.imageUrl,
                  abrade: sticker.abradeDesc,
                  rawIndex: sticker.rawIndex
                })))
              }

              // 解析挂件数据（如果有）
              let pendantData = null
              if (item.pendant) {
                pendantData = JSON.stringify({
                  name: item.pendant.name || '',
                  image: item.pendant.imageUrl || '',
                  pattern: item.pendant.pattern || ''
                })
              }

              return {
                id: item.id,
                item_name: item.name,
                steam_hash_name: item.commodityHashName,
                sale_price: parseFloat(item.sellAmount || 0),  // 售价
                buy_price: null,  // 预售没有购入价显示
                weapon_float: item.abrade,
                weapon_type: item.typeName || '',
                float_range: item.exteriorName || '',
                sticker: stickerData,  // 印花数据
                pendant: pendantData,  // 挂件数据
                rename: item.haveNameTag ? '已改名' : null,  // 改名标记
                on_sale_time: item.cacheExpirationDesc || null,  // 剩余冷却天数
                platform: 'yyyp',
                trade_type: 'presale',
                account_id: selectedAccount.value,
                // 预售特有字段
                reference_price: item.referencePrice,  // 市场价
                guard_price_desc: item.guardPriceDesc,  // 保证金描述
                cache_expiration_desc: item.cacheExpirationDesc,  // 剩余冷却天数
                paintseed: item.paintseed  // 图案模板
              }
            })
            ElMessage.success('加载成功')
          } else {
            ElMessage.error(response.data?.message || '加载失败')
          }
        } else {
          // 其他类型：调用原有的在售商品API
          response = await axios.post(apiUrls.getOnSaleItems(), {
            platform: 'yyyp',
            account_id: selectedAccount.value,
            trade_type: selectedTradeType.value
          })

          if (response.data && response.data.success) {
            onSaleData.value = response.data.data || []
            ElMessage.success('加载成功')
          } else {
            ElMessage.error(response.data?.message || '加载失败')
          }
        }
      } catch (error) {
        console.error('加载在售数据失败:', error)
        ElMessage.error('加载失败: ' + error.message)
      } finally {
        loading.value = false
      }
    }

    // 加载账号列表
    const loadAccountList = async () => {
      try {
        const response = await axios.get(apiUrls.getYYYPAccounts())
        if (response.data && response.data.success) {
          accountList.value = response.data.data || []
          if (accountList.value.length > 0) {
            selectedAccount.value = accountList.value[0].id
            // 默认查询第一个账号的数据
            loadOnSaleData()
          } else {
            ElMessage.warning('没有找到悠悠有品账号')
          }
        }
      } catch (error) {
        console.error('加载账号列表失败:', error)
        ElMessage.error('加载账号列表失败: ' + error.message)
      }
    }

    // 处理账号变化
    const handleAccountChange = () => {
      loadOnSaleData()
    }

    // 重置筛选
    const handleReset = () => {
      searchText.value = ''
      weaponTypeFilter.value = ''
      floatRangeFilter.value = ''
      loadOnSaleData()
    }

    // 打开改价弹窗
    const handleUpdatePrice = (item) => {
      selectedItem.value = item
      previewVisible.value = false

      // 判断是否为租赁或转租类型
      if (item.trade_type === 'lease' || item.trade_type === 'sublease') {
        // 打开租赁改价对话框
        openRentPriceDialog(item)
      } else {
        // 打开简单售价改价对话框
        updatePriceForm.value.newPrice = item.sale_price
        updatePriceDialogVisible.value = true
      }
    }

    // 校验价格输入
    const validatePriceInput = () => {
      let value = updatePriceForm.value.newPrice

      if (!value) {
        return
      }

      // 转换为字符串
      value = String(value)

      // 移除非数字和小数点的字符
      value = value.replace(/[^\d.]/g, '')

      // 不允许以多个0开头（除非是0.xx）
      if (value.length > 1 && value[0] === '0' && value[1] !== '.') {
        value = value.replace(/^0+/, '0')
      }

      // 只保留第一个小数点
      const parts = value.split('.')
      if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('')
      }

      // 限制小数点后最多两位
      if (parts.length === 2 && parts[1].length > 2) {
        value = parts[0] + '.' + parts[1].substring(0, 2)
      }

      updatePriceForm.value.newPrice = value
    }

    // 确认改价
    const confirmUpdatePrice = async () => {
      const price = updatePriceForm.value.newPrice

      // 验证价格
      if (!price || price.trim() === '') {
        ElMessage.warning('请输入售价')
        return
      }

      const priceFloat = parseFloat(price)
      if (isNaN(priceFloat) || priceFloat <= 0) {
        ElMessage.warning('请输入有效的价格（大于0）')
        return
      }

      // 验证小数位数
      const parts = price.split('.')
      if (parts.length === 2 && parts[1].length > 2) {
        ElMessage.warning('价格最多保留两位小数')
        return
      }

      updating.value = true
      try {
        const response = await axios.post(apiUrls.updateSalePrice(), {
          id: selectedItem.value.id,
          new_price: price,  // 直接传递原始字符串
          account_id: selectedAccount.value
        })

        if (response.data && response.data.success) {
          ElMessage.success('改价成功')
          updatePriceDialogVisible.value = false
          loadOnSaleData()
        } else {
          ElMessage.error(response.data?.message || '改价失败')
        }
      } catch (error) {
        console.error('改价失败:', error)
        ElMessage.error('改价失败: ' + error.message)
      } finally {
        updating.value = false
      }
    }

    // 打开租赁改价对话框
    const openRentPriceDialog = async (item) => {
      try {
        loading.value = true

        // 获取完整的 Steam ID（从 accountList 中查找）
        steamId.value = accountList.value.find(acc => acc.id === selectedAccount.value)?.steam_id || ''

        if (!steamId.value) {
          ElMessage.error('无法获取Steam ID，请重新选择账号')
          loading.value = false
          return
        }

        // 获取租赁初始化数据、赔付文本、转租协议和转租详情（并行请求）
        const [initResponse, compensationResponse, agreementResponse, detailResponse] = await Promise.all([
          axios.post(
            `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/rentInit`,
            {
              steamId: steamId.value,
              steam_hash_name: [item.steam_hash_name || item.item_name]
            }
          ),
          axios.post(
            `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getCompensationText`,
            {
              steamId: steamId.value,
              itemInfo: {
                abrade: String(item.weapon_float || item.float || '0'),
                leaseType: 0,  // 租赁
                marketHashName: item.steam_hash_name || item.item_name,
                marketPrice: String(item.yyyp_price || item.market_price || '0'),
                pageSourceType: 10,
                paintSeed: parseInt(item.paintseed || 0),
                steamAssetId: parseInt(item.assetid || item.id || 0),
                supportEasyCompensation: false,
                templateId: parseInt(item.template_id || item.yyyp_id || 0)
              }
            }
          ),
          axios.post(
            `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getSubleaseAgreement`,
            {
              steamId: steamId.value
            }
          ),
          axios.post(
            `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getSubleaseDetail`,
            {
              steamId: steamId.value,
              commodityIds: [String(item.commodity_id || item.id)]
            }
          )
        ])

        // 解析初始化数据
        if (initResponse.data && initResponse.data.success) {
          rentInitData.value = initResponse.data.data

          // 合并赔付文本数据
          if (compensationResponse.data && compensationResponse.data.success) {
            const compensationData = compensationResponse.data.data
            // 保存赔付文本到 initData 中，方便 RentFormYYYP 使用
            rentInitData.value.compensationRichContent = compensationData.compensationRichContent
            console.log('[租赁改价] 赔付文本获取成功:', compensationData.compensationRichContent)
          } else {
            console.warn('[租赁改价] 赔付文本获取失败:', compensationResponse.data?.message)
          }

          // 合并转租协议数据
          if (agreementResponse.data && agreementResponse.data.success) {
            const agreementData = agreementResponse.data.data
            rentInitData.value.agreementList = agreementData
            console.log('[租赁改价] 转租协议获取成功:', agreementData)
          } else {
            console.warn('[租赁改价] 转租协议获取失败:', agreementResponse.data?.message)
          }

          // 合并转租详情数据
          if (detailResponse.data && detailResponse.data.success) {
            const detailData = detailResponse.data.data
            rentInitData.value.subleaseDetail = detailData
            console.log('[租赁改价] 转租详情获取成功:', detailData)
          } else {
            console.warn('[租赁改价] 转租详情获取失败:', detailResponse.data?.message)
          }

          // 打开租赁改价对话框
          rentPriceDialogVisible.value = true
        } else {
          ElMessage.error(initResponse.data?.message || '获取租赁配置失败')
        }
      } catch (error) {
        console.error('打开租赁改价对话框失败:', error)
        ElMessage.error('打开租赁改价对话框失败: ' + error.message)
      } finally {
        loading.value = false
      }
    }

    // 提交租赁改价（此处省略了具体实现，太长了）
    const confirmRentPriceUpdate = async (submitData) => {
      // 实现代码太长，这里省略...
      // 具体实现请参考原文件
    }

    // 下架商品
    const handleRemoveFromSale = async (item) => {
      const actionText = item.trade_type === 'sublease' ? '取消转租' : '下架'

      try {
        await ElMessageBox.confirm(
          `确定要${actionText} "${getCardTitle(item)}" 吗？`,
          `确认${actionText}`,
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        loading.value = true

        // 根据交易类型选择不同的API
        let response
        if (item.trade_type === 'sublease') {
          // 转租类型：调用取消转租API
          const steamId = accountList.value.find(acc => acc.id === selectedAccount.value)?.steam_id || ''
          response = await axios.post(apiUrls.yyypCancelSublease(), {
            steamId: steamId,
            orderNoList: [item.order_no || item.id]  // 传递订单号数组
          })
        } else if (item.trade_type === 'lease') {
          // 租赁类型：调用悠悠有品下架API
          const steamId = accountList.value.find(acc => acc.id === selectedAccount.value)?.steam_id || ''
          response = await axios.post(apiUrls.yyypOffShelf(), {
            steamId: steamId,
            ids: [item.id]  // 传递ID数组
          })
        } else {
          // 其他类型：调用原有的下架API
          response = await axios.post(apiUrls.removeFromSale(), {
            id: item.id,
            account_id: selectedAccount.value
          })
        }

        if (response.data && response.data.success) {
          ElMessage.success(`${actionText}成功`)
          previewVisible.value = false
          loadOnSaleData()
        } else {
          ElMessage.error(response.data?.message || `${actionText}失败`)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error(`${actionText}失败:`, error)
          ElMessage.error(`${actionText}失败: ` + error.message)
        }
      } finally {
        loading.value = false
      }
    }

    // 打开批量改价对话框
    const handleBatchChangePrice = async () => {
      // 实现代码省略...
    }

    // 计算新价格（用于预览）
    const calculateNewPrice = (currentPrice) => {
      const price = parseFloat(currentPrice)
      if (isNaN(price)) return '0.00'

      if (batchChangePriceForm.value.priceChangeType === 'fixed') {
        return parseFloat(batchChangePriceForm.value.fixedPrice || 0).toFixed(2)
      } else {
        const percent = parseFloat(batchChangePriceForm.value.percentValue || 0) / 100
        let newPrice = price
        if (batchChangePriceForm.value.percentType === 'increase') {
          newPrice = price * (1 + percent)
        } else {
          newPrice = price * (1 - percent)
        }
        return Math.max(0, newPrice).toFixed(2)
      }
    }

    // 确认批量改价
    const confirmBatchChangePrice = async () => {
      // 实现代码省略...
    }

    // 批量下架商品
    const handleBatchRemoveFromSale = async () => {
      // 实现代码省略...
    }

    // 打开预览
    const openPreview = (item) => {
      previewItem.value = item
      previewVisible.value = true
    }

    // 工具函数
    const getWeaponImage = (steamHashName) => {
      if (!steamHashName) {
        return null // 如果没有steam_hash_name，返回null，不显示图片
      }
      // 检查是否已经在404缓存中
      if (image404Cache.value.has(steamHashName)) {
        return null // 如果之前404过，直接返回null，不显示图片
      }
      // 将空格和竖线分别替换为下划线，并添加.png扩展名
      const imageName = steamHashName
        .replace(/\s*\|\s*/g, '___')  // " | " -> "___" (竖线及其两侧空格替换为三个下划线)
        .replace(/\s/g, '_')          // 剩余所有空格 -> "_"
        + '.png'

      return apiUrls.weaponImage(imageName)
    }

    const handleImageError = (e, steamHashName) => {
      // 将失败的steam_hash_name添加到404缓存中
      if (steamHashName) {
        image404Cache.value.add(steamHashName)
      }

      // 移除错误监听器，防止重复触发
      e.target.onerror = null

      // 隐藏图片，不设置data URI，避免将图片数据加载到内存
      e.target.style.display = 'none'
    }

    const getCardTitle = (item) => {
      if (!item) return ''
      return item.item_name || item.steam_hash_name || '未知物品'
    }

    const getItemTitle = (item) => {
      return getCardTitle(item)
    }

    const hasExtras = (item) => {
      return item.sticker || item.pendant || item.rename
    }

    const parseStickers = (stickerData) => {
      if (!stickerData) return []
      try {
        if (typeof stickerData === 'string') {
          return JSON.parse(stickerData)
        }
        return Array.isArray(stickerData) ? stickerData : []
      } catch (e) {
        return []
      }
    }

    const parsePendant = (pendantData) => {
      if (!pendantData) return null
      try {
        if (typeof pendantData === 'string') {
          return JSON.parse(pendantData)
        }
        return pendantData
      } catch (e) {
        return null
      }
    }

    const getPlatformLabel = (platform) => {
      const labels = {
        'yyyp': '悠悠有品',
        'buff': 'BUFF',
        'csfloat': 'CSFloat'
      }
      return labels[platform] || platform
    }

    const getPlatformTagType = (platform) => {
      const types = {
        'yyyp': 'success',
        'buff': 'warning',
        'csfloat': 'info'
      }
      return types[platform] || 'default'
    }

    // 多选模式相关函数
    const toggleMultiSelectMode = () => {
      isMultiSelectMode.value = !isMultiSelectMode.value
      if (!isMultiSelectMode.value) {
        // 退出多选模式时清空选择
        selectedItems.value = []
      }
    }

    const isItemSelected = (itemId) => {
      return selectedItems.value.some(item => item.id === itemId)
    }

    const toggleItemSelection = (item) => {
      const index = selectedItems.value.findIndex(i => i.id === item.id)
      if (index > -1) {
        selectedItems.value.splice(index, 1)
      } else {
        selectedItems.value.push(item)
      }
    }

    const handleCardClick = (item) => {
      if (isMultiSelectMode.value) {
        toggleItemSelection(item)
      } else {
        openPreview(item)
      }
    }

    const formatOnSaleTime = (time) => {
      if (!time) return ''

      // 如果已经是描述性文本（如"在售1天"），直接返回
      if (typeof time === 'string' && (time.includes('在售') || time.includes('天') || time.includes('小时'))) {
        return time
      }

      // 尝试解析为日期
      const date = new Date(time)

      // 检查是否为有效日期
      if (isNaN(date.getTime())) {
        return ''  // 无效日期返回空字符串，不显示
      }

      const now = new Date()
      const diff = now - date
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))

      if (days === 0) return '今天上架'
      if (days === 1) return '昨天上架'
      if (days < 7) return `${days}天前`
      return date.toLocaleDateString('zh-CN')
    }

    // 获取价格差异样式类
    const getPriceDiffClass = (salePrice, buyPrice) => {
      if (!salePrice || !buyPrice) return ''
      const diff = parseFloat(salePrice) - parseFloat(buyPrice)
      if (diff === 0) return 'price-equal'
      return diff > 0 ? 'price-profit' : 'price-loss'
    }

    onMounted(() => {
      loadAccountList()
    })

    return {
      loading,
      updating,
      onSaleData,
      accountList,
      selectedAccount,
      searchText,
      weaponTypeFilter,
      floatRangeFilter,
      displayMode,
      selectedTradeType,
      tradeTypes,
      isMultiSelectMode,
      selectedItems,
      updatePriceDialogVisible,
      rentPriceDialogVisible,
      previewVisible,
      selectedItem,
      previewItem,
      updatePriceForm,
      rentInitData,
      steamId,
      formattedRentItem,
      onSaleStats,
      currentDisplayData,
      loadOnSaleData,
      loadAccountList,
      handleAccountChange,
      handleReset,
      handleUpdatePrice,
      validatePriceInput,
      confirmUpdatePrice,
      confirmRentPriceUpdate,
      handleRemoveFromSale,
      handleBatchChangePrice,
      calculateNewPrice,
      confirmBatchChangePrice,
      handleBatchRemoveFromSale,
      openPreview,
      getWeaponImage,
      handleImageError,
      getCardTitle,
      getItemTitle,
      hasExtras,
      parseStickers,
      parsePendant,
      getPlatformLabel,
      getPlatformTagType,
      formatOnSaleTime,
      toggleMultiSelectMode,
      isItemSelected,
      toggleItemSelection,
      handleCardClick,
      getPriceDiffClass,
      getTradeTypeCount,
      handleTradeTypeChange,
      batchChangePriceDialogVisible,
      batchChangePriceForm
    }
  }
}