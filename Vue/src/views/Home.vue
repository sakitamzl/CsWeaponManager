<template>
  <div>
    <h1 class="page-title">欢迎使用 CSDB</h1>
    <div class="dashboard">
      <div class="grid grid-4">
        <div class="card">
          <h3>总购入数量</h3>
          <p class="stat-number">{{ stats.totalBuy }}</p>
        </div>
        <div class="card">
          <h3>总出售数量</h3>
          <p class="stat-number">{{ stats.totalSell }}</p>
        </div>
        <div class="card">
          <h3>库存数量</h3>
          <p class="stat-number">{{ stats.totalInventory }}</p>
        </div>
        <div class="card">
          <h3>总盈利</h3>
          <p class="stat-number">¥{{ stats.totalProfit }}</p>
        </div>
      </div>
      
      <div class="recent-activities">
        <div class="card">
          <h3>最近活动</h3>
          <div class="activity-list">
            <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
              <span class="activity-type">{{ activity.type }}</span>
              <span class="activity-item-name">{{ activity.itemName }}</span>
              <span class="activity-price">¥{{ activity.price }}</span>
              <span class="activity-time">{{ formatTime(activity.time) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Home',
  setup() {
    const stats = ref({
      totalBuy: 0,
      totalSell: 0,
      totalInventory: 0,
      totalProfit: 0
    })

    const recentActivities = ref([
      {
        id: 1,
        type: '购入',
        itemName: 'AK-47 | 红线',
        price: 280,
        time: new Date()
      },
      {
        id: 2,
        type: '出售',
        itemName: 'M4A4 | 龙王',
        price: 520,
        time: new Date(Date.now() - 3600000)
      }
    ])

    const formatTime = (time) => {
      return new Date(time).toLocaleString('zh-CN')
    }

    const loadStats = async () => {
      try {
        // 这里应该调用API获取统计数据
        // const response = await fetch('/api/stats')
        // const data = await response.json()
        // stats.value = data
        
        // 临时模拟数据
        stats.value = {
          totalBuy: 156,
          totalSell: 89,
          totalInventory: 67,
          totalProfit: 12580
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }

    onMounted(() => {
      loadStats()
    })

    return {
      stats,
      recentActivities,
      formatTime
    }
  }
}
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-number {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: bold;
  color: #4CAF50;
  margin-top: clamp(0.5rem, 1vw, 0.625rem);
}

.recent-activities {
  margin-top: clamp(1rem, 3vw, 1.875rem);
}

.activity-list {
  margin-top: clamp(0.75rem, 2vw, 0.9375rem);
}

.activity-item {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: clamp(0.5rem, 2vw, 0.9375rem);
  padding: clamp(0.5rem, 1.5vw, 0.75rem) 0;
  border-bottom: 1px solid #333;
  align-items: center;
}

.activity-type {
  padding: clamp(0.25rem, 0.5vw, 0.375rem) clamp(0.5rem, 1vw, 0.75rem);
  border-radius: 0.75rem;
  font-size: clamp(0.625rem, 1vw, 0.75rem);
  background-color: #4CAF50;
  color: white;
  text-align: center;
  white-space: nowrap;
}

.activity-item-name {
  font-weight: 500;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.activity-price {
  color: #4CAF50;
  font-weight: bold;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
  white-space: nowrap;
}

.activity-time {
  color: #999;
  font-size: clamp(0.625rem, 1vw, 0.75rem);
  white-space: nowrap;
}

@media (max-width: 768px) {
  .activity-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    text-align: center;
    padding: 0.75rem;
    background-color: #2a2a2a;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    border-bottom: none;
  }
  
  .activity-type {
    justify-self: center;
  }
  
  .activity-item-name,
  .activity-price,
  .activity-time {
    white-space: normal;
    text-align: center;
  }
}
</style>