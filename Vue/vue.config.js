const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 9001,
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

  publicPath: process.env.NODE_ENV === 'production' ? './' : '/'
})