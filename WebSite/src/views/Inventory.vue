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
        <el-button type="primary" @click="loadInventoryData" :loading="loading">
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="success" @click="fetchSteamInventory" :loading="fetchingInventory" icon="Refresh" class="action-button">
          更新Steam库存
        </el-button>
        <el-button type="success" @click="fetchYYYPPrice" :loading="fetchingYYYPPrice" icon="Money" class="action-button">
          获取悠悠有品价格
        </el-button>
        <el-button type="success" @click="fetchBuffPrice" :loading="fetchingBuffPrice" icon="Money" class="action-button">
          获取BUFF价格
        </el-button>
        <el-button-group style="margin-left: auto;">
          <el-button 
            :type="displayMode === 'list' ? 'primary' : ''" 
            @click="displayMode = 'list'"
            icon="List"
          >
            列表
          </el-button>
          <el-button 
            :type="displayMode === 'card' ? 'primary' : ''" 
            @click="displayMode = 'card'"
            icon="Grid"
          >
            卡片
          </el-button>
        </el-button-group>
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
        :data="inventoryData"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        :row-style="{ backgroundColor: 'transparent' }"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        height="calc(100vh - 400px)"
        :default-sort="{ prop: 'buy_price', order: 'descending' }"
        @sort-change="handleSortChange"
      >
        <el-table-column 
          prop="order_time" 
          label="入库时间" 
          width="180" 
          sortable="custom"
        >
          <template #default="scope">
            <span v-if="scope.row.order_time" style="color: #9E9E9E;">
              {{ scope.row.order_time }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="weapon_name" label="武器" min-width="120" />
        <el-table-column prop="weapon_type" label="类型" min-width="100" />
        <el-table-column prop="item_name" label="饰品名称" min-width="250" show-overflow-tooltip />
        <el-table-column 
          prop="float_range" 
          label="磨损等级" 
          min-width="100" 
          sortable="custom"
        />
        <el-table-column
          prop="weapon_float"
          label="磨损值"
          min-width="220"
          sortable="custom"
        >
          <template #default="scope">
            <div v-if="scope.row.weapon_float">
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
          label="附加信息"
          width="250"
          fixed="right"
        >
          <template #default="scope">
            <div class="table-info-container">
              <div class="table-tags">
                <el-tooltip v-if="scope.row.remark" :content="scope.row.remark" placement="left" effect="dark">
                  <el-tag type="warning" size="small" style="cursor: help; margin: 2px;">
                    交易限制
                  </el-tag>
                </el-tooltip>
                <el-tooltip v-if="scope.row.rename" :content="`名称标签: ${scope.row.rename}`" placement="left" effect="dark">
                  <el-tag type="info" size="small" style="cursor: help; margin: 2px;">
                    🏷️{{ scope.row.rename.length > 6 ? scope.row.rename.substring(0, 6) + '...' : scope.row.rename }}
                  </el-tag>
                </el-tooltip>
                <el-tag v-if="scope.row.pendant" type="primary" size="small" style="margin: 2px;">
                  🎗️挂件
                </el-tag>
              </div>
              <!-- 贴纸图片显示 -->
              <div v-if="scope.row.sticker" class="sticker-images-table">
                <div
                  v-for="(sticker, index) in parseStickers(scope.row.sticker)"
                  :key="index"
                  class="sticker-item-table"
                  :title="sticker.name || '未知贴纸'"
                >
                  <img
                    v-if="sticker.image"
                    :src="sticker.image"
                    :alt="sticker.name"
                    class="sticker-img-table"
                    @error="(e) => e.target.style.display = 'none'"
                  />
                  <div v-else class="sticker-placeholder-table">?</div>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-footer">
        <span>共 {{ inventoryData.length }} 条数据</span>
        <span v-if="hasMore && !loadingMore" style="margin-left: 1rem; color: #999;">滚动加载更多...</span>
        <span v-if="loadingMore" style="margin-left: 1rem; color: #4CAF50;">正在加载更多...</span>
        <span v-if="!hasMore && inventoryData.length > 0" style="margin-left: 1rem; color: #999;">已加载全部数据</span>
      </div>
      <!-- 滚动触发元素 -->
      <div id="load-more-trigger" style="height: 1px;"></div>
    </div>

    <!-- 卡片显示 -->
    <div class="card-container" v-if="displayMode === 'card'">
      <div v-loading="loading" class="card-grid">
        <div
          v-for="item in inventoryData"
          :key="item.assetid"
          class="inventory-card"
          @click="openPreview(item)"
        >
          <div class="card-image">
            <img
              v-if="getWeaponImage(item.steam_hash_name)"
              :src="getWeaponImage(item.steam_hash_name)"
              :alt="item.item_name"
              loading="lazy"
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
                  :src="sticker.image"
                  :alt="sticker.name"
                  class="sticker-img-overlay"
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
                  :src="parsePendant(item.pendant).image"
                  :alt="parsePendant(item.pendant).name"
                  class="pendant-img-overlay"
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
              <!-- 磨损值显示条 -->
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
            </div>
            <div class="card-prices">
              <!-- 购入和Steam合并为一行 -->
              <div class="price-row" v-if="item.buy_price || item.steam_price || true">
                <div class="price-group">
                  <span class="price-label">购入:</span>
                  <span class="price-value buy-price" v-if="item.buy_price">¥{{ parseFloat(item.buy_price).toFixed(2) }}</span>
                  <span class="price-value" v-else style="color: #888;">-</span>
                </div>
                <div class="price-group" v-if="item.steam_price">
                  <span class="price-label">Steam:</span>
                  <span class="price-value">¥{{ parseFloat(item.steam_price).toFixed(2) }}</span>
                </div>
              </div>
              <!-- 悠悠和BUFF合并为一行 -->
              <div class="price-row" v-if="item.yyyp_price || item.buff_price">
                <div class="price-group" v-if="item.yyyp_price">
                  <span class="price-label">悠悠:</span>
                  <span
                    class="price-value"
                    :class="getPriceDiffClass(item.yyyp_price, item.buy_price)"
                  >
                    ¥{{ parseFloat(item.yyyp_price).toFixed(2) }}
                  </span>
                </div>
                <div class="price-group" v-if="item.buff_price">
                  <span class="price-label">BUFF:</span>
                  <span
                    class="price-value"
                    :class="getPriceDiffClass(item.buff_price, item.buy_price)"
                  >
                    ¥{{ parseFloat(item.buff_price).toFixed(2) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="card-footer">
              <div class="card-tags">
                <el-tag v-if="item.remark" type="warning" size="small">交易限制</el-tag>
                <el-tag v-if="item.rename" type="info" size="small" class="rename-tag">
                  <span class="tag-icon">🏷️</span>{{ item.rename }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="table-footer">
        <span>共 {{ inventoryData.length }} 条数据</span>
        <span v-if="hasMore && !loadingMore" style="margin-left: 1rem; color: #999;">滚动加载更多...</span>
        <span v-if="loadingMore" style="margin-left: 1rem; color: #4CAF50;">正在加载更多...</span>
        <span v-if="!hasMore && inventoryData.length > 0" style="margin-left: 1rem; color: #999;">已加载全部数据</span>
      </div>
      <!-- 滚动触发元素 -->
      <div id="load-more-trigger-card" style="height: 1px;"></div>
    </div>

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
                <el-tag v-if="previewItem.remark" type="warning" size="default">交易限制</el-tag>
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
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { API_CONFIG } from '@/config/api.js'

export default {
  name: 'Inventory',
  setup() {
    const loading = ref(false)
    const fetchingInventory = ref(false) // 获取库存中
    const fetchingYYYPPrice = ref(false) // 获取悠悠有品价格中
    const fetchingBuffPrice = ref(false) // 获取BUFF价格中
    const inventoryData = ref([])
    const searchText = ref('')
    const weaponTypeFilter = ref('')
    const floatRangeFilter = ref('')
    const displayMode = ref('card') // 默认卡片显示
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
    const sortConfig = ref({ prop: 'buy_price', order: 'desc' }) // 默认按购入价格降序排序

    // 预览弹窗相关
    const previewVisible = ref(false)
    const previewItem = ref(null)

    // API 基础地址
    const API_BASE = `${API_CONFIG.BASE_URL}/webInventoryV1`
    const CONFIG_API = `${API_CONFIG.BASE_URL}/configV1`

    const inventoryStats = computed(() => {
      // 基于后端返回的整库统计数据计算
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
      // 使用后端返回的整库购入价格统计
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
      // 基于后端整库统计的悠悠有品价格 + 购入总价计算
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
      // 基于后端整库统计的 BUFF 价格 + 购入总价计算（扣除2.5%手续费）
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
      // 基于后端整库统计的 Steam 价格 + 购入总价计算
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
          search: searchText.value,
          weapon_type: weaponTypeFilter.value,
          float_range: floatRangeFilter.value,
          limit: pageSize.value,
          offset: currentOffset.value
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
          if (sortConfig.value.prop) {
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
      })
    }

    const loadStats = async () => {
      try {
        const response = await axios.get(`${API_BASE}/inventory/stats/${selectedSteamId.value}`)
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

    const handleReset = () => {
      searchText.value = ''
      weaponTypeFilter.value = ''
      floatRangeFilter.value = ''
      sortConfig.value = { prop: '', order: '' }
      loadInventoryData(true) // 重置加载
    }


    // 统一的排序函数
    const applySorting = () => {
      if (!sortConfig.value.prop || !sortConfig.value.order) return
      
      const { prop, order } = sortConfig.value
      
      inventoryData.value.sort((a, b) => {
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

    // 生成卡片标题（组合显示）
    const getCardTitle = (item) => {
      const parts = []
      if (item.weapon_name) {
        parts.push(item.weapon_name)
      }
      if (item.item_name) {
        parts.push(item.item_name)
      }
      // 组合格式: "AK-47 | 轨道 Mk01 （崭新出厂）"
      let title = parts.join(' | ')
      if (item.float_range) {
        title += ` （${item.float_range}）`
      }
      return title
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

      return `/weapon_imgs/${imageName}`
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

    // 打开预览弹窗
    const openPreview = (item) => {
      previewItem.value = item
      previewVisible.value = true
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
            imageUrl = `/weapon_imgs/${imageName}`
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
          imageUrl = `/weapon_imgs/${imageName}`
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
        const statsResponse = await axios.get(
          `${API_CONFIG.BASE_URL}/webInventoryV1/inventory/stats/${selectedSteamId.value}`
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
    })

    return {
      loading,
      fetchingInventory,
      fetchingYYYPPrice,
      fetchingBuffPrice,
      inventoryData,
      inventoryStats,
      priceStats,
      yyypPriceStats,
      buffPriceStats,
      steamPriceStats,
      searchText,
      weaponTypeFilter,
      floatRangeFilter,
      displayMode,
      steamIdList,
      selectedSteamId,
      sortConfig,
      getCardTitle,
      getWeaponImage,
      handleImageError,
      getPriceDiffClass,
      parseStickers,
      getStickerCount,
      getStickerTooltip,
      loadInventoryData,
      loadMoreData,
      handleReset,
      handleSteamIdChange,
      handleSortChange,
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
      parsePendant
    }
  }
}
</script>

<style scoped>
.steam-id-select {
  min-width: 250px;
  max-width: 350px;
}

.search-input {
  min-width: 200px;
  flex: 1;
  max-width: 300px;
}

.type-select,
.wear-select {
  min-width: 120px;
  max-width: 180px;
}

.action-button {
  min-width: 140px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
}

.action-button :deep(.el-icon) {
  margin-right: 4px;
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
  border-color: var(--el-color-primary);
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
  .wear-select {
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
}

.preview-tags .el-tag {
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
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
}
</style>
