<template>
  <div class="rent-form-yyyp">
    <!-- 头部标题已简化，去掉“X个饰品上架”提示 -->

    <div class="form-content">
      <!-- 交易方式 + 押金赔付 + 增值服务 -->
      <div class="form-section">
        <div class="trade-and-services-row">
          <!-- 交易方式 -->
          <div class="trade-mode-block trade-card">
            <div class="trade-mode-buttons">
              <div
                v-for="method in tradeMethods"
                :key="method.id"
                class="trade-mode-btn"
                :class="{ active: formData.tradeMode === method.type }"
                @click="formData.tradeMode = method.type"
              >
                <span class="mode-label">{{ method.name }}</span>
              </div>
            </div>
          </div>

          <!-- 押金赔付 -->
          <div class="trade-card deposit-card">
            <div class="compensation-icon">
              <span class="icon-badge">V</span>
            </div>
            <div class="compensation-content">
              <div class="compensation-text" v-html="compensationRichText"></div>
            </div>
          </div>

          <!-- 增值服务 -->
          <div class="trade-card services-card">
            <div class="value-added-inline">
              <!-- 0CD出租 -->
              <div
                class="service-item-inline service-switch-item"
                :class="{ disabled: !canEnableZeroCD }"
              >
                <span class="service-label">
                  <span class="service-badge zero-cd">0CD</span>
                </span>
                <el-switch
                  v-model="formData.services.zeroCooldown"
                  size="large"
                  :disabled="!canEnableZeroCD"
                />
              </div>

              <!-- 租送活动 -->
              <div
                class="service-item-inline service-switch-item"
              >
                <span class="service-label">
                  <span class="service-badge rent-activity">租送</span>
                </span>
                <el-switch
                  v-model="formData.services.rentActivity"
                  size="large"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 出租天数 -->
      <div class="form-section">
        <div class="section-label">出租天数</div>
        <div class="rent-days-buttons">
          <div
            v-for="days in rentDaysOptions"
            :key="days"
            class="rent-day-btn"
            :class="{ active: formData.rentDays === days }"
            @click="formData.rentDays = days"
          >
            <span class="day-label">{{ days }}天</span>
          </div>
          <!-- 自定义天数输入框 -->
          <div class="rent-day-input-wrapper">
            <el-input
              v-model="formData.customDays"
              placeholder="自定义"
              type="number"
              :min="minRentDays"
              :max="maxRentDays"
              class="custom-days-inline-input"
              @focus="formData.rentDays = 'custom'"
            >
              <template #suffix>
                <span class="input-suffix">天</span>
              </template>
            </el-input>
          </div>
        </div>
      </div>

      <!-- 选中的饰品列表 -->
      <div class="form-section">
        <div class="section-label">选中的饰品</div>
        <div class="items-list">
          <div
            v-for="(item, index) in items"
            :key="item.assetid"
            class="item-card"
          >
            <!-- 左侧：饰品信息 -->
            <div class="item-left-box">
              <div class="item-image">
                <img
                  v-if="item.image"
                  :src="item.image"
                  :alt="item.name"
                  @error="handleImageError"
                />
                <div v-else class="image-placeholder">无图</div>
              </div>
              <div class="item-info">
                <div class="item-name" :title="item.name">{{ item.name }}</div>
                
                <!-- 磨损值 -->
                <div v-if="item.float" class="item-float-text">
                  磨损: {{ item.float }}
                </div>
                
                <!-- 磨损进度条 -->
                <div v-if="item.float" class="float-bar">
                  <div class="float-segment fn"></div>
                  <div class="float-segment mw"></div>
                  <div class="float-segment ft"></div>
                  <div class="float-segment ww"></div>
                  <div class="float-segment bs"></div>
                  <div
                    class="float-pointer"
                    :style="{ left: `${parseFloat(item.float) * 100}%` }"
                  ></div>
                </div>
                
                <!-- 购入价格 -->
                <div v-if="item.buyPrice" class="item-buy-price">
                  购入: ¥{{ item.buyPrice }}
                </div>
              </div>
            </div>

            <!-- 右侧：输入框 -->
            <div class="item-right-box">
              <!-- 短租租金 -->
              <el-input
                v-model="itemFormMap[item.assetid].shortRentPrice"
                placeholder="短租租金"
                class="price-input"
              />

              <!-- 长租租金 -->
              <el-input
                v-model="itemFormMap[item.assetid].longRentPrice"
                placeholder="长租租金"
                class="price-input"
              />

              <!-- 商品押金 -->
              <el-input
                v-model="itemFormMap[item.assetid].depositPrice"
                placeholder="商品押金"
                class="price-input"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作按钮 -->
    <div class="form-footer">
      <el-button
        class="footer-btn auto-price-btn"
        @click="handleAutoPricing"
        :loading="autoPricingLoading"
      >
        一键定价
      </el-button>
      <el-button class="footer-btn cancel-btn" @click="handleCancel">
        取消
      </el-button>
      <el-button class="footer-btn submit-btn" type="primary" @click="handleSubmit">
        确认上架
      </el-button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api'

export default {
  name: 'RentFormYYYP',
  props: {
    items: {
      type: Array,
      default: () => []
    },
    initData: {
      type: Object,
      default: () => null
    },
    steamId: {
      type: String,
      default: ''
    }
  },
  emits: ['cancel', 'submit'],
  setup(props, { emit }) {
    const autoPricingLoading = ref(false)

    // 赔付文本（富文本HTML）
    const compensationRichText = ref('')

    // 全局表单数据（交易方式/租期/增值服务）
    const formData = reactive({
      tradeMode: 1, // 默认租赁
      rentDays: 8, // 默认天数
      customDays: null,
      services: {
        zeroCooldown: false, // 0CD出租
        rentActivity: false  // 租送活动
      }
    })

    // 每个饰品独立的价格表单：短租/长租/押金
    const itemFormMap = reactive({})

    // 从 initData 解析交易方式
    const tradeMethods = computed(() => {
      if (!props.initData?.tradingMethodDTOList) {
        return [
          { id: '2', name: '租赁', type: 1 },
          { id: '3', name: '可租可售', type: 2 }
        ]
      }
      // 过滤掉"出售"选项,只保留租赁相关
      return props.initData.tradingMethodDTOList
        .filter(item => item.tradingMethodType !== 0)
        .map(item => ({
          id: item.tradingMethodId,
          name: item.tradingMethodName,
          type: item.tradingMethodType
        }))
    })

    // 从 initData 解析出租天数选项
    const rentDaysOptions = computed(() => {
      return props.initData?.leaseDayList || [8, 15, 30]
    })

    // 获取第一个饰品的配置信息
    const firstItemConfig = computed(() => {
      if (!props.items || props.items.length === 0 || !props.initData) {
        return null
      }
      const firstItem = props.items[0]
      const hashName = firstItem.steam_hash_name || firstItem.name

      return {
        coefficient: props.initData.coefficientMap?.[hashName],
        zeroRent: props.initData.zeroRentMap?.[hashName],
        depositProtect: props.initData.depositProtectFeeConfigMap?.[hashName],
        enableZeroCD: props.initData.zeroCDRentSupportTempateMap?.[hashName]
      }
    })

    // 最小/最大租赁天数
    const minRentDays = computed(() => {
      return firstItemConfig.value?.coefficient?.minRentDays || 8
    })

    const maxRentDays = computed(() => {
      return firstItemConfig.value?.coefficient?.maxRentDays || 100
    })

    // 租金提示
    const rentPriceTip = computed(() => {
      return firstItemConfig.value?.zeroRent?.activityRentDesc || '租金<=0.89更快出租'
    })

    // 押金提示
    const depositTip = computed(() => {
      return firstItemConfig.value?.zeroRent?.activityDepositDesc || '押金<=1299，优先展示'
    })

    // 服务费率
    const serviceFeeRate = computed(() => {
      const rate = firstItemConfig.value?.depositProtect?.rate
      return rate ? (rate * 100).toFixed(0) : '25'
    })

    const vipServiceFeeRate = computed(() => {
      const vipRate = firstItemConfig.value?.depositProtect?.vipRate
      return vipRate ? (vipRate * 100).toFixed(0) : null
    })

    // 检测赔付文本中是否有删除线（表示有折扣活动）
    const hasStrikethrough = computed(() => {
      if (!compensationRichText.value) {
        return false
      }
      // 检查HTML中是否包含 text-decoration: line-through
      return compensationRichText.value.includes('text-decoration: line-through')
    })

    // 是否可以启用0CD出租（需要同时满足：后端支持 + 有折扣活动）
    const canEnableZeroCD = computed(() => {
      return hasStrikethrough.value && firstItemConfig.value?.enableZeroCD === true
    })

    // 租送活动
    const rentActivities = computed(() => {
      if (!props.initData?.activityCustomConfigDTOList) {
        return []
      }
      return props.initData.activityCustomConfigDTOList.filter(
        activity => activity.activityType === 0 && activity.activityStatus === 0
      )
    })

    const rentActivityDesc = computed(() => {
      if (rentActivities.value.length === 0) {
        return ''
      }
      const activity = rentActivities.value[0]
      if (activity.activityItemList && activity.activityItemList.length > 0) {
        return activity.activityItemList.map(item => item.itemDesc).join('、')
      }
      return activity.activityDesc || ''
    })

    // 初始化表单数据（全局 + 每个饰品）
    const initForms = () => {
      // 全局租期默认值
      if (rentDaysOptions.value.length > 0) {
        formData.rentDays = rentDaysOptions.value[0]
      }

      // 初始化每个饰品的价格表单
      if (props.items && props.items.length > 0) {
        props.items.forEach((item) => {
          if (!itemFormMap[item.assetid]) {
            itemFormMap[item.assetid] = {
              shortRentPrice: '',
              longRentPrice: '',
              depositPrice: ''
            }
          }
        })
      }
    }

    // 获取赔付文本
    const fetchCompensationText = async () => {
      console.log('[DEBUG] fetchCompensationText called')
      console.log('[DEBUG] props.items:', props.items)
      console.log('[DEBUG] props.steamId:', props.steamId)

      if (!props.items || props.items.length === 0) {
        console.log('[DEBUG] No items, returning early')
        return
      }

      try {
        // 使用第一个饰品的数据
        const firstItem = props.items[0]
        console.log('[DEBUG] firstItem:', firstItem)

        // 构建itemInfo
        const itemInfo = {
          abrade: String(firstItem.weapon_float || firstItem.float || '0'),
          leaseType: formData.tradeMode === 1 ? 0 : 1,  // 0=租赁, 1=可租可售
          marketHashName: firstItem.steam_hash_name || firstItem.name,
          marketPrice: String(firstItem.yyyp_Price || firstItem.weapon_classID?.yyyp_Price || '0'),
          pageSourceType: 10,
          paintSeed: parseInt(firstItem.paintseed || 0),
          steamAssetId: parseInt(firstItem.assetid || 0),
          supportEasyCompensation: false,
          templateId: parseInt(firstItem.weapon_classID?.yyyp_id || 0)
        }
        console.log('[DEBUG] itemInfo:', itemInfo)

        const requestBody = {
          steamId: props.steamId || '',
          itemInfo: itemInfo
        }
        console.log('[DEBUG] Request body:', requestBody)

        const apiUrl = `${window.location.origin.replace('9003', '9005')}/youping898SpiderV1/getCompensationText`
        console.log('[DEBUG] API URL:', apiUrl)

        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        })

        console.log('[DEBUG] Response status:', response.status)
        const result = await response.json()
        console.log('[DEBUG] Response result:', result)

        if (result.success && result.data) {
          // 使用富文本HTML
          const richContent = result.data.compensationRichContent
          console.log('[DEBUG] Rich content:', richContent)
          if (richContent) {
            compensationRichText.value = richContent
            console.log('[DEBUG] Compensation text set successfully')
          }
        } else {
          console.log('[DEBUG] Response not successful or no data')
        }
      } catch (error) {
        console.error('[DEBUG] Error in fetchCompensationText:', error)
        // 失败时保留默认值
      }
    }

    watch(
      () => [props.initData, props.items],
      (newVal, oldVal) => {
        console.log('[DEBUG] Watch triggered')
        console.log('[DEBUG] New initData:', newVal[0])
        console.log('[DEBUG] New items:', newVal[1])
        console.log('[DEBUG] Old initData:', oldVal?.[0])
        console.log('[DEBUG] Old items:', oldVal?.[1])

        initForms()

        // 直接从 initData 中获取赔付文本（已在 handleRentPlatformSelect 中预加载）
        if (props.initData?.compensationRichContent) {
          compensationRichText.value = props.initData.compensationRichContent
          console.log('[DEBUG] 从 initData 加载赔付文本:', props.initData.compensationRichContent)

          // 检测是否有删除线，如果有则自动开启0CD
          if (hasStrikethrough.value && firstItemConfig.value?.enableZeroCD === true) {
            formData.services.zeroCooldown = true
            console.log('[DEBUG] 检测到折扣活动，自动开启0CD')
          } else {
            formData.services.zeroCooldown = false
            console.log('[DEBUG] 无折扣活动或不支持0CD，禁用0CD')
          }
        } else {
          // 如果 initData 中没有，则尝试请求API（降级方案）
          console.log('[DEBUG] initData 中没有赔付文本，尝试请求API')
          fetchCompensationText()
        }
      },
      { immediate: true, deep: true }
    )

    // 切换服务选项
    const toggleService = (serviceName) => {
      formData.services[serviceName] = !formData.services[serviceName]
    }

    // 处理图片加载错误
    const handleImageError = (e) => {
      e.target.style.display = 'none'
    }

    // 处理取消
    const handleCancel = () => {
      emit('cancel')
    }

    // 处理提交
    const handleSubmit = () => {
      // 验证表单
      if (!validateForm()) {
        return
      }

      // 准备提交数据（全局配置 + 每个饰品的独立价格）
      const submitData = {
        tradeMode: formData.tradeMode,
        rentDays: formData.rentDays === 'custom' ? formData.customDays : formData.rentDays,
        services: formData.services,
        items: props.items.map((item) => ({
          assetid: item.assetid,
          steam_hash_name: item.steam_hash_name,
          shortRentPrice: parseFloat(itemFormMap[item.assetid].shortRentPrice),
          longRentPrice: itemFormMap[item.assetid].longRentPrice
            ? parseFloat(itemFormMap[item.assetid].longRentPrice)
            : null,
          depositPrice: parseFloat(itemFormMap[item.assetid].depositPrice)
        }))
      }

      emit('submit', submitData)
    }

    // 表单验证
    const validateForm = () => {
      // 验证租赁天数
      if (formData.rentDays === 'custom') {
        if (!formData.customDays || formData.customDays <= 0) {
          ElMessage.warning('请输入有效的租赁天数')
          return false
        }
        if (formData.customDays < minRentDays.value || formData.customDays > maxRentDays.value) {
          ElMessage.warning(`租赁天数必须在 ${minRentDays.value}-${maxRentDays.value} 之间`)
          return false
        }
      }

      // 验证每个饰品的价格配置
      const minRent = firstItemConfig.value?.coefficient?.minRent
      const maxRent = firstItemConfig.value?.coefficient?.maxRent
      const minDeposit = firstItemConfig.value?.coefficient?.minDeposit
      const maxDeposit = firstItemConfig.value?.coefficient?.maxDeposit

      for (const item of props.items || []) {
        const itemForm = itemFormMap[item.assetid]
        if (!itemForm) continue

        // 短租租金必填
        if (!itemForm.shortRentPrice || itemForm.shortRentPrice === '') {
          ElMessage.warning(`【${item.name}】请输入短租租金`)
          return false
        }
        const shortRent = parseFloat(itemForm.shortRentPrice)
        if (isNaN(shortRent) || shortRent <= 0) {
          ElMessage.warning(`【${item.name}】请输入有效的短租租金`)
          return false
        }
        if (minRent && shortRent < parseFloat(minRent)) {
          ElMessage.warning(`【${item.name}】租金不能低于 ¥${minRent}/天`)
          return false
        }
        if (maxRent && shortRent > parseFloat(maxRent)) {
          ElMessage.warning(`【${item.name}】租金不能高于 ¥${maxRent}/天`)
          return false
        }

        // 押金必填
        if (!itemForm.depositPrice || itemForm.depositPrice === '') {
          ElMessage.warning(`【${item.name}】请输入商品押金`)
          return false
        }
        const deposit = parseFloat(itemForm.depositPrice)
        if (isNaN(deposit) || deposit <= 0) {
          ElMessage.warning(`【${item.name}】请输入有效的押金`)
          return false
        }
        if (minDeposit && deposit < parseFloat(minDeposit)) {
          ElMessage.warning(`【${item.name}】押金不能低于 ¥${minDeposit}`)
          return false
        }
        if (maxDeposit && deposit > parseFloat(maxDeposit)) {
          ElMessage.warning(`【${item.name}】押金不能高于 ¥${maxDeposit}`)
          return false
        }
      }

      return true
    }

    // 本地回退的一键定价逻辑（按购入价简单估算）
    const localAutoPricingFallback = () => {
      if (!props.items || props.items.length === 0) {
        ElMessage.warning('没有可定价的饰品')
        return 0
      }

      let successCount = 0

      props.items.forEach((item) => {
        const itemForm = itemFormMap[item.assetid]
        if (!itemForm) return

        const buyPrice = parseFloat(item.buyPrice || item.buy_price || 0)
        if (buyPrice > 0) {
          const shortRent = (buyPrice * 0.015).toFixed(2)
          itemForm.shortRentPrice = shortRent

          const longRent = (parseFloat(shortRent) * 0.8).toFixed(2)
          itemForm.longRentPrice = longRent

          const deposit = (buyPrice * 1.05).toFixed(2)
          itemForm.depositPrice = deposit

          successCount++
        }
      })

      return successCount
    }

    // 一键定价功能：优先调用后端自动定价接口，失败时回退到本地估算
    const handleAutoPricing = async () => {
      if (!props.items || props.items.length === 0) {
        ElMessage.warning('没有可定价的饰品')
        return
      }

      // 收集 steam_hash_name -> assetid 列表
      const hashNameSet = new Set()
      const hashToAssetIds = {}
      props.items.forEach(item => {
        const hashName = item.steam_hash_name || item.name
        if (!hashName) return
        hashNameSet.add(hashName)
        if (!hashToAssetIds[hashName]) {
          hashToAssetIds[hashName] = []
        }
        hashToAssetIds[hashName].push(item.assetid)
      })

      const steamHashNames = Array.from(hashNameSet)
      if (!steamHashNames.length) {
        ElMessage.warning('选中的饰品缺少 steam_hash_name，无法调用自动定价，将使用本地估算')
        const localCount = localAutoPricingFallback()
        if (localCount > 0) {
          ElMessage.success(`已为 ${localCount} 件饰品按购入价估算定价`)
        }
        return
      }

      autoPricingLoading.value = true
      try {
        const resp = await fetch(apiUrls.yyypRentAutoPricing(), {
          method: 'POST',
          mode: 'cors',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            steamId: props.steamId || '',
            steam_hash_name: steamHashNames
          })
        })

        if (!resp.ok) {
          throw new Error(`HTTP ${resp.status}`)
        }

        const result = await resp.json()
        if (!result.success) {
          ElMessage.error(result.message || '自动定价失败，将使用本地估算')
          const localCount = localAutoPricingFallback()
          if (localCount > 0) {
            ElMessage.success(`已为 ${localCount} 件饰品按购入价估算定价`)
          }
          return
        }

        const data = result.data || {}
        const pricingList = data.pricingInfoVos || []
        if (!pricingList.length) {
          ElMessage.warning('自动定价成功，但未返回任何定价数据，将使用本地估算')
          const localCount = localAutoPricingFallback()
          if (localCount > 0) {
            ElMessage.success(`已为 ${localCount} 件饰品按购入价估算定价`)
          }
          return
        }

        // 构建 commodityHashName -> 定价信息 映射
        const priceMap = {}
        pricingList.forEach(p => {
          if (!p.commodityHashName) return
          priceMap[p.commodityHashName] = {
            price: p.price,
            shortLeaseUnitPrice: p.shortLeaseUnitPrice,
            longLeaseUnitPrice: p.longLeaseUnitPrice,
            leaseDeposit: p.leaseDeposit,
            leaseMaxDays: p.leaseMaxDays
          }
        })

        let successCount = 0
        // 将定价结果写入每个饰品对应的表单
        Object.entries(hashToAssetIds).forEach(([hashName, assetIds]) => {
          const pricing = priceMap[hashName]
          if (!pricing) return

          assetIds.forEach(assetid => {
            const itemForm = itemFormMap[assetid]
            if (!itemForm) return

            const shortRent = parseFloat(pricing.shortLeaseUnitPrice || pricing.price || 0)
            const longRent = parseFloat(pricing.longLeaseUnitPrice || 0)
            const deposit = parseFloat(pricing.leaseDeposit || 0)

            if (shortRent > 0) {
              itemForm.shortRentPrice = shortRent.toFixed(2)
            }
            if (longRent > 0) {
              itemForm.longRentPrice = longRent.toFixed(2)
            }
            if (deposit > 0) {
              itemForm.depositPrice = deposit.toFixed(2)
            }

            successCount++
          })
        })

        if (successCount > 0) {
          ElMessage.success(`已为 ${successCount} 件饰品完成悠悠有品自动定价`)
        } else {
          ElMessage.warning('未能为当前饰品匹配到定价数据，将使用本地估算')
          const localCount = localAutoPricingFallback()
          if (localCount > 0) {
            ElMessage.success(`已为 ${localCount} 件饰品按购入价估算定价`)
          }
        }
      } catch (e) {
        console.error('悠悠有品自动定价接口异常:', e)
        ElMessage.error(`自动定价失败: ${e.message}，将使用本地估算`)
        const localCount = localAutoPricingFallback()
        if (localCount > 0) {
          ElMessage.success(`已为 ${localCount} 件饰品按购入价估算定价`)
        }
      } finally {
        autoPricingLoading.value = false
      }
    }

    return {
      formData,
      itemFormMap,
      tradeMethods,
      rentDaysOptions,
      minRentDays,
      maxRentDays,
      rentPriceTip,
      depositTip,
      serviceFeeRate,
      vipServiceFeeRate,
      compensationRichText,
      hasStrikethrough,
      canEnableZeroCD,
      rentActivities,
      rentActivityDesc,
      toggleService,
      handleImageError,
      handleCancel,
      handleSubmit,
      handleAutoPricing,
      autoPricingLoading
    }
  }
}
</script>

<style scoped>
.rent-form-yyyp {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 70vh;
  background: #1a1a1a;
  color: #fff;
}

/* 表单头部 */
.form-header {
  padding: 1rem 1.5rem;
  background: #2a2a2a;
  border-bottom: 1px solid #3a3a3a;
}

.form-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-count {
  font-size: 1.2rem;
  font-weight: bold;
  color: #fff;
}

/* 表单内容 */
.form-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

/* 饰品列表 */
.items-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 50vh;
  overflow-y: auto;
  padding: 0.5rem;
  background: #0a0a0a;
  border-radius: 8px;
}

.item-card {
  display: grid;
  grid-template-columns: 4fr 6fr;
  gap: 1rem;
  padding: 0.75rem;
  background: #2a2a2a;
  border: 1px solid #3a3a3a;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.item-card:hover {
  background: #333;
  border-color: #4a4a4a;
}

/* 左侧饰品信息盒子 */
.item-left-box {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

/* 右侧输入框盒子 */
.item-right-box {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  align-items: center;
}

.item-image {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.item-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.image-placeholder {
  color: #666;
  font-size: 0.75rem;
}

.item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.item-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: #fff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-float-text {
  font-size: 0.85rem;
  color: #999;
  font-family: monospace;
}

/* 磨损进度条样式 - 与Inventory页面一致 */
.float-bar {
  position: relative;
  height: 8px;
  display: flex;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.float-segment {
  height: 100%;
  transition: opacity 0.2s;
}

.float-segment:hover {
  opacity: 0.8;
}

/* CS2 标准磨损等级颜色 */
.float-segment.fn {
  flex: 7;  /* 0.00 - 0.07 */
  background: linear-gradient(to right, #4CAF50, #66BB6A);
}

.float-segment.mw {
  flex: 8;  /* 0.07 - 0.15 */
  background: linear-gradient(to right, #8BC34A, #9CCC65);
}

.float-segment.ft {
  flex: 23; /* 0.15 - 0.38 */
  background: linear-gradient(to right, #FFC107, #FFB300);
}

.float-segment.ww {
  flex: 7;  /* 0.38 - 0.45 */
  background: linear-gradient(to right, #FF9800, #FB8C00);
}

.float-segment.bs {
  flex: 55; /* 0.45 - 1.00 */
  background: linear-gradient(to right, #F44336, #E53935);
}

/* 磨损值指针 */
.float-pointer {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 3px;
  height: 16px;
  background: #fff;
  border-radius: 2px;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.5), 0 0 8px rgba(255, 255, 255, 0.8);
  z-index: 10;
  pointer-events: none;
  transition: all 0.2s ease;
}

.float-pointer::before {
  content: '';
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid #fff;
}

.float-pointer::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 5px solid #fff;
}

.item-buy-price {
  font-size: 0.85rem;
  color: #4CAF50;
  font-weight: 500;
  font-family: monospace;
}

.item-form-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field-label {
  font-size: 0.8rem;
  color: #ccc;
}

/* 表单区块 */
.form-section {
  margin-bottom: 1.5rem;
}

.section-label {
  font-size: 0.95rem;
  color: #ccc;
  margin-bottom: 0.75rem;
  font-weight: 500;
}

/* 交易方式按钮 */
.trade-mode-buttons {
  display: flex;
  gap: 1rem;
}

/* 顶部 行：交易方式 + 押金赔付 + 增值服务 */
.trade-and-services-row {
  display: grid;
  grid-template-columns: 2fr 2fr 1.5fr;
  gap: 1rem;
  align-items: stretch;
}

.trade-mode-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* 顶部三块统一卡片样式 */
.trade-card {
  padding: 1rem;
  background: #2a2a2a;
  border: 2px solid #3a3a3a;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100%;
}

/* 押金赔付卡片：图标与文本同一行显示 */
.deposit-card {
  flex-direction: row;
  align-items: center;
  gap: 0.75rem;
}

.trade-mode-btn {
  flex: 1;
  padding: 1rem;
  background: #2a2a2a;
  border: 2px solid #3a3a3a;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.trade-mode-btn:hover {
  background: #333;
  border-color: #4a4a4a;
}

.trade-mode-btn.active {
  background: rgba(64, 158, 255, 0.1);
  border-color: #409EFF;
}

.mode-label {
  font-size: 1rem;
  font-weight: 500;
  color: #fff;
}

/* 出租天数按钮 */
.rent-days-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.rent-day-btn {
  padding: 0.75rem;
  background: #2a2a2a;
  border: 2px solid #3a3a3a;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.rent-day-btn:hover {
  background: #333;
  border-color: #4a4a4a;
}

.rent-day-btn.active {
  background: rgba(64, 158, 255, 0.1);
  border-color: #409EFF;
}

.day-label {
  font-size: 0.95rem;
  font-weight: 500;
  color: #fff;
}

/* 自定义天数输入框 */
.rent-day-input-wrapper {
  display: flex;
  align-items: center;
}

.custom-days-inline-input {
  width: 100%;
}

.custom-days-inline-input :deep(.el-input__wrapper) {
  background-color: #2a2a2a;
  border: 2px solid #3a3a3a;
  box-shadow: none;
  border-radius: 8px;
  padding: 0.75rem;
  transition: all 0.3s ease;
}

.custom-days-inline-input :deep(.el-input__wrapper:hover) {
  background: #333;
  border-color: #4a4a4a;
}

.custom-days-inline-input :deep(.el-input__wrapper.is-focus) {
  background: rgba(64, 158, 255, 0.1);
  border-color: #409EFF;
}

.custom-days-inline-input :deep(.el-input__inner) {
  color: #fff;
  font-size: 0.95rem;
  font-weight: 500;
  text-align: center;
}

/* 隐藏数字输入框的上下箭头 */
.custom-days-inline-input :deep(.el-input__inner)::-webkit-outer-spin-button,
.custom-days-inline-input :deep(.el-input__inner)::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.custom-days-inline-input :deep(.el-input__inner[type="number"]) {
  -moz-appearance: textfield;
}

.custom-days-inline-input :deep(.el-input__inner::placeholder) {
  color: #999;
  font-weight: 500;
}

.custom-days-inline-input :deep(.el-input__suffix) {
  display: flex;
  align-items: center;
}

.input-suffix {
  color: #999;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

/* 输入框带提示 */
.input-with-tips {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.price-input {
  width: 100%;
}

.input-tip {
  font-size: 0.85rem;
  color: #999;
  padding-left: 0.25rem;
}

.compensation-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-badge {
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff;
}

.compensation-content {
  flex: 1;
}

.compensation-text {
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 0.25rem;
}

/* 确保富文本中的内联样式能够正确显示 */
.compensation-text span {
  display: inline;
}

/* 删除线样式 */
.compensation-text span[style*="text-decoration: line-through"] {
  text-decoration: line-through !important;
}

.service-fee {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.fee-value {
  font-size: 1rem;
  font-weight: bold;
  color: #fff;
}

.fee-value.highlight {
  color: #f56c6c;
}

.fee-original {
  font-size: 0.85rem;
  color: #999;
  text-decoration: line-through;
}

.compensation-arrow {
  font-size: 1.5rem;
  color: #666;
}

/* 增值服务 */
.value-added-services {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.value-added-inline {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  justify-content: center;
}

.service-item-inline {
  display: flex;
  align-items: center;
}

.service-switch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  transition: all 0.3s ease;
}

.service-switch-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

/* 禁用状态样式 */
.service-switch-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(255, 255, 255, 0.02);
}

.service-switch-item.disabled:hover {
  background: rgba(255, 255, 255, 0.02);
}

.service-switch-item.disabled .service-badge {
  opacity: 0.6;
}

.service-switch-item .service-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.services-title {
  font-size: 0.9rem;
  color: #ccc;
  margin-bottom: 0.5rem;
}

.service-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #2a2a2a;
  border: 2px solid #3a3a3a;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.service-item:hover {
  background: #333;
  border-color: #4a4a4a;
}

.service-checkbox {
  flex-shrink: 0;
}

.service-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.service-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
}

.service-badge.zero-cd {
  background: linear-gradient(135deg, #409EFF, #3A8EE6);
}

.service-badge.rent-activity {
  background: linear-gradient(135deg, #67C23A, #85CE61);
}

.service-label {
  font-size: 0.9rem;
  color: #fff;
}

/* 底部操作栏 */
.form-footer {
  display: flex;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: #2a2a2a;
  border-top: 1px solid #3a3a3a;
}

.footer-btn {
  flex: 1;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
}

.auto-price-btn {
  background: linear-gradient(135deg, #67C23A, #85CE61);
  color: #fff;
  border: none;
}

.auto-price-btn:hover {
  background: linear-gradient(135deg, #85CE61, #67C23A);
  opacity: 0.9;
}

.cancel-btn {
  background: #3a3a3a;
  color: #fff;
  border: none;
}

.cancel-btn:hover {
  background: #4a4a4a;
}

.submit-btn {
  background: linear-gradient(135deg, #409EFF, #3A8EE6);
  border: none;
}

.submit-btn:hover {
  opacity: 0.9;
}

/* 滚动条样式 */
.form-content::-webkit-scrollbar,
.items-list::-webkit-scrollbar {
  width: 6px;
}

.form-content::-webkit-scrollbar-track,
.items-list::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.form-content::-webkit-scrollbar-thumb,
.items-list::-webkit-scrollbar-thumb {
  background: #3a3a3a;
  border-radius: 3px;
}

.form-content::-webkit-scrollbar-thumb:hover,
.items-list::-webkit-scrollbar-thumb:hover {
  background: #4a4a4a;
}

/* Element Plus 样式覆盖 */
:deep(.el-input__wrapper) {
  background-color: #2a2a2a;
  border: 2px solid #3a3a3a;
  box-shadow: none;
  border-radius: 8px;
  padding: 0.75rem;
}

:deep(.el-input__wrapper:hover) {
  border-color: #4a4a4a;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #409EFF;
}

:deep(.el-input__inner) {
  color: #fff;
  font-size: 1rem;
}

:deep(.el-input-group__prepend),
:deep(.el-input-group__append) {
  background-color: #1a1a1a;
  color: #fff;
  border: none;
  padding: 0 1rem;
}

:deep(.el-checkbox__inner) {
  background-color: #2a2a2a;
  border-color: #3a3a3a;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #409EFF;
  border-color: #409EFF;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .rent-days-buttons {
    grid-template-columns: repeat(2, 1fr);
  }

  .trade-mode-buttons {
    flex-direction: column;
  }

  .form-content {
    padding: 1rem;
  }

  .form-footer {
    padding: 1rem;
  }

  .items-list {
    max-height: 150px;
  }

  .item-card {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .item-image {
    width: 60px;
    height: 60px;
  }
  
  .trade-and-services-row {
    grid-template-columns: 1fr;
  }
  
  .item-right-box {
    grid-template-columns: 1fr;
  }
}
</style>
