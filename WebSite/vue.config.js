const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

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
        // weapon_imgs 请求不重写
        { from: /^\/weapon_imgs/, to: context => context.parsedUrl.pathname },
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
    // 添加静态文件服务配置 - 将 weapon_imgs 映射到项目根目录
    static: {
      directory: require('path').join(__dirname, '..', 'weapon_imgs'),
      publicPath: '/weapon_imgs',
      serveIndex: false
    }
  },

  publicPath: process.env.NODE_ENV === 'production' ? './' : '/',

  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false),
        __VUE_OPTIONS_API__: JSON.stringify(true),
        __VUE_PROD_DEVTOOLS__: JSON.stringify(false)
      })
    ]
  }
})