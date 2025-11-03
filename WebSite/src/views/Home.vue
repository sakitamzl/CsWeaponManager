<template>
  <div>
    <div class="search-container">
      <div class="card search-card">
        <div class="search-box">
          <input 
            v-model="searchKeyword" 
            type="text" 
            class="search-input" 
            placeholder="请输入饰品名称进行搜索..." 
            @keyup.enter="handleSearch"
          />
          <button class="search-button" @click="handleSearch">搜索</button>
        </div>
      </div>
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
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { API_CONFIG } from '@/config/api.js'

export default {
  name: 'Home',
  setup() {
    const searchKeyword = ref('')
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

    const handleSearch = () => {
      if (!searchKeyword.value.trim()) {
        return
      }
      console.log('搜索关键词:', searchKeyword.value)
      // 这里后续对接API
    }

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
          selectedSteamId.value = steamIdList.value[0].steam_id
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
        }
      } catch (error) {
        console.error('加载库存统计失败:', error)
      }
    }

    // 加载所有统计数据
    const loadAllStats = async () => {
      await loadSteamIdList()
      await loadBuyStats()
      await loadSellStats()
      await loadInventoryStats()
    }

    onMounted(() => {
      loadAllStats()
    })

    return {
      searchKeyword,
      buyStats,
      sellStats,
      inventoryStats,
      handleSearch
    }
  }
}
</script>

<style scoped>
.search-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: clamp(1rem, 3vw, 2rem) 0;
}

.search-card {
  padding: clamp(1.5rem, 3vw, 2rem);
}

.search-box {
  display: flex;
  gap: clamp(0.75rem, 2vw, 1rem);
  align-items: stretch;
}

.search-input {
  flex: 1;
  padding: clamp(0.75rem, 2vw, 1rem);
  font-size: clamp(0.875rem, 1.5vw, 1rem);
  background-color: #2a2a2a;
  border: 1px solid #444;
  border-radius: 0.5rem;
  color: #fff;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.search-input::placeholder {
  color: #888;
}

.search-button {
  padding: clamp(0.75rem, 2vw, 1rem) clamp(1.5rem, 3vw, 2rem);
  font-size: clamp(0.875rem, 1.5vw, 1rem);
  font-weight: 500;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.search-button:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.search-button:active {
  transform: translateY(0);
}

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
  .search-box {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .search-button {
    width: 100%;
  }

  .grid-7 {
    grid-template-columns: 1fr;
  }

  .stat-price-container {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}
</style>