<template>
  <!-- 悠悠有品商品列表 -->
  <div v-if="showYYYPList" class="card yyyp-commodity-list">
    <!-- 折叠/展开控制头部 -->
    <div class="yyyp-collapse-header" @click.stop="toggleYYYPList">
      <div class="yyyp-collapse-left">
        <el-icon class="collapse-icon">
          <CaretRight v-if="!showYYYPTable" />
          <CaretBottom v-if="showYYYPTable" />
        </el-icon>
        <span class="yyyp-collapse-title">悠悠有品</span>

        <!-- 筛选按钮组 - 移到左侧 -->
        <div class="yyyp-filter-buttons">
          <button
            class="filter-btn"
            :class="{ active: yyypFilterType === 'on_sale' }"
            @click.stop="handleFilterChange('on_sale')"
          >
            在售
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn"
            :class="{ active: yyypFilterType === 'on_lease' }"
            @click.stop="handleFilterChange('on_lease')"
          >
            在租
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn"
            :class="{ active: yyypFilterType === 'presale' }"
            @click.stop="handleFilterChange('presale')"
          >
            预售
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn"
            :class="{ active: yyypFilterType === 'wanted' }"
            @click.stop="handleFilterChange('wanted')"
          >
            求购
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn"
            :class="{ active: yyypFilterType === 'sold' }"
            @click.stop="handleFilterChange('sold')"
          >
            成交
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn"
            @click.stop="handleOpenPriceTrend"
          >
            价格走势
          </button>
          <span class="filter-divider">|</span>
          <button
            class="filter-btn filter-advanced"
            @click.stop="handleAdvancedFilter"
          >
            筛选
          </button>

          <!-- 排序选择器 - 仅在在售模块下显示 -->
          <el-select
            v-if="yyypFilterType === 'on_sale'"
            v-model="sortType"
            size="small"
            placeholder="排序方式"
            @click.stop
            @change="handleSortChange"
            style="width: 120px; margin-left: 16px"
          >
            <el-option label="默认" value="default" />
            <el-option label="热度" value="popularity" />
            <el-option label="最新" value="newest" />
            <el-option label="价格 ↑" value="price_asc" />
            <el-option label="价格 ↓" value="price_desc" />
            <el-option label="磨损 ↑" value="wear_asc" />
            <el-option label="磨损 ↓" value="wear_desc" />
          </el-select>

          <!-- 磨损区间选择器 - 仅在在售模块且有磨损区间时显示 -->
          <el-select
            v-if="yyypFilterType === 'on_sale' && wearRangeOptions.length > 0"
            v-model="wearRange"
            size="small"
            placeholder="磨损区间"
            @click.stop
            @change="handleWearRangeChange"
            style="width: 140px; margin-left: 8px"
            clearable
          >
            <el-option label="全部磨损" value="" />
            <el-option
              v-for="option in wearRangeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </div>
      </div>
      <div class="yyyp-weapon-info">
        <span class="weapon-name">{{ yyypCurrentWeapon?.market_listing_item_name }}</span>
        <span class="total-count">总数: {{ yyypTotalCount }} 件</span>

        <!-- 价格追踪按钮 - 移到右侧 -->
        <el-button
          type="primary"
          size="small"
          :icon="Refresh"
          @click.stop="handleRefreshYYYP"
          :loading="isSearching && searchSource === 'yyyp'"
        >
          刷新列表
        </el-button>
        <el-button
          :type="isMultiSelectMode ? 'warning' : 'info'"
          size="small"
          @click.stop="toggleMultiSelectMode"
        >
          {{ isMultiSelectMode ? '取消多选' : '多选' }}
        </el-button>
        <el-button
          v-if="isMultiSelectMode"
          type="info"
          size="small"
          @click.stop="selectAllCommodities('yyyp')"
        >
          全选
        </el-button>
      </div>
    </div>

    <!-- 悠悠有品卡片模式 -->
    <div
      v-show="showYYYPTable"
      class="commodity-card-grid yyyp-scroll-container"
      v-loading="isSearching && searchSource === 'yyyp'"
      element-loading-text="加载中..."
      element-loading-background="rgba(0, 0, 0, 0.8)"
      @scroll="handleYYYPScroll"
    >
      <div
        v-for="(item, index) in yyypCommodities"
        :key="index"
        class="commodity-card"
        :class="{
          'selected': isCommoditySelected(item),
          'multi-select-mode': isMultiSelectMode
        }"
        @click="handleCommodityCardClick(item, 'yyyp', $event)"
      >
        <!-- 选中标记 -->
        <div v-if="isMultiSelectMode && isCommoditySelected(item)" class="selected-check">
          <el-icon><Check /></el-icon>
        </div>
        <div class="commodity-card-image">
          <img :src="item.iconUrl" class="commodity-icon" @error="handleImageError" />
          <!-- 印花覆盖层 - 左下角 -->
          <div v-if="item.stickers && item.stickers.length > 0" class="sticker-overlay">
            <div
              v-for="(sticker, sIdx) in item.stickers"
              :key="sIdx"
              class="sticker-item-overlay"
              :title="sticker.Name || '印花'"
            >
              <img
                v-if="sticker.TemplateHashName"
                :src="getWeaponImage(sticker.TemplateHashName)"
                :alt="sticker.Name"
                class="sticker-img-overlay"
                @error="(e) => e.target.style.display = 'none'"
              />
              <img
                v-else-if="sticker.ImgUrl"
                :src="sticker.ImgUrl"
                :alt="sticker.Name"
                class="sticker-img-overlay"
                @error="(e) => e.target.style.display = 'none'"
              />
              <div v-else class="sticker-placeholder-overlay">?</div>
            </div>
          </div>
          <!-- 挂件覆盖层 - 右上角 -->
          <div v-if="item.pendants && item.pendants.length > 0" class="pendant-overlay">
            <div
              v-for="(pendant, pIdx) in item.pendants"
              :key="pIdx"
              class="pendant-item-overlay"
              :title="pendant.pendantSourceName || pendant.name || '挂件'"
            >
              <img
                v-if="pendant.steamHashName"
                :src="getWeaponImage(pendant.steamHashName)"
                :alt="pendant.name"
                class="pendant-img-overlay"
                @error="(e) => e.target.style.display = 'none'"
              />
              <img
                v-else-if="pendant.imgUrl"
                :src="pendant.imgUrl"
                :alt="pendant.name"
                class="pendant-img-overlay"
                @error="(e) => e.target.style.display = 'none'"
              />
              <div v-else class="pendant-placeholder-overlay">🎗️</div>
            </div>
          </div>
        </div>
        <div class="commodity-card-content">
          <!-- 磨损进度条 - 顶部 -->
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
            <div class="float-value">{{ item.abrade }}</div>
          </div>
          <!-- 商品详情信息 -->
          <div class="commodity-card-info">
            <!-- 价格/租金显示 -->
            <div class="info-item" v-if="!item.isLeaseItem && !item.isPurchaseOrder">
              <span class="info-label">价格:</span>
              <span class="info-value price-highlight">¥{{ item.price }}</span>
            </div>
            <!-- 求购信息显示 -->
            <div class="info-item" v-if="item.isPurchaseOrder && item.purchasePrice">
              <span class="info-label">求购价:</span>
              <span class="info-value price-highlight">¥{{ item.purchasePrice }}</span>
            </div>
            <div class="info-item" v-if="item.isPurchaseOrder && item.surplusQuantity">
              <span class="info-label">求购数量:</span>
              <span class="info-value price-highlight">{{ item.surplusQuantity }}</span>
            </div>
            <!-- 租赁信息显示 -->
            <div class="info-item" v-if="item.isLeaseItem && item.leaseUnitPrice">
              <span class="info-label">租金:</span>
              <span class="info-value price-highlight">¥{{ item.leaseUnitPrice }}/天</span>
            </div>
            <div class="info-item" v-if="item.isLeaseItem && item.leaseDeposit">
              <span class="info-label">押金:</span>
              <span class="info-value">¥{{ item.leaseDeposit }}</span>
            </div>
            <div class="info-item" v-if="item.isLeaseItem && item.leaseDayDesc">
              <span class="info-label">租期:</span>
              <span class="info-value">{{ item.leaseDayDesc }}</span>
            </div>
            <!-- 模板信息 -->
            <div class="info-item" v-if="item.paintSeed">
              <span class="info-label">模板:</span>
              <span class="info-value">{{ item.paintSeed }}</span>
            </div>
            <div class="info-item" v-if="item.haveNameTag === 1">
              <span class="info-label">改名:</span>
              <div v-if="item.nameTagText" class="info-value nametag-text" :title="item.nameTagText">
                {{ item.nameTagText }}
              </div>
              <span
                v-else
                @click.stop="fetchSingleNameTag(item)"
                class="info-value nametag-parse"
                :style="{ opacity: item.nameTagLoading ? 0.5 : 1 }"
                :title="item.nameTagLoading ? '加载中...' : '点击解析改名'"
              >
                🏷️ 解析名称
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ item.isPurchaseOrder ? '买家:' : '卖家:' }}</span>
              <span class="info-value">{{ item.userName || item.userNickName || '-' }}</span>
            </div>
          </div>
          <!-- 印花/挂件价值 -->
          <div class="sticker-value-info" v-if="(item.stickers && item.stickers.length > 0) || (item.pendants && item.pendants.length > 0)">
            <div class="sticker-value-item" v-if="item.stickerTotalValue !== undefined">
              <span class="sticker-value-label">印花价值:</span>
              <span class="sticker-value-amount">¥{{ item.stickerTotalValue || '0.00' }}</span>
            </div>
            <div class="sticker-value-item" v-if="item.pendantTotalValue !== undefined">
              <span class="sticker-value-label">挂件价值:</span>
              <span class="sticker-value-amount">¥{{ item.pendantTotalValue || '0.00' }}</span>
            </div>
            <div class="sticker-value-loading" v-if="item.priceLoading">
              <span>价格查询中...</span>
            </div>
          </div>
          <!-- 购买/租用/供应按钮 -->
          <el-button
            v-if="!isMultiSelectMode"
            :type="getButtonType(item)"
            size="small"
            class="card-buy-button"
            :disabled="item.isLeaseItem || yyypFilterType === 'on_lease'"
            @click.stop="handleBuyCommodityWithPresale(item)"
          >
            {{ getButtonText(item) }}
          </el-button>
        </div>
      </div>
      <!-- 加载更多提示 -->
      <div class="load-more-indicator" v-if="yyypCommodities.length > 0">
        <div v-if="yyypLoadingMore" class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        <div v-else-if="!yyypHasMore" class="no-more-data">
          <span>没有更多数据了</span>
        </div>
        <div v-else class="scroll-hint">
          <span>下拉加载更多</span>
        </div>
      </div>
    </div>

    <!-- 价格走势对话框 -->
    <el-dialog
      v-model="priceTrendDialogVisible"
      :title="`价格走势 - ${yyypCurrentWeapon?.market_listing_item_name || ''}`"
      width="800px"
      :close-on-click-modal="false"
      class="yyyp-price-trend-dialog"
    >
      <!-- 天数选择器 -->
      <div class="price-trend-header">
        <el-radio-group v-model="selectedDays" size="small" @change="loadPriceTrend">
          <el-radio-button :label="7">7天</el-radio-button>
          <el-radio-button :label="30">30天</el-radio-button>
          <el-radio-button :label="90">90天</el-radio-button>
          <el-radio-button :label="180">180天</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 图表容器 -->
      <div
        v-loading="priceTrendLoading"
        element-loading-text="加载中..."
        class="price-trend-chart-container"
      >
        <div ref="priceTrendChart" class="price-trend-chart"></div>
      </div>

      <!-- 统计信息 -->
      <div v-if="priceTrendData" class="price-trend-stats">
        <el-descriptions :column="4" border size="small">
          <el-descriptions-item label="最高价">¥{{ priceStats.maxPrice }}</el-descriptions-item>
          <el-descriptions-item label="最低价">¥{{ priceStats.minPrice }}</el-descriptions-item>
          <el-descriptions-item label="平均价">¥{{ priceStats.avgPrice }}</el-descriptions-item>
          <el-descriptions-item label="数据点数">{{ priceStats.count }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="priceTrendDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 高级筛选对话框 -->
    <el-dialog
      v-model="filterDialogVisible"
      title="筛选"
      width="400px"
      :close-on-click-modal="false"
      class="yyyp-filter-dialog"
    >
      <el-form :model="filterForm" label-position="left" label-width="100px">
        <!-- 图案模板 -->
        <el-form-item label="图案模板">
          <el-input
            v-model="filterForm.templateId"
            placeholder="请输入模板编号0-1000"
            clearable
          />
        </el-form-item>

        <!-- 磨损区间 -->
        <el-form-item label="磨损区间">
          <div class="wear-range-inputs">
            <el-input
              v-model="filterForm.wearMin"
              placeholder="最小值"
              style="width: 48%"
            />
            <span style="margin: 0 2%">-</span>
            <el-input
              v-model="filterForm.wearMax"
              placeholder="最大值"
              style="width: 48%"
            />
          </div>
        </el-form-item>

        <!-- 名称标签 -->
        <el-form-item label="名称标签">
          <el-select
            v-model="filterForm.hasNameTag"
            placeholder="请选择"
            clearable
            style="width: 100%"
          >
            <el-option label="全部" :value="null" />
            <el-option label="有名称标签" :value="true" />
            <el-option label="无名称标签" :value="false" />
          </el-select>
        </el-form-item>

        <!-- 名称标签二级菜单 -->
        <el-form-item label="" v-if="filterForm.hasNameTag === true">
          <el-input
            v-model="filterForm.nameTagText"
            placeholder="输入名称标签内容"
            clearable
          />
        </el-form-item>

        <!-- 印花搜枪 -->
        <el-form-item label="印花搜枪">
          <el-select
            v-model="filterForm.hasStickerFilter"
            placeholder="请选择"
            clearable
            style="width: 100%"
          >
            <el-option label="全部" :value="null" />
            <el-option label="有印花" :value="true" />
            <el-option label="无印花" :value="false" />
          </el-select>
        </el-form-item>

        <!-- 印花搜枪二级菜单 -->
        <el-form-item label="" v-if="filterForm.hasStickerFilter === true">
          <el-input
            v-model="filterForm.stickerName"
            placeholder="输入印花名称"
            clearable
          />
        </el-form-item>

        <!-- 挂件 -->
        <el-form-item label="挂件">
          <el-select
            v-model="filterForm.hasPendant"
            placeholder="请选择"
            clearable
            style="width: 100%"
          >
            <el-option label="全部" :value="null" />
            <el-option label="有挂件" :value="true" />
            <el-option label="无挂件" :value="false" />
          </el-select>
        </el-form-item>

        <!-- 挂件二级菜单 -->
        <el-form-item label="" v-if="filterForm.hasPendant === true">
          <el-input
            v-model="filterForm.pendantName"
            placeholder="输入挂件名称"
            clearable
          />
        </el-form-item>

        <!-- 极速发货 -->
        <el-form-item label="极速发货">
          <el-switch v-model="filterForm.fastDelivery" />
        </el-form-item>

        <!-- 出售价格 -->
        <el-form-item label="出售价格">
          <div class="price-range-inputs">
            <el-input
              v-model="filterForm.priceMin"
              placeholder="最低价格"
              style="width: 48%"
            />
            <span style="margin: 0 2%">-</span>
            <el-input
              v-model="filterForm.priceMax"
              placeholder="最高价格"
              style="width: 48%"
            />
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleResetFilter">重置</el-button>
          <el-button type="primary" @click="handleApplyFilter">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 预售购买对话框 -->
    <el-dialog
      v-model="presaleBuyDialogVisible"
      title="购买预售商品"
      width="600px"
      :close-on-click-modal="false"
      class="yyyp-presale-buy-dialog"
    >
      <div v-loading="presaleDetailLoading" class="presale-buy-content">
        <div v-if="presaleDetail && presaleDetail.commodity" class="presale-detail">
          <!-- 商品信息 -->
          <div class="commodity-info-section">
            <div class="commodity-image-large">
              <img
                v-if="presaleDetail.commodity.templateInfo?.iconUrlLarge"
                :src="presaleDetail.commodity.templateInfo.iconUrlLarge"
                :alt="presaleDetail.commodity.commodityName"
                style="max-width: 100%; max-height: 200px;"
              />
            </div>
            <div class="commodity-info-details">
              <h3>{{ presaleDetail.commodity.commodityName }}</h3>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="价格">
                  <span style="color: #f56c6c; font-size: 18px; font-weight: bold;">
                    {{ presaleDetail.commodity.sellPrice }}
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="定金" v-if="presaleDetail.commodity.commodityPreSaleDTO">
                  <span style="color: #e6a23c; font-size: 16px; font-weight: bold;">
                    ¥{{ presaleDetail.commodity.commodityPreSaleDTO.depositAmount }}
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="品质">
                  <span :style="{ color: '#' + presaleDetail.commodity.templateInfo?.qualityColor }">
                    {{ presaleDetail.commodity.templateInfo?.qualityName }}
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="稀有度">
                  <span :style="{ color: '#' + presaleDetail.commodity.templateInfo?.rarityColor }">
                    {{ presaleDetail.commodity.templateInfo?.rarityName }}
                  </span>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>

          <!-- 预售信息 -->
          <div v-if="presaleDetail.commodity.commodityPreSaleDTO" class="presale-info-section">
            <el-alert
              title="预售说明"
              type="warning"
              :closable="false"
              style="margin-bottom: 15px;"
            >
              <div style="line-height: 1.8; white-space: pre-wrap;">{{ presaleDetail.preSaleBuyDesc || '1. 等待冷却结束期间取消订单会产生违约费用\n2. 预售交易模式采用买家自动接收报价\n3. 冷却结束后由卖家发起报价，买家接收报价\n4. 冷却结束后进入收发货流程，将无法取消订单' }}</div>
            </el-alert>

            <el-descriptions :column="2" border>
              <el-descriptions-item label="未发货赔付">
                <span style="color: #67c23a; font-weight: bold;">
                  ¥{{ presaleDetail.commodity.commodityPreSaleDTO.buyerCompensationAmount }}
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="不收货惩罚">
                <span style="color: #f56c6c; font-weight: bold;">
                  ¥{{ presaleDetail.commodity.commodityPreSaleDTO.buyerLiquidatedDamagesAmount }}
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="冷却结束时间">
                {{ formatTimestamp(presaleDetail.commodity.commodityPreSaleDTO.preSaleEndTime) }}
              </el-descriptions-item>
              <el-descriptions-item label="发送报价截止时间" :span="2">
                {{ formatTimestamp(presaleDetail.commodity.commodityPreSaleDTO.sendOfferEndTime) }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 支付方式 -->
          <div class="payment-section">
            <div class="payment-info" v-if="filteredPayList.length > 0">
              <span style="font-size: 16px; font-weight: 600; margin-right: 20px;">支付方式</span>
              <img
                :src="filteredPayList[0].channelLogo"
                :alt="filteredPayList[0].channelName"
                style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"
              />
              <span style="font-size: 14px;">{{ filteredPayList[0].channelName }}</span>
              <span v-if="filteredPayList[0].balance" style="color: #67c23a; margin-left: 10px; font-weight: bold;">
                ¥{{ filteredPayList[0].balance }}
              </span>
            </div>
          </div>

          <!-- 购买选项 -->
          <div class="buy-options-section">
            <el-checkbox v-model="presaleBuyForm.autoConfirmPayment">
              自动确认支付
            </el-checkbox>
            <el-checkbox v-model="presaleBuyForm.pollPayment">
              轮询支付状态
            </el-checkbox>
          </div>
        </div>

        <div v-else-if="!presaleDetailLoading" class="no-detail-section">
          <el-empty description="无法加载预售详情" />
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="presaleBuyDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="buyingPresale"
            :disabled="!presaleDetail || presaleDetailLoading || !isPresaleBalanceSufficient"
            @click="confirmPresaleBuy"
          >
            {{ isPresaleBalanceSufficient ? '确认购买' : '余额不足' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 在售购买对话框 -->
    <el-dialog
      v-model="onSaleBuyDialogVisible"
      title="购买商品"
      width="600px"
      :close-on-click-modal="false"
      class="yyyp-onsale-buy-dialog"
    >
      <div v-loading="onSaleDetailLoading" class="onsale-buy-content">
        <div v-if="onSaleDetail && onSaleDetail.commodity" class="onsale-detail">
          <!-- 商品信息 -->
          <div class="commodity-info-section">
            <div class="commodity-image-large">
              <img
                v-if="onSaleDetail.commodity.templateInfo?.iconUrlLarge"
                :src="onSaleDetail.commodity.templateInfo.iconUrlLarge"
                :alt="onSaleDetail.commodity.commodityName"
                style="max-width: 100%; max-height: 200px;"
              />
            </div>
            <div class="commodity-info-details">
              <h3>{{ onSaleDetail.commodity.commodityName }}</h3>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="价格">
                  <span style="color: #f56c6c; font-size: 18px; font-weight: bold;">
                    {{ onSaleDetail.commodity.sellPrice }}
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="品质">
                  <span :style="{ color: '#' + onSaleDetail.commodity.templateInfo?.qualityColor }">
                    {{ onSaleDetail.commodity.templateInfo?.qualityName }}
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="稀有度">
                  <span :style="{ color: '#' + onSaleDetail.commodity.templateInfo?.rarityColor }">
                    {{ onSaleDetail.commodity.templateInfo?.rarityName }}
                  </span>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>

          <!-- 支付方式 -->
          <div class="payment-section">
            <div class="payment-info" v-if="filteredOnSalePayList.length > 0">
              <span style="font-size: 16px; font-weight: 600; margin-right: 20px;">支付方式</span>
              <img
                :src="filteredOnSalePayList[0].channelLogo"
                :alt="filteredOnSalePayList[0].channelName"
                style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"
              />
              <span style="font-size: 14px;">{{ filteredOnSalePayList[0].channelName }}</span>
              <span v-if="filteredOnSalePayList[0].balance" style="color: #67c23a; margin-left: 10px; font-weight: bold;">
                ¥{{ filteredOnSalePayList[0].balance }}
              </span>
            </div>
          </div>

          <!-- 购买选项 -->
          <div class="buy-options-section">
            <el-checkbox v-model="onSaleBuyForm.autoConfirmPayment">
              自动确认支付
            </el-checkbox>
            <el-checkbox v-model="onSaleBuyForm.pollPayment">
              轮询支付状态
            </el-checkbox>
          </div>
        </div>

        <div v-else-if="!onSaleDetailLoading" class="no-detail-section">
          <el-empty description="无法加载商品详情" />
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="onSaleBuyDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="buyingOnSale"
            :disabled="!onSaleDetail || onSaleDetailLoading || !isOnSaleBalanceSufficient"
            @click="confirmOnSaleBuy"
          >
            {{ isOnSaleBalanceSufficient ? '确认购买' : '余额不足' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { CaretRight, CaretBottom, Check, Loading, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'
import { API_CONFIG } from '@/config/api.js'

// 接收父组件传递的 props
const props = defineProps({
  showYYYPList: Boolean,
  showYYYPTable: Boolean,
  isSearching: Boolean,
  searchSource: String,
  isMultiSelectMode: Boolean,
  yyypCurrentWeapon: Object,
  yyypCommodities: Array,
  yyypTotalCount: Number,
  yyypLoadingMore: Boolean,
  yyypHasMore: Boolean,
  yyypFilterType: String  // 当前筛选类型
})

// 定义事件
const emit = defineEmits([
  'toggle-yyyp-list',
  'refresh-yyyp',
  'toggle-multi-select',
  'select-all',
  'commodity-click',
  'yyyp-scroll',
  'buy-commodity',
  'fetch-single-nametag',
  'filter-change',
  'advanced-filter',
  'sort-change',
  'wear-range-change'
])

// activeFilter 已移除，使用 props.yyypFilterType

// 排序和磨损区间状态
const sortType = ref('default')
const wearRange = ref('')

// 判断当前武器品质并返回对应的磨损区间选项
const wearRangeOptions = computed(() => {
  if (!props.yyypCurrentWeapon?.market_listing_item_name) return []

  const name = props.yyypCurrentWeapon.market_listing_item_name

  // 崭新出厂 (Factory New: 0.00 - 0.07)
  if (name.includes('崭新出厂') || name.includes('Factory New')) {
    return [
      { label: '0.00 - 0.01', value: '0.00-0.01' },
      { label: '0.01 - 0.02', value: '0.01-0.02' },
      { label: '0.02 - 0.03', value: '0.02-0.03' },
      { label: '0.03 - 0.04', value: '0.03-0.04' },
      { label: '0.04 - 0.07', value: '0.04-0.07' }
    ]
  }

  // 略有磨损 (Minimal Wear: 0.07 - 0.15)
  if (name.includes('略有磨损') || name.includes('Minimal Wear')) {
    return [
      { label: '0.07 - 0.08', value: '0.07-0.08' },
      { label: '0.08 - 0.09', value: '0.08-0.09' },
      { label: '0.09 - 0.10', value: '0.09-0.10' },
      { label: '0.10 - 0.11', value: '0.10-0.11' },
      { label: '0.11 - 0.15', value: '0.11-0.15' }
    ]
  }

  // 久经沙场 (Field-Tested: 0.15 - 0.38)
  if (name.includes('久经沙场') || name.includes('Field-Tested')) {
    return [
      { label: '0.15 - 0.18', value: '0.15-0.18' },
      { label: '0.18 - 0.21', value: '0.18-0.21' },
      { label: '0.21 - 0.24', value: '0.21-0.24' },
      { label: '0.24 - 0.27', value: '0.24-0.27' },
      { label: '0.27 - 0.38', value: '0.27-0.38' }
    ]
  }

  // 破损不堪 (Well-Worn: 0.38 - 0.45)
  if (name.includes('破损不堪') || name.includes('Well-Worn')) {
    return [
      { label: '0.38 - 0.39', value: '0.38-0.39' },
      { label: '0.39 - 0.40', value: '0.39-0.40' },
      { label: '0.40 - 0.41', value: '0.40-0.41' },
      { label: '0.41 - 0.42', value: '0.41-0.42' },
      { label: '0.42 - 0.45', value: '0.42-0.45' }
    ]
  }

  // 战痕累累 (Battle-Scarred: 0.45 - 1.00)
  if (name.includes('战痕累累') || name.includes('Battle-Scarred')) {
    return [
      { label: '全部', value: '' },
      { label: '0.45 - 0.50', value: '0.45-0.50' },
      { label: '0.50 - 0.63', value: '0.50-0.63' },
      { label: '0.63 - 0.76', value: '0.63-0.76' },
      { label: '0.76 - 0.90', value: '0.76-0.90' },
      { label: '0.90 - 1.00', value: '0.90-1.00' }
    ]
  }

  // 其他品质暂不支持磨损区间筛选
  return []
})

// 排序变更处理
const handleSortChange = (value) => {
  console.log('排序变更:', value)
  emit('sort-change', value)
}

// 磨损区间变更处理
const handleWearRangeChange = (value) => {
  console.log('磨损区间变更:', value)
  emit('wear-range-change', value)
}

// 筛选对话框状态
const filterDialogVisible = ref(false)

// 筛选表单数据
const filterForm = ref({
  templateId: '',           // 图案模板编号
  wearMin: '',              // 磨损最小值
  wearMax: '',              // 磨损最大值
  hasNameTag: null,         // 是否有名称标签 (null=全部, true=有, false=无)
  nameTagText: '',          // 名称标签内容（二级）
  hasStickerFilter: null,   // 是否有印花 (null=全部, true=有, false=无)
  stickerName: '',          // 印花名称（二级）
  hasPendant: null,         // 是否有挂件 (null=全部, true=有, false=无)
  pendantName: '',          // 挂件名称（二级）
  fastDelivery: false,      // 极速发货
  priceMin: '',             // 最低价格
  priceMax: ''              // 最高价格
})

// 价格走势对话框状态
const priceTrendDialogVisible = ref(false)
const selectedDays = ref(30)
const priceTrendData = ref(null)
const priceTrendLoading = ref(false)
const priceTrendChart = ref(null)
let chartInstance = null

// 价格统计计算
const priceStats = computed(() => {
  if (!priceTrendData.value || !priceTrendData.value.tradeDataList || priceTrendData.value.tradeDataList.length === 0) {
    return { maxPrice: '0.00', minPrice: '0.00', avgPrice: '0.00', count: 0 }
  }

  const prices = priceTrendData.value.tradeDataList.map(item => parseFloat(item.price))
  return {
    maxPrice: Math.max(...prices).toFixed(2),
    minPrice: Math.min(...prices).toFixed(2),
    avgPrice: (prices.reduce((a, b) => a + b, 0) / prices.length).toFixed(2),
    count: prices.length
  }
})

// 打开价格走势对话框
const handleOpenPriceTrend = () => {
  if (!props.yyypCurrentWeapon) {
    ElMessage.warning('请先选择武器')
    return
  }
  priceTrendDialogVisible.value = true
  selectedDays.value = 30
  loadPriceTrend()
}

// 加载价格走势数据
const loadPriceTrend = async () => {
  if (!props.yyypCurrentWeapon || !props.yyypCurrentWeapon.yyyp_id) {
    ElMessage.error('缺少武器ID信息')
    return
  }

  priceTrendLoading.value = true

  try {
    const url = `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getPriceTrend`
    const response = await axios.post(url, {
      yyypId: props.yyypCurrentWeapon.yyyp_id,
      day: selectedDays.value
    })

    if (response.data.success) {
      priceTrendData.value = response.data.data
      await nextTick()
      initPriceTrendChart()
    } else {
      ElMessage.error(response.data.message || '获取价格走势失败')
    }
  } catch (error) {
    console.error('加载价格走势失败:', error)
    ElMessage.error('加载价格走势失败: ' + (error.message || '未知错误'))
  } finally {
    priceTrendLoading.value = false
  }
}

// 初始化价格走势图表
const initPriceTrendChart = () => {
  if (!priceTrendChart.value || !priceTrendData.value || !priceTrendData.value.tradeDataList) {
    return
  }

  // 销毁已存在的图表实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建新图表实例
  chartInstance = echarts.init(priceTrendChart.value)

  // 准备数据
  const tradeDataList = priceTrendData.value.tradeDataList
  const dates = tradeDataList.map(item => {
    // 使用 time 字段（毫秒时间戳）显示具体日期和时间
    const date = new Date(item.time)
    const month = date.getMonth() + 1
    const day = date.getDate()
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `${month}/${day} ${hours}:${minutes}`
  })
  const prices = tradeDataList.map(item => parseFloat(item.price))

  // 计算价格范围，用于聚焦显示
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  const priceRange = maxPrice - minPrice
  const padding = priceRange * 0.1 // 上下留10%的空间
  const yAxisMin = Math.max(0, minPrice - padding)
  const yAxisMax = maxPrice + padding

  // 图表配置
  const option = {
    title: {
      text: '价格走势',
      left: 'center',
      textStyle: {
        color: '#e0e0e0',
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(50, 50, 50, 0.95)',
      borderColor: '#555',
      textStyle: {
        color: '#e0e0e0'
      },
      formatter: (params) => {
        const param = params[0]
        return `${param.name}<br/>价格: ¥${param.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',  // 增加底部空间，容纳旋转的时间标签
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#555'
        }
      },
      axisLabel: {
        color: '#999',
        rotate: 45,  // 旋转45度避免重叠
        interval: 'auto'  // 自动计算显示间隔
      }
    },
    yAxis: {
      type: 'value',
      name: '价格 (¥)',
      min: yAxisMin,
      max: yAxisMax,
      nameTextStyle: {
        color: '#999'
      },
      axisLine: {
        lineStyle: {
          color: '#555'
        }
      },
      axisLabel: {
        color: '#999',
        formatter: '¥{value}'
      },
      splitLine: {
        lineStyle: {
          color: '#333'
        }
      }
    },
    series: [
      {
        name: '价格',
        type: 'line',
        data: prices,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#409eff'
        },
        itemStyle: {
          color: '#409eff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(64, 158, 255, 0.3)'
              },
              {
                offset: 1,
                color: 'rgba(64, 158, 255, 0.05)'
              }
            ]
          }
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 方法转发给父组件
const toggleYYYPList = () => emit('toggle-yyyp-list')
const handleRefreshYYYP = () => emit('refresh-yyyp')
const toggleMultiSelectMode = () => emit('toggle-multi-select')
const selectAllCommodities = (type) => emit('select-all', type)
const handleCommodityCardClick = (item, type, event) => emit('commodity-click', { item, type, event })
const handleYYYPScroll = (event) => emit('yyyp-scroll', event)
const handleBuyCommodity = (item) => emit('buy-commodity', item)
const fetchSingleNameTag = (item) => emit('fetch-single-nametag', item)
const handleImageError = (e) => {
  // 图片加载失败处理
  e.target.style.display = 'none'
}

// 获取按钮文字
const getButtonText = (item) => {
  if (item.isPurchaseOrder) {
    return '供应'
  } else if (item.isLeaseItem) {
    return '租用'
  } else {
    return '购买'
  }
}

// 获取按钮类型
const getButtonType = (item) => {
  if (item.isPurchaseOrder) {
    return 'primary'  // 蓝色 - 供应
  } else if (item.isLeaseItem) {
    return 'primary'  // 蓝色 - 租用
  } else {
    return 'success'  // 绿色 - 购买
  }
}

// 筛选相关方法
const handleFilterChange = (filterType) => {
  // 直接触发事件，由父组件管理状态
  emit('filter-change', filterType)
}

const handleAdvancedFilter = () => {
  filterDialogVisible.value = true
}

// 重置筛选表单
const handleResetFilter = () => {
  filterForm.value = {
    templateId: '',
    wearMin: '',
    wearMax: '',
    hasNameTag: null,
    nameTagText: '',
    hasStickerFilter: null,
    stickerName: '',
    hasPendant: null,
    pendantName: '',
    fastDelivery: false,
    priceMin: '',
    priceMax: ''
  }
}

// 应用筛选
const handleApplyFilter = () => {
  console.log('应用筛选:', filterForm.value)
  emit('advanced-filter', filterForm.value)
  filterDialogVisible.value = false
}

// 从父组件注入的方法
import { inject } from 'vue'
const isCommoditySelected = inject('isCommoditySelected', () => false)
const getWeaponImage = inject('getWeaponImage', (hashName) => {
  if (!hashName) return ''
  return `/weapon_imgs/${encodeURIComponent(hashName)}.png`
})

// ========== 预售购买相关 ==========
import { apiUrls } from '@/config/api.js'
import { ElMessageBox } from 'element-plus'

// 预售购买对话框状态
const presaleBuyDialogVisible = ref(false)
const presaleDetail = ref(null)
const presaleDetailLoading = ref(false)
const buyingPresale = ref(false)
const currentPresaleItem = ref(null)

// 预售购买表单
const presaleBuyForm = ref({
  autoConfirmPayment: true,
  pollPayment: true,
  paymentChannel: 'balance'
})

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 过滤支付方式列表，只显示有品余额
const filteredPayList = computed(() => {
  if (!presaleDetail.value?.payList) return []
  // 只返回 channelId === 100 的有品余额支付方式
  return presaleDetail.value.payList.filter(pay => pay.channelId === 100)
})

// 判断预售商品余额是否充足
const isPresaleBalanceSufficient = computed(() => {
  if (!presaleDetail.value?.commodity) return false
  if (filteredPayList.value.length === 0) return false

  const balance = filteredPayList.value[0].balance || 0
  const depositAmount = presaleDetail.value.commodity.commodityPreSaleDTO?.depositAmount || 0

  return balance >= depositAmount
})

// ========== 在售购买相关 ==========
// 在售购买对话框状态
const onSaleBuyDialogVisible = ref(false)
const onSaleDetail = ref(null)
const onSaleDetailLoading = ref(false)
const buyingOnSale = ref(false)
const currentOnSaleItem = ref(null)

// 在售购买表单
const onSaleBuyForm = ref({
  autoConfirmPayment: true,
  pollPayment: true,
  paymentChannel: 'balance'
})

// 过滤在售商品的支付方式列表，只显示有品余额
const filteredOnSalePayList = computed(() => {
  if (!onSaleDetail.value?.payList) return []
  return onSaleDetail.value.payList.filter(pay => pay.channelId === 100)
})

// 判断在售商品余额是否充足
const isOnSaleBalanceSufficient = computed(() => {
  if (!onSaleDetail.value?.commodity) return false
  if (filteredOnSalePayList.value.length === 0) return false

  const balance = filteredOnSalePayList.value[0].balance || 0
  const price = onSaleDetail.value.commodity.commodityConversionPrice ||
                (onSaleDetail.value.commodity.commodityPrice / 100) || 0

  return balance >= price
})

// 修改购买按钮处理逻辑，添加预售和在售支持
const handleBuyCommodityWithPresale = async (item) => {
  // 如果是预售商品，打开预售购买对话框
  if (item.isPreSale === 1 || props.yyypFilterType === 'presale') {
    await openPresaleBuyDialog(item)
  } else if (props.yyypFilterType === 'on_sale') {
    // 在售商品，打开在售购买对话框
    await openOnSaleBuyDialog(item)
  } else {
    // 其他商品，调用父组件的购买方法
    emit('buy-commodity', item)
  }
}

// 打开预售购买对话框
const openPresaleBuyDialog = async (item) => {
  if (!item || !item.id) {
    ElMessage.warning('商品信息不完整')
    return
  }

  currentPresaleItem.value = item
  presaleBuyDialogVisible.value = true
  presaleDetailLoading.value = true
  presaleDetail.value = null

  try {
    const response = await axios.post(
      apiUrls.yyypGetPresaleDetail(),
      {
        steamId: '',
        commodityId: item.id.toString()
      }
    )

    if (response.data.success) {
      presaleDetail.value = response.data.data
      console.log('预售详情:', presaleDetail.value)
    } else {
      throw new Error(response.data.message || '获取预售详情失败')
    }
  } catch (error) {
    console.error('获取预售详情失败:', error)
    ElMessage.error(error.message || '获取预售详情失败')
    presaleBuyDialogVisible.value = false
  } finally {
    presaleDetailLoading.value = false
  }
}

// 确认购买预售商品
const confirmPresaleBuy = async () => {
  if (!currentPresaleItem.value || !presaleDetail.value) {
    ElMessage.error('商品信息不完整')
    return
  }

  const commodity = presaleDetail.value.commodity
  if (!commodity) {
    ElMessage.error('商品详情缺失')
    return
  }

  // 获取定金金额
  const depositAmount = commodity.commodityPreSaleDTO?.depositAmount
  if (!depositAmount) {
    ElMessage.error('定金金额缺失')
    return
  }

  // 确认对话框
  try {
    await ElMessageBox.confirm(
      `确认购买 ${commodity.commodityName}？\n定金: ¥${depositAmount}`,
      '确认购买',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  buyingPresale.value = true

  try {
    const response = await axios.post(
      apiUrls.yyypBuyPresaleCommodity(),
      {
        steamId: '',
        commodityId: currentPresaleItem.value.id.toString(),
        price: depositAmount.toString(),  // 传入定金金额（元）
        autoConfirmPayment: presaleBuyForm.value.autoConfirmPayment,
        pollPayment: presaleBuyForm.value.pollPayment,
        paymentChannel: presaleBuyForm.value.paymentChannel
      }
    )

    if (response.data.success) {
      ElMessage.success('购买成功！')

      const orderData = response.data.data?.order
      if (orderData && orderData.orderNo) {
        ElMessage.info(`订单号: ${orderData.orderNo}`)
      }

      presaleBuyDialogVisible.value = false

      // 刷新列表
      emit('refresh-yyyp')
    } else {
      throw new Error(response.data.message || '购买失败')
    }
  } catch (error) {
    console.error('购买预售商品失败:', error)
    // 优先从 response.data.message 获取后端返回的错误信息
    const errorMsg = error.response?.data?.message || error.message || '购买失败，请稍后重试'
    ElMessage.error(errorMsg)
  } finally {
    buyingPresale.value = false
  }
}

// 打开在售购买对话框
const openOnSaleBuyDialog = async (item) => {
  if (!item || !item.id) {
    ElMessage.warning('商品信息不完整')
    return
  }

  currentOnSaleItem.value = item
  onSaleBuyDialogVisible.value = true
  onSaleDetailLoading.value = true
  onSaleDetail.value = null

  try {
    // 使用相同的API获取购买确认页面信息（在售商品也有这个接口）
    const response = await axios.post(
      apiUrls.yyypGetPresaleDetail(),  // 在售和预售使用相同的API
      {
        steamId: '',
        commodityId: item.id.toString()
      }
    )

    if (response.data.success) {
      onSaleDetail.value = response.data.data
      console.log('在售商品详情:', onSaleDetail.value)
    } else {
      throw new Error(response.data.message || '获取商品详情失败')
    }
  } catch (error) {
    console.error('获取商品详情失败:', error)
    ElMessage.error(error.message || '获取商品详情失败')
    onSaleBuyDialogVisible.value = false
  } finally {
    onSaleDetailLoading.value = false
  }
}

// 确认购买在售商品
const confirmOnSaleBuy = async () => {
  if (!currentOnSaleItem.value || !onSaleDetail.value) {
    ElMessage.error('商品信息不完整')
    return
  }

  const commodity = onSaleDetail.value.commodity
  if (!commodity) {
    ElMessage.error('商品详情缺失')
    return
  }

  // 获取商品价格
  const price = commodity.commodityConversionPrice || commodity.commodityPrice
  if (!price) {
    ElMessage.error('商品价格缺失')
    return
  }

  // 确认对话框
  try {
    await ElMessageBox.confirm(
      `确认购买 ${commodity.commodityName}？\n价格: ¥${typeof price === 'number' && price > 100 ? (price / 100).toFixed(2) : price}`,
      '确认购买',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  buyingOnSale.value = true

  try {
    // 调用父组件的购买方法
    emit('buy-commodity', currentOnSaleItem.value)

    ElMessage.success('购买请求已发送！')
    onSaleBuyDialogVisible.value = false

    // 刷新列表
    emit('refresh-yyyp')
  } catch (error) {
    console.error('购买在售商品失败:', error)
    const errorMsg = error.response?.data?.message || error.message || '购买失败，请稍后重试'
    ElMessage.error(errorMsg)
  } finally {
    buyingOnSale.value = false
  }
}
</script>

<style scoped src="./yyyp-commodity-list.css"></style>
