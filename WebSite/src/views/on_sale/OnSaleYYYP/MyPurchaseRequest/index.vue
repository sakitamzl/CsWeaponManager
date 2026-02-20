<template>
  <div class="purchase-request-container">
    <div class="purchase-request-layout">
      <!-- 左半部分：正在求购 -->
      <div class="purchase-request-section">
        <div class="purchase-request-header">
          <h3>正在求购</h3>
          <el-button
            v-if="activePurchaseRequests.length > 0"
            type="primary"
            size="small"
            @click="handleBatchProcessActive"
          >
            批量处理
          </el-button>
        </div>

        <!-- 子标签页：求购中、暂停中、待支付 -->
        <div class="sub-tabs-bar">
          <div
            v-for="tab in subTabs"
            :key="tab.value"
            class="sub-tab"
            :class="{ active: activeSubTab === tab.value }"
            @click="activeSubTab = tab.value"
          >
            <span class="sub-tab-label">{{ tab.label }}</span>
            <span class="sub-tab-count">{{ getSubTabCount(tab.value) }}</span>
          </div>
        </div>

        <div class="purchase-request-content" v-loading="loading">
          <!-- 求购中列表 -->
          <div v-if="activeSubTab === 'purchasing'" class="request-list">
            <div
              v-for="item in purchasingItems"
              :key="item.id"
              class="purchase-request-item"
            >
              <div class="request-item-left">
                <div class="request-item-image">
                  <img
                    v-if="item.icon_url"
                    :src="item.icon_url"
                    :alt="item.item_name"
                    class="request-weapon-image"
                    @error="(e) => e.target.style.display = 'none'"
                  />
                  <div v-else class="request-image-placeholder">无图</div>
                </div>
                <div class="request-item-info">
                  <div class="request-item-name">
                    {{ item.item_name }}
                  </div>
                  <div class="request-item-details">
                    <el-tag
                      v-if="item.rarity"
                      :style="{ color: '#' + item.rarity_color, borderColor: '#' + item.rarity_color }"
                      size="small"
                    >
                      {{ item.rarity }}
                    </el-tag>
                    <el-tag
                      v-if="item.float_range"
                      :style="{ color: '#' + item.exterior_color, borderColor: '#' + item.exterior_color }"
                      size="small"
                    >
                      {{ item.float_range }}
                    </el-tag>
                    <span v-if="item.rank" class="rank-info-inline">
                      <span class="rank-label">排名:</span>
                      <span class="rank-value">{{ item.rank }}</span>
                    </span>
                    <span class="price-info-inline">
                      <span class="price-label">求购价:</span>
                      <span class="price-value">¥{{ item.purchase_price }}</span>
                    </span>
                    <span class="max-price-info-inline">
                      <span class="max-price-label">最高价:</span>
                      <span class="max-price-value">{{ item.max_purchase_price }}</span>
                    </span>
                    <span class="quantity-info-inline">
                      <span class="quantity-label">数量:</span>
                      <span class="buy-quantity">{{ item.buy_quantity }}</span>
                      <span class="quantity-separator">/</span>
                      <span class="total-quantity">{{ item.quantity }}</span>
                    </span>
                  </div>
                </div>
              </div>
              <div class="request-item-right">
                <div class="request-buttons">
                  <el-button
                    type="success"
                    size="default"
                    @click="handleQuickPriceIncrease(item)"
                  >
                    一键加价
                  </el-button>
                  <el-button
                    type="success"
                    size="default"
                    @click="handlePauseRequest(item)"
                  >
                    暂停
                  </el-button>
                  <el-button
                    type="success"
                    size="default"
                    @click="handleEditRequest(item)"
                  >
                    修改
                  </el-button>
                  <el-button
                    type="danger"
                    size="default"
                    @click="handleDeleteRequest(item)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </div>
            <div v-if="purchasingItems.length === 0" class="empty-request-list">
              <el-empty description="暂无求购中的物品" />
            </div>
          </div>

          <!-- 暂停中列表 -->
          <div v-if="activeSubTab === 'paused'" class="request-list">
            <div
              v-for="item in pausedItems"
              :key="item.id"
              class="purchase-request-item paused"
            >
              <div class="request-item-left">
                <div class="request-item-image">
                  <img
                    v-if="item.icon_url"
                    :src="item.icon_url"
                    :alt="item.item_name"
                    class="request-weapon-image"
                    @error="(e) => e.target.style.display = 'none'"
                  />
                  <div v-else class="request-image-placeholder">无图</div>
                </div>
                <div class="request-item-info">
                  <div class="request-item-name">
                    {{ item.item_name }}
                  </div>
                  <div class="request-item-details">
                    <el-tag
                      v-if="item.rarity"
                      :style="{ color: '#' + item.rarity_color, borderColor: '#' + item.rarity_color }"
                      size="small"
                    >
                      {{ item.rarity }}
                    </el-tag>
                    <el-tag
                      v-if="item.float_range"
                      :style="{ color: '#' + item.exterior_color, borderColor: '#' + item.exterior_color }"
                      size="small"
                    >
                      {{ item.float_range }}
                    </el-tag>
                    <el-tag v-if="item.weapon_type" size="small" type="info">
                      {{ item.weapon_type }}
                    </el-tag>
                  </div>
                  <div class="request-price-info">
                    <span class="price-label">求购价:</span>
                    <span class="price-value">¥{{ item.purchase_price }}</span>
                    <span class="quantity-label">数量:</span>
                    <span class="quantity-value">{{ item.quantity }}</span>
                  </div>
                </div>
              </div>
              <div class="request-item-right">
                <div class="request-time-info">
                  <div class="time-label">暂停时间</div>
                  <div class="time-value">{{ item.pause_time }}</div>
                </div>
                <div class="request-buttons">
                  <el-button
                    type="success"
                    size="small"
                    @click="handleResumeRequest(item)"
                  >
                    恢复
                  </el-button>
                  <el-button
                    type="primary"
                    size="small"
                    @click="handleEditRequest(item)"
                  >
                    修改
                  </el-button>
                  <el-button
                    type="danger"
                    size="small"
                    @click="handleCancelRequest(item)"
                  >
                    取消
                  </el-button>
                </div>
              </div>
            </div>
            <div v-if="pausedItems.length === 0" class="empty-request-list">
              <el-empty description="暂无暂停的求购" />
            </div>
          </div>

          <!-- 待支付列表 -->
          <div v-if="activeSubTab === 'pending_payment'" class="request-list">
            <div
              v-for="item in pendingPaymentItems"
              :key="item.id"
              class="purchase-request-item pending-payment"
            >
              <div class="request-item-left">
                <div class="request-item-image">
                  <img
                    v-if="item.icon_url"
                    :src="item.icon_url"
                    :alt="item.item_name"
                    class="request-weapon-image"
                    @error="(e) => e.target.style.display = 'none'"
                  />
                  <div v-else class="request-image-placeholder">无图</div>
                </div>
                <div class="request-item-info">
                  <div class="request-item-name">
                    {{ item.item_name }}
                  </div>
                  <div class="request-item-details">
                    <el-tag
                      v-if="item.rarity"
                      :style="{ color: '#' + item.rarity_color, borderColor: '#' + item.rarity_color }"
                      size="small"
                    >
                      {{ item.rarity }}
                    </el-tag>
                    <el-tag
                      v-if="item.float_range"
                      :style="{ color: '#' + item.exterior_color, borderColor: '#' + item.exterior_color }"
                      size="small"
                    >
                      {{ item.float_range }}
                    </el-tag>
                    <el-tag v-if="item.weapon_type" size="small" type="info">
                      {{ item.weapon_type }}
                    </el-tag>
                  </div>
                  <div class="request-price-info">
                    <span class="price-label">成交价:</span>
                    <span class="price-value highlight">¥{{ item.deal_price }}</span>
                    <span class="seller-label">卖家:</span>
                    <span class="seller-value">{{ item.seller_name }}</span>
                  </div>
                </div>
              </div>
              <div class="request-item-right">
                <div class="request-countdown">
                  <div class="countdown-label">剩余时间</div>
                  <div class="countdown-value" :class="{
                    'countdown-danger': item.remaining_seconds < 300,
                    'countdown-warning': item.remaining_seconds >= 300 && item.remaining_seconds < 600,
                    'countdown-normal': item.remaining_seconds >= 600
                  }">
                    {{ formatCountdown(item.remaining_seconds) }}
                  </div>
                </div>
                <div class="request-buttons">
                  <el-button
                    type="success"
                    size="small"
                    @click="handlePayNow(item)"
                  >
                    立即支付
                  </el-button>
                  <el-button
                    type="info"
                    size="small"
                    @click="handleViewDetails(item)"
                  >
                    详情
                  </el-button>
                </div>
              </div>
            </div>
            <div v-if="pendingPaymentItems.length === 0" class="empty-request-list">
              <el-empty description="暂无待支付订单" />
            </div>
          </div>
        </div>
      </div>

      <!-- 右半部分：求购记录 -->
      <div class="purchase-request-section">
        <div class="purchase-request-header">
          <h3>求购记录</h3>
          <div class="header-actions">
            <el-select
              v-model="historyFilter"
              size="small"
              style="width: 120px; margin-right: 10px;"
            >
              <el-option label="全部" value="all" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
              <el-option label="已超时" value="timeout" />
            </el-select>
          </div>
        </div>
        <div class="purchase-request-content" v-loading="loading">
          <div
            v-for="item in filteredHistoryItems"
            :key="item.id"
            class="purchase-request-item history"
          >
            <div class="request-item-left">
              <div class="request-item-image">
                <img
                  v-if="item.icon_url"
                  :src="item.icon_url"
                  :alt="item.item_name"
                  class="request-weapon-image"
                  @error="(e) => e.target.style.display = 'none'"
                />
                <div v-else class="request-image-placeholder">无图</div>
              </div>
              <div class="request-item-info">
                <div class="request-item-name">
                  {{ item.item_name }}
                </div>
                <div class="request-item-details">
                  <el-tag
                    v-if="item.rarity"
                    :style="{ color: '#' + item.rarity_color, borderColor: '#' + item.rarity_color }"
                    size="small"
                  >
                    {{ item.rarity }}
                  </el-tag>
                  <el-tag
                    v-if="item.float_range"
                    :style="{ color: '#' + item.exterior_color, borderColor: '#' + item.exterior_color }"
                    size="small"
                  >
                    {{ item.float_range }}
                  </el-tag>
                  <el-tag v-if="item.weapon_type" size="small" type="info">
                    {{ item.weapon_type }}
                  </el-tag>
                </div>
                <div class="request-price-info">
                  <span class="price-label">求购价:</span>
                  <span class="price-value">¥{{ item.purchase_price }}</span>
                  <span v-if="item.deal_price" class="deal-price-label">成交价:</span>
                  <span v-if="item.deal_price" class="deal-price-value">¥{{ item.deal_price }}</span>
                </div>
              </div>
            </div>
            <div class="request-item-right">
              <div class="request-status-info">
                <el-tag
                  :type="getHistoryStatusType(item.status)"
                  size="large"
                >
                  {{ getHistoryStatusLabel(item.status) }}
                </el-tag>
                <div class="status-time">{{ item.finish_time }}</div>
              </div>
              <div class="request-buttons">
                <el-button
                  v-if="item.status === 'completed'"
                  type="primary"
                  size="small"
                  @click="handleRepurchase(item)"
                >
                  再次求购
                </el-button>
                <el-button
                  type="info"
                  size="small"
                  @click="handleViewHistoryDetails(item)"
                >
                  详情
                </el-button>
              </div>
            </div>
          </div>
          <div v-if="filteredHistoryItems.length === 0" class="empty-request-list">
            <el-empty description="暂无求购记录" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script src="./useMyPurchaseRequest.js"></script>
<style scoped src="./styles.css"></style>
