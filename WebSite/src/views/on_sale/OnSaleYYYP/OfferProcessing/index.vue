<template>
  <div class="offer-list-container">
    <div class="offer-list-layout">
      <!-- 左半部分：我出售的 -->
      <div class="offer-list-section">
        <div class="offer-list-header">
          <h3>我出售的</h3>
          <el-button
            v-if="sellOrders.length > 0"
            type="primary"
            size="small"
            @click="handleBatchProcessSell"
          >
            批量处理
          </el-button>
        </div>
        <div class="offer-list-content" v-loading="loading">
          <div
            v-for="item in sellOrders"
            :key="item.id"
            class="offer-list-item"
          >
            <div class="offer-item-left">
              <div class="offer-item-image">
                <img
                  v-if="item.icon_url"
                  :src="item.icon_url"
                  :alt="item.item_name"
                  class="offer-weapon-image"
                  @error="(e) => e.target.style.display = 'none'"
                />
                <div v-else class="offer-image-placeholder">无图</div>
              </div>
              <div class="offer-item-info">
                <div class="offer-item-name">
                  <el-tag
                    v-if="item.order_type"
                    size="small"
                    class="order-type-tag"
                    :class="{ 'tag-rent': item.order_type === 1, 'tag-sell': item.order_type === 2 }"
                  >
                    {{ getOrderTypeLabel(item.order_type) }}
                  </el-tag>
                  {{ item.item_name }}
                </div>
                <div class="offer-item-details">
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
              </div>
            </div>
            <!-- Token确认信息 - 中间区域 -->
            <div v-if="getTokenInfo(item.order_no)" class="offer-item-center">
              <div class="token-info-card" :class="{ 'token-card-rent': item.order_type === 1, 'token-card-sell': item.order_type === 2 }">
                <div class="token-info-body">
                  <img
                    v-if="getTokenInfo(item.order_no).avatarfull"
                    :src="getTokenInfo(item.order_no).avatarfull"
                    alt="头像"
                    class="token-avatar"
                  />
                  <div class="token-user-details">
                    <div class="token-username">{{ getTokenInfo(item.order_no).personaName || 'NotTGn' }}</div>
                    <div class="token-badges">
                      <div class="token-badge-circle">
                        <span>{{ getTokenInfo(item.order_no).playerLevel || '9' }}</span>
                      </div>
                      <div class="token-badge-square">
                        <span>{{ getTokenInfo(item.order_no).gameTime || '7' }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="token-join-date">
                  Steam加入时间：{{ getTokenInfo(item.order_no).joinSteamDate || '2018-12-22' }}
                </div>
              </div>
            </div>
            <div class="offer-item-right">
              <div class="offer-countdown">
                <div class="countdown-value" :class="{
                  'countdown-danger': item.remaining_seconds > 0 && item.remaining_seconds < 3600,
                  'countdown-warning': item.remaining_seconds >= 3600 && item.remaining_seconds < 21600,
                  'countdown-normal': item.remaining_seconds >= 21600,
                  'countdown-expired': item.remaining_seconds <= 0
                }">
                  {{ formatCountdown(item.remaining_seconds) }}
                </div>
                <div class="countdown-desc">{{ item.end_countdown_desc }}</div>
              </div>
              <div class="offer-buttons">
                <el-button
                  v-for="button in getSortedButtons(item.buttons)"
                  :key="button.type"
                  :type="button.action === 'confirm' ? 'success' : 'primary'"
                  size="small"
                  :disabled="button.name === '手动确认'"
                  @click.stop="handleOfferButton(item, button)"
                  :style="{
                    backgroundColor: button.fill_color || undefined,
                    borderColor: button.border_color || undefined,
                    color: button.text_color || undefined
                  }"
                >
                  {{ button.name }}
                </el-button>
              </div>
            </div>
          </div>
          <div v-if="sellOrders.length === 0" class="empty-offer-list">
            <el-empty description="暂无待确认报价" />
          </div>
        </div>
      </div>
      <!-- 右半部分：我收货的 -->
      <div class="offer-list-section">
        <div class="offer-list-header">
          <h3>我收货的</h3>
          <el-button
            v-if="buyOrders.length > 0"
            type="primary"
            size="small"
            @click="handleBatchProcessBuy"
          >
            批量处理
          </el-button>
        </div>
        <div class="offer-list-content" v-loading="loading">
          <div
            v-for="item in buyOrders"
            :key="item.id"
            class="offer-list-item"
          >
            <div class="offer-item-left">
              <div class="offer-item-image">
                <img
                  v-if="item.icon_url"
                  :src="item.icon_url"
                  :alt="item.item_name"
                  class="offer-weapon-image"
                  @error="(e) => e.target.style.display = 'none'"
                />
                <div v-else class="offer-image-placeholder">无图</div>
              </div>
              <div class="offer-item-info">
                <div class="offer-item-name">
                  <el-tag
                    v-if="item.order_type"
                    size="small"
                    class="order-type-tag"
                    :class="{ 'tag-rent': item.order_type === 1, 'tag-sell': item.order_type === 2 }"
                  >
                    {{ getOrderTypeLabel(item.order_type) }}
                  </el-tag>
                  {{ item.item_name }}
                </div>
                <div class="offer-item-details">
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
              </div>
            </div>
            <!-- Token确认信息 - 中间区域 -->
            <div v-if="getTokenInfo(item.order_no)" class="offer-item-center">
              <div class="token-info-card" :class="{ 'token-card-rent': item.order_type === 1, 'token-card-sell': item.order_type === 2 }">
                <div class="token-info-body">
                  <img
                    v-if="getTokenInfo(item.order_no).avatarfull"
                    :src="getTokenInfo(item.order_no).avatarfull"
                    alt="头像"
                    class="token-avatar"
                  />
                  <div class="token-user-details">
                    <div class="token-username">{{ getTokenInfo(item.order_no).personaName || 'NotTGn' }}</div>
                    <div class="token-badges">
                      <div class="token-badge-circle">
                        <span>{{ getTokenInfo(item.order_no).playerLevel || '9' }}</span>
                      </div>
                      <div class="token-badge-square">
                        <span>{{ getTokenInfo(item.order_no).gameTime || '7' }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="token-join-date">
                  Steam加入时间：{{ getTokenInfo(item.order_no).joinSteamDate || '2018-12-22' }}
                </div>
              </div>
            </div>
            <div class="offer-item-right">
              <div class="offer-countdown">
                <div class="countdown-value" :class="{
                  'countdown-danger': item.remaining_seconds > 0 && item.remaining_seconds < 3600,
                  'countdown-warning': item.remaining_seconds >= 3600 && item.remaining_seconds < 21600,
                  'countdown-normal': item.remaining_seconds >= 21600,
                  'countdown-expired': item.remaining_seconds <= 0
                }">
                  {{ formatCountdown(item.remaining_seconds) }}
                </div>
                <div class="countdown-desc">{{ item.end_countdown_desc }}</div>
              </div>
              <div class="offer-buttons">
                <el-button
                  v-for="button in getSortedButtons(item.buttons)"
                  :key="button.type"
                  :type="button.action === 'confirm' ? 'success' : 'primary'"
                  size="small"
                  :disabled="button.name === '手动确认'"
                  @click.stop="handleOfferButton(item, button)"
                  :style="{
                    backgroundColor: button.fill_color || undefined,
                    borderColor: button.border_color || undefined,
                    color: button.text_color || undefined
                  }"
                >
                  {{ button.name }}
                </el-button>
              </div>
            </div>
          </div>
          <div v-if="buyOrders.length === 0" class="empty-offer-list">
            <el-empty description="暂无待确认报价" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script src="./useOfferProcessing.js"></script>
<style scoped src="./styles.css"></style>
