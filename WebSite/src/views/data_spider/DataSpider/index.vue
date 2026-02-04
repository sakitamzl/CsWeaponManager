<template>
  <div class="data-spider-container" :class="{ 'main-sidebar-collapsed': isMainSidebarCollapsed }">
    <!-- 二级左侧栏 -->
    <aside class="secondary-sidebar" :class="{ collapsed: sidebarCollapsed, 'no-transition': !isMounted }">
      <div class="sidebar-content">
        <div class="sidebar-header">
          <!-- 保留标题空位，用于间距 -->
        </div>

        <ul class="category-list">
          <li
            :class="{ active: $route.name === 'DataSpiderSearchRename' }"
            @click="navigateTo('/data-spider/search-rename')"
          >
            <el-icon :size="18">
              <Edit />
            </el-icon>
            <span>爬取改名</span>
          </li>
          <li
            :class="{ active: $route.name === 'DataSpiderSearchPendant' }"
            @click="navigateTo('/data-spider/search-pendant')"
          >
            <el-icon :size="18">
              <Medal />
            </el-icon>
            <span>爬取挂件</span>
          </li>
          <li
            :class="{ active: $route.name === 'DataSpiderInventoryMining' }"
            @click="navigateTo('/data-spider/inventory-mining')"
          >
            <el-icon :size="18">
              <Search />
            </el-icon>
            <span>库存挖掘</span>
          </li>
        </ul>
      </div>
    </aside>

    <!-- 折叠/展开按钮 -->
    <div class="toggle-button" :class="{ collapsed: sidebarCollapsed, 'no-transition': !isMounted }" @click="toggleSidebar">
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
import { Search, Edit, Medal, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { useDataSpider } from './useDataSpider.js'

const {
  sidebarCollapsed,
  isMainSidebarCollapsed,
  isMounted,
  navigateTo,
  toggleSidebar,
  handleContentClick
} = useDataSpider()
</script>

<style scoped src="./styles.css"></style>
