<template>
  <div>
    <!-- 筛选器 -->
    <div class="filters card">
      <div class="flex flex-wrap gap-4 items-center">
        <el-select
          v-model="selectedAccount"
          placeholder="选择账号"
          class="account-select"
          @change="handleAccountChange"
          filterable
        >
          <el-option
            v-for="item in accountList"
            :key="item.id"
            :label="`${item.name} - ${item.item_count || 0}件`"
            :value="item.id"
          >
            <span style="float: left">{{ item.name }}</span>
            <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">
              {{ item.item_count || 0 }}件
            </span>
          </el-option>
        </el-select>
        <el-input
          v-model="searchText"
          placeholder="搜索饰品名称..."
          prefix-icon="Search"
          class="search-input"
          @keyup.enter="loadOnSaleData"
          clearable
        />
        <el-select v-model="weaponTypeFilter" placeholder="武器类型" class="type-select" clearable>
          <el-option label="全部" value="" />
          <el-option label="步枪" value="步枪" />
          <el-option label="手枪" value="手枪" />
          <el-option label="狙击枪" value="狙击枪" />
          <el-option label="冲锋枪" value="冲锋枪" />
          <el-option label="霰弹枪" value="霰弹枪" />
          <el-option label="机枪" value="机枪" />
          <el-option label="手套" value="手套" />
          <el-option label="匕首" value="匕首" />
        </el-select>
        <el-select v-model="floatRangeFilter" placeholder="磨损等级" class="wear-select" clearable>
          <el-option label="全部" value="" />
          <el-option label="崭新出厂" value="崭新出厂" />
          <el-option label="略有磨损" value="略有磨损" />
          <el-option label="久经沙场" value="久经沙场" />
          <el-option label="破损不堪" value="破损不堪" />
          <el-option label="战痕累累" value="战痕累累" />
        </el-select>
        <el-button type="primary" @click="loadOnSaleData" :loading="loading">
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button
          v-if="displayMode === 'card'"
          :type="isMultiSelectMode ? 'warning' : 'info'"
          @click="toggleMultiSelectMode"
        >
          {{ isMultiSelectMode ? '取消多选' : '多选' }}
        </el-button>
        <div style="margin-left: auto;" v-if="selectedTradeType !== 'offer'">
          <el-button-group>
            <el-button
              :type="displayMode === 'list' ? 'primary' : ''"
              @click="displayMode = 'list'"
            >
              列表
            </el-button>
            <el-button
              :type="displayMode === 'card' ? 'primary' : ''"
              @click="displayMode = 'card'"
            >
              卡片
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>

    <!-- 交易类型选择栏 -->
    <div class="trade-type-bar card">
      <div class="trade-type-tabs">
        <div
          v-for="type in tradeTypes"
          :key="type.value"
          class="trade-type-tab"
          :class="{ active: selectedTradeType === type.value }"
          @click="handleTradeTypeChange(type.value)"
        >
          <span class="trade-type-icon">{{ type.icon }}</span>
          <span class="trade-type-label">{{ type.label }}</span>
          <span class="trade-type-count" v-if="getTradeTypeCount(type.value) > 0">
            {{ getTradeTypeCount(type.value) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="inventory-stats" v-if="selectedTradeType !== 'offer' && selectedTradeType !== 'lease' && selectedTradeType !== 'sublease' && selectedTradeType !== 'presale'">
      <div class="grid grid-4">
        <div class="card">
          <h3>在售数量</h3>
          <p class="stat-number">{{ onSaleStats.totalCount }}</p>
        </div>
        <div class="card">
          <h3>在售总价值</h3>
          <p class="stat-number">¥{{ onSaleStats.totalPrice }}</p>
        </div>
        <div class="card">
          <h3>平均售价</h3>
          <p class="stat-number">¥{{ onSaleStats.avgPrice }}</p>
        </div>
        <div class="card">
          <h3>预期收益</h3>
          <p class="stat-number" :class="onSaleStats.expectedProfit >= 0 ? 'price-profit' : 'price-loss'">
            {{ onSaleStats.expectedProfit >= 0 ? '+' : '' }}¥{{ onSaleStats.expectedProfit }}
          </p>
        </div>
      </div>
    </div>

    <!-- 报价处理列表显示（特殊布局） -->
    <OfferProcessing
      v-if="selectedTradeType === 'offer'"
      :steam-id="accountList.find(acc => acc.id === selectedAccount)?.steam_id || ''"
      :key="selectedAccount"
    />

    <!-- 已租出列表显示 -->
    <RentedOut
      v-if="selectedTradeType === 'rented_out'"
      :steam-id="accountList.find(acc => acc.id === selectedAccount)?.steam_id || ''"
      :key="selectedAccount"
    />

    <!-- 租赁管理组件 -->
    <LeaseManagement
      v-if="selectedTradeType === 'lease' || selectedTradeType === 'sublease'"
      :loading="loading"
      :display-data="currentDisplayData"
      :display-mode="displayMode"
      :trade-type="selectedTradeType"
      :is-multi-select-mode="isMultiSelectMode"
      :selected-items="selectedItems"
      @update-price="handleUpdatePrice"
      @remove-from-sale="handleRemoveFromSale"
      @batch-change-price="handleBatchChangePrice"
      @batch-remove-from-sale="handleBatchRemoveFromSale"
      @card-click="handleCardClick"
      @preview="openPreview"
      @clear-selection="selectedItems = []"
    />

    <!-- 预售管理组件 -->
    <PresaleManagement
      v-if="selectedTradeType === 'presale'"
      :loading="loading"
      :display-data="currentDisplayData"
      :display-mode="displayMode"
      :is-multi-select-mode="isMultiSelectMode"
      :selected-items="selectedItems"
      @update-price="handleUpdatePrice"
      @remove-from-sale="handleRemoveFromSale"
      @batch-change-price="handleBatchChangePrice"
      @batch-remove-from-sale="handleBatchRemoveFromSale"
      @card-click="handleCardClick"
      @preview="openPreview"
      @clear-selection="selectedItems = []"
    />

    <!-- 出售管理组件（卡片和列表显示） -->
    <SaleManagement
      v-if="selectedTradeType === 'sale' || selectedTradeType === 'transfer' || selectedTradeType === 'instant'"
      :loading="loading"
      :display-data="currentDisplayData"
      :display-mode="displayMode"
      :selected-trade-type="selectedTradeType"
      :is-multi-select-mode="isMultiSelectMode"
      :selected-items="selectedItems"
      @update-price="handleUpdatePrice"
      @remove-from-sale="handleRemoveFromSale"
      @batch-change-price="handleBatchChangePrice"
      @batch-remove-from-sale="handleBatchRemoveFromSale"
      @card-click="handleCardClick"
      @preview="openPreview"
      @clear-selection="selectedItems = []"
    />


    <!-- 改价弹窗 -->
    <el-dialog
      v-model="updatePriceDialogVisible"
      title="修改售价"
      width="500px"
      :close-on-click-modal="false"
      class="update-price-dialog"
    >
      <div v-if="selectedItem" class="update-price-content">
        <div class="item-preview">
          <img
            v-if="getWeaponImage(selectedItem.steam_hash_name)"
            :src="getWeaponImage(selectedItem.steam_hash_name)"
            :alt="selectedItem.item_name"
            class="preview-thumb"
          />
          <div class="item-info">
            <div class="item-name">{{ getCardTitle(selectedItem) }}</div>
            <div class="current-price">当前售价: ¥{{ parseFloat(selectedItem.sale_price).toFixed(2) }}</div>
          </div>
        </div>
        <el-form :model="updatePriceForm" label-width="80px">
          <el-form-item label="新售价">
            <el-input
              v-model="updatePriceForm.newPrice"
              placeholder="请输入新的售价（如：200.11）"
              @input="validatePriceInput"
            >
              <template #prepend>¥</template>
            </el-input>
            <div style="color: #909399; font-size: 12px; margin-top: 4px;">
              请输入正数，最多保留两位小数
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="updatePriceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmUpdatePrice" :loading="updating">确定</el-button>
      </template>
    </el-dialog>

    <!-- 租赁改价弹窗 -->
    <el-dialog
      v-model="rentPriceDialogVisible"
      :title="selectedItem ? `租赁改价 - ${getCardTitle(selectedItem)}` : `批量租赁改价 - 已选择${selectedItems.length}件物品`"
      width="900px"
      :close-on-click-modal="false"
      class="rent-price-dialog"
    >
      <div v-if="(selectedItem || selectedItems.length > 0) && rentInitData" class="rent-price-content">
        <RentFormYYYP
          :items="formattedRentItem"
          :steamId="steamId"
          :initData="rentInitData"
          @submit="confirmRentPriceUpdate"
          @cancel="rentPriceDialogVisible = false"
        />
      </div>
      <div v-else class="loading-placeholder">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载租赁配置中...</span>
      </div>
    </el-dialog>

    <!-- 批量改价弹窗 -->
    <el-dialog
      v-model="batchChangePriceDialogVisible"
      title="批量改价"
      width="600px"
      :close-on-click-modal="false"
      class="batch-change-price-dialog"
    >
      <div class="batch-change-price-content">
        <div class="selected-items-summary">
          <p>已选择 <strong>{{ selectedItems.length }}</strong> 件物品</p>
          <p class="hint-text">交易类型: {{ selectedItems[0]?.trade_type === 'sale' ? '售卖' : (selectedItems[0]?.trade_type === 'lease' ? '租赁' : '转租') }}</p>
        </div>

        <el-form :model="batchChangePriceForm" label-width="120px">
          <el-form-item label="改价方式">
            <el-radio-group v-model="batchChangePriceForm.priceChangeType">
              <el-radio label="fixed">固定价格</el-radio>
              <el-radio label="percent">百分比调整</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 固定价格模式 -->
          <el-form-item
            v-if="batchChangePriceForm.priceChangeType === 'fixed'"
            label="统一价格"
          >
            <el-input
              v-model="batchChangePriceForm.fixedPrice"
              placeholder="请输入新的售价（如：200.11）"
            >
              <template #prepend>¥</template>
            </el-input>
            <div style="color: #909399; font-size: 12px; margin-top: 4px;">
              所有选中物品将被设置为相同价格
            </div>
          </el-form-item>

          <!-- 百分比调整模式 -->
          <template v-if="batchChangePriceForm.priceChangeType === 'percent'">
            <el-form-item label="调整方式">
              <el-radio-group v-model="batchChangePriceForm.percentType">
                <el-radio label="increase">价格增加</el-radio>
                <el-radio label="decrease">价格减少</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="调整百分比">
              <el-input
                v-model="batchChangePriceForm.percentValue"
                placeholder="请输入百分比（如：10）"
              >
                <template #append>%</template>
              </el-input>
              <div style="color: #909399; font-size: 12px; margin-top: 4px;">
                基于当前价格 {{ batchChangePriceForm.percentType === 'increase' ? '增加' : '减少' }} 指定百分比
              </div>
            </el-form-item>
          </template>
        </el-form>

        <!-- 预览价格变化 -->
        <div class="price-preview" v-if="batchChangePriceForm.priceChangeType === 'percent' && batchChangePriceForm.percentValue">
          <el-divider>价格预览</el-divider>
          <div class="preview-list">
            <div v-for="item in selectedItems.slice(0, 3)" :key="item.id" class="preview-item">
              <span class="item-name">{{ getCardTitle(item).substring(0, 20) }}...</span>
              <span class="price-change">
                ¥{{ item.sale_price }} → ¥{{ calculateNewPrice(item.sale_price) }}
              </span>
            </div>
            <div v-if="selectedItems.length > 3" class="more-items">
              还有 {{ selectedItems.length - 3 }} 件物品...
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="batchChangePriceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchChangePrice" :loading="updating">
          确定改价
        </el-button>
      </template>
    </el-dialog>

    <!-- 预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      :title="previewItem ? getCardTitle(previewItem) : ''"
      width="800px"
      :close-on-click-modal="true"
      class="preview-dialog"
    >
      <div v-if="previewItem" class="preview-content">
        <div class="preview-main-layout">
          <div class="preview-left-section">
            <div class="preview-image-section">
              <img
                v-if="getWeaponImage(previewItem.steam_hash_name)"
                :src="getWeaponImage(previewItem.steam_hash_name)"
                :alt="previewItem.item_name"
                class="preview-image"
              />
              <div v-else class="preview-image-placeholder">
                <span>无图片</span>
              </div>
            </div>
            <div class="preview-info-section">
              <div v-if="previewItem.weapon_float" class="preview-float-section">
                <div class="preview-float-bar-container">
                  <div class="float-bar">
                    <div class="float-segment fn"></div>
                    <div class="float-segment mw"></div>
                    <div class="float-segment ft"></div>
                    <div class="float-segment ww"></div>
                    <div class="float-segment bs"></div>
                    <div
                      class="float-pointer"
                      :style="{ left: `${parseFloat(previewItem.weapon_float) * 100}%` }"
                    ></div>
                  </div>
                </div>
                <div class="preview-float-value">{{ previewItem.weapon_float }}</div>
              </div>
              <div class="preview-prices">
                <div class="preview-price-row">
                  <div class="preview-price-item">
                    <span class="preview-price-label">售价:</span>
                    <span class="preview-price-value sale-price">¥{{ parseFloat(previewItem.sale_price).toFixed(2) }}</span>
                  </div>
                  <div class="preview-price-item" v-if="previewItem.buy_price">
                    <span class="preview-price-label">购入:</span>
                    <span class="preview-price-value">¥{{ parseFloat(previewItem.buy_price).toFixed(2) }}</span>
                  </div>
                </div>
                <div class="preview-price-row" v-if="previewItem.buy_price">
                  <div class="preview-price-item">
                    <span class="preview-price-label">预期收益:</span>
                    <span
                      class="preview-price-value"
                      :class="getPriceDiffClass(previewItem.sale_price, previewItem.buy_price)"
                    >
                      {{ (parseFloat(previewItem.sale_price) - parseFloat(previewItem.buy_price)) >= 0 ? '+' : '' }}¥{{ Math.abs(parseFloat(previewItem.sale_price) - parseFloat(previewItem.buy_price)).toFixed(2) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="preview-action-buttons">
                <el-button type="success" @click="handleUpdatePrice(previewItem)">修改售价</el-button>
                <el-button type="primary" @click="handleRemoveFromSale(previewItem)">
                  {{ previewItem.trade_type === 'sublease' ? '取消转租' : '下架商品' }}
                </el-button>
              </div>
            </div>
          </div>
          <div class="preview-right-section">
            <div class="preview-rename" v-if="previewItem.rename">
              <span class="preview-rename-icon">🏷️</span>
              <span class="preview-rename-text">{{ previewItem.rename }}</span>
            </div>
            <div v-if="previewItem.sticker && parseStickers(previewItem.sticker).length > 0" class="preview-sticker-list-section">
              <div class="preview-sticker-list">
                <div
                  v-for="(sticker, index) in parseStickers(previewItem.sticker)"
                  :key="index"
                  class="preview-sticker-list-item"
                >
                  <el-tooltip :content="sticker.name || '未知贴纸'" placement="left">
                    <div class="preview-sticker-list-img-wrapper">
                      <img
                        v-if="sticker.image"
                        :src="sticker.image"
                        :alt="sticker.name"
                        class="preview-sticker-list-img"
                        @error="(e) => e.target.style.display = 'none'"
                      />
                      <div v-else class="preview-sticker-list-placeholder">?</div>
                    </div>
                  </el-tooltip>
                  <div class="preview-sticker-list-name">{{ sticker.name || '未知贴纸' }}</div>
                </div>
              </div>
            </div>
            <div v-if="previewItem.pendant" class="preview-pendant-section">
              <div class="preview-pendant-list">
                <div class="preview-pendant-list-item">
                  <el-tooltip :content="parsePendant(previewItem.pendant)?.name || '挂件'" placement="left">
                    <div class="preview-pendant-list-img-wrapper">
                      <img
                        v-if="parsePendant(previewItem.pendant)?.image"
                        :src="parsePendant(previewItem.pendant).image"
                        :alt="parsePendant(previewItem.pendant).name"
                        class="preview-pendant-list-img"
                        @error="(e) => e.target.style.display = 'none'"
                      />
                      <div v-else class="preview-pendant-list-placeholder">🎗️</div>
                    </div>
                  </el-tooltip>
                  <div class="preview-pendant-list-name">{{ parsePendant(previewItem.pendant)?.name || '挂件' }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script src="./useOnSaleYYYP.js"></script>
<style scoped src="./styles.css"></style>