const { CracoAliasPlugin } = require("@craco/craco");

module.exports = {
  plugins: [],
  devServer: {
    // Fix for allowedHosts error
    allowedHosts: 'all',
    // Alternative specific configuration
    // allowedHosts: ['localhost', '127.0.0.1', '::1'],
    client: {
      webSocketURL: {
        hostname: 'localhost',
        pathname: '/ws',
        port: 3000,
        protocol: 'ws',
      },
    },
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization',
    },
  },
  webpack: {
    configure: (webpackConfig, { env, paths }) => {
      // Additional webpack configurations if needed
      return webpackConfig;
    },
  },
};