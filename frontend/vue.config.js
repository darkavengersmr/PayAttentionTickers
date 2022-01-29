module.exports = {
    devServer: {
      proxy: {
        '^/': {
          target: 'http://127.0.0.1:5000',
          ws: true,
          changeOrigin: true
        },
        '^/charts': {
          target: 'http://127.0.0.1:5000/charts'
        }
      }
    }
  }

/*
  module.exports = {
    devServer: {
        proxy: 'http://127.0.0.1:5000'
    }
}
*/