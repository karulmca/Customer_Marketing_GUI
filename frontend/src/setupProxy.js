const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Get backend URL from environment or use default
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
  
  // Only proxy API requests to the FastAPI backend
  app.use(
    '/api',
    createProxyMiddleware({
      target: backendUrl,
      changeOrigin: true,
      secure: false,
      logLevel: 'silent',  // Reduce proxy logging
      pathRewrite: {
        '^/api': '/api'  // Keep the /api prefix
      }
    })
  );
};