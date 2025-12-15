<template>
  <div class="container" @click="handleContainerClick">
    <aside class="sidebar" :class="{ collapsed: isCollapsed }" @click.stop="handleSidebarClick">
      <div class="sidebar-header">
        <h1 v-if="!isCollapsed">CsWeaponManager</h1>
        <h1 v-else class="collapsed-title">CS</h1>
      </div>
      <ul>
        <li 
          v-for="item in menuItems" 
          :key="item.path"
          :class="{ active: $route.path === item.path }"
          @click.stop="handleMenuClick(item.path)"
          :title="isCollapsed ? item.title : ''"
        >
          <img :src="item.icon" :alt="item.title" class="menu-icon">
          <span v-if="!isCollapsed" class="menu-text">{{ item.title }}</span>
        </li>
      </ul>
      
      <!-- 空白填充区域，用于捕获点击事件 -->
      <div class="sidebar-spacer"></div>
      
      <!-- 用户信息和退出按钮 -->
      <div class="sidebar-footer" v-if="isLoggedIn" @click.stop>
        <div class="user-info" v-if="!isCollapsed">
          <span class="username">{{ username }}</span>
          <button @click.stop="handleLogout" class="logout-btn" title="退出登录">
            退出
          </button>
        </div>
        <button v-else @click.stop="handleLogout" class="logout-btn-icon" title="退出登录">
          🚪
        </button>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import { ElMessageBox, ElMessage } from 'element-plus'

export default {
  name: 'Layout',
  data() {
    return {
      isCollapsed: false, // 默认展开状态
      isLoggedIn: false,
      username: '',
      menuItems: [
        {
          path: '/home',
          title: '主页',
          icon: '/icons/indexPage.png'
        },
        {
          path: '/item-search',
          title: '饰品搜索',
          icon: '/icons/search.png'
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
          path: '/data-website',
          title: '第三方数据',
          icon: '/icons/data_from.png'
        },
        {
          path: '/data-spider',
          title: '数据挖掘',
          icon: '/icons/铲子.png'
        },
        {
          path: '/settings',
          title: '其他功能',
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
  mounted() {
    // 检查登录状态
    this.isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
    this.username = localStorage.getItem('username') || '用户'
  },
  watch: {
    // 监听路由变化，切换页面时自动收缩侧边栏
    '$route'() {
      this.isCollapsed = true
    }
  },
  methods: {
    handleMenuClick(path) {
      this.$router.push(path)
    },
    handleSidebarClick(event) {
      // 点击侧边栏空白区域切换展开/收缩状态
      console.log('Sidebar clicked:', event.target.className)
      this.isCollapsed = !this.isCollapsed
    },
    handleContainerClick() {
      // 点击主内容区域时，只在展开状态下才收缩侧边栏
      if (!this.isCollapsed) {
        this.isCollapsed = true
      }
    },
    handleLogout() {
      ElMessageBox.confirm(
        '确定要退出登录吗？',
        '确认退出',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        // 清除登录状态
        localStorage.removeItem('isLoggedIn')
        localStorage.removeItem('username')
        localStorage.removeItem('loginTime')
        
        ElMessage.success('已退出登录')
        
        // 跳转到登录页
        this.$router.push('/login')
      }).catch(() => {
        // 取消退出
      })
    }
  }
}
</script>

<style scoped>
/* 侧边栏头部 */
.sidebar-header {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 1.875rem;
  padding-right: 0.5rem;
  cursor: pointer;
}

.collapsed-title {
  font-size: clamp(1.125rem, 2vw, 1.5rem);
  color: var(--text-primary);
  margin: 0;
  text-align: center;
  width: 100%;
}

/* 侧边栏收缩状态 */
.sidebar.collapsed {
  min-width: 4rem;
  max-width: 4rem;
  width: 4rem;
}

.sidebar.collapsed .sidebar-header {
  justify-content: center;
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
  cursor: pointer;
}

.sidebar ul {
  cursor: default;
}

.sidebar li {
  cursor: pointer;
}

/* 空白填充区域 */
.sidebar-spacer {
  flex: 1;
  min-height: 2rem;
  cursor: pointer;
}

/* 侧边栏底部用户信息 */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #333;
}

.user-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.username {
  color: #4CAF50;
  font-size: 0.875rem;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  padding: 0.375rem 0.75rem;
  background-color: #f56c6c;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #f54545;
}

.logout-btn-icon {
  width: 100%;
  padding: 0.5rem;
  background-color: #f56c6c;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1.25rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-btn-icon:hover {
  background-color: #f54545;
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
}
</style>