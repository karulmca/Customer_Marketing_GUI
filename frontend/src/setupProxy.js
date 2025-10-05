const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Only proxy API requests to the FastAPI backend
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      logLevel: 'silent',  // Reduce proxy logging
      pathRewrite: {
        '^/api': '/api'  // Keep the /api prefix
      }
    })
  );
};