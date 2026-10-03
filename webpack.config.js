// 배포 빌드: index.html(압축)과 assets/를 dist/로 복사합니다.
// 앱 코드는 브라우저 ES 모듈(assets/js/app/)을 그대로 쓰므로 번들링하지 않습니다.
//
// npm run build  → dist/
// npm start      → 개발 서버 (http://localhost:5501)

const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = (env, argv) => ({
    // 번들할 JS가 없으므로 빈 진입점을 사용합니다.
    entry: {},
    output: {
        path: path.resolve(__dirname, 'dist'),
        clean: true,
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './index.html',
            filename: 'index.html',
            inject: false,
            minify:
                argv.mode === 'production'
                    ? {
                          collapseWhitespace: true,
                          removeComments: true,
                          removeRedundantAttributes: true,
                          removeScriptTypeAttributes: false,
                          useShortDoctype: true,
                          minifyCSS: true,
                          minifyJS: true,
                      }
                    : false,
        }),
        new CopyWebpackPlugin({
            patterns: [
                {
                    from: 'assets',
                    to: 'assets',
                    globOptions: {
                        ignore: [
                            '**/*.scss',
                            '**/__pycache__/**',
                            '**/.DS_Store',
                        ],
                    },
                },
            ],
        }),
    ],
    devServer: {
        static: { directory: path.resolve(__dirname, 'dist') },
        port: 5501,
    },
    // 이미지·PDF 같은 정적 파일을 복사만 하므로 번들 크기 경고는 끕니다.
    performance: { hints: false },
    stats: 'errors-warnings',
});
