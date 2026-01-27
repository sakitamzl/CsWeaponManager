<template>
  <div class="rent-form-yyyp">
    <div class="form-header">
      <div class="form-title">
        <span class="item-count">1个饰品上架</span>
      </div>
    </div>

    <div class="form-content">
      <!-- 交易方式 -->
      <div class="form-section">
        <div class="section-label">交易方式</div>
        <div class="trade-mode-buttons">
          <div
            class="trade-mode-btn"
            :class="{ active: formData.tradeMode === 'rent' }"
            @click="formData.tradeMode = 'rent'"
          >
            <span class="mode-label">租赁</span>
          </div>
          <div
            class="trade-mode-btn"
            :class="{ active: formData.tradeMode === 'rentOrSale' }"
            @click="formData.tradeMode = 'rentOrSale'"
          >
            <span class="mode-label">可租可售</span>
          </div>
        </div>
      </div>

      <!-- 出租天数 -->
      <div class="form-section">
        <div class="section-label">出租天数</div>
        <div class="rent-days-buttons">
          <div
            class="rent-day-btn"
            :class="{ active: formData.rentDays === 10 }"
            @click="formData.rentDays = 10"
          >
            <span class="day-label">10天</span>
          </div>
          <div
            class="rent-day-btn"
            :class="{ active: formData.rentDays === 21 }"
            @click="formData.rentDays = 21"
          >
            <span class="day-label">21天</span>
          </div>
          <div
            class="rent-day-btn"
            :class="{ active: formData.rentDays === 30 }"
            @click="formData.rentDays = 30"
          >
            <span class="day-label">30天</span>
          </div>
          <div
            class="rent-day-btn custom-btn"
            :class="{ active: formData.rentDays === 'custom' }"
            @click="formData.rentDays = 'custom'"
          >
            <span class="day-label">自定义</span>
          </div>
        </div>
        <!-- 自定义天数输入 -->
        <div v-if="formData.rentDays === 'custom'" class="custom-days-input">
          <el-input
            v-model="formData.customDays"
            placeholder="请输入天数"
            type="number"
          />
        </div>
      </div>

      <!-- 短租租金 -->
      <div class="form-section">
        <div class="section-label">短租租金</div>
        <div class="input-with-tips">
          <el-input
            v-model="formData.shortRentPrice"
            placeholder="租金<=0.89更快出租"
            class="price-input"
          >
            <template #prepend>¥</template>
          </el-input>
          <div class="input-tip">租金<=0.89更快出租</div>
        </div>
      </div>

      <!-- 押金赔付 -->
      <div class="form-section">
        <div class="section-label">押金赔付</div>
        <div class="deposit-compensation-card">
          <div class="compensation-icon">
            <span class="icon-badge">V</span>
          </div>
          <div class="compensation-content">
            <div class="compensation-text">买断或不归还,全额赔押金,赔付服务费</div>
            <div class="service-fee">
              <span class="fee-value highlight">8%</span>
              <span class="fee-original">15%</span>
            </div>
          </div>
          <div class="compensation-arrow">›</div>
        </div>
      </div>

      <!-- 商品押金 -->
      <div class="form-section">
        <div class="section-label">商品押金</div>
        <div class="input-with-tips">
          <el-input
            v-model="formData.depositPrice"
            placeholder="押金<=1299,优先展示"
            class="price-input"
          >
            <template #prepend>¥</template>
          </el-input>
          <div class="input-tip">押金<=1299,优先展示</div>
        </div>
      </div>

      <!-- 增值服务 -->
      <div class="form-section">
        <div class="section-label">增值服务</div>
        <div class="value-added-services">
          <div class="service-item" @click="toggleService('zeroCooldown')">
            <div class="service-checkbox">
              <el-checkbox v-model="formData.services.zeroCooldown" />
            </div>
            <div class="service-info">
              <span class="service-badge zero-cd">0CD出租</span>
              <span class="service-label">租送活动</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作按钮 -->
    <div class="form-footer">
      <el-button class="footer-btn cancel-btn" @click="handleCancel">
        取消
      </el-button>
      <el-button class="footer-btn submit-btn" type="primary" @click="handleSubmit">
        确认上架
      </el-button>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'RentFormYYYP',
  emits: ['cancel', 'submit'],
  setup(props, { emit }) {
    // 表单数据
    const formData = reactive({
      tradeMode: 'rent', // 'rent' | 'rentOrSale'
      rentDays: 10, // 10 | 21 | 30 | 'custom'
      customDays: null,
      shortRentPrice: '',
      depositPrice: '',
      services: {
        zeroCooldown: false // 0CD出租
      }
    })

    // 切换服务选项
    const toggleService = (serviceName) => {
      formData.services[serviceName] = !formData.services[serviceName]
    }

    // 处理取消
    const handleCancel = () => {
      emit('cancel')
    }

    // 处理提交
    const handleSubmit = () => {
      // 验证表单
      if (!validateForm()) {
        return
      }

      // 准备提交数据
      const submitData = {
        tradeMode: formData.tradeMode,
        rentDays: formData.rentDays === 'custom' ? formData.customDays : formData.rentDays,
        shortRentPrice: parseFloat(formData.shortRentPrice),
        depositPrice: parseFloat(formData.depositPrice),
        services: formData.services
      }

      emit('submit', submitData)
    }

    // 表单验证
    const validateForm = () => {
      // 验证租赁天数
      if (formData.rentDays === 'custom') {
        if (!formData.customDays || formData.customDays <= 0) {
          ElMessage.warning('请输入有效的租赁天数')
          return false
        }
      }

      // 验证短租租金
      if (!formData.shortRentPrice || formData.shortRentPrice === '') {
        ElMessage.warning('请输入短租租金')
        return false
      }
      const shortRent = parseFloat(formData.shortRentPrice)
      if (isNaN(shortRent) || shortRent <= 0) {
        ElMessage.warning('请输入有效的短租租金')
        return false
      }

      // 验证押金
      if (!formData.depositPrice || formData.depositPrice === '') {
        ElMessage.warning('请输入商品押金')
        return false
      }
      const deposit = parseFloat(formData.depositPrice)
      if (isNaN(deposit) || deposit <= 0) {
        ElMessage.warning('请输入有效的押金')
        return false
      }

      return true
    }

    return {
      formData,
      toggleService,
      handleCancel,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.rent-form-yyyp {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1a1a1a;
  color: #fff;
}

/* 表单头部 */
.form-header {
  padding: 1rem 1.5rem;
  background: #2a2a2a;
  border-bottom: 1px solid #3a3a3a;
}

.form-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-count {
  font-size: 1.2rem;
  font-weight: bold;
  color: #fff;
}

/* 表单内容 */
.form-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

/* 表单区块 */
.form-section {
  margin-bottom: 1.5rem;
}

.section-label {
  font-size: 0.95rem;
  color: #ccc;
  margin-bottom: 0.75rem;
  font-weight: 500;
}

/* 交易方式按钮 */
.trade-mode-buttons {
  display: flex;
  gap: 1rem;
}

.trade-mode-btn {
  flex: 1;
  padding: 1rem;
  background: #2a2a2a;
  border: 2px solid #3a3a3a;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.trade-mode-btn:hover {
  background: #333;
  border-color: #4a4a4a;
}

.trade-mode-btn.active {
  background: rgba(64, 158, 255, 0.1);
  border-color: #409EFF;
}

.mode-label {
  font-size: 1rem;
  font-weight: 500;
  color: #fff;
}

/* 出租天数按钮 */
.rent-days-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.rent-day-btn {
  padding: 0.75rem;
  background: #2a2a2a;
  border: 2px solid #3a3a3a;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.rent-day-btn:hover {
  background: #333;
  border-color: #4a4a4a;
}

.rent-day-btn.active {
  background: rgba(64, 158, 255, 0.1);
  border-color: #409EFF;
}

.day-label {
  font-size: 0.95rem;
  font-weight: 500;
  color: #fff;
}

/* 自定义天数输入 */
.custom-days-input {
  margin-top: 0.75rem;
}

/* 输入框带提示 */
.input-with-tips {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.price-input {
  width: 100%;
}

.input-tip {
  font-size: 0.85rem;
  color: #999;
  padding-left: 0.25rem;
}

/* 押金赔付卡片 */
.deposit-compensation-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #2a2a2a;
  border: 2px solid #3a3a3a;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.deposit-compensation-card:hover {
  background: #333;
  border-color: #4a4a4a;
}

.compensation-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-badge {
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff;
}

.compensation-content {
  flex: 1;
}

.compensation-text {
  font-size: 0.9rem;
  color: #fff;
  margin-bottom: 0.25rem;
}

.service-fee {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.fee-value {
  font-size: 1rem;
  font-weight: bold;
  color: #fff;
}

.fee-value.highlight {
  color: #f56c6c;
}

.fee-original {
  font-size: 0.85rem;
  color: #999;
  text-decoration: line-through;
}

.compensation-arrow {
  font-size: 1.5rem;
  color: #666;
}

/* 增值服务 */
.value-added-services {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.service-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #2a2a2a;
  border: 2px solid #3a3a3a;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.service-item:hover {
  background: #333;
  border-color: #4a4a4a;
}

.service-checkbox {
  flex-shrink: 0;
}

.service-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.service-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
}

.service-badge.zero-cd {
  background: linear-gradient(135deg, #409EFF, #3A8EE6);
}

.service-label {
  font-size: 0.9rem;
  color: #fff;
}

/* 底部操作栏 */
.form-footer {
  display: flex;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: #2a2a2a;
  border-top: 1px solid #3a3a3a;
}

.footer-btn {
  flex: 1;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
}

.cancel-btn {
  background: #3a3a3a;
  color: #fff;
  border: none;
}

.cancel-btn:hover {
  background: #4a4a4a;
}

.submit-btn {
  background: linear-gradient(135deg, #409EFF, #3A8EE6);
  border: none;
}

.submit-btn:hover {
  opacity: 0.9;
}

/* 滚动条样式 */
.form-content::-webkit-scrollbar {
  width: 6px;
}

.form-content::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.form-content::-webkit-scrollbar-thumb {
  background: #3a3a3a;
  border-radius: 3px;
}

.form-content::-webkit-scrollbar-thumb:hover {
  background: #4a4a4a;
}

/* Element Plus 样式覆盖 */
:deep(.el-input__wrapper) {
  background-color: #2a2a2a;
  border: 2px solid #3a3a3a;
  box-shadow: none;
  border-radius: 8px;
  padding: 0.75rem;
}

:deep(.el-input__wrapper:hover) {
  border-color: #4a4a4a;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #409EFF;
}

:deep(.el-input__inner) {
  color: #fff;
  font-size: 1rem;
}

:deep(.el-input-group__prepend) {
  background-color: #1a1a1a;
  color: #fff;
  border: none;
  padding: 0 1rem;
}

:deep(.el-checkbox__inner) {
  background-color: #2a2a2a;
  border-color: #3a3a3a;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #409EFF;
  border-color: #409EFF;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .rent-days-buttons {
    grid-template-columns: repeat(2, 1fr);
  }

  .trade-mode-buttons {
    flex-direction: column;
  }

  .form-content {
    padding: 1rem;
  }

  .form-footer {
    padding: 1rem;
  }
}
</style>
