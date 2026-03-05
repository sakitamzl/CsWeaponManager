<template>
  <div class="favorite-container">
    <div class="favorite-layout">

      <!-- 左：皮肤关注 -->
      <div class="favorite-section">
        <div class="favorite-header">
          <div class="header-left">
            <h3>皮肤关注
              <span class="favorite-count">{{ skinList.length }} 个</span>
            </h3>
          </div>
          <div class="header-actions">
            <el-input
              v-model="skinSearch"
              placeholder="搜索皮肤名称..."
              size="small"
              clearable
              class="favorite-search"
            />
          </div>
        </div>

        <div class="favorite-content">
          <div
            v-for="item in filteredSkinList"
            :key="item.id"
            class="favorite-item"
          >
            <!-- 左：图片 -->
            <div class="favorite-item-image">
              <img
                v-if="item.icon_url"
                :src="item.icon_url"
                :alt="item.name"
                class="favorite-weapon-image"
                @error="(e) => e.target.style.display = 'none'"
              />
              <div v-else class="favorite-image-placeholder">无图</div>
            </div>

            <!-- 中：信息 -->
            <div class="favorite-item-info">
              <div class="favorite-item-name">{{ item.name }}</div>
              <div class="favorite-item-tags">
                <el-tag v-if="item.exterior" size="small" type="info">{{ item.exterior }}</el-tag>
                <el-tag v-if="item.weapon_type" size="small" type="info">{{ item.weapon_type }}</el-tag>
                <el-tag
                  v-if="item.rarity"
                  size="small"
                  :style="{ color: item.rarity_color, borderColor: item.rarity_color }"
                >
                  {{ item.rarity }}
                </el-tag>
              </div>
              <div class="favorite-item-price-row">
                <span class="price-label">参考价:</span>
                <span class="price-value">¥{{ item.ref_price }}</span>
                <span class="price-label" style="margin-left: 1rem;">在售:</span>
                <span class="price-value sale-color">{{ item.on_sale_count }} 件</span>
              </div>
              <div class="favorite-item-price-row" v-if="item.lowest_price">
                <span class="price-label">最低价:</span>
                <span class="price-value highlight-color">¥{{ item.lowest_price }}</span>
              </div>
            </div>

            <!-- 右：操作 -->
            <div class="favorite-item-actions">
              <div class="price-trend" :class="getTrendClass(item.trend)">
                <span class="trend-icon">{{ getTrendIcon(item.trend) }}</span>
                <span class="trend-value">{{ item.trend_text }}</span>
              </div>
              <div class="action-buttons">
                <el-button size="small" type="primary" plain>查看</el-button>
                <el-button size="small" type="danger" plain>取消关注</el-button>
              </div>
            </div>
          </div>

          <div v-if="filteredSkinList.length === 0" class="empty-favorite">
            <el-empty description="暂无皮肤关注" />
          </div>
        </div>
      </div>

      <!-- 右：单件关注 -->
      <div class="favorite-section">
        <div class="favorite-header">
          <div class="header-left">
            <h3>单件关注
              <span class="favorite-count">{{ itemList.length }} 个</span>
            </h3>
          </div>
          <div class="header-actions">
            <el-select
              v-model="itemStatusFilter"
              placeholder="状态筛选"
              size="small"
              clearable
              class="favorite-filter"
            >
              <el-option label="在售" value="on_sale" />
              <el-option label="已售出" value="sold" />
              <el-option label="已下架" value="off_shelf" />
            </el-select>
            <el-input
              v-model="itemSearch"
              placeholder="搜索饰品名称..."
              size="small"
              clearable
              class="favorite-search"
            />
          </div>
        </div>

        <div class="favorite-content">
          <div
            v-for="item in filteredItemList"
            :key="item.id"
            class="favorite-item"
            :class="{ 'item-sold': item.status === 'sold', 'item-off': item.status === 'off_shelf' }"
          >
            <!-- 左：图片 + 状态角标 -->
            <div class="favorite-item-image">
              <img
                v-if="item.icon_url"
                :src="item.icon_url"
                :alt="item.name"
                class="favorite-weapon-image"
                @error="(e) => e.target.style.display = 'none'"
              />
              <div v-else class="favorite-image-placeholder">无图</div>
              <div class="item-status-badge" :class="getStatusBadgeClass(item.status)">
                {{ getStatusLabel(item.status) }}
              </div>
            </div>

            <!-- 中：信息 -->
            <div class="favorite-item-info">
              <div class="favorite-item-name">{{ item.name }}</div>
              <div class="favorite-item-tags">
                <el-tag v-if="item.exterior" size="small" type="info">{{ item.exterior }}</el-tag>
                <el-tag v-if="item.float_value" size="small">{{ item.float_value }}</el-tag>
                <el-tag
                  v-if="item.rarity"
                  size="small"
                  :style="{ color: item.rarity_color, borderColor: item.rarity_color }"
                >
                  {{ item.rarity }}
                </el-tag>
              </div>
              <!-- 磨损条 -->
              <div class="float-bar-container" v-if="item.float_value">
                <div class="float-bar">
                  <div class="float-segment fn"></div>
                  <div class="float-segment mw"></div>
                  <div class="float-segment ft"></div>
                  <div class="float-segment ww"></div>
                  <div class="float-segment bs"></div>
                  <div
                    class="float-pointer"
                    :style="{ left: `${parseFloat(item.float_value) * 100}%` }"
                  ></div>
                </div>
              </div>
              <div class="favorite-item-price-row">
                <span class="price-label">售价:</span>
                <span class="price-value sale-color">¥{{ item.sale_price }}</span>
                <span class="price-label" style="margin-left: 1rem;">参考:</span>
                <span class="price-value">¥{{ item.ref_price }}</span>
              </div>
              <div class="favorite-item-price-row">
                <span class="price-label">卖家:</span>
                <span class="seller-name">{{ item.seller }}</span>
              </div>
            </div>

            <!-- 右：操作 -->
            <div class="favorite-item-actions">
              <div class="item-add-time">
                <span class="time-label">关注时间</span>
                <span class="time-value">{{ item.follow_time }}</span>
              </div>
              <div class="action-buttons">
                <el-button size="small" type="primary" plain :disabled="item.status !== 'on_sale'">
                  查看
                </el-button>
                <el-button size="small" type="danger" plain>取消关注</el-button>
              </div>
            </div>
          </div>

          <div v-if="filteredItemList.length === 0" class="empty-favorite">
            <el-empty description="暂无单件关注" />
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'MyFavorite',
  props: {
    steamId: {
      type: String,
      required: true
    }
  },
  emits: ['update:count'],
  setup() {
    const skinSearch = ref('')
    const itemSearch = ref('')
    const itemStatusFilter = ref('')

    const skinList = ref([])
    const itemList = ref([])

    // 皮肤关注过滤
    const filteredSkinList = computed(() => {
      if (!skinSearch.value) return skinList.value
      return skinList.value.filter(i =>
        i.name.toLowerCase().includes(skinSearch.value.toLowerCase())
      )
    })

    // 单件关注过滤
    const filteredItemList = computed(() => {
      let list = itemList.value
      if (itemStatusFilter.value) {
        list = list.filter(i => i.status === itemStatusFilter.value)
      }
      if (itemSearch.value) {
        list = list.filter(i =>
          i.name.toLowerCase().includes(itemSearch.value.toLowerCase())
        )
      }
      return list
    })

    const getTrendClass = (trend) => {
      if (trend === 'up') return 'trend-up'
      if (trend === 'down') return 'trend-down'
      return 'trend-flat'
    }

    const getTrendIcon = (trend) => {
      if (trend === 'up') return '▲'
      if (trend === 'down') return '▼'
      return '—'
    }

    const getStatusLabel = (status) => {
      const map = { on_sale: '在售', sold: '已售', off_shelf: '下架' }
      return map[status] || status
    }

    const getStatusBadgeClass = (status) => {
      const map = { on_sale: 'badge-on-sale', sold: 'badge-sold', off_shelf: 'badge-off' }
      return map[status] || ''
    }

    return {
      skinSearch,
      itemSearch,
      itemStatusFilter,
      skinList,
      itemList,
      filteredSkinList,
      filteredItemList,
      getTrendClass,
      getTrendIcon,
      getStatusLabel,
      getStatusBadgeClass
    }
  }
}
</script>

