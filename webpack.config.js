// index.html 진입점
// asset에 데이터 다들어있으니 연결해야함

// 1. entry
// 2. output
// 3. loader
// 4. plugin

const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
    entry: './index.html', // 진입점
    mode: 'development', // 'development' or 'production
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: 'bundle.js',
    },
    module: {
        rules: [
            {
                test: /\.html$/,
                use: 'html-loader',
            },
            {
                test: /\.css$/,
                use: [MiniCssExtractPlugin.loader, 'css-loader'],
            },
        ],
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './index.html', // 여기에 HTML 파일 경로를 지정합니다.
            filename: 'index.html', // 출력될 파일 이름을 지정합니다.
            minify: false, // 빌드시 HTML 파일을 압축합니다.
        }),
        new MiniCssExtractPlugin({
            filename: './assets/css/style.css',
        }),
        new CleanWebpackPlugin(),
        new CopyWebpackPlugin({
            patterns: [
                {
                    from: 'assets/pyscript',
                    to: 'assets/pyscript',
                },
                {
                    from: 'assets/model',
                    to: 'assets/model',
                },
                {
                    from: 'assets/data',
                    to: 'assets/data',
                },
                {
                    from: 'assets/img',
                    to: 'assets/img',
                },
                {
                    from: 'assets/py',
                    to: 'assets/py',
                },
                {
                    from: 'assets/js',
                    to: 'assets/js',
                },
            ],
        }),
    ],
    devServer: {
        static: {
            directory: path.resolve(__dirname, 'dist'),
        },
        port: 5501,
    },
    stats: {
        errorDetails: true,
    },
};
