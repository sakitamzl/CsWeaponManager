import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import 'element-plus/dist/index.css'
import './assets/css/global.css'

// 忽略 ResizeObserver 错误
const debounce = (fn, delay) => {
  let timeoutId
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn.apply(null, args), delay)
  }
}

const _ResizeObserver = window.ResizeObserver
window.ResizeObserver = class ResizeObserver extends _ResizeObserver {
  constructor(callback) {
    callback = debounce(callback, 16)
    super(callback)
  }
}

// 全局错误处理
window.addEventListener('error', (e) => {
  const msg = e.message || ''

  // 忽略 ResizeObserver 相关噪音错误
  if (
    msg.includes('ResizeObserver loop completed with undelivered notifications') ||
    msg.includes('ResizeObserver loop limit exceeded')
  ) {
    e.stopImmediatePropagation()
    return false
  }

  // 忽略 getBoundingClientRect 相关错误
  if (msg.includes('getBoundingClientRect')) {
    e.stopImmediatePropagation()
    e.preventDefault()
    return false
  }

  // 忽略 ElementPlus 内部触发的 getComputedStyle 类型错误
  // 典型信息: Failed to execute 'getComputedStyle' on 'Window': parameter 1 is not of type 'Element'.
  if (msg.includes('getComputedStyle')) {
    e.stopImmediatePropagation()
    e.preventDefault()
    return false
  }
})

const app = createApp(App)

app.config.errorHandler = (err, vm, info) => {
  const msg = err && err.message ? err.message : ''

  // 忽略部分已知的 UI 噪音错误
  if (
    msg.includes('ResizeObserver') ||
    msg.includes('getBoundingClientRect') ||
    msg.includes('getComputedStyle')
  ) {
    return
  }

  console.error('Vue error:', err, info)
}

dayjs.locale('zh-cn')

app.use(router)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')