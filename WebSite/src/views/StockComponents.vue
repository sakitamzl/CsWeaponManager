<template>
  <div>
    <!-- 搜索与统计数据 -->
    <div class="stats-summary">
      <div class="card">
        <!-- 搜索栏 -->
        <div class="search-section">
          <div class="flex flex-wrap gap-4 items-center">
            <el-select 
              v-model="selectedSteamId" 
              placeholder="选择完美世界账号" 
              class="steam-id-select"
              @change="handleSteamIdChange"
              filterable
            >
              <el-option
                v-for="item in steamIdList"
                :key="item.dataID"
                :label="`${item.dataName} (${item.steamID})`"
                :value="item.steamID"
              >
                <span>{{ item.dataName }} ({{ item.steamID }})</span>
              </el-option>
            </el-select>
            <el-select 
              v-model="selectedComponent" 
              placeholder="选择库存组件（选中后只显示该组件）" 
              class="component-select"
              @change="handleComponentSelect"
              filterable
              clearable
            >
              <el-option
                v-for="item in inventoryComponents"
                :key="item.assetid"
                :label="item.weapon_float ? `${item.item_name} (数量:${item.weapon_float})` : item.item_name"
                :value="item.assetid"
              >
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                  <span style="flex: 0 0 auto; max-width: 45%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ item.item_name }}</span>
                  <span style="flex: 0 0 auto; color: var(--el-text-color-secondary); font-size: 13px; margin-left: 8px; font-family: monospace;">
                    数量: <span style="display: inline-block; text-align: right; min-width: 2.5em;">{{ item.weapon_float || 0 }}</span> | assetid: {{ item.assetid }}
                  </span>
                </div>
              </el-option>
            </el-select>
            <el-input
              v-model="searchText"
              placeholder="搜索武器名称..."
              prefix-icon="Search"
              class="search-input"
              @keyup.enter="handleSearch"
              @clear="handleClearSearch"
              clearable
            />
            <el-button type="primary" @click="handleSearch" :loading="loading">
              搜索
            </el-button>
            <el-button @click="handleClearSearch" :disabled="loading">
              重置
            </el-button>
            <el-button type="success" @click="handleUpdateComponent" :loading="updateLoading" :disabled="!selectedComponent">
              获取/更新组件物品
            </el-button>
            <el-button type="success" @click="handleUpdateAllComponents" :loading="updateAllLoading" :disabled="!selectedSteamId">
              获取/更新全部组件
            </el-button>
            <el-button type="primary" plain @click="handleFillAllPlatformPrices" :loading="platformPriceLoading" :disabled="!selectedSteamId">
              获取/更新平台价格
            </el-button>
            <el-button 
              :type="showPriceDiff ? 'info' : 'primary'" 
              @click="showPriceDiff = !showPriceDiff" 
              class="action-button"
            >
              {{ showPriceDiff ? '显示价格' : '显示差价' }}
            </el-button>
            <el-switch
              v-model="groupMode"
              active-text="组合模式"
              inactive-text="明细模式"
              @change="handleToggleGroupMode"
              style="margin-left: auto;"
            />
          </div>
        </div>
        
        <!-- 分隔线 -->
        <div class="search-stats-divider"></div>
        
        <!-- 统计数据 -->
        <div class="inventory-stats">
          <div class="grid grid-5">
            <div class="card">
              <h3>总组件数量</h3>
              <p class="stat-number">{{ totalStats.totalCount }}</p>
            </div>
            <div class="card">
              <h3>购入总价值</h3>
              <p class="stat-number">¥{{ totalStats.totalCost }}</p>
            </div>
            <div class="card">
              <h3>悠悠有品最低价</h3>
              <div class="stat-price-container">
                <p class="stat-number">¥{{ totalStats.totalYYYPPrice }}</p>
                <p class="stat-diff-right" :style="{ color: totalStats.yyypDiff >= 0 ? '#f56c6c' : '#4CAF50' }">
                  {{ totalStats.yyypDiff >= 0 ? '+' : '' }}¥{{ totalStats.yyypDiff }}
                </p>
              </div>
            </div>
            <div class="card">
              <h3>BUFF最低价</h3>
              <div class="stat-price-container">
                <p class="stat-number">¥{{ totalStats.totalBuffPrice }}</p>
                <p class="stat-diff-right" :style="{ color: totalStats.buffDiff >= 0 ? '#f56c6c' : '#4CAF50' }">
                  {{ totalStats.buffDiff >= 0 ? '+' : '' }}¥{{ totalStats.buffDiff }}
                </p>
              </div>
            </div>
            <div class="card">
              <h3>Steam参考价</h3>
              <div class="stat-price-container">
                <p class="stat-number">¥{{ totalStats.totalSteamPrice }}</p>
                <p class="stat-diff-right" :style="{ color: totalStats.steamDiff >= 0 ? '#f56c6c' : '#4CAF50' }">
                  {{ totalStats.steamDiff >= 0 ? '+' : '' }}¥{{ totalStats.steamDiff }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="table-container">
      <!-- 明细模式：卡片视图 -->
      <div v-if="!groupMode" class="card-container">
        <div v-loading="loading" class="card-grid">
          <div
            v-for="item in componentData"
            :key="item.goods_assetid"
            class="inventory-card"
            @click="handleCardClick(item)"
          >
            <div class="card-image">
              <img
                v-if="getWeaponImage(item.steam_hash_name)"
                :data-src="getWeaponImage(item.steam_hash_name)"
                :alt="item.item_name"
                class="lazy-image"
                @error="(e) => e.target.style.display = 'none'"
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
              <div class="card-title" :title="getItemTitle(item)">
                {{ getItemTitle(item) }}
              </div>
              <div class="card-info">
                <div class="float-bar-container" v-if="item.weapon_float && formatWeaponFloat(item.weapon_float)">
                  <div class="float-bar">
                    <div class="float-segment fn"></div>
                    <div class="float-segment mw"></div>
                    <div class="float-segment ft"></div>
                    <div class="float-segment ww"></div>
                    <div class="float-segment bs"></div>
                    <div
                      class="float-pointer"
                      :style="{ left: `${parseFloat(item.weapon_float) * 100}%` }"
                      :title="`磨损值: ${item.weapon_float}`"
                    ></div>
                  </div>
                </div>
                <div class="float-value" v-if="item.weapon_float && formatWeaponFloat(item.weapon_float)">
                  {{ item.weapon_float }}
                </div>
              </div>
              <div class="card-prices">
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
                  <el-tag v-if="item.rename" type="info" size="small" class="rename-tag">
                    <span class="tag-icon">🏷️</span>{{ item.rename }}
                  </el-tag>
                  <el-tag type="success" size="small">
                    {{ item.assetid }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="table-footer">
          <span>共 {{ componentData.length }} 条数据</span>
          <span v-if="hasMore && !loadingMore" style="margin-left: 1rem; color: #999;">滚动加载更多...</span>
          <span v-if="loadingMore" style="margin-left: 1rem; color: #4CAF50;">正在加载更多...</span>
          <span v-if="!hasMore && componentData.length > 0" style="margin-left: 1rem; color: #999;">已加载全部数据</span>
        </div>
        <!-- 滚动触发元素 -->
        <div id="load-more-trigger-card" style="height: 1px;"></div>
      </div>

      <!-- 组合模式：表格视图 -->
      <div v-else class="table-wrapper">
        <div class="table-toolbar">
          <div class="pagination pagination-top">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="totalItems"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
        
        <el-table
        ref="tableRef"
        :data="filteredData"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        :row-style="getRowStyle"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        :flexible="true"
        :scrollbar-always-on="true"
        @row-click="handleRowClick"
        :row-key="row => row.goods_assetid"
      >
        <el-table-column v-if="groupMode" type="expand" width="1">
          <template #default="scope">
            <div class="expand-content" v-if="scope.row.item_count > 1">
              <div class="expand-two-columns">
                <div 
                  v-for="(item, index) in getExpandedItems(scope.row)" 
                  :key="item.goods_assetid"
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
                          @error="(e) => e.target.style.display = 'none'"
                        />
                        <span v-else class="no-image">无图</span>
                        
                        <!-- 贴纸覆盖层 -->
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
                        
                        <!-- 挂件覆盖层 -->
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
                @error="(e) => e.target.style.display = 'none'"
              />
              <span v-else class="no-image">无图</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="物品名称" min-width="250" show-overflow-tooltip fixed="left">
          <template #default="scope">
            <div class="item-name-cell">
              <div class="item-title">{{ getItemTitle(scope.row) }}</div>
              <!-- 组合模式下显示分页器 - 固定在名称下方 -->
              <div v-if="groupMode && getExpandedTotal(scope.row) > getItemsPerPage()" class="inline-pagination-below" @click.stop>
                <el-pagination
                  small
                  :current-page="expandedRowPages[scope.row.goods_assetid] || 1"
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
        <el-table-column prop="weapon_type" label="武器类型" min-width="120" />
        <el-table-column prop="weapon_level" label="武器等级" min-width="120" />
        <el-table-column v-if="!groupMode" prop="assetid" label="所属组件" min-width="160" show-overflow-tooltip>
          <template #default="scope">
            <span style="font-family: monospace;">{{ scope.row.assetid || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="!groupMode" prop="goods_assetid" label="组件ID" min-width="160" show-overflow-tooltip>
          <template #default="scope">
            <span style="font-family: monospace;">{{ scope.row.goods_assetid || scope.row.component_id || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="数量" width="120" align="center">
          <template #default="scope">
            <span>{{ groupMode ? (scope.row.item_count || 0) : (scope.row.weapon_float || 0) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="weapon_float" label="磨损值" width="200" align="left">
          <template #default="scope">
            <!-- 组合模式下，数量大于1时不显示磨损值 -->
            <div v-if="groupMode && scope.row.item_count > 1" style="color: #888;">
              多个磨损值
            </div>
            <div v-else-if="scope.row.weapon_float && formatWeaponFloat(scope.row.weapon_float)">
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
        <el-table-column prop="float_range" label="磨损范围" min-width="120" />
        <el-table-column prop="buy_price" label="购入价格" min-width="150" sortable>
          <template #default="scope">
            <div v-if="editingGoodsAssetId !== scope.row.goods_assetid"
                 @click="startEdit(scope.row)"
                 style="cursor: pointer; padding: 5px;">
              <div v-if="scope.row.buy_price" style="display: flex; align-items: center; gap: 5px;">
                <span style="color: #fff; font-weight: bold;">¥{{ formatPrice(scope.row.buy_price) }}</span>
              </div>
              <span v-else style="color: #888;">点击输入</span>
            </div>
            <el-input
              v-else
              v-model="editingPrice"
              placeholder="输入价格"
              size="small"
              :id="'price-input-' + scope.row.goods_assetid"
              @blur="finishEdit(scope.row)"
              @keyup.enter="finishEdit(scope.row)"
              @keyup.esc="cancelEdit"
            />
          </template>
        </el-table-column>
        <el-table-column prop="yyyp_price" label="悠悠价格" min-width="150" sortable>
          <template #default="scope">
            <span 
              v-if="scope.row.yyyp_price && scope.row.buy_price"
              :style="{
                color: parseFloat(scope.row.yyyp_price) < parseFloat(scope.row.buy_price) ? '#4CAF50' : '#f56c6c',
                fontWeight: 'bold'
              }"
            >
              {{ showPriceDiff ? (parseFloat(scope.row.yyyp_price) < parseFloat(scope.row.buy_price) ? '-' : '+') : '' }}¥{{ showPriceDiff ? Math.abs(parseFloat(scope.row.yyyp_price) - parseFloat(scope.row.buy_price)).toFixed(2) : formatPrice(scope.row.yyyp_price) }}
            </span>
            <span v-else-if="scope.row.yyyp_price" style="color: #fff; font-weight: bold;">
              ¥{{ formatPrice(scope.row.yyyp_price) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="buff_price" label="BUFF价格" min-width="150" sortable>
          <template #default="scope">
            <span 
              v-if="scope.row.buff_price && scope.row.buy_price"
              :style="{
                color: parseFloat(scope.row.buff_price) < parseFloat(scope.row.buy_price) ? '#4CAF50' : '#f56c6c',
                fontWeight: 'bold'
              }"
            >
              {{ showPriceDiff ? (parseFloat(scope.row.buff_price) < parseFloat(scope.row.buy_price) ? '-' : '+') : '' }}¥{{ showPriceDiff ? Math.abs(parseFloat(scope.row.buff_price) - parseFloat(scope.row.buy_price)).toFixed(2) : formatPrice(scope.row.buff_price) }}
            </span>
            <span v-else-if="scope.row.buff_price" style="color: #fff; font-weight: bold;">
              ¥{{ formatPrice(scope.row.buff_price) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="steam_price" label="Steam价格" min-width="150" sortable>
          <template #default="scope">
            <span 
              v-if="scope.row.steam_price && scope.row.buy_price"
              :style="{
                color: parseFloat(scope.row.steam_price) < parseFloat(scope.row.buy_price) ? '#4CAF50' : '#f56c6c',
                fontWeight: 'bold'
              }"
            >
              {{ showPriceDiff ? (parseFloat(scope.row.steam_price) < parseFloat(scope.row.buy_price) ? '-' : '+') : '' }}¥{{ showPriceDiff ? Math.abs(parseFloat(scope.row.steam_price) - parseFloat(scope.row.buy_price)).toFixed(2) : formatPrice(scope.row.steam_price) }}
            </span>
            <span v-else-if="scope.row.steam_price" style="color: #fff; font-weight: bold;">
              ¥{{ formatPrice(scope.row.steam_price) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        </el-table>
        
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalItems"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { API_CONFIG, apiUrls } from '@/config/api.js'

export default {
  name: 'StockComponents',
  setup() {
    const loading = ref(false)
    const updateLoading = ref(false)
    const updateAllLoading = ref(false)
    const platformPriceLoading = ref(false)
    const componentData = ref([])
    const groupedData = ref([])
    const groupMode = ref(true)
    const showPriceDiff = ref(false)
    const searchText = ref('')
    const currentPage = ref(1)
    const pageSize = ref(50) // 每次加载数量
    const currentOffset = ref(0) // 当前偏移量
    const hasMore = ref(true) // 是否还有更多数据
    const loadingMore = ref(false) // 是否正在加载更多
    const totalItems = ref(0)
    const steamIdList = ref([])
    const selectedSteamId = ref('')
    const inventoryComponents = ref([])
    const selectedComponent = ref('')
    const tableRef = ref(null)
    const expandedRowPages = ref({})
    const previewVisible = ref(false)
    const previewItem = ref(null)
    
    // 图片观察器
    let imageObserver = null
    
    // 编辑价格相关
    const editingGoodsAssetId = ref(null)
    const editingPrice = ref('')
    const originalPrice = ref('')
    
    // API 基础地址
    const API_BASE = `${API_CONFIG.BASE_URL}/webInventoryV1`
    const API_PERFECTWORLD = `${API_CONFIG.BASE_URL}/prefectWorldConfigV1`
    const API_COMPONENTS = `${API_CONFIG.BASE_URL}/webStockComponentsV1`
    const API_COMPONENTS_GROUPED = `${API_CONFIG.BASE_URL}/webStockComponentsV1/components/grouped`
    const API_SPIDER = API_CONFIG.SPIDER_BASE_URL
    
    // classid常量 - 组件的classid
    const COMPONENT_CLASSID = '3604678661'

    const totalStats = ref({
      totalCount: 0,
      totalCost: '0.00',
      totalYYYPPrice: '0.00',
      totalBuffPrice: '0.00',
      totalSteamPrice: '0.00',
      yyypDiff: '0.00',
      buffDiff: '0.00',
      steamDiff: '0.00'
    })

    const filteredData = computed(() => {
      return groupMode.value ? groupedData.value : componentData.value
    })

    const formatTime = (time) => {
      if (!time) return '-'
      return new Date(time).toLocaleString('zh-CN')
    }

    const formatPrice = (price) => {
      if (!price || price === 0 || price === '0') return '0.00'
      const num = parseFloat(price)
      if (isNaN(num)) return '0.00'
      return num.toFixed(2)
    }

    const formatWeaponFloat = (value) => {
      if (!value || value === '0' || value === '0.0') return ''
      const str = String(value)
      if (str === '0' || str === '0.0') return ''
      return str
    }

    const getQuantityType = (quantity) => {
      if (quantity === 0) return 'danger'
      if (quantity < 5) return 'warning'
      if (quantity < 10) return 'info'
      return 'success'
    }

    // 获取武器图片
    const getWeaponImage = (steamHashName) => {
      if (!steamHashName) {
        return null
      }
      const imageName = steamHashName
        .replace(/\s*\|\s*/g, '___')
        .replace(/\s/g, '_')
        + '.png'
      return apiUrls.weaponImage(imageName)
    }

    // 获取组合后的商品标题，若 weapon_name 与 item_name 相同则只显示一次
    const getItemTitle = (item) => {
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

    // 检查是否有额外信息（印花、挂件、改名）
    const hasExtras = (item) => {
      return !!(item.sticker || item.pendant || item.rename)
    }

    // 解析印花数据
    const parseStickers = (stickerData) => {
      if (!stickerData) return []
      try {
        const parsed = typeof stickerData === 'string' ? JSON.parse(stickerData) : stickerData
        if (!Array.isArray(parsed)) return []

        // 返回贴纸数组，每个贴纸包含name和image
        return parsed.map(sticker => {
          const name = sticker.name || '未知贴纸'
          const hashName = sticker.hashName || sticker.steam_hash_name || sticker.steamHashName

          // 根据hashName生成图片URL，添加"Sticker___"前缀
          let imageUrl = null
          if (hashName) {
            const imageName = hashName
              .replace(/\s*\|\s*/g, '___')
              .replace(/\s/g, '_')
            imageUrl = apiUrls.weaponImage(`Sticker___${imageName}.png`)
          }

          return {
            name: name,
            image: imageUrl
          }
        })
      } catch (e) {
        console.error('解析印花数据失败:', e)
        return []
      }
    }

    // 解析挂件数据
    const parsePendant = (pendantData) => {
      if (!pendantData) return null
      try {
        const parsed = typeof pendantData === 'string' ? JSON.parse(pendantData) : pendantData

        // 如果是数组，取第一个元素
        let pendantObj = Array.isArray(parsed) ? parsed[0] : parsed

        if (!pendantObj || typeof pendantObj !== 'object') return null

        // 获取hashName，支持多种字段名以提高兼容性
        const hashName = pendantObj.hashName || pendantObj.steam_hash_name || pendantObj.steamHashName

        // 生成图片URL
        let imageUrl = null
        if (hashName) {
          const imageName = hashName
            .replace(/\s*\|\s*/g, '___')
            .replace(/\s/g, '_')
            + '.png'
          imageUrl = apiUrls.weaponImage(imageName)
        }

        return {
          name: pendantObj.name || '挂件',
          image: imageUrl
        }
      } catch (e) {
        console.error('解析挂件数据失败:', e)
        return null
      }
    }

    const loadSteamIdList = async () => {
      try {
        // 从完美世界配置中获取账号列表，传递classid参数统计库存组件数量
        const response = await axios.get(`${API_PERFECTWORLD}/configs`, {
          params: {
            classid: COMPONENT_CLASSID
          }
        })
        console.log('完美世界配置列表响应:', response.data)
        if (response.data.success) {
          steamIdList.value = response.data.data
          if (steamIdList.value.length > 0) {
            selectedSteamId.value = steamIdList.value[0].steamID
            console.log('默认选择Steam ID:', selectedSteamId.value)
          } else {
            ElMessage.warning('没有找到完美世界账号配置')
          }
        }
      } catch (error) {
        console.error('加载完美世界配置列表失败:', error)
        ElMessage.error('加载账号列表失败: ' + (error.response?.data?.error || error.message))
      }
    }

    const handleSteamIdChange = () => {
      console.log('Steam ID已切换:', selectedSteamId.value)
      selectedComponent.value = ''
      loadInventoryComponents()
      groupMode.value ? loadGroupedData() : loadComponentData()
    }

    const loadInventoryComponents = async () => {
      if (!selectedSteamId.value) {
        return
      }
      
      try {
        console.log('正在加载库存组件列表，Steam ID:', selectedSteamId.value, 'ClassID:', COMPONENT_CLASSID)
        
        // 从 steam_inventory 表获取组件列表用于下拉框
        const response = await axios.get(`${API_BASE}/inventory/${selectedSteamId.value}`, {
          params: {
            classid: COMPONENT_CLASSID,
            limit: 9999,
            offset: 0
          }
        })
        
        console.log('库存组件列表响应:', response.data)
        
        if (response.data.success) {
          inventoryComponents.value = response.data.data || []
          console.log(`加载成功，共 ${inventoryComponents.value.length} 个组件`)
        } else {
          console.error('加载库存组件失败:', response.data.error)
          inventoryComponents.value = []
        }
      } catch (error) {
        console.error('加载库存组件失败:', error)
        console.error('错误详情:', error.response?.status, error.response?.data)
        // 如果获取失败,不显示错误提示,只是清空列表
        inventoryComponents.value = []
      }
    }

    const handleComponentSelect = async () => {
      console.log('选择的组件 assetid:', selectedComponent.value)
      
      if (!selectedComponent.value) {
        // 清空选择，重新加载所有组件数据
        currentPage.value = 1
        currentOffset.value = 0
        groupMode.value ? loadGroupedData() : loadComponentData()
        if (!groupMode.value) {
          setupScrollObserver()
        }
        return
      }
      
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }
      
      // 重置页码和偏移量
      currentPage.value = 1
      currentOffset.value = 0
      
      // 根据当前模式加载数据
      groupMode.value ? loadGroupedData() : loadComponentData()
      if (!groupMode.value) {
        setupScrollObserver()
      }
    }

    const loadComponentData = async (reset = true) => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请选择Steam账号')
        return
      }
      
      // 如果是重置，清空数据
      if (reset) {
        componentData.value = []
        currentOffset.value = 0
        hasMore.value = true
      }
      
      loading.value = true
      try {
        // 计算当前页码
        const currentPageNum = Math.floor(currentOffset.value / pageSize.value) + 1
        
        console.log('正在加载组件数据，Steam ID:', selectedSteamId.value, 'Page:', currentPageNum, 'PageSize:', pageSize.value)
        
        const params = {
          search: searchText.value,
          page: currentPageNum,
          page_size: pageSize.value
        }
        
        // 如果选择了组件，添加 assetid 参数进行筛选
        if (selectedComponent.value) {
          params.assetid = selectedComponent.value
        }
        
        const response = await axios.get(`${API_COMPONENTS}/components/${selectedSteamId.value}`, {
          params: params
        })
        
        console.log('组件数据响应:', response.data)
        
        if (response.data.success) {
          const newData = response.data.data || []
          
          // 追加新数据
          componentData.value = [...componentData.value, ...newData]
          totalItems.value = response.data.total
          
          // 检查是否还有更多数据
          hasMore.value = newData.length === pageSize.value && componentData.value.length < totalItems.value
          
          // 更新偏移量
          currentOffset.value += newData.length
          
          await loadComponentStats()
          
          if (reset) {
            ElMessage.success(`加载成功，共 ${totalItems.value} 条记录`)
          }
          
          console.log('数据已加载，当前:', componentData.value.length, '条，总计:', totalItems.value, '还有更多:', hasMore.value)
        } else {
          ElMessage.error(response.data.error || '加载数据失败')
          componentData.value = []
          totalItems.value = 0
        }
      } catch (error) {
        console.error('加载组件数据失败:', error)
        ElMessage.error('加载数据失败: ' + (error.response?.data?.error || error.message))
        componentData.value = []
        totalItems.value = 0
      } finally {
        loading.value = false
      }
    }

    const loadGroupedData = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请选择Steam账号')
        return
      }

      loading.value = true
      try {
        const params = {
          search: searchText.value,
          page: currentPage.value,
          page_size: pageSize.value
        }
        
        // 如果选择了组件，添加 assetid 参数进行筛选
        if (selectedComponent.value) {
          params.assetid = selectedComponent.value
        }
        
        const response = await axios.get(`${API_COMPONENTS_GROUPED}/${selectedSteamId.value}`, {
          params: params
        })

        if (response.data.success) {
          groupedData.value = (response.data.data || []).map(item => ({
            ...item,
            // 复用表格字段，便于直接展示
            weapon_float: item.item_count,           // 用数量占位
            buy_price: item.total_buy_price,
            yyyp_price: item.total_yyyp_price,
            buff_price: item.total_buff_price,
            steam_price: item.total_steam_price,
            goods_assetid: item.item_name || item.steam_hash_name || Math.random().toString(36).slice(2)
          }))
          totalItems.value = response.data.total || 0
          
          // 加载统计数据
          await loadComponentStats()
          
          ElMessage.success(`组合加载成功，共 ${groupedData.value.length} 条记录`)
        } else {
          ElMessage.error(response.data.error || '加载组合数据失败')
          groupedData.value = []
          totalItems.value = 0
        }
      } catch (error) {
        console.error('加载组合数据失败:', error)
        ElMessage.error('加载组合数据失败: ' + (error.response?.data?.error || error.message))
        groupedData.value = []
        totalItems.value = 0
      } finally {
        loading.value = false
      }
    }

    const loadComponentStats = async () => {
      try {
        const response = await axios.get(`${API_COMPONENTS}/components/stats/${selectedSteamId.value}`)
        console.log('统计数据响应:', response.data)
        
        if (response.data.success) {
          const stats = response.data.data
          
          const totalCost = parseFloat(stats.totalCost || 0)
          const totalYYYPPrice = parseFloat(stats.totalYYYPPrice || 0)
          const totalBuffPrice = parseFloat(stats.totalBuffPrice || 0)
          const totalSteamPrice = parseFloat(stats.totalSteamPrice || 0)
          
          totalStats.value = {
            totalCount: stats.totalCount || 0,
            totalCost: totalCost.toFixed(2),
            totalYYYPPrice: totalYYYPPrice.toFixed(2),
            totalBuffPrice: totalBuffPrice.toFixed(2),
            totalSteamPrice: totalSteamPrice.toFixed(2),
            yyypDiff: (totalYYYPPrice - totalCost).toFixed(2),
            buffDiff: (totalBuffPrice - totalCost).toFixed(2),
            steamDiff: (totalSteamPrice - totalCost).toFixed(2)
          }
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      if (!selectedComponent.value) {
        groupMode.value ? loadGroupedData() : loadComponentData()
      }
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
      if (!selectedComponent.value) {
        groupMode.value ? loadGroupedData() : loadComponentData()
      }
    }

    // 加载更多数据
    const loadMoreData = async () => {
      if (loadingMore.value || !hasMore.value) {
        return
      }
      
      loadingMore.value = true
      try {
        await loadComponentData(false)
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
            }
          })
        }, {
          root: null,
          rootMargin: '200px',
          threshold: 0.01
        })

        // 观察所有懒加载图片
        const lazyImages = document.querySelectorAll('.lazy-image')
        lazyImages.forEach(img => {
          imageObserver.observe(img)
        })
      })
    }

    // 设置滚动监听
    const setupScrollObserver = () => {
      nextTick(() => {
        const trigger = document.getElementById('load-more-trigger-card')
        if (trigger) {
          // 如果已有观察器，先断开
          if (trigger._observer) {
            trigger._observer.disconnect()
          }
          
          const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
              if (entry.isIntersecting && hasMore.value && !loadingMore.value && !loading.value) {
                loadMoreData()
              }
            })
          }, {
            root: null,
            rootMargin: '100px'
          })
          
          observer.observe(trigger)
          trigger._observer = observer
        }

        // 设置懒加载图片观察器
        setupLazyImageObserver()
      })
    }

    const handleSearch = () => {
      currentPage.value = 1
      currentOffset.value = 0
      selectedComponent.value = ''
      groupMode.value ? loadGroupedData() : loadComponentData()
      if (!groupMode.value) {
        setupScrollObserver()
      }
    }

    const handleClearSearch = () => {
      searchText.value = ''
      selectedComponent.value = ''
      currentPage.value = 1
      currentOffset.value = 0
      groupMode.value ? loadGroupedData() : loadComponentData()
      if (!groupMode.value) {
        setupScrollObserver()
      }
    }

    const calcAvg = (total, count) => {
      const c = parseFloat(count) || 0
      const t = parseFloat(total) || 0
      if (!c) return '0.00'
      return (t / c).toFixed(2)
    }

    const handleToggleGroupMode = (val = null) => {
      // 按钮直接传 true，开关传布尔值，默认取反
      if (val === true || val === false) {
        groupMode.value = val
      } else {
        groupMode.value = !groupMode.value
      }
      currentPage.value = 1
      currentOffset.value = 0
      selectedComponent.value = ''
      
      if (groupMode.value) {
        loadGroupedData()
      } else {
        loadComponentData()
        setupScrollObserver()
      }
    }

    const handleUpdateComponent = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }
      
      if (!selectedComponent.value) {
        ElMessage.warning('请先选择要更新的组件')
        return
      }
      
      updateLoading.value = true
      try {
        console.log('更新组件 - steamId:', selectedSteamId.value, 'assetid:', [selectedComponent.value])
        
        const response = await axios.post(`${API_SPIDER}/prefectWorldSpiderV1/getInventoryComponent`, {
          steamId: selectedSteamId.value,
          assetid: [selectedComponent.value]  // 传递数组
        })
        
        console.log('更新组件响应:', response.data)
        
        if (response.data.success) {
          const itemCount = response.data.total_items || 0
          ElMessage.success(`组件物品更新成功! 共更新 ${itemCount} 个物品`)
          
          // 自动同步购入价格
          try {
            console.log('自动同步购入价格...')
            const priceResponse = await axios.post(`${API_COMPONENTS}/auto_fill_prices/${selectedSteamId.value}`)
            if (priceResponse.data.success) {
              const data = priceResponse.data.data
              console.log(`购入价格自动同步完成: 成功填充 ${data.filled_count}/${data.total_count}`)
            }
          } catch (priceError) {
            console.error('自动同步购入价格失败:', priceError)
            // 不阻断主流程，只记录错误
          }
          
          // 更新成功后重新加载数据
          await loadComponentData()
        } else {
          ElMessage.error(response.data.message || '更新组件物品失败')
        }
      } catch (error) {
        console.error('更新组件失败:', error)
        ElMessage.error('更新组件失败: ' + (error.response?.data?.message || error.message))
      } finally {
        updateLoading.value = false
      }
    }

    // 开始编辑价格
    const startEdit = (row) => {
      editingGoodsAssetId.value = row.goods_assetid || row.component_id
      originalPrice.value = row.buy_price || ''
      editingPrice.value = row.buy_price || ''

      // 使用nextTick确保input已渲染后聚焦
      nextTick(() => {
        const input = document.getElementById(`price-input-${row.goods_assetid || row.component_id}`)
        if (input) {
          input.focus()
          input.select() // 选中所有文本，方便修改
        }
      })
    }

    // 取消编辑
    const cancelEdit = () => {
      editingGoodsAssetId.value = null
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
      const currentGoodsAssetId = editingGoodsAssetId.value
      cancelEdit()

      // 异步发送请求到后端
      try {
        const response = await axios.put(
          `${API_COMPONENTS}/update/buy_price/${selectedSteamId.value}/${currentGoodsAssetId}`,
          { buy_price: newPrice }
        )

        if (response.data.success) {
          ElMessage.success('价格更新成功')
          // 重新加载统计数据
          await loadComponentStats()
        } else {
          // 如果失败，恢复原价格
          row.buy_price = oldPrice
          ElMessage.error(response.data.message || '价格更新失败')
        }
      } catch (error) {
        // 如果失败，恢复原价格
        row.buy_price = oldPrice
        console.error('更新价格失败:', error)
        ElMessage.error('更新价格失败: ' + (error.response?.data?.message || error.message))
      }
    }

    const handleUpdateAllComponents = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }
      
      // 筛选出数量非0的组件
      const validComponents = inventoryComponents.value.filter(item => {
        const quantity = parseFloat(item.weapon_float) || 0
        return quantity > 0
      })
      
      if (validComponents.length === 0) {
        ElMessage.warning('没有找到数量大于0的组件')
        return
      }
      
      // 提取所有assetid
      const assetidList = validComponents.map(item => item.assetid)
      
      // 确认操作
      const confirmResult = await ElMessageBox.confirm(
        `即将更新 ${assetidList.length} 个组件的物品数据，此操作可能需要较长时间，是否继续？`,
        '确认更新',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).catch(() => false)
      
      if (!confirmResult) {
        return
      }
      
      updateAllLoading.value = true
      try {
        console.log('批量更新组件 - steamId:', selectedSteamId.value, '组件数量:', assetidList.length)
        
        ElMessage.info(`开始更新 ${assetidList.length} 个组件，请稍候...`)
        
        const response = await axios.post(`${API_SPIDER}/prefectWorldSpiderV1/getInventoryComponent`, {
          steamId: selectedSteamId.value,
          assetid: assetidList
        })
        
        console.log('批量更新组件响应:', response.data)
        
        const successCount = response.data.success_count || 0
        const failedCount = response.data.failed_count || 0
        const totalItems = response.data.total_items || 0
        
        if (response.data.success) {
          ElMessage.success(`全部组件更新成功! 成功: ${successCount}/${assetidList.length}, 总物品数: ${totalItems}`)
        } else {
          ElMessage.warning(`部分组件更新失败! 成功: ${successCount}, 失败: ${failedCount}, 总物品数: ${totalItems}`)
        }
        
        // 自动同步购入价格
        try {
          console.log('自动同步购入价格...')
          const priceResponse = await axios.post(`${API_COMPONENTS}/auto_fill_prices/${selectedSteamId.value}`)
          if (priceResponse.data.success) {
            const data = priceResponse.data.data
            console.log(`购入价格自动同步完成: 成功填充 ${data.filled_count}/${data.total_count}`)
          }
        } catch (priceError) {
          console.error('自动同步购入价格失败:', priceError)
          // 不阻断主流程，只记录错误
        }
        
        // 更新成功后重新加载数据
        await loadComponentData()
        
      } catch (error) {
        console.error('批量更新组件失败:', error)
        ElMessage.error('批量更新组件失败: ' + (error.response?.data?.message || error.message))
      } finally {
        updateAllLoading.value = false
      }
    }

    const handleAutoFillPrices = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }
      
      autoFillLoading.value = true
      try {
        console.log('开始自动填充价格 - steamId:', selectedSteamId.value)
        
        ElMessage.info('正在自动获取购入价格，请稍候...')
        
        const response = await axios.post(`${API_COMPONENTS}/auto_fill_prices/${selectedSteamId.value}`)
        
        console.log('自动填充价格响应:', response.data)
        
        if (response.data.success) {
          const data = response.data.data
          const message = `价格自动填充完成！\n总计: ${data.total_count}\n成功填充: ${data.filled_count}\n已有价格: ${data.already_filled_count}\n未找到: ${data.not_found_count}`
          
          ElMessage({
            type: 'success',
            message: message,
            duration: 5000,
            showClose: true
          })
          
          // 重新加载数据和统计
          await loadComponentData()
        } else {
          ElMessage.error(response.data.message || '自动填充价格失败')
        }
      } catch (error) {
        console.error('自动填充价格失败:', error)
        ElMessage.error('自动填充价格失败: ' + (error.response?.data?.message || error.message))
      } finally {
        autoFillLoading.value = false
      }
    }

    const handleFillReferencePrice = async (source) => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }

      const isYyyp = source === 'yyyp'
      const label = isYyyp ? '悠悠有品' : 'BUFF'

      try {
        ElMessage.info(`正在同步${label}价格，请稍候...`)

        const response = await axios.post(
          `${API_COMPONENTS}/fill_reference_price/${selectedSteamId.value}/${source}`
        )

        if (response.data.success) {
          const msg = response.data.message || `${label}价格同步完成`
          ElMessage.success({
            message: msg,
            duration: 5000,
            showClose: true
          })

          await loadComponentData()
        } else {
          ElMessage.error(response.data.message || `${label}价格同步失败`)
        }
      } catch (error) {
        console.error(`${label}价格同步失败:`, error)
        ElMessage.error(`${label}价格同步失败: ` + (error.response?.data?.message || error.message))
      }
    }

    // 获取/更新所有平台价格（悠悠有品 + BUFF）
    const handleFillAllPlatformPrices = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择Steam账号')
        return
      }

      platformPriceLoading.value = true
      try {
        ElMessage.info('正在获取/更新平台价格（悠悠有品 + BUFF），请稍候...')

        // 依次调用悠悠有品和BUFF价格接口，强制重新获取最新价格
        const yyypResponse = await axios.post(
          `${API_COMPONENTS}/fill_reference_price/${selectedSteamId.value}/yyyp`,
          { force_update: true }
        )

        const buffResponse = await axios.post(
          `${API_COMPONENTS}/fill_reference_price/${selectedSteamId.value}/buff`,
          { force_update: true }
        )

        // 检查两个接口的返回结果
        const yyypSuccess = yyypResponse.data.success
        const buffSuccess = buffResponse.data.success

        if (yyypSuccess && buffSuccess) {
          ElMessage.success({
            message: '平台价格获取/更新完成（悠悠有品 + BUFF）',
            duration: 5000,
            showClose: true
          })
        } else if (yyypSuccess) {
          ElMessage.warning('悠悠有品价格获取/更新成功，BUFF价格同步失败')
        } else if (buffSuccess) {
          ElMessage.warning('BUFF价格获取/更新成功，悠悠有品价格同步失败')
        } else {
          ElMessage.error('平台价格获取/更新失败')
        }

        // 重新加载数据
        await (groupMode.value ? loadGroupedData() : loadComponentData())
      } catch (error) {
        console.error('平台价格获取/更新失败:', error)
        ElMessage.error('平台价格获取/更新失败: ' + (error.response?.data?.message || error.message))
      } finally {
        platformPriceLoading.value = false
      }
    }

    // 计算每页显示的卡片数量
    const getItemsPerPage = () => {
      return 12
    }

    // 获取展开行的详细数据（带分页）
    const getExpandedItems = (row) => {
      if (!row.goods_assetids || !Array.isArray(row.goods_assetids)) {
        return []
      }

      const allItems = row.goods_assetids.map((goods_assetid, index) => ({
        goods_assetid: goods_assetid,
        weapon_float: row.weapon_floats && row.weapon_floats[index] ? row.weapon_floats[index] : null,
        buy_price: row.buy_prices && row.buy_prices[index] ? row.buy_prices[index] : '0',
        yyyp_price: row.yyyp_prices && row.yyyp_prices[index] ? row.yyyp_prices[index] : '0',
        buff_price: row.buff_prices && row.buff_prices[index] ? row.buff_prices[index] : '0',
        steam_price: row.steam_prices && row.steam_prices[index] ? row.steam_prices[index] : '0',
        sticker: row.stickers && row.stickers[index] ? row.stickers[index] : null,
        pendant: row.pendants && row.pendants[index] ? row.pendants[index] : null,
        rename: row.renames && row.renames[index] ? row.renames[index] : null,
        steam_hash_name: row.steam_hash_name,
        item_name: row.item_name,
        weapon_name: row.weapon_name,
        weapon_type: row.weapon_type,
        float_range: row.float_range
      }))

      const currentPage = expandedRowPages.value[row.goods_assetid] || 1
      const itemsPerPage = getItemsPerPage()
      const totalPages = Math.ceil(allItems.length / itemsPerPage)
      
      if (currentPage > totalPages && totalPages > 0) {
        expandedRowPages.value = {
          ...expandedRowPages.value,
          [row.goods_assetid]: 1
        }
        const start = 0
        const end = itemsPerPage
        return allItems.slice(start, end)
      }
      
      const start = (currentPage - 1) * itemsPerPage
      const end = start + itemsPerPage
      
      return allItems.slice(start, end)
    }

    // 获取展开行的总数据量
    const getExpandedTotal = (row) => {
      if (!row.goods_assetids || !Array.isArray(row.goods_assetids)) {
        return 0
      }
      return row.goods_assetids.length
    }

    // 处理展开行的分页变化
    const handleExpandPageChange = (row, page) => {
      expandedRowPages.value = {
        ...expandedRowPages.value,
        [row.goods_assetid]: page
      }
      
      if (tableRef.value) {
        const expandedRows = tableRef.value.store.states.expandRows.value || []
        const isExpanded = expandedRows.some(r => r.goods_assetid === row.goods_assetid)
        
        if (!isExpanded) {
          tableRef.value.toggleRowExpansion(row, true)
        }
      }
    }

    // 处理行点击事件
    const handleRowClick = (row, column, event) => {
      if (!groupMode.value) return
      if (row.item_count <= 1) return
      
      if (tableRef.value) {
        tableRef.value.toggleRowExpansion(row)
      }
    }

    // 获取行样式
    const getRowStyle = (data) => {
      const style = { backgroundColor: 'transparent' }
      if (groupMode.value && data.row.item_count > 1) {
        style.cursor = 'pointer'
      }
      return style
    }

    // 打开预览弹窗
    const openPreview = (item) => {
      previewItem.value = item
      previewVisible.value = true
    }

    // 处理卡片点击事件
    const handleCardClick = (item) => {
      console.log('点击卡片:', item)
      // 可以在这里添加卡片点击的逻辑，比如显示详情、选择等
    }

    onMounted(async () => {
      await loadSteamIdList()
      if (selectedSteamId.value) {
        await loadInventoryComponents()
        if (groupMode.value) {
          loadGroupedData()
        } else {
          loadComponentData()
          setupScrollObserver()
        }
      }
    })

    return {
      loading,
      groupMode,
      showPriceDiff,
      updateLoading,
      updateAllLoading,
      platformPriceLoading,
      componentData,
      groupedData,
      filteredData,
      totalStats,
      searchText,
      currentPage,
      pageSize,
      totalItems,
      steamIdList,
      selectedSteamId,
      inventoryComponents,
      selectedComponent,
      editingGoodsAssetId,
      editingPrice,
      tableRef,
      expandedRowPages,
      previewVisible,
      previewItem,
      hasMore,
      loadingMore,
      formatTime,
      formatPrice,
      formatWeaponFloat,
      getQuantityType,
      getWeaponImage,
      getItemTitle,
      hasExtras,
      calcAvg,
      parseStickers,
      parsePendant,
      handleSizeChange,
      handleCurrentChange,
      handleSearch,
      handleClearSearch,
      handleSteamIdChange,
      handleComponentSelect,
      handleUpdateComponent,
      handleUpdateAllComponents,
      handleToggleGroupMode,
      handleFillReferencePrice,
      handleFillAllPlatformPrices,
      startEdit,
      finishEdit,
      cancelEdit,
      getItemsPerPage,
      getExpandedItems,
      getExpandedTotal,
      handleExpandPageChange,
      handleRowClick,
      getRowStyle,
      openPreview,
      handleCardClick,
      loadMoreData
    }
  }
}
</script>

