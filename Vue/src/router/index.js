import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/Layout.vue'
import Home from '@/views/Home.vue'
import Buy from '@/views/Buy.vue'
import Sell from '@/views/Sell.vue'
import Lent from '@/views/Lent.vue'
import Inventory from '@/views/Inventory.vue'
import Setting from '@/views/Setting.vue'
import DataSource from '@/views/DataSource.vue'

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
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router