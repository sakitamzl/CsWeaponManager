# CS武器管理系统 - Vue前端

基于Vue 3 + Element Plus开发的CS武器管理系统前端界面。

## 功能特性

- 🎨 现代化暗色主题界面
- 📊 数据可视化仪表板
- 🔍 智能搜索和筛选
- 📱 响应式设计
- ⚡ 高性能数据表格
- 🔧 完整的设置管理
- 📈 实时数据统计

## 页面结构

```
src/
├── views/
│   ├── Layout.vue      # 主布局组件
│   ├── Home.vue        # 首页仪表板
│   ├── Buy.vue         # 购入记录页面
│   ├── Sell.vue        # 出售记录页面
│   ├── Inventory.vue   # Steam库存页面
│   ├── Setting.vue     # 设置页面
│   └── DataSource.vue  # 数据来源配置页面
├── router/
│   └── index.js        # 路由配置
├── assets/
│   └── css/
│       └── global.css  # 全局样式
├── App.vue             # 根组件
└── main.js             # 入口文件
```

## 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Vue Router 4** - 官方路由管理器
- **Element Plus** - Vue 3 UI组件库
- **Axios** - HTTP客户端
- **Vite** - 现代化构建工具

## 安装和运行

1. 安装依赖：
```bash
cd VUE
npm install
```

2. 启动开发服务器：
```bash
npm run serve
# 或
npm run dev
```

3. 构建生产版本：
```bash
npm run build
```

## 配置说明

### 代理配置
在 `vue.config.js` 中配置了API代理，将 `/api` 请求代理到后端服务器：

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
    pathRewrite: {
      '^/api': ''
    }
  }
}
```

### 静态资源
图标文件需要放置在后端的 `/static/icons/` 目录下，前端通过绝对路径引用。

## 页面功能

### 🏠 首页 (Home.vue)
- 数据统计卡片
- 最近活动列表
- 快速操作入口

### 💰 购入页面 (Buy.vue)
- 购入记录表格
- 搜索和筛选
- 状态管理
- 快速操作（出售、出租）

### 💸 出售页面 (Sell.vue)
- 出售记录表格
- 盈亏计算和显示
- 出售统计汇总
- 详情查看功能

### 📦 库存页面 (Inventory.vue)
- Steam库存展示
- 武器类型筛选
- 库存统计
- 快速出售/出租
- 市场价格查询

### ⚙️ 设置页面 (Setting.vue)
- 基本设置
- API配置
- 通知设置
- 数据管理
- 系统信息

### 🔌 数据来源 (DataSource.vue)
- 数据源配置
- 连接测试
- 状态监控
- 统计分析

## 样式说明

### 颜色方案
- 主背景：`#121212`
- 卡片背景：`#1e1e1e`
- 次级背景：`#2a2a2a`
- 边框颜色：`#333`
- 主色调：`#4CAF50`
- 文字颜色：`#fff` / `#ccc`

### 响应式断点
- 移动端：`< 768px`
- 平板：`768px - 1024px`
- 桌面：`> 1024px`

## 开发规范

1. **组件命名**：使用PascalCase
2. **文件命名**：使用PascalCase.vue
3. **样式作用域**：使用scoped样式
4. **数据管理**：使用Composition API
5. **错误处理**：统一使用ElMessage显示错误

## API集成

前端通过Axios调用后端API，主要端点：

- `GET /api/stats` - 获取统计数据
- `GET /api/buy` - 获取购入记录
- `GET /api/sell` - 获取出售记录
- `GET /api/inventory` - 获取库存数据
- `POST /api/settings` - 保存设置
- `GET /api/data-sources` - 获取数据源列表

## 注意事项

1. 确保后端服务器在端口5000运行
2. 静态资源路径需要与后端保持一致
3. 所有API调用都需要正确的错误处理
4. 生产环境需要配置正确的publicPath

## 部署说明

1. 构建项目：`npm run build`
2. 将`dist`目录内容部署到Web服务器
3. 配置服务器代理API请求到后端
4. 确保静态资源路径正确