const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 9003,
    historyApiFallback: true,  // 添加 HTML5 History 模式支持，解决刷新404问题
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:9001',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      },
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