<template>
  <div>
    <div class="filters card">
      <div class="flex flex-wrap gap-4 items-center">
        <el-select 
          v-model="selectedSteamId" 
          placeholder="选择Steam账号" 
          class="steam-id-select"
          @change="handleSteamIdChange"
          filterable
        >
          <el-option
            v-for="item in steamIdList"
            :key="item.dataID"
            :label="`${item.dataName} (${item.steamID}) - ${item.item_count}件`"
            :value="item.steamID"
          >
            <span style="float: left">{{ item.dataName }} ({{ item.steamID }})</span>
            <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">
              {{ item.item_count }}件
            </span>
          </el-option>
        </el-select>
        <el-input
          v-model="searchText"
          placeholder="搜索饰品名称..."
          prefix-icon="Search"
          class="search-input"
          @keyup.enter="loadInventoryData"
          clearable
        />
        <el-select v-model="weaponTypeFilter" placeholder="武器类型" class="filter-select" clearable @change="handleFilterChange">
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
        <el-select v-model="floatRangeFilter" placeholder="磨损等级" class="filter-select" clearable @change="handleFilterChange">
          <el-option label="全部" value="" />
          <el-option label="崭新出厂" value="崭新出厂" />
          <el-option label="略有磨损" value="略有磨损" />
          <el-option label="久经沙场" value="久经沙场" />
          <el-option label="破损不堪" value="破损不堪" />
          <el-option label="战痕累累" value="战痕累累" />
        </el-select>
        <el-select v-model="pendantFilter" placeholder="挂件" class="filter-select" clearable @change="handleFilterChange">
          <el-option label="全部" value="" />
          <el-option label="有挂件" value="has" />
          <el-option label="无挂件" value="none" />
        </el-select>
        <el-select v-model="stickerFilter" placeholder="印花" class="filter-select" clearable @change="handleFilterChange">
          <el-option label="全部" value="" />
          <el-option label="有印花" value="has" />
          <el-option label="无印花" value="none" />
        </el-select>
        <el-select v-model="renameFilter" placeholder="改名" class="filter-select" clearable @change="handleFilterChange">
          <el-option label="全部" value="" />
          <el-option label="有改名" value="has" />
          <el-option label="无改名" value="none" />
        </el-select>
        <el-select v-model="tradeRestrictionFilter" placeholder="交易限制" class="filter-select" clearable @change="handleFilterChange">
          <el-option label="全部" value="" />
          <el-option label="有交易限制" value="has" />
          <el-option label="无交易限制" value="none" />
        </el-select>
        <el-button type="primary" @click="loadInventoryData" :loading="loading">
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="success" @click="fetchSteamInventory" :loading="fetchingInventory" class="action-button">
          更新Steam库存
        </el-button>
        <el-button type="success" @click="fetchYYYPPrice" :loading="fetchingYYYPPrice" class="action-button">
          获取悠悠有品价格
        </el-button>
        <el-button type="success" @click="fetchBuffPrice" :loading="fetchingBuffPrice" class="action-button">
          获取BUFF价格
        </el-button>
        <el-button 
          :type="showPriceDiff ? 'primary' : 'info'" 
          @click="showPriceDiff = !showPriceDiff" 
          class="action-button"
        >
          {{ showPriceDiff ? '显示差价' : '显示价格' }}
        </el-button>
        <div style="margin-left: auto; display: flex; gap: 0.5rem; align-items: center;">
          <el-switch
            v-if="displayMode === 'list'"
            v-model="groupMode"
            active-text="组合模式"
            inactive-text="明细模式"
            @change="handleToggleGroupMode"
          />
          <el-button 
            v-if="displayMode === 'card'"
            :type="isMultiSelectMode ? 'warning' : 'info'" 
            @click="toggleMultiSelectMode"
          >
            {{ isMultiSelectMode ? '取消多选' : '多选' }}
          </el-button>
          <el-button 
            :type="displayMode === 'list' ? 'primary' : ''" 
            @click="toggleDisplayMode"
          >
            {{ displayMode === 'list' ? '列表' : '卡片' }}
          </el-button>
        </div>
      </div>
    </div>

    <div class="inventory-stats">
      <div class="grid grid-5">
        <div class="card">
          <h3>总库存数量</h3>
          <p class="stat-number">{{ inventoryStats.totalCount }}</p>
        </div>
        <div class="card">
          <h3>购入总价值</h3>
          <p class="stat-number">¥{{ priceStats.total_price }}</p>
        </div>
        <div class="card">
          <h3>悠悠有品最低价</h3>
          <div class="stat-price-container">
            <p class="stat-number">¥{{ yyypPriceStats.total_price }}</p>
            <p class="stat-diff-right" :style="{ color: yyypPriceStats.diff >= 0 ? '#f56c6c' : '#4CAF50' }">
              {{ yyypPriceStats.diff >= 0 ? '+' : '' }}¥{{ yyypPriceStats.diff }}
            </p>
          </div>
        </div>
        <div class="card">
          <h3>BUFF最低价</h3>
          <div class="stat-price-container">
            <p class="stat-number">¥{{ buffPriceStats.total_price }}</p>
            <p class="stat-diff-right" :style="{ color: buffPriceStats.diff >= 0 ? '#f56c6c' : '#4CAF50' }">
              {{ buffPriceStats.diff >= 0 ? '+' : '' }}¥{{ buffPriceStats.diff }}
            </p>
          </div>
        </div>
        <div class="card">
          <h3>Steam参考价</h3>
          <div class="stat-price-container">
            <p class="stat-number">¥{{ steamPriceStats.total_price }}</p>
            <p class="stat-diff-right" :style="{ color: steamPriceStats.diff >= 0 ? '#f56c6c' : '#4CAF50' }">
              {{ steamPriceStats.diff >= 0 ? '+' : '' }}¥{{ steamPriceStats.diff }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 列表显示 -->
    <div class="table-container" v-if="displayMode === 'list'">
      <el-table
        ref="tableRef"
        :data="currentDisplayData"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        :row-style="getRowStyle"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        height="calc(100vh - 400px)"
        :default-sort="{ prop: 'buy_price', order: 'descending' }"
        @sort-change="handleSortChange"
        @row-click="handleRowClick"
        :row-key="row => row.assetid"
      >
        <el-table-column v-if="groupMode" type="expand" width="1">
          <template #default="scope">
            <div class="expand-content" v-if="scope.row.item_count > 1">
              <div class="expand-two-columns">
                <div 
                  v-for="(item, index) in getExpandedItems(scope.row)" 
                  :key="item.assetid"
                  class="expand-item-card"
                  @click="openPreview(item)"
                >
                  <div class="expand-item-row">
                    <div class="expand-item-left">
                      <div class="expand-item-image">
                        <img
                          v-if="getWeaponImage(scope.row.steam_hash_name)"
                          :src="getWeaponImage(scope.row.steam_hash_name)"
                          :alt="scope.row.item_name"
                          class="weapon-img-small"
                          @error="(e) => handleImageError(e, scope.row.steam_hash_name)"
                        />
                        <span v-else class="no-image">无图</span>
                        
                        <!-- 贴纸覆盖层 - 左下角 -->
                        <div v-if="item.sticker" class="sticker-overlay-expand">
                          <div
                            v-for="(sticker, sIdx) in parseStickers(item.sticker)"
                            :key="sIdx"
                            class="sticker-item-overlay-expand"
                            :title="sticker.name || '未知贴纸'"
                          >
                            <img
                              v-if="sticker.image"
                              :src="sticker.image"
                              :alt="sticker.name"
                              class="sticker-img-overlay"
                              @error="(e) => e.target.style.display = 'none'"
                            />
                            <div v-else class="sticker-placeholder-overlay">?</div>
                          </div>
                        </div>
                        
                        <!-- 挂件覆盖层 - 右上角 -->
                        <div v-if="item.pendant" class="pendant-overlay-expand">
                          <div
                            class="pendant-item-overlay-expand"
                            :title="parsePendant(item.pendant).name || '挂件'"
                          >
                            <img
                              v-if="parsePendant(item.pendant).image"
                              :src="parsePendant(item.pendant).image"
                              :alt="parsePendant(item.pendant).name"
                              class="pendant-img-overlay"
                              @error="(e) => e.target.style.display = 'none'"
                            />
                            <div v-else class="pendant-placeholder-overlay">🎗️</div>
                          </div>
                        </div>
                      </div>
                      <div v-if="item.remark" class="expand-remark-tag">
                        <el-tooltip v-if="parseTradeLockDate(item.remark) && !parseTradeLockDate(item.remark).expired" :content="item.remark" placement="top" effect="dark">
                          <el-tag type="warning" size="small">
                            至{{ parseTradeLockDate(item.remark).date }}
                          </el-tag>
                        </el-tooltip>
                        <el-tooltip v-else-if="item.remark && !parseTradeLockDate(item.remark)" :content="item.remark" placement="top" effect="dark">
                          <el-tag type="warning" size="small">交易保护</el-tag>
                        </el-tooltip>
                      </div>
                      <!-- 改名标签 - 只显示图标 -->
                      <div v-if="item.rename" class="expand-rename-tag">
                        <el-tag type="info" size="small" :title="item.rename">
                          🏷️
                        </el-tag>
                      </div>
                    </div>
                    <div class="expand-item-details">
                      <div class="expand-item-float" v-if="item.weapon_float && item.weapon_float !== '0' && item.weapon_float !== '0.0'">
                        <div class="float-text-row">
                          <span class="expand-label">磨损:</span>
                          <span class="expand-value-small">{{ item.weapon_float }}</span>
                        </div>
                        <div class="float-bar-mini">
                          <div class="float-segment fn"></div>
                          <div class="float-segment mw"></div>
                          <div class="float-segment ft"></div>
                          <div class="float-segment ww"></div>
                          <div class="float-segment bs"></div>
                          <div
                            class="float-pointer"
                            :style="{ left: `${parseFloat(item.weapon_float) * 100}%` }"
                          ></div>
                        </div>
                      </div>
                      <div class="expand-item-prices">
                        <!-- 第一行：购入和Steam -->
                        <div class="expand-price-item" v-if="item.buy_price && item.buy_price !== '0'">
                          <span class="expand-label">购入:</span>
                          <span class="expand-value">¥{{ parseFloat(item.buy_price).toFixed(2) }}</span>
                        </div>
                        <div class="expand-price-item" v-if="item.steam_price && item.steam_price !== '0'">
                          <span class="expand-label">Steam:</span>
                          <span 
                            class="expand-value"
                            :style="item.buy_price && item.buy_price !== '0' ? { color: parseFloat(item.steam_price) >= parseFloat(item.buy_price) ? '#f56c6c' : '#4CAF50' } : {}"
                          >
                            ¥{{ showPriceDiff && item.buy_price && item.buy_price !== '0' ? Math.abs(parseFloat(item.steam_price) - parseFloat(item.buy_price)).toFixed(2) : parseFloat(item.steam_price).toFixed(2) }}
                          </span>
                        </div>
                        <!-- 第二行：悠悠和BUFF -->
                        <div class="expand-price-item" v-if="item.yyyp_price && item.yyyp_price !== '0'">
                          <span class="expand-label">悠悠:</span>
                          <span 
                            class="expand-value"
                            :style="item.buy_price && item.buy_price !== '0' ? { color: parseFloat(item.yyyp_price) >= parseFloat(item.buy_price) ? '#f56c6c' : '#4CAF50' } : {}"
                          >
                            ¥{{ showPriceDiff && item.buy_price && item.buy_price !== '0' ? Math.abs(parseFloat(item.yyyp_price) - parseFloat(item.buy_price)).toFixed(2) : parseFloat(item.yyyp_price).toFixed(2) }}
                          </span>
                        </div>
                        <div class="expand-price-item" v-if="item.buff_price && item.buff_price !== '0'">
                          <span class="expand-label">BUFF:</span>
                          <span 
                            class="expand-value"
                            :style="item.buy_price && item.buy_price !== '0' ? { color: parseFloat(item.buff_price) >= parseFloat(item.buy_price) ? '#f56c6c' : '#4CAF50' } : {}"
                          >
                            ¥{{ showPriceDiff && item.buy_price && item.buy_price !== '0' ? Math.abs(parseFloat(item.buff_price) - parseFloat(item.buy_price)).toFixed(2) : parseFloat(item.buff_price).toFixed(2) }}
                          </span>
                        </div>
                      </div>
                      <div class="expand-item-meta">
                        <div v-if="item.order_time" class="expand-meta-item">
                          <span class="expand-label">入库:</span>
                          <span class="expand-value" style="color: #9E9E9E;">{{ item.order_time }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>
            <div v-else class="expand-content-empty">
              <span style="color: #999;">仅有1件物品，无需展开</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="图片" width="144" align="center" fixed="left">
          <template #default="scope">
            <div class="weapon-image-cell" style="cursor: pointer;">
              <img
                v-if="getWeaponImage(scope.row.steam_hash_name)"
                :src="getWeaponImage(scope.row.steam_hash_name)"
                :alt="scope.row.item_name"
                class="weapon-img"
                @error="(e) => handleImageError(e, scope.row.steam_hash_name)"
              />
              <span v-else class="no-image">无图</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="饰品名称" min-width="250">
          <template #default="scope">
            <div class="item-name-cell">
              <div class="item-title">{{ getItemTitle(scope.row) }}</div>
              <!-- 组合模式下显示分页器 - 固定在名称下方 -->
              <div v-if="groupMode && getExpandedTotal(scope.row) > getItemsPerPage()" class="inline-pagination-below" @click.stop>
                <el-pagination
                  small
                  :current-page="expandedRowPages[scope.row.assetid] || 1"
                  :page-size="getItemsPerPage()"
                  :total="getExpandedTotal(scope.row)"
                  layout="prev, pager, next"
                  :hide-on-single-page="true"
                  @current-change="(page) => handleExpandPageChange(scope.row, page)"
                />
              </div>
              <div class="item-extras" v-if="hasExtras(scope.row)">
                <!-- 印花图片 -->
                <div class="sticker-list" v-if="scope.row.sticker">
                  <div
                    v-for="(sticker, idx) in parseStickers(scope.row.sticker)"
                    :key="idx"
                    class="sticker-item"
                    :title="sticker.name || '未知贴纸'"
                  >
                    <img
                      v-if="sticker.image"
                      :src="sticker.image"
                      :alt="sticker.name"
                      class="sticker-img"
                      @error="(e) => e.target.style.display = 'none'"
                    />
                    <div v-else class="sticker-placeholder">?</div>
                  </div>
                </div>
                <!-- 挂件图片 -->
                <div class="pendant-list" v-if="scope.row.pendant">
                  <img
                    v-if="parsePendant(scope.row.pendant)?.image"
                    :src="parsePendant(scope.row.pendant).image"
                    :alt="parsePendant(scope.row.pendant)?.name"
                    class="pendant-img"
                    @error="(e) => e.target.style.display = 'none'"
                  />
                </div>
                <!-- 改名显示 -->
                <div class="rename-text" v-if="scope.row.rename">
                  <span class="rename-value">{{ scope.row.rename }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="weapon_type" label="类型" min-width="100" />
        <el-table-column v-if="groupMode" prop="item_count" label="数量" width="120" align="center" sortable="custom">
          <template #default="scope">
            <span>{{ scope.row.item_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="weapon_float"
          label="磨损值"
          min-width="220"
          sortable="custom"
        >
          <template #default="scope">
            <!-- 组合模式下，数量大于1时不显示磨损值 -->
            <div v-if="groupMode && scope.row.item_count > 1" style="color: #888;">
              多个磨损值
            </div>
            <div v-else-if="scope.row.weapon_float">
              <div style="font-family: monospace; font-size: 0.85rem; margin-bottom: 4px;">
                {{ scope.row.weapon_float }}
              </div>
              <!-- 磨损值显示条 -->
              <div class="float-bar">
                <div class="float-segment fn"></div>
                <div class="float-segment mw"></div>
                <div class="float-segment ft"></div>
                <div class="float-segment ww"></div>
                <div class="float-segment bs"></div>
                <div
                  class="float-pointer"
                  :style="{ left: `${parseFloat(scope.row.weapon_float) * 100}%` }"
                ></div>
              </div>
            </div>
            <span v-else style="color: #888;">N/A</span>
          </template>
        </el-table-column>
        <el-table-column 
          prop="buy_price" 
          label="购入价格" 
          width="150" 
          sortable="custom"
        >
          <template #default="scope">
            <div v-if="editingAssetId !== scope.row.assetid" 
                 @click="startEdit(scope.row)" 
                 style="cursor: pointer; padding: 5px;">
              <div v-if="scope.row.buy_price" style="display: flex; align-items: center; gap: 5px;">
                <span style="color: #fff; font-weight: bold;">¥{{ parseFloat(scope.row.buy_price).toFixed(2) }}</span>
              </div>
              <span v-else style="color: #888;">点击输入</span>
            </div>
            <el-input 
              v-else
              v-model="editingPrice" 
              placeholder="输入价格" 
              size="small"
              :id="'price-input-' + scope.row.assetid"
              @blur="finishEdit(scope.row)"
              @keyup.enter="finishEdit(scope.row)"
              @keyup.esc="cancelEdit"
            />
          </template>
        </el-table-column>
        <el-table-column 
          prop="yyyp_price" 
          label="悠悠有品" 
          width="180" 
          sortable="custom"
        >
          <template #default="scope">
            <div v-if="scope.row.yyyp_price && scope.row.buy_price" style="display: flex; flex-direction: column; align-items: flex-start; gap: 2px;">
              <span style="color: #fff; font-weight: bold;">
                ¥{{ parseFloat(scope.row.yyyp_price).toFixed(2) }}
              </span>
              <span 
                :style="{
                  color: parseFloat(scope.row.yyyp_price) < parseFloat(scope.row.buy_price) ? '#4CAF50' : '#f56c6c',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }"
              >
                {{ parseFloat(scope.row.yyyp_price) < parseFloat(scope.row.buy_price) ? '-' : '+' }}
                ¥{{ Math.abs(parseFloat(scope.row.yyyp_price) - parseFloat(scope.row.buy_price)).toFixed(2) }}
              </span>
            </div>
            <span v-else-if="scope.row.yyyp_price" style="color: #fff; font-weight: bold;">
              ¥{{ parseFloat(scope.row.yyyp_price).toFixed(2) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column 
          prop="buff_price" 
          label="BUFF" 
          width="180" 
          sortable="custom"
        >
          <template #default="scope">
            <div v-if="scope.row.buff_price && scope.row.buy_price" style="display: flex; flex-direction: column; align-items: flex-start; gap: 2px;">
              <span style="color: #fff; font-weight: bold;">
                ¥{{ parseFloat(scope.row.buff_price).toFixed(2) }}
              </span>
              <span 
                :style="{
                  color: parseFloat(scope.row.buff_price) < parseFloat(scope.row.buy_price) ? '#4CAF50' : '#f56c6c',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }"
              >
                {{ parseFloat(scope.row.buff_price) < parseFloat(scope.row.buy_price) ? '-' : '+' }}
                ¥{{ Math.abs(parseFloat(scope.row.buff_price) - parseFloat(scope.row.buy_price)).toFixed(2) }}
              </span>
            </div>
            <span v-else-if="scope.row.buff_price" style="color: #fff; font-weight: bold;">
              ¥{{ parseFloat(scope.row.buff_price).toFixed(2) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column 
          prop="steam_price" 
          label="Steam" 
          width="120" 
          sortable="custom"
        >
          <template #default="scope">
            <span v-if="scope.row.steam_price" style="color: #fff; font-weight: bold;">
              ¥{{ parseFloat(scope.row.steam_price).toFixed(2) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="!groupMode"
          label="备注"
          width="220"
          fixed="right"
        >
          <template #default="scope">
            <div v-if="scope.row.remark && parseTradeLockDate(scope.row.remark) && !parseTradeLockDate(scope.row.remark).expired">
              <el-tooltip :content="scope.row.remark" placement="left" effect="dark">
                <el-tag type="warning" size="small" style="cursor: help;">
                  至{{ parseTradeLockDate(scope.row.remark).date }}
                </el-tag>
              </el-tooltip>
            </div>
            <div v-else-if="scope.row.remark && !parseTradeLockDate(scope.row.remark)">
              <el-tooltip :content="scope.row.remark" placement="left" effect="dark">
                <el-tag type="warning" size="small" style="cursor: help;">
                  交易限制
                </el-tag>
              </el-tooltip>
            </div>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column 
          v-if="!groupMode"
          prop="order_time" 
          label="入库时间" 
          width="180" 
          sortable="custom"
          fixed="right"
        >
          <template #default="scope">
            <span v-if="scope.row.order_time" style="color: #9E9E9E;">
              {{ scope.row.order_time }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-footer">
        <span>共 {{ currentDisplayData.length }} 条数据</span>
        <span v-if="hasMore && !loadingMore" style="margin-left: 1rem; color: #999;">滚动加载更多...</span>
        <span v-if="loadingMore" style="margin-left: 1rem; color: #4CAF50;">正在加载更多...</span>
        <span v-if="!hasMore && currentDisplayData.length > 0" style="margin-left: 1rem; color: #999;">已加载全部数据</span>
      </div>
      <!-- 滚动触发元素 -->
      <div id="load-more-trigger" style="height: 1px;"></div>
    </div>

    <!-- 多选模式下的操作按钮 -->
    <div v-if="isMultiSelectMode && selectedItems.length > 0 && !isSelectingComponent" class="multi-select-actions">
      <div class="selected-count">
        已选择 {{ selectedItems.length }} 件物品
      </div>
      <div class="action-buttons">
        <el-button type="info" @click="selectAllDisplayed">全选</el-button>
        <el-button type="primary" @click="showSellDialog">出售</el-button>
        <el-button type="primary" @click="showRentDialog">出租</el-button>
        <el-button type="success" @click="moveToComponent">存入组件</el-button>
        <el-button @click="clearSelection">清空选择</el-button>
      </div>
    </div>

    <!-- 选择组件模式提示 -->
    <div v-if="isSelectingComponent" class="component-selection-banner">
      <div class="banner-content">
        <el-icon class="banner-icon"><InfoFilled /></el-icon>
        <span class="banner-text">
          正在选择库存组件，准备存入 <strong>{{ itemsToDeposit.length }}</strong> 件物品，请点击下方组件卡片完成存入
        </span>
      </div>
      <el-button @click="cancelComponentSelection" type="danger" plain>取消存入</el-button>
    </div>

    <!-- 卡片显示 -->
    <div class="card-container" v-if="displayMode === 'card'">
      <div v-loading="loading" class="card-grid">
        <div
          v-for="item in currentDisplayData"
          :key="item.assetid"
          class="inventory-card"
          :class="{ 
            'selected': isItemSelected(item.assetid), 
            'multi-select-mode': isMultiSelectMode,
            'trade-restricted': hasTradeRestriction(item) && isMultiSelectMode,
            'component-full': isSelectingComponent && parseFloat(item.weapon_float || 0) >= 1000
          }"
          :data-assetid="item.assetid"
          @click="handleCardClick(item)"
        >
          <div class="card-image">
            <img
              v-if="getWeaponImage(item.steam_hash_name)"
              :data-src="getWeaponImage(item.steam_hash_name)"
              :alt="item.item_name"
              class="lazy-image"
              @error="(e) => handleImageError(e, item.steam_hash_name)"
            />
            <div v-else class="image-placeholder">
              <span>无图片</span>
            </div>
            <!-- 贴纸图片覆盖层 - 左下角 -->
            <div v-if="item.sticker" class="sticker-overlay">
              <div
                v-for="(sticker, index) in parseStickers(item.sticker)"
                :key="index"
                class="sticker-item-overlay"
                :title="sticker.name || '未知贴纸'"
              >
                <img
                  v-if="sticker.image"
                  :data-src="sticker.image"
                  :alt="sticker.name"
                  class="sticker-img-overlay lazy-image"
                  @error="(e) => e.target.style.display = 'none'"
                />
                <div v-else class="sticker-placeholder-overlay">?</div>
              </div>
            </div>
            <!-- 挂件图片覆盖层 - 右上角 -->
            <div v-if="item.pendant" class="pendant-overlay">
              <div
                class="pendant-item-overlay"
                :title="parsePendant(item.pendant).name || '挂件'"
              >
                <img
                  v-if="parsePendant(item.pendant).image"
                  :data-src="parsePendant(item.pendant).image"
                  :alt="parsePendant(item.pendant).name"
                  class="pendant-img-overlay lazy-image"
                  @error="(e) => e.target.style.display = 'none'"
                />
                <div v-else class="pendant-placeholder-overlay">🎗️</div>
              </div>
            </div>
          </div>
          <div class="card-content">
            <div class="card-title" :title="getCardTitle(item)">
              {{ getCardTitle(item) }}
            </div>
            <div class="card-info">
              <!-- 组件：显示空位占比 -->
              <div v-if="item.classid === '3604678661'" class="component-storage-info">
                <div class="storage-stats">
                  <span class="storage-label">已存储:</span>
                  <span class="storage-value">{{ parseFloat(item.weapon_float || 0) }} / 1000</span>
                </div>
                <div class="storage-progress">
                  <el-progress
                    :percentage="(parseFloat(item.weapon_float || 0) / 1000 * 100)"
                    :stroke-width="8"
                    :show-text="false"
                    :color="getComponentProgressColor(parseFloat(item.weapon_float || 0))"
                  />
                </div>
                <div class="storage-remaining">
                  <span class="remaining-label">剩余空位:</span>
                  <span class="remaining-value" :class="getComponentRemainingClass(1000 - parseFloat(item.weapon_float || 0))">
                    {{ 1000 - parseFloat(item.weapon_float || 0) }}
                  </span>
                </div>
              </div>
              
              <!-- 普通物品：显示磨损值 -->
              <template v-else>
                <div class="float-bar-container" v-if="item.weapon_float">
                  <div class="float-bar">
                    <!-- 五个磨损等级的颜色区域 -->
                    <div class="float-segment fn" title="崭新出厂 (0.00 - 0.07)"></div>
                    <div class="float-segment mw" title="略有磨损 (0.07 - 0.15)"></div>
                    <div class="float-segment ft" title="久经沙场 (0.15 - 0.38)"></div>
                    <div class="float-segment ww" title="破损不堪 (0.38 - 0.45)"></div>
                    <div class="float-segment bs" title="战痕累累 (0.45 - 1.00)"></div>
                    <!-- 磨损值指针 -->
                    <div
                      class="float-pointer"
                      :style="{ left: `${parseFloat(item.weapon_float) * 100}%` }"
                      :title="`磨损值: ${item.weapon_float}`"
                    ></div>
                  </div>
                </div>
                <div class="float-value" v-if="item.weapon_float">
                  {{ item.weapon_float }}
                </div>
              </template>
            </div>
            <div class="card-prices" v-if="item.classid !== '3604678661'">
              <!-- 第一行：购入和Steam -->
              <div class="price-row" v-if="item.buy_price || item.steam_price">
                <div class="price-group" v-if="item.buy_price">
                  <span class="price-label">购入:</span>
                  <span class="price-value buy-price">¥{{ parseFloat(item.buy_price).toFixed(2) }}</span>
                </div>
                <div class="price-group" v-if="item.steam_price && item.steam_price !== '0'">
                  <span class="price-label">Steam:</span>
                  <span 
                    class="price-value"
                    :style="item.buy_price ? { color: parseFloat(item.steam_price) >= parseFloat(item.buy_price) ? '#f56c6c' : '#4CAF50' } : {}"
                  >
                    ¥{{ showPriceDiff && item.buy_price ? Math.abs(parseFloat(item.steam_price) - parseFloat(item.buy_price)).toFixed(2) : parseFloat(item.steam_price).toFixed(2) }}
                  </span>
                </div>
              </div>
              <!-- 第二行：悠悠和BUFF -->
              <div class="price-row" v-if="item.yyyp_price || item.buff_price">
                <div class="price-group" v-if="item.yyyp_price && item.yyyp_price !== '0'">
                  <span class="price-label">悠悠:</span>
                  <span
                    class="price-value"
                    :style="item.buy_price ? { color: parseFloat(item.yyyp_price) >= parseFloat(item.buy_price) ? '#f56c6c' : '#4CAF50' } : {}"
                  >
                    ¥{{ showPriceDiff && item.buy_price ? Math.abs(parseFloat(item.yyyp_price) - parseFloat(item.buy_price)).toFixed(2) : parseFloat(item.yyyp_price).toFixed(2) }}
                  </span>
                </div>
                <div class="price-group" v-if="item.buff_price && item.buff_price !== '0'">
                  <span class="price-label">BUFF:</span>
                  <span
                    class="price-value"
                    :style="item.buy_price ? { color: parseFloat(item.buff_price) >= parseFloat(item.buy_price) ? '#f56c6c' : '#4CAF50' } : {}"
                  >
                    ¥{{ showPriceDiff && item.buy_price ? Math.abs(parseFloat(item.buff_price) - parseFloat(item.buy_price)).toFixed(2) : parseFloat(item.buff_price).toFixed(2) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="card-footer">
              <div class="card-tags">
                <el-tooltip v-if="item.remark && parseTradeLockDate(item.remark) && !parseTradeLockDate(item.remark).expired" :content="item.remark" placement="top" effect="dark">
                  <el-tag type="warning" size="small">
                    至{{ parseTradeLockDate(item.remark).date }}
                  </el-tag>
                </el-tooltip>
                <el-tooltip v-else-if="item.remark && !parseTradeLockDate(item.remark)" :content="item.remark" placement="top" effect="dark">
                  <el-tag type="warning" size="small">交易限制</el-tag>
                </el-tooltip>
                <el-tag v-if="item.rename" type="info" size="small" class="rename-tag">
                  <span class="tag-icon">🏷️</span>{{ item.rename }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="table-footer">
        <span>共 {{ currentDisplayData.length }} 条数据</span>
        <span v-if="hasMore && !loadingMore" style="margin-left: 1rem; color: #999;">滚动加载更多...</span>
        <span v-if="loadingMore" style="margin-left: 1rem; color: #4CAF50;">正在加载更多...</span>
        <span v-if="!hasMore && inventoryData.length > 0" style="margin-left: 1rem; color: #999;">已加载全部数据</span>
      </div>
      <!-- 滚动触发元素 -->
      <div id="load-more-trigger-card" style="height: 1px;"></div>
    </div>

    <!-- 备注弹窗 -->
    <el-dialog
      v-model="remarkDialogVisible"
      title="添加备注"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-input 
        v-model="currentRemark" 
        type="textarea"
        :rows="4"
        placeholder="请输入备注信息（可选）"
        maxlength="200"
        show-word-limit
      />
      <template #footer>
        <el-button @click="remarkDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRemark">确定</el-button>
      </template>
    </el-dialog>

    <!-- 备注弹窗 -->
    <el-dialog
      v-model="remarkDialogVisible"
      title="添加备注"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-input 
        v-model="currentRemark" 
        type="textarea"
        :rows="4"
        placeholder="请输入备注信息（可选）"
        maxlength="200"
        show-word-limit
      />
      <template #footer>
        <el-button @click="remarkDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRemark">确定</el-button>
      </template>
    </el-dialog>

    <!-- 备注弹窗 -->
    <el-dialog
      v-model="remarkDialogVisible"
      title="添加备注"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-input 
        v-model="currentRemark" 
        type="textarea"
        :rows="4"
        placeholder="请输入备注信息"
        maxlength="200"
        show-word-limit
      />
      <template #footer>
        <el-button @click="remarkDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRemark">确定</el-button>
      </template>
    </el-dialog>

    <!-- 备注弹窗 -->
    <el-dialog
      v-model="remarkDialogVisible"
      title="添加备注"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-input 
        v-model="currentRemark" 
        type="textarea"
        :rows="4"
        placeholder="请输入备注信息（可选）"
        maxlength="200"
        show-word-limit
      />
      
      <template #footer>
        <el-button @click="remarkDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRemark">确认</el-button>
      </template>
    </el-dialog>

    <!-- 出售/出租弹窗 -->
    <el-dialog
      v-model="sellRentDialogVisible"
      :title="sellRentDialogTitle"
      width="800px"
      :close-on-click-modal="false"
      class="sell-rent-dialog"
    >
      <div class="sell-rent-content">
        <div class="selected-items-list-with-inputs">
          <div class="list-header">
            <h4>选中的物品 ({{ selectedItems.length }}件)</h4>
            <div class="header-actions">
              <el-button 
                size="small" 
                type="success"
                @click="isGroupedView ? autoFillGroupPrices() : autoFillItemPrices()"
              >
                自动填充价格
              </el-button>
              <el-button 
                size="small" 
                @click="toggleGroupedView"
                :type="isGroupedView ? 'primary' : 'default'"
              >
                {{ isGroupedView ? '取消组合' : '组合显示' }}
              </el-button>
            </div>
          </div>
          
          <!-- 非组合显示 -->
          <div v-if="!isGroupedView" class="items-scroll">
            <div 
              v-for="(item, index) in selectedItems" 
              :key="item.assetid"
              class="selected-item-card"
            >
              <div class="item-left">
                <div class="item-thumb-wrapper">
                  <img
                    v-if="getWeaponImage(item.steam_hash_name)"
                    :src="getWeaponImage(item.steam_hash_name)"
                    :alt="item.item_name"
                    class="item-thumb"
                  />
                  
                  <!-- 印花覆盖层 - 左下角 -->
                  <div v-if="item.sticker && parseStickers(item.sticker).length > 0" class="item-sticker-overlay">
                    <div
                      v-for="(sticker, sIdx) in parseStickers(item.sticker)"
                      :key="sIdx"
                      class="item-sticker-mini"
                      :title="sticker.name || '未知印花'"
                    >
                      <img
                        v-if="sticker.image"
                        :src="sticker.image"
                        :alt="sticker.name"
                      />
                    </div>
                  </div>
                  
                  <!-- 挂件覆盖层 - 右上角 -->
                  <div v-if="item.pendant" class="item-pendant-overlay">
                    <div
                      class="item-pendant-mini"
                      :title="parsePendant(item.pendant).name || '挂件'"
                    >
                      <img
                        v-if="parsePendant(item.pendant).image"
                        :src="parsePendant(item.pendant).image"
                        :alt="parsePendant(item.pendant).name"
                      />
                    </div>
                  </div>
                </div>
                
                <div class="item-info">
                  <div class="item-name">{{ getCardTitle(item) }}</div>
                  <div class="item-details">
                    <!-- 磨损进度条 -->
                    <div class="item-float-bar" v-if="item.weapon_float && item.weapon_float !== '0' && item.weapon_float !== '0.0'">
                      <div class="float-row">
                        <div class="float-bar-mini">
                          <div class="float-segment fn"></div>
                          <div class="float-segment mw"></div>
                          <div class="float-segment ft"></div>
                          <div class="float-segment ww"></div>
                          <div class="float-segment bs"></div>
                          <div
                            class="float-pointer"
                            :style="{ left: `${parseFloat(item.weapon_float) * 100}%` }"
                          ></div>
                        </div>
                        <div class="float-value-text">{{ item.weapon_float }}</div>
                      </div>
                    </div>
                    
                    <!-- 改名信息 -->
                    <div class="item-rename" v-if="item.rename">
                      <span class="rename-icon">🏷️</span>
                      <span class="rename-value" :title="item.rename">{{ item.rename }}</span>
                    </div>
                    
                    <!-- 购入价与悠悠底价在同一行 -->
                    <div class="item-price-row">
                      <div class="item-buy-price" v-if="item.buy_price">
                        购入: ¥{{ parseFloat(item.buy_price).toFixed(2) }}
                      </div>
                      
                      <!-- 悠悠底价 -->
                      <div class="item-yyyp-price">
                        <template v-if="yyypRealtimePrices[item.assetid]">
                          <div v-if="yyypRealtimePrices[item.assetid].loading" class="price-loading">
                            <el-icon class="is-loading"><Loading /></el-icon>
                            <span>查询中...</span>
                          </div>
                          <div v-else-if="yyypRealtimePrices[item.assetid].error" class="price-error">
                            悠悠: {{ yyypRealtimePrices[item.assetid].error }}
                          </div>
                          <div v-else 
                            :class="{
                              'price-higher': item.buy_price && parseFloat(yyypRealtimePrices[item.assetid].lowest_price) > parseFloat(item.buy_price),
                              'price-lower': item.buy_price && parseFloat(yyypRealtimePrices[item.assetid].lowest_price) < parseFloat(item.buy_price),
                              'price-equal': item.buy_price && parseFloat(yyypRealtimePrices[item.assetid].lowest_price) === parseFloat(item.buy_price),
                              'price-no-compare': !item.buy_price
                            }"
                          >
                            悠悠: ¥{{ parseFloat(yyypRealtimePrices[item.assetid].lowest_price).toFixed(2) }}
                            <span class="price-count">({{ yyypRealtimePrices[item.assetid].total_count }}件)</span>
                          </div>
                        </template>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="item-right">
                <el-form :model="itemForms[index]" :rules="itemFormRules" :ref="el => itemFormRefs[index] = el" class="inline-form">
                  <div>
                    <el-form-item prop="price">
                      <el-input 
                        v-model="itemForms[index].price" 
                        placeholder="价格"
                        @input="validateItemPrice(index)"
                        size="small"
                        :disabled="itemForms[index].uploadStatus === 'uploading' || itemForms[index].uploadStatus === 'success'"
                      />
                    </el-form-item>
                    <el-button 
                      size="small" 
                      @click="openRemarkDialog(index)"
                      :type="itemForms[index].remark ? 'success' : 'default'"
                      :disabled="itemForms[index].uploadStatus === 'uploading' || itemForms[index].uploadStatus === 'success'"
                    >
                      {{ itemForms[index].remark ? '已备注' : '备注' }}
                    </el-button>
                  </div>
                  <!-- 上架状态显示 -->
                  <div v-if="itemForms[index].uploadStatus" class="upload-status">
                    <el-tag 
                      v-if="itemForms[index].uploadStatus === 'uploading'" 
                      type="info" 
                      size="small"
                    >
                      <el-icon class="is-loading"><Loading /></el-icon>
                      {{ itemForms[index].uploadMessage }}
                    </el-tag>
                    <el-tag 
                      v-else-if="itemForms[index].uploadStatus === 'success'" 
                      type="success" 
                      size="small"
                    >
                      ✓ {{ itemForms[index].uploadMessage }}
                    </el-tag>
                    <el-tag 
                      v-else-if="itemForms[index].uploadStatus === 'failed'" 
                      type="danger" 
                      size="small"
                      :title="itemForms[index].uploadMessage"
                    >
                      ✗ {{ itemForms[index].uploadMessage }}
                    </el-tag>
                  </div>
                </el-form>
              </div>
            </div>
          </div>
          
          <!-- 组合显示 -->
          <div v-else class="items-scroll">
            <div 
              v-for="group in groupedItems" 
              :key="group.classid"
              class="grouped-section"
            >
              <div class="group-card" @click="toggleGroupExpand(group.classid)">
                <div class="group-left">
                  <img
                    v-if="getWeaponImage(group.steamHashName)"
                    :src="getWeaponImage(group.steamHashName)"
                    class="group-thumb"
                  />
                  <div class="group-info">
                    <div class="group-name">{{ group.itemName }}</div>
                    <div class="group-meta">
                      <span class="group-count">{{ group.items.length }} 件</span>
                      <span v-if="getGroupAveragePrice(group)" class="group-avg-price">
                        均价: ¥{{ getGroupAveragePrice(group) }}
                      </span>
                      <!-- 悠悠底价显示 -->
                      <template v-if="group.items[0] && yyypRealtimePrices[group.items[0].assetid]">
                        <span v-if="yyypRealtimePrices[group.items[0].assetid].loading" class="group-yyyp-price price-loading">
                          <el-icon class="is-loading"><Loading /></el-icon>
                          <span>查询中...</span>
                        </span>
                        <span v-else-if="yyypRealtimePrices[group.items[0].assetid].error" class="group-yyyp-price price-error">
                          悠悠: {{ yyypRealtimePrices[group.items[0].assetid].error }}
                        </span>
                        <span v-else 
                          class="group-yyyp-price"
                          :class="{
                            'price-higher': getGroupAveragePrice(group) && parseFloat(yyypRealtimePrices[group.items[0].assetid].lowest_price) > parseFloat(getGroupAveragePrice(group)),
                            'price-lower': getGroupAveragePrice(group) && parseFloat(yyypRealtimePrices[group.items[0].assetid].lowest_price) < parseFloat(getGroupAveragePrice(group)),
                            'price-equal': getGroupAveragePrice(group) && parseFloat(yyypRealtimePrices[group.items[0].assetid].lowest_price) === parseFloat(getGroupAveragePrice(group)),
                            'price-no-compare': !getGroupAveragePrice(group)
                          }"
                        >
                          悠悠: ¥{{ parseFloat(yyypRealtimePrices[group.items[0].assetid].lowest_price).toFixed(2) }}
                          <span class="price-count">({{ yyypRealtimePrices[group.items[0].assetid].total_count }}件)</span>
                        </span>
                      </template>
                    </div>
                  </div>
                  <div class="group-expand-icon">
                    <el-icon :class="{ 'is-expanded': expandedGroups[group.classid] }">
                      <ArrowDown />
                    </el-icon>
                  </div>
                </div>
                
                <div class="group-right" @click.stop>
                  <el-form :model="groupForms[group.classid]" :rules="itemFormRules" :ref="el => groupFormRefs[group.classid] = el" class="inline-form">
                    <el-form-item prop="price">
                      <el-input 
                        v-model="groupForms[group.classid].price" 
                        placeholder="统一价格"
                        @input="validateGroupPrice(group.classid)"
                        size="small"
                      />
                    </el-form-item>
                    <el-button 
                      size="small" 
                      @click="openGroupRemarkDialog(group.classid)"
                      :type="groupForms[group.classid].remark ? 'success' : 'default'"
                    >
                      {{ groupForms[group.classid].remark ? '已备注' : '备注' }}
                    </el-button>
                  </el-form>
                </div>
              </div>
              
              <!-- 展开的物品列表 -->
              <div v-if="expandedGroups[group.classid]" class="group-items-list">
                <div 
                  v-for="item in group.items" 
                  :key="item.assetid"
                  class="group-item-detail"
                >
                  <div class="item-detail-row">
                    <span v-if="item.buy_price" class="detail-label">
                      购入: ¥{{ parseFloat(item.buy_price).toFixed(2) }}
                    </span>
                    <span v-if="item.weapon_float && item.weapon_float !== '0' && item.weapon_float !== '0.0'" class="detail-label">
                      磨损: {{ item.weapon_float }}
                    </span>
                    <span v-if="item.rename" class="detail-label rename" :title="item.rename">
                      🏷️ {{ item.rename }}
                    </span>
                    <span v-if="item.remark" class="detail-label remark" :title="item.remark">
                      ⚠️ {{ item.remark }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button type="success" @click="confirmSellRent('yyyp')" :loading="submitting">上架悠悠</el-button>
        <el-button type="success" @click="confirmSellRent('buff')" :loading="submitting" disabled>上架BUFF</el-button>
        <el-button type="success" @click="confirmSellRent('csfl')" :loading="submitting" disabled>上架CSFL</el-button>
      </template>
    </el-dialog>

    <!-- 预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      :title="previewItem ? getCardTitle(previewItem) : ''"
      width="800px"
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      class="preview-dialog"
    >
      <div v-if="previewItem" class="preview-content">
        <div class="preview-main-layout">
          <!-- 左侧区域 -->
          <div class="preview-left-section">
            <!-- 图片区域 -->
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

            <!-- 详细信息区域 -->
            <div class="preview-info-section">
              <!-- 磨损信息 -->
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
                <div class="preview-float-range" v-if="previewItem.float_range">
                  {{ previewItem.float_range }}
                </div>
              </div>

              <!-- 价格信息 -->
              <div class="preview-prices">
                <div class="preview-price-row" v-if="previewItem.buy_price || previewItem.steam_price || true">
                  <div class="preview-price-item">
                    <span class="preview-price-label">购入:</span>
                    <span class="preview-price-value buy-price" v-if="previewItem.buy_price">¥{{ parseFloat(previewItem.buy_price).toFixed(2) }}</span>
                    <span class="preview-price-value" v-else style="color: #888;">-</span>
                  </div>
                  <div class="preview-price-item" v-if="previewItem.steam_price">
                    <span class="preview-price-label">Steam:</span>
                    <span class="preview-price-value">¥{{ parseFloat(previewItem.steam_price).toFixed(2) }}</span>
                  </div>
                </div>
                <div class="preview-price-row" v-if="previewItem.yyyp_price || previewItem.buff_price">
                  <div class="preview-price-item" v-if="previewItem.yyyp_price">
                    <span class="preview-price-label">悠悠:</span>
                    <span
                      class="preview-price-value"
                      :class="getPriceDiffClass(previewItem.yyyp_price, previewItem.buy_price)"
                    >
                      ¥{{ parseFloat(previewItem.yyyp_price).toFixed(2) }}
                    </span>
                  </div>
                  <div class="preview-price-item" v-if="previewItem.buff_price">
                    <span class="preview-price-label">BUFF:</span>
                    <span
                      class="preview-price-value"
                      :class="getPriceDiffClass(previewItem.buff_price, previewItem.buy_price)"
                    >
                      ¥{{ parseFloat(previewItem.buff_price).toFixed(2) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- 标签信息 -->
              <div class="preview-tags">
                <el-tooltip v-if="previewItem.remark && parseTradeLockDate(previewItem.remark) && !parseTradeLockDate(previewItem.remark).expired" :content="previewItem.remark" placement="top" effect="dark">
                  <el-tag type="warning" size="default">
                    交易限制至 {{ parseTradeLockDate(previewItem.remark).date }}
                  </el-tag>
                </el-tooltip>
                <el-tooltip v-else-if="previewItem.remark && !parseTradeLockDate(previewItem.remark)" :content="previewItem.remark" placement="top" effect="dark">
                  <el-tag type="warning" size="default">交易限制</el-tag>
                </el-tooltip>
              </div>

              <!-- 操作按钮 -->
              <div class="preview-action-buttons">
                <el-button type="primary" @click="handleYYYPSell">悠悠出售</el-button>
                <el-button type="primary" @click="handleYYYPRent">悠悠出租</el-button>
                <el-button type="primary" @click="handleBuffSell">BUFF出售</el-button>
                <el-button type="primary" @click="handleBuffRent">BUFF出租</el-button>
              </div>
            </div>
          </div>

          <!-- 右侧区域 -->
          <div class="preview-right-section">
            <!-- 改名标签 -->
            <div class="preview-rename" v-if="previewItem.rename">
              <span class="preview-rename-icon">🏷️</span>
              <span class="preview-rename-text">{{ previewItem.rename }}</span>
            </div>

            <!-- 贴纸列表 -->
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

            <!-- 挂件信息 -->
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

        <!-- 移入组件按钮 - 右下角 -->
        <div class="preview-bottom-right-button">
          <el-button type="success" @click="handleMoveToComponent">移入组件</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 平台选择对话框 -->
    <PlatformSelectDialog
      v-model="platformSelectVisible"
      :item-count="selectedItems.length"
      @select="handlePlatformSelect"
      @cancel="handlePlatformSelectCancel"
    />

    <!-- 悠悠有品出租表单对话框 -->
    <el-dialog
      v-model="rentFormVisible"
      width="1000px"
      :show-header="false"
      :close-on-click-modal="false"
      class="rent-form-dialog"
      @closed="handleRentFormClosed"
    >
      <RentFormYYYP
        :items="formattedSelectedItems"
        :initData="rentInitData"
        @cancel="rentFormVisible = false"
        @submit="handleRentFormSubmit"
      />
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick, watch, h } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { ArrowDown, Loading, Close, Star, Box, Upload, InfoFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import { API_CONFIG, apiUrls } from '@/config/api.js'
import PlatformSelectDialog from './Inventory/PlatformSelectDialog.vue'
import RentFormYYYP from './Inventory/RentFormYYYP.vue'

export default {
  name: 'Inventory',
  components: {
    PlatformSelectDialog,
    RentFormYYYP
  },
  setup() {
    const loading = ref(false)
    const fetchingInventory = ref(false) // 获取库存中
    const fetchingYYYPPrice = ref(false) // 获取悠悠有品价格中
    const fetchingBuffPrice = ref(false) // 获取BUFF价格中
    const inventoryData = ref([])
    const searchText = ref('')
    const weaponTypeFilter = ref('')
    const floatRangeFilter = ref('')
    const pendantFilter = ref('')
    const stickerFilter = ref('')
    const renameFilter = ref('')
    const tradeRestrictionFilter = ref('')
    const displayMode = ref('card') // 默认卡片显示
    const groupMode = ref(true) // 组合模式开关，默认开启
    const groupedData = ref([]) // 组合后的数据
    const tableRef = ref(null) // 表格引用
    const expandedRowPages = ref({}) // 展开行的分页状态 { assetid: currentPage }
    const showPriceDiff = ref(true) // 是否显示差价（true=差价，false=价格）
    const editingAssetId = ref(null) // 正在编辑的资产ID
    const editingPrice = ref('') // 编辑中的价格
    const originalPrice = ref('') // 原始价格
    // 懒加载相关
    const pageSize = ref(50) // 每页加载数量
    const currentOffset = ref(0) // 当前偏移量
    const hasMore = ref(true) // 是否还有更多数据
    const loadingMore = ref(false) // 是否正在加载更多
    // 图片404缓存，避免重复请求
    const image404Cache = ref(new Set())
    const statsData = ref({
      total_count: 0,
      by_type: [],
      by_wear: [],
      price_stats: {
        priced_count: 0,
        total_price: 0,
        avg_price: 0,
        min_price: 0,
        max_price: 0
      }
    })
    const steamIdList = ref([])
    const selectedSteamId = ref('')
    const sortConfig = ref({ prop: 'item_count', order: 'desc' }) // 默认按数量降序排序（组合模式）

    // 预览弹窗相关
    const previewVisible = ref(false)
    const previewItem = ref(null)

    // 多选模式相关
    const isMultiSelectMode = ref(true) // 默认开启多选模式
    const selectedItems = ref([])
    
    // 组件选择对话框相关
    const itemsToDeposit = ref([])
    const isSelectingComponent = ref(false) // 是否处于选择组件模式
    
    // 备注弹窗相关
    const remarkDialogVisible = ref(false)
    const currentRemarkIndex = ref(-1)
    const currentRemark = ref('')
    
    // 打开备注弹窗
    const openRemarkDialog = (index) => {
      currentRemarkIndex.value = index
      currentRemark.value = itemForms.value[index].remark || ''
      remarkDialogVisible.value = true
    }
    
    // 保存备注
    const saveRemark = () => {
      if (isGroupedView.value) {
        // 组合模式下保存组合备注
        saveGroupRemark()
      } else {
        // 非组合模式下保存单个物品备注
        if (currentRemarkIndex.value >= 0) {
          itemForms.value[currentRemarkIndex.value].remark = currentRemark.value
        }
        remarkDialogVisible.value = false
      }
    }
    
    // 出售/出租弹窗相关
    const sellRentDialogVisible = ref(false)
    const sellRentDialogTitle = ref('')
    const sellRentDialogType = ref('') // 'sell' 或 'rent'
    const submitting = ref(false)
    const isGroupedView = ref(false) // 是否组合显示
    const expandedGroups = ref({}) // 记录哪些组是展开的

    // 出租相关状态
    const platformSelectVisible = ref(false) // 平台选择对话框
    const rentFormVisible = ref(false) // 出租表单对话框
    const selectedRentPlatform = ref('') // 选中的出租平台
    const rentInitData = ref(null) // 出租 init 数据
    
    // 每个物品的表单数据
    const itemForms = ref([])
    const itemFormRefs = ref([])
    
    // 组合模式下的表单数据（按classid）
    const groupForms = ref({})
    const groupFormRefs = ref({})
    
    // 单个物品表单验证规则
    const itemFormRules = {
      price: [
        { required: true, message: '请输入价格', trigger: 'blur' },
        { 
          pattern: /^\d+(\.\d{1,2})?$/, 
          message: '价格格式不正确', 
          trigger: 'blur' 
        }
      ]
    }
    
    // 切换组合显示
    const toggleGroupedView = () => {
      isGroupedView.value = !isGroupedView.value
      if (isGroupedView.value) {
        // 切换到组合模式时，初始化组合表单
        initGroupForms()
        // 清空展开状态
        expandedGroups.value = {}
      } else {
        // 切换回非组合模式时，重新初始化物品表单
        initItemForms()
      }
    }
    
    // 切换组的展开/折叠状态
    const toggleGroupExpand = (classid) => {
      expandedGroups.value[classid] = !expandedGroups.value[classid]
    }
    
    // 初始化组合表单
    const initGroupForms = () => {
      groupForms.value = {}
      groupFormRefs.value = {}
      
      // 按classid分组并初始化表单（不自动填充价格）
      const groupMap = new Map()
      
      selectedItems.value.forEach(item => {
        const classid = item.classid || `unknown_${item.assetid}`
        
        if (!groupMap.has(classid)) {
          groupMap.set(classid, {
            price: '',
            remark: ''
          })
        }
      })
      
      groupForms.value = Object.fromEntries(groupMap)
    }
    
    // 自动填充组合价格（使用悠悠底价-0.01）
    const autoFillGroupPrices = () => {
      const groupMap = new Map()
      let filledCount = 0
      let noDataCount = 0
      
      selectedItems.value.forEach(item => {
        const classid = item.classid || `unknown_${item.assetid}`
        
        if (!groupMap.has(classid)) {
          // 获取该组第一个物品的悠悠底价
          const groupItems = selectedItems.value.filter(i => 
            (i.classid || `unknown_${i.assetid}`) === classid
          )
          
          // 使用第一个物品的悠悠底价
          const firstItem = groupItems[0]
          const yyypPrice = yyypRealtimePrices.value[firstItem.assetid]
          
          let price = ''
          if (yyypPrice && !yyypPrice.loading && !yyypPrice.error && yyypPrice.lowest_price) {
            // 底价减0.01
            const lowestPrice = parseFloat(yyypPrice.lowest_price)
            const fillPrice = Math.max(0.01, lowestPrice - 0.01)
            price = fillPrice.toFixed(2)
          }
          
          groupMap.set(classid, price)
        }
      })
      
      // 填充价格到表单
      groupMap.forEach((price, classid) => {
        if (groupForms.value[classid]) {
          if (price) {
            groupForms.value[classid].price = price
            filledCount++
          } else {
            noDataCount++
          }
        }
      })
      
      if (filledCount > 0) {
        ElMessage.success(`已自动填充 ${filledCount} 组的价格（底价-0.01）`)
      } else if (noDataCount > 0) {
        ElMessage.warning('没有可用的悠悠底价数据，请先查询底价')
      } else {
        ElMessage.warning('没有可填充的价格')
      }
    }
    
    // 自动填充非组合模式的价格（使用悠悠底价-0.01）
    const autoFillItemPrices = () => {
      let filledCount = 0
      let noDataCount = 0
      
      selectedItems.value.forEach((item, index) => {
        const yyypPrice = yyypRealtimePrices.value[item.assetid]
        
        if (yyypPrice && !yyypPrice.loading && !yyypPrice.error && yyypPrice.lowest_price) {
          if (itemForms.value[index]) {
            // 底价减0.01
            const lowestPrice = parseFloat(yyypPrice.lowest_price)
            const fillPrice = Math.max(0.01, lowestPrice - 0.01)
            itemForms.value[index].price = fillPrice.toFixed(2)
            filledCount++
          }
        } else {
          noDataCount++
        }
      })
      
      if (filledCount > 0) {
        ElMessage.success(`已自动填充 ${filledCount} 件物品的价格（底价-0.01）`)
      } else if (noDataCount > 0) {
        ElMessage.warning('没有可用的悠悠底价数据，请先查询底价')
      } else {
        ElMessage.warning('没有可填充的价格')
      }
    }
    
    // 验证组合表单的价格输入
    const validateGroupPrice = (classid) => {
      if (!groupForms.value[classid]) return
      
      const value = groupForms.value[classid].price
      let newValue = value.replace(/[^\d.]/g, '')
      
      const parts = newValue.split('.')
      if (parts.length > 2) {
        newValue = parts[0] + '.' + parts.slice(1).join('')
      }
      
      if (parts.length === 2 && parts[1].length > 2) {
        newValue = parts[0] + '.' + parts[1].substring(0, 2)
      }
      
      groupForms.value[classid].price = newValue
    }
    
    // 打开组合备注弹窗
    const openGroupRemarkDialog = (classid) => {
      currentRemarkIndex.value = classid
      currentRemark.value = groupForms.value[classid]?.remark || ''
      remarkDialogVisible.value = true
    }
    
    // 保存组合备注
    const saveGroupRemark = () => {
      if (currentRemarkIndex.value && groupForms.value[currentRemarkIndex.value]) {
        groupForms.value[currentRemarkIndex.value].remark = currentRemark.value
      }
      remarkDialogVisible.value = false
    }
    
    // 按 classid 分组物品
    const groupedItems = computed(() => {
      if (!isGroupedView.value) {
        return []
      }
      
      const groupMap = new Map()
      
      selectedItems.value.forEach((item, index) => {
        const classid = item.classid || `unknown_${item.assetid}`
        
        if (!groupMap.has(classid)) {
          groupMap.set(classid, {
            classid: classid,
            items: [],
            itemName: item.item_name,
            steamHashName: item.steam_hash_name,
            weaponType: item.weapon_type
          })
        }
        
        groupMap.get(classid).items.push({
          ...item,
          originalIndex: index
        })
      })
      
      // 转换为数组并按物品数量降序排序
      return Array.from(groupMap.values()).sort((a, b) => b.items.length - a.items.length)
    })

    // 计算组的平均购入价格
    const getGroupAveragePrice = (group) => {
      if (!group || !group.items || group.items.length === 0) {
        return null
      }
      
      const validPrices = group.items
        .map(item => parseFloat(item.buy_price))
        .filter(price => !isNaN(price) && price > 0)
      
      if (validPrices.length === 0) {
        return null
      }
      
      const sum = validPrices.reduce((acc, price) => acc + price, 0)
      const avg = sum / validPrices.length
      return avg.toFixed(2)
    }
    
    // 获取组的价格范围
    const getGroupPriceRange = (group) => {
      if (!group || !group.items || group.items.length === 0) {
        return null
      }
      
      const validPrices = group.items
        .map(item => parseFloat(item.buy_price))
        .filter(price => !isNaN(price) && price > 0)
      
      if (validPrices.length === 0) {
        return null
      }
      
      const min = Math.min(...validPrices)
      const max = Math.max(...validPrices)
      
      if (min === max) {
        return `¥${min.toFixed(2)}`
      }
      
      return `¥${min.toFixed(2)} - ¥${max.toFixed(2)}`
    }
    
    // 获取组的磨损范围
    const getGroupFloatRange = (group) => {
      if (!group || !group.items || group.items.length === 0) {
        return null
      }
      
      const validFloats = group.items
        .map(item => parseFloat(item.weapon_float))
        .filter(f => !isNaN(f) && f > 0)
      
      if (validFloats.length === 0) {
        return null
      }
      
      const min = Math.min(...validFloats)
      const max = Math.max(...validFloats)
      
      if (min === max) {
        return min.toFixed(8)
      }
      
      return `${min.toFixed(8)} - ${max.toFixed(8)}`
    }

    // 懒加载图片观察器
    let imageObserver = null

    // API 基础地址
    const API_BASE = `${API_CONFIG.BASE_URL}/webInventoryV1`
    const API_GROUPED = `${API_CONFIG.BASE_URL}/webInventoryV1/inventory/grouped`
    const CONFIG_API = `${API_CONFIG.BASE_URL}/configV1`

    const loadSteamIdList = async () => {
      try {
        const response = await axios.get(`${API_BASE}/steam_ids`)
        console.log('Steam ID列表响应:', response.data)
        if (response.data.success) {
          steamIdList.value = response.data.data
          if (steamIdList.value.length > 0) {
            // 默认选择第一个 - 使用新格式 steamID（大写）
            selectedSteamId.value = steamIdList.value[0].steamID
            console.log('默认选择Steam ID:', selectedSteamId.value)
          } else {
            ElMessage.warning('没有找到库存数据，请先获取Steam库存')
          }
        }
      } catch (error) {
        console.error('加载Steam ID列表失败:', error)
        ElMessage.error('加载Steam ID列表失败: ' + (error.response?.data?.error || error.message))
      }
    }

    const loadInventoryData = async (reset = true) => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请选择Steam账号')
        return
      }
      
      // 如果是列表模式且开启组合模式，调用组合数据加载
      if (displayMode.value === 'list' && groupMode.value) {
        return await loadGroupedData(reset)
      }
      
      // 如果是重置加载，清空数据和分页状态
      if (reset) {
        inventoryData.value = []
        currentOffset.value = 0
        hasMore.value = true
      }
      
      loading.value = true
      try {
        console.log('正在加载库存数据，Steam ID:', selectedSteamId.value)
        // 加载卡片数据 - 使用分页
        const params = {
          weapon_type: weaponTypeFilter.value,
          float_range: floatRangeFilter.value,
          // 添加前端筛选条件
          pendant_filter: pendantFilter.value,
          sticker_filter: stickerFilter.value,
          rename_filter: renameFilter.value,
          trade_restriction_filter: tradeRestrictionFilter.value,
          limit: pageSize.value,
          offset: currentOffset.value
        }

        // 如果处于选择组件模式，只显示库存组件，并忽略搜索过滤
        if (isSelectingComponent.value) {
          params.classid = '3604678661'
        } else {
          // 只在非选择组件模式下应用搜索过滤
          params.search = searchText.value
        }
        
        const url = `${API_BASE}/inventory/${selectedSteamId.value}`
        console.log('请求URL:', url, '参数:', params)
        const response = await axios.get(url, { params })
        console.log('数据响应:', response.data)
        if (response.data.success) {
          const newData = response.data.data || []
          
          // 如果是重置，直接替换数据；否则追加数据
          if (reset) {
            inventoryData.value = newData
          } else {
            inventoryData.value = [...inventoryData.value, ...newData]
          }
          
          // 检查是否还有更多数据
          hasMore.value = newData.length === pageSize.value
          
          // 更新偏移量
          currentOffset.value += newData.length
          
          // 应用排序（包括默认排序）
          if (sortConfig.value.prop && sortConfig.value.order) {
            applySorting()
          }
          
          console.log('数据已加载，当前:', inventoryData.value.length, '条，还有更多:', hasMore.value, '排序:', sortConfig.value)
        } else {
          ElMessage.error(response.data.error || '加载数据失败')
        }
        
        // 加载统计数据（只在重置时加载，避免频繁请求）
        if (reset) {
          await loadStats()
        }
      } catch (error) {
        console.error('加载库存数据失败:', error)
        ElMessage.error('加载数据失败: ' + (error.response?.data?.error || error.message))
      } finally {
        loading.value = false
      }
    }

    // 加载组合数据
    const loadGroupedData = async (reset = true) => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请选择Steam账号')
        return
      }

      // 如果是重置加载，清空数据和分页状态
      if (reset) {
        groupedData.value = []
        currentOffset.value = 0
        hasMore.value = true
      }

      loading.value = true
      try {
        console.log('正在加载组合库存数据，Steam ID:', selectedSteamId.value)
        const params = {
          search: searchText.value,
          weapon_type: weaponTypeFilter.value,
          float_range: floatRangeFilter.value,
          // 添加前端筛选条件
          pendant_filter: pendantFilter.value,
          sticker_filter: stickerFilter.value,
          rename_filter: renameFilter.value,
          trade_restriction_filter: tradeRestrictionFilter.value,
          limit: pageSize.value,
          offset: currentOffset.value
        }

        const response = await axios.get(`${API_GROUPED}/${selectedSteamId.value}`, { params })
        console.log('组合数据响应:', response.data)

        if (response.data.success) {
          const newData = (response.data.data || []).map(item => ({
            ...item,
            // 为了兼容现有的显示逻辑，添加必要的字段
            assetid: item.item_name || Math.random().toString(36).slice(2),
            item_count: item.count || 0,
            // 计算总价格（如果有多个物品）
            buy_price: item.buy_prices && item.buy_prices.length > 0 
              ? item.buy_prices.reduce((sum, price) => sum + (parseFloat(price) || 0), 0).toFixed(2)
              : '0.00',
            yyyp_price: item.yyyp_prices && item.yyyp_prices.length > 0
              ? item.yyyp_prices.reduce((sum, price) => sum + (parseFloat(price) || 0), 0).toFixed(2)
              : '0.00',
            buff_price: item.buff_prices && item.buff_prices.length > 0
              ? item.buff_prices.reduce((sum, price) => sum + (parseFloat(price) || 0), 0).toFixed(2)
              : '0.00',
            steam_price: item.steam_prices && item.steam_prices.length > 0
              ? item.steam_prices.reduce((sum, price) => sum + (parseFloat(price) || 0), 0).toFixed(2)
              : '0.00',
            // 使用第一个物品的磨损值作为代表
            weapon_float: item.weapon_floats && item.weapon_floats.length > 0 ? item.weapon_floats[0] : null
            // steam_hash_name 直接使用后端返回的值，不需要重新生成
          }))

          // 如果是重置，直接替换数据；否则追加数据
          if (reset) {
            groupedData.value = newData
          } else {
            groupedData.value = [...groupedData.value, ...newData]
          }

          // 检查是否还有更多数据
          hasMore.value = newData.length === pageSize.value

          // 更新偏移量
          currentOffset.value += newData.length

          // 应用排序（包括默认排序）
          if (sortConfig.value.prop && sortConfig.value.order) {
            applySorting()
          }

          console.log('组合数据已加载，当前:', groupedData.value.length, '条，还有更多:', hasMore.value, '排序:', sortConfig.value)
        } else {
          ElMessage.error(response.data.error || '加载组合数据失败')
        }

        // 加载统计数据（只在重置时加载）
        if (reset) {
          await loadStats()
        }
      } catch (error) {
        console.error('加载组合数据失败:', error)
        ElMessage.error('加载组合数据失败: ' + (error.response?.data?.error || error.message))
      } finally {
        loading.value = false
      }
    }

    // 加载更多数据
    const loadMoreData = async () => {
      if (loadingMore.value || !hasMore.value) {
        return
      }
      
      loadingMore.value = true
      try {
        await loadInventoryData(false)
      } finally {
        loadingMore.value = false
      }
    }

    // 设置懒加载图片观察器
    const setupLazyImageObserver = () => {
      nextTick(() => {
        // 清理旧的观察器
        if (imageObserver) {
          imageObserver.disconnect()
        }

        // 创建新的观察器
        imageObserver = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            const img = entry.target
            
            if (entry.isIntersecting) {
              // 图片进入视口，加载图片
              const src = img.getAttribute('data-src')
              if (src && !img.src) {
                img.src = src
                img.classList.add('loaded')
              }
            } else {
              // 图片离开视口，释放内存
              if (img.src && img.classList.contains('loaded')) {
                // 保存 data-src 以便重新加载
                if (!img.getAttribute('data-src')) {
                  img.setAttribute('data-src', img.src)
                }
                // 清空 src 释放内存
                img.removeAttribute('src')
                img.classList.remove('loaded')
              }
            }
          })
        }, {
          root: null, // 使用视口作为根
          rootMargin: '200px', // 提前200px开始加载
          threshold: 0.01
        })

        // 观察所有懒加载图片
        const lazyImages = document.querySelectorAll('.lazy-image')
        lazyImages.forEach(img => {
          imageObserver.observe(img)
        })
      })
    }

    // 设置滚动监听（使用 Intersection Observer）
    const setupScrollObserver = () => {
      nextTick(() => {
        const triggerId = displayMode.value === 'card' ? 'load-more-trigger-card' : 'load-more-trigger'
        const trigger = document.getElementById(triggerId)
        if (trigger) {
          // 如果已有观察器，先断开
          if (trigger._observer) {
            trigger._observer.disconnect()
          }
          
          // 找到滚动容器
          let scrollContainer = null
          if (displayMode.value === 'card') {
            scrollContainer = trigger.closest('.card-container')
          } else {
            // 对于 el-table，找到表格的滚动容器
            const tableWrapper = trigger.closest('.table-container')
            if (tableWrapper) {
              scrollContainer = tableWrapper.querySelector('.el-table__body-wrapper')
            }
          }
          
            const observer = new IntersectionObserver((entries) => {
              entries.forEach(entry => {
                if (entry.isIntersecting && hasMore.value && !loadingMore.value && !loading.value) {
                  loadMoreData()
                }
              })
            }, {
            root: scrollContainer,
            rootMargin: '100px'
          })
          
          observer.observe(trigger)
          trigger._observer = observer
        }

        // 设置懒加载图片观察器
        setupLazyImageObserver()
      })
    }

    const loadStats = async () => {
      try {
        // 构建查询参数（包含所有筛选条件）
        const params = {
          weapon_type: weaponTypeFilter.value,
          float_range: floatRangeFilter.value,
          // 添加前端筛选条件
          pendant_filter: pendantFilter.value,
          sticker_filter: stickerFilter.value,
          rename_filter: renameFilter.value,
          trade_restriction_filter: tradeRestrictionFilter.value
        }

        // 如果处于选择组件模式，只统计库存组件
        if (isSelectingComponent.value) {
          params.classid = '3604678661'
        } else {
          // 只在非选择组件模式下应用搜索过滤
          params.search = searchText.value
        }

        const response = await axios.get(`${API_BASE}/inventory/stats/${selectedSteamId.value}`, { params })
        console.log('统计数据响应:', response.data)
        if (response.data.success) {
          statsData.value = response.data.data
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }

    const handleSteamIdChange = () => {
      console.log('Steam ID已切换:', selectedSteamId.value)
      loadInventoryData(true) // 重置加载
    }

    const handleFilterChange = () => {
      console.log('筛选条件已变更')
      loadInventoryData(true) // 重置加载数据和统计
    }

    const handleReset = () => {
      searchText.value = ''
      weaponTypeFilter.value = ''
      floatRangeFilter.value = ''
      pendantFilter.value = ''
      stickerFilter.value = ''
      renameFilter.value = ''
      tradeRestrictionFilter.value = ''
      sortConfig.value = { prop: '', order: '' }
      loadInventoryData(true) // 重置加载
    }

    // 切换组合模式
    const handleToggleGroupMode = (val = null) => {
      // 只在列表模式下才允许切换组合模式
      if (displayMode.value !== 'list') {
        return
      }
      
      // 按钮直接传 true，开关传布尔值，默认取反
      if (val === true || val === false) {
        groupMode.value = val
      } else {
        groupMode.value = !groupMode.value
      }
      
      // 清空展开行的分页状态
      expandedRowPages.value = {}
      
      // 切换到组合模式时，设置默认排序为数量降序
      if (groupMode.value) {
        sortConfig.value = { prop: 'item_count', order: 'desc' }
      } else {
        // 切换回明细模式时，恢复默认排序
        sortConfig.value = { prop: 'buy_price', order: 'desc' }
      }
      
      // 重置加载数据
      loadInventoryData(true)
    }

    // 监听显示模式变化，切换到卡片模式时关闭组合模式
    watch(displayMode, (newMode, oldMode) => {
      if (newMode === 'card' && groupMode.value) {
        // 切换到卡片模式，关闭组合模式
        groupMode.value = false
        sortConfig.value = { prop: 'buy_price', order: 'desc' }
        loadInventoryData(true)
      } else if (newMode === 'list' && oldMode === 'card') {
        // 从卡片模式切换回列表模式，恢复组合模式
        groupMode.value = true
        sortConfig.value = { prop: 'item_count', order: 'desc' }
        loadInventoryData(true)
      }
    })

    // 计算每页显示的卡片数量（基于300px卡片宽度和容器宽度）
    const getItemsPerPage = () => {
      // 假设容器宽度约为1200px（可以根据实际情况调整）
      // 每个卡片300px，加上间隙，大约每行3-4个
      // 4行 x 3个 = 12个卡片
      return 12
    }

    // 获取展开行的详细数据（带分页）
    const getExpandedItems = (row) => {
      if (!row.assetids || !Array.isArray(row.assetids)) {
        return []
      }

      // 将组合数据转换为详细列表
      const allItems = row.assetids.map((assetid, index) => ({
        assetid: assetid,
        weapon_float: row.weapon_floats && row.weapon_floats[index] ? row.weapon_floats[index] : null,
        buy_price: row.buy_prices && row.buy_prices[index] ? row.buy_prices[index] : '0',
        yyyp_price: row.yyyp_prices && row.yyyp_prices[index] ? row.yyyp_prices[index] : '0',
        buff_price: row.buff_prices && row.buff_prices[index] ? row.buff_prices[index] : '0',
        steam_price: row.steam_prices && row.steam_prices[index] ? row.steam_prices[index] : '0',
        order_time: row.order_times && row.order_times[index] ? row.order_times[index] : null,
        remark: row.remarks && row.remarks[index] ? row.remarks[index] : null,
        // 添加印花、挂件、改名等字段
        sticker: row.stickers && row.stickers[index] ? row.stickers[index] : null,
        pendant: row.pendants && row.pendants[index] ? row.pendants[index] : null,
        rename: row.renames && row.renames[index] ? row.renames[index] : null,
        // 添加用于预览的字段
        steam_hash_name: row.steam_hash_name,
        item_name: row.item_name,
        weapon_name: row.weapon_name,
        weapon_type: row.weapon_type,
        float_range: row.float_range
      }))

      // 获取当前页码，确保页码有效
      const currentPage = expandedRowPages.value[row.assetid] || 1
      const itemsPerPage = getItemsPerPage()
      const totalPages = Math.ceil(allItems.length / itemsPerPage)
      
      console.log('获取展开数据:', {
        assetid: row.assetid,
        currentPage,
        itemsPerPage,
        totalPages,
        totalItems: allItems.length
      })
      
      // 如果当前页码超出范围，重置为第1页
      if (currentPage > totalPages && totalPages > 0) {
        expandedRowPages.value = {
          ...expandedRowPages.value,
          [row.assetid]: 1
        }
        const start = 0
        const end = itemsPerPage
        return allItems.slice(start, end)
      }
      
      const start = (currentPage - 1) * itemsPerPage
      const end = start + itemsPerPage

      console.log('分页范围:', { start, end, 返回数量: allItems.slice(start, end).length })
      
      return allItems.slice(start, end)
    }

    // 获取展开行的总数据量
    const getExpandedTotal = (row) => {
      if (!row.assetids || !Array.isArray(row.assetids)) {
        return 0
      }
      return row.assetids.length
    }

    // 处理展开行的分页变化
    const handleExpandPageChange = (row, page) => {
      console.log('分页变化:', row.assetid, '页码:', page)
      
      // 先更新页码
      expandedRowPages.value = {
        ...expandedRowPages.value,
        [row.assetid]: page
      }
      
      // 如果行未展开，先展开它
      if (tableRef.value) {
        const expandedRows = tableRef.value.store.states.expandRows.value || []
        const isExpanded = expandedRows.some(r => r.assetid === row.assetid)
        
        if (!isExpanded) {
          console.log('行未展开，自动展开:', row.assetid)
          tableRef.value.toggleRowExpansion(row, true)
        }
      }
    }

    // 处理行点击事件（仅在组合模式下）
    const handleRowClick = (row, column, event) => {
      if (!groupMode.value) return
      if (row.item_count <= 1) return // 只有1件物品不展开
      
      // 切换展开状态
      if (tableRef.value) {
        tableRef.value.toggleRowExpansion(row)
      }
    }

    // 获取行样式
    const getRowStyle = (data) => {
      const style = { backgroundColor: 'transparent' }
      // 在组合模式下，如果数量大于1，添加可点击样式
      if (groupMode.value && data.row.item_count > 1) {
        style.cursor = 'pointer'
      }
      return style
    }


    // 统一的排序函数
    const applySorting = () => {
      if (!sortConfig.value.prop || !sortConfig.value.order) return
      
      const { prop, order } = sortConfig.value
      
      // 根据当前模式选择要排序的数据
      const dataToSort = groupMode.value ? groupedData.value : inventoryData.value
      
      dataToSort.sort((a, b) => {
        // 特殊处理：库存存储组件始终排在最后
        const isStorageA = a.item_name === '库存存储组件' || a.steam_hash_name === '库存存储组件'
        const isStorageB = b.item_name === '库存存储组件' || b.steam_hash_name === '库存存储组件'
        
        if (isStorageA && !isStorageB) return 1  // A是存储组件，排在后面
        if (!isStorageA && isStorageB) return -1 // B是存储组件，排在后面
        if (isStorageA && isStorageB) return 0   // 都是存储组件，保持相对位置
        
        let valueA, valueB
        
        if (prop === 'buy_price') {
          // 价格排序
          valueA = parseFloat(a.buy_price) || 0
          valueB = parseFloat(b.buy_price) || 0
        } else if (prop === 'yyyp_price') {
          // 悠悠有品价格排序
          valueA = parseFloat(a.yyyp_price) || 0
          valueB = parseFloat(b.yyyp_price) || 0
        } else if (prop === 'buff_price') {
          // BUFF价格排序
          valueA = parseFloat(a.buff_price) || 0
          valueB = parseFloat(b.buff_price) || 0
        } else if (prop === 'steam_price') {
          // Steam价格排序
          valueA = parseFloat(a.steam_price) || 0
          valueB = parseFloat(b.steam_price) || 0
        } else if (prop === 'order_time') {
          // 入库时间排序
          valueA = a.order_time ? new Date(a.order_time).getTime() : 0
          valueB = b.order_time ? new Date(b.order_time).getTime() : 0
        } else if (prop === 'weapon_float') {
          // 磨损值排序
          valueA = parseFloat(a.weapon_float) || 999999 // 没有磨损值的排在最后
          valueB = parseFloat(b.weapon_float) || 999999
        } else if (prop === 'float_range') {
          // 磨损等级排序（按照游戏内的品质顺序）
          const floatRangeOrder = {
            '崭新出厂': 1,
            '略有磨损': 2,
            '久经沙场': 3,
            '破损不堪': 4,
            '战痕累累': 5
          }
          valueA = floatRangeOrder[a.float_range] || 999
          valueB = floatRangeOrder[b.float_range] || 999
        } else if (prop === 'item_count') {
          // 数量排序（仅组合模式）
          valueA = parseInt(a.item_count) || 0
          valueB = parseInt(b.item_count) || 0
        } else if (prop === 'remark') {
          // 备注排序（有备注的在前，无备注的在后）
          valueA = a.remark ? 0 : 1
          valueB = b.remark ? 0 : 1
        }
        
        if (order === 'asc') {
          return valueA - valueB
        } else {
          return valueB - valueA
        }
      })
    }

    // Element Plus 表格的排序事件处理
    const handleSortChange = ({ prop, order }) => {
      console.log('排序改变:', prop, order)
      
      if (!order) {
        // 取消排序
        sortConfig.value = { prop: '', order: '' }
        loadInventoryData(true)
        return
      }
      
      // 设置排序配置
      sortConfig.value = { 
        prop, 
        order: order === 'ascending' ? 'asc' : 'desc' 
      }
      
      // 应用排序
      applySorting()
    }


    // 开始编辑价格
    const startEdit = (row) => {
      editingAssetId.value = row.assetid
      originalPrice.value = row.buy_price || ''
      editingPrice.value = row.buy_price || ''
      
      // 使用nextTick确保input已渲染后聚焦
      nextTick(() => {
        const input = document.getElementById(`price-input-${row.assetid}`)
        if (input) {
          input.focus()
          input.select() // 选中所有文本，方便修改
        }
      })
    }

    // 取消编辑
    const cancelEdit = () => {
      editingAssetId.value = null
      editingPrice.value = ''
      originalPrice.value = ''
    }

    // 完成编辑价格
    const finishEdit = async (row) => {
      const newPrice = editingPrice.value
      const oldPrice = originalPrice.value
      
      // 如果价格没有改变，直接取消编辑
      if (newPrice === oldPrice) {
        cancelEdit()
        return
      }
      
      // 如果价格为空，提示用户
      if (!newPrice || newPrice.trim() === '') {
        ElMessage.warning('请输入有效的价格')
        return
      }
      
      // 先更新UI（乐观更新）
      row.buy_price = newPrice
      const currentAssetId = editingAssetId.value
      cancelEdit()
      
      // 异步发送请求到后端
      try {
        const response = await axios.put(
          `${API_CONFIG.BASE_URL}/webInventoryV1/inventory/buy_price/${selectedSteamId.value}/${currentAssetId}`,
          { buy_price: newPrice }
        )
        
        if (response.data.success) {
          ElMessage.success('价格更新成功')
          // 只更新统计数据，不重新加载整个列表
          await loadInventoryStats()
        } else {
          // 如果失败，恢复原价格
          row.buy_price = oldPrice
          ElMessage.error('价格更新失败: ' + response.data.error)
        }
      } catch (error) {
        // 如果失败，恢复原价格
        row.buy_price = oldPrice
        console.error('更新价格失败:', error)
        ElMessage.error('更新价格失败: ' + error.message)
      }
    }

    // 生成标题（卡片/列表复用），若 weapon_name 与 item_name 相同则只显示一次
    const getCardTitle = (item) => {
      const weaponName = (item.weapon_name || '').trim()
      const itemName = (item.item_name || '').trim()
      const parts = []

      if (weaponName && itemName) {
        if (weaponName === itemName) {
          parts.push(itemName)
        } else {
          parts.push(weaponName)
          parts.push(itemName)
        }
      } else if (weaponName) {
        parts.push(weaponName)
      } else if (itemName) {
        parts.push(itemName)
      }

      let title = parts.join(' | ')
      if (item.float_range) {
        title += ` （${item.float_range}）`
      }
      return title
    }

    const getItemTitle = (item) => getCardTitle(item)

    // 检查是否有额外信息（印花、挂件、改名）
    const hasExtras = (item) => {
      return !!(item.sticker || item.pendant || item.rename)
    }

    // 获取武器图片路径
    const getWeaponImage = (steamHashName) => {
      if (!steamHashName) {
        return null // 如果没有steam_hash_name，返回null，不显示图片
      }
      // 检查是否已经在404缓存中
      if (image404Cache.value.has(steamHashName)) {
        return null // 如果之前404过，直接返回null，不显示图片
      }
      // 将空格和竖线分别替换为下划线，并添加.png扩展名
      // 例如: "AK-47 | Neon Revolution (Factory New)" -> "AK-47___Neon_Revolution_(Factory_New).png"
      const imageName = steamHashName
        .replace(/\s*\|\s*/g, '___')  // " | " -> "___" (竖线及其两侧空格替换为三个下划线)
        .replace(/\s/g, '_')          // 剩余所有空格 -> "_"
        + '.png'

      return apiUrls.weaponImage(imageName)
    }

    // 处理图片加载错误
    const handleImageError = (event, steamHashName) => {
      // 将失败的steam_hash_name添加到404缓存中
      if (steamHashName) {
        image404Cache.value.add(steamHashName)
      }
      
      // 移除错误监听器，防止重复触发
      event.target.onerror = null
      
      // 隐藏图片，不设置data URI，避免将图片数据加载到内存
      event.target.style.display = 'none'
    }

    // 获取价格差异样式类
    const getPriceDiffClass = (marketPrice, buyPrice) => {
      if (!marketPrice || !buyPrice) return ''
      const diff = parseFloat(marketPrice) - parseFloat(buyPrice)
      return diff >= 0 ? 'price-profit' : 'price-loss'
    }

    // 切换显示模式
    const toggleDisplayMode = () => {
      displayMode.value = displayMode.value === 'list' ? 'card' : 'list'
    }
    
    // 切换多选模式
    const toggleMultiSelectMode = () => {
      isMultiSelectMode.value = !isMultiSelectMode.value
      if (!isMultiSelectMode.value) {
        // 退出多选模式时清空选择
        selectedItems.value = []
      }
    }
    
    // 判断物品是否有交易限制
    const hasTradeRestriction = (item) => {
      if (!item.remark) return false
      
      const lockDate = parseTradeLockDate(item.remark)
      // 如果有交易限制且未过期，返回true
      return lockDate && !lockDate.expired
    }
    
    // 判断物品是否被选中
    const isItemSelected = (assetid) => {
      return selectedItems.value.some(item => item.assetid === assetid)
    }
    
    // 切换物品选中状态
    const toggleItemSelection = (item) => {
      // 检查是否有交易限制
      if (hasTradeRestriction(item)) {
        ElMessage.warning('无法交易')
        return
      }
      
      const index = selectedItems.value.findIndex(i => i.assetid === item.assetid)
      if (index > -1) {
        selectedItems.value.splice(index, 1)
      } else {
        selectedItems.value.push(item)
      }
    }
    
    // 清空选择
    const clearSelection = () => {
      selectedItems.value = []
    }
    
    // 全选当前显示的物品
    const selectAllDisplayed = () => {
      // 获取当前显示的数据
      const displayData = currentDisplayData.value
      
      let addedCount = 0
      let skippedCount = 0
      
      // 遍历当前显示的物品，添加到选中列表（排除已有交易限制的）
      displayData.forEach(item => {
        // 检查是否有交易限制
        if (hasTradeRestriction(item)) {
          skippedCount++
          return
        }
        
        // 检查是否已经在选中列表中
        const alreadySelected = selectedItems.value.some(i => i.assetid === item.assetid)
        if (!alreadySelected) {
          selectedItems.value.push(item)
          addedCount++
        }
      })
      
      let message = `已选择 ${selectedItems.value.length} 件物品`
      if (skippedCount > 0) {
        message += `，已跳过 ${skippedCount} 件有交易限制的物品`
      }
      ElMessage.success(message)
    }
    
    // 处理卡片点击
    const handleCardClick = async (item) => {
      // 如果处于选择组件模式
      if (isSelectingComponent.value) {
        // 检查组件是否已满（weapon_float存储的是已存储数量）
        const storedCount = parseFloat(item.weapon_float) || 0
        if (storedCount >= 1000) {
          ElMessage.warning('该组件已满，无法继续存入物品')
          return
        }
        
        // 确认存入
        try {
          await ElMessageBox.confirm(
            `确认将 ${itemsToDeposit.value.length} 件物品存入此组件吗？`,
            '确认存入',
            {
              confirmButtonText: '确认存入',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
          
          // 执行存入
          await executeDeposit(itemsToDeposit.value, item.assetid)
          
          // 退出选择组件模式
          isSelectingComponent.value = false
          itemsToDeposit.value = []
          
          // 重新加载数据
          await loadInventoryData()
        } catch {
          // 用户取消
        }
        return
      }
      
      // 原有的卡片点击逻辑
      if (isMultiSelectMode.value) {
        // 多选模式下切换选中状态
        toggleItemSelection(item)
      } else {
        // 普通模式下打开预览
        openPreview(item)
      }
    }
    
    // 初始化物品表单
    const initItemForms = () => {
      itemForms.value = selectedItems.value.map(() => ({
        price: '',
        remark: '',
        uploadStatus: null,  // 上架状态：null=未上架, 'uploading'=上架中, 'success'=成功, 'failed'=失败
        uploadMessage: ''     // 上架消息
      }))
      itemFormRefs.value = []
    }
    
    // 悠悠有品实时底价数据
    const yyypRealtimePrices = ref({})
    const loadingYYYPPrices = ref(false)
    
    // 查询悠悠有品实时底价
    const fetchYYYPRealtimePrice = async (item) => {
      try {
        // 通过steam_hash_name查询yyyp_id
        const response = await axios.post(
          `${API_CONFIG.BASE_URL}/webSelectWeaponV1/getYYYPLowestPrice`,
          { steamHashName: item.steam_hash_name }
        )
        
        if (response.data.success && response.data.data.yyyp_id) {
          const yyypId = response.data.data.yyyp_id
          
          // 实时查询悠悠在售底价
          const priceResponse = await axios.post(
            `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getRealTimeLowestPrice`,
            {
              yyypId: yyypId,
              steamId: selectedSteamId.value,
              includeList: false
            }
          )
          
          if (priceResponse.data.success) {
            return {
              assetid: item.assetid,
              lowest_price: priceResponse.data.data.lowest_price,
              total_count: priceResponse.data.data.total_count,
              loading: false,
              error: null
            }
          } else {
            return {
              assetid: item.assetid,
              loading: false,
              error: priceResponse.data.message
            }
          }
        } else {
          return {
            assetid: item.assetid,
            loading: false,
            error: '未找到悠悠ID'
          }
        }
      } catch (error) {
        console.error('查询悠悠底价失败:', error)
        return {
          assetid: item.assetid,
          loading: false,
          error: error.message
        }
      }
    }
    
    // 批量查询悠悠底价
    const fetchAllYYYPRealtimePrices = async () => {
      loadingYYYPPrices.value = true
      yyypRealtimePrices.value = {}
      
      // 初始化loading状态
      selectedItems.value.forEach(item => {
        yyypRealtimePrices.value[item.assetid] = {
          loading: true,
          lowest_price: null,
          total_count: null,
          error: null
        }
      })
      
      // 按 steam_hash_name 分组，避免重复查询相同饰品
      const groupedByHashName = new Map()
      selectedItems.value.forEach(item => {
        const hashName = item.steam_hash_name
        if (!groupedByHashName.has(hashName)) {
          groupedByHashName.set(hashName, [])
        }
        groupedByHashName.get(hashName).push(item)
      })
      
      console.log(`[悠悠底价查询] 共 ${selectedItems.value.length} 件物品，去重后需查询 ${groupedByHashName.size} 个饰品`)
      
      // 逐个查询唯一的饰品（避免并发过多）
      let queryCount = 0
      for (const [hashName, items] of groupedByHashName.entries()) {
        queryCount++
        console.log(`[悠悠底价查询] (${queryCount}/${groupedByHashName.size}) 查询: ${hashName} (${items.length}件)`)
        
        // 查询第一个物品（同一个hash_name的物品yyyp_id相同）
        const result = await fetchYYYPRealtimePrice(items[0])
        
        // 将查询结果应用到所有相同hash_name的物品
        items.forEach(item => {
          yyypRealtimePrices.value[item.assetid] = {
            ...result,
            assetid: item.assetid  // 保持各自的assetid
          }
        })
        
        // 添加延迟避免请求过快
        if (queryCount < groupedByHashName.size) {
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
      }
      
      console.log(`[悠悠底价查询] 查询完成，共查询 ${groupedByHashName.size} 个饰品`)
      loadingYYYPPrices.value = false
    }
    
    // 显示出售弹窗
    const showSellDialog = async () => {
      if (selectedItems.value.length === 0) {
        ElMessage.warning('请先选择要出售的物品')
        return
      }
      sellRentDialogType.value = 'sell'
      sellRentDialogTitle.value = '出售物品'
      initItemForms()
      sellRentDialogVisible.value = true
      
      // 异步查询悠悠底价
      fetchAllYYYPRealtimePrices()
    }
    
    // 显示出租弹窗 - 改为先选择平台
    const showRentDialog = () => {
      if (selectedItems.value.length === 0) {
        ElMessage.warning('请先选择要出租的物品')
        return
      }
      // 打开平台选择对话框
      platformSelectVisible.value = true
    }

    // 处理平台选择
    const handlePlatformSelect = async (platform) => {
      selectedRentPlatform.value = platform

      if (platform === 'yyyp') {
        // 显示加载提示
        const loading = ElLoading.service({
          lock: true,
          text: '正在获取出租配置...',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        try {
          // 调用 init API
          const response = await axios.post(
            `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/rentInit`,
            {
              steamId: selectedSteamId.value,
              // 直接传 steam_hash_name 列表，后端 rentInit 会按该列表请求悠悠有品 init
              steam_hash_name: selectedItems.value.map(item => item.steam_hash_name)
            }
          )

          if (response.data.success) {
            // 保存 init 数据
            rentInitData.value = response.data.data

            // 打开悠悠有品出租表单
            rentFormVisible.value = true

            console.log('[出租] 获取配置成功')
          } else {
            ElMessage.error(response.data.message || '获取出租配置失败')
            console.error('[出租] 获取配置失败:', response.data.message)
          }
        } catch (error) {
          console.error('获取出租配置失败:', error)
          ElMessage.error('获取出租配置失败，请重试')
        } finally {
          loading.close()
        }
      } else if (platform === 'buff') {
        // BUFF 出租功能待开发
        ElMessage.info('BUFF出租功能开发中，敬请期待...')
      }
    }

    // 取消平台选择
    const handlePlatformSelectCancel = () => {
      selectedRentPlatform.value = ''
    }

    // 出租表单关闭
    const handleRentFormClosed = () => {
      selectedRentPlatform.value = ''
    }

    // 处理出租表单提交
    const handleRentFormSubmit = async (formData) => {
      console.log('出租表单提交:', formData)
      console.log('选中的物品:', selectedItems.value)

      // TODO: 这里对接悠悠有品出租 API
      ElMessage.info('出租功能API对接开发中...')

      // 暂时关闭表单
      // rentFormVisible.value = false
    }
    
    // 验证单个物品的价格输入
    const validateItemPrice = (index) => {
      const value = itemForms.value[index].price
      // 只允许数字和小数点
      let newValue = value.replace(/[^\d.]/g, '')
      
      // 只允许一个小数点
      const parts = newValue.split('.')
      if (parts.length > 2) {
        newValue = parts[0] + '.' + parts.slice(1).join('')
      }
      
      // 限制小数点后最多两位
      if (parts.length === 2 && parts[1].length > 2) {
        newValue = parts[0] + '.' + parts[1].substring(0, 2)
      }
      
      itemForms.value[index].price = newValue
    }
    
    // 确认出售/出租
    const confirmSellRent = async (platform) => {
      try {
        let itemsData = []
        
        if (isGroupedView.value) {
          // 组合模式：验证所有组的表单
          const groupValidations = []
          
          for (const classid of Object.keys(groupForms.value)) {
            const formRef = groupFormRefs.value[classid]
            if (formRef) {
              groupValidations.push(formRef.validate().catch(() => {
                throw new Error(`组 ${classid} 的价格验证失败`)
              }))
            }
          }
          
          await Promise.all(groupValidations)
          
          // 将组合数据展开为每个物品的数据
          selectedItems.value.forEach(item => {
            const classid = item.classid || `unknown_${item.assetid}`
            const groupForm = groupForms.value[classid]
            
            if (!groupForm) {
              console.warn(`物品 ${item.assetid} 没有对应的组表单数据`)
              return
            }
            
            itemsData.push({
              assetid: item.assetid,
              name: getCardTitle(item),
              price: groupForm.price,
              remark: groupForm.remark || ''
            })
          })
        } else {
          // 非组合模式：验证所有物品的表单
          const validationPromises = itemFormRefs.value
            .filter(ref => ref)
            .map((ref, index) => ref.validate().catch(() => {
              throw new Error(`第 ${index + 1} 件物品的价格验证失败`)
            }))
          
          await Promise.all(validationPromises)
          
          // 收集每个物品的数据
          itemsData = selectedItems.value.map((item, index) => ({
            assetid: item.assetid,
            name: getCardTitle(item),
            price: itemForms.value[index].price,
            remark: itemForms.value[index].remark || ''
          }))
        }
        
        // 验证是否有数据
        if (itemsData.length === 0) {
          ElMessage.warning('没有可提交的物品数据')
          return
        }
        
        submitting.value = true
        
        const action = sellRentDialogType.value === 'sell' ? '出售' : '出租'
        const platformName = platform === 'yyyp' ? '悠悠有品' : platform === 'buff' ? 'BUFF' : 'CSFL'
        
        // 只处理悠悠有品上架
        if (platform === 'yyyp' && action === '出售') {
          console.log(`开始上架${itemsData.length}件物品到悠悠有品`)
          
          let successCount = 0
          let failCount = 0
          
          // 逐个上架
          for (let i = 0; i < itemsData.length; i++) {
            const item = itemsData[i]
            
            // 更新状态为上架中
            if (isGroupedView.value) {
              // 组合模式暂不支持状态显示
            } else {
              itemForms.value[i].uploadStatus = 'uploading'
              itemForms.value[i].uploadMessage = '上架中...'
            }
            
            try {
              console.log(`[${i + 1}/${itemsData.length}] 正在上架: ${item.name}`)
              
              const response = await axios.post(
                `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/sellInventoryItem`,
                {
                  steamId: selectedSteamId.value,
                  assetId: item.assetid,
                  price: item.price,
                  remark: item.remark,
                  isCanLease: false
                }
              )
              
              if (response.data.success) {
                successCount++
                console.log(`✓ 上架成功: ${item.name}`)
                
                // 更新状态为成功
                if (!isGroupedView.value) {
                  itemForms.value[i].uploadStatus = 'success'
                  itemForms.value[i].uploadMessage = '上架成功'
                }
              } else {
                failCount++
                const errorMsg = response.data.message || '未知错误'
                console.error(`✗ 上架失败: ${item.name} - ${errorMsg}`)
                
                // 更新状态为失败
                if (!isGroupedView.value) {
                  itemForms.value[i].uploadStatus = 'failed'
                  itemForms.value[i].uploadMessage = errorMsg
                }
              }
              
              // 添加延迟，避免请求过快
              if (i < itemsData.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 1000))
              }
              
            } catch (error) {
              failCount++
              const errorMsg = error.response?.data?.message || error.message || '网络错误'
              console.error(`✗ 上架异常: ${item.name}`, error)
              
              // 更新状态为失败
              if (!isGroupedView.value) {
                itemForms.value[i].uploadStatus = 'failed'
                itemForms.value[i].uploadMessage = errorMsg
              }
            }
          }
          
          // 显示结果
          if (failCount === 0) {
            ElMessage.success(`全部上架成功！共${successCount}件物品`)
          } else if (successCount === 0) {
            ElMessage.error(`全部上架失败！共${failCount}件物品`)
          } else {
            ElMessage.warning(`上架完成：成功${successCount}件，失败${failCount}件`)
          }
          
          // 不关闭弹窗，让用户查看上架结果
          // 刷新库存数据
          await loadInventoryData()
          
        } else {
          // 其他平台暂未实现
          ElMessage.warning(`${platformName}${action}功能暂未实现`)
        }
        
      } catch (error) {
        if (error !== false) {
          console.error('操作失败:', error)
          ElMessage.error(error.message || '请检查所有物品的价格是否填写正确')
        }
      } finally {
        submitting.value = false
      }
    }
    
    // 打开预览弹窗
    const openPreview = (item) => {
      previewItem.value = item
      previewVisible.value = true
    }

    // 悠悠出售按钮处理
    const handleYYYPSell = () => {
      ElMessage.info('悠悠出售功能待开发')
      // TODO: 实现悠悠出售功能
    }

    // 悠悠出租按钮处理
    const handleYYYPRent = () => {
      ElMessage.info('悠悠出租功能待开发')
      // TODO: 实现悠悠出租功能
    }

    // BUFF出售按钮处理
    const handleBuffSell = () => {
      ElMessage.info('BUFF出售功能待开发')
      // TODO: 实现BUFF出售功能
    }

    // BUFF出租按钮处理
    const handleBuffRent = () => {
      ElMessage.info('BUFF出租功能待开发')
      // TODO: 实现BUFF出租功能
    }

    // 移入组件按钮处理（单个物品）
    const handleMoveToComponent = async () => {
      if (!previewItem.value) {
        ElMessage.warning('未找到物品信息')
        return
      }
      
      // 检查是否有交易限制
      if (hasTradeRestriction(previewItem.value)) {
        ElMessage.warning('该物品有交易限制，无法存入组件')
        return
      }
      
      // 调用批量移入组件，传入单个物品
      await moveToComponentWithItems([previewItem.value])
    }
    
    // 批量移入组件
    const moveToComponent = async () => {
      if (selectedItems.value.length === 0) {
        ElMessage.warning('请先选择要移入组件的物品')
        return
      }
      
      // 检查是否有交易限制的物品
      const restrictedItems = selectedItems.value.filter(item => hasTradeRestriction(item))
      if (restrictedItems.length > 0) {
        ElMessage.warning('所选物品中有交易限制的物品，无法存入组件')
        return
      }
      
      // 保存要存入的物品
      itemsToDeposit.value = selectedItems.value
      
      // 进入选择组件模式
      isSelectingComponent.value = true
      
      // 重新加载数据，只显示库存组件
      await loadInventoryData()
      
      ElMessage.info(`请选择一个库存组件来存入 ${itemsToDeposit.value.length} 件物品`)
    }

    // 取消选择组件
    const cancelComponentSelection = async () => {
      isSelectingComponent.value = false
      itemsToDeposit.value = []
      // 重新加载数据，显示所有物品
      await loadInventoryData()
    }
    
    // 执行存入操作
    const executeDeposit = async (items, storageUnitId) => {
      const loading = ElLoading.service({
        lock: true,
        text: '正在存入物品...',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      
      try {
        const itemIds = items.map(item => item.assetid)
        
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/prefectWorldSpiderV1/depositToComponent`,
          {
            steamId: selectedSteamId.value,
            itemIds: itemIds,
            storageUnitId: storageUnitId,
            transferType: 1  // 1表示存入
          }
        )
        
        if (response.data.success) {
          ElMessage.success(response.data.message)
          
          // 清空选择
          clearSelection()
          
          // 刷新库存数据
          await loadInventoryData()
        } else {
          ElMessage.error(response.data.message)
        }
        
      } catch (error) {
        console.error('存入物品失败:', error)
        ElMessage.error(error.response?.data?.message || error.message)
      } finally {
        loading.close()
      }
    }

    // 解析交易限制日期
    const parseTradeLockDate = (remark) => {
      if (!remark) return null
      
      try {
        // 匹配日期格式：2025 10月 23 (7:00:00) 或 2025年10月23日
        const dateMatch = remark.match(/(\d{4})\s*年?\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日?\s*\((\d{1,2}):(\d{2}):(\d{2})\)/)
        
        if (dateMatch) {
          const [, year, month, day, hour, minute, second] = dateMatch
          
          // 创建UTC时间（格林尼治标准时间）
          const utcDate = new Date(Date.UTC(year, month - 1, day, hour, minute, second))
          
          // 转换为本地时间
          const localDate = new Date(utcDate)
          
          // 格式化本地日期（只显示到日期）
          const localYear = localDate.getFullYear()
          const localMonth = localDate.getMonth() + 1
          const localDay = localDate.getDate()
          const formattedDate = `${localYear}年${localMonth}月${localDay}日`
          
          // 计算剩余天数
          const now = new Date()
          const diffTime = localDate - now
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
          
          return {
            date: formattedDate,
            daysLeft: diffDays > 0 ? diffDays : 0,
            expired: diffDays <= 0
          }
        }
        
        return null
      } catch (e) {
        console.error('解析交易限制日期失败:', e)
        return null
      }
    }

    // 解析贴纸JSON数据
    const parseStickers = (stickerJson) => {
      if (!stickerJson) return []
      try {
        const stickers = JSON.parse(stickerJson)
        if (!Array.isArray(stickers)) return []

        // 返回贴纸数组，每个贴纸包含name和image
        return stickers.map(sticker => {
          const name = sticker.name || sticker.sticker_name || '未知贴纸'
          const steamHashName = sticker.steam_hash_name || sticker.image || sticker.sticker_img

          // 根据steam_hash_name生成图片URL
          let imageUrl = null
          if (steamHashName) {
            // 使用getWeaponImage相同的逻辑转换路径
            const imageName = steamHashName
              .replace(/\s*\|\s*/g, '___')
              .replace(/\s/g, '_')
              + '.png'
            imageUrl = apiUrls.weaponImage(imageName)
          }

          return {
            name: name,
            image: imageUrl
          }
        })
      } catch (e) {
        console.error('解析贴纸JSON失败:', e)
        return []
      }
    }

    // 解析挂件JSON数据
    const parsePendant = (pendantJson) => {
      if (!pendantJson) return { name: null, image: null }
      try {
        const pendant = JSON.parse(pendantJson)
        const name = pendant.name || '未知挂件'
        const steamHashName = pendant.steam_hash_name

        // 根据steam_hash_name生成图片URL
        let imageUrl = null
        if (steamHashName) {
          const imageName = steamHashName
            .replace(/\s*\|\s*/g, '___')
            .replace(/\s/g, '_')
            + '.png'
          imageUrl = apiUrls.weaponImage(imageName)
        }

        return {
          name: name,
          image: imageUrl
        }
      } catch (e) {
        console.error('解析挂件JSON失败:', e)
        return { name: null, image: null }
      }
    }

    // 获取贴纸数量
    const getStickerCount = (stickerJson) => {
      return parseStickers(stickerJson).length
    }

    // 获取贴纸提示信息
    const getStickerTooltip = (stickerJson) => {
      const stickers = parseStickers(stickerJson)
      if (stickers.length === 0) return ''
      return '贴纸列表:\n' + stickers.map((s, i) => `${i + 1}. ${s.name}`).join('\n')
    }

    // 单独加载统计数据（不重新加载列表）
    const loadInventoryStats = async () => {
      try {
        // 构建查询参数（与loadInventoryData保持一致）
        const params = {
          weapon_type: weaponTypeFilter.value,
          float_range: floatRangeFilter.value
        }
        
        // 如果处于选择组件模式，只统计库存组件
        if (isSelectingComponent.value) {
          params.classid = '3604678661'
        } else {
          // 只在非选择组件模式下应用搜索过滤
          params.search = searchText.value
        }
        
        const statsResponse = await axios.get(
          `${API_CONFIG.BASE_URL}/webInventoryV1/inventory/stats/${selectedSteamId.value}`,
          { params }
        )
        if (statsResponse.data.success) {
          statsData.value = statsResponse.data.data
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }

    // 获取Steam库存
    const fetchSteamInventory = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }

      try {
        fetchingInventory.value = true

        // 直接调用Spider接口，只传steamId
        // Spider会自己调用后端API查询config表获取cookie
        const spiderResponse = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/steamSpiderV1/getInventory`,
          {
            steamId: selectedSteamId.value
          }
        )

        if (spiderResponse.data.success) {
          ElMessage.success(spiderResponse.data.message || '库存获取成功')
          // 重新加载库存数据
          await loadInventoryData()
        } else {
          ElMessage.error(spiderResponse.data.message || '库存获取失败')
        }
      } catch (error) {
        console.error('获取Steam库存失败:', error)
        ElMessage.error('获取库存失败: ' + (error.response?.data?.message || error.message))
      } finally {
        fetchingInventory.value = false
      }
    }

    // 获取悠悠有品价格
    const fetchYYYPPrice = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }

      try {
        fetchingYYYPPrice.value = true
        
        // 调用Spider API获取悠悠有品价格
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getYYYPPrice`,
          {
            steamId: selectedSteamId.value
          }
        )
        
        if (response.data.success) {
          ElMessage.success(response.data.message || '悠悠有品价格获取成功')
          // 重新加载库存数据和统计信息
          await loadInventoryData()
        } else {
          ElMessage.error(response.data.message || '悠悠有品价格获取失败')
        }
        
      } catch (error) {
        console.error('获取悠悠有品价格失败:', error)
        ElMessage.error('获取价格失败: ' + (error.response?.data?.message || error.message))
      } finally {
        fetchingYYYPPrice.value = false
      }
    }

    // 获取BUFF价格
    const fetchBuffPrice = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }

      try {
        fetchingBuffPrice.value = true
        
        // 调用Spider API获取BUFF价格
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/buffSpiderV1/getBUFFPrice`,
          {
            steamId: selectedSteamId.value
          }
        )
        
        if (response.data.success) {
          ElMessage.success(response.data.message || 'BUFF价格获取成功')
          // 重新加载库存数据和统计信息
          await loadInventoryData()
        } else {
          ElMessage.error(response.data.message || 'BUFF价格获取失败')
        }
        
      } catch (error) {
        console.error('获取BUFF价格失败:', error)
        ElMessage.error('获取价格失败: ' + (error.response?.data?.message || error.message))
      } finally {
        fetchingBuffPrice.value = false
      }
    }

    // 计算当前显示的数据（后端已处理所有筛选，前端不再需要额外筛选）
    const currentDisplayData = computed(() => {
      // 只在列表模式下才使用组合数据
      if (displayMode.value === 'list' && groupMode.value) {
        return groupedData.value
      } else {
        return inventoryData.value
      }
    })

    // 格式化选中的饰品数据，用于传递给出租表单
    const formattedSelectedItems = computed(() => {
      return selectedItems.value.map(item => ({
        assetid: item.assetid,
        name: getCardTitle(item),
        steam_hash_name: item.steam_hash_name || item.item_name,
        image: getWeaponImage(item.steam_hash_name),
        float: item.weapon_float,
        buyPrice: item.buy_price ? parseFloat(item.buy_price).toFixed(2) : null
      }))
    })

    // 统计数据计算（使用后端返回的全局统计，支持所有筛选条件）
    const inventoryStats = computed(() => {
      const totalCount = statsData.value.total_count || 0

      const typeDistribution = statsData.value.by_type.length > 0
        ? statsData.value.by_type.slice(0, 3).map(t => `${t.weapon_type}(${t.count})`).join(', ')
        : '暂无数据'

      const wearDistribution = statsData.value.by_wear.length > 0
        ? statsData.value.by_wear.slice(0, 3).map(w => `${w.float_range}(${w.count})`).join(', ')
        : '暂无数据'

      return {
        totalCount: totalCount,
        typeDistribution,
        wearDistribution
      }
    })

    const priceStats = computed(() => {
      // 使用后端返回的统计数据
      const ps = statsData.value.price_stats || {}
      const priced_count = ps.priced_count || 0
      const total_price = typeof ps.total_price === 'number' ? ps.total_price : Number(ps.total_price || 0)
      const avg_price = typeof ps.avg_price === 'number' ? ps.avg_price : Number(ps.avg_price || 0)

      return {
        priced_count,
        total_price: total_price.toFixed(2),
        avg_price: avg_price.toFixed(2),
        min_price: ps.min_price !== undefined ? Number(ps.min_price || 0).toFixed(2) : '0.00',
        max_price: ps.max_price !== undefined ? Number(ps.max_price || 0).toFixed(2) : '0.00'
      }
    })

    const yyypPriceStats = computed(() => {
      // 使用后端返回的统计数据
      const yy = statsData.value.yyyp_price_stats || {}
      const ps = statsData.value.price_stats || {}
      const priced_count = yy.priced_count || 0
      const yy_total = typeof yy.total_price === 'number' ? yy.total_price : Number(yy.total_price || 0)
      const buy_total = typeof ps.total_price === 'number' ? ps.total_price : Number(ps.total_price || 0)
      const avg_price = typeof yy.avg_price === 'number' ? yy.avg_price : Number(yy.avg_price || 0)
      const diff = (yy_total - buy_total).toFixed(2)

      return {
        priced_count,
        total_price: yy_total.toFixed(2),
        avg_price: avg_price.toFixed(2),
        diff
      }
    })

    const buffPriceStats = computed(() => {
      // 使用后端返回的统计数据（扣除2.5%手续费）
      const buff = statsData.value.buff_price_stats || {}
      const ps = statsData.value.price_stats || {}
      const priced_count = buff.priced_count || 0
      const buff_total = typeof buff.total_price === 'number' ? buff.total_price : Number(buff.total_price || 0)
      const buff_total_after_fee = buff_total * 0.975
      const buy_total = typeof ps.total_price === 'number' ? ps.total_price : Number(ps.total_price || 0)
      const diff = (buff_total_after_fee - buy_total).toFixed(2)

      return {
        priced_count,
        total_price: buff_total_after_fee.toFixed(2),
        avg_price: priced_count > 0 ? (buff_total_after_fee / priced_count).toFixed(2) : '0.00',
        diff
      }
    })

    const steamPriceStats = computed(() => {
      // 使用后端返回的统计数据
      const steam = statsData.value.steam_price_stats || {}
      const ps = statsData.value.price_stats || {}
      const priced_count = steam.priced_count || 0
      const steam_total = typeof steam.total_price === 'number' ? steam.total_price : Number(steam.total_price || 0)
      const buy_total = typeof ps.total_price === 'number' ? ps.total_price : Number(ps.total_price || 0)
      const avg_price = typeof steam.avg_price === 'number' ? steam.avg_price : Number(steam.avg_price || 0)
      const diff = (steam_total - buy_total).toFixed(2)

      return {
        priced_count,
        total_price: steam_total.toFixed(2),
        avg_price: avg_price.toFixed(2),
        diff
      }
    })

    onMounted(async () => {
      await loadSteamIdList()
      if (selectedSteamId.value) {
        loadInventoryData(true)
      }
      
      // 设置滚动监听
      setupScrollObserver()
      
      // 监听显示模式变化，重新设置观察器
      watch(displayMode, () => {
        setupScrollObserver()
      })
      
      // 监听数据变化，重新设置观察器（数据加载后）
      watch(inventoryData, () => {
        setupScrollObserver()
      })

      // 监听组合数据变化
      watch(groupedData, () => {
        setupScrollObserver()
      })
    })

    // 组件卸载时清理观察器
    onUnmounted(() => {
      if (imageObserver) {
        imageObserver.disconnect()
        imageObserver = null
      }
    })

    // 组件选择对话框辅助方法
    const getComponentRemainingClass = (remaining) => {
      if (remaining > 100) return 'remaining-high'
      if (remaining > 20) return 'remaining-medium'
      return 'remaining-low'
    }

    const getComponentProgressColor = (storedCount) => {
      const percentage = storedCount / 1000
      if (percentage < 0.7) return '#67C23A'
      if (percentage < 0.9) return '#E6A23C'
      return '#F56C6C'
    }

    return {
      loading,
      fetchingInventory,
      fetchingYYYPPrice,
      fetchingBuffPrice,
      inventoryData,
      groupedData,
      groupMode,
      currentDisplayData,
      inventoryStats,
      priceStats,
      yyypPriceStats,
      buffPriceStats,
      steamPriceStats,
      searchText,
      weaponTypeFilter,
      floatRangeFilter,
      pendantFilter,
      stickerFilter,
      renameFilter,
      tradeRestrictionFilter,
      displayMode,
      steamIdList,
      selectedSteamId,
      sortConfig,
      getItemTitle,
      getCardTitle,
      getWeaponImage,
      handleImageError,
      getPriceDiffClass,
      parseTradeLockDate,
      parseStickers,
      getStickerCount,
      getStickerTooltip,
      loadInventoryData,
      loadMoreData,
      handleReset,
      handleSteamIdChange,
      handleFilterChange,
      handleSortChange,
      handleToggleGroupMode,
      hasMore,
      loadingMore,
      editingAssetId,
      editingPrice,
      startEdit,
      finishEdit,
      cancelEdit,
      fetchSteamInventory,
      fetchYYYPPrice,
      fetchBuffPrice,
      previewVisible,
      previewItem,
      openPreview,
      handleYYYPSell,
      handleYYYPRent,
      handleBuffSell,
      handleBuffRent,
      handleMoveToComponent,
      moveToComponent,
      parsePendant,
      getExpandedItems,
      getExpandedTotal,
      handleExpandPageChange,
      expandedRowPages,
      getItemsPerPage,
      handleRowClick,
      getRowStyle,
      tableRef,
      hasExtras,
      showPriceDiff,
      // 多选相关
      isMultiSelectMode,
      selectedItems,
      toggleDisplayMode,
      toggleMultiSelectMode,
      isItemSelected,
      hasTradeRestriction,
      toggleItemSelection,
      clearSelection,
      selectAllDisplayed,
      handleCardClick,
      // 出售/出租相关
      sellRentDialogVisible,
      sellRentDialogTitle,
      sellRentDialogType,
      itemForms,
      itemFormRefs,
      itemFormRules,
      submitting,
      showSellDialog,
      showRentDialog,
      validateItemPrice,
      yyypRealtimePrices,
      loadingYYYPPrices,
      confirmSellRent,
      // 出租功能
      platformSelectVisible,
      rentFormVisible,
      selectedRentPlatform,
      rentInitData,
      formattedSelectedItems,
      handlePlatformSelect,
      handlePlatformSelectCancel,
      handleRentFormClosed,
      handleRentFormSubmit,
      // 组合显示
      isGroupedView,
      toggleGroupedView,
      groupedItems,
      getGroupAveragePrice,
      getGroupPriceRange,
      getGroupFloatRange,
      autoFillGroupPrices,
      autoFillItemPrices,
      expandedGroups,
      toggleGroupExpand,
      groupForms,
      groupFormRefs,
      validateGroupPrice,
      openGroupRemarkDialog,
      // 备注弹窗
      remarkDialogVisible,
      currentRemark,
      openRemarkDialog,
      saveRemark,
      saveRemark,
      // 备注弹窗
      remarkDialogVisible,
      currentRemark,
      openRemarkDialog,
      saveRemark,
      // 备注弹窗相关
      remarkDialogVisible,
      currentRemarkIndex,
      currentRemark,
      openRemarkDialog,
      saveRemark,
      // 图标组件
      ArrowDown,
      InfoFilled,
      isSelectingComponent,
      itemsToDeposit,
      cancelComponentSelection,
      getComponentRemainingClass,
      getComponentProgressColor
    }
  }
}
</script>

<style scoped>
/* 多选模式操作按钮 */
.multi-select-actions {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-tertiary);
  border: 2px solid var(--el-color-primary);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  animation: slideUp 0.3s ease-out;
}

/* 选择组件模式提示横幅 */
.component-selection-banner {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-tertiary);
  border: 2px solid var(--el-color-primary);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  min-width: 600px;
  animation: slideUp 0.3s ease-out;
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #fff;
}

.banner-icon {
  font-size: 20px;
  flex-shrink: 0;
  color: var(--el-color-primary);
}

.banner-text {
  font-size: 15px;
  line-height: 1.5;
  color: #fff;
}

.banner-text strong {
  font-size: 16px;
  font-weight: bold;
  color: var(--el-color-primary);
  padding: 0 4px;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.multi-select-actions .selected-count {
  color: #fff;
  font-size: 1rem;
  font-weight: bold;
}

.multi-select-actions .action-buttons {
  display: flex;
  gap: 0.5rem;
}

/* 多选模式下的卡片样式 */
.inventory-card.multi-select-mode {
  cursor: pointer;
  user-select: none;
}

.inventory-card.multi-select-mode:hover {
  border-color: var(--el-color-primary);
}

.inventory-card.selected {
  border-color: var(--el-color-primary);
  background: rgba(64, 158, 255, 0.1);
  box-shadow: 0 0 0 2px var(--el-color-primary);
}

/* 有交易限制的卡片样式 */
.inventory-card.trade-restricted {
  cursor: not-allowed !important;
}

.inventory-card.trade-restricted:hover {
  border-color: rgba(255, 255, 255, 0.1) !important;
}

/* 组件已满的卡片样式 */
.inventory-card.component-full {
  cursor: not-allowed !important;
  opacity: 0.5;
  filter: grayscale(0.5);
}

.inventory-card.component-full:hover {
  border-color: rgba(255, 255, 255, 0.1) !important;
  transform: none !important;
  box-shadow: none !important;
}

.inventory-card.component-full::after {
  content: '已满';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(245, 108, 108, 0.9);
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  z-index: 10;
  pointer-events: none;
}

/* 出售/出租弹窗样式 */
.sell-rent-dialog :deep(.el-dialog__header) {
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 1.5rem;
}

.sell-rent-dialog :deep(.el-dialog__title) {
  color: #fff;
  font-weight: bold;
  font-size: 1.1rem;
}

.sell-rent-dialog :deep(.el-dialog__body) {
  background: var(--bg-secondary);
  padding: 1.5rem;
}

.sell-rent-dialog :deep(.el-dialog__footer) {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: 1rem 1.5rem;
}

.sell-rent-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.selected-items-list-with-inputs {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
}

.selected-items-list-with-inputs h4 {
  color: #fff;
  margin: 0;
  font-size: 1rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

/* 组合显示样式 - 重新设计 */
.grouped-section {
  margin-bottom: 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.02);
  flex-shrink: 0;
}

.group-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.25rem 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  cursor: pointer;
  transition: background 0.2s ease;
}

.group-card:hover {
  background: rgba(255, 255, 255, 0.05);
}

.group-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.group-thumb {
  width: 60px;
  height: 60px;
  object-fit: contain;
  background: var(--bg-tertiary);
  border-radius: 6px;
  flex-shrink: 0;
}

.group-info {
  flex: 1;
  min-width: 0;
}

.group-name {
  color: #fff;
  font-size: 0.95rem;
  font-weight: 500;
  margin-bottom: 0.35rem;
  line-height: 1.4;
}

.group-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.group-count {
  color: #4CAF50;
  font-size: 0.9rem;
  font-weight: 600;
}

.group-type {
  color: #2196F3;
  font-size: 0.85rem;
  padding: 2px 8px;
  background: rgba(33, 150, 243, 0.1);
  border-radius: 4px;
}

.group-avg-price {
  color: #FFC107;
  font-size: 0.85rem;
  font-weight: 500;
}

.group-yyyp-price {
  font-size: 0.85rem;
  font-weight: 500;
}

.group-yyyp-price.price-loading {
  color: #409EFF;
}

.group-price-range {
  color: #999;
  font-size: 0.85rem;
}

.group-float-range {
  color: #999;
  font-size: 0.8rem;
  margin-top: 0.25rem;
  font-family: monospace;
}

.group-expand-icon {
  margin-left: auto;
  color: #999;
  transition: transform 0.3s ease;
}

.group-expand-icon .is-expanded {
  transform: rotate(180deg);
}

.group-right {
  flex-shrink: 0;
}

.group-items-list {
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.group-item-detail {
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border-left: 2px solid rgba(76, 175, 80, 0.3);
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.group-item-detail:last-child {
  margin-bottom: 0;
}

.item-detail-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.detail-label {
  color: #999;
  font-size: 0.85rem;
}

.detail-label.rename {
  color: #67C23A;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

.detail-label.remark {
  color: #E6A23C;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

.grouped-item-info {
  flex: 1;
  min-width: 0;
}

.grouped-item-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.85rem;
}


.item-float-inline {
  color: #4CAF50;
  font-family: monospace;
}

.item-rename-inline {
  color: #67C23A;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.grouped-item-right {
  flex-shrink: 0;
}

.items-scroll {
  height: 70vh;
  max-height: 70vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 0.5rem;
  padding-right: 1rem;
}

.items-scroll::-webkit-scrollbar {
  width: 8px;
}

.items-scroll::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.items-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.items-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.selected-item-card {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.selected-item-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(76, 175, 80, 0.3);
}

.item-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.item-thumb-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.item-thumb {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: var(--bg-tertiary);
  border-radius: 4px;
}

/* 印花覆盖层 - 左下角 */
.item-sticker-overlay {
  position: absolute;
  bottom: 2px;
  left: 2px;
  display: flex;
  gap: 2px;
  z-index: 5;
}

.item-sticker-mini {
  width: 18px;
  height: 18px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 2px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  transition: all 0.2s ease;
  cursor: pointer;
}

.item-sticker-mini:hover {
  transform: scale(2);
  z-index: 10;
  border-color: rgba(76, 175, 80, 0.8);
}

.item-sticker-mini img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* 挂件覆盖层 - 右上角 */
.item-pendant-overlay {
  position: absolute;
  top: 2px;
  right: 2px;
  z-index: 5;
}

.item-pendant-mini {
  width: 20px;
  height: 20px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 2px;
  overflow: hidden;
  border: 1px solid rgba(255, 215, 0, 0.4);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  transition: all 0.2s ease;
  cursor: pointer;
}

.item-pendant-mini:hover {
  transform: scale(2);
  z-index: 10;
  border-color: rgba(255, 215, 0, 0.8);
}

.item-pendant-mini img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  color: #fff;
  font-size: 0.95rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  line-height: 1.4;
  word-break: break-word;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.item-price-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.item-buy-price {
  color: #999;
  font-size: 0.85rem;
}

.item-yyyp-price {
  font-size: 0.85rem;
}

.price-loading {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #409EFF;
}

.price-loading .el-icon {
  font-size: 0.9rem;
}

.price-error {
  color: #F56C6C;
}

.price-higher {
  color: #F56C6C;
  font-weight: 500;
}

.price-lower {
  color: #67C23A;
  font-weight: 500;
}

.price-equal {
  color: #999;
  font-weight: 500;
}

.price-no-compare {
  color: #409EFF;
  font-weight: 500;
}

.price-count {
  color: #999;
  font-size: 0.8rem;
  margin-left: 0.25rem;
}

.item-float-bar {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.float-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.float-value-text {
  color: #fff;
  font-size: 0.8rem;
  font-family: monospace;
  font-weight: 500;
  flex-shrink: 0;
}

.float-bar-mini {
  position: relative;
  height: 4px;
  display: flex;
  border-radius: 2px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  width: 100px !important;
  max-width: 100px;
  flex-shrink: 0;
}

.float-bar-mini .float-segment {
  height: 100%;
}

.float-bar-mini .float-segment.fn {
  flex: 7;
  background: linear-gradient(to right, #4CAF50, #66BB6A);
}

.float-bar-mini .float-segment.mw {
  flex: 8;
  background: linear-gradient(to right, #8BC34A, #9CCC65);
}

.float-bar-mini .float-segment.ft {
  flex: 23;
  background: linear-gradient(to right, #FFC107, #FFB300);
}

.float-bar-mini .float-segment.ww {
  flex: 7;
  background: linear-gradient(to right, #FF9800, #FB8C00);
}

.float-bar-mini .float-segment.bs {
  flex: 55;
  background: linear-gradient(to right, #F44336, #E53935);
}

.float-bar-mini .float-pointer {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 2px;
  height: 8px;
  background: #fff;
  border-radius: 1px;
  box-shadow: 0 0 3px rgba(0, 0, 0, 0.5), 0 0 6px rgba(255, 255, 255, 0.8);
  z-index: 10;
  pointer-events: none;
}

.float-bar-mini .float-pointer::before {
  content: '';
  position: absolute;
  top: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 2px solid transparent;
  border-right: 2px solid transparent;
  border-top: 2.5px solid #fff;
}

.float-bar-mini .float-pointer::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 2px solid transparent;
  border-right: 2px solid transparent;
  border-bottom: 2.5px solid #fff;
}

.item-rename {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.rename-icon {
  font-size: 0.9rem;
}

.rename-value {
  color: #67C23A;
  font-size: 0.8rem;
  font-weight: 500;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-right {
  flex: 0 0 auto;
  padding: 0;
  display: flex;
  align-items: center;
}

.inline-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.inline-form > div:first-child {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

.inline-form :deep(.el-form-item) {
  margin-bottom: 0;
  flex: 1;
}

.inline-form :deep(.el-button) {
  flex-shrink: 0;
}

.upload-status {
  width: 100%;
}

.upload-status .el-tag {
  width: 100%;
  justify-content: center;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.item-right :deep(.el-input__inner) {
  background-color: #2a2a2a;
  border-color: #333;
  color: #fff;
}

.item-right :deep(.el-input-group__prepend) {
  background-color: #1a1a1a;
  border-color: #333;
  color: #999;
}

.form-tip {
  color: #999;
  font-size: 0.75rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
  text-align: center;
}

/* 懒加载图片样式 */
.lazy-image {
  opacity: 0;
  transition: opacity 0.3s ease-in-out;
  background: linear-gradient(90deg, #2a2a2a 25%, #333 50%, #2a2a2a 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

.lazy-image.loaded {
  opacity: 1;
  background: none;
  animation: none;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.steam-id-select {
  width: 200px;
}

.search-input {
  width: 200px;
}

.filter-select {
  width: 100px;
}

.action-button {
  min-width: auto;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  padding: 8px 12px;
}

.inventory-stats {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.table-container {
  position: relative;
}

.table-wrapper {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.table-footer {
  padding: 1rem;
  text-align: right;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-number {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: bold;
  color: #fff;
  margin-top: clamp(0.5rem, 1vw, 0.625rem);
}

.stat-text {
  font-size: clamp(0.75rem, 1.5vw, 0.875rem);
  color: #ccc;
  margin-top: clamp(0.5rem, 1vw, 0.625rem);
  line-height: 1.5;
}

.stat-price-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: clamp(0.5rem, 1vw, 0.625rem);
}

.stat-diff-right {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: bold;
  margin: 0;
}

.pagination {
  margin-top: clamp(1rem, 3vw, 1.25rem);
  display: flex;
  justify-content: center;
}

.expand-content {
  padding: 1rem;
  background-color: var(--bg-secondary) !important;
}

.expand-content :deep(.el-table) {
  background-color: transparent !important;
}

.expand-content :deep(.el-table__body-wrapper) {
  background-color: transparent !important;
}

.expand-content :deep(.el-table th.el-table__cell) {
  background-color: var(--bg-tertiary) !important;
}

.expand-content :deep(.el-table td.el-table__cell) {
  background-color: transparent !important;
}

.expand-content :deep(.el-table__row) {
  background-color: transparent !important;
}

.expand-content :deep(.el-table__expanded-cell) {
  background-color: var(--bg-secondary) !important;
}

:deep(.el-table__expanded-cell) {
  background-color: var(--bg-secondary) !important;
  padding: 0 !important;
}

:deep(.el-table) {
  background-color: transparent;
  color: #fff;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

:deep(.el-table th) {
  background-color: var(--bg-tertiary);
  color: #fff;
  border-bottom: 1px solid var(--border-default);
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
}

:deep(.el-table td) {
  background-color: transparent !important;
  border-bottom: 1px solid var(--border-default);
  color: #ccc;
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
}

:deep(.el-table tr:hover > td) {
  background-color: rgba(255, 255, 255, 0.05) !important;
}

/* 隐藏展开列的箭头图标 */
:deep(.el-table__expand-column .cell) {
  display: none;
}

/* 组合模式下可展开行的悬停效果 */
:deep(.el-table__body-wrapper .el-table__row[style*="cursor: pointer"]:hover) {
  background-color: rgba(76, 175, 80, 0.1) !important;
}

/* 展开列宽度设置为最小 */
:deep(.el-table__expand-column) {
  width: 1px !important;
  padding: 0 !important;
}

/* 商品名称单元格样式 */
.item-name-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-title {
  line-height: 1.4;
}

.inline-pagination-below {
  margin-top: 0.5rem;
}

.inline-pagination-below :deep(.el-pagination) {
  padding: 0;
}

.inline-pagination-below :deep(.el-pager li) {
  min-width: 24px;
  height: 24px;
  line-height: 24px;
  font-size: 12px;
}

.inline-pagination-below :deep(.btn-prev),
.inline-pagination-below :deep(.btn-next) {
  padding: 0 4px;
  min-width: 24px;
  height: 24px;
  line-height: 24px;
}

.item-extras {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

/* 印花列表样式 */
.sticker-list {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.sticker-item {
  position: relative;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sticker-item:hover {
  transform: scale(2);
  z-index: 10;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  border-color: rgba(76, 175, 80, 0.5);
}

.sticker-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.5));
}

.sticker-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 1rem;
  font-weight: bold;
  background: rgba(255, 255, 255, 0.05);
}

/* 挂件样式 */
.pendant-list {
  display: flex;
  gap: 4px;
}

.pendant-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 2px;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
}

/* 改名文本样式 */
.rename-text {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: #999;
}

.rename-value {
  color: #4CAF50;
  font-weight: 500;
}

:deep(.el-table__expanded-cell) {
  background-color: transparent !important;
}

:deep(.el-input__inner) {
  background-color: #2a2a2a;
  border-color: #333;
  color: #fff;
}

:deep(.el-select .el-input__inner) {
  background-color: #2a2a2a;
  border-color: #333;
  color: #fff;
}

:deep(.el-switch) {
  --el-switch-on-color: #4CAF50;
  --el-switch-off-color: #909399;
}

:deep(.el-switch__label) {
  color: #ccc;
}

:deep(.el-table .el-table__cell) {
  word-break: break-word;
}

:deep(.el-table__header th) {
  user-select: none;
}

/* 卡片显示样式 */
.card-container {
  margin-top: 1rem;
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.inventory-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: visible; /* 允许印花和挂件hover时溢出 */
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 340px; /* 降低卡片高度 */
}

.inventory-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.inventory-card:not(.selected):hover {
  border-color: var(--el-color-primary);
}

.inventory-card.selected:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3), 0 0 0 2px var(--el-color-primary);
}

.card-image {
  width: 100%;
  height: 150px; /* 缩小图片区域高度 */
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: visible; /* 允许贴纸和挂件溢出 */
  flex-shrink: 0; /* 防止压缩 */
  position: relative; /* 为贴纸和挂件覆盖层定位 */
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 保持比例，完整显示 */
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
}

/* 贴纸覆盖层 - 左下角 */
.sticker-overlay {
  position: absolute;
  bottom: 4px;
  left: 4px;
  display: flex;
  gap: 3px;
  z-index: 5;
  pointer-events: none; /* 不阻挡鼠标事件 */
}

/* 挂件覆盖层 - 右上角 */
.pendant-overlay {
  position: absolute;
  top: 4px;
  right: 4px;
  z-index: 5;
  pointer-events: none; /* 不阻挡鼠标事件 */
}

.sticker-item-overlay {
  position: relative;
  width: 36px;
  height: 36px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 4px;
  overflow: hidden;
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
  transition: all 0.2s ease;
  pointer-events: auto; /* 贴纸本身可以交互 */
  cursor: pointer;
}

.sticker-item-overlay:hover {
  transform: scale(2);
  z-index: 10;
  border-color: rgba(76, 175, 80, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.7);
}

/* 挂件样式 - 右上角 */
.pendant-item-overlay {
  position: relative;
  width: 42px;
  height: 42px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 4px;
  overflow: hidden;
  border: 1.5px solid rgba(255, 215, 0, 0.4);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
  transition: all 0.2s ease;
  pointer-events: auto; /* 挂件本身可以交互 */
  cursor: pointer;
}

.pendant-item-overlay:hover {
  transform: scale(2);
  z-index: 10;
  border-color: rgba(255, 215, 0, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.7);
}

.sticker-img-overlay {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.5));
}

.sticker-placeholder-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 1rem;
  font-weight: bold;
}

.pendant-img-overlay {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.5));
}

.pendant-placeholder-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffd700;
  font-size: 1.2rem;
  font-weight: bold;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  color: #999;
  font-size: 0.9rem;
}

.card-content {
  padding: 0.75rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-title {
  font-size: 0.8rem;
  font-weight: bold;
  color: #fff;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.3;
  min-height: 2.6em;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.75rem;
}

/* 组件存储信息样式 */
.component-storage-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

.storage-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}

.storage-label {
  color: #999;
}

.storage-value {
  color: #fff;
  font-weight: bold;
}

.storage-progress {
  margin: 0.25rem 0;
}

.storage-remaining {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.remaining-label {
  color: #999;
}

.remaining-value {
  font-weight: bold;
  font-size: 0.9rem;
}

.remaining-value.remaining-high {
  color: #67C23A;
}

.remaining-value.remaining-medium {
  color: #E6A23C;
}

.remaining-value.remaining-low {
  color: #F56C6C;
}

.card-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  color: #999;
  font-size: 0.7rem;
}

.info-value {
  color: #ccc;
  font-size: 0.7rem;
  text-align: right;
  flex: 1;
  margin-left: 0.5rem;
}

.card-prices {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.3rem;
  padding-top: 0;
  border-top: none;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  gap: 0.5rem;
}

.price-group {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
}

.price-label {
  color: #999;
  font-size: 0.7rem;
  white-space: nowrap;
}

.price-value {
  color: #fff;
  font-weight: bold;
  font-size: 0.75rem;
}

.buy-price {
  color: #fff;
}

.price-profit {
  color: #f56c6c;
}

.price-loss {
  color: #4CAF50;
}

.card-footer {
  margin-top: 0.5rem;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.tag-icon {
  margin-right: 0.2rem;
}

.rename-tag {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  margin-bottom: 0.3rem;
}

.table-info-container {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

/* 贴纸图片样式 - 列表视图 */
.sticker-images-table {
  display: flex;
  flex-wrap: wrap;
  gap: 0.2rem;
  padding: 0.2rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 3px;
}

.sticker-item-table {
  position: relative;
  width: 30px;
  height: 30px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sticker-item-table:hover {
  transform: scale(1.2);
  z-index: 10;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  border-color: rgba(76, 175, 80, 0.5);
}

.sticker-img-table {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.2), rgba(255, 255, 255, 0.1));
}

.sticker-placeholder-table {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.05);
}

/* 磨损值数字显示 */
.float-value {
  text-align: left;
  font-size: 0.75rem;
  color: #ccc;
  font-family: monospace;
  margin-top: 0.2rem;
  margin-bottom: 0;
  font-weight: 500;
}

/* 磨损值显示条样式 */
.float-bar-container {
  margin-top: 0.3rem;
  padding: 0;
  margin-bottom: 0;
}

.float-bar {
  position: relative;
  height: 8px;
  display: flex;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.float-segment {
  height: 100%;
  transition: opacity 0.2s;
}

.float-segment:hover {
  opacity: 0.8;
}

/* CS2 标准磨损等级颜色 */
.float-segment.fn {
  flex: 7;  /* 0.00 - 0.07 */
  background: linear-gradient(to right, #4CAF50, #66BB6A);
}

.float-segment.mw {
  flex: 8;  /* 0.07 - 0.15 */
  background: linear-gradient(to right, #8BC34A, #9CCC65);
}

.float-segment.ft {
  flex: 23; /* 0.15 - 0.38 */
  background: linear-gradient(to right, #FFC107, #FFB300);
}

.float-segment.ww {
  flex: 7;  /* 0.38 - 0.45 */
  background: linear-gradient(to right, #FF9800, #FB8C00);
}

.float-segment.bs {
  flex: 55; /* 0.45 - 1.00 */
  background: linear-gradient(to right, #F44336, #E53935);
}

/* 磨损值指针 */
.float-pointer {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 3px;
  height: 16px;
  background: #fff;
  border-radius: 2px;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.5), 0 0 8px rgba(255, 255, 255, 0.8);
  z-index: 10;
  pointer-events: none;
  transition: all 0.2s ease;
}

.float-pointer::before {
  content: '';
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid #fff;
}

.float-pointer::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 5px solid #fff;
}

@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    padding: 0.5rem;
  }

  .inventory-card {
    height: 320px; /* 移动端卡片高度 */
  }

  .card-image {
    height: 120px; /* 移动端图片区域高度 */
  }

  .card-content {
    padding: 0.75rem;
  }

  .card-title {
    font-size: 0.85rem;
  }

  .info-label,
  .info-value,
  .price-label,
  .price-value {
    font-size: 0.7rem;
  }

  .float-bar {
    height: 6px;
  }

  .float-pointer {
    height: 12px;
  }

  .sticker-item-overlay {
    width: 28px;
    height: 28px;
  }

  .pendant-item-overlay {
    width: 34px;
    height: 34px;
  }
}

@media (max-width: 768px) {
  .search-input,
  .type-select,
  .wear-select,
  .filter-select {
    min-width: unset;
    width: 100%;
    max-width: none;
  }

  :deep(.el-table) {
    font-size: 0.75rem;
  }

  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 0.5rem 0.25rem;
  }
}

/* 预览弹窗样式 */
.preview-dialog :deep(.el-dialog__header) {
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 1.5rem;
}

.preview-dialog :deep(.el-dialog__title) {
  color: #fff;
  font-weight: bold;
  font-size: 1.1rem;
}

.preview-dialog :deep(.el-dialog__body) {
  background: var(--bg-secondary);
  padding: 1.5rem;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.preview-main-layout {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.preview-left-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preview-right-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preview-image-section {
  position: relative;
  width: 100%;
  height: 300px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
}

.preview-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 1.2rem;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
}

/* 预览弹窗中的贴纸列表 */
.preview-sticker-list-section {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.preview-sticker-list-title {
  color: #fff;
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.preview-sticker-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  height: auto;
}

.preview-sticker-list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s ease;
}

.preview-sticker-list-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(76, 175, 80, 0.5);
}

.preview-sticker-list-img-wrapper {
  position: relative;
  width: 50px;
  height: 50px;
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.2s ease;
  cursor: pointer;
}

.preview-sticker-list-img-wrapper:hover {
  transform: scale(1.2);
  border-color: rgba(76, 175, 80, 0.8);
  z-index: 10;
}

.preview-sticker-list-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-sticker-list-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 1.2rem;
  font-weight: bold;
}

.preview-sticker-list-name {
  color: #fff;
  font-size: 0.9rem;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 预览弹窗中的挂件信息 */
.preview-pendant-section {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.preview-pendant-title {
  color: #fff;
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.preview-pendant-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  height: auto;
}

.preview-pendant-list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s ease;
}

.preview-pendant-list-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 215, 0, 0.5);
}

.preview-pendant-list-img-wrapper {
  position: relative;
  width: 50px;
  height: 50px;
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(255, 215, 0, 0.2);
  transition: transform 0.2s ease;
  cursor: pointer;
}

.preview-pendant-list-img-wrapper:hover {
  transform: scale(1.2);
  border-color: rgba(255, 215, 0, 0.8);
  z-index: 10;
}

.preview-pendant-list-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-pendant-list-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffd700;
  font-size: 1.5rem;
  font-weight: bold;
}

.preview-pendant-list-name {
  color: #fff;
  font-size: 0.9rem;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-info-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 改名标签 */
.preview-rename {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.preview-rename-icon {
  font-size: 1.2rem;
}

.preview-rename-text {
  color: #fff;
  font-size: 1rem;
  font-weight: 500;
}

/* 磨损信息 */
.preview-float-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-float-bar-container {
  width: 100%;
}

.preview-float-value {
  font-size: 1.1rem;
  font-family: monospace;
  color: #fff;
  font-weight: bold;
}

.preview-float-range {
  font-size: 0.9rem;
  color: #999;
}

/* 价格信息 */
.preview-prices {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.preview-price-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.preview-price-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.preview-price-label {
  color: #999;
  font-size: 0.9rem;
  white-space: nowrap;
}

.preview-price-value {
  color: #fff;
  font-weight: bold;
  font-size: 1rem;
}

.preview-price-value.price-profit {
  color: #f56c6c;
}

.preview-price-value.price-loss {
  color: #4CAF50;
}

/* 标签信息 */
.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  min-height: 0;
}

.preview-tags .el-tag {
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
}

/* 操作按钮样式 */
.preview-action-buttons {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.25rem;
  padding: 0;
  border-top: none;
}

.preview-action-buttons .el-button {
  flex: 1;
  font-weight: 400;
  font-size: 0.8rem;
  padding: 0.4rem 0.5rem;
  height: 32px;
  min-height: 32px;
}

/* 右下角移入组件按钮 */
.preview-bottom-right-button {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.preview-bottom-right-button .el-button {
  font-weight: 400;
  font-size: 0.85rem;
  padding: 0.5rem 1.5rem;
}

/* 武器图片单元格样式 */
.weapon-image-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 80px;
  padding: 4px;
}

.weapon-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  border-radius: 4px;
}

.weapon-image-cell-small {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 60px;
  padding: 2px;
}

.weapon-img-small {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  border-radius: 4px;
}

.no-image {
  color: #999;
  font-size: 0.8rem;
  text-align: center;
}

/* 展开内容样式 */
.expand-content {
  padding: 1rem;
  background-color: var(--bg-secondary) !important;
}

.expand-two-columns {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.expand-item-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 0.75rem;
  transition: all 0.2s ease;
  cursor: pointer;
}

.expand-item-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(76, 175, 80, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.expand-item-row {
  display: flex;
  gap: 0.75rem;
}

.expand-item-left {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.expand-item-image {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 4px;
  position: relative;
  overflow: visible;
}

/* 展开卡片中的贴纸覆盖层 - 左下角 */
.sticker-overlay-expand {
  position: absolute;
  bottom: 2px;
  left: 2px;
  display: flex;
  gap: 2px;
  z-index: 5;
  pointer-events: none;
}

.sticker-item-overlay-expand {
  position: relative;
  width: 16px;
  height: 16px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 2px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  transition: all 0.2s ease;
  pointer-events: auto;
  cursor: pointer;
}

.sticker-item-overlay-expand:hover {
  transform: scale(2);
  z-index: 10;
  border-color: rgba(76, 175, 80, 0.8);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.7);
}

/* 展开卡片中的挂件覆盖层 - 右上角 */
.pendant-overlay-expand {
  position: absolute;
  top: 2px;
  right: 2px;
  z-index: 5;
  pointer-events: none;
}

.pendant-item-overlay-expand {
  position: relative;
  width: 18px;
  height: 18px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 2px;
  overflow: hidden;
  border: 1px solid rgba(255, 215, 0, 0.4);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  transition: all 0.2s ease;
  pointer-events: auto;
  cursor: pointer;
}

.pendant-item-overlay-expand:hover {
  transform: scale(2);
  z-index: 10;
  border-color: rgba(255, 215, 0, 0.8);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.7);
}

.expand-remark-tag {
  display: flex;
  justify-content: center;
}

.expand-rename-tag {
  display: flex;
  justify-content: center;
  margin-top: 0.25rem;
}

.expand-rename-tag .el-tag {
  font-size: 0.85rem;
  padding: 2px 6px;
  cursor: help;
}

.expand-item-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
}

.expand-item-float {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.float-text-row {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.expand-value-small {
  color: #fff;
  font-weight: 500;
  font-size: 0.75rem;
  font-family: monospace;
}

.expand-item-prices {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.25rem;
  font-size: 0.85rem;
}

.expand-price-item {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.expand-item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.expand-meta-item {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.expand-label {
  color: #999;
  font-size: 0.8rem;
}

.expand-value {
  color: #fff;
  font-weight: 500;
  font-size: 0.85rem;
}

.float-bar-mini {
  position: relative;
  height: 4px;
  display: flex;
  border-radius: 2px;
  overflow: hidden;
  width: 100px;
  max-width: 100px;
  margin-top: 2px;
}

.float-bar-mini .float-segment {
  height: 100%;
}

.float-bar-mini .float-pointer {
  width: 2px;
  height: 8px;
  top: 50%;
  transform: translate(-50%, -50%);
}

.float-bar-mini .float-pointer::before,
.float-bar-mini .float-pointer::after {
  border-left-width: 2px;
  border-right-width: 2px;
  border-top-width: 3px;
  border-bottom-width: 3px;
}

.expand-content-empty {
  padding: 1rem;
  text-align: center;
  background-color: var(--bg-secondary);
}



/* 响应式调整 */
@media (max-width: 768px) {
  .preview-dialog {
    width: 95% !important;
  }

  .preview-main-layout {
    flex-direction: column;
  }

  .preview-image-section {
    height: 200px;
  }

  .preview-sticker-list {
    height: auto;
  }

  .preview-price-row {
    flex-direction: column;
    gap: 0.5rem;
  }

  .weapon-image-cell {
    height: 60px;
  }
}

/* 出租表单对话框样式 */
.rent-form-dialog :deep(.el-dialog) {
  max-height: 75vh;
  height: 75vh;
  display: flex;
  flex-direction: column;
}

.rent-form-dialog :deep(.el-dialog__header) {
  padding: 0;
  border-bottom: none;
  flex-shrink: 0;
}

.rent-form-dialog :deep(.el-dialog__body) {
  padding: 0;
  background: #1a1a1a;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.rent-form-dialog :deep(.el-dialog__footer) {
  display: none;
}
</style>
