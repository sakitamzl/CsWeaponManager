<template>
  <div>
    <h1 class="page-title">Steam库存</h1>
    
    <div class="filters card">
      <div class="flex flex-wrap gap-4 items-center">
        <el-input
          v-model="searchText"
          placeholder="搜索饰品名称..."
          prefix-icon="Search"
          class="search-input"
        />
        <el-select v-model="weaponTypeFilter" placeholder="武器类型" class="type-select">
          <el-option label="全部" value="all" />
          <el-option label="步枪" value="rifle" />
          <el-option label="手枪" value="pistol" />
          <el-option label="狙击枪" value="sniper" />
          <el-option label="冲锋枪" value="smg" />
          <el-option label="霰弹枪" value="shotgun" />
          <el-option label="机枪" value="machinegun" />
          <el-option label="手套" value="gloves" />
          <el-option label="刀具" value="knife" />
        </el-select>
        <el-button type="primary" @click="refreshInventory" :loading="loading">
          刷新库存
        </el-button>
      </div>
    </div>

    <div class="inventory-stats">
      <div class="grid grid-3">
        <div class="card">
          <h3>总库存数量</h3>
          <p class="stat-number">{{ inventoryStats.totalCount }}</p>
        </div>
        <div class="card">
          <h3>总估值</h3>
          <p class="stat-number">¥{{ inventoryStats.totalValue }}</p>
        </div>
        <div class="card">
          <h3>平均价值</h3>
          <p class="stat-number">¥{{ inventoryStats.avgValue }}</p>
        </div>
      </div>
    </div>

    <div class="table-container">
      <el-table
        :data="filteredInventoryData"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        :row-style="{ backgroundColor: 'transparent' }"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
      >
        <el-table-column prop="weapon_name" label="类型" min-width="100" />
        <el-table-column prop="weapon_type" label="分类" min-width="80" />
        <el-table-column prop="item_name" label="饰品名称" min-width="220" show-overflow-tooltip />
        <el-table-column prop="weapon_float" label="Float" min-width="100" />
        <el-table-column prop="float_range" label="磨损" min-width="80" />
        <el-table-column prop="price" label="当前价格" min-width="100">
          <template #default="scope">
            ¥{{ scope.row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="acquired_time" label="获得时间" min-width="140">
          <template #default="scope">
            {{ formatTime(scope.row.acquired_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="80">
          <template #default="scope">
            <el-tag 
              :type="getStatusType(scope.row.status)" 
              size="small"
              :style="{
                backgroundColor: getStatusColor(scope.row.status),
                borderColor: getStatusColor(scope.row.status),
                color: getStatusTextColor(scope.row.status)
              }"
            >
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalItems"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Inventory',
  setup() {
    const loading = ref(false)
    const inventoryData = ref([])
    const searchText = ref('')
    const weaponTypeFilter = ref('all')
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalItems = ref(0)

    const filteredInventoryData = computed(() => {
      let filtered = inventoryData.value

      if (searchText.value) {
        filtered = filtered.filter(item =>
          item.item_name.toLowerCase().includes(searchText.value.toLowerCase())
        )
      }

      if (weaponTypeFilter.value !== 'all') {
        filtered = filtered.filter(item => item.weapon_type === weaponTypeFilter.value)
      }

      totalItems.value = filtered.length
      
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filtered.slice(start, end)
    })

    const inventoryStats = computed(() => {
      const totalCount = inventoryData.value.length
      const totalValue = inventoryData.value.reduce((sum, item) => sum + item.price, 0)
      const avgValue = totalCount > 0 ? (totalValue / totalCount).toFixed(2) : 0

      return {
        totalCount,
        totalValue,
        avgValue
      }
    })

    const formatTime = (time) => {
      return new Date(time).toLocaleString('zh-CN')
    }

    const getStatusType = (status) => {
      const statusMap = {
        '可用': 'success',
        '出租中': 'warning',
        '锁定': 'danger',
        '交易冷却': 'info'
      }
      return statusMap[status] || 'info'
    }

    const getStatusColor = (status) => {
      const colorMap = {
        '可用': '#67C23A',
        '出租中': '#E6A23C',
        '锁定': '#F56C6C',
        '交易冷却': '#409EFF'
      }
      return colorMap[status] || '#909399'
    }

    const getStatusTextColor = (status) => {
      return '#FFFFFF'
    }

    const loadInventoryData = async () => {
      loading.value = true
      try {
        // 这里应该调用API获取Steam库存数据
        // const response = await fetch('/api/inventory')
        // const data = await response.json()
        // inventoryData.value = data
        
        // 临时模拟数据
        inventoryData.value = [
          {
            id: 1,
            weapon_name: 'AK-47',
            weapon_type: 'rifle',
            item_name: 'AK-47 | 红线 (久经沙场)',
            weapon_float: 0.234,
            float_range: '久经沙场',
            price: 285,
            acquired_time: '2025-01-15 10:30:25',
            status: '可用'
          },
          {
            id: 2,
            weapon_name: 'M4A1-S',
            weapon_type: 'rifle',
            item_name: 'M4A1-S | 金属网 (崭新出厂)',
            weapon_float: 0.045,
            float_range: '崭新出厂',
            price: 420,
            acquired_time: '2025-01-16 14:22:10',
            status: '出租中'
          },
          {
            id: 3,
            weapon_name: 'Glock-18',
            weapon_type: 'pistol',
            item_name: 'Glock-18 | 水元素 (略有磨损)',
            weapon_float: 0.158,
            float_range: '略有磨损',
            price: 125,
            acquired_time: '2025-01-14 16:45:30',
            status: '可用'
          }
        ]
        totalItems.value = inventoryData.value.length
      } catch (error) {
        console.error('加载库存数据失败:', error)
        ElMessage.error('加载数据失败')
      } finally {
        loading.value = false
      }
    }

    const refreshInventory = async () => {
      ElMessage.info('正在刷新Steam库存...')
      await loadInventoryData()
      ElMessage.success('库存已刷新')
    }

    const handleSell = (item) => {
      ElMessageBox.confirm(
        `确定要出售 ${item.item_name} 吗？`,
        '确认出售',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).then(() => {
        ElMessage.success(`已添加到出售队列: ${item.item_name}`)
        // 这里应该调用API添加到出售队列
      }).catch(() => {
        ElMessage.info('已取消出售')
      })
    }

    const handleRent = (item) => {
      ElMessageBox.confirm(
        `确定要出租 ${item.item_name} 吗？`,
        '确认出租',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).then(() => {
        ElMessage.success(`已添加到出租队列: ${item.item_name}`)
        // 这里应该调用API添加到出租队列
      }).catch(() => {
        ElMessage.info('已取消出租')
      })
    }

    const handleViewMarketPrice = (item) => {
      ElMessage.info(`查看市场价格: ${item.item_name}`)
      // 这里应该打开市场价格查询对话框
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
    }

    onMounted(() => {
      loadInventoryData()
    })

    return {
      loading,
      inventoryData,
      filteredInventoryData,
      inventoryStats,
      searchText,
      weaponTypeFilter,
      currentPage,
      pageSize,
      totalItems,
      formatTime,
      getStatusType,
      getStatusColor,
      getStatusTextColor,
      refreshInventory,
      handleSell,
      handleRent,
      handleViewMarketPrice,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.search-input {
  min-width: 200px;
  flex: 1;
  max-width: 300px;
}

.type-select {
  min-width: 120px;
  max-width: 180px;
}

.inventory-stats {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.stat-number {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: bold;
  color: #4CAF50;
  margin-top: clamp(0.5rem, 1vw, 0.625rem);
}

.pagination {
  margin-top: clamp(1rem, 3vw, 1.25rem);
  display: flex;
  justify-content: center;
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

.action-buttons {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  justify-content: center;
}

:deep(.el-button) {
  font-size: clamp(0.625rem, 1vw, 0.75rem);
  padding: clamp(0.375rem, 1vw, 0.5rem) clamp(0.5rem, 1.5vw, 0.75rem);
}

:deep(.el-table) {
  min-width: 1200px;
}

:deep(.el-table .el-table__cell) {
  word-break: break-word;
}

@media (max-width: 1200px) {
  :deep(.el-table) {
    min-width: 1100px;
  }
}

@media (max-width: 768px) {
  .search-input {
    min-width: unset;
    width: 100%;
    max-width: none;
  }
  
  .type-select {
    min-width: unset;
    width: 100%;
    max-width: none;
  }
  
  :deep(.el-table) {
    font-size: 0.75rem;
    min-width: 1000px;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 0.5rem 0.25rem;
  }
  
  :deep(.el-button) {
    font-size: 0.625rem;
    padding: 0.25rem 0.5rem;
    width: 100%;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .action-buttons .el-button {
    width: 100%;
    min-width: 0;
  }
}

@media (max-width: 480px) {
  :deep(.el-table) {
    min-width: 900px;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 0.375rem 0.125rem;
    font-size: 0.625rem;
  }
  
  :deep(.el-button) {
    font-size: 0.5rem;
    padding: 0.125rem 0.25rem;
  }
}
</style>