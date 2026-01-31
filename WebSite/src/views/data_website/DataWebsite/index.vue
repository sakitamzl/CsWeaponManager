<template>
  <div class="data-website-container" :class="{ 'main-sidebar-collapsed': isMainSidebarCollapsed }">
    <!-- 二级左侧栏 -->
    <aside class="secondary-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-content">
        <div class="sidebar-header">
          <!-- 保留标题空位，用于间距 -->
        </div>
        
        <ul class="category-list">
          <li 
            :class="{ active: $route.name === 'MarketOverview' }"
            @click="navigateTo('/data-website/market-overview')"
          >
            <el-icon :size="18">
              <TrendCharts />
            </el-icon>
            <span>市场大盘</span>
          </li>
          <li 
            :class="{ active: $route.name === 'DataWebsiteItemSearch' }"
            @click="navigateTo('/data-website/item-search')"
          >
            <el-icon :size="18">
              <Search />
            </el-icon>
            <span>饰品搜索</span>
          </li>
        </ul>
      </div>
    </aside>

    <!-- 折叠/展开按钮 -->
    <div class="toggle-button" :class="{ collapsed: sidebarCollapsed }" @click="toggleSidebar">
      <el-icon :size="20">
        <ArrowLeft v-if="!sidebarCollapsed" />
        <ArrowRight v-else />
      </el-icon>
    </div>

    <!-- 主内容区域 -->
    <div class="main-wrapper" :class="{ expanded: sidebarCollapsed }" @click="handleContentClick">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { TrendCharts, Search, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { useDataWebsite } from './useDataWebsite.js'

const {
  sidebarCollapsed,
  isMainSidebarCollapsed,
  navigateTo,
  toggleSidebar,
  handleContentClick
} = useDataWebsite()
</script>

<style scoped src="./styles.css"></style>
