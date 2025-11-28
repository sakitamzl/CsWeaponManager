<template>
  <div>
    <div class="filters card">
      <div class="flex flex-wrap gap-4 items-center">
        <el-select 
          v-model="selectedSteamId" 
          placeholder="选择Steam账号" 
          class="steam-id-select"
          @change="handleSteamIdChange"
          filterable
        >
          <el-option
            v-for="item in steamIdList"
            :key="item.dataID"
            :label="`${item.dataName} (${item.steamID}) - ${item.item_count}件`"
            :value="item.steamID"
          >
            <span style="float: left">{{ item.dataName }} ({{ item.steamID }})</span>
            <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">
              {{ item.item_count }}件
            </span>
          </el-option>
        </el-select>
        <el-input
          v-model="searchText"
          placeholder="搜索饰品名称..."
          prefix-icon="Search"
          class="search-input"
          @keyup.enter="loadInventoryData"
          clearable
        />
        <el-select v-model="weaponTypeFilter" placeholder="武器类型" class="type-select" clearable>
          <el-option label="全部" value="" />
          <el-option label="步枪" value="步枪" />
          <el-option label="手枪" value="手枪" />
          <el-option label="狙击枪" value="狙击枪" />
          <el-option label="冲锋枪" value="冲锋枪" />
          <el-option label="霰弹枪" value="霰弹枪" />
          <el-option label="机枪" value="机枪" />
          <el-option label="手套" value="手套" />
          <el-option label="匕首" value="匕首" />
        </el-select>
        <el-select v-model="floatRangeFilter" placeholder="磨损等级" class="wear-select" clearable>
          <el-option label="全部" value="" />
          <el-option label="崭新出厂" value="崭新出厂" />
          <el-option label="略有磨损" value="略有磨损" />
          <el-option label="久经沙场" value="久经沙场" />
          <el-option label="破损不堪" value="破损不堪" />
          <el-option label="战痕累累" value="战痕累累" />
        </el-select>
        <el-button type="primary" @click="loadInventoryData" :loading="loading">
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="success" @click="fetchSteamInventory" :loading="fetchingInventory" icon="Refresh" class="action-button">
          更新Steam库存
        </el-button>
        <el-button type="success" @click="fetchYYYPPrice" :loading="fetchingYYYPPrice" icon="Money" class="action-button">
          获取悠悠有品价格
        </el-button>
        <el-button type="success" @click="fetchBuffPrice" :loading="fetchingBuffPrice" icon="Money" class="action-button">
          获取BUFF价格
        </el-button>
        <el-switch
          v-model="groupByItem"
          active-text="分组显示"
          inactive-text="列表显示"
          @change="handleGroupChange"
        />
        <el-button-group>
          <el-button 
            :type="displayMode === 'list' ? 'primary' : ''" 
            @click="displayMode = 'list'"
            icon="List"
          >
            列表
          </el-button>
          <el-button 
            :type="displayMode === 'card' ? 'primary' : ''" 
            @click="displayMode = 'card'"
            icon="Grid"
          >
            卡片
          </el-button>
        </el-button-group>
      </div>
    </div>

    <div class="inventory-stats">
      <div class="grid grid-5">
        <div class="card">
          <h3>总库存数量</h3>
          <p class="stat-number">{{ inventoryStats.totalCount }}</p>
        </div>
        <div class="card">
          <h3>购入总价值</h3>
          <p class="stat-number">¥{{ priceStats.total_price }}</p>
        </div>
        <div class="card">
          <h3>悠悠有品最低价</h3>
          <div class="stat-price-container">
            <p class="stat-number">¥{{ yyypPriceStats.total_price }}</p>
            <p class="stat-diff-right" :style="{ color: yyypPriceStats.diff >= 0 ? '#f56c6c' : '#4CAF50' }">
              {{ yyypPriceStats.diff >= 0 ? '+' : '' }}¥{{ yyypPriceStats.diff }}
            </p>
          </div>
        </div>
        <div class="card">
          <h3>BUFF最低价</h3>
          <div class="stat-price-container">
            <p class="stat-number">¥{{ buffPriceStats.total_price }}</p>
            <p class="stat-diff-right" :style="{ color: buffPriceStats.diff >= 0 ? '#f56c6c' : '#4CAF50' }">
              {{ buffPriceStats.diff >= 0 ? '+' : '' }}¥{{ buffPriceStats.diff }}
            </p>
          </div>
        </div>
        <div class="card">
          <h3>Steam参考价</h3>
          <div class="stat-price-container">
            <p class="stat-number">¥{{ steamPriceStats.total_price }}</p>
            <p class="stat-diff-right" :style="{ color: steamPriceStats.diff >= 0 ? '#f56c6c' : '#4CAF50' }">
              {{ steamPriceStats.diff >= 0 ? '+' : '' }}¥{{ steamPriceStats.diff }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 列表显示 -->
    <div class="table-container" v-if="!groupByItem && displayMode === 'list'">
      <el-table
        :data="inventoryData"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        :row-style="{ backgroundColor: 'transparent' }"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        height="calc(100vh - 400px)"
        :default-sort="{ prop: 'buy_price', order: 'descending' }"
        @sort-change="handleSortChange"
      >
        <el-table-column 
          prop="order_time" 
          label="入库时间" 
          width="180" 
          sortable="custom"
        >
          <template #default="scope">
            <span v-if="scope.row.order_time" style="color: #9E9E9E;">
              {{ scope.row.order_time }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="weapon_name" label="武器" min-width="120" />
        <el-table-column prop="weapon_type" label="类型" min-width="100" />
        <el-table-column prop="item_name" label="饰品名称" min-width="250" show-overflow-tooltip />
        <el-table-column 
          prop="float_range" 
          label="磨损等级" 
          min-width="100" 
          sortable="custom"
        />
        <el-table-column 
          prop="weapon_float" 
          label="磨损值" 
          min-width="150" 
          sortable="custom"
        >
          <template #default="scope">
            <span v-if="scope.row.weapon_float" style="font-family: monospace;">
              {{ scope.row.weapon_float }}
            </span>
            <span v-else style="color: #888;">N/A</span>
          </template>
        </el-table-column>
        <el-table-column 
          prop="buy_price" 
          label="购入价格" 
          width="150" 
          sortable="custom"
        >
          <template #default="scope">
            <div v-if="editingAssetId !== scope.row.assetid" 
                 @click="startEdit(scope.row)" 
                 style="cursor: pointer; padding: 5px;">
              <div v-if="scope.row.buy_price" style="display: flex; align-items: center; gap: 5px;">
                <span style="color: #fff; font-weight: bold;">¥{{ parseFloat(scope.row.buy_price).toFixed(2) }}</span>
              </div>
              <span v-else style="color: #888;">点击输入</span>
            </div>
            <el-input 
              v-else
              v-model="editingPrice" 
              placeholder="输入价格" 
              size="small"
              :id="'price-input-' + scope.row.assetid"
              @blur="finishEdit(scope.row)"
              @keyup.enter="finishEdit(scope.row)"
              @keyup.esc="cancelEdit"
            />
          </template>
        </el-table-column>
        <el-table-column 
          prop="yyyp_price" 
          label="悠悠有品" 
          width="180" 
          sortable="custom"
        >
          <template #default="scope">
            <div v-if="scope.row.yyyp_price && scope.row.buy_price" style="display: flex; flex-direction: column; align-items: flex-start; gap: 2px;">
              <span style="color: #fff; font-weight: bold;">
                ¥{{ parseFloat(scope.row.yyyp_price).toFixed(2) }}
              </span>
              <span 
                :style="{
                  color: parseFloat(scope.row.yyyp_price) < parseFloat(scope.row.buy_price) ? '#4CAF50' : '#f56c6c',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }"
              >
                {{ parseFloat(scope.row.yyyp_price) < parseFloat(scope.row.buy_price) ? '-' : '+' }}
                ¥{{ Math.abs(parseFloat(scope.row.yyyp_price) - parseFloat(scope.row.buy_price)).toFixed(2) }}
              </span>
            </div>
            <span v-else-if="scope.row.yyyp_price" style="color: #fff; font-weight: bold;">
              ¥{{ parseFloat(scope.row.yyyp_price).toFixed(2) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column 
          prop="buff_price" 
          label="BUFF" 
          width="180" 
          sortable="custom"
        >
          <template #default="scope">
            <div v-if="scope.row.buff_price && scope.row.buy_price" style="display: flex; flex-direction: column; align-items: flex-start; gap: 2px;">
              <span style="color: #fff; font-weight: bold;">
                ¥{{ parseFloat(scope.row.buff_price).toFixed(2) }}
              </span>
              <span 
                :style="{
                  color: parseFloat(scope.row.buff_price) < parseFloat(scope.row.buy_price) ? '#4CAF50' : '#f56c6c',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }"
              >
                {{ parseFloat(scope.row.buff_price) < parseFloat(scope.row.buy_price) ? '-' : '+' }}
                ¥{{ Math.abs(parseFloat(scope.row.buff_price) - parseFloat(scope.row.buy_price)).toFixed(2) }}
              </span>
            </div>
            <span v-else-if="scope.row.buff_price" style="color: #fff; font-weight: bold;">
              ¥{{ parseFloat(scope.row.buff_price).toFixed(2) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column 
          prop="steam_price" 
          label="Steam" 
          width="120" 
          sortable="custom"
        >
          <template #default="scope">
            <span v-if="scope.row.steam_price" style="color: #fff; font-weight: bold;">
              ¥{{ parseFloat(scope.row.steam_price).toFixed(2) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column 
          prop="remark" 
          label="备注" 
          width="120" 
          fixed="right" 
          sortable="custom"
        >
          <template #default="scope">
            <el-tooltip v-if="scope.row.remark" :content="scope.row.remark" placement="left" effect="dark">
              <el-tag type="warning" size="small" style="cursor: help;">
                交易限制
              </el-tag>
            </el-tooltip>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="table-footer">
        <span>共 {{ inventoryData.length }} 条数据</span>
        <span v-if="hasMore && !loadingMore" style="margin-left: 1rem; color: #999;">滚动加载更多...</span>
        <span v-if="loadingMore" style="margin-left: 1rem; color: #4CAF50;">正在加载更多...</span>
        <span v-if="!hasMore && inventoryData.length > 0" style="margin-left: 1rem; color: #999;">已加载全部数据</span>
      </div>
      <!-- 滚动触发元素 -->
      <div id="load-more-trigger" style="height: 1px;"></div>
    </div>

    <!-- 卡片显示 -->
    <div class="card-container" v-if="!groupByItem && displayMode === 'card'">
      <div v-loading="loading" class="card-grid">
        <div 
          v-for="item in inventoryData" 
          :key="item.assetid" 
          class="inventory-card"
        >
          <div class="card-image">
            <img 
              v-if="getWeaponImage(item.steam_hash_name)"
              :src="getWeaponImage(item.steam_hash_name)" 
              :alt="item.item_name"
              @error="(e) => handleImageError(e, item.steam_hash_name)"
            />
            <div v-else class="image-placeholder">
              <span>无图片</span>
            </div>
          </div>
          <div class="card-content">
            <div class="card-title" :title="item.item_name">{{ item.item_name }}</div>
            <div class="card-info">
              <div class="card-info-row">
                <span class="info-label">武器:</span>
                <span class="info-value">{{ item.weapon_name }}</span>
              </div>
              <div class="card-info-row">
                <span class="info-label">类型:</span>
                <span class="info-value">{{ item.weapon_type }}</span>
              </div>
              <div class="card-info-row" v-if="item.float_range">
                <span class="info-label">磨损:</span>
                <span class="info-value">{{ item.float_range }}</span>
              </div>
              <div class="card-info-row" v-if="item.weapon_float">
                <span class="info-label">磨损值:</span>
                <span class="info-value">{{ item.weapon_float }}</span>
              </div>
            </div>
            <div class="card-prices">
              <div class="price-row" v-if="item.buy_price">
                <span class="price-label">购入:</span>
                <span class="price-value buy-price">¥{{ parseFloat(item.buy_price).toFixed(2) }}</span>
              </div>
              <div class="price-row" v-if="item.yyyp_price">
                <span class="price-label">悠悠:</span>
                <span 
                  class="price-value" 
                  :class="getPriceDiffClass(item.yyyp_price, item.buy_price)"
                >
                  ¥{{ parseFloat(item.yyyp_price).toFixed(2) }}
                </span>
              </div>
              <div class="price-row" v-if="item.buff_price">
                <span class="price-label">BUFF:</span>
                <span 
                  class="price-value" 
                  :class="getPriceDiffClass(item.buff_price, item.buy_price)"
                >
                  ¥{{ parseFloat(item.buff_price).toFixed(2) }}
                </span>
              </div>
              <div class="price-row" v-if="item.steam_price">
                <span class="price-label">Steam:</span>
                <span class="price-value">¥{{ parseFloat(item.steam_price).toFixed(2) }}</span>
              </div>
            </div>
            <div class="card-footer" v-if="item.remark">
              <el-tag type="warning" size="small">交易限制</el-tag>
            </div>
          </div>
        </div>
      </div>
      <div class="table-footer">
        <span>共 {{ inventoryData.length }} 条数据</span>
        <span v-if="hasMore && !loadingMore" style="margin-left: 1rem; color: #999;">滚动加载更多...</span>
        <span v-if="loadingMore" style="margin-left: 1rem; color: #4CAF50;">正在加载更多...</span>
        <span v-if="!hasMore && inventoryData.length > 0" style="margin-left: 1rem; color: #999;">已加载全部数据</span>
      </div>
      <!-- 滚动触发元素 -->
      <div id="load-more-trigger-card" style="height: 1px;"></div>
    </div>

    <!-- 分组显示 -->
    <div class="table-container" v-else>
      <el-table
        :data="groupedData"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        :row-style="{ backgroundColor: 'transparent' }"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        row-key="item_name"
        :expand-row-keys="expandedRows"
        @expand-change="handleExpandChange"
        height="calc(100vh - 400px)"
      >
        <el-table-column type="expand">
          <template #default="scope">
            <div class="expand-content">
              <el-table
                :data="scope.row.details"
                style="width: 100%"
                size="small"
                :row-style="{ backgroundColor: 'transparent' }"
                :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
              >
                <el-table-column prop="order_time" label="入库时间" min-width="160">
                  <template #default="props">
                    <span v-if="props.row.order_time" style="color: #9E9E9E;">
                      {{ props.row.order_time }}
                    </span>
                    <span v-else style="color: #888;">-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="assetid" label="Asset ID" min-width="150" />
                <el-table-column prop="weapon_float" label="磨损值" min-width="150">
                  <template #default="props">
                    <span v-if="props.row.weapon_float" style="font-family: monospace;">
                      {{ props.row.weapon_float }}
                    </span>
                    <span v-else style="color: #888;">N/A</span>
                  </template>
                </el-table-column>
                <el-table-column prop="buy_price" label="购入价格" min-width="120">
                  <template #default="props">
                    <div v-if="props.row.buy_price">
                      <span style="color: #fff; font-weight: bold;">¥{{ parseFloat(props.row.buy_price).toFixed(2) }}</span>
                      <el-tag v-if="!props.row.weapon_float" type="info" size="small" style="margin-left: 5px;">均</el-tag>
                    </div>
                    <span v-else style="color: #888;">-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="yyyp_price" label="悠悠有品" min-width="160">
                  <template #default="props">
                    <div v-if="props.row.yyyp_price && props.row.buy_price" style="display: flex; flex-direction: column; align-items: flex-start; gap: 2px;">
                      <span style="color: #fff; font-weight: bold;">
                        ¥{{ parseFloat(props.row.yyyp_price).toFixed(2) }}
                      </span>
                      <span 
                        :style="{
                          color: parseFloat(props.row.yyyp_price) < parseFloat(props.row.buy_price) ? '#4CAF50' : '#f56c6c',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }"
                      >
                        {{ parseFloat(props.row.yyyp_price) < parseFloat(props.row.buy_price) ? '-' : '+' }}
                        ¥{{ Math.abs(parseFloat(props.row.yyyp_price) - parseFloat(props.row.buy_price)).toFixed(2) }}
                      </span>
                    </div>
                    <span v-else-if="props.row.yyyp_price" style="color: #fff; font-weight: bold;">
                      ¥{{ parseFloat(props.row.yyyp_price).toFixed(2) }}
                    </span>
                    <span v-else style="color: #888;">-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="buff_price" label="BUFF" min-width="160">
                  <template #default="props">
                    <div v-if="props.row.buff_price && props.row.buy_price" style="display: flex; flex-direction: column; align-items: flex-start; gap: 2px;">
                      <span style="color: #fff; font-weight: bold;">
                        ¥{{ parseFloat(props.row.buff_price).toFixed(2) }}
                      </span>
                      <span 
                        :style="{
                          color: parseFloat(props.row.buff_price) < parseFloat(props.row.buy_price) ? '#4CAF50' : '#f56c6c',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }"
                      >
                        {{ parseFloat(props.row.buff_price) < parseFloat(props.row.buy_price) ? '-' : '+' }}
                        ¥{{ Math.abs(parseFloat(props.row.buff_price) - parseFloat(props.row.buy_price)).toFixed(2) }}
                      </span>
                    </div>
                    <span v-else-if="props.row.buff_price" style="color: #fff; font-weight: bold;">
                      ¥{{ parseFloat(props.row.buff_price).toFixed(2) }}
                    </span>
                    <span v-else style="color: #888;">-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="steam_price" label="Steam" min-width="120">
                  <template #default="props">
                    <span v-if="props.row.steam_price" style="color: #fff; font-weight: bold;">
                      ¥{{ parseFloat(props.row.steam_price).toFixed(2) }}
                    </span>
                    <span v-else style="color: #888;">-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="remark" label="备注" min-width="250">
                  <template #default="props">
                    <el-tooltip v-if="props.row.remark" :content="props.row.remark" placement="top" effect="dark">
                      <div style="cursor: help; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {{ props.row.remark }}
                      </div>
                    </el-tooltip>
                    <span v-else style="color: #888;">-</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="weapon_name" label="武器" min-width="120" />
        <el-table-column prop="weapon_type" label="类型" min-width="100" />
        <el-table-column prop="item_name" label="饰品名称" min-width="250" show-overflow-tooltip />
        <el-table-column prop="float_range" label="磨损" min-width="100" />
        <el-table-column prop="count" label="数量" min-width="80">
          <template #default="scope">
            <el-tag type="primary" size="small">{{ scope.row.count }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="table-footer">
        <span>共 {{ groupedData.length }} 组数据</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { API_CONFIG } from '@/config/api.js'

export default {
  name: 'Inventory',
  setup() {
    const loading = ref(false)
    const fetchingInventory = ref(false) // 获取库存中
    const fetchingYYYPPrice = ref(false) // 获取悠悠有品价格中
    const fetchingBuffPrice = ref(false) // 获取BUFF价格中
    const inventoryData = ref([])
    const groupedData = ref([])
    const searchText = ref('')
    const weaponTypeFilter = ref('')
    const floatRangeFilter = ref('')
    const groupByItem = ref(false)
    const displayMode = ref('list') // 'list' 或 'card'
    const expandedRows = ref([])
    const editingAssetId = ref(null) // 正在编辑的资产ID
    const editingPrice = ref('') // 编辑中的价格
    const originalPrice = ref('') // 原始价格
    // 懒加载相关
    const pageSize = ref(50) // 每页加载数量
    const currentOffset = ref(0) // 当前偏移量
    const hasMore = ref(true) // 是否还有更多数据
    const loadingMore = ref(false) // 是否正在加载更多
    // 图片404缓存，避免重复请求
    const image404Cache = ref(new Set())
    const statsData = ref({
      total_count: 0,
      by_type: [],
      by_wear: [],
      price_stats: {
        priced_count: 0,
        total_price: 0,
        avg_price: 0,
        min_price: 0,
        max_price: 0
      }
    })
    const steamIdList = ref([])
    const selectedSteamId = ref('')
    const sortConfig = ref({ prop: 'buy_price', order: 'desc' }) // 默认按购入价格降序排序

    // API 基础地址
    const API_BASE = `${API_CONFIG.BASE_URL}/webInventoryV1`
    const CONFIG_API = `${API_CONFIG.BASE_URL}/configV1`

    const inventoryStats = computed(() => {
      // 基于当前显示的数据计算统计
      const currentData = inventoryData.value || []
      const totalCount = currentData.length
      
      const typeDistribution = statsData.value.by_type.length > 0
        ? statsData.value.by_type.slice(0, 3).map(t => `${t.weapon_type}(${t.count})`).join(', ')
        : '暂无数据'
      
      const wearDistribution = statsData.value.by_wear.length > 0
        ? statsData.value.by_wear.slice(0, 3).map(w => `${w.float_range}(${w.count})`).join(', ')
        : '暂无数据'

      return {
        totalCount: totalCount,
        typeDistribution,
        wearDistribution
      }
    })

    const priceStats = computed(() => {
      // 基于当前显示的数据计算购入价格统计
      const currentData = inventoryData.value || []
      let total_price = 0
      let priced_count = 0
      
      currentData.forEach(item => {
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          if (!isNaN(price)) {
            total_price += price
            priced_count++
          }
        }
      })
      
      return {
        priced_count: priced_count,
        total_price: total_price.toFixed(2),
        avg_price: priced_count > 0 ? (total_price / priced_count).toFixed(2) : '0.00',
        min_price: '0.00',
        max_price: '0.00'
      }
    })

    const yyypPriceStats = computed(() => {
      // 基于当前显示的数据计算悠悠有品价格统计
      const currentData = inventoryData.value || []
      let yyyp_total = 0
      let buy_total = 0
      let priced_count = 0
      
      currentData.forEach(item => {
        if (item.yyyp_price) {
          const price = parseFloat(item.yyyp_price)
          if (!isNaN(price)) {
            yyyp_total += price
            priced_count++
          }
        }
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          if (!isNaN(price)) {
            buy_total += price
          }
        }
      })
      
      const diff = (yyyp_total - buy_total).toFixed(2)
      
      return {
        priced_count: priced_count,
        total_price: yyyp_total.toFixed(2),
        avg_price: priced_count > 0 ? (yyyp_total / priced_count).toFixed(2) : '0.00',
        diff: diff
      }
    })

    const buffPriceStats = computed(() => {
      // 基于当前显示的数据计算BUFF价格统计（扣除2.5%手续费）
      const currentData = inventoryData.value || []
      let buff_total = 0
      let buff_total_after_fee = 0
      let buy_total = 0
      let priced_count = 0
      
      currentData.forEach(item => {
        if (item.buff_price) {
          const price = parseFloat(item.buff_price)
          if (!isNaN(price)) {
            buff_total += price
            // 扣除2.5%手续费
            buff_total_after_fee += price * 0.975
            priced_count++
          }
        }
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          if (!isNaN(price)) {
            buy_total += price
          }
        }
      })
      
      // 差价基于扣除手续费后的价格计算
      const diff = (buff_total_after_fee - buy_total).toFixed(2)
      
      return {
        priced_count: priced_count,
        total_price: buff_total_after_fee.toFixed(2),
        avg_price: priced_count > 0 ? (buff_total_after_fee / priced_count).toFixed(2) : '0.00',
        diff: diff
      }
    })

    const steamPriceStats = computed(() => {
      // 基于当前显示的数据计算Steam价格统计
      const currentData = inventoryData.value || []
      let steam_total = 0
      let buy_total = 0
      let priced_count = 0
      
      currentData.forEach(item => {
        if (item.steam_price) {
          const price = parseFloat(item.steam_price)
          if (!isNaN(price)) {
            steam_total += price
            priced_count++
          }
        }
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          if (!isNaN(price)) {
            buy_total += price
          }
        }
      })
      
      const diff = (steam_total - buy_total).toFixed(2)
      
      return {
        priced_count: priced_count,
        total_price: steam_total.toFixed(2),
        avg_price: priced_count > 0 ? (steam_total / priced_count).toFixed(2) : '0.00',
        diff: diff
      }
    })

    const loadSteamIdList = async () => {
      try {
        const response = await axios.get(`${API_BASE}/steam_ids`)
        console.log('Steam ID列表响应:', response.data)
        if (response.data.success) {
          steamIdList.value = response.data.data
          if (steamIdList.value.length > 0) {
            // 默认选择第一个 - 使用新格式 steamID（大写）
            selectedSteamId.value = steamIdList.value[0].steamID
            console.log('默认选择Steam ID:', selectedSteamId.value)
          } else {
            ElMessage.warning('没有找到库存数据，请先获取Steam库存')
          }
        }
      } catch (error) {
        console.error('加载Steam ID列表失败:', error)
        ElMessage.error('加载Steam ID列表失败: ' + (error.response?.data?.error || error.message))
      }
    }

    const loadInventoryData = async (reset = true) => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请选择Steam账号')
        return
      }
      
      // 如果是重置加载，清空数据和分页状态
      if (reset) {
        inventoryData.value = []
        currentOffset.value = 0
        hasMore.value = true
      }
      
      loading.value = true
      try {
        console.log('正在加载库存数据，Steam ID:', selectedSteamId.value)
        if (groupByItem.value) {
          // 加载分组数据 - 全部数据（分组模式不支持分页）
          const url = `${API_BASE}/inventory/grouped/${selectedSteamId.value}`
          console.log('请求URL:', url)
          const response = await axios.get(url)
          console.log('分组数据响应:', response.data)
          if (response.data.success) {
            groupedData.value = response.data.data.map(item => ({
              ...item,
              details: item.assetids.map((assetid, index) => ({
                assetid,
                weapon_float: item.weapon_floats[index],
                remark: item.remarks[index],
                buy_price: item.buy_prices && item.buy_prices[index] ? item.buy_prices[index] : null,
                yyyp_price: item.yyyp_prices && item.yyyp_prices[index] ? item.yyyp_prices[index] : null,
                buff_price: item.buff_prices && item.buff_prices[index] ? item.buff_prices[index] : null,
                steam_price: item.steam_prices && item.steam_prices[index] ? item.steam_prices[index] : null,
                order_time: item.order_times && item.order_times[index] ? item.order_times[index] : null
              }))
            }))
            console.log('分组数据已加载，总计:', groupedData.value.length)
          }
        } else {
          // 加载列表数据 - 使用分页
          const params = {
            search: searchText.value,
            weapon_type: weaponTypeFilter.value,
            float_range: floatRangeFilter.value,
            limit: pageSize.value,
            offset: currentOffset.value
          }
          
          const url = `${API_BASE}/inventory/${selectedSteamId.value}`
          console.log('请求URL:', url, '参数:', params)
          const response = await axios.get(url, { params })
          console.log('列表数据响应:', response.data)
          if (response.data.success) {
            const newData = response.data.data || []
            
            // 如果是重置，直接替换数据；否则追加数据
            if (reset) {
              inventoryData.value = newData
            } else {
              inventoryData.value = [...inventoryData.value, ...newData]
            }
            
            // 检查是否还有更多数据
            hasMore.value = newData.length === pageSize.value
            
            // 更新偏移量
            currentOffset.value += newData.length
            
            // 应用排序（包括默认排序）
            if (sortConfig.value.prop) {
              applySorting()
            }
            
            console.log('数据已加载，当前:', inventoryData.value.length, '条，还有更多:', hasMore.value, '排序:', sortConfig.value)
          } else {
            ElMessage.error(response.data.error || '加载数据失败')
          }
        }
        
        // 加载统计数据（只在重置时加载，避免频繁请求）
        if (reset) {
          await loadStats()
        }
      } catch (error) {
        console.error('加载库存数据失败:', error)
        ElMessage.error('加载数据失败: ' + (error.response?.data?.error || error.message))
      } finally {
        loading.value = false
      }
    }

    // 加载更多数据
    const loadMoreData = async () => {
      if (loadingMore.value || !hasMore.value || groupByItem.value) {
        return
      }
      
      loadingMore.value = true
      try {
        await loadInventoryData(false)
      } finally {
        loadingMore.value = false
      }
    }

    // 设置滚动监听（使用 Intersection Observer）
    const setupScrollObserver = () => {
      nextTick(() => {
        const triggerId = displayMode.value === 'card' ? 'load-more-trigger-card' : 'load-more-trigger'
        const trigger = document.getElementById(triggerId)
        if (trigger) {
          // 如果已有观察器，先断开
          if (trigger._observer) {
            trigger._observer.disconnect()
          }
          
          // 找到滚动容器
          let scrollContainer = null
          if (displayMode.value === 'card') {
            scrollContainer = trigger.closest('.card-container')
          } else {
            // 对于 el-table，找到表格的滚动容器
            const tableWrapper = trigger.closest('.table-container')
            if (tableWrapper) {
              scrollContainer = tableWrapper.querySelector('.el-table__body-wrapper')
            }
          }
          
          const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
              if (entry.isIntersecting && hasMore.value && !loadingMore.value && !loading.value && !groupByItem.value) {
                loadMoreData()
              }
            })
          }, {
            root: scrollContainer,
            rootMargin: '100px'
          })
          
          observer.observe(trigger)
          trigger._observer = observer
        }
      })
    }

    const loadStats = async () => {
      try {
        const response = await axios.get(`${API_BASE}/inventory/stats/${selectedSteamId.value}`)
        console.log('统计数据响应:', response.data)
        if (response.data.success) {
          statsData.value = response.data.data
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }

    const handleSteamIdChange = () => {
      console.log('Steam ID已切换:', selectedSteamId.value)
      loadInventoryData(true) // 重置加载
    }

    const handleReset = () => {
      searchText.value = ''
      weaponTypeFilter.value = ''
      floatRangeFilter.value = ''
      sortConfig.value = { prop: '', order: '' }
      loadInventoryData(true) // 重置加载
    }

    const handleGroupChange = () => {
      expandedRows.value = []
      loadInventoryData(true) // 重置加载
    }

    // 统一的排序函数
    const applySorting = () => {
      if (!sortConfig.value.prop || !sortConfig.value.order) return
      
      const { prop, order } = sortConfig.value
      
      inventoryData.value.sort((a, b) => {
        let valueA, valueB
        
        if (prop === 'buy_price') {
          // 价格排序
          valueA = parseFloat(a.buy_price) || 0
          valueB = parseFloat(b.buy_price) || 0
        } else if (prop === 'yyyp_price') {
          // 悠悠有品价格排序
          valueA = parseFloat(a.yyyp_price) || 0
          valueB = parseFloat(b.yyyp_price) || 0
        } else if (prop === 'buff_price') {
          // BUFF价格排序
          valueA = parseFloat(a.buff_price) || 0
          valueB = parseFloat(b.buff_price) || 0
        } else if (prop === 'order_time') {
          // 入库时间排序
          valueA = a.order_time ? new Date(a.order_time).getTime() : 0
          valueB = b.order_time ? new Date(b.order_time).getTime() : 0
        } else if (prop === 'weapon_float') {
          // 磨损值排序
          valueA = parseFloat(a.weapon_float) || 999999 // 没有磨损值的排在最后
          valueB = parseFloat(b.weapon_float) || 999999
        } else if (prop === 'float_range') {
          // 磨损等级排序（按照游戏内的品质顺序）
          const floatRangeOrder = {
            '崭新出厂': 1,
            '略有磨损': 2,
            '久经沙场': 3,
            '破损不堪': 4,
            '战痕累累': 5
          }
          valueA = floatRangeOrder[a.float_range] || 999
          valueB = floatRangeOrder[b.float_range] || 999
        } else if (prop === 'remark') {
          // 备注排序（有备注的在前，无备注的在后）
          valueA = a.remark ? 0 : 1
          valueB = b.remark ? 0 : 1
        }
        
        if (order === 'asc') {
          return valueA - valueB
        } else {
          return valueB - valueA
        }
      })
    }

    // Element Plus 表格的排序事件处理
    const handleSortChange = ({ prop, order }) => {
      console.log('排序改变:', prop, order)
      
      if (!order) {
        // 取消排序
        sortConfig.value = { prop: '', order: '' }
        loadInventoryData(true)
        return
      }
      
      // 设置排序配置
      sortConfig.value = { 
        prop, 
        order: order === 'ascending' ? 'asc' : 'desc' 
      }
      
      // 应用排序
      applySorting()
    }

    const isExpanded = (itemName) => {
      return expandedRows.value.includes(itemName)
    }

    const toggleExpand = (row) => {
      const index = expandedRows.value.indexOf(row.item_name)
      if (index > -1) {
        expandedRows.value.splice(index, 1)
      } else {
        expandedRows.value.push(row.item_name)
      }
    }

    const handleExpandChange = (row, expandedRowsArray) => {
      expandedRows.value = expandedRowsArray.map(r => r.item_name)
    }

    // 开始编辑价格
    const startEdit = (row) => {
      editingAssetId.value = row.assetid
      originalPrice.value = row.buy_price || ''
      editingPrice.value = row.buy_price || ''
      
      // 使用nextTick确保input已渲染后聚焦
      nextTick(() => {
        const input = document.getElementById(`price-input-${row.assetid}`)
        if (input) {
          input.focus()
          input.select() // 选中所有文本，方便修改
        }
      })
    }

    // 取消编辑
    const cancelEdit = () => {
      editingAssetId.value = null
      editingPrice.value = ''
      originalPrice.value = ''
    }

    // 完成编辑价格
    const finishEdit = async (row) => {
      const newPrice = editingPrice.value
      const oldPrice = originalPrice.value
      
      // 如果价格没有改变，直接取消编辑
      if (newPrice === oldPrice) {
        cancelEdit()
        return
      }
      
      // 如果价格为空，提示用户
      if (!newPrice || newPrice.trim() === '') {
        ElMessage.warning('请输入有效的价格')
        return
      }
      
      // 先更新UI（乐观更新）
      row.buy_price = newPrice
      const currentAssetId = editingAssetId.value
      cancelEdit()
      
      // 异步发送请求到后端
      try {
        const response = await axios.put(
          `${API_CONFIG.BASE_URL}/webInventoryV1/inventory/buy_price/${selectedSteamId.value}/${currentAssetId}`,
          { buy_price: newPrice }
        )
        
        if (response.data.success) {
          ElMessage.success('价格更新成功')
          // 只更新统计数据，不重新加载整个列表
          await loadInventoryStats()
        } else {
          // 如果失败，恢复原价格
          row.buy_price = oldPrice
          ElMessage.error('价格更新失败: ' + response.data.error)
        }
      } catch (error) {
        // 如果失败，恢复原价格
        row.buy_price = oldPrice
        console.error('更新价格失败:', error)
        ElMessage.error('更新价格失败: ' + error.message)
      }
    }

    // 获取武器图片路径
    const getWeaponImage = (steamHashName) => {
      if (!steamHashName) {
        return null // 如果没有steam_hash_name，返回null，不显示图片
      }
      // 检查是否已经在404缓存中
      if (image404Cache.value.has(steamHashName)) {
        return null // 如果之前404过，直接返回null，不显示图片
      }
      // 将空格替换为下划线，并添加.png扩展名
      const imageName = steamHashName.replace(/\s+/g, '_') + '.png'
      return `/weapon_imgs/${imageName}`
    }

    // 处理图片加载错误
    const handleImageError = (event, steamHashName) => {
      // 将失败的steam_hash_name添加到404缓存中
      if (steamHashName) {
        image404Cache.value.add(steamHashName)
      }
      // 隐藏图片或显示占位符
      event.target.style.display = 'none'
      // 或者可以设置一个占位符图片
      // event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzMzMzMzMyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+Tm8gSW1hZ2U8L3RleHQ+PC9zdmc+'
    }

    // 获取价格差异样式类
    const getPriceDiffClass = (marketPrice, buyPrice) => {
      if (!marketPrice || !buyPrice) return ''
      const diff = parseFloat(marketPrice) - parseFloat(buyPrice)
      return diff >= 0 ? 'price-profit' : 'price-loss'
    }

    // 单独加载统计数据（不重新加载列表）
    const loadInventoryStats = async () => {
      try {
        const statsResponse = await axios.get(
          `${API_CONFIG.BASE_URL}/webInventoryV1/inventory/stats/${selectedSteamId.value}`
        )
        if (statsResponse.data.success) {
          inventoryStats.value = statsResponse.data.data
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }

    // 获取Steam库存
    const fetchSteamInventory = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }

      try {
        fetchingInventory.value = true

        // 直接调用Spider接口，只传steamId
        // Spider会自己调用后端API查询config表获取cookie
        const spiderResponse = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/steamSpiderV1/getInventory`,
          {
            steamId: selectedSteamId.value
          }
        )

        if (spiderResponse.data.success) {
          ElMessage.success(spiderResponse.data.message || '库存获取成功')
          // 重新加载库存数据
          await loadInventoryData()
        } else {
          ElMessage.error(spiderResponse.data.message || '库存获取失败')
        }
      } catch (error) {
        console.error('获取Steam库存失败:', error)
        ElMessage.error('获取库存失败: ' + (error.response?.data?.message || error.message))
      } finally {
        fetchingInventory.value = false
      }
    }

    // 获取悠悠有品价格
    const fetchYYYPPrice = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }

      try {
        fetchingYYYPPrice.value = true
        
        // 调用Spider API获取悠悠有品价格
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getYYYPPrice`,
          {
            steamId: selectedSteamId.value
          }
        )
        
        if (response.data.success) {
          ElMessage.success(response.data.message || '悠悠有品价格获取成功')
          // 重新加载库存数据和统计信息
          await loadInventoryData()
        } else {
          ElMessage.error(response.data.message || '悠悠有品价格获取失败')
        }
        
      } catch (error) {
        console.error('获取悠悠有品价格失败:', error)
        ElMessage.error('获取价格失败: ' + (error.response?.data?.message || error.message))
      } finally {
        fetchingYYYPPrice.value = false
      }
    }

    // 获取BUFF价格
    const fetchBuffPrice = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }

      try {
        fetchingBuffPrice.value = true
        
        // 调用Spider API获取BUFF价格
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/buffSpiderV1/getBUFFPrice`,
          {
            steamId: selectedSteamId.value
          }
        )
        
        if (response.data.success) {
          ElMessage.success(response.data.message || 'BUFF价格获取成功')
          // 重新加载库存数据和统计信息
          await loadInventoryData()
        } else {
          ElMessage.error(response.data.message || 'BUFF价格获取失败')
        }
        
      } catch (error) {
        console.error('获取BUFF价格失败:', error)
        ElMessage.error('获取价格失败: ' + (error.response?.data?.message || error.message))
      } finally {
        fetchingBuffPrice.value = false
      }
    }

    onMounted(async () => {
      await loadSteamIdList()
      if (selectedSteamId.value) {
        loadInventoryData(true)
      }
      
      // 设置滚动监听
      setupScrollObserver()
      
      // 监听显示模式变化，重新设置观察器
      watch(displayMode, () => {
        setupScrollObserver()
      })
      
      // 监听数据变化，重新设置观察器（数据加载后）
      watch(inventoryData, () => {
        setupScrollObserver()
      })
    })

    return {
      loading,
      fetchingInventory,
      fetchingYYYPPrice,
      fetchingBuffPrice,
      inventoryData,
      groupedData,
      inventoryStats,
      priceStats,
      yyypPriceStats,
      buffPriceStats,
      steamPriceStats,
      searchText,
      weaponTypeFilter,
      floatRangeFilter,
      groupByItem,
      displayMode,
      expandedRows,
      steamIdList,
      selectedSteamId,
      sortConfig,
      getWeaponImage,
      handleImageError,
      getPriceDiffClass,
      loadInventoryData,
      loadMoreData,
      handleReset,
      handleGroupChange,
      handleSteamIdChange,
      handleSortChange,
      hasMore,
      loadingMore,
      isExpanded,
      toggleExpand,
      handleExpandChange,
      editingAssetId,
      editingPrice,
      startEdit,
      finishEdit,
      cancelEdit,
      fetchSteamInventory,
      fetchYYYPPrice,
      fetchBuffPrice
    }
  }
}
</script>

<style scoped>
.steam-id-select {
  min-width: 250px;
  max-width: 350px;
}

.search-input {
  min-width: 200px;
  flex: 1;
  max-width: 300px;
}

.type-select,
.wear-select {
  min-width: 120px;
  max-width: 180px;
}

.action-button {
  min-width: 140px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
}

.action-button :deep(.el-icon) {
  margin-right: 4px;
}

.inventory-stats {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.table-container {
  position: relative;
}

.table-wrapper {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.table-footer {
  padding: 1rem;
  text-align: right;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-number {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: bold;
  color: #fff;
  margin-top: clamp(0.5rem, 1vw, 0.625rem);
}

.stat-text {
  font-size: clamp(0.75rem, 1.5vw, 0.875rem);
  color: #ccc;
  margin-top: clamp(0.5rem, 1vw, 0.625rem);
  line-height: 1.5;
}

.stat-price-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: clamp(0.5rem, 1vw, 0.625rem);
}

.stat-diff-right {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: bold;
  margin: 0;
}

.pagination {
  margin-top: clamp(1rem, 3vw, 1.25rem);
  display: flex;
  justify-content: center;
}

.expand-content {
  padding: 1rem;
  background-color: var(--bg-secondary) !important;
}

.expand-content :deep(.el-table) {
  background-color: transparent !important;
}

.expand-content :deep(.el-table__body-wrapper) {
  background-color: transparent !important;
}

.expand-content :deep(.el-table th.el-table__cell) {
  background-color: var(--bg-tertiary) !important;
}

.expand-content :deep(.el-table td.el-table__cell) {
  background-color: transparent !important;
}

.expand-content :deep(.el-table__row) {
  background-color: transparent !important;
}

.expand-content :deep(.el-table__expanded-cell) {
  background-color: var(--bg-secondary) !important;
}

:deep(.el-table__expanded-cell) {
  background-color: var(--bg-secondary) !important;
  padding: 0 !important;
}

:deep(.el-table) {
  background-color: transparent;
  color: #fff;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

:deep(.el-table th) {
  background-color: var(--bg-tertiary);
  color: #fff;
  border-bottom: 1px solid var(--border-default);
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
}

:deep(.el-table td) {
  background-color: transparent !important;
  border-bottom: 1px solid var(--border-default);
  color: #ccc;
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
}

:deep(.el-table tr:hover > td) {
  background-color: rgba(255, 255, 255, 0.05) !important;
}

:deep(.el-table__expanded-cell) {
  background-color: transparent !important;
}

:deep(.el-input__inner) {
  background-color: #2a2a2a;
  border-color: #333;
  color: #fff;
}

:deep(.el-select .el-input__inner) {
  background-color: #2a2a2a;
  border-color: #333;
  color: #fff;
}

:deep(.el-switch) {
  --el-switch-on-color: #4CAF50;
  --el-switch-off-color: #909399;
}

:deep(.el-switch__label) {
  color: #ccc;
}

:deep(.el-table .el-table__cell) {
  word-break: break-word;
}

:deep(.el-table__header th) {
  user-select: none;
}

/* 卡片显示样式 */
.card-container {
  margin-top: 1rem;
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 1rem;
}

.inventory-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  aspect-ratio: 1;
}

.inventory-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border-color: var(--el-color-primary);
}

.card-image {
  width: 100%;
  aspect-ratio: 1;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  color: #999;
  font-size: 0.9rem;
}

.card-content {
  padding: 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.card-title {
  font-size: 0.9rem;
  font-weight: bold;
  color: #fff;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
  min-height: 2.8em;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.8rem;
}

.card-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  color: #999;
  font-size: 0.75rem;
}

.info-value {
  color: #ccc;
  font-size: 0.75rem;
  text-align: right;
  flex: 1;
  margin-left: 0.5rem;
}

.card-prices {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color);
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}

.price-label {
  color: #999;
  font-size: 0.75rem;
}

.price-value {
  color: #fff;
  font-weight: bold;
  font-size: 0.85rem;
}

.buy-price {
  color: #4CAF50;
}

.price-profit {
  color: #f56c6c;
}

.price-loss {
  color: #4CAF50;
}

.card-footer {
  margin-top: 0.5rem;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    padding: 0.5rem;
  }

  .card-content {
    padding: 0.75rem;
  }

  .card-title {
    font-size: 0.85rem;
  }

  .info-label,
  .info-value,
  .price-label,
  .price-value {
    font-size: 0.7rem;
  }
}

@media (max-width: 768px) {
  .search-input,
  .type-select,
  .wear-select {
    min-width: unset;
    width: 100%;
    max-width: none;
  }
  
  :deep(.el-table) {
    font-size: 0.75rem;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 0.5rem 0.25rem;
  }
}
</style>
