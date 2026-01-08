<template>
  <div>
    <!-- 数据源切换 -->
    <div class="data-source-switch">
      <el-radio-group v-model="dataSource" @change="handleDataSourceChange">
        <el-radio-button label="inventory">库存数据</el-radio-button>
        <el-radio-button label="components">库存组件</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 统计数据卡片 -->
    <div class="stats-container">
      <div class="grid grid-7">
        <div class="card">
          <h3>总购买金额</h3>
          <p class="stat-number">¥{{ buyStats.totalAmount }}</p>
        </div>
        <div class="card">
          <h3>总出售金额</h3>
          <p class="stat-number">¥{{ sellStats.totalAmount }}</p>
        </div>
        <div class="card">
          <h3>总库存数量</h3>
          <p class="stat-number">{{ inventoryStats.totalCount }}</p>
        </div>
        <div class="card">
          <h3>购入总价值</h3>
          <p class="stat-number">¥{{ inventoryStats.total_price }}</p>
        </div>
        <div class="card">
          <h3>悠悠有品最低价</h3>
          <div class="stat-price-container">
            <p class="stat-number">¥{{ inventoryStats.yyyp_price }}</p>
            <p class="stat-diff" :style="{ color: inventoryStats.yyyp_diff >= 0 ? '#f56c6c' : '#4CAF50' }">
              {{ inventoryStats.yyyp_diff >= 0 ? '+' : '' }}¥{{ inventoryStats.yyyp_diff }}
            </p>
          </div>
        </div>
        <div class="card">
          <h3>BUFF最低价</h3>
          <div class="stat-price-container">
            <p class="stat-number">¥{{ inventoryStats.buff_price }}</p>
            <p class="stat-diff" :style="{ color: inventoryStats.buff_diff >= 0 ? '#f56c6c' : '#4CAF50' }">
              {{ inventoryStats.buff_diff >= 0 ? '+' : '' }}¥{{ inventoryStats.buff_diff }}
            </p>
          </div>
        </div>
        <div class="card">
          <h3>Steam参考价</h3>
          <div class="stat-price-container">
            <p class="stat-number">¥{{ inventoryStats.steam_price }}</p>
            <p class="stat-diff" :style="{ color: inventoryStats.steam_diff >= 0 ? '#f56c6c' : '#4CAF50' }">
              {{ inventoryStats.steam_diff >= 0 ? '+' : '' }}¥{{ inventoryStats.steam_diff }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 价格区间分析图表 -->
    <div class="chart-container">
      <div class="card chart-card">
        <h3>库存饰品价格区间分析（按总价值分布）</h3>
        <div ref="priceChartRef" class="price-chart"></div>
      </div>
      <div class="card chart-card">
        <h3>库存饰品价格区间分析（按数量分布）</h3>
        <div ref="countChartRef" class="price-chart"></div>
      </div>
    </div>

    <!-- 库存组件价格区间分析图表 -->
    <div class="chart-container">
      <div class="card chart-card">
        <h3>库存组件价格区间分析（按总价值分布）</h3>
        <div ref="componentPriceChartRef" class="price-chart"></div>
      </div>
      <div class="card chart-card">
        <h3>库存组件价格区间分析（按数量分布）</h3>
        <div ref="componentCountChartRef" class="price-chart"></div>
      </div>
    </div>

    <!-- 饰品列表弹窗 -->
    <el-dialog
      v-model="itemListVisible"
      :title="`价格区间 ${selectedRange} 的饰品列表`"
      width="80%"
      :close-on-click-modal="true"
      class="item-list-dialog"
    >
      <div class="item-list-container">
        <div class="item-list-header">
          <span>共 {{ filteredItems.length }} 件饰品</span>
        </div>
        <el-table
          :data="filteredItems"
          style="width: 100%"
          max-height="500"
          :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        >
          <el-table-column label="饰品名称" min-width="300">
            <template #default="scope">
              <div class="item-name-cell">
                {{ scope.row.item_name }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="weapon_type" label="类型" width="120" />
          <el-table-column label="磨损值" width="150">
            <template #default="scope">
              <span v-if="scope.row.weapon_float">{{ scope.row.weapon_float }}</span>
              <span v-else style="color: #888;">N/A</span>
            </template>
          </el-table-column>
          <el-table-column label="购入价格" width="120" align="right">
            <template #default="scope">
              <span style="color: #4CAF50; font-weight: bold;">
                ¥{{ parseFloat(scope.row.buy_price).toFixed(2) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="悠悠有品" width="120" align="right">
            <template #default="scope">
              <span v-if="scope.row.yyyp_price" style="color: #fff;">
                ¥{{ parseFloat(scope.row.yyyp_price).toFixed(2) }}
              </span>
              <span v-else style="color: #888;">-</span>
            </template>
          </el-table-column>
          <el-table-column label="BUFF" width="120" align="right">
            <template #default="scope">
              <span v-if="scope.row.buff_price" style="color: #fff;">
                ¥{{ parseFloat(scope.row.buff_price).toFixed(2) }}
              </span>
              <span v-else style="color: #888;">-</span>
            </template>
          </el-table-column>
          <el-table-column label="Steam" width="120" align="right">
            <template #default="scope">
              <span v-if="scope.row.steam_price" style="color: #fff;">
                ¥{{ parseFloat(scope.row.steam_price).toFixed(2) }}
              </span>
              <span v-else style="color: #888;">-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import { API_CONFIG } from '@/config/api.js'
import * as echarts from 'echarts'

export default {
  name: 'Home',
  setup() {
    const buyStats = ref({
      totalAmount: '0.00'
    })
    const sellStats = ref({
      totalAmount: '0.00'
    })
    const inventoryStats = ref({
      totalCount: 0,
      total_price: '0.00',
      yyyp_price: '0.00',
      yyyp_diff: '0.00',
      buff_price: '0.00',
      buff_diff: '0.00',
      steam_price: '0.00',
      steam_diff: '0.00'
    })
    const steamIdList = ref([])
    const selectedSteamId = ref('')
    const priceChartRef = ref(null)
    const countChartRef = ref(null)
    const componentPriceChartRef = ref(null)
    const componentCountChartRef = ref(null)
    let priceChart = null
    let countChart = null
    let componentPriceChart = null
    let componentCountChart = null
    
    // 数据源选择
    const dataSource = ref('inventory') // 'inventory' 或 'components'
    
    // 饰品列表相关
    const itemListVisible = ref(false)
    const selectedRange = ref('')
    const filteredItems = ref([])
    const allInventoryData = ref([])
    const allComponentsData = ref([])

    // 加载购买统计数据
    const loadBuyStats = async () => {
      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/webBuyV1/getBuyStats`)
        if (response.data) {
          buyStats.value = {
            totalAmount: response.data.total_amount?.toFixed(2) || '0.00'
          }
        }
      } catch (error) {
        console.error('加载购买统计失败:', error)
      }
    }

    // 加载出售统计数据
    const loadSellStats = async () => {
      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/webSellV1/getSellStats`)
        if (response.data) {
          sellStats.value = {
            totalAmount: response.data.total_amount?.toFixed(2) || '0.00'
          }
        }
      } catch (error) {
        console.error('加载出售统计失败:', error)
      }
    }

    // 加载Steam ID列表
    const loadSteamIdList = async () => {
      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/webInventoryV1/steam_ids`)
        if (response.data.success && response.data.data.length > 0) {
          steamIdList.value = response.data.data
          selectedSteamId.value = steamIdList.value[0].steamID
        }
      } catch (error) {
        console.error('加载Steam ID列表失败:', error)
      }
    }

    // 加载库存统计数据
    const loadInventoryStats = async () => {
      if (!selectedSteamId.value) return

      try {
        // 获取库存数据
        const response = await axios.get(
          `${API_CONFIG.BASE_URL}/webInventoryV1/inventory/${selectedSteamId.value}`,
          {
            params: {
              limit: 9999,
              offset: 0
            }
          }
        )
        
        if (response.data.success) {
          const inventoryData = response.data.data
          allInventoryData.value = inventoryData // 保存完整数据用于后续筛选
          
          // 计算统计数据
          let totalCount = inventoryData.length
          let buy_total = 0
          let yyyp_total = 0
          let buff_total = 0
          let buff_total_after_fee = 0
          let steam_total = 0
          
          inventoryData.forEach(item => {
            if (item.buy_price) {
              const price = parseFloat(item.buy_price)
              if (!isNaN(price)) {
                buy_total += price
              }
            }
            if (item.yyyp_price) {
              const price = parseFloat(item.yyyp_price)
              if (!isNaN(price)) {
                yyyp_total += price
              }
            }
            if (item.buff_price) {
              const price = parseFloat(item.buff_price)
              if (!isNaN(price)) {
                buff_total += price
                // BUFF扣除2.5%手续费
                buff_total_after_fee += price * 0.975
              }
            }
            if (item.steam_price) {
              const price = parseFloat(item.steam_price)
              if (!isNaN(price)) {
                steam_total += price
              }
            }
          })
          
          inventoryStats.value = {
            totalCount: totalCount,
            total_price: buy_total.toFixed(2),
            yyyp_price: yyyp_total.toFixed(2),
            yyyp_diff: (yyyp_total - buy_total).toFixed(2),
            buff_price: buff_total_after_fee.toFixed(2),
            buff_diff: (buff_total_after_fee - buy_total).toFixed(2),
            steam_price: steam_total.toFixed(2),
            steam_diff: (steam_total - buy_total).toFixed(2)
          }

          // 如果当前是库存数据源，加载价格区间分析图表
          if (dataSource.value === 'inventory') {
            await loadPriceRangeChart(inventoryData)
            await loadCountRangeChart(inventoryData)
          }
        }
      } catch (error) {
        console.error('加载库存统计失败:', error)
      }
    }

    // 加载库存组件统计数据
    const loadComponentsStats = async () => {
      if (!selectedSteamId.value) return

      try {
        // 获取库存组件数据
        const response = await axios.get(
          `${API_CONFIG.BASE_URL}/webStockComponentsV1/components/${selectedSteamId.value}`,
          {
            params: {
              search: '',
              page: 1,
              page_size: 9999
            }
          }
        )
        
        if (response.data.success) {
          const componentsData = response.data.data
          allComponentsData.value = componentsData // 保存完整数据用于后续筛选
          
          // 加载库存组件价格区间分析图表
          await loadComponentPriceRangeChart(componentsData)
          await loadComponentCountRangeChart(componentsData)
        }
      } catch (error) {
        console.error('加载库存组件统计失败:', error)
      }
    }

    // 根据价格区间筛选饰品
    const filterItemsByRange = (rangeName) => {
      const priceRanges = {
        '¥0-100': { min: 0, max: 100 },
        '¥101-500': { min: 101, max: 500 },
        '¥501-1000': { min: 501, max: 1000 },
        '¥1001-2000': { min: 1001, max: 2000 },
        '¥2001-5000': { min: 2001, max: 5000 },
        '¥5001-10000': { min: 5001, max: 10000 },
        '¥10001-20000': { min: 10001, max: 20000 },
        '¥20001+': { min: 20001, max: Infinity }
      }

      const range = priceRanges[rangeName]
      if (!range) return []

      return allInventoryData.value.filter(item => {
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          return !isNaN(price) && price >= range.min && price <= range.max
        }
        return false
      })
    }

    // 根据价格区间筛选库存组件
    const filterComponentsByRange = (rangeName) => {
      const priceRanges = {
        '¥0-100': { min: 0, max: 100 },
        '¥101-500': { min: 101, max: 500 },
        '¥501-1000': { min: 501, max: 1000 },
        '¥1001-2000': { min: 1001, max: 2000 },
        '¥2001-5000': { min: 2001, max: 5000 },
        '¥5001-10000': { min: 5001, max: 10000 },
        '¥10001-20000': { min: 10001, max: 20000 },
        '¥20001+': { min: 20001, max: Infinity }
      }

      const range = priceRanges[rangeName]
      if (!range) return []

      return allComponentsData.value.filter(item => {
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          return !isNaN(price) && price >= range.min && price <= range.max
        }
        return false
      })
    }

    // 加载价格区间分析图表
    const loadPriceRangeChart = async (inventoryData) => {
      await nextTick()
      
      if (!priceChartRef.value) return

      // 定义价格区间
      const priceRanges = [
        { name: '0-100', min: 0, max: 100, count: 0, totalValue: 0 },
        { name: '101-500', min: 101, max: 500, count: 0, totalValue: 0 },
        { name: '501-1000', min: 501, max: 1000, count: 0, totalValue: 0 },
        { name: '1001-2000', min: 1001, max: 2000, count: 0, totalValue: 0 },
        { name: '2001-5000', min: 2001, max: 5000, count: 0, totalValue: 0 },
        { name: '5001-10000', min: 5001, max: 10000, count: 0, totalValue: 0 },
        { name: '10001-20000', min: 10001, max: 20000, count: 0, totalValue: 0 },
        { name: '20001+', min: 20001, max: Infinity, count: 0, totalValue: 0 }
      ]

      // 统计每个价格区间的数量和总价值
      inventoryData.forEach(item => {
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          if (!isNaN(price)) {
            for (let range of priceRanges) {
              if (price >= range.min && price <= range.max) {
                range.count++
                range.totalValue += price
                break
              }
            }
          }
        }
      })

      // 过滤掉数量为0的区间
      const chartData = priceRanges
        .filter(range => range.count > 0)
        .map(range => ({
          name: `¥${range.name}`,
          value: range.totalValue,
          count: range.count,
          avgPrice: range.totalValue / range.count
        }))

      // 初始化或更新图表
      if (!priceChart) {
        priceChart = echarts.init(priceChartRef.value)
        
        // 添加点击事件
        priceChart.on('click', (params) => {
          if (params.componentType === 'series') {
            selectedRange.value = params.name
            filteredItems.value = filterItemsByRange(params.name)
            itemListVisible.value = true
          }
        })
      }

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const data = params.data
            return `${params.seriesName}<br/>
                    ${params.name}<br/>
                    件数: ${data.count} 件<br/>
                    总价值: ¥${data.value.toFixed(2)}<br/>
                    平均价格: ¥${data.avgPrice.toFixed(2)}<br/>
                    占比: ${params.percent}%`
          },
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#333',
          textStyle: {
            color: '#fff'
          }
        },
        legend: {
          orient: 'vertical',
          right: '5%',
          top: 'center',
          textStyle: {
            color: '#fff',
            fontSize: 12
          },
          formatter: (name) => {
            const item = chartData.find(d => d.name === name)
            if (item) {
              return `${name}\n${item.count}件 ¥${item.value.toFixed(0)}`
            }
            return name
          }
        },
        series: [
          {
            name: '价格区间分布',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#1a1a1a',
              borderWidth: 2
            },
            label: {
              show: true,
              formatter: (params) => {
                return `${params.name}\n${params.data.count}件\n¥${params.data.value.toFixed(0)}`
              },
              color: '#fff',
              fontSize: 11
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 14,
                fontWeight: 'bold'
              },
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            labelLine: {
              show: true,
              lineStyle: {
                color: '#888'
              }
            },
            data: chartData,
            color: [
              '#5470c6',
              '#91cc75',
              '#fac858',
              '#ee6666',
              '#73c0de',
              '#3ba272',
              '#fc8452',
              '#9a60b4'
            ]
          }
        ]
      }

      priceChart.setOption(option)

      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    }

    // 加载数量区间分析图表
    const loadCountRangeChart = async (inventoryData) => {
      await nextTick()
      
      if (!countChartRef.value) return

      // 定义价格区间
      const priceRanges = [
        { name: '0-100', min: 0, max: 100, count: 0, totalValue: 0 },
        { name: '101-500', min: 101, max: 500, count: 0, totalValue: 0 },
        { name: '501-1000', min: 501, max: 1000, count: 0, totalValue: 0 },
        { name: '1001-2000', min: 1001, max: 2000, count: 0, totalValue: 0 },
        { name: '2001-5000', min: 2001, max: 5000, count: 0, totalValue: 0 },
        { name: '5001-10000', min: 5001, max: 10000, count: 0, totalValue: 0 },
        { name: '10001-20000', min: 10001, max: 20000, count: 0, totalValue: 0 },
        { name: '20001+', min: 20001, max: Infinity, count: 0, totalValue: 0 }
      ]

      // 统计每个价格区间的数量和总价值
      inventoryData.forEach(item => {
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          if (!isNaN(price)) {
            for (let range of priceRanges) {
              if (price >= range.min && price <= range.max) {
                range.count++
                range.totalValue += price
                break
              }
            }
          }
        }
      })

      // 过滤掉数量为0的区间
      const chartData = priceRanges
        .filter(range => range.count > 0)
        .map(range => ({
          name: `¥${range.name}`,
          value: range.count,
          totalValue: range.totalValue,
          avgPrice: range.totalValue / range.count
        }))

      // 初始化或更新图表
      if (!countChart) {
        countChart = echarts.init(countChartRef.value)
        
        // 添加点击事件
        countChart.on('click', (params) => {
          if (params.componentType === 'series') {
            selectedRange.value = params.name
            filteredItems.value = filterItemsByRange(params.name)
            itemListVisible.value = true
          }
        })
      }

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const data = params.data
            return `${params.seriesName}<br/>
                    ${params.name}<br/>
                    件数: ${data.value} 件<br/>
                    总价值: ¥${data.totalValue.toFixed(2)}<br/>
                    平均价格: ¥${data.avgPrice.toFixed(2)}<br/>
                    占比: ${params.percent}%`
          },
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#333',
          textStyle: {
            color: '#fff'
          }
        },
        legend: {
          orient: 'vertical',
          right: '5%',
          top: 'center',
          textStyle: {
            color: '#fff',
            fontSize: 12
          },
          formatter: (name) => {
            const item = chartData.find(d => d.name === name)
            if (item) {
              return `${name}\n${item.value}件`
            }
            return name
          }
        },
        series: [
          {
            name: '数量区间分布',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#1a1a1a',
              borderWidth: 2
            },
            label: {
              show: true,
              formatter: (params) => {
                return `${params.name}\n${params.data.value}件`
              },
              color: '#fff',
              fontSize: 11
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 14,
                fontWeight: 'bold'
              },
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            labelLine: {
              show: true,
              lineStyle: {
                color: '#888'
              }
            },
            data: chartData,
            color: [
              '#5470c6',
              '#91cc75',
              '#fac858',
              '#ee6666',
              '#73c0de',
              '#3ba272',
              '#fc8452',
              '#9a60b4'
            ]
          }
        ]
      }

      countChart.setOption(option)

      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    }

    // 加载库存组件价格区间分析图表（按总价值）
    const loadComponentPriceRangeChart = async (componentsData) => {
      await nextTick()
      
      if (!componentPriceChartRef.value) return

      // 定义价格区间
      const priceRanges = [
        { name: '0-100', min: 0, max: 100, count: 0, totalValue: 0 },
        { name: '101-500', min: 101, max: 500, count: 0, totalValue: 0 },
        { name: '501-1000', min: 501, max: 1000, count: 0, totalValue: 0 },
        { name: '1001-2000', min: 1001, max: 2000, count: 0, totalValue: 0 },
        { name: '2001-5000', min: 2001, max: 5000, count: 0, totalValue: 0 },
        { name: '5001-10000', min: 5001, max: 10000, count: 0, totalValue: 0 },
        { name: '10001-20000', min: 10001, max: 20000, count: 0, totalValue: 0 },
        { name: '20001+', min: 20001, max: Infinity, count: 0, totalValue: 0 }
      ]

      // 统计每个价格区间的数量和总价值
      componentsData.forEach(item => {
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          if (!isNaN(price)) {
            for (let range of priceRanges) {
              if (price >= range.min && price <= range.max) {
                range.count++
                range.totalValue += price
                break
              }
            }
          }
        }
      })

      // 过滤掉数量为0的区间
      const chartData = priceRanges
        .filter(range => range.count > 0)
        .map(range => ({
          name: `¥${range.name}`,
          value: range.totalValue,
          count: range.count,
          avgPrice: range.totalValue / range.count
        }))

      // 初始化或更新图表
      if (!componentPriceChart) {
        componentPriceChart = echarts.init(componentPriceChartRef.value)
        
        // 添加点击事件
        componentPriceChart.on('click', (params) => {
          if (params.componentType === 'series') {
            selectedRange.value = params.name
            filteredItems.value = filterComponentsByRange(params.name)
            itemListVisible.value = true
          }
        })
      }

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const data = params.data
            return `${params.seriesName}<br/>
                    ${params.name}<br/>
                    件数: ${data.count} 件<br/>
                    总价值: ¥${data.value.toFixed(2)}<br/>
                    平均价格: ¥${data.avgPrice.toFixed(2)}<br/>
                    占比: ${params.percent}%`
          },
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#333',
          textStyle: {
            color: '#fff'
          }
        },
        legend: {
          orient: 'vertical',
          right: '5%',
          top: 'center',
          textStyle: {
            color: '#fff',
            fontSize: 12
          },
          formatter: (name) => {
            const item = chartData.find(d => d.name === name)
            if (item) {
              return `${name}\n${item.count}件 ¥${item.value.toFixed(0)}`
            }
            return name
          }
        },
        series: [
          {
            name: '价格区间分布',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#1a1a1a',
              borderWidth: 2
            },
            label: {
              show: true,
              formatter: (params) => {
                return `${params.name}\n${params.data.count}件\n¥${params.data.value.toFixed(0)}`
              },
              color: '#fff',
              fontSize: 11
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 14,
                fontWeight: 'bold'
              },
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            labelLine: {
              show: true,
              lineStyle: {
                color: '#888'
              }
            },
            data: chartData,
            color: [
              '#5470c6',
              '#91cc75',
              '#fac858',
              '#ee6666',
              '#73c0de',
              '#3ba272',
              '#fc8452',
              '#9a60b4'
            ]
          }
        ]
      }

      componentPriceChart.setOption(option)

      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    }

    // 加载库存组件数量区间分析图表
    const loadComponentCountRangeChart = async (componentsData) => {
      await nextTick()
      
      if (!componentCountChartRef.value) return

      // 定义价格区间
      const priceRanges = [
        { name: '0-100', min: 0, max: 100, count: 0, totalValue: 0 },
        { name: '101-500', min: 101, max: 500, count: 0, totalValue: 0 },
        { name: '501-1000', min: 501, max: 1000, count: 0, totalValue: 0 },
        { name: '1001-2000', min: 1001, max: 2000, count: 0, totalValue: 0 },
        { name: '2001-5000', min: 2001, max: 5000, count: 0, totalValue: 0 },
        { name: '5001-10000', min: 5001, max: 10000, count: 0, totalValue: 0 },
        { name: '10001-20000', min: 10001, max: 20000, count: 0, totalValue: 0 },
        { name: '20001+', min: 20001, max: Infinity, count: 0, totalValue: 0 }
      ]

      // 统计每个价格区间的数量和总价值
      componentsData.forEach(item => {
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          if (!isNaN(price)) {
            for (let range of priceRanges) {
              if (price >= range.min && price <= range.max) {
                range.count++
                range.totalValue += price
                break
              }
            }
          }
        }
      })

      // 过滤掉数量为0的区间
      const chartData = priceRanges
        .filter(range => range.count > 0)
        .map(range => ({
          name: `¥${range.name}`,
          value: range.count,
          totalValue: range.totalValue,
          avgPrice: range.totalValue / range.count
        }))

      // 初始化或更新图表
      if (!componentCountChart) {
        componentCountChart = echarts.init(componentCountChartRef.value)
        
        // 添加点击事件
        componentCountChart.on('click', (params) => {
          if (params.componentType === 'series') {
            selectedRange.value = params.name
            filteredItems.value = filterComponentsByRange(params.name)
            itemListVisible.value = true
          }
        })
      }

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const data = params.data
            return `${params.seriesName}<br/>
                    ${params.name}<br/>
                    件数: ${data.value} 件<br/>
                    总价值: ¥${data.totalValue.toFixed(2)}<br/>
                    平均价格: ¥${data.avgPrice.toFixed(2)}<br/>
                    占比: ${params.percent}%`
          },
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#333',
          textStyle: {
            color: '#fff'
          }
        },
        legend: {
          orient: 'vertical',
          right: '5%',
          top: 'center',
          textStyle: {
            color: '#fff',
            fontSize: 12
          },
          formatter: (name) => {
            const item = chartData.find(d => d.name === name)
            if (item) {
              return `${name}\n${item.value}件`
            }
            return name
          }
        },
        series: [
          {
            name: '数量区间分布',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#1a1a1a',
              borderWidth: 2
            },
            label: {
              show: true,
              formatter: (params) => {
                return `${params.name}\n${params.data.value}件`
              },
              color: '#fff',
              fontSize: 11
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 14,
                fontWeight: 'bold'
              },
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            labelLine: {
              show: true,
              lineStyle: {
                color: '#888'
              }
            },
            data: chartData,
            color: [
              '#5470c6',
              '#91cc75',
              '#fac858',
              '#ee6666',
              '#73c0de',
              '#3ba272',
              '#fc8452',
              '#9a60b4'
            ]
          }
        ]
      }

      componentCountChart.setOption(option)

      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    }

    // 处理窗口大小变化
    const handleResize = () => {
      if (priceChart) {
        priceChart.resize()
      }
      if (countChart) {
        countChart.resize()
      }
      if (componentPriceChart) {
        componentPriceChart.resize()
      }
      if (componentCountChart) {
        componentCountChart.resize()
      }
    }

    // 加载所有统计数据
    const loadAllStats = async () => {
      await loadSteamIdList()
      await loadBuyStats()
      await loadSellStats()
      await loadInventoryStats()
      await loadComponentsStats()
    }

    // 处理数据源切换
    const handleDataSourceChange = async () => {
      console.log('数据源切换为:', dataSource.value)
      // 数据源切换时不需要重新加载，因为数据已经加载过了
    }

    onMounted(() => {
      loadAllStats()
    })

    onUnmounted(() => {
      if (priceChart) {
        window.removeEventListener('resize', handleResize)
        priceChart.dispose()
        priceChart = null
      }
      if (countChart) {
        countChart.dispose()
        countChart = null
      }
      if (componentPriceChart) {
        componentPriceChart.dispose()
        componentPriceChart = null
      }
      if (componentCountChart) {
        componentCountChart.dispose()
        componentCountChart = null
      }
    })

    return {
      buyStats,
      sellStats,
      inventoryStats,
      priceChartRef,
      countChartRef,
      itemListVisible,
      selectedRange,
      filteredItems
    }
  }
}
</script>

<style scoped>
.stats-container {
  width: 100%;
  margin-top: clamp(1.5rem, 3vw, 2rem);
}

.grid-7 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: clamp(1rem, 2vw, 1.25rem);
}

.stat-number {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: bold;
  color: #4CAF50;
  margin-top: clamp(0.5rem, 1vw, 0.625rem);
}

.stat-price-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  margin-top: clamp(0.5rem, 1vw, 0.625rem);
}

.stat-diff {
  font-size: clamp(0.875rem, 1.5vw, 1rem);
  font-weight: bold;
  margin: 0;
}

@media (max-width: 1200px) {
  .grid-7 {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
}

@media (max-width: 768px) {
  .grid-7 {
    grid-template-columns: 1fr;
  }

  .stat-price-container {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .price-chart {
    height: 300px;
  }

  .chart-card {
    max-width: 100%;
    min-width: 100%;
  }
}

.chart-container {
  width: 100%;
  margin-top: clamp(1.5rem, 3vw, 2rem);
  display: flex;
  justify-content: flex-start;
  gap: clamp(1rem, 2vw, 1.5rem);
  flex-wrap: wrap;
}

.chart-card {
  padding: clamp(1.5rem, 3vw, 2rem);
  max-width: 800px;
  width: 100%;
  flex: 1;
  min-width: 400px;
}

.chart-card h3 {
  margin: 0 0 1.5rem 0;
  font-size: clamp(1rem, 2vw, 1.25rem);
  color: #fff;
  text-align: center;
}

.price-chart {
  width: 100%;
  height: 450px;
  min-height: 300px;
  cursor: pointer;
}

/* 饰品列表弹窗样式 */
.item-list-dialog {
  --el-dialog-bg-color: #1a1a1a;
}

.item-list-container {
  background-color: #1a1a1a;
}

.item-list-header {
  padding: 1rem 0;
  font-size: 1rem;
  color: #fff;
  border-bottom: 1px solid #333;
  margin-bottom: 1rem;
}

.item-name-cell {
  color: #fff;
  word-break: break-word;
}

/* Element Plus 表格深色主题 */
:deep(.el-table) {
  --el-table-bg-color: #1a1a1a;
  --el-table-tr-bg-color: #1a1a1a;
  --el-table-row-hover-bg-color: #2a2a2a;
  --el-table-header-bg-color: #252525;
  --el-table-header-text-color: #fff;
  --el-table-text-color: #fff;
  --el-table-border-color: #333;
}

:deep(.el-table__body tr:hover > td) {
  background-color: #2a2a2a !important;
}

:deep(.el-dialog) {
  background-color: #1a1a1a;
  border: 1px solid #333;
}

:deep(.el-dialog__header) {
  background-color: #252525;
  border-bottom: 1px solid #333;
}

:deep(.el-dialog__title) {
  color: #fff;
}

:deep(.el-dialog__close) {
  color: #fff;
}

:deep(.el-dialog__close:hover) {
  color: #4CAF50;
}
</style>