const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: [], 
  
  chainWebpack: config => {
    config.plugins.delete('progress')
  },

  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        pathRewrite: { '^/api': '' }
      }
    }
  }
})