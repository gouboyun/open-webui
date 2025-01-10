import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	define: {
		APP_VERSION: JSON.stringify(process.env.npm_package_version),
		APP_BUILD_HASH: JSON.stringify(process.env.APP_BUILD_HASH || 'dev-build')
	},
	build: {
		sourcemap: true
	},
	worker: {
		format: 'es'
	},
	server: {
		proxy: {
			'/api': {
				target: 'http://gmk8.netbird.selfhosted:9321',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api/, '/api')
			},
			'/ollama': {
				target: 'http://gmk8.netbird.selfhosted:9321',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/ollama/, '/ollama')
			},
			'/openai': {
				target: 'http://gmk8.netbird.selfhosted:9321',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/openai/, '/openai')
			},
			'/ws': {
				// WebSocket目标服务器地址
				target: 'ws://gmk8.netbird.selfhosted:9321',
				// 允许跨域
				changeOrigin: true,
				// 配置为ws或wss协议
				ws: true
			}
			// 'http://gmk8.netbird.selfhosted:9321/api/config': {
			// 	target: 'http://gmk8.netbird.selfhosted/9321', // 远程服务器地址
			// 	changeOrigin: true,
			// 	configure: (proxy) => {
			//     console.log('********************')
			// 		proxy.on('proxyReq', (proxyReq, req) => {
			// 			// 将本地请求的Cookie复制到代理请求中
			// 			proxyReq.setHeader('Cookie', req.headers.cookie);
			// 		});
			// 	}
			// }
		}
	}
});
