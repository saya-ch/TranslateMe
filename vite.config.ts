import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 使用相对路径 base，保证 dist 可打包为 HTML Zip 并在本地静态环境打开
export default defineConfig({
  base: './',
  plugins: [react()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
