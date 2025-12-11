# 图片读取逻辑修改说明

## 修改概述
将前端直接读取图片的方式改为通过后端API返回图片，提高安全性和可控性。

## 修改内容

### 1. 后端新增图片API
**文件**: `backEnd/src/web_side/webSide/read_imges.py`

新增两个API接口：
- `GET /api/v1/images/weapon_image/<image_name>` - 获取武器图片
- `GET /api/v1/images/weapon_image/check/<image_name>` - 检查图片是否存在

图片文件夹路径：`backEnd/weapon_imgs/`（与backEnd.py同目录）

### 2. 后端注册Blueprint
**文件**: `backEnd/backEnd.py`

```python
from src.web_side.webSide.read_imges import readImagesV1
app.register_blueprint(readImagesV1, url_prefix='/api/v1/images')
```

### 3. 前端API配置
**文件**: `WebSite/src/config/api.js`

新增API配置：
```javascript
// ENDPOINTS
WEAPON_IMAGE: (imageName) => `/api/v1/images/weapon_image/${imageName}`,
WEAPON_IMAGE_CHECK: (imageName) => `/api/v1/images/weapon_image/check/${imageName}`,

// apiUrls快捷方法
weaponImage: (imageName) => getApiUrl(API_CONFIG.ENDPOINTS.WEAPON_IMAGE(imageName)),
weaponImageCheck: (imageName) => getApiUrl(API_CONFIG.ENDPOINTS.WEAPON_IMAGE_CHECK(imageName)),
```

### 4. 前端页面修改
修改以下Vue文件中的`getWeaponImage`函数，将图片路径从`/weapon_imgs/${imageName}`改为`apiUrls.weaponImage(imageName)`：

- `WebSite/src/views/Buy.vue`
- `WebSite/src/views/Sell.vue`
- `WebSite/src/views/Lent.vue`
- `WebSite/src/views/Inventory.vue`
- `WebSite/src/views/StockComponents.vue`

同时修改了这些文件中贴纸和挂件图片的生成逻辑。

## 使用示例

### 前端调用
```javascript
// 获取武器图片
const imageName = 'AK-47___Neon_Revolution.png'
const imageUrl = apiUrls.weaponImage(imageName)
// 返回: /api/v1/images/weapon_image/AK-47___Neon_Revolution.png

// 检查图片是否存在
const checkUrl = apiUrls.weaponImageCheck(imageName)
fetch(checkUrl).then(res => res.json()).then(data => {
  console.log(data.exists) // true/false
})
```

### 后端API响应
```python
# 成功返回图片
GET /api/v1/images/weapon_image/AK-47___Neon_Revolution.png
Response: 图片文件 (image/png)

# 图片不存在
Response: {"error": "Image not found", "message": "图片 xxx 不存在"} (404)

# 检查图片
GET /api/v1/images/weapon_image/check/AK-47___Neon_Revolution.png
Response: {"exists": true, "image_name": "AK-47___Neon_Revolution.png", "path": "..."}
```

## 优势
1. **安全性提升**：图片访问通过后端控制，可以添加权限验证
2. **统一管理**：所有资源访问通过API统一管理
3. **易于扩展**：可以添加图片缓存、压缩、水印等功能
4. **错误处理**：统一的错误处理和日志记录

## 注意事项
1. 图片文件夹路径为`backEnd/weapon_imgs/`
2. 前端通过代理访问：`/api` -> `http://127.0.0.1:9001`
3. vite.config.js中的weapon_imgs中间件可以保留作为开发环境的备用方案
