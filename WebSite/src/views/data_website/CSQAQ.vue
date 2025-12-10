<template>
  <div class="csqaq-container">
    <div class="page-header">
      <h1>CSQAQ 数据查询</h1>
      <p class="subtitle">第三方CS饰品数据查询平台</p>
    </div>

    <div class="content-wrapper">
      <el-card class="search-card">
        <template #header>
          <div class="card-header">
            <span>饰品查询</span>
          </div>
        </template>
        
        <el-form :model="searchForm" label-width="100px">
          <el-form-item label="饰品名称">
            <el-input 
              v-model="searchForm.itemName" 
              placeholder="请输入饰品名称"
              clearable
            />
          </el-form-item>
          
          <el-form-item label="饰品ID">
            <el-input 
              v-model="searchForm.itemId" 
              placeholder="请输入饰品ID"
              clearable
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleSearch" :loading="loading">
              <el-icon style="margin-right: 5px;"><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="result-card" v-if="searchResult">
        <template #header>
          <div class="card-header">
            <span>查询结果</span>
          </div>
        </template>
        
        <div class="result-content">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="饰品名称">
              {{ searchResult.name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="饰品ID">
              {{ searchResult.id || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="价格">
              {{ searchResult.price || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ searchResult.updateTime || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>

      <el-empty 
        v-if="!searchResult && !loading" 
        description="暂无查询结果"
        :image-size="200"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

const loading = ref(false)
const searchResult = ref(null)

const searchForm = reactive({
  itemName: '',
  itemId: ''
})

const handleSearch = async () => {
  if (!searchForm.itemName && !searchForm.itemId) {
    ElMessage.warning('请输入饰品名称或ID')
    return
  }

  loading.value = true
  try {
    // 这里调用CSQAQ的API
    // const response = await axios.get(apiUrls.csqaqSearch(), {
    //   params: {
    //     name: searchForm.itemName,
    //     id: searchForm.itemId
    //   }
    // })
    
    // 模拟数据
    setTimeout(() => {
      searchResult.value = {
        name: searchForm.itemName || '测试饰品',
        id: searchForm.itemId || '12345',
        price: '¥ 1,234.56',
        updateTime: new Date().toLocaleString('zh-CN')
      }
      loading.value = false
      ElMessage.success('查询成功')
    }, 1000)
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败，请稍后重试')
    loading.value = false
  }
}

const handleReset = () => {
  searchForm.itemName = ''
  searchForm.itemId = ''
  searchResult.value = null
}
</script>

<style scoped>
.csqaq-container {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  color: #ffffff;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.subtitle {
  color: #909399;
  font-size: 0.875rem;
  margin: 0;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.search-card,
.result-card {
  background: #1e1e1e;
  border: 1px solid #333;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #ffffff;
}

.result-content {
  padding: 1rem 0;
}

:deep(.el-form-item__label) {
  color: #b0b0b0;
}

:deep(.el-input__wrapper) {
  background-color: #2a2a2a;
  box-shadow: 0 0 0 1px #3a3a3a inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4a4a4a inset;
}

:deep(.el-input__inner) {
  color: #ffffff;
}

:deep(.el-descriptions__label) {
  background-color: #2a2a2a;
  color: #b0b0b0;
}

:deep(.el-descriptions__content) {
  background-color: #1e1e1e;
  color: #ffffff;
}

:deep(.el-card__header) {
  background-color: #252525;
  border-bottom: 1px solid #333;
  padding: 1rem 1.5rem;
}

:deep(.el-card__body) {
  padding: 1.5rem;
}

@media (max-width: 768px) {
  .csqaq-container {
    padding: 1rem;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }
}
</style>
