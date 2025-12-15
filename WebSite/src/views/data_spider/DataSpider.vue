<template>
  <div class="data-spider-container" :class="{ 'main-sidebar-collapsed': isMainSidebarCollapsed }">
    <!-- 二级左侧栏 -->
    <aside class="secondary-sidebar" :class="{ collapsed: sidebarCollapsed }">
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Edit, Medal, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const sidebarCollapsed = ref(false)
const isMainSidebarCollapsed = ref(false)

const navigateTo = (path) => {
  router.push(path)
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 点击内容区域时收缩侧边栏
const handleContentClick = () => {
  if (!sidebarCollapsed.value) {
    sidebarCollapsed.value = true
  }
}

// 监听主侧边栏的状态变化
const checkMainSidebarState = () => {
  const mainSidebar = document.querySelector('.sidebar')
  if (mainSidebar) {
    isMainSidebarCollapsed.value = mainSidebar.classList.contains('collapsed')
  }
}

// 使用 MutationObserver 监听主侧边栏的 class 变化
let observer = null

onMounted(() => {
  checkMainSidebarState()
  
  const mainSidebar = document.querySelector('.sidebar')
  if (mainSidebar) {
    observer = new MutationObserver(() => {
      checkMainSidebarState()
    })
    
    observer.observe(mainSidebar, {
      attributes: true,
      attributeFilter: ['class']
    })
  }
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style scoped>
.data-spider-container {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background: transparent;
  position: relative;
}

/* 二级左侧栏 */
.secondary-sidebar {
  position: fixed;
  left: var(--main-sidebar-width, max(15rem, min(18vw, 20rem)));
  top: 0;
  bottom: 0;
  width: 220px;
  background: linear-gradient(135deg, rgba(26, 26, 26, 0.98) 0%, rgba(35, 35, 35, 0.95) 100%);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-right: 1px solid rgba(58, 58, 58, 0.8);
  border-left: none;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  z-index: 100;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 2px 0 16px rgba(0, 0, 0, 0.5);
}

/* 当主侧边栏收缩时，二级侧边栏也跟随调整 */
.data-spider-container.main-sidebar-collapsed .secondary-sidebar {
  left: 4rem;
}

.secondary-sidebar.collapsed {
  transform: translateX(-100%);
}

/* 折叠/展开按钮 */
.toggle-button {
  position: fixed;
  left: calc(var(--main-sidebar-width, max(15rem, min(18vw, 20rem))) + 220px + 2px);
  top: 50%;
  transform: translateY(-50%);
  width: 36px;
  height: 80px;
  background: linear-gradient(90deg, rgba(30, 30, 30, 0.95) 0%, rgba(30, 30, 30, 0.98) 100%);
  border: 1px solid rgba(58, 58, 58, 0.8);
  border-radius: 0 12px 12px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: #b0b0b0;
  z-index: 101;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.2);
}

/* 当二级侧边栏收缩时，按钮移到主侧边栏右侧（紧贴，无间隙） */
.toggle-button.collapsed {
  left: var(--main-sidebar-width, max(15rem, min(18vw, 20rem)));
}

/* 当主侧边栏收缩时 */
.data-spider-container.main-sidebar-collapsed .toggle-button {
  left: calc(4rem + 220px + 2px);
}

.data-spider-container.main-sidebar-collapsed .toggle-button.collapsed {
  left: 4rem;
}

.toggle-button:hover {
  background: linear-gradient(90deg, rgba(76, 175, 80, 0.2) 0%, rgba(76, 175, 80, 0.3) 100%);
  color: #4CAF50;
  border-color: #4CAF50;
  box-shadow: 2px 0 12px rgba(76, 175, 80, 0.4);
  transform: translateY(-50%) translateX(2px);
}

.toggle-button .el-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 侧边栏内容 */
.sidebar-content {
  flex: 1;
  padding: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  border-bottom: 1px solid #3a3a3a;
  margin-bottom: 0;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
}

.category-list li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  color: #b0b0b0;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.category-list li:hover {
  background-color: #333333;
  color: #ffffff;
}

.category-list li.active {
  background-color: #4CAF50;
  color: #ffffff;
  font-weight: 600;
}

.category-list li.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: #66bb6a;
}

.category-list li span {
  flex: 1;
}

/* 主内容区域包装器 */
.main-wrapper {
  flex: 1;
  margin-left: 220px;
  overflow-y: auto;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-wrapper.expanded {
  margin-left: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .secondary-sidebar {
    width: 180px;
  }

  .main-wrapper {
    margin-left: 180px;
  }

  .main-wrapper.expanded {
    margin-left: 0;
  }
}

/* 深色主题滚动条 */
.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: rgba(74, 74, 74, 0.6);
  border-radius: 3px;
  transition: background 0.2s;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: rgba(90, 90, 90, 0.8);
}

.main-wrapper::-webkit-scrollbar {
  width: 8px;
}

.main-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.main-wrapper::-webkit-scrollbar-thumb {
  background: rgba(74, 74, 74, 0.6);
  border-radius: 4px;
  transition: background 0.2s;
}

.main-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(90, 90, 90, 0.8);
}
</style>
