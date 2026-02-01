<template>
  <div class="rented-out-container">
    <div v-loading="loading" class="card-grid">
      <!-- 卡片显示 -->
      <div
        v-for="item in rentedOutItems"
        :key="item.id"
        class="inventory-card"
      >
        <div class="card-image">
          <img
            v-if="item.icon_url"
            :src="item.icon_url"
            :alt="item.item_name"
            class="weapon-image"
            @error="(e) => e.target.style.display = 'none'"
          />
          <div v-else class="image-placeholder">
            <span>无图片</span>
          </div>
          <!-- 状态标签 - 左上角 -->
          <div v-if="item.order_status_desc" class="status-overlay">
            {{ item.order_status_desc }}
          </div>
        </div>
        <div class="card-content">
          <div class="card-title" :title="item.item_name">
            {{ item.item_name }}
          </div>
          <div class="card-info">
            <!-- 磨损值显示条 -->
            <div class="float-bar-container" v-if="item.abrade">
              <div class="float-bar">
                <div class="float-segment fn" title="崭新出厂 (0.00 - 0.07)"></div>
                <div class="float-segment mw" title="略有磨损 (0.07 - 0.15)"></div>
                <div class="float-segment ft" title="久经沙场 (0.15 - 0.38)"></div>
                <div class="float-segment ww" title="破损不堪 (0.38 - 0.45)"></div>
                <div class="float-segment bs" title="战痕累累 (0.45 - 1.00)"></div>
                <div
                  class="float-pointer"
                  :style="{ left: `${parseFloat(item.abrade) * 100}%` }"
                  :title="`磨损值: ${item.abrade}`"
                ></div>
              </div>
            </div>
            <div class="float-value" v-if="item.abrade">
              {{ parseFloat(item.abrade).toFixed(4) }}
            </div>
          </div>
          <div class="card-prices">
            <!-- 租赁信息 -->
            <div class="price-row">
              <div class="price-group">
                <span class="price-label">租金:</span>
                <span class="price-value sale-price">¥{{ item.rent_amount }}</span>
              </div>
              <div class="price-group">
                <span class="price-label">押金:</span>
                <span class="price-value">¥{{ item.deposit_amount }}</span>
              </div>
            </div>
            <div class="price-row">
              <div class="price-group">
                <span class="price-label">租期:</span>
                <span class="price-value">{{ item.lease_days }}天</span>
              </div>
              <div class="price-group">
                <span class="price-label">到期:</span>
                <span class="price-value" style="font-size: 0.65rem;">{{ item.expire_time }}</span>
              </div>
            </div>
            <div class="price-row" v-if="item.remaining_seconds !== null && item.remaining_seconds !== undefined">
              <div class="price-group">
                <span class="price-label">剩余:</span>
                <span class="price-value" :class="item.remaining_seconds <= 0 ? 'price-loss' : 'sale-price'">
                  {{ formatCountdown(item.remaining_seconds) }}
                </span>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <div class="card-actions">
              <el-button size="small" type="primary" @click.stop="handleTransfer(item)">
                上架过户
              </el-button>
              <el-button size="small" type="warning" @click.stop="handleCancelSublease(item)">
                取消转租
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="rentedOutItems.length === 0" class="empty-state">
        <el-empty description="暂无已租出记录" />
      </div>
    </div>
  </div>
</template>

<script src="./useRentedOut.js"></script>
<style scoped src="./styles.css"></style>