<style scoped>
.favorite-container {
  margin-top: 1rem;
}

.favorite-layout {
  display: flex;
  gap: 1.5rem;
  height: calc(100vh - 300px);
  min-height: 600px;
}

/* 左右两栏 */
.favorite-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 头部 */
.favorite-header {
  padding: 1rem;
  background: var(--bg-tertiary);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.header-left h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.favorite-count {
  font-size: 0.85rem;
  font-weight: 400;
  color: var(--text-secondary);
  margin-left: 0.5rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.favorite-search {
  width: 180px;
}

.favorite-filter {
  width: 120px;
}

/* 列表内容区 */
.favorite-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

/* 每一行 */
.favorite-item {
  display: flex;
  align-items: center;
  padding: 0.9rem 1rem;
  margin-bottom: 0.75rem;
  background: var(--bg-primary);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.2s ease;
  gap: 1rem;
}

.favorite-item:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.favorite-item.item-sold {
  opacity: 0.6;
}

.favorite-item.item-off {
  opacity: 0.5;
}

/* 图片区 */
.favorite-item-image {
  position: relative;
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
}

.favorite-weapon-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.favorite-image-placeholder {
  color: var(--el-text-color-secondary);
  font-size: 0.8rem;
}

/* 单件状态角标 */
.item-status-badge {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 0;
}

.badge-on-sale {
  background: rgba(76, 175, 80, 0.85);
  color: #fff;
}

.badge-sold {
  background: rgba(144, 144, 144, 0.85);
  color: #fff;
}

.badge-off {
  background: rgba(245, 108, 108, 0.85);
  color: #fff;
}

/* 信息区 */
.favorite-item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.favorite-item-name {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.favorite-item-tags {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.favorite-item-price-row {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.8rem;
}

.price-label {
  color: var(--text-secondary);
  white-space: nowrap;
}

.price-value {
  font-weight: 600;
  color: var(--text-primary);
}

.sale-color {
  color: #4CAF50;
}

.highlight-color {
  color: #409EFF;
}

.seller-name {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* 磨损条 */
.float-bar-container {
  padding: 0;
}

.float-bar {
  position: relative;
  height: 5px;
  border-radius: 3px;
  overflow: hidden;
  display: flex;
}

.float-segment { flex: 1; height: 100%; }
.float-segment.fn { background: #4CAF50; flex: 0.07; }
.float-segment.mw { background: #8BC34A; flex: 0.08; }
.float-segment.ft { background: #FFC107; flex: 0.23; }
.float-segment.ww { background: #FF9800; flex: 0.07; }
.float-segment.bs { background: #F44336; flex: 0.55; }

.float-pointer {
  position: absolute;
  top: -2px;
  width: 2px;
  height: 9px;
  background: #fff;
  box-shadow: 0 0 3px rgba(0,0,0,0.5);
  transform: translateX(-50%);
  z-index: 1;
}

/* 右侧操作区 */
.favorite-item-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.6rem;
  flex-shrink: 0;
}

/* 价格趋势 */
.price-trend {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
  font-weight: 600;
  min-width: 64px;
  justify-content: flex-end;
}

.trend-up { color: #F56C6C; }
.trend-down { color: #4CAF50; }
.trend-flat { color: var(--text-secondary); }

.trend-icon {
  font-size: 0.7rem;
}

/* 关注时间 */
.item-add-time {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.1rem;
}

.time-label {
  font-size: 0.7rem;
  color: var(--text-secondary);
}

.time-value {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.action-buttons {
  display: flex;
  gap: 0.4rem;
}

/* 空状态 */
.empty-favorite {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}

/* 响应式 */
@media (max-width: 900px) {
  .favorite-layout {
    flex-direction: column;
    height: auto;
  }
}
</style>
