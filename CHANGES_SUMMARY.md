# 库存组件页面 - 平台价格更新逻辑修改

## 修改内容

### 1. 后端修改 (`backEnd/src/web_side/webSide/stock_components.py`)

**修改的接口**: `/fill_reference_price/<steam_id>/<source>`

**主要变更**:
- 添加了 `force_update` 参数支持（从请求 JSON body 中获取）
- 当 `force_update=True` 时，强制更新所有匹配到的价格字段，即使当前价格与目标价格相同
- 当 `force_update=False` 时，保持原有逻辑（仅更新空值或不同的价格）
- 在返回消息中显示更新模式（"强制更新" 或 "增量更新"）
- 在返回数据中添加 `force_update` 字段

**修改前的逻辑**:
```python
# 如果当前价格与目标价格相同，跳过更新
if current_price_str == target_price:
    unchanged += 1
    continue
```

**修改后的逻辑**:
```python
# 如果不是强制更新模式，且当前价格与目标价格相同，则跳过
if not force_update and current_price_str == target_price:
    unchanged += 1
    continue
```

### 2. 前端修改 (`WebSite/src/views/StockComponents.vue`)

**主要变更**:
1. **按钮文案更新**: "获取/更新平台价格" → "强制更新平台价格"
2. **提示信息优化**: 
   - 开始时显示 "正在强制更新平台价格..."
   - 成功时显示更新的具体数量
3. **数据刷新增强**: 更新完成后同时刷新统计数据和列表数据

**修改的函数**: `handleFillAllPlatformPrices`

**关键改进**:
```javascript
// 成功后显示详细的更新信息
ElMessage.success({
  message: `平台价格强制更新完成！\n悠悠有品：更新 ${yyypData.updated} 条\nBUFF：更新 ${buffData.updated} 条`,
  duration: 5000,
  showClose: true
})

// 同时刷新统计数据和列表数据
await loadStats()
await (groupMode.value ? loadGroupedData() : loadComponentData())
```

## 功能说明

### 使用场景

1. **强制更新模式** (点击"强制更新平台价格"按钮):
   - 所有匹配到价格的组件都会被更新
   - 即使当前价格与 weapon_classID 表中的价格相同，也会执行 UPDATE 操作
   - 适用于需要确保所有价格数据与价格表完全同步的场景

2. **增量更新模式** (如果需要，可以通过 API 直接调用):
   - 仅更新空值或与价格表不同的价格
   - 减少不必要的数据库写操作
   - 适用于日常的价格同步

### API 调用示例

```javascript
// 强制更新
await axios.post('/api/components/fill_reference_price/steamid123/yyyp', {
  force_update: true
})

// 增量更新
await axios.post('/api/components/fill_reference_price/steamid123/yyyp', {
  force_update: false
})
```

## 测试建议

1. 选择一个 Steam 账号
2. 点击"强制更新平台价格"按钮
3. 观察提示信息，确认更新的数量
4. 检查数据库中的价格字段是否已更新
5. 验证统计卡片和列表数据是否同步刷新

## 影响范围

- ✅ 不影响现有的其他功能
- ✅ 向后兼容（不传 force_update 参数时默认为 False）
- ✅ 提升用户体验（明确的按钮文案和详细的反馈信息）
