import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/Layout.vue'
import Home from '@/views/Home.vue'
import ItemSearch from '@/views/ItemSearch.vue'
import Buy from '@/views/Buy.vue'
import Sell from '@/views/Sell.vue'
import Lent from '@/views/Lent.vue'
import Inventory from '@/views/Inventory.vue'
import Setting from '@/views/Setting.vue'
import DataSource from '@/views/DataSource.vue'
import SteamMarket from '@/views/SteamMarket.vue'
import SteamInventoryHistory from '@/views/SteamInventoryHistory.vue'
import StockComponents from '@/views/StockComponents.vue'
import DevTool from '@/views/DevTool.vue'
import SpiderWeaponRename from '@/views/SpiderWeaponRename.vue'
import Automation from '@/views/Automation.vue'

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
        path: '/data-source',
        name: 'DataSource',
        component: DataSource,
        meta: { title: '数据来源' }
      },
      {
        path: '/steam-market',
        name: 'SteamMarket',
        component: SteamMarket,
        meta: { title: 'Steam市场历史' }
      },
      {
        path: '/steam-inventory-history',
        name: 'SteamInventoryHistory',
        component: SteamInventoryHistory,
        meta: { title: 'Steam交易历史' }
      },
      {
        path: '/stock-components',
        name: 'StockComponents',
        component: StockComponents,
        meta: { title: '库存组件' }
      },
      {
        path: '/devTool',
        name: 'DevTool',
        component: DevTool,
        meta: { title: '开发工具' }
      },
      {
        path: '/automation',
        name: 'Automation',
        component: Automation,
        meta: { title: '其他工具' }
      }
    ]
  },
  {
    path: '/spider-weapon-rename',
    name: 'SpiderWeaponRename',
    component: SpiderWeaponRename,
    meta: { title: '饰品重命名工具' }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router