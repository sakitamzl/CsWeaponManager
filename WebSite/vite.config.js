import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'

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
      '/api': {
        target: 'http://127.0.0.1:9001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/spider': {
        target: 'http://127.0.0.1:9002',
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/spider/, ''),
        configure: (proxy) => {
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
  
  configureServer(server) {
    const weaponImgsPath = path.join(__dirname, '..', 'weapon_imgs')
    
    server.middlewares.use((req, res, next) => {
      if (req.url && req.url.startsWith('/weapon_imgs/')) {
        const urlPath = req.url.split('?')[0]
        const filename = decodeURIComponent(urlPath.replace('/weapon_imgs/', ''))
        const filePath = path.join(weaponImgsPath, filename)
        
        if (fs.existsSync(filePath)) {
          const ext = path.extname(filePath).toLowerCase()
          const contentTypes = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
          }
          res.setHeader('Content-Type', contentTypes[ext] || 'image/jpeg')
          fs.createReadStream(filePath).pipe(res)
        } else {
          res.statusCode = 404
          res.end('Image not found')
        }
      } else {
        next()
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
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'echarts': ['echarts']
        }
      }
    }
  }
})
