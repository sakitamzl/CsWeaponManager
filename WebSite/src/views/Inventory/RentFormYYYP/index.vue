<template>
  <div class="rent-form-yyyp">
    <!-- 头部标题已简化，去掉“X个饰品上架”提示 -->

    <div class="form-content">
      <!-- 交易方式 + 押金赔付 + 增值服务 -->
      <div class="form-section">
        <div class="trade-and-services-row">
          <!-- 交易方式 -->
          <div class="trade-mode-block trade-card">
            <div class="trade-mode-buttons">
              <div
                v-for="method in tradeMethods"
                :key="method.id"
                class="trade-mode-btn"
                :class="{ active: formData.tradeMode === method.type }"
                @click="formData.tradeMode = method.type"
              >
                <span class="mode-label">{{ method.name }}</span>
              </div>
            </div>
          </div>

          <!-- 押金赔付 -->
          <div class="trade-card deposit-card">
            <div class="compensation-icon">
              <span class="icon-badge">V</span>
            </div>
            <div class="compensation-content">
              <div class="compensation-text" v-html="compensationRichText"></div>
            </div>
          </div>

          <!-- 增值服务 -->
          <div class="trade-card services-card">
            <div class="value-added-inline">
              <!-- 0CD出租 -->
              <div
                class="service-item-inline service-switch-item"
                :class="{ disabled: !canEnableZeroCD }"
              >
                <span class="service-label">
                  <span class="service-badge zero-cd">0CD</span>
                </span>
                <el-switch
                  v-model="formData.services.zeroCooldown"
                  size="large"
                  :disabled="!canEnableZeroCD"
                />
              </div>

              <!-- 租送活动 -->
              <div
                class="service-item-inline service-switch-item"
              >
                <span class="service-label">
                  <span class="service-badge rent-activity">租送</span>
                </span>
                <el-switch
                  v-model="formData.services.rentActivity"
                  size="large"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 出租天数 -->
      <div class="form-section">
        <div class="section-label">出租天数</div>
        <div class="rent-days-buttons">
          <div
            v-for="days in rentDaysOptions"
            :key="days"
            class="rent-day-btn"
            :class="{ active: formData.rentDays === days }"
            @click="formData.rentDays = days"
          >
            <span class="day-label">{{ days }}天</span>
          </div>
          <!-- 自定义天数输入框 -->
          <div class="rent-day-input-wrapper">
            <el-input
              v-model="formData.customDays"
              placeholder="自定义"
              type="number"
              :min="minRentDays"
              :max="maxRentDays"
              class="custom-days-inline-input"
              @focus="formData.rentDays = 'custom'"
            >
              <template #suffix>
                <span class="input-suffix">天</span>
              </template>
            </el-input>
          </div>
        </div>
      </div>

      <!-- 选中的饰品列表 -->
      <div class="form-section">
        <div class="section-label">选中的饰品</div>
        <div class="items-list">
          <div
            v-for="(item, index) in items"
            :key="item.assetid"
            class="item-card"
          >
            <!-- 左侧：饰品信息 -->
            <div class="item-left-box">
              <div class="item-image">
                <img
                  v-if="item.image"
                  :src="item.image"
                  :alt="item.name"
                  @error="handleImageError"
                />
                <div v-else class="image-placeholder">无图</div>
              </div>
              <div class="item-info">
                <div class="item-name" :title="item.name">{{ item.name }}</div>
                
                <!-- 磨损值 -->
                <div v-if="item.float" class="item-float-text">
                  磨损: {{ item.float }}
                </div>
                
                <!-- 磨损进度条 -->
                <div v-if="item.float" class="float-bar">
                  <div class="float-segment fn"></div>
                  <div class="float-segment mw"></div>
                  <div class="float-segment ft"></div>
                  <div class="float-segment ww"></div>
                  <div class="float-segment bs"></div>
                  <div
                    class="float-pointer"
                    :style="{ left: `${parseFloat(item.float) * 100}%` }"
                  ></div>
                </div>
                
                <!-- 购入价格 -->
                <div v-if="item.buyPrice" class="item-buy-price">
                  购入: ¥{{ item.buyPrice }}
                </div>
              </div>
            </div>

            <!-- 右侧：输入框 -->
            <div class="item-right-box">
              <!-- 短租租金 -->
              <el-input
                v-model="itemFormMap[item.assetid].shortRentPrice"
                placeholder="短租租金"
                class="price-input"
              />

              <!-- 长租租金（租期≤21天时禁用） -->
              <el-input
                v-model="itemFormMap[item.assetid].longRentPrice"
                placeholder="长租租金"
                :disabled="!showLongRentPrice"
                class="price-input"
              />

              <!-- 商品押金 -->
              <el-input
                v-model="itemFormMap[item.assetid].depositPrice"
                placeholder="商品押金"
                class="price-input"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作按钮 -->
    <div class="form-footer">
      <el-button
        class="footer-btn auto-price-btn"
        @click="handleAutoPricing"
        :loading="autoPricingLoading"
      >
        一键定价
      </el-button>
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
import { useRentFormYYYP } from './useRentFormYYYP.js'

export default {
  name: 'RentFormYYYP',
  props: {
    items: {
      type: Array,
      default: () => []
    },
    initData: {
      type: Object,
      default: () => null
    },
    steamId: {
      type: String,
      default: ''
    }
  },
  emits: ['cancel', 'submit'],
  setup(props, context) {
    return useRentFormYYYP(props, context)
  }
}
</script>

<style scoped src="./styles.css"></style>
