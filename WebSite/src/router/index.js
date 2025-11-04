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

const routes = [
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
            path: 'spider-sticker',
            name: 'SpiderSticker',
            component: () => import('@/views/settings/SpiderSticker.vue'),
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
            meta: { title: '开发工具' }
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

export default router