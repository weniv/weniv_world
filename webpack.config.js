// index.html 진입점
// asset에 데이터 다들어있으니 연결해야함

// 1. entry
// 2. output
// 3. loader
// 4. plugin

const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
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
                test: /\.(png|jpe?g|gif|svg|webp)$/i,
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            name: '[path][name].[ext]',  // 원래의 경로와 파일 이름을 유지
                            context: path.resolve(__dirname, 'assets'),  // 상대 경로의 시작점 지정
                            outputPath: 'assets',  // 출력 경로 지정
                            publicPath: 'assets',  // 가상 경로 지정
                        },
                    },
                ],
            },
            // {
            //     test: /\.s[ac]ss$/i,
            //     use: ['style-loader', 'css-loader', 'sass-loader'],
            // },
            // {
            //     test: /\.css$/i,
            //     use: ['style-loader', 'css-loader'],
            // },

            // ... 기타 로더 ...
        ],
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './index.html', // 여기에 HTML 파일 경로를 지정합니다.
            filename: 'index.html', // 출력될 파일 이름을 지정합니다.
            minify: false, // 빌드시 HTML 파일을 압축합니다.
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
                    from: 'assets/tutorial',
                    to: 'assets/tutorial',
                },
                {
                    from: 'assets/css',
                    to: 'assets/css',
                },
                {
                    from: 'assets/py',
                    to: 'assets/py',
                },
            ],
        }),
        // ... 기타 플러그인 ...
    ],
};