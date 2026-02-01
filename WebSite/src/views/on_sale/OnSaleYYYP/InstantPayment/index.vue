<template>
  <div class="card-container">
    <div v-loading="loading" class="card-grid">
      <div
        v-for="item in instantPaymentItems"
        :key="item.order_no"
        class="inventory-card"
      >
        <div class="card-image">
          <img
            v-if="item.commodity_icon_url"
            :src="item.commodity_icon_url"
            :alt="item.commodity_name"
            class="weapon-image"
            @error="(e) => e.target.style.display = 'none'"
          />
          <div v-else class="image-placeholder">
            <span>无图片</span>
          </div>
          <!-- 状态标签 - 左上角 -->
          <div class="status-overlay" :class="{
            'status-guarding': item.guard_status === 1
          }">
            {{ item.guard_status_text || '未知状态' }}
          </div>
          <!-- 贴纸覆盖层 - 左下角 -->
          <div v-if="item.sticker_list && item.sticker_list.length > 0" class="sticker-overlay">
            <div
              v-for="(sticker, index) in item.sticker_list"
              :key="index"
              class="sticker-item-overlay"
              :title="sticker.name || '未知贴纸'"
            >
              <img
                v-if="sticker.imgUrl"
                :src="sticker.imgUrl"
                :alt="sticker.name"
                class="sticker-img-overlay"
                @error="(e) => e.target.style.display = 'none'"
              />
              <div v-else class="sticker-placeholder-overlay">?</div>
            </div>
          </div>
        </div>
        <div class="card-content">
          <div class="card-title" :title="item.commodity_name">
            {{ item.commodity_name }}
          </div>
          <div class="card-info">
            <!-- 磨损值显示条 -->
            <div class="float-bar-container" v-if="item.abrade">
              <div class="float-bar">
                <div class="float-segment fn" title="崭新出厂 (0.00 - 0.07)"></div>
                <div class="float-segment mw" title="略有磨损 (0.07 - 0.15)"></div>
                <div class="float-segment ft" title="久经沙场 (0.15 - 0.38)"></div>
                <div class="float-segment ww" title="破损不堪 (0.38 - 0.45)"></div>
                <div class="float-segment bs" title="战痕累累 (0.45 - 1.00)"></div>
                <div
                  class="float-pointer"
                  :style="{ left: `${parseFloat(item.abrade) * 100}%` }"
                  :title="`磨损值: ${item.abrade}`"
                ></div>
              </div>
            </div>
            <div class="float-value" v-if="item.abrade">
              {{ item.abrade }}
            </div>
          </div>
          <div class="card-prices">
            <!-- 第一行：可提取金额 创建时间 -->
            <div class="price-row">
              <div class="price-group">
                <span class="price-label">可提取:</span>
                <span class="price-value sale-price">¥{{ item.remaining_retrieve_amount }}</span>
              </div>
              <div class="price-group" v-if="item.create_time">
                <span class="price-label">创建:</span>
                <span class="price-value" style="font-size: 0.65rem;">{{ item.create_time }}</span>
              </div>
            </div>
            <!-- 第二行:可交易余额 解冻金额 -->
            <div class="price-row">
              <div class="price-group" v-if="item.tradable_balance">
                <span class="price-label">可交易:</span>
                <span class="price-value">¥{{ item.tradable_balance }}</span>
              </div>
              <div class="price-group" v-if="item.unfreeze_amount">
                <span class="price-label">解冻:</span>
                <span class="price-value" style="color: #FFA500;">¥{{ item.unfreeze_amount }}</span>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <div class="card-tags">
              <el-tag v-if="item.tip_content" type="warning" size="small" class="tip-tag">
                <span class="tag-icon">ℹ️</span>{{ formatTipContent(item.tip_content) }}
              </el-tag>
            </div>
            <div class="card-actions">
              <el-button
                size="small"
                type="primary"
                :disabled="item.fund_status !== 1"
                @click="handleExtract(item)"
              >
                {{ item.fund_status === 1 ? '提取' : item.fund_status_text }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="table-footer">
      <span>共 {{ instantPaymentItems.length }} 条数据</span>
      <span v-if="statistics.totalAmount > 0" style="margin-left: 2rem;">
        总可提取金额: <span style="color: #4CAF50; font-weight: bold;">¥{{ statistics.totalAmount }}</span>
      </span>
      <span v-if="statistics.tradableBalance > 0" style="margin-left: 2rem;">
        总可交易余额: <span style="color: #409EFF; font-weight: bold;">¥{{ statistics.tradableBalance }}</span>
      </span>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

export default {
  name: 'InstantPayment',
  props: {
    steamId: {
      type: String,
      required: true
    }
  },
  emits: ['update:count'],
  setup(props, { emit }) {
    const loading = ref(false)
    const instantPaymentItems = ref([])

    // 统计信息
    const statistics = computed(() => {
      const itemCount = instantPaymentItems.value.length
      const totalAmount = instantPaymentItems.value.reduce((sum, item) => {
        return sum + parseFloat(item.remaining_retrieve_amount || 0)
      }, 0)
      const tradableBalance = instantPaymentItems.value.reduce((sum, item) => {
        return sum + parseFloat(item.tradable_balance || 0)
      }, 0)

      return {
        itemCount,
        totalAmount: totalAmount.toFixed(2),
        tradableBalance: tradableBalance.toFixed(2)
      }
    })

    // 加载数据
    const loadData = async () => {
      if (!props.steamId) {
        return
      }

      loading.value = true
      try {
        const response = await axios.post(apiUrls.yyypGetInstantPaymentList(), {
          steamId: props.steamId,
          pageIndex: 1,
          pageSize: 100,
          fundStatus: 1
        })

        if (response.data && response.data.success) {
          const data = response.data.data || {}
          const responseList = data.responseList || []

          // 转换数据格式
          instantPaymentItems.value = responseList.map(item => {
            // 获取第一个商品信息
            const commodity = item.commodityInfoList?.[0] || {}

            return {
              order_no: item.orderNo,
              order_fulfill_guard_no: item.orderFulfillGuardNo,
              unfreeze_amount: item.unfreezeAmount,
              create_time: item.createTime,
              guard_status: item.guardStatus,
              fund_status: item.fundStatus,
              guard_status_text: item.guardStatusText,
              fund_status_text: item.fundStatusText,
              tip_content: item.tipContent,
              remaining_retrieve_amount: item.remainingRetrieveAmount,
              tradable_balance: item.tradableBalance,
              auto_retrieve: item.autoRetrieve,

              // 商品信息
              commodity_name: commodity.commodityName,
              commodity_icon_url: commodity.commodityIconUrl,
              abrade: commodity.abrade,
              paint_index: commodity.paintIndex,
              paint_seed: commodity.paintSeed,
              exterior_name: commodity.exteriorName,
              rarity_name: commodity.rarityName,
              sticker_list: commodity.stickerList || []
            }
          })

          const totalCount = instantPaymentItems.value.length
          ElMessage.success(`加载成功，共 ${totalCount} 个秒到账订单`)

          // 发送数量给父组件
          emit('update:count', totalCount)
        } else {
          ElMessage.error(response.data?.message || '加载失败')
          emit('update:count', 0)
        }
      } catch (error) {
        console.error('加载0CD订单失败:', error)
        ElMessage.error('加载失败: ' + (error.response?.data?.message || error.message))
      } finally {
        loading.value = false
      }
    }

    // 格式化提示内容 - 缩短显示
    const formatTipContent = (content) => {
      if (!content) return ''
      // 提取日期信息，例如 "冻结资金将于 2026.02.08 16:00 后开始解冻" -> "2026.02.08解冻"
      const match = content.match(/(\d{4}\.\d{2}\.\d{2})/)
      if (match) {
        return `${match[1]}解冻`
      }
      return content.length > 20 ? content.substring(0, 20) + '...' : content
    }

    // 提取资金
    const handleExtract = (item) => {
      ElMessage.info('提取功能暂未实现')
    }

    // 监听steamId变化
    watch(() => props.steamId, (newValue) => {
      if (newValue) {
        loadData()
      }
    }, { immediate: true })

    return {
      loading,
      instantPaymentItems,
      statistics,
      loadData,
      handleExtract,
      formatTipContent
    }
  }
}
</script>

<style scoped>
/* 卡片网格样式 */
.card-container {
  margin-top: 1rem;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.inventory-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  overflow: visible;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  min-height: 340px;
  height: auto;
}

.inventory-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.card-image {
  position: relative;
  width: 100%;
  height: 150px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* 主武器图片 - 固定尺寸不压缩 */
.card-image .weapon-image {
  width: 180px;
  height: 120px;
  object-fit: contain;
}

.image-placeholder {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* 贴纸覆盖层 */
.sticker-overlay {
  position: absolute;
  bottom: 8px;
  left: 8px;
  display: flex;
  gap: 4px;
  z-index: 2;
}

.sticker-item-overlay {
  width: 32px;
  height: 32px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

/* 印花图片 - 保持缩放样式 */
.sticker-img-overlay {
  max-width: 28px;
  max-height: 28px;
  object-fit: contain;
}

.sticker-placeholder-overlay {
  color: #999;
  font-size: 12px;
}

/* 状态覆盖层 - 左上角 */
.status-overlay {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 4px 8px;
  background: rgba(76, 175, 80, 0.9);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 4px;
  backdrop-filter: blur(4px);
  z-index: 3;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  white-space: nowrap;
}

.status-overlay.status-guarding {
  background: rgba(255, 165, 0, 0.9);
}

/* 卡片内容 */
.card-content {
  padding: 0.75rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-title {
  font-size: 0.8rem;
  font-weight: bold;
  color: #fff;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.3;
  min-height: 2.6em;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.75rem;
}

/* 磨损值显示条 */
.float-bar-container {
  margin-top: 0.3rem;
  padding: 0;
  margin-bottom: 0;
}

.float-bar {
  position: relative;
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
  display: flex;
}

.float-segment {
  flex: 1;
  height: 100%;
}

.float-segment.fn {
  background: #4CAF50;
  flex: 0.07;
}

.float-segment.mw {
  background: #8BC34A;
  flex: 0.08;
}

.float-segment.ft {
  background: #FFC107;
  flex: 0.23;
}

.float-segment.ww {
  background: #FF9800;
  flex: 0.07;
}

.float-segment.bs {
  background: #F44336;
  flex: 0.55;
}

.float-pointer {
  position: absolute;
  top: -2px;
  width: 2px;
  height: 10px;
  background: #fff;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.5);
  transform: translateX(-50%);
  z-index: 1;
}

.float-value {
  text-align: left;
  font-size: 0.75rem;
  color: #ccc;
  font-family: monospace;
  margin-top: 0.2rem;
  margin-bottom: 0;
  font-weight: 500;
}

/* 价格显示 */
.card-prices {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.3rem;
  padding-top: 0;
  border-top: none;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  gap: 0.5rem;
}

.price-group {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
}

.price-label {
  color: #999;
  font-size: 0.7rem;
  white-space: nowrap;
}

.price-value {
  color: #fff;
  font-weight: bold;
  font-size: 0.75rem;
}

.sale-price {
  color: #4CAF50;
}

/* 卡片底部 */
.card-footer {
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  min-height: 28px;
}

.tip-tag {
  max-width: 100%;
  font-size: 0.65rem;
}

.tag-icon {
  margin-right: 0.25rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.card-actions .el-button {
  flex: 1;
}

.table-footer {
  margin-top: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }

  .inventory-card {
    min-height: 320px;
  }
}
</style>
