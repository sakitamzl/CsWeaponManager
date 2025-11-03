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
            :key="item.steam_id"
            :label="`${item.steam_id} (${item.item_count}件)`"
            :value="item.steam_id"
          >
            <span style="float: left">{{ item.steam_id }}</span>
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
    <div class="table-container" v-if="!groupByItem">
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
      </div>
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
import { ref, computed, onMounted, nextTick } from 'vue'
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
    const expandedRows = ref([])
    const editingAssetId = ref(null) // 正在编辑的资产ID
    const editingPrice = ref('') // 编辑中的价格
    const originalPrice = ref('') // 原始价格
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
            // 默认选择第一个
            selectedSteamId.value = steamIdList.value[0].steam_id
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

    const loadInventoryData = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请选择Steam账号')
        return
      }
      
      loading.value = true
      try {
        console.log('正在加载库存数据，Steam ID:', selectedSteamId.value)
        if (groupByItem.value) {
          // 加载分组数据 - 全部数据
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
          // 加载列表数据 - 全部数据，不使用limit
          const params = {
            search: searchText.value,
            weapon_type: weaponTypeFilter.value,
            float_range: floatRangeFilter.value,
            limit: 9999, // 获取全部数据
            offset: 0
          }
          
          const url = `${API_BASE}/inventory/${selectedSteamId.value}`
          console.log('请求URL:', url, '参数:', params)
          const response = await axios.get(url, { params })
          console.log('列表数据响应:', response.data)
          if (response.data.success) {
            inventoryData.value = response.data.data
            
            // 应用排序（包括默认排序）
            if (sortConfig.value.prop) {
              applySorting()
            }
            
            console.log('数据已加载，总计:', inventoryData.value.length, '排序:', sortConfig.value)
          } else {
            ElMessage.error(response.data.error || '加载数据失败')
          }
        }
        
        // 加载统计数据
        await loadStats()
      } catch (error) {
        console.error('加载库存数据失败:', error)
        ElMessage.error('加载数据失败: ' + (error.response?.data?.error || error.message))
      } finally {
        loading.value = false
      }
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
      loadInventoryData()
    }

    const handleReset = () => {
      searchText.value = ''
      weaponTypeFilter.value = ''
      floatRangeFilter.value = ''
      sortConfig.value = { prop: '', order: '' }
      loadInventoryData()
    }

    const handleGroupChange = () => {
      expandedRows.value = []
      loadInventoryData()
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
        loadInventoryData()
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
        loadInventoryData()
      }
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
      expandedRows,
      steamIdList,
      selectedSteamId,
      sortConfig,
      loadInventoryData,
      handleReset,
      handleGroupChange,
      handleSteamIdChange,
      handleSortChange,
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

.table-footer {
  padding: 1rem;
  text-align: right;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-color);
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