<style scoped>
/* 卡片视图样式 */
.card-container {
  width: 100%;
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
  overflow: visible;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 340px;
  cursor: pointer;
}

.inventory-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border-color: var(--el-color-primary);
}

.card-image {
  width: 100%;
  height: 150px;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: visible;
  flex-shrink: 0;
  position: relative;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
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
  pointer-events: none;
}

/* 挂件覆盖层 - 右上角 */
.pendant-overlay {
  position: absolute;
  top: 4px;
  right: 4px;
  z-index: 5;
  pointer-events: none;
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
  pointer-events: auto;
  cursor: pointer;
}

.sticker-item-overlay:hover {
  transform: scale(2);
  z-index: 10;
  border-color: rgba(76, 175, 80, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.7);
}

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
  pointer-events: auto;
  cursor: pointer;
}

.pendant-item-overlay:hover {
  transform: scale(2);
  z-index: 10;
  border-color: rgba(255, 215, 0, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.7);
}

.sticker-img-overlay,
.pendant-img-overlay {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.5));
}

.sticker-placeholder-overlay,
.pendant-placeholder-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 1rem;
  font-weight: bold;
}

.pendant-placeholder-overlay {
  color: #ffd700;
  font-size: 1.2rem;
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

.float-bar-container {
  width: 100%;
}

.float-value {
  color: #fff;
  font-family: monospace;
  font-size: 0.75rem;
  text-align: center;
  margin-top: 0.25rem;
}

.card-prices {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.3rem;
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

.card-footer {
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color);
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.rename-tag {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-icon {
  margin-right: 0.25rem;
}

.table-footer {
  padding: 1rem;
  text-align: center;
  color: #999;
  font-size: 0.875rem;
}

/* 表格视图样式 */
.table-wrapper {
  width: 100%;
}

.inventory-stats {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.grid {
  display: grid;
  gap: 1rem;
}

.grid-5 {
  grid-template-columns: repeat(5, 1fr);
}

@media (max-width: 1400px) {
  .grid-5 {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .grid-5 {
    grid-template-columns: 1fr;
  }
  
  .steam-id-select,
  .component-select,
  .search-input {
    min-width: unset;
    width: 100%;
    max-width: none;
  }
  
  .search-section :deep(.el-button) {
    flex: 1 1 calc(50% - 0.5rem);
    min-width: unset;
  }
  
  :deep(.el-table) {
    font-size: 0.75rem;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 0.5rem 0.25rem;
  }

  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .search-section :deep(.el-button) {
    flex: 1 1 100%;
  }
}

.stat-number {
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: bold;
  color: #fff;
  margin-top: clamp(0.5rem, 1vw, 0.625rem);
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

.weapon-image-cell {
  width: 100%;
  height: 100%;
  min-height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.weapon-img {
  width: 100%;
  height: auto;
  max-width: 100%;
  max-height: 90px;
  object-fit: contain;
}

.no-image {
  color: #666;
  font-size: 0.875rem;
}

.item-name-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-title {
  color: #fff;
  font-weight: 500;
}

.item-extras {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.sticker-list {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.sticker-item {
  width: 32px;
  height: 32px;
  border-radius: 2px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
}

.sticker-item:hover {
  transform: scale(1.1);
  border-color: rgba(76, 175, 80, 0.5);
  z-index: 10;
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
  color: #666;
  font-size: 0.75rem;
}

.pendant-list {
  display: flex;
  align-items: center;
}

.pendant-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 2px;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

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

/* 磨损值显示条 */
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
}

/* 磨损值指针箭头 */
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

.steam-id-select {
  min-width: 250px;
  max-width: 350px;
}

.component-select {
  min-width: 300px;
  max-width: 450px;
}

.search-input {
  min-width: 200px;
  flex: 1;
  max-width: 300px;
}

.pagination {
  margin-top: clamp(1rem, 3vw, 1.25rem);
  display: flex;
  justify-content: center;
}

.pagination-top {
  margin-top: 0;
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.group-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

:deep(.el-pagination) {
  background-color: transparent;
}

:deep(.el-pagination .el-pager li) {
  background-color: transparent;
  color: #fff;
  border: 1px solid #333;
}

:deep(.el-pagination .el-pager li:hover) {
  background-color: #333;
}

:deep(.el-pagination .el-pager li.is-active) {
  background-color: #4CAF50;
  color: #fff;
}

:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next) {
  background-color: transparent;
  color: #fff;
  border: 1px solid #333;
}

:deep(.el-pagination .btn-prev:hover),
:deep(.el-pagination .btn-next:hover) {
  background-color: #333;
}

:deep(.el-pagination .el-select .el-input__inner) {
  background-color: #484848 !important;
  color: #fff;
  border: 1px solid #333;
}

:deep(.el-pagination .el-input__inner) {
  background-color: #484848 !important;
  color: #fff;
  border: 1px solid #333;
}

:deep(.el-table) {
  background-color: transparent;
  color: #fff;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

:deep(.el-table th) {
  background-color: var(--bg-tertiary) !important;
  color: #fff;
  border-bottom: 1px solid var(--border-default);
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
}

:deep(.el-table td) {
  background-color: transparent !important;
  border-bottom: 1px solid var(--border-default);
  color: #fff;
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
}

:deep(.el-table tr:hover > td) {
  background-color: transparent !important;
}

:deep(.el-input__inner) {
  background-color: #1a1a1a;
  border-color: #333;
  color: #fff;
}

:deep(.el-select .el-input__inner) {
  background-color: #1a1a1a;
  border-color: #333;
  color: #fff;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  justify-content: center;
}

:deep(.el-button) {
  font-size: clamp(0.625rem, 1vw, 0.75rem);
  padding: clamp(0.375rem, 1vw, 0.5rem) clamp(0.5rem, 1.5vw, 0.75rem);
}

.stats-summary {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.search-section {
  margin-bottom: 1.5rem;
}

.search-stats-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-default) 20%, var(--border-default) 80%, transparent);
  margin: 1.5rem 0;
}

/* 展开行样式 */
:deep(.el-table__expand-column .cell) {
  display: none;
}

:deep(.el-table__expand-column) {
  width: 1px !important;
  padding: 0 !important;
}

:deep(.el-table__body-wrapper .el-table__row[style*="cursor: pointer"]:hover) {
  background-color: rgba(76, 175, 80, 0.1) !important;
}

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

.weapon-img-small {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

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

.sticker-img-overlay,
.pendant-img-overlay {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.5));
}

.sticker-placeholder-overlay,
.pendant-placeholder-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 0.8rem;
  font-weight: bold;
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
  width: 100%;
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

.expand-content-empty {
  padding: 1rem;
  text-align: center;
  background-color: var(--bg-secondary);
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
</style>

<style>
.el-loading-mask {
  background-color: rgba(26, 26, 26, 0.8) !important;
}

.el-loading-spinner {
  color: #409eff !important;
}

.el-loading-text {
  color: #fff !important;
}
</style>
