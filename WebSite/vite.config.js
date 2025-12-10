import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'

const SPIDER_PROXY_TARGET = 'http://127.0.0.1:9002'

const prepareSseProxyReq = (proxyReq) => {
  if (!proxyReq) return
  proxyReq.setHeader('Connection', 'keep-alive')
  proxyReq.setHeader('Cache-Control', 'no-cache')
  proxyReq.setHeader('X-Accel-Buffering', 'no')
  proxyReq.setHeader('Accept', 'text/event-stream')
}

const ensureSseProxyResHeaders = (proxyRes) => {
  if (!proxyRes || !proxyRes.headers) return
  proxyRes.headers['cache-control'] = 'no-cache'
  proxyRes.headers['x-accel-buffering'] = 'no'
  proxyRes.headers['connection'] = 'keep-alive'
  if (!proxyRes.headers['content-type'] || !proxyRes.headers['content-type'].includes('text/event-stream')) {
    proxyRes.headers['content-type'] = 'text/event-stream; charset=utf-8'
  }
}

export default defineConfig({
  plugins: [vue()],
  
  server: {
    port: 9003,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:9001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/spider': {
        target: SPIDER_PROXY_TARGET,
        changeOrigin: true,
        ws: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/spider/, ''),
        configure: (proxy, options) => {
          proxy.on('proxyReq', prepareSseProxyReq)
          proxy.on('proxyRes', ensureSseProxyResHeaders)
        }
      }
    },
    // 配置中间件处理 weapon_imgs
    middlewareMode: false
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },

  define: {
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false),
    __VUE_OPTIONS_API__: JSON.stringify(true),
    __VUE_PROD_DEVTOOLS__: JSON.stringify(false)
  },

  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'echarts': ['echarts']
        }
      }
    }
  },

  // 添加自定义中间件处理 weapon_imgs
  configureServer: (server) => {
    const weaponImgsPath = path.resolve(__dirname, '..', 'weapon_imgs')
    
    server.middlewares.use((req, res, next) => {
      if (req.url && req.url.startsWith('/weapon_imgs/')) {
        const filename = req.url.replace('/weapon_imgs/', '')
        const filePath = path.join(weaponImgsPath, filename)
        
        if (fs.existsSync(filePath)) {
          const ext = path.extname(filename).toLowerCase()
          const contentTypes = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp'
          }
          
          res.setHeader('Content-Type', contentTypes[ext] || 'application/octet-stream')
          fs.createReadStream(filePath).pipe(res)
        } else {
          res.statusCode = 404
          res.end('Image not found')
        }
      } else {
        next()
      }
    })
  }
})
