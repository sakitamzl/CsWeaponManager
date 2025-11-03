<template>
  <div class="container">
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-header">
        <h1 v-if="!isCollapsed">CsWeaponManager</h1>
        <h1 v-else class="collapsed-title">CS</h1>
        <button @click="toggleSidebar" class="toggle-btn" :title="isCollapsed ? '展开侧边栏' : '收起侧边栏'">
          <img 
            src="/icons/left-arrow.png" 
            alt="toggle sidebar" 
            class="toggle-icon"
            :class="{ rotated: isCollapsed }"
          >
        </button>
      </div>
      <ul>
        <li 
          v-for="item in menuItems" 
          :key="item.path"
          :class="{ active: $route.path === item.path }"
          @click="handleMenuClick(item.path)"
          :title="isCollapsed ? item.title : ''"
        >
          <img :src="item.icon" :alt="item.title" class="menu-icon">
          <span v-if="!isCollapsed" class="menu-text">{{ item.title }}</span>
        </li>
      </ul>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'Layout',
  data() {
    return {
      isCollapsed: false,
      menuItems: [
        {
          path: '/home',
          title: '主页',
          icon: '/icons/indexPage.png'
        },
        {
          path: '/item-search',
          title: '饰品搜索',
          icon: '/icons/Stock_components.png'
        },
        {
          path: '/buy',
          title: '购入列表',
          icon: '/icons/buy.png'
        },
        {
          path: '/sell',
          title: '出售列表',
          icon: '/icons/sell.png'
        },
        {
          path: '/rent',
          title: '出租列表',
          icon: '/icons/label-zuhu.png'
        },
        {
          path: '/inventory',
          title: 'Steam库存',
          icon: '/icons/In _library.png'
        },
        // {
        //   path: '/sublet',
        //   title: '正在转租',
        //   icon: '/icons/Sublet.png'
        // },
        // {
        //   path: '/rental-records',
        //   title: '出租记录',
        //   icon: '/icons/Rental_records.png'
        // },
        {
          path: '/stock-components',
          title: '库存组件',
          icon: '/icons/Stock_components.png'
        },
        {
          path: '/data-source',
          title: '数据来源',
          icon: '/icons/data_from.png'
        },
        {
          path: '/automation',
          title: '其他工具',
          icon: '/icons/setting.png'
        }
        // {
        //   path: '/setting',
        //   title: '设置',
        //   icon: '/icons/setting.png'
        // }
      ]
    }
  },
  methods: {
    handleMenuClick(path) {
      this.$router.push(path)
    },
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed
    }
  }
}
</script>

<style scoped>
/* 侧边栏头部 */
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.875rem;
  padding-right: 0.5rem;
}

.collapsed-title {
  font-size: clamp(1.125rem, 2vw, 1.5rem);
  color: var(--text-primary);
  margin: 0;
  text-align: center;
  width: 100%;
}

/* 切换按钮 */
.toggle-btn {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: 0.25rem;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  min-width: 2rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-btn:hover {
  background: var(--bg-overlay);
  color: var(--text-primary);
  border-color: var(--text-accent);
}

/* 切换图标 */
.toggle-icon {
  width: 1rem;
  height: 1rem;
  transition: transform 0.3s ease;
  filter: brightness(0) saturate(100%) invert(59%) sepia(11%) saturate(200%) hue-rotate(176deg) brightness(90%) contrast(94%);
}

.toggle-btn:hover .toggle-icon {
  filter: brightness(0) saturate(100%) invert(100%) sepia(0%) saturate(2%) hue-rotate(28deg) brightness(107%) contrast(101%);
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

/* 侧边栏收缩状态 */
.sidebar.collapsed {
  min-width: 4rem;
  max-width: 4rem;
  width: 4rem;
}

.sidebar.collapsed .sidebar-header {
  justify-content: center;
  flex-direction: column;
  gap: 0.5rem;
}

.sidebar.collapsed .toggle-btn {
  margin-top: 0.5rem;
}

/* 菜单项 */
.menu-icon {
  width: clamp(1.5rem, 3vw, 2.375rem);
  height: auto;
  vertical-align: middle;
  margin-right: clamp(0.5rem, 1.5vw, 0.75rem);
  flex-shrink: 0;
}

.sidebar.collapsed .menu-icon {
  margin: 0 auto;
}

.menu-text {
  opacity: 1;
  transition: opacity 0.2s ease;
}

.sidebar.collapsed .menu-text {
  opacity: 0;
  display: none;
}

/* 收缩状态下的菜单项居中 */
.sidebar.collapsed li {
  justify-content: center;
  text-align: center;
  padding: 0.75rem 0.25rem;
}

/* 过渡动画 */
.sidebar {
  transition: all 0.3s ease;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .menu-icon {
    width: 1.25rem;
    margin-right: 0.25rem;
  }
  
  .sidebar.collapsed .menu-icon {
    width: 1rem;
    margin: 0 auto;
  }
  
  .sidebar.collapsed {
    min-width: 3rem;
    max-width: 3rem;
    width: 3rem;
  }
  
  .toggle-btn {
    font-size: 0.75rem;
    padding: 0.125rem 0.25rem;
    min-width: 1.5rem;
    height: 1.5rem;
  }
  
  .toggle-icon {
    width: 0.75rem;
    height: 0.75rem;
  }
}
</style>