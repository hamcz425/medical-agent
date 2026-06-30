const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack');

module.exports = (env, argv) => {
  const isProd = argv.mode === 'production';

  const definePluginEntries = {
    'process.env.NODE_ENV': JSON.stringify(isProd ? 'production' : 'development')
  };

  if (isProd) {
    for (const [key, val] of Object.entries(process.env)) {
      if (key.startsWith('REACT_APP_')) {
        definePluginEntries[`process.env.${key}`] = JSON.stringify(val);
      }
    }
  }

  return {
    entry: './src/index.tsx',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'bundle.[contenthash].js',
      clean: true
    },
    resolve: {
      extensions: ['.tsx', '.ts', '.js']
    },
    module: {
      rules: [
        {
          test: /\.(ts|tsx)$/,
          use: 'ts-loader',
          exclude: /node_modules/
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader']
        },
        {
          test: /\.(png|jpg|jpeg|gif|svg)$/,
          type: 'asset/resource'
        }
      ]
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: './public/index.html'
      }),
      new webpack.DefinePlugin(definePluginEntries)
    ],
    devServer: {
      static: {
        directory: path.join(__dirname, 'public')
      },
      hot: true,
      port: 3001,
      historyApiFallback: true,
      proxy: [
        {
          context: ['/api'],
          target: 'http://localhost:8000',
          changeOrigin: true
        }
      ]
    }
  };
};
