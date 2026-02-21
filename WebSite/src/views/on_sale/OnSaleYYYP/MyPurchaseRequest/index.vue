<template>
  <div class="purchase-request-container">
    <div class="purchase-request-layout">
      <!-- 左半部分：正在求购（含求购记录标签） -->
      <div class="purchase-request-section">
        <div class="purchase-request-header">
          <h3>正在求购</h3>
          <div class="header-actions">
            <el-select
              v-if="activeSubTab === 'history'"
              v-model="historyFilter"
              size="small"
              style="width: 120px;"
            >
              <el-option label="全部" value="all" />
              <el-option label="已完成" value="completed" />
              <el-option label="已删除" value="deleted" />
            </el-select>
            <el-button
              v-else
              size="small"
              :loading="loading"
              @click="loadCurrentTabData"
            >
              刷新列表
            </el-button>
          </div>
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

        <div
          class="purchase-request-content"
          v-loading="loading"
          v-infinite-scroll="loadMoreCurrentTab"
          :infinite-scroll-disabled="currentTabScrollDisabled"
          :infinite-scroll-distance="30"
        >
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
            <div v-if="purchasingItems.length === 0 && !purchasingLoading && !purchasingHasMore" class="empty-request-list">
              <el-empty description="暂无求购中的物品" />
            </div>
            <div v-if="purchasingLoading" class="history-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载中...</span>
            </div>
            <div v-if="!purchasingHasMore && purchasingItems.length > 0" class="history-no-more">
              已加载全部
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
                  <el-tooltip
                    v-if="parseFloat(item.purchase_price) > parseFloat(item.max_purchase_price)"
                    content="求购价高于最高价，无法开启"
                    placement="top"
                  >
                    <span>
                      <el-button
                        type="success"
                        size="default"
                        disabled
                      >
                        开启
                      </el-button>
                    </span>
                  </el-tooltip>
                  <el-button
                    v-else
                    type="success"
                    size="default"
                    @click="handleResumeRequest(item)"
                  >
                    开启
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
                    取消
                  </el-button>
                </div>
              </div>
            </div>
            <div v-if="pausedItems.length === 0 && !pausedLoading && !pausedHasMore" class="empty-request-list">
              <el-empty description="暂无暂停的求购" />
            </div>
            <div v-if="pausedLoading" class="history-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载中...</span>
            </div>
            <div v-if="!pausedHasMore && pausedItems.length > 0" class="history-no-more">
              已加载全部
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

          <!-- 求购记录列表 -->
          <div v-if="activeSubTab === 'history'" class="request-list">
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
                      v-if="item.float_range"
                      size="small"
                      type="info"
                    >
                      {{ item.float_range }}
                    </el-tag>
                    <span class="price-info-inline">
                      <span class="price-label">求购价:</span>
                      <span class="price-value">¥{{ item.purchase_price }}</span>
                    </span>
                    <span class="quantity-info-inline">
                      <span class="quantity-label">已购:</span>
                      <span class="buy-quantity">{{ item.buy_quantity }}</span>
                      <span class="quantity-separator">/</span>
                      <span class="total-quantity">{{ item.quantity }}</span>
                    </span>
                  </div>
                  <div class="record-time">{{ item.last_update_time }}</div>
                </div>
              </div>
              <div class="request-item-right">
                <div class="request-status-info">
                  <el-tag
                    :type="getHistoryStatusType(item.status)"
                    size="large"
                  >
                    {{ item.status_text }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div v-if="filteredHistoryItems.length === 0 && !historyLoading && !historyHasMore" class="empty-request-list">
              <el-empty description="暂无求购记录" />
            </div>
            <div v-if="historyLoading" class="history-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载中...</span>
            </div>
            <div v-if="!historyHasMore && filteredHistoryItems.length > 0" class="history-no-more">
              已加载全部记录
            </div>
          </div>
        </div>
      </div>

      <!-- 右半部分：发布求购 -->
      <div class="purchase-request-section">
        <div class="purchase-request-header">
          <h3>发布求购</h3>
          <div class="header-actions">
            <div class="balance-display">
              <span class="balance-label">求购余额</span>
              <span class="balance-value" v-loading="balanceLoading">
                ¥{{ purchaseBalance !== null ? purchaseBalance.balance_yuan.toFixed(2) : '--' }}
              </span>
            </div>
            <el-button size="small" type="primary" @click="handleTransferIn">从钱包余额转入</el-button>
            <el-button size="small" type="warning" @click="handleTransferOut">转出到钱包</el-button>
          </div>
        </div>
        <div class="publish-search-area">
          <el-input
            v-model="searchKeyword"
            placeholder="输入饰品名称搜索"
            class="publish-search-input"
            clearable
            @keyup.enter="handleSearchTemplate"
          />
          <el-button
            type="primary"
            :loading="searchLoading"
            @click="handleSearchTemplate"
          >
            搜索
          </el-button>
        </div>
        <div class="purchase-request-content">
          <!-- 搜索结果列表 -->
          <div v-if="searchResults.length > 0" class="request-list">
            <div
              v-for="item in searchResults"
              :key="item.id"
              class="purchase-request-item search-result"
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
                  <div class="request-item-name">{{ item.item_name }}</div>
                  <div class="request-item-details">
                    <el-tag
                      v-if="item.quality && item.quality !== '普通' && item.quality !== 'StatTrak™'"
                      :style="{ color: '#' + item.quality_color, borderColor: '#' + item.quality_color }"
                      size="small"
                    >
                      {{ item.quality }}
                    </el-tag>
                    <span class="price-info-inline">
                      <span class="price-label">参考价:</span>
                      <span class="price-value">¥{{ item.price }}</span>
                    </span>
                    <span class="search-result-on-sale">
                      <span class="price-label">在售:</span>
                      <span class="price-value">{{ item.on_sale_count }}</span>
                    </span>
                    <span v-if="item.purchase_count_text" class="search-result-purchasing">
                      {{ item.purchase_count_text }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="request-item-right">
                <div class="request-buttons">
                  <el-button
                    type="primary"
                    size="default"
                    @click="handlePublishRequest(item)"
                  >
                    发布求购
                  </el-button>
                  <el-button
                    type="info"
                    size="default"
                    @click="handleViewMarket(item)"
                  >
                    查看市场
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <!-- 空状态 -->
          <div v-else-if="!searchLoading" class="empty-request-list">
            <el-empty description="输入饰品名称搜索" />
          </div>
          <!-- 搜索中 -->
          <div v-if="searchLoading" class="history-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>搜索中...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改求购对话框 -->
    <EditPurchaseOrderDialog
      v-model:visible="editDialogVisible"
      :order-data="editOrderData"
      @submit="handleSubmitEdit"
    />

    <!-- 发布求购对话框 -->
    <PublishPurchaseDialog
      v-model:visible="publishDialogVisible"
      :template-data="publishDialogData"
      @submit="handleSubmitPublish"
    />

    <!-- 从钱包转入对话框 -->
    <TransferInDialog
      v-model:visible="transferInDialogVisible"
      :available-yuan="transferInAvailableYuan"
      @confirm="handleTransferInConfirm"
    />

    <!-- 转出到钱包对话框 -->
    <TransferOutDialog
      v-model:visible="transferOutDialogVisible"
      :available-yuan="purchaseBalance ? purchaseBalance.balance_yuan : 0"
      @confirm="handleTransferOutConfirm"
    />
  </div>
</template>

<script>
import { Loading } from '@element-plus/icons-vue'
import EditPurchaseOrderDialog from './EditPurchaseOrderDialog.vue'
import PublishPurchaseDialog from './PublishPurchaseDialog.vue'
import TransferInDialog from './TransferInDialog.vue'
import TransferOutDialog from './TransferOutDialog.vue'
import useMyPurchaseRequest from './useMyPurchaseRequest.js'

export default {
  name: 'MyPurchaseRequest',
  components: {
    EditPurchaseOrderDialog,
    PublishPurchaseDialog,
    TransferInDialog,
    TransferOutDialog,
    Loading
  },
  ...useMyPurchaseRequest
}
</script>
<style scoped src="./styles.css"></style>
