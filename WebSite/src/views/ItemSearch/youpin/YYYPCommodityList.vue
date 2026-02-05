<template>
  <!-- 悠悠有品商品列表 -->
  <div v-if="showYYYPList" class="card yyyp-commodity-list">
    <!-- 折叠/展开控制头部 -->
    <div class="yyyp-collapse-header" @click.stop="toggleYYYPList">
      <div class="yyyp-collapse-left">
        <el-icon class="collapse-icon">
          <CaretRight v-if="!showYYYPTable" />
          <CaretBottom v-if="showYYYPTable" />
        </el-icon>
        <span class="yyyp-collapse-title">悠悠有品商品列表</span>
        <el-button
          type="primary"
          size="small"
          :icon="Refresh"
          @click.stop="handleRefreshYYYP"
          :loading="isSearching && searchSource === 'yyyp'"
        >
          刷新列表
        </el-button>
        <el-button
          :type="isMultiSelectMode ? 'warning' : 'info'"
          size="small"
          @click.stop="toggleMultiSelectMode"
        >
          {{ isMultiSelectMode ? '取消多选' : '多选' }}
        </el-button>
        <el-button
          v-if="isMultiSelectMode"
          type="info"
          size="small"
          @click.stop="selectAllCommodities('yyyp')"
        >
          全选
        </el-button>
      </div>
      <div class="yyyp-weapon-info">
        <span class="weapon-name">{{ yyypCurrentWeapon?.market_listing_item_name }}</span>

        <!-- 筛选按钮组 -->
        <div class="yyyp-filter-buttons">
          <button
            class="filter-btn"
            :class="{ active: activeFilter === 'on_sale' }"
            @click.stop="handleFilterChange('on_sale')"
          >
            在售
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn"
            :class="{ active: activeFilter === 'on_lease' }"
            @click.stop="handleFilterChange('on_lease')"
          >
            在租
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn"
            :class="{ active: activeFilter === 'presale' }"
            @click.stop="handleFilterChange('presale')"
          >
            预售
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn"
            :class="{ active: activeFilter === 'wanted' }"
            @click.stop="handleFilterChange('wanted')"
          >
            求购
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn"
            :class="{ active: activeFilter === 'sold' }"
            @click.stop="handleFilterChange('sold')"
          >
            成交
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn"
            :class="{ active: activeFilter === 'price_trend' }"
            @click.stop="handleFilterChange('price_trend')"
          >
            价格走势
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn filter-advanced"
            @click.stop="handleAdvancedFilter"
          >
            筛选
          </button>
        </div>

        <span class="commodity-count">已加载: {{ yyypCommodities.length }} 件</span>
        <span class="total-count">总数: {{ yyypTotalCount }} 件</span>
      </div>
    </div>

    <!-- 悠悠有品卡片模式 -->
    <div
      v-show="showYYYPTable"
      class="commodity-card-grid yyyp-scroll-container"
      v-loading="isSearching && searchSource === 'yyyp'"
      element-loading-text="加载中..."
      element-loading-background="rgba(0, 0, 0, 0.8)"
      @scroll="handleYYYPScroll"
    >
      <div
        v-for="(item, index) in yyypCommodities"
        :key="index"
        class="commodity-card"
        :class="{
          'selected': isCommoditySelected(item),
          'multi-select-mode': isMultiSelectMode
        }"
        @click="handleCommodityCardClick(item, 'yyyp', $event)"
      >
        <!-- 选中标记 -->
        <div v-if="isMultiSelectMode && isCommoditySelected(item)" class="selected-check">
          <el-icon><Check /></el-icon>
        </div>
        <div class="commodity-card-image">
          <img :src="item.iconUrl" class="commodity-icon" @error="handleImageError" />
          <!-- 印花覆盖层 - 左下角 -->
          <div v-if="item.stickers && item.stickers.length > 0" class="sticker-overlay">
            <div
              v-for="(sticker, sIdx) in item.stickers"
              :key="sIdx"
              class="sticker-item-overlay"
              :title="sticker.Name || '印花'"
            >
              <img
                v-if="sticker.TemplateHashName"
                :src="getWeaponImage(sticker.TemplateHashName)"
                :alt="sticker.Name"
                class="sticker-img-overlay"
                @error="(e) => e.target.style.display = 'none'"
              />
              <img
                v-else-if="sticker.ImgUrl"
                :src="sticker.ImgUrl"
                :alt="sticker.Name"
                class="sticker-img-overlay"
                @error="(e) => e.target.style.display = 'none'"
              />
              <div v-else class="sticker-placeholder-overlay">?</div>
            </div>
          </div>
          <!-- 挂件覆盖层 - 右上角 -->
          <div v-if="item.pendants && item.pendants.length > 0" class="pendant-overlay">
            <div
              v-for="(pendant, pIdx) in item.pendants"
              :key="pIdx"
              class="pendant-item-overlay"
              :title="pendant.pendantSourceName || pendant.name || '挂件'"
            >
              <img
                v-if="pendant.steamHashName"
                :src="getWeaponImage(pendant.steamHashName)"
                :alt="pendant.name"
                class="pendant-img-overlay"
                @error="(e) => e.target.style.display = 'none'"
              />
              <img
                v-else-if="pendant.imgUrl"
                :src="pendant.imgUrl"
                :alt="pendant.name"
                class="pendant-img-overlay"
                @error="(e) => e.target.style.display = 'none'"
              />
              <div v-else class="pendant-placeholder-overlay">🎗️</div>
            </div>
          </div>
        </div>
        <div class="commodity-card-content">
          <!-- 磨损进度条 - 顶部 -->
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
            <div class="float-value">{{ item.abrade }}</div>
          </div>
          <!-- 商品详情信息 -->
          <div class="commodity-card-info">
            <div class="info-item">
              <span class="info-label">价格:</span>
              <span class="info-value price-highlight">¥{{ item.price }}</span>
            </div>
            <div class="info-item" v-if="item.paintSeed">
              <span class="info-label">模板:</span>
              <span class="info-value">{{ item.paintSeed }}</span>
            </div>
            <div class="info-item" v-if="item.haveNameTag === 1">
              <span class="info-label">改名:</span>
              <div v-if="item.nameTagText" class="info-value nametag-text" :title="item.nameTagText">
                {{ item.nameTagText }}
              </div>
              <span
                v-else
                @click.stop="fetchSingleNameTag(item)"
                class="info-value nametag-parse"
                :style="{ opacity: item.nameTagLoading ? 0.5 : 1 }"
                :title="item.nameTagLoading ? '加载中...' : '点击解析改名'"
              >
                🏷️ 解析名称
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">卖家:</span>
              <span class="info-value">{{ item.userNickName || '-' }}</span>
            </div>
          </div>
          <!-- 印花/挂件价值 -->
          <div class="sticker-value-info" v-if="(item.stickers && item.stickers.length > 0) || (item.pendants && item.pendants.length > 0)">
            <div class="sticker-value-item" v-if="item.stickerTotalValue !== undefined">
              <span class="sticker-value-label">印花价值:</span>
              <span class="sticker-value-amount">¥{{ item.stickerTotalValue || '0.00' }}</span>
            </div>
            <div class="sticker-value-item" v-if="item.pendantTotalValue !== undefined">
              <span class="sticker-value-label">挂件价值:</span>
              <span class="sticker-value-amount">¥{{ item.pendantTotalValue || '0.00' }}</span>
            </div>
            <div class="sticker-value-loading" v-if="item.priceLoading">
              <span>价格查询中...</span>
            </div>
          </div>
          <!-- 购买按钮 -->
          <el-button
            v-if="!isMultiSelectMode"
            type="success"
            size="small"
            class="card-buy-button"
            @click.stop="handleBuyCommodity(item)"
          >
            购买
          </el-button>
        </div>
      </div>
      <!-- 加载更多提示 -->
      <div class="load-more-indicator" v-if="yyypCommodities.length > 0">
        <div v-if="yyypLoadingMore" class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        <div v-else-if="!yyypHasMore" class="no-more-data">
          <span>没有更多数据了</span>
        </div>
        <div v-else class="scroll-hint">
          <span>下拉加载更多</span>
        </div>
      </div>
    </div>

    <!-- 高级筛选对话框 -->
    <el-dialog
      v-model="filterDialogVisible"
      title="筛选"
      width="400px"
      :close-on-click-modal="false"
      class="yyyp-filter-dialog"
    >
      <el-form :model="filterForm" label-position="left" label-width="100px">
        <!-- 图案模板 -->
        <el-form-item label="图案模板">
          <el-input
            v-model="filterForm.templateId"
            placeholder="请输入模板编号0-1000"
            clearable
          />
        </el-form-item>

        <!-- 磨损区间 -->
        <el-form-item label="磨损区间">
          <div class="wear-range-inputs">
            <el-input
              v-model="filterForm.wearMin"
              placeholder="最小值"
              style="width: 48%"
            />
            <span style="margin: 0 2%">-</span>
            <el-input
              v-model="filterForm.wearMax"
              placeholder="最大值"
              style="width: 48%"
            />
          </div>
        </el-form-item>

        <!-- 名称标签 -->
        <el-form-item label="名称标签">
          <el-select
            v-model="filterForm.hasNameTag"
            placeholder="请选择"
            clearable
            style="width: 100%"
          >
            <el-option label="全部" :value="null" />
            <el-option label="有名称标签" :value="true" />
            <el-option label="无名称标签" :value="false" />
          </el-select>
        </el-form-item>

        <!-- 名称标签二级菜单 -->
        <el-form-item label="" v-if="filterForm.hasNameTag === true">
          <el-input
            v-model="filterForm.nameTagText"
            placeholder="输入名称标签内容"
            clearable
          />
        </el-form-item>

        <!-- 印花搜枪 -->
        <el-form-item label="印花搜枪">
          <el-select
            v-model="filterForm.hasStickerFilter"
            placeholder="请选择"
            clearable
            style="width: 100%"
          >
            <el-option label="全部" :value="null" />
            <el-option label="有印花" :value="true" />
            <el-option label="无印花" :value="false" />
          </el-select>
        </el-form-item>

        <!-- 印花搜枪二级菜单 -->
        <el-form-item label="" v-if="filterForm.hasStickerFilter === true">
          <el-input
            v-model="filterForm.stickerName"
            placeholder="输入印花名称"
            clearable
          />
        </el-form-item>

        <!-- 挂件 -->
        <el-form-item label="挂件">
          <el-select
            v-model="filterForm.hasPendant"
            placeholder="请选择"
            clearable
            style="width: 100%"
          >
            <el-option label="全部" :value="null" />
            <el-option label="有挂件" :value="true" />
            <el-option label="无挂件" :value="false" />
          </el-select>
        </el-form-item>

        <!-- 挂件二级菜单 -->
        <el-form-item label="" v-if="filterForm.hasPendant === true">
          <el-input
            v-model="filterForm.pendantName"
            placeholder="输入挂件名称"
            clearable
          />
        </el-form-item>

        <!-- 极速发货 -->
        <el-form-item label="极速发货">
          <el-switch v-model="filterForm.fastDelivery" />
        </el-form-item>

        <!-- 出售价格 -->
        <el-form-item label="出售价格">
          <div class="price-range-inputs">
            <el-input
              v-model="filterForm.priceMin"
              placeholder="最低价格"
              style="width: 48%"
            />
            <span style="margin: 0 2%">-</span>
            <el-input
              v-model="filterForm.priceMax"
              placeholder="最高价格"
              style="width: 48%"
            />
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleResetFilter">重置</el-button>
          <el-button type="primary" @click="handleApplyFilter">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { CaretRight, CaretBottom, Check, Loading, Refresh } from '@element-plus/icons-vue'

// 接收父组件传递的 props
const props = defineProps({
  showYYYPList: Boolean,
  showYYYPTable: Boolean,
  isSearching: Boolean,
  searchSource: String,
  isMultiSelectMode: Boolean,
  yyypCurrentWeapon: Object,
  yyypCommodities: Array,
  yyypTotalCount: Number,
  yyypLoadingMore: Boolean,
  yyypHasMore: Boolean
})

// 定义事件
const emit = defineEmits([
  'toggle-yyyp-list',
  'refresh-yyyp',
  'toggle-multi-select',
  'select-all',
  'commodity-click',
  'yyyp-scroll',
  'buy-commodity',
  'fetch-single-nametag',
  'filter-change',
  'advanced-filter'
])

// 当前激活的筛选项
const activeFilter = ref('on_sale')

// 筛选对话框状态
const filterDialogVisible = ref(false)

// 筛选表单数据
const filterForm = ref({
  templateId: '',           // 图案模板编号
  wearMin: '',              // 磨损最小值
  wearMax: '',              // 磨损最大值
  hasNameTag: null,         // 是否有名称标签 (null=全部, true=有, false=无)
  nameTagText: '',          // 名称标签内容（二级）
  hasStickerFilter: null,   // 是否有印花 (null=全部, true=有, false=无)
  stickerName: '',          // 印花名称（二级）
  hasPendant: null,         // 是否有挂件 (null=全部, true=有, false=无)
  pendantName: '',          // 挂件名称（二级）
  fastDelivery: false,      // 极速发货
  priceMin: '',             // 最低价格
  priceMax: ''              // 最高价格
})

// 方法转发给父组件
const toggleYYYPList = () => emit('toggle-yyyp-list')
const handleRefreshYYYP = () => emit('refresh-yyyp')
const toggleMultiSelectMode = () => emit('toggle-multi-select')
const selectAllCommodities = (type) => emit('select-all', type)
const handleCommodityCardClick = (item, type, event) => emit('commodity-click', { item, type, event })
const handleYYYPScroll = (event) => emit('yyyp-scroll', event)
const handleBuyCommodity = (item) => emit('buy-commodity', item)
const fetchSingleNameTag = (item) => emit('fetch-single-nametag', item)
const handleImageError = (e) => {
  // 图片加载失败处理
  e.target.style.display = 'none'
}

// 筛选相关方法
const handleFilterChange = (filterType) => {
  activeFilter.value = filterType
  emit('filter-change', filterType)
}

const handleAdvancedFilter = () => {
  filterDialogVisible.value = true
}

// 重置筛选表单
const handleResetFilter = () => {
  filterForm.value = {
    templateId: '',
    wearMin: '',
    wearMax: '',
    hasNameTag: null,
    nameTagText: '',
    hasStickerFilter: null,
    stickerName: '',
    hasPendant: null,
    pendantName: '',
    fastDelivery: false,
    priceMin: '',
    priceMax: ''
  }
}

// 应用筛选
const handleApplyFilter = () => {
  console.log('应用筛选:', filterForm.value)
  emit('advanced-filter', filterForm.value)
  filterDialogVisible.value = false
}

// 从父组件注入的方法
import { inject } from 'vue'
const isCommoditySelected = inject('isCommoditySelected', () => false)
const getWeaponImage = inject('getWeaponImage', (hashName) => {
  if (!hashName) return ''
  return `/weapon_imgs/${encodeURIComponent(hashName)}.png`
})
</script>

<style scoped src="./yyyp-commodity-list.css"></style>
