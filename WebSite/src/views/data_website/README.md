# 第三方数据网站模块

## 概述
该模块用于集成第三方CS饰品数据平台，目前支持CSQAQ数据开放API。

## 页面列表

### 1. 市场大盘 (MarketOverview.vue)
- **路径**: `/data-website/market-overview`
- **功能**: 
  - 显示CS饰品市场指数K线图
  - 支持多种时间周期（1分钟、5分钟、15分钟、30分钟、1小时、4小时、1天、1周）
  - 显示MA5、MA10、MA20移动平均线
  - 实时统计数据（最新价格、涨跌幅、最高价、最低价）
  - 支持数据缩放和拖拽查看
- **API**: `https://api.csqaq.com/api/kline`
- **参数**:
  - `period`: 时间周期（1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w）
  - `limit`: 数据条数（10-1000）

### 2. CSQAQ (CSQAQ.vue)
- **路径**: `/data-website/csqaq`
- **功能**: 
  - 饰品数据查询
  - 按名称或ID搜索
  - 显示详细信息

## 技术栈
- Vue 3 Composition API
- Element Plus UI组件库
- ECharts 图表库
- Axios HTTP客户端

## 安装依赖

```bash
cd WebSite
npm install
```

确保已安装以下依赖：
- echarts: ^5.4.3
- element-plus: ^2.3.8
- axios: ^1.4.0

## API文档

### CSQAQ 数据开放API

#### 获取指数K线图
- **接口**: `GET https://api.csqaq.com/api/kline`
- **参数**:
  - `period`: 时间周期
    - `1m`: 1分钟
    - `5m`: 5分钟
    - `15m`: 15分钟
    - `30m`: 30分钟
    - `1h`: 1小时
    - `4h`: 4小时
    - `1d`: 1天
    - `1w`: 1周
  - `limit`: 返回数据条数（默认100，最大1000）

- **响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "time": "2024-01-01 12:00",
      "open": "1000.00",
      "close": "1010.00",
      "high": "1020.00",
      "low": "995.00"
    }
  ]
}
```

## 使用说明

1. 启动开发服务器：
```bash
npm run serve
```

2. 访问页面：
   - 主页面: `http://localhost:8080/data-website`
   - 市场大盘: `http://localhost:8080/data-website/market-overview`
   - CSQAQ: `http://localhost:8080/data-website/csqaq`

3. 在左侧主导航中点击"第三方数据网站"进入模块

## 功能特点

### 市场大盘页面
- ✅ 实时K线图展示
- ✅ 多周期切换
- ✅ 移动平均线（MA5/MA10/MA20）
- ✅ 数据缩放和拖拽
- ✅ 统计信息面板
- ✅ 深色主题
- ✅ 响应式设计
- ✅ 自动刷新功能
- ✅ 错误处理和模拟数据

### 图表交互
- 鼠标滚轮：缩放图表
- 鼠标拖拽：移动查看不同时间段
- 悬停：显示详细数据
- 底部滑块：快速定位

## 注意事项

1. **API调用**: 
   - 如果API调用失败，系统会自动使用模拟数据
   - 建议配置CORS或使用代理服务器

2. **性能优化**:
   - 图表会在组件卸载时自动销毁
   - 窗口大小变化时自动调整图表尺寸

3. **数据更新**:
   - 点击"刷新数据"按钮手动更新
   - 可以根据需要添加自动刷新功能

## 扩展开发

### 添加新页面
1. 在 `WebSite/src/views/data_website/` 创建新的Vue文件
2. 在 `WebSite/src/router/index.js` 添加路由配置
3. 在 `DataWebsite.vue` 的侧边栏添加菜单项

### 添加新API
1. 在页面组件中使用axios调用API
2. 处理响应数据
3. 更新UI显示

## 故障排除

### 图表不显示
- 检查echarts是否正确安装
- 确认chartRef已正确绑定
- 查看浏览器控制台错误信息

### API调用失败
- 检查网络连接
- 确认API地址正确
- 查看CORS配置
- 系统会自动降级到模拟数据

### 样式问题
- 确认Element Plus主题正确加载
- 检查CSS变量定义
- 查看响应式断点设置
