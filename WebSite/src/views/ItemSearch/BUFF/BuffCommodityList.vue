<template>
  <!-- BUFF商品列表 -->
  <div v-if="showBuffList" class="card buff-commodity-list">
    <!-- 折叠/展开控制头部 -->
    <div class="buff-collapse-header" @click.stop="toggleBuffList">
      <div class="buff-collapse-left">
        <el-icon class="collapse-icon">
          <CaretRight v-if="!showBuffTable" />
          <CaretBottom v-if="showBuffTable" />
        </el-icon>
        <span class="buff-collapse-title">BUFF</span>
        <el-button
          type="primary"
          size="small"
          :icon="Refresh"
          @click.stop="handleRefreshBuff"
          :loading="isSearching && searchSource === 'buff'"
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
          @click.stop="selectAllCommodities('buff')"
        >
          全选
        </el-button>
      </div>
      <div class="buff-weapon-info">
        <span class="weapon-name">{{ buffCurrentWeapon?.market_listing_item_name }}</span>
        <span class="weapon-id">商品ID: {{ buffCurrentWeapon?.buff_id }}</span>
        <span class="commodity-count">已加载: {{ buffCommodities.length }} 件</span>
        <span class="total-count">总数: {{ buffTotalCount }} 件</span>
        <span class="buy-count">求购: {{ buffBuyNum }} 件</span>
        <span class="rent-count">租赁: {{ buffRentNum }} 件</span>
      </div>
    </div>

    <!-- BUFF卡片模式 -->
    <div
      v-show="showBuffTable"
      class="commodity-card-grid buff-scroll-container"
      v-loading="isSearching && searchSource === 'buff'"
      element-loading-text="加载中..."
      element-loading-background="rgba(0, 0, 0, 0.8)"
      @scroll="handleBuffScroll"
    >
      <div
        v-for="(item, index) in buffCommodities"
        :key="index"
        class="commodity-card"
        :class="{
          'selected': isCommoditySelected(item),
          'multi-select-mode': isMultiSelectMode
        }"
        @click="handleCommodityCardClick(item, 'buff', $event)"
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
              :title="sticker.name || '印花'"
            >
              <img
                v-if="sticker.img_url"
                :src="sticker.img_url"
                :alt="sticker.name"
                class="sticker-img-overlay"
                @error="(e) => e.target.style.display = 'none'"
              />
              <div v-else class="sticker-placeholder-overlay">?</div>
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
              <span class="info-label">售价:</span>
              <span class="info-value price-highlight">¥{{ item.price }}</span>
            </div>
            <div class="info-item" v-if="item.description">
              <span class="info-label">描述:</span>
              <span class="info-value description-text" :title="item.description">{{ item.description }}</span>
            </div>
            <div class="info-item" v-if="item.user_name">
              <span class="info-label">卖家:</span>
              <span class="info-value">{{ item.user_name }}</span>
            </div>
            <div class="info-item" v-if="item.paintseed">
              <span class="info-label">模板:</span>
              <span class="info-value">{{ item.paintseed }}</span>
            </div>
          </div>
          <!-- 印花/挂件价值 -->
          <div class="sticker-value-info" v-if="item.stickers && item.stickers.length > 0">
            <div class="sticker-value-item" v-if="item.stickerTotalValue !== undefined">
              <span class="sticker-value-label">印花价值:</span>
              <span class="sticker-value-amount">¥{{ item.stickerTotalValue || '0.00' }}</span>
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
            @click.stop="handleBuyBuffCommodity(item)"
          >
            购买
          </el-button>
        </div>
      </div>
      <!-- BUFF加载更多提示 -->
      <div class="load-more-indicator" v-if="buffCommodities.length > 0">
        <div v-if="buffLoadingMore" class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        <div v-else-if="!buffHasMore" class="no-more-data">
          <span>没有更多数据了</span>
        </div>
        <div v-else class="scroll-hint">
          <span>下拉加载更多</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { CaretRight, CaretBottom, Check, Loading, Refresh } from '@element-plus/icons-vue'

// 接收父组件传递的 props
const props = defineProps({
  showBuffList: Boolean,
  showBuffTable: Boolean,
  isSearching: Boolean,
  searchSource: String,
  isMultiSelectMode: Boolean,
  buffCurrentWeapon: Object,
  buffCommodities: Array,
  buffTotalCount: Number,
  buffBuyNum: Number,
  buffRentNum: Number,
  buffLoadingMore: Boolean,
  buffHasMore: Boolean
})

// 定义事件
const emit = defineEmits([
  'toggle-buff-list',
  'refresh-buff',
  'toggle-multi-select',
  'select-all',
  'commodity-click',
  'buff-scroll',
  'buy-buff-commodity'
])

// 方法转发给父组件
const toggleBuffList = () => emit('toggle-buff-list')
const handleRefreshBuff = () => emit('refresh-buff')
const toggleMultiSelectMode = () => emit('toggle-multi-select')
const selectAllCommodities = (type) => emit('select-all', type)
const handleCommodityCardClick = (item, type, event) => emit('commodity-click', { item, type, event })
const handleBuffScroll = (event) => emit('buff-scroll', event)
const handleBuyBuffCommodity = (item) => emit('buy-buff-commodity', item)
const handleImageError = (e) => {
  // 图片加载失败处理
  e.target.style.display = 'none'
}

// 从父组件注入的方法
import { inject } from 'vue'
const isCommoditySelected = inject('isCommoditySelected', () => false)
</script>

<style scoped src="./buff-commodity-list.css"></style>
