import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
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
  if (e.message.includes('ResizeObserver loop completed with undelivered notifications') ||
      e.message.includes('ResizeObserver loop limit exceeded')) {
    e.stopImmediatePropagation()
    return false
  }
})

const app = createApp(App)

app.config.errorHandler = (err, vm, info) => {
  if (err.message && err.message.includes('ResizeObserver')) {
    return
  }
  console.error('Vue error:', err, info)
}

app.use(router)
app.use(ElementPlus)

app.mount('#app')