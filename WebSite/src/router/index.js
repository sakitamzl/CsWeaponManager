import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/Layout.vue'
import Home from '@/views/Home.vue'
import ItemSearch from '@/views/ItemSearch.vue'
import Buy from '@/views/Buy.vue'
import Sell from '@/views/Sell.vue'
import Lent from '@/views/Lent.vue'
import Inventory from '@/views/Inventory.vue'
import Setting from '@/views/Setting.vue'
import StockComponents from '@/views/StockComponents.vue'
import Settings from '@/views/Settings.vue'
import Login from '@/views/Login.vue'
import axios from 'axios'
import { apiUrls } from '@/config/api'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/home',
    children: [
      {
        path: '/home',
        name: 'Home',
        component: Home,
        meta: { title: '主页' }
      },
      {
        path: '/item-search',
        name: 'ItemSearch',
        component: ItemSearch,
        meta: { title: '饰品搜索' }
      },
      {
        path: '/buy',
        name: 'Buy',
        component: Buy,
        meta: { title: '已购入' }
      },
      {
        path: '/sell',
        name: 'Sell',
        component: Sell,
        meta: { title: '已出售' }
      },
      {
        path: '/rent',
        name: 'Lent',
        component: Lent,
        meta: { title: '出租记录' }
      },
      {
        path: '/inventory',
        name: 'Inventory',
        component: Inventory,
        meta: { title: 'Steam库存' }
      },
      {
        path: '/setting',
        name: 'Setting',
        component: Setting,
        meta: { title: '设置' }
      },
      {
        path: '/stock-components',
        name: 'StockComponents',
        component: StockComponents,
        meta: { title: '库存组件' }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: Settings,
        meta: { title: '系统设置' },
        redirect: '/settings/data-source',
        children: [
          {
            path: 'data-source',
            name: 'DataSource',
            component: () => import('@/views/settings/DataSource.vue'),
            meta: { title: '数据来源' }
          },
          {
            path: 'auto-manager',
            name: 'AutoManager',
            component: () => import('@/views/settings/Automate_management.vue'),
            meta: { title: '自动化管理' }
          },
          {
            path: 'spider-rename',
            name: 'SpiderRename',
            component: () => import('@/views/settings/SpiderWeaponRename.vue'),
            meta: { title: '爬取改名' }
          },
          {
            path: 'spider-pendant',
            name: 'SpiderPendant',
            component: () => import('@/views/settings/SpiderPendant.vue'),
            meta: { title: '爬取挂件' }
          },
          {
            path: 'steam-market',
            name: 'SteamMarket',
            component: () => import('@/views/settings/SteamMarket.vue'),
            meta: { title: 'Steam市场历史' }
          },
          {
            path: 'steam-inventory-history',
            name: 'SteamInventoryHistory',
            component: () => import('@/views/settings/SteamInventoryHistory.vue'),
            meta: { title: 'Steam交易历史' }
          },
          {
            path: 'dev-tools',
            name: 'DevTools',
            component: () => import('@/views/settings/DevTool.vue'),
            meta: { title: '开荒工具' }
          },
          {
            path: 'system-settings',
            name: 'SystemSettings',
            component: () => import('@/views/settings/SystemSettings.vue'),
            meta: { title: '登录设置' }
          },
          {
            path: 'database-manager',
            name: 'DatabaseManager',
            component: () => import('@/views/settings/DatabaseManager.vue'),
            meta: { title: '数据库管理' }
          },
          {
            path: 'message-box',
            name: 'MessageBox',
            component: () => import('@/views/MessageBox.vue'),
            meta: { title: '悠悠有品消息' }
          }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 检查登录状态
async function checkLoginRequired() {
  try {
    const response = await axios.get(apiUrls.loginSettings())
    if (response.data.success) {
      return response.data.data.enableLogin || false
    }
    return false
  } catch (error) {
    console.error('检查登录状态失败:', error)
    return false
  }
}

// 全局路由守卫
router.beforeEach(async (to, from, next) => {
  // 如果是登录页面，直接通过
  if (to.path === '/login') {
    next()
    return
  }
  
  // 检查是否需要登录验证
  const loginRequired = await checkLoginRequired()
  
  if (!loginRequired) {
    // 不需要登录，直接通过
    next()
    return
  }
  
  // 需要登录，检查是否已登录
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
  const loginTime = localStorage.getItem('loginTime')
  
  // 检查登录是否过期（24小时）
  if (isLoggedIn && loginTime) {
    const now = new Date().getTime()
    const elapsed = now - parseInt(loginTime)
    const maxAge = 24 * 60 * 60 * 1000 // 24小时
    
    if (elapsed > maxAge) {
      // 登录已过期
      localStorage.removeItem('isLoggedIn')
      localStorage.removeItem('username')
      localStorage.removeItem('loginTime')
      next('/login')
      return
    }
  }
  
  if (isLoggedIn) {
    // 已登录，允许访问
    next()
  } else {
    // 未登录，跳转到登录页
    next('/login')
  }
})

export default router