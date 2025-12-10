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
    fs: {
      // 允许访问项目根目录外的文件
      strict: false,
      allow: ['..']
    }
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
    console.log('武器图片路径:', weaponImgsPath)
    
    server.middlewares.use((req, res, next) => {
      if (req.url && req.url.startsWith('/weapon_imgs/')) {
        // 移除查询参数
        const urlPath = req.url.split('?')[0]
        const filename = decodeURIComponent(urlPath.replace('/weapon_imgs/', ''))

        // 尝试查找文件,支持 png 和 jpg 扩展名
        let filePath = path.join(weaponImgsPath, filename)
        let actualFilePath = null

        // 如果请求的文件直接存在
        if (fs.existsSync(filePath)) {
          actualFilePath = filePath
        } else {
          // 尝试不同的扩展名
          const filenameWithoutExt = filename.replace(/\.(png|jpg|jpeg)$/i, '')
          const extensions = ['.png', '.jpg', '.jpeg']

          for (const ext of extensions) {
            const testPath = path.join(weaponImgsPath, filenameWithoutExt + ext)
            if (fs.existsSync(testPath)) {
              actualFilePath = testPath
              break
            }
          }
        }

        if (actualFilePath) {
          const ext = path.extname(actualFilePath).toLowerCase()
          const contentTypes = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp'
          }

          res.setHeader('Content-Type', contentTypes[ext] || 'application/octet-stream')
          res.setHeader('Cache-Control', 'public, max-age=31536000')
          res.setHeader('Access-Control-Allow-Origin', '*')

          const stream = fs.createReadStream(actualFilePath)
          stream.on('error', (err) => {
            console.error('读取文件错误:', err)
            res.statusCode = 500
            res.end('Error reading file')
          })
          stream.pipe(res)
        } else {
          console.log('文件不存在:', filename)
          res.statusCode = 404
          res.end('Image not found: ' + filename)
        }
      } else {
        next()
      }
    })
  }
})
