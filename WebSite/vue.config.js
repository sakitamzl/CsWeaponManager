const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

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
        target: 'http://127.0.0.1:9002',
        changeOrigin: true,
        pathRewrite: {
          '^/spider': ''
        }
      }
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