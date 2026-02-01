<template>
  <div class="offer-list-container">
    <div class="offer-list-layout">
      <!-- 左半部分：我出售的 -->
      <div class="offer-list-section">
        <div class="offer-list-header">
          <h3>我出售的</h3>
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
                <div class="offer-item-name">{{ item.item_name }}</div>
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
            <div class="offer-item-right">
              <div class="offer-countdown">
                <div class="countdown-label">剩余时间</div>
                <div class="countdown-value" :class="{ 'countdown-expired': item.remaining_seconds <= 0 }">
                  {{ formatCountdown(item.remaining_seconds) }}
                </div>
                <div class="countdown-desc">{{ item.end_countdown_desc }}</div>
              </div>
              <div class="offer-buttons">
                <el-button
                  v-for="button in item.buttons"
                  :key="button.type"
                  :type="button.action === 'confirm' ? 'success' : 'primary'"
                  size="small"
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
                <div class="offer-item-name">{{ item.item_name }}</div>
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
            <div class="offer-item-right">
              <div class="offer-countdown">
                <div class="countdown-label">剩余时间</div>
                <div class="countdown-value" :class="{ 'countdown-expired': item.remaining_seconds <= 0 }">
                  {{ formatCountdown(item.remaining_seconds) }}
                </div>
                <div class="countdown-desc">{{ item.end_countdown_desc }}</div>
              </div>
              <div class="offer-buttons">
                <el-button
                  v-for="button in item.buttons"
                  :key="button.type"
                  :type="button.action === 'confirm' ? 'success' : 'primary'"
                  size="small"
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
