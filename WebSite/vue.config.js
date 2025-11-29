const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')
const path = require('path')

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

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 9003,
    historyApiFallback: {
      index: '/index.html',
      rewrites: [
        // 不重写静态资源请求
        { from: /\.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$/i, to: context => context.parsedUrl.pathname },
        // API 请求不重写
        { from: /^\/api/, to: context => context.parsedUrl.pathname },
        { from: /^\/spider/, to: context => context.parsedUrl.pathname },
        // 其他所有请求重写到 index.html
        { from: /./, to: '/index.html' }
      ],
      verbose: true
    },
    proxy: {
      // 后端API服务器（9001端口） - 统一使用 /api 前缀
      '/api': {
        target: 'http://127.0.0.1:9001',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      },
      // Spider API服务器（9002端口） - 统一使用 /spider 前缀
      '/spider': {
        target: SPIDER_PROXY_TARGET,
        changeOrigin: true,
        ws: true,
        secure: false,
        logLevel: 'silent',
        pathRewrite: {
          '^/spider': ''
        },
        proxyTimeout: 0,
        timeout: 0,
        onProxyReq: prepareSseProxyReq,
        onProxyRes: ensureSseProxyResHeaders
      },
    },
    // 动态提供静态文件，不加载到内存
    onBeforeSetupMiddleware: (devServer) => {
      const fs = require('fs')
      const weaponImgsPath = path.join(__dirname, '..', 'weapon_imgs')

      devServer.app.get('/weapon_imgs/:filename', (req, res) => {
        const filename = req.params.filename
        const filePath = path.join(weaponImgsPath, filename)

        // 检查文件是否存在
        if (fs.existsSync(filePath)) {
          // 直接流式传输文件，不加载到内存
          res.sendFile(filePath)
        } else {
          res.status(404).send('Image not found')
        }
      })
    }
  },

  publicPath: '/',

  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false),
        __VUE_OPTIONS_API__: JSON.stringify(true),
        __VUE_PROD_DEVTOOLS__: JSON.stringify(false)
      })
    ]
  },

  // 确保 weapon_imgs 不会被包含在生产构建中
  // weapon_imgs 是一个独立的图片包，应该单独部署
  // 注意：Vue CLI 默认只会打包 public 目录和 src 中静态导入的资源
  // weapon_imgs 不在 public 目录，也不在 src 中被静态导入，因此不会被包含
  chainWebpack: (config) => {
    // 确保 CopyWebpackPlugin 不会复制 weapon_imgs
    // Vue CLI 默认只复制 public 目录，但为了安全起见，明确排除 weapon_imgs
    config.plugin('copy').tap((args) => {
      if (args && args[0] && Array.isArray(args[0])) {
        // 如果 args[0] 是数组（Vue CLI 5.x 格式）
        args[0] = args[0].filter(
          pattern => !pattern.from || (typeof pattern.from === 'string' && !pattern.from.includes('weapon_imgs'))
        )
      } else if (args && args[0] && args[0].patterns) {
        // 如果 args[0] 是对象，包含 patterns 数组（某些版本格式）
        args[0].patterns = args[0].patterns.filter(
          pattern => !pattern.from || (typeof pattern.from === 'string' && !pattern.from.includes('weapon_imgs'))
        )
      }
      return args
    })
  }
})