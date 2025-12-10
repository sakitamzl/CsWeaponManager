import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  
  server: {
    port: 9003,
    proxy: {
      // 后端API服务器（9001端口） - 统一使用 /api 前缀
      '/api': {
        target: 'http://127.0.0.1:9001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // Spider API服务器（9002端口） - 统一使用 /spider 前缀
      '/spider': {
        target: 'http://127.0.0.1:9002',
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/spider/, ''),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq) => {
            proxyReq.setHeader('Connection', 'keep-alive')
            proxyReq.setHeader('Cache-Control', 'no-cache')
            proxyReq.setHeader('X-Accel-Buffering', 'no')
            proxyReq.setHeader('Accept', 'text/event-stream')
          })
          proxy.on('proxyRes', (proxyRes) => {
            if (proxyRes.headers) {
              proxyRes.headers['cache-control'] = 'no-cache'
              proxyRes.headers['x-accel-buffering'] = 'no'
              proxyRes.headers['connection'] = 'keep-alive'
              if (!proxyRes.headers['content-type'] || !proxyRes.headers['content-type'].includes('text/event-stream')) {
                proxyRes.headers['content-type'] = 'text/event-stream; charset=utf-8'
              }
            }
          })
        }
      }
    }
  },
  
  // 配置中间件来提供weapon_imgs静态文件
  configureServer(server) {
    const weaponImgsPath = path.join(__dirname, '..', 'weapon_imgs')
    
    server.middlewares.use('/weapon_imgs', (req, res, next) => {
      const filename = req.url.split('?')[0].substring(1) // 移除开头的 /
      const filePath = path.join(weaponImgsPath, filename)
      
      if (fs.existsSync(filePath)) {
        res.setHeader('Content-Type', 'image/jpeg')
        fs.createReadStream(filePath).pipe(res)
      } else {
        res.statusCode = 404
        res.end('Image not found')
      }
    })
  },
  
  define: {
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false),
    __VUE_OPTIONS_API__: JSON.stringify(true),
    __VUE_PROD_DEVTOOLS__: JSON.stringify(false)
  },
  
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // 确保 weapon_imgs 不会被包含在构建中
    rollupOptions: {
      external: []
    }
  }
})
