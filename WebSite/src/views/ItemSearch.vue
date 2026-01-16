<template>
  <div class="item-search-container">
    <!-- 搜索区域 - 固定在顶部 -->
    <div class="search-wrapper top-left">
      <div class="card search-card">
        <div class="search-section">
          <div class="search-controls compact">
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
            
            <el-select 
              v-model="selectedExterior" 
              placeholder="筛选外观" 
              class="exterior-select"
              clearable
              @change="handleExteriorChange"
            >
              <el-option label="全部外观" value="" />
              <el-option label="崭新出厂" value="崭新出厂">
                <span :style="{ color: '#4caf50' }">崭新出厂</span>
              </el-option>
              <el-option label="略有磨损" value="略有磨损">
                <span :style="{ color: '#8bc34a' }">略有磨损</span>
              </el-option>
              <el-option label="久经沙场" value="久经沙场">
                <span :style="{ color: '#ffc107' }">久经沙场</span>
              </el-option>
              <el-option label="破损不堪" value="破损不堪">
                <span :style="{ color: '#ff9800' }">破损不堪</span>
              </el-option>
              <el-option label="战痕累累" value="战痕累累">
                <span :style="{ color: '#f44336' }">战痕累累</span>
              </el-option>
            </el-select>
            
            <el-select 
              v-model="selectedStatTrak" 
              placeholder="StatTrak™" 
              class="stattrak-select"
              @change="handleStatTrakChange"
            >
              <el-option label="非StatTrak™" value="normal">
                <span>非StatTrak™</span>
              </el-option>
              <el-option label="StatTrak™" value="stattrak">
                <span :style="{ color: '#cf6a32' }">StatTrak™</span>
              </el-option>
              <el-option label="全部" value="" />
            </el-select>
            
            <el-input
              v-model="searchKeyword"
              placeholder="搜索饰品名称..."
              prefix-icon="Search"
              class="search-input"
              @keyup.enter="handleSearchWeapon"
              clearable
            />
            
            <div class="button-group">
              <el-button type="primary" @click="handleSearchWeapon" :loading="isSearching && searchSource === 'weapon'">
                搜索武器
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索结果表格 -->
    <div class="card table-card" v-if="searchResults.length > 0">
      <!-- 折叠/展开控制（始终显示） -->
      <div class="collapse-header" @click.stop="toggleSearchResults">
        <span class="collapse-title">
          <el-icon><CaretRight v-if="!showSearchResults" /><CaretBottom v-if="showSearchResults" /></el-icon>
          武器搜索结果 ({{ searchResults.length }} 件)
        </span>
        <div class="header-actions">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredResults.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            small
            style="margin-right: 15px;"
            @click.stop
          />
          <el-button-group style="margin-right: 10px;">
            <el-button 
              :type="displayMode === 'list' ? 'primary' : ''" 
              @click.stop="displayMode = 'list'"
              size="small"
            >
              列表
            </el-button>
            <el-button 
              :type="displayMode === 'card' ? 'primary' : ''" 
              @click.stop="displayMode = 'card'"
              size="small"
            >
              卡片
            </el-button>
          </el-button-group>
          <el-button 
            type="primary" 
            size="small" 
            :icon="Refresh" 
            @click.stop="handleRefreshSearch"
            :loading="isSearching && searchSource === 'weapon'"
          >
            刷新列表
          </el-button>
        </div>
      </div>
      
      <!-- 列表模式 -->
      <el-table 
        v-show="showSearchResults && displayMode === 'list'" 
        :data="paginatedResults" 
        style="width: 100%"
        :default-sort="{ prop: 'name', order: 'ascending' }"
        v-loading="isSearching"
        element-loading-text="搜索中..."
        element-loading-background="rgba(0, 0, 0, 0.8)"
      >
        <el-table-column type="index" label="#" width="60" align="center" />
        
        <el-table-column label="图片" width="120" align="center">
          <template #default="{ row }">
            <div class="weapon-image-cell">
              <img
                v-if="getWeaponImage(row.steam_hash_name)"
                :src="getWeaponImage(row.steam_hash_name)"
                :alt="row.item_name"
                class="weapon-img"
                @error="(e) => handleImageError(e, row.steam_hash_name)"
              />
              <span v-else class="no-image">无图</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="饰品名称" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <el-popover
              :visible="activePopoverRow === row"
              placement="bottom"
              :width="200"
              trigger="click"
            >
              <template #reference>
                <span class="clickable-item-name" @click="togglePopover(row)">
                  {{ row.market_listing_item_name }}
                </span>
              </template>
              <div class="search-platform-selector">
                <div class="selector-buttons">
                  <el-button 
                    type="warning" 
                    size="small" 
                    @click="selectPlatform(row, 'yyyp')"
                    :loading="isSearching && searchSource === 'yyyp'"
                  >
                    悠悠有品
                  </el-button>
                  <el-button 
                    type="info" 
                    size="small" 
                    class="buff-button"
                    @click="selectPlatform(row, 'buff')"
                    :loading="isSearching && searchSource === 'buff'"
                  >
                    BUFF
                  </el-button>
                  <el-button 
                    type="success" 
                    size="small" 
                    class="csfloat-button"
                    @click="selectPlatform(row, 'csfloat')"
                    :loading="isSearching && searchSource === 'csfloat'"
                  >
                    CsFloat
                  </el-button>
                  <el-button 
                    type="primary" 
                    size="small" 
                    class="all-button"
                    @click="selectPlatform(row, 'all')"
                    :loading="isSearching && searchSource === 'all'"
                  >
                    全部搜索
                  </el-button>
                </div>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        
        <el-table-column label="Steam Hash Name" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="hash-name-text">{{ row.steam_hash_name || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="weapon_type" label="武器类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.weapon_type || '-' }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="item_name" label="皮肤名称" width="180" align="center" show-overflow-tooltip />
        
        <el-table-column prop="Rarity" label="稀有度" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.Rarity" class="rarity-text" :style="{ color: getRarityColor(row.Rarity) }">
              {{ row.Rarity }}
            </span>
            <span v-else class="no-data">-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="yyyp_id" label="悠悠有品ID" width="120" align="center">
          <template #default="{ row }">
            <span class="id-text">{{ row.yyyp_id || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="buff_id" label="BUFF ID" width="100" align="center">
          <template #default="{ row }">
            <span class="id-text">{{ row.buff_id || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 卡片模式 -->
      <div v-show="showSearchResults && displayMode === 'card'" class="card-grid-container">
        <div class="card-grid">
          <div
            v-for="item in paginatedResults"
            :key="item.market_listing_item_name"
            class="search-result-card"
            @click="handleCardClick(item, $event)"
          >
              <div class="card-image">
                <!-- 左上角标签 -->
                <div class="card-badges">
                  <el-tag v-if="item.float_range" size="small" class="badge-item" :style="{ color: getFloatRangeColor(item.float_range) + ' !important', backgroundColor: 'rgba(0, 0, 0, 0.7)', borderColor: getFloatRangeColor(item.float_range) }">
                    {{ item.float_range }}
                  </el-tag>
                  <el-tag v-if="item.Rarity" size="small" class="badge-item" :style="{ color: getRarityColor(item.Rarity) + ' !important', backgroundColor: 'rgba(0, 0, 0, 0.7)', borderColor: getRarityColor(item.Rarity) }">
                    {{ item.Rarity }}
                  </el-tag>
                </div>
                
                <img
                  v-if="getWeaponImage(item.steam_hash_name)"
                  :src="getWeaponImage(item.steam_hash_name)"
                  :alt="item.item_name"
                  class="weapon-card-img"
                  @error="(e) => handleImageError(e, item.steam_hash_name)"
                />
                <div v-else class="image-placeholder">
                  <span>无图片</span>
                </div>
              </div>
              <div class="card-content">
                <div class="card-title" :title="item.market_listing_item_name">
                  {{ item.market_listing_item_name }}
                </div>
                <div class="card-info">
                  <div class="info-row" v-if="item.float_range">
                    <span class="info-label">磨损:</span>
                    <span class="float-range-text" :style="`color: ${getFloatRangeColor(item.float_range)} !important; font-weight: 600 !important;`">
                      {{ item.float_range }}
                    </span>
                  </div>
                  <div class="info-row" v-if="item.Rarity">
                    <span class="info-label">稀有度:</span>
                    <span class="rarity-text" :style="`color: ${getRarityColor(item.Rarity)} !important; font-weight: 600 !important;`">
                      {{ item.Rarity }}
                    </span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">类型:</span>
                    <span>{{ item.weapon_type || '-' }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">悠悠ID:</span>
                    <span>{{ item.yyyp_id || '-' }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">BUFF ID:</span>
                    <span>{{ item.buff_id || '-' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>

    <!-- BUFF商品列表 -->
    <div v-if="showBuffList" class="card buff-commodity-list">
      <!-- 折叠/展开控制头部 -->
      <div class="buff-collapse-header" @click.stop="toggleBuffList">
        <div class="buff-collapse-left">
          <el-icon class="collapse-icon">
            <CaretRight v-if="!showBuffTable" />
            <CaretBottom v-if="showBuffTable" />
          </el-icon>
          <span class="buff-collapse-title">BUFF商品列表</span>
          <el-button 
            type="primary" 
            size="small" 
            :icon="Refresh" 
            @click.stop="handleRefreshBuff"
            :loading="isSearching && searchSource === 'buff'"
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
            @click.stop="selectAllCommodities('buff')"
          >
            全选
          </el-button>
        </div>
        <div class="buff-weapon-info">
          <span class="weapon-name">{{ buffCurrentWeapon?.market_listing_item_name }}</span>
          <span class="weapon-id">商品ID: {{ buffCurrentWeapon?.buff_id }}</span>
          <span class="commodity-count">已加载: {{ buffCommodities.length }} 件</span>
          <span class="total-count">总数: {{ buffTotalCount }} 件</span>
          <span class="buy-count">求购: {{ buffBuyNum }} 件</span>
          <span class="rent-count">租赁: {{ buffRentNum }} 件</span>
        </div>
      </div>
      
      <!-- BUFF卡片模式 -->
      <div 
        v-show="showBuffTable" 
        class="commodity-card-grid buff-scroll-container" 
        v-loading="isSearching && searchSource === 'buff'" 
        element-loading-text="加载中..." 
        element-loading-background="rgba(0, 0, 0, 0.8)"
        @scroll="handleBuffScroll"
      >
        <div
          v-for="(item, index) in buffCommodities"
          :key="index"
          class="commodity-card"
          :class="{ 
            'selected': isCommoditySelected(item), 
            'multi-select-mode': isMultiSelectMode 
          }"
          @click="handleCommodityCardClick(item, 'buff', $event)"
        >
          <!-- 选中标记 -->
          <div v-if="isMultiSelectMode && isCommoditySelected(item)" class="selected-check">
            <el-icon><Check /></el-icon>
          </div>
          <div class="commodity-card-image">
            <img :src="item.iconUrl" class="commodity-icon" @error="handleImageError" />
            <!-- 模板号覆盖层 - 左上角 -->
            <div v-if="item.paintSeed" class="paint-seed-overlay" :title="`模板编号: ${item.paintSeed}`">
              #{{ item.paintSeed }}
            </div>
            <!-- 印花覆盖层 - 左下角 -->
            <div v-if="item.stickers && item.stickers.length > 0" class="sticker-overlay">
              <div
                v-for="(sticker, sIdx) in item.stickers"
                :key="sIdx"
                class="sticker-item-overlay"
                :title="sticker.name || '印花'"
              >
                <img
                  v-if="sticker.img_url"
                  :src="sticker.img_url"
                  :alt="sticker.name"
                  class="sticker-img-overlay"
                  @error="(e) => e.target.style.display = 'none'"
                />
                <div v-else class="sticker-placeholder-overlay">?</div>
              </div>
            </div>
          </div>
          <div class="commodity-card-content">
            <div class="commodity-card-info">
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
                {{ item.abrade }}
              </div>
              <div class="info-item">
                <span class="info-label">价格:</span>
                <span class="info-value price-highlight">¥{{ item.price }}</span>
              </div>
              <div class="info-item" v-if="item.description">
                <span class="info-label">描述:</span>
                <span class="info-value description-text" :title="item.description">{{ item.description }}</span>
              </div>
            </div>
          </div>
        </div>
        <!-- BUFF加载更多提示 -->
        <div class="load-more-indicator" v-if="buffCommodities.length > 0">
          <div v-if="buffLoadingMore" class="loading-more">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
          <div v-else-if="!buffHasMore" class="no-more-data">
            <span>没有更多数据了</span>
          </div>
          <div v-else class="scroll-hint">
            <span>下拉加载更多</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 悠悠有品商品列表 -->
    <div v-if="showYYYPList" class="card yyyp-commodity-list">
      <!-- 折叠/展开控制头部 -->
      <div class="yyyp-collapse-header" @click.stop="toggleYYYPList">
        <div class="yyyp-collapse-left">
          <el-icon class="collapse-icon">
            <CaretRight v-if="!showYYYPTable" />
            <CaretBottom v-if="showYYYPTable" />
          </el-icon>
          <span class="yyyp-collapse-title">悠悠有品商品列表</span>
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
        <div class="yyyp-weapon-info">
          <span class="weapon-name">{{ yyypCurrentWeapon?.market_listing_item_name }}</span>
          <span class="weapon-id">模板ID: {{ yyypCurrentWeapon?.yyyp_id }}</span>
          <span class="commodity-count">已加载: {{ yyypCommodities.length }} 件</span>
          <span class="total-count">总数: {{ yyypTotalCount }} 件</span>
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
            <!-- 模板号覆盖层 - 左上角 -->
            <div v-if="item.paintSeed" class="paint-seed-overlay" :title="`模板编号: ${item.paintSeed}`">
              #{{ item.paintSeed }}
            </div>
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
            <div class="commodity-card-info">
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
                {{ item.abrade }}
              </div>
              <div class="info-item">
                <span class="info-label">价格:</span>
                <span class="info-value price-highlight">¥{{ item.price }}</span>
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
                <span class="info-label">卖家:</span>
                <span class="info-value">{{ item.userNickName || '-' }}</span>
              </div>
            </div>
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
    </div>

    <!-- 多选模式下的操作栏 -->
    <div v-if="isMultiSelectMode && selectedCommodities.length > 0" class="multi-select-actions">
      <div class="selected-count">
        已选择 {{ selectedCommodities.length }} 件商品
        <span class="total-price">总价: ¥{{ selectedCommodities.reduce((sum, item) => sum + parseFloat(item.price || 0), 0).toFixed(2) }}</span>
      </div>
      <div class="action-buttons">
        <el-button type="success" @click="handleBatchBuy">批量购买</el-button>
        <el-button @click="clearCommoditySelection">清空选择</el-button>
      </div>
    </div>

    <!-- 无结果提示 -->
    <div v-if="searchResults.length === 0 && !isSearching && searchKeyword" class="card no-results-card">
      <el-empty description="未找到相关饰品" />
    </div>

    <!-- 卡片模式弹出框 -->
    <teleport to="body">
      <div 
        v-if="showCardPopover" 
        class="card-popover-overlay"
        @click="showCardPopover = false"
      >
        <div 
          class="card-popover-content"
          :style="{ 
            left: cardPopoverPosition.x + 'px', 
            top: cardPopoverPosition.y + 'px' 
          }"
          @click.stop
        >
          <div class="popover-buttons">
            <el-button 
              type="success" 
              size="small" 
              @click="selectPlatform(selectedCardItem, 'yyyp'); showCardPopover = false"
              :loading="isSearching && searchSource === 'yyyp'"
            >
              悠悠有品
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="selectPlatform(selectedCardItem, 'buff'); showCardPopover = false"
              :loading="isSearching && searchSource === 'buff'"
            >
              BUFF
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="selectPlatform(selectedCardItem, 'csfloat'); showCardPopover = false"
              :loading="isSearching && searchSource === 'csfloat'"
            >
              CsFloat
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="selectPlatform(selectedCardItem, 'all'); showCardPopover = false"
              :loading="isSearching && searchSource === 'all'"
            >
              全部搜索
            </el-button>
          </div>
        </div>
      </div>
    </teleport>

    <!-- 商品详情弹窗 -->
    <el-dialog
      v-model="commodityPreviewVisible"
      :title="commodityPreviewItem ? getCommodityTitle(commodityPreviewItem) : ''"
      width="800px"
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      class="commodity-preview-dialog"
    >
      <div v-if="commodityPreviewItem" class="commodity-preview-content">
        <div class="preview-main-layout">
          <!-- 左侧区域 -->
          <div class="preview-left-section">
            <!-- 图片区域 -->
            <div class="preview-image-section">
              <img :src="commodityPreviewItem.iconUrl" class="preview-image" @error="handleImageError" />
            </div>

            <!-- 磨损进度条 -->
            <div v-if="commodityPreviewItem.abrade" class="preview-float-section">
              <div class="preview-float-bar-container">
                <div class="float-bar">
                  <div class="float-segment fn"></div>
                  <div class="float-segment mw"></div>
                  <div class="float-segment ft"></div>
                  <div class="float-segment ww"></div>
                  <div class="float-segment bs"></div>
                  <div
                    class="float-pointer"
                    :style="{ left: `${parseFloat(commodityPreviewItem.abrade) * 100}%` }"
                  ></div>
                </div>
              </div>
              <div class="preview-float-value">{{ commodityPreviewItem.abrade }}</div>
              <div class="preview-float-range" v-if="getWearRange(commodityPreviewItem.abrade)">
                {{ getWearRange(commodityPreviewItem.abrade) }}
              </div>
            </div>

            <!-- 价格信息 -->
            <div class="preview-prices">
              <div class="preview-price-row">
                <div class="preview-price-item">
                  <span class="preview-price-label">价格:</span>
                  <span class="preview-price-value price-highlight">¥{{ commodityPreviewItem.price }}</span>
                </div>
                <div class="preview-price-item" v-if="commodityPreviewItem.paintSeed">
                  <span class="preview-price-label">模板:</span>
                  <span class="preview-price-value">#{{ commodityPreviewItem.paintSeed }}</span>
                </div>
              </div>
              <!-- 卖家信息 - 通用显示 -->
              <div class="preview-price-row">
                <div class="preview-price-item">
                  <span class="preview-price-label">卖家:</span>
                  <span class="preview-price-value">{{ commodityPreviewItem.userNickName || commodityPreviewItem.sellerName || '-' }}</span>
                </div>
              </div>
              <!-- BUFF特有信息 -->
              <template v-if="commodityPreviewType === 'buff'">
                <div class="preview-price-row" v-if="commodityPreviewItem.description">
                  <div class="preview-price-item full-width">
                    <span class="preview-price-label">描述:</span>
                    <span class="preview-price-value">{{ commodityPreviewItem.description }}</span>
                  </div>
                </div>
              </template>
              <!-- 悠悠有品特有信息 -->
              <template v-if="commodityPreviewType === 'yyyp'">
                <div class="preview-price-row" v-if="commodityPreviewItem.haveNameTag === 1">
                  <div class="preview-price-item full-width">
                    <span class="preview-price-label">改名:</span>
                    <span class="preview-price-value nametag-text" v-if="commodityPreviewItem.nameTagText">
                      {{ commodityPreviewItem.nameTagText }}
                    </span>
                    <span 
                      v-else
                      @click="fetchSingleNameTag(commodityPreviewItem)"
                      class="preview-price-value nametag-parse"
                    >
                      🏷️ 点击解析
                    </span>
                  </div>
                </div>
              </template>
            </div>
          </div>

          <!-- 右侧区域 - 印花和挂件列表 -->
          <div class="preview-right-section">
            <!-- 印花列表 -->
            <div v-if="commodityPreviewItem.stickers && commodityPreviewItem.stickers.length > 0" class="preview-sticker-list-section">
              <div class="preview-sticker-list">
                <div
                  v-for="(sticker, index) in commodityPreviewItem.stickers"
                  :key="index"
                  class="preview-sticker-list-item"
                >
                  <div class="preview-sticker-list-img-wrapper">
                    <img
                      v-if="sticker.TemplateHashName"
                      :src="getWeaponImage(sticker.TemplateHashName)"
                      :alt="sticker.Name"
                      class="preview-sticker-list-img"
                      @error="(e) => e.target.style.display = 'none'"
                    />
                    <img
                      v-else-if="sticker.ImgUrl || sticker.img_url"
                      :src="sticker.ImgUrl || sticker.img_url"
                      :alt="sticker.Name || sticker.name"
                      class="preview-sticker-list-img"
                      @error="(e) => e.target.style.display = 'none'"
                    />
                    <div v-else class="preview-sticker-list-placeholder">?</div>
                  </div>
                  <div class="preview-sticker-list-name">{{ sticker.Name || sticker.name || '未知印花' }}</div>
                </div>
              </div>
            </div>
            <!-- 挂件列表 -->
            <div v-if="commodityPreviewItem.pendants && commodityPreviewItem.pendants.length > 0" class="preview-pendant-list-section">
              <div class="preview-sticker-list">
                <div
                  v-for="(pendant, index) in commodityPreviewItem.pendants"
                  :key="'pendant-' + index"
                  class="preview-sticker-list-item pendant-item"
                >
                  <div class="preview-sticker-list-img-wrapper">
                    <img
                      v-if="pendant.steamHashName"
                      :src="getWeaponImage(pendant.steamHashName)"
                      :alt="pendant.name"
                      class="preview-sticker-list-img"
                      @error="(e) => e.target.style.display = 'none'"
                    />
                    <img
                      v-else-if="pendant.imgUrl"
                      :src="pendant.imgUrl"
                      :alt="pendant.name"
                      class="preview-sticker-list-img"
                      @error="(e) => e.target.style.display = 'none'"
                    />
                    <div v-else class="preview-sticker-list-placeholder">🎗️</div>
                  </div>
                  <div class="preview-sticker-list-name">{{ pendant.pendantSourceName || pendant.name || '挂件' }}</div>
                </div>
              </div>
            </div>
            <div v-if="(!commodityPreviewItem.stickers || commodityPreviewItem.stickers.length === 0) && (!commodityPreviewItem.pendants || commodityPreviewItem.pendants.length === 0)" class="preview-no-stickers">
              <span>无印花/挂件</span>
            </div>
          </div>
        </div>
        
        <!-- 右下角购买按钮 -->
        <div class="preview-bottom-right-button">
          <el-button type="success" @click="handleBuyCommodityFromPreview">购买</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CaretRight, CaretBottom, Refresh, Check, Loading } from '@element-plus/icons-vue'
import { API_CONFIG, apiUrls } from '@/config/api.js'

export default {
  name: 'ItemSearch',
  components: {
    CaretRight,
    CaretBottom,
    Refresh,
    Check
  },
  setup() {
    const searchKeyword = ref('')
    const searchResults = ref([])
    const isSearching = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const searchSource = ref('') // 'yyyp' 或 'buff'
    const steamIdList = ref([])
    const selectedSteamId = ref('')
    const selectedExterior = ref('') // 选择的外观筛选
    const selectedStatTrak = ref('normal') // 选择的StatTrak筛选，默认非StatTrak™
    const showSearchResults = ref(false) // 是否展开搜索结果
    const displayMode = ref('card') // 显示模式：'list' 或 'card'，默认卡片模式
    const image404Cache = ref(new Set()) // 图片404缓存
    const activePopoverRow = ref(null) // 当前激活的 popover 行
    
    // 卡片模式弹出框
    const showCardPopover = ref(false)
    const cardPopoverPosition = ref({ x: 0, y: 0 })
    const selectedCardItem = ref(null)
    
    // 商品详情弹窗
    const commodityPreviewVisible = ref(false)
    const commodityPreviewItem = ref(null)
    const commodityPreviewType = ref('') // 'buff' 或 'yyyp'
    
    // BUFF商品列表
    const buffCommodities = ref([])
    const buffCurrentWeapon = ref(null)
    const buffTotalCount = ref(0)  // 在售总数量
    const buffBuyNum = ref(0)  // 求购数量
    const buffRentNum = ref(0)  // 租赁数量
    const showBuffList = ref(false)
    const showBuffTable = ref(true)  // 控制BUFF表格的展开/折叠
    const buffCurrentPage = ref(1)  // BUFF分页当前页
    const buffPageSize = ref(5)  // BUFF每页显示5条
    const buffLoadingMore = ref(false)  // BUFF是否正在加载更多
    const buffHasMore = ref(true)  // BUFF是否还有更多数据
    const buffTotalPage = ref(1)  // BUFF总页数
    
    // 悠悠有品商品列表
    const yyypCommodities = ref([])
    const yyypCurrentWeapon = ref(null)
    const yyypTotalCount = ref(0)  // 在售总数量
    const showYYYPList = ref(false)
    const showYYYPTable = ref(true)  // 控制悠悠有品表格的展开/折叠
    const yyypCurrentPage = ref(1)  // 悠悠有品分页当前页
    const yyypPageSize = ref(50)  // 悠悠有品每页显示50条
    const yyypLoadingMore = ref(false)  // 是否正在加载更多
    const yyypHasMore = ref(true)  // 是否还有更多数据
    
    // 多选模式相关
    const isMultiSelectMode = ref(false)  // 是否开启多选模式
    const selectedCommodities = ref([])   // 选中的商品列表
    const selectedCommodityType = ref('') // 选中商品的类型 'buff' 或 'yyyp'
    
    // 图片缓存 - 存储已加载的图片URL
    const imageCache = new Set()
    
    // API 基础地址
    const API_BASE = `${API_CONFIG.BASE_URL}/webInventoryV1`

    // 计算属性 - 筛选后的结果
    const filteredResults = computed(() => {
      let results = searchResults.value
      
      // 根据选择的外观筛选（使用 float_range 字段）
      if (selectedExterior.value) {
        results = results.filter(item => {
          const floatRange = item.float_range || ''
          return floatRange === selectedExterior.value
        })
      }
      
      // 根据选择的StatTrak筛选
      if (selectedStatTrak.value === 'stattrak') {
        // 只显示StatTrak™饰品
        results = results.filter(item => {
          const itemName = item.market_listing_item_name || ''
          return itemName.includes('StatTrak™') || itemName.includes('（StatTrak™）')
        })
      } else if (selectedStatTrak.value === 'normal') {
        // 只显示非StatTrak™饰品
        results = results.filter(item => {
          const itemName = item.market_listing_item_name || ''
          return !itemName.includes('StatTrak™') && !itemName.includes('（StatTrak™）')
        })
      }
      // 如果是空值''，显示全部
      
      return results
    })

    // 计算属性 - 分页结果
    const paginatedResults = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredResults.value.slice(start, end)
    })

    // 计算属性 - BUFF商品分页结果
    const paginatedBuffCommodities = computed(() => {
      const start = (buffCurrentPage.value - 1) * buffPageSize.value
      const end = start + buffPageSize.value
      return buffCommodities.value.slice(start, end)
    })

    // 计算属性 - 悠悠有品商品分页结果
    const paginatedYYYPCommodities = computed(() => {
      const start = (yyypCurrentPage.value - 1) * yyypPageSize.value
      const end = start + yyypPageSize.value
      return yyypCommodities.value.slice(start, end)
    })

    // 预加载图片（相同URL只加载一次）
    const preloadImages = (commodityList) => {
      const uniqueUrls = new Set()
      
      // 收集所有唯一的图片URL
      commodityList.forEach(item => {
        if (item.iconUrl && !imageCache.has(item.iconUrl)) {
          uniqueUrls.add(item.iconUrl)
        }
      })
      
      // 预加载未缓存的图片
      uniqueUrls.forEach(url => {
        const img = new Image()
        img.onload = () => {
          imageCache.add(url)
          console.log(`图片已缓存: ${url}`)
        }
        img.onerror = () => {
          console.error(`图片加载失败: ${url}`)
        }
        img.src = url
      })
      
      console.log(`开始预加载 ${uniqueUrls.size} 张唯一图片，已缓存 ${imageCache.size} 张`)
    }

    // 实时搜索武器名称
    const querySearchAsync = async (queryString, cb) => {
      if (!queryString || queryString.trim().length === 0) {
        cb([])
        return
      }

      try {
        const response = await axios.get(apiUrls.searchWeapon(queryString.trim()))
        if (response.data.success && response.data.data) {
          const results = response.data.data.map(name => ({
            value: name
          }))
          cb(results)
        } else {
          cb([])
        }
      } catch (error) {
        console.error('搜索武器名称失败:', error)
        cb([])
      }
    }

    // 选择搜索建议
    const handleSelect = (item) => {
      searchKeyword.value = item.value
      console.log('已选择:', item.value)
    }

    // 搜索武器详情
    const handleSearchWeapon = async () => {
      if (!searchKeyword.value.trim()) {
        ElMessage.warning('请输入搜索关键词')
        return
      }

      isSearching.value = true
      searchSource.value = 'weapon'
      currentPage.value = 1
      
      try {
        console.log('搜索武器:', searchKeyword.value)
        
        const response = await axios.get(apiUrls.searchWeaponDetail(searchKeyword.value.trim()))
        
        if (response.data.success) {
          searchResults.value = response.data.data || []
          
          if (searchResults.value.length === 0) {
            ElMessage.info('未找到匹配的武器')
            showSearchResults.value = false
          } else {
            ElMessage.success(`找到 ${searchResults.value.length} 件武器`)
            showSearchResults.value = true  // 搜索成功后自动展开
          }
        } else {
          ElMessage.error('搜索失败: ' + (response.data.error || '未知错误'))
          searchResults.value = []
          showSearchResults.value = false
        }
        
      } catch (error) {
        console.error('搜索武器失败:', error)
        ElMessage.error('搜索失败: ' + (error.response?.data?.error || error.message))
        searchResults.value = []
        showSearchResults.value = false
      } finally {
        isSearching.value = false
      }
    }

    // 刷新搜索结果
    const handleRefreshSearch = async () => {
      if (!searchKeyword.value.trim()) {
        ElMessage.warning('请先输入搜索关键词')
        return
      }

      ElMessage.info('正在刷新数据...')
      await handleSearchWeapon()
    }

    // 加载Steam ID列表
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

    // Steam ID 改变处理
    const handleSteamIdChange = (value) => {
      console.log('Steam ID已改变:', value)
      selectedSteamId.value = value
    }

    // 外观筛选改变处理
    const handleExteriorChange = (value) => {
      console.log('外观筛选已改变:', value)
      selectedExterior.value = value
      currentPage.value = 1 // 重置到第一页
    }

    // StatTrak筛选改变处理
    const handleStatTrakChange = (value) => {
      console.log('StatTrak筛选已改变:', value)
      selectedStatTrak.value = value
      currentPage.value = 1 // 重置到第一页
    }

    // 处理从高级搜索组件选择单个武器
    const handleSelectWeaponFromSearch = (weapon) => {
      console.log('从高级搜索选择武器:', weapon)
      // 将选中的武器添加到搜索结果中
      const exists = searchResults.value.some(item => 
        item.market_listing_item_name === weapon.market_listing_item_name
      )
      
      if (!exists) {
        searchResults.value.push(weapon)
        ElMessage.success(`已添加: ${weapon.market_listing_item_name}`)
      } else {
        ElMessage.warning('该武器已在列表中')
      }
      
      showSearchResults.value = true
    }

    // 处理从高级搜索组件选择全部武器
    const handleSelectAllWeaponsFromSearch = (weapons) => {
      console.log('从高级搜索添加全部武器:', weapons.length)
      let addedCount = 0
      
      weapons.forEach(weapon => {
        const exists = searchResults.value.some(item => 
          item.market_listing_item_name === weapon.market_listing_item_name
        )
        
        if (!exists) {
          searchResults.value.push(weapon)
          addedCount++
        }
      })
      
      if (addedCount > 0) {
        ElMessage.success(`成功添加 ${addedCount} 件武器`)
        showSearchResults.value = true
      } else {
        ElMessage.info('所有武器已在列表中')
      }
    }

    // 刷新悠悠有品商品列表
    const handleRefreshYYYP = async () => {
      if (!yyypCurrentWeapon.value) {
        ElMessage.warning('无法刷新，请重新选择武器')
        return
      }

      yyypCurrentPage.value = 1  // 重置分页到第一页
      ElMessage.info('正在刷新悠悠有品商品数据...')
      await handleSearchYYYPByRow(yyypCurrentWeapon.value)
    }
    
    // 刷新BUFF商品列表
    const handleRefreshBuff = async () => {
      if (!buffCurrentWeapon.value) {
        ElMessage.warning('无法刷新，请重新选择武器')
        return
      }

      buffCurrentPage.value = 1  // 重置分页到第一页
      ElMessage.info('正在刷新BUFF商品数据...')
      await handleSearchBuffByRow(buffCurrentWeapon.value)
    }
    
    // 切换BUFF表格的展开/折叠
    const toggleBuffList = () => {
      showBuffTable.value = !showBuffTable.value
    }
    
    // 购买BUFF商品（暂未对接）
    const handleBuyBuffCommodity = (commodity) => {
      console.log('购买BUFF商品:', commodity)
      ElMessage.info(`购买功能开发中... 订单ID: ${commodity.id}`)
      // TODO: 对接BUFF购买接口
    }

    // 获取稀有度类型（根据CS:GO品质颜色）
    const getRarityType = (rarity) => {
      if (!rarity) return ''
      // 不使用Element Plus的type，使用自定义颜色
      return ''
    }
    
    // 获取稀有度颜色样式
    const getRarityColor = (rarity) => {
      if (!rarity) return ''
      
      // 移除"级"后缀进行匹配
      const normalizedRarity = rarity.replace(/级$/, '')
      
      const rarityColorMap = {
        '违禁': '#e4ae39',      // 金色
        '非凡': '#e4ae39',      // 金色
        '隐秘': '#eb4b4b',      // 红色
        '保密': '#d32ce6',      // 紫色/粉色
        '受限': '#8847ff',      // 紫色
        '军规': '#4b69ff',      // 蓝色
        '工业': '#5e98d9',      // 浅蓝色
        '消费': '#b0c3d9',      // 灰蓝色
        '普通': '#b0c3d9'       // 灰蓝色
      }
      return rarityColorMap[normalizedRarity] || '#fff'
    }

    // 获取武器类型颜色样式
    const getWeaponTypeColor = (weaponType) => {
      if (!weaponType) return '#909399'
      const typeColorMap = {
        '手枪': '#67c23a',        // 绿色
        '步枪': '#409eff',        // 蓝色
        '狙击步枪': '#e6a23c',    // 橙色
        '冲锋枪': '#909399',      // 灰色
        '霰弹枪': '#f56c6c',      // 红色
        '机枪': '#c45656',        // 深红色
        '挂件': '#d4a5ff',        // 浅紫色
        '挂件（纪念品）': '#ffd700', // 金色
        '匕首': '#ff4757',        // 亮红色
        '手套': '#ffa502',        // 橙黄色
        '探员': '#5f27cd',        // 紫色
        '印花': '#48dbfb',        // 青色
        '涂鸦': '#ff6348',        // 珊瑚红
        '音乐盒': '#1dd1a1',      // 青绿色
        '收藏品': '#ee5a6f',      // 粉红色
        '容器': '#c8d6e5'         // 浅灰蓝色
      }
      return typeColorMap[weaponType] || '#909399'
    }

    // 获取磨损等级的标签类型
    const getFloatRangeType = (floatRange) => {
      if (!floatRange) return ''
      const typeMap = {
        '崭新出厂': 'success',
        '略有磨损': 'success',
        '久经沙场': 'warning',
        '破损不堪': 'warning',
        '战痕累累': 'danger'
      }
      return typeMap[floatRange] || ''
    }

    // 获取磨损等级的颜色
    const getFloatRangeColor = (floatRange) => {
      if (!floatRange) return '#fff'
      const colorMap = {
        '崭新出厂': '#4caf50',      // 绿色 - Factory New
        '略有磨损': '#8bc34a',      // 浅绿色 - Minimal Wear
        '久经沙场': '#ffc107',      // 黄色 - Field-Tested
        '破损不堪': '#ff9800',      // 橙色 - Well-Worn
        '战痕累累': '#f44336'       // 红色 - Battle-Scarred
      }
      return colorMap[floatRange] || '#fff'
    }

    // 根据磨损值返回颜色（用于进度条）
    const getWearColor = (abrade) => {
      if (!abrade) return '#4caf50'
      const wear = parseFloat(abrade)
      if (wear <= 0.07) return '#4caf50'      // 崭新出厂 - 绿色
      if (wear <= 0.15) return '#8bc34a'      // 略有磨损 - 浅绿色
      if (wear <= 0.38) return '#ffc107'      // 久经沙场 - 黄色
      if (wear <= 0.45) return '#ff9800'      // 破损不堪 - 橙色
      return '#f44336'                        // 战痕累累 - 红色
    }

    // 根据磨损值返回磨损等级名称
    const getWearRange = (abrade) => {
      if (!abrade) return ''
      const wear = parseFloat(abrade)
      if (wear <= 0.07) return '崭新出厂'
      if (wear <= 0.15) return '略有磨损'
      if (wear <= 0.38) return '久经沙场'
      if (wear <= 0.45) return '破损不堪'
      return '战痕累累'
    }

    // 获取外观（磨损）颜色样式
    const getExteriorColor = (itemName) => {
      if (!itemName) return '#fff'
      
      const exteriorColorMap = {
        '崭新出厂': '#4caf50',      // 绿色 - Factory New
        '略有磨损': '#8bc34a',      // 浅绿色 - Minimal Wear
        '久经沙场': '#ffc107',      // 黄色 - Field-Tested
        '破损不堪': '#ff9800',      // 橙色 - Well-Worn
        '战痕累累': '#f44336'       // 红色 - Battle-Scarred
      }
      
      // 检查饰品名称中是否包含外观关键词
      for (const [exterior, color] of Object.entries(exteriorColorMap)) {
        if (itemName.includes(exterior) || itemName.includes(`(${exterior})`)) {
          return color
        }
      }
      
      return '#fff' // 默认白色
    }

    // 通过行数据搜索悠悠有品
    const handleSearchYYYPByRow = async (row) => {
      console.log('=== 开始执行 handleSearchYYYPByRow ===')
      console.log('row数据:', row)
      console.log('row.yyyp_id:', row.yyyp_id)
      console.log('selectedSteamId.value:', selectedSteamId.value)
      
      if (!row.yyyp_id) {
        console.log('没有yyyp_id，退出')
        ElMessage.warning('该武器没有悠悠有品ID')
        return
      }

      if (!selectedSteamId.value) {
        console.log('没有选择Steam账号，退出')
        ElMessage.warning('请先选择Steam账号')
        return
      }

      console.log('通过验证，开始请求')
      isSearching.value = true
      searchSource.value = 'yyyp'
      
      try {
        console.log('搜索悠悠有品:', row.market_listing_item_name, 'ID:', row.yyyp_id, 'SteamID:', selectedSteamId.value)
        
        // 构建请求数据
        const requestData = {
          steamId: selectedSteamId.value || '',
          yyypId: row.yyyp_id,
          pageIndex: 1,
          pageSize: 50
        }
        
        const apiUrl = `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getCommoditiesByTemplateId`
        
        console.log('请求URL:', apiUrl)
        console.log('请求数据:', requestData)
        
        // 调用悠悠有品商品列表API（使用Spider服务器地址）
        const response = await axios.post(apiUrl, requestData)
        
        console.log('API响应:', response.data)
        
        if (response.data.success) {
          const parsedData = response.data.data
          console.log('获取到悠悠有品已解析数据:', parsedData)
          
          // 直接使用Spider解析后的数据
          const commodityList = parsedData.commodityList || []
          const totalCount = parsedData.totalCount || 0
          console.log('商品列表:', commodityList)
          console.log('在售总数:', totalCount)
          
          // 更新状态，显示商品列表
          yyypCurrentWeapon.value = row
          yyypCommodities.value = commodityList
          yyypTotalCount.value = totalCount
          yyypCurrentPage.value = 1  // 重置分页到第一页
          yyypHasMore.value = commodityList.length < totalCount  // 判断是否还有更多
          showYYYPList.value = true
          showSearchResults.value = false  // 折叠搜索结果
          
          ElMessage.success(`成功获取 ${commodityList.length} 条商品数据，在售总数: ${totalCount}`)
          
          // 预加载图片（相同URL只加载一次）
          preloadImages(commodityList)
          
          // 滚动到商品列表区域
          setTimeout(() => {
            const listElement = document.querySelector('.yyyp-commodity-list')
            if (listElement) {
              listElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
            }
          }, 100)
          
          // 自动批量获取改名信息
          fetchAllNameTags(commodityList)
        } else {
          console.error('API返回失败:', response.data)
          ElMessage.error(response.data.message || '获取商品列表失败')
        }
        
      } catch (error) {
        console.error('搜索悠悠有品失败 - 完整错误:', error)
        console.error('错误响应:', error.response)
        console.error('错误数据:', error.response?.data)
        
        const errorMessage = error.response?.data?.message || error.message || '搜索失败，请检查网络连接'
        ElMessage.error(errorMessage)
      } finally {
        console.log('请求完成，重置加载状态')
        isSearching.value = false
        searchSource.value = ''
      }
    }

    // 悠悠有品加载更多
    const loadMoreYYYPCommodities = async () => {
      if (yyypLoadingMore.value || !yyypHasMore.value || !yyypCurrentWeapon.value) {
        return
      }
      
      yyypLoadingMore.value = true
      const nextPage = yyypCurrentPage.value + 1
      
      try {
        console.log(`加载悠悠有品第 ${nextPage} 页数据`)
        
        const requestData = {
          steamId: selectedSteamId.value || '',
          yyypId: yyypCurrentWeapon.value.yyyp_id,
          pageIndex: nextPage,
          pageSize: 50
        }
        
        const apiUrl = `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getCommoditiesByTemplateId`
        const response = await axios.post(apiUrl, requestData)
        
        if (response.data.success) {
          const parsedData = response.data.data
          const newCommodities = parsedData.commodityList || []
          
          if (newCommodities.length > 0) {
            // 追加到现有列表
            yyypCommodities.value = [...yyypCommodities.value, ...newCommodities]
            yyypCurrentPage.value = nextPage
            
            // 判断是否还有更多
            yyypHasMore.value = yyypCommodities.value.length < yyypTotalCount.value
            
            console.log(`加载了 ${newCommodities.length} 条数据，当前共 ${yyypCommodities.value.length} 条`)
            
            // 预加载新图片
            preloadImages(newCommodities)
            
            // 获取新商品的改名信息
            fetchAllNameTags(newCommodities)
          } else {
            yyypHasMore.value = false
          }
        }
      } catch (error) {
        console.error('加载更多失败:', error)
        ElMessage.error('加载更多失败')
      } finally {
        yyypLoadingMore.value = false
      }
    }

    // 悠悠有品滚动事件处理
    const handleYYYPScroll = (event) => {
      const target = event.target
      const scrollTop = target.scrollTop
      const scrollHeight = target.scrollHeight
      const clientHeight = target.clientHeight
      
      // 当滚动到底部附近时（距离底部50px）加载更多
      if (scrollHeight - scrollTop - clientHeight < 50) {
        loadMoreYYYPCommodities()
      }
    }

    // BUFF加载更多
    const loadMoreBuffCommodities = async () => {
      if (buffLoadingMore.value || !buffHasMore.value || !buffCurrentWeapon.value) {
        return
      }
      
      buffLoadingMore.value = true
      const nextPage = buffCurrentPage.value + 1
      
      try {
        console.log(`加载BUFF第 ${nextPage} 页数据`)
        
        const requestData = {
          steamId: selectedSteamId.value || '',
          goodsId: buffCurrentWeapon.value.buff_id,
          pageIndex: nextPage
        }
        
        const apiUrl = `${API_CONFIG.SPIDER_BASE_URL}/buffSpiderV1/getCommoditiesByGoodsId`
        const response = await axios.post(apiUrl, requestData)
        
        if (response.data.success) {
          const parsedData = response.data.data
          const newCommodities = parsedData.commodityList || []
          
          if (newCommodities.length > 0) {
            // 追加到现有列表
            buffCommodities.value = [...buffCommodities.value, ...newCommodities]
            buffCurrentPage.value = nextPage
            
            // 判断是否还有更多
            buffHasMore.value = nextPage < buffTotalPage.value
            
            console.log(`加载了 ${newCommodities.length} 条数据，当前共 ${buffCommodities.value.length} 条`)
            
            // 预加载新图片
            preloadImages(newCommodities)
          } else {
            buffHasMore.value = false
          }
        }
      } catch (error) {
        console.error('BUFF加载更多失败:', error)
        ElMessage.error('加载更多失败')
      } finally {
        buffLoadingMore.value = false
      }
    }

    // BUFF滚动事件处理
    const handleBuffScroll = (event) => {
      const target = event.target
      const scrollTop = target.scrollTop
      const scrollHeight = target.scrollHeight
      const clientHeight = target.clientHeight
      
      // 当滚动到底部附近时（距离底部50px）加载更多
      if (scrollHeight - scrollTop - clientHeight < 50) {
        loadMoreBuffCommodities()
      }
    }

    // 查看商品详情（暂未对接）
    const handleViewDetail = (commodity) => {
      console.log('查看商品详情:', commodity)
      ElMessage.info(`查看详情功能开发中... 商品ID: ${commodity.id}`)
      // TODO: 对接查看详情接口
    }

    // 购买商品
    const handleBuyCommodity = async (commodity) => {
      console.log('购买商品:', commodity)
      
      // 确认购买
      try {
        await ElMessageBox.confirm(
          `确认购买该商品吗？\n\n商品：${commodity.commodityName}\n价格：¥${commodity.price}\n磨损：${commodity.abrade || '-'}`,
          '确认购买',
          {
            confirmButtonText: '确认购买',
            cancelButtonText: '取消',
            type: 'warning',
            distinguishCancelAndClose: true
          }
        )
      } catch (error) {
        // 用户取消
        ElMessage.info('已取消购买')
        return
      }
      
      // 开始购买流程
      const loadingMessage = ElMessage({
        message: '正在创建订单...',
        type: 'info',
        duration: 0,
        customClass: 'buy-loading-message'
      })
      
      try {
        const requestData = {
          steamId: selectedSteamId.value,
          commodityId: commodity.id,
          buyQuantity: 1,
          price: commodity.price,  // 添加商品价格
          autoConfirmPayment: true,  // 自动使用余额支付
          pollPayment: true  // 轮询支付状态
        }
        
        console.log('购买请求数据:', requestData)
        
        // 调用完整购买接口（创建订单+自动支付）
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/buyCommodity`,
          requestData
        )
        
        console.log('购买响应:', response.data)
        
        loadingMessage.close()
        
        if (response.data.success) {
          const orderData = response.data.data?.order || {}
          const paymentStatus = response.data.data?.payment_status || {}
          const orderNo = orderData.orderNo || '未知'
          const paymentAmount = commodity.price || '未知'
          
          // 检查支付状态
          const payStatus = paymentStatus.payStatus
          let message = ''
          
          if (payStatus === 2) {
            // 支付成功
            message = `购买成功！\n\n订单号：${orderNo}\n金额：¥${paymentAmount}\n状态：支付成功✅\n\n饰品将发送至您的库存。`
          } else if (payStatus === 1) {
            // 支付处理中
            message = `订单已创建！\n\n订单号：${orderNo}\n金额：¥${paymentAmount}\n状态：支付处理中⏳\n\n请稍后查看订单状态。`
          } else {
            // 订单创建成功但支付未完成
            message = `订单创建成功！\n\n订单号：${orderNo}\n金额：¥${paymentAmount}\n\n已自动使用余额支付，请稍后查看订单状态。`
          }
          
          // 显示购买成功信息
          ElMessageBox.alert(
            message,
            '购买完成',
            {
              confirmButtonText: '知道了',
              type: 'success',
              callback: () => {
                ElMessage.success(payStatus === 2 ? '购买成功！' : '订单已创建')
              }
            }
          )
        } else {
          ElMessageBox.alert(
            `购买失败：${response.data.message || '未知错误'}\n\n请检查配置或稍后重试。`,
            '购买失败',
            {
              confirmButtonText: '知道了',
              type: 'error'
            }
          )
        }
      } catch (error) {
        loadingMessage.close()
        console.error('购买商品失败:', error)
        
        const errorMessage = error.response?.data?.message || error.message || '网络错误，请稍后重试'
        
        ElMessageBox.alert(
          `购买失败：${errorMessage}`,
          '购买失败',
          {
            confirmButtonText: '知道了',
            type: 'error'
          }
        )
      }
    }

    // 批量获取改名信息（自动调用，只获取第一条）
    const fetchAllNameTags = async (commodityList) => {
      // 筛选出有改名标签的商品
      const commoditiesWithNameTag = commodityList.filter(item => item.haveNameTag === 1)
      
      if (commoditiesWithNameTag.length === 0) {
        console.log('没有需要获取改名信息的商品')
        return
      }

      // 只自动获取第一条
      console.log(`共有 ${commoditiesWithNameTag.length} 个商品有改名标签，自动获取第一个`)
      
      const commodity = commoditiesWithNameTag[0]
      
      try {
        console.log(`正在获取商品 ${commodity.id} 的改名信息`)
        
        // 调用接口获取详细信息
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getWeaponDetail`,
          {
            steamId: selectedSteamId.value,
            id: commodity.id
          }
        )

        if (response.data.success && response.data.data) {
          const detailData = response.data.data.Data
          const nameTags = detailData.NameTags || []
          
          // 缓存改名信息到商品对象中
          commodity.nameTags = nameTags
          commodity.nameTagText = nameTags.length > 0 ? nameTags[0].replace(/^名称标签：[""]?|[""]$/g, '') : ''
          
          console.log(`商品 ${commodity.id} 改名信息:`, nameTags)
        } else {
          console.error(`获取商品 ${commodity.id} 改名信息失败:`, response.data.message)
        }
      } catch (error) {
        console.error(`获取商品 ${commodity.id} 改名信息异常:`, error)
      }
      
      console.log(`自动获取改名信息完成`)
    }

    // 获取单个商品的改名信息（点击按钮时调用）
    const fetchSingleNameTag = async (commodity) => {
      try {
        // 设置加载状态
        commodity.nameTagLoading = true

        console.log('正在获取改名信息，商品ID:', commodity.id)

        // 调用接口获取详细信息
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getWeaponDetail`,
          {
            steamId: selectedSteamId.value,
            id: commodity.id
          }
        )

        console.log('改名信息响应:', response.data)

        if (response.data.success && response.data.data) {
          const detailData = response.data.data.Data
          const nameTags = detailData.NameTags || []
          
          // 缓存改名信息到商品对象中
          commodity.nameTags = nameTags
          commodity.nameTagText = nameTags.length > 0 ? nameTags[0].replace(/^名称标签：[""]?|[""]$/g, '') : ''

          if (nameTags.length === 0) {
            ElMessage.info('该商品没有改名信息')
          }
        } else {
          ElMessage.error('获取改名信息失败: ' + (response.data.message || '未知错误'))
        }
      } catch (error) {
        console.error('获取改名信息失败:', error)
        ElMessage.error('获取改名信息失败: ' + (error.response?.data?.message || error.message))
      } finally {
        commodity.nameTagLoading = false
      }
    }

    // 显示印花信息对话框
    const showStickersDialog = (commodity) => {
      const stickers = commodity.stickers || []
      
      if (stickers.length === 0) {
        ElMessage.info('该商品没有印花')
        return
      }

      // 最多显示5个印花
      const displayStickers = stickers.slice(0, 5)

      // 构建印花信息HTML - 横向平铺展示（自适应宽度）
      let stickersHtml = `
        <div style="padding: 20px;">
          <div style="text-align: center; margin-bottom: 20px;">
            <h4 style="margin: 0 0 10px 0; color: #303133; font-size: 16px;">${commodity.commodityName}</h4>
            <p style="margin: 0; color: #909399; font-size: 14px;">印花数量：${stickers.length} 个${stickers.length > 5 ? '（显示前5个）' : ''}</p>
          </div>
          
          <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: nowrap;">
      `
      
      displayStickers.forEach((sticker, index) => {
        stickersHtml += `
          <div style="text-align: center; min-width: 110px; flex-shrink: 0;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
              <div style="background: white; border-radius: 8px; padding: 8px; margin-bottom: 8px;">
                <img src="${sticker.ImgUrl}" style="width: 70px; height: 52px; object-fit: contain; display: block; margin: 0 auto;" />
              </div>
              <div style="color: white; font-size: 11px; margin-bottom: 4px;">
                <strong>位置 ${sticker.RawIndex !== null ? sticker.RawIndex + 1 : '-'}</strong>
              </div>
              <div style="background: rgba(255,255,255,0.2); border-radius: 4px; padding: 3px 6px; font-size: 11px; color: white;">
                磨损: ${sticker.Abrade || '-'}
              </div>
              ${sticker.priceV1 ? `
                <div style="margin-top: 6px; background: rgba(255,255,255,0.9); border-radius: 4px; padding: 3px 6px; font-size: 12px; color: #f56c6c; font-weight: 600;">
                  ${sticker.priceV1}
                </div>
              ` : ''}
            </div>
            <div style="margin-top: 6px; font-size: 11px; color: #606266; max-width: 110px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${sticker.Name || '-'}">
              ${sticker.Name || '-'}
            </div>
          </div>
        `
      })
      
      stickersHtml += `
          </div>
        </div>
      `
      
      // 根据印花数量计算对话框宽度（最多5个印花）
      // 每个卡片宽度110px，间距15px，加上对话框内边距和额外空间
      // 计算公式：卡片数量*110 + (卡片数量-1)*15 + 对话框边距和额外空间
      const dialogWidth = displayStickers.length * 110 + (displayStickers.length - 1) * 15 + 160
      
      ElMessageBox({
        title: '印花信息',
        message: stickersHtml,
        dangerouslyUseHTMLString: true,
        confirmButtonText: '关闭',
        customClass: 'stickers-dialog',
        width: `${dialogWidth}px`
      }).catch(() => {
        // 用户点击关闭或取消时，忽略错误
      })
    }

    // 关闭悠悠有品商品列表，返回搜索结果
    const closeYYYPList = () => {
      showYYYPList.value = false
      showSearchResults.value = true
      yyypCommodities.value = []
      yyypCurrentWeapon.value = null
    }

    // 切换搜索结果的展开/折叠
    const toggleSearchResults = () => {
      showSearchResults.value = !showSearchResults.value
    }

    // 切换悠悠有品表格的展开/折叠
    const toggleYYYPList = () => {
      showYYYPTable.value = !showYYYPTable.value
    }

    // 旧的对话框函数（已废弃，保留以防需要）
    const showYYYPCommoditiesDialog_OLD = (row, commodities, total) => {
      // 构建商品列表HTML
      let commoditiesHtml = `
        <div style="max-height: 500px; overflow-y: auto;">
          <p style="margin-bottom: 15px; color: #606266;">
            <strong>武器名称：</strong>${row.market_listing_item_name}<br/>
            <strong>悠悠有品ID：</strong>${row.yyyp_id}<br/>
            <strong>商品总数：</strong>${total} 条
          </p>
          <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <thead>
              <tr style="background-color: #f5f7fa; border-bottom: 2px solid #dcdfe6;">
                <th style="padding: 10px; text-align: left; border: 1px solid #dcdfe6;">商品名称</th>
                <th style="padding: 10px; text-align: center; border: 1px solid #dcdfe6; width: 100px;">价格</th>
                <th style="padding: 10px; text-align: center; border: 1px solid #dcdfe6; width: 80px;">磨损</th>
                <th style="padding: 10px; text-align: center; border: 1px solid #dcdfe6; width: 100px;">操作</th>
              </tr>
            </thead>
            <tbody>
      `
      
      if (commodities.length === 0) {
        commoditiesHtml += `
          <tr>
            <td colspan="4" style="padding: 20px; text-align: center; color: #909399;">暂无商品数据</td>
          </tr>
        `
      } else {
        commodities.forEach((item, index) => {
          const price = item.price ? (item.price / 100).toFixed(2) : '-'
          const abrade = item.abrade ? item.abrade.toFixed(4) : '-'
          const commodityUrl = `https://www.youpin898.com/goodInfo?id=${item.id}`
          
          commoditiesHtml += `
            <tr style="border-bottom: 1px solid #ebeef5; ${index % 2 === 0 ? 'background-color: #fafafa;' : ''}">
              <td style="padding: 10px; border: 1px solid #ebeef5;">
                <div style="display: flex; align-items: center;">
                  ${item.iconUrl ? `<img src="${item.iconUrl}" style="width: 40px; height: 30px; margin-right: 10px; object-fit: contain;" />` : ''}
                  <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${item.commodityName || '-'}</span>
                </div>
              </td>
              <td style="padding: 10px; text-align: center; border: 1px solid #ebeef5;">
                <span style="color: #f56c6c; font-weight: bold;">¥${price}</span>
              </td>
              <td style="padding: 10px; text-align: center; border: 1px solid #ebeef5;">${abrade}</td>
              <td style="padding: 10px; text-align: center; border: 1px solid #ebeef5;">
                <a href="${commodityUrl}" target="_blank" style="color: #409eff; text-decoration: none;">查看详情</a>
              </td>
            </tr>
          `
        })
      }
      
      commoditiesHtml += `
            </tbody>
          </table>
        </div>
      `
      
      ElMessageBox({
        title: '悠悠有品商品列表',
        message: commoditiesHtml,
        dangerouslyUseHTMLString: true,
        confirmButtonText: '关闭',
        customClass: 'yyyp-commodities-dialog',
        width: '900px'
      })
    }
    
    // 切换popover显示
    const togglePopover = (row) => {
      if (activePopoverRow.value === row) {
        activePopoverRow.value = null
      } else {
        activePopoverRow.value = row
      }
    }
    
    // 选择平台并搜索
    const selectPlatform = (row, platform) => {
      activePopoverRow.value = null // 关闭popover
      
      if (platform === 'yyyp') {
        handleSearchYYYPByRow(row)
      } else if (platform === 'buff') {
        handleSearchBuffByRow(row)
      } else if (platform === 'csfloat') {
        handleSearchCsFloatByRow(row)
      } else if (platform === 'all') {
        handleSearchAllPlatforms(row)
      }
    }

    // 同时搜索悠悠有品和BUFF
    const handleSearchAllPlatforms = async (row) => {
      console.log('=== 开始执行 handleSearchAllPlatforms ===')
      console.log('row数据:', row)
      
      if (!selectedSteamId.value) {
        console.log('没有选择Steam账号，退出')
        ElMessage.warning('请先选择Steam账号')
        return
      }

      // 检查是否有悠悠有品ID或BUFF ID
      const hasYYYPId = row.yyyp_id
      const hasBuffId = row.buff_id
      
      if (!hasYYYPId && !hasBuffId) {
        ElMessage.warning('该武器没有悠悠有品ID和BUFF ID')
        return
      }

      isSearching.value = true
      searchSource.value = 'all'
      
      try {
        ElMessage.info('正在同时搜索悠悠有品和BUFF...')
        
        // 并行请求悠悠有品和BUFF
        const promises = []
        
        if (hasYYYPId) {
          promises.push(handleSearchYYYPByRow(row))
        }
        
        if (hasBuffId) {
          promises.push(handleSearchBuffByRow(row))
        }
        
        await Promise.all(promises)
        
        ElMessage.success('全部平台搜索完成！')
        
      } catch (error) {
        console.error('搜索全部平台失败:', error)
        ElMessage.error('搜索失败，请重试')
      } finally {
        setTimeout(() => {
          isSearching.value = false
          searchSource.value = ''
        }, 300)
      }
    }

    // 通过行数据搜索BUFF
    const handleSearchBuffByRow = async (row) => {
      console.log('=== 开始执行 handleSearchBuffByRow ===')
      console.log('row数据:', row)
      console.log('row.buff_id:', row.buff_id)
      console.log('selectedSteamId.value:', selectedSteamId.value)
      
      if (!row.buff_id) {
        console.log('没有buff_id，退出')
        ElMessage.warning('该武器没有BUFF ID')
        return
      }

      if (!selectedSteamId.value) {
        console.log('没有选择Steam账号，退出')
        ElMessage.warning('请先选择Steam账号')
        return
      }

      console.log('通过验证，开始请求')
      isSearching.value = true
      searchSource.value = 'buff'
      
      try {
        console.log('搜索BUFF:', row.market_listing_item_name, 'ID:', row.buff_id, 'SteamID:', selectedSteamId.value)
        
        // 构建请求数据
        const requestData = {
          steamId: selectedSteamId.value || '',
          goodsId: row.buff_id
        }
        
        const apiUrl = `${API_CONFIG.SPIDER_BASE_URL}/buffSpiderV1/getCommoditiesByGoodsId`
        
        console.log('请求URL:', apiUrl)
        console.log('请求数据:', requestData)
        
        // 调用BUFF商品列表API
        const response = await axios.post(apiUrl, requestData)
        
        console.log('API响应:', response.data)
        
        if (response.data.success) {
          const parsedData = response.data.data
          console.log('获取到BUFF已解析数据:', parsedData)
          
          // 直接使用Spider解析后的数据
          const commodityList = parsedData.commodityList || []
          const totalCount = parsedData.totalCount || 0
          const buyNum = parsedData.buy_num || 0
          const sellNum = parsedData.sell_num || 0
          const rentNum = parsedData.rent_num || 0
          const totalPage = parsedData.totalPage || 1
          
          console.log('商品列表:', commodityList)
          console.log('在售总数:', totalCount)
          console.log('总页数:', totalPage)
          console.log('求购数:', buyNum, '在售数:', sellNum, '租赁数:', rentNum)
          
          // 更新BUFF状态，显示商品列表
          buffCurrentWeapon.value = row
          buffCommodities.value = commodityList
          buffTotalCount.value = totalCount
          buffBuyNum.value = buyNum
          buffRentNum.value = rentNum
          buffCurrentPage.value = 1  // 重置分页到第一页
          buffTotalPage.value = totalPage  // 设置总页数
          buffHasMore.value = totalPage > 1  // 判断是否还有更多
          showBuffList.value = true
          // showYYYPList.value = false  // 允许同时显示两个列表
          showSearchResults.value = false  // 折叠搜索结果
          
          ElMessage.success(`成功获取 ${commodityList.length} 条商品数据，在售总数: ${totalCount}（求购:${buyNum}, 租赁:${rentNum}）`)
          
          // 预加载图片（相同URL只加载一次）
          preloadImages(commodityList)
          
          // 滚动到商品列表区域
          setTimeout(() => {
            const listElement = document.querySelector('.buff-commodity-list')
            if (listElement) {
              listElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
            }
          }, 100)
          
        } else {
          console.error('API返回失败:', response.data)
          ElMessage.error(response.data.message || '获取商品列表失败')
        }
        
      } catch (error) {
        console.error('搜索BUFF失败 - 完整错误:', error)
        console.error('错误响应:', error.response)
        console.error('错误数据:', error.response?.data)
        
        const errorMessage = error.response?.data?.message || error.message || '搜索失败，请检查网络连接'
        ElMessage.error(errorMessage)
      } finally {
        console.log('请求完成，重置加载状态')
        isSearching.value = false
        searchSource.value = ''
      }
    }

    // 通过行数据搜索CsFloat
    const handleSearchCsFloatByRow = async (row) => {
      if (!row.steam_hash_name) {
        ElMessage.warning('该武器没有Steam Hash Name')
        return
      }

      isSearching.value = true
      searchSource.value = 'csfloat'
      
      try {
        console.log('搜索CsFloat:', row.market_listing_item_name, 'Hash Name:', row.steam_hash_name)
        
        // 对hash name进行URL编码
        const encodedName = encodeURIComponent(row.steam_hash_name)
        
        // 构建CsFloat搜索URL
        const csfloatUrl = `https://csfloat.com/search?name=${encodedName}`
        
        // 在新窗口中打开CsFloat搜索页面
        window.open(csfloatUrl, '_blank')
        
        ElMessage.success(`正在跳转到CsFloat: ${row.market_listing_item_name}`)
        
      } catch (error) {
        console.error('搜索CsFloat失败:', error)
        ElMessage.error('跳转失败,请检查浏览器设置是否允许弹出窗口')
      } finally {
        // 延迟关闭加载状态,给用户反馈
        setTimeout(() => {
          isSearching.value = false
        }, 300)
      }
    }

    const handleClearSearch = () => {
      searchKeyword.value = ''
      searchResults.value = []
      searchSource.value = ''
      selectedExterior.value = ''
      selectedStatTrak.value = 'normal' // 重置为默认值：非StatTrak™
      currentPage.value = 1
      ElMessage.info('已重置搜索')
    }

    const handleViewDetails = (item) => {
      ElMessage.info(`查看详情: ${item.name}`)
      // TODO: 实现详情查看功能
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
    }

    // BUFF分页切换
    const handleBuffPageChange = (val) => {
      buffCurrentPage.value = val
    }

    // 悠悠有品分页切换
    const handleYYYPPageChange = (val) => {
      yyypCurrentPage.value = val
    }

    // 获取武器图片路径
    const getWeaponImage = (steamHashName) => {
      if (!steamHashName) {
        return null
      }
      // 检查是否已经在404缓存中
      if (image404Cache.value.has(steamHashName)) {
        return null
      }
      // 将空格和竖线分别替换为下划线，并添加.png扩展名
      const imageName = steamHashName
        .replace(/\s*\|\s*/g, '___')  // " | " -> "___"
        .replace(/\s/g, '_')          // 剩余所有空格 -> "_"
        + '.png'

      // 直接使用路径，不通过 getApiUrl（因为 WEAPON_IMAGE 已经包含 /api）
      return `/api/api/v1/images/weapon_image/${imageName}`
    }

    // 处理图片加载错误
    const handleImageError = (event, steamHashName) => {
      // 将失败的steam_hash_name添加到404缓存中
      if (steamHashName) {
        image404Cache.value.add(steamHashName)
      }
      // 设置默认图片或隐藏
      event.target.style.display = 'none'
    }

    // 处理卡片点击
    const handleCardClick = (item, event) => {
      // 获取鼠标点击位置
      const x = event.clientX
      const y = event.clientY
      
      // 设置弹出框位置和内容
      cardPopoverPosition.value = { x, y }
      selectedCardItem.value = item
      showCardPopover.value = true
    }

    // 处理商品卡片点击
    const handleCommodityCardClick = (item, type, event) => {
      if (isMultiSelectMode.value) {
        // 多选模式下切换选中状态
        toggleCommoditySelection(item, type)
      } else {
        // 非多选模式打开详情弹窗
        commodityPreviewItem.value = item
        commodityPreviewType.value = type
        commodityPreviewVisible.value = true
      }
    }

    // 切换多选模式
    const toggleMultiSelectMode = () => {
      isMultiSelectMode.value = !isMultiSelectMode.value
      if (!isMultiSelectMode.value) {
        // 退出多选模式时清空选择
        selectedCommodities.value = []
        selectedCommodityType.value = ''
      }
    }

    // 判断商品是否被选中
    const isCommoditySelected = (item) => {
      return selectedCommodities.value.some(c => c.id === item.id)
    }

    // 切换商品选中状态
    const toggleCommoditySelection = (item, type) => {
      // 如果切换了平台类型，清空之前的选择
      if (selectedCommodityType.value && selectedCommodityType.value !== type) {
        selectedCommodities.value = []
      }
      selectedCommodityType.value = type
      
      const index = selectedCommodities.value.findIndex(c => c.id === item.id)
      if (index > -1) {
        selectedCommodities.value.splice(index, 1)
      } else {
        selectedCommodities.value.push(item)
      }
    }

    // 清空选择
    const clearCommoditySelection = () => {
      selectedCommodities.value = []
      selectedCommodityType.value = ''
    }

    // 全选当前列表
    const selectAllCommodities = (type) => {
      selectedCommodityType.value = type
      if (type === 'buff') {
        selectedCommodities.value = [...buffCommodities.value]
      } else if (type === 'yyyp') {
        selectedCommodities.value = [...yyypCommodities.value]
      }
      ElMessage.success(`已选择 ${selectedCommodities.value.length} 件商品`)
    }

    // 批量购买
    const handleBatchBuy = async () => {
      if (selectedCommodities.value.length === 0) {
        ElMessage.warning('请先选择要购买的商品')
        return
      }
      
      const totalPrice = selectedCommodities.value.reduce((sum, item) => {
        return sum + parseFloat(item.price || 0)
      }, 0)
      
      try {
        await ElMessageBox.confirm(
          `确定要批量购买 ${selectedCommodities.value.length} 件商品吗？\n总价: ¥${totalPrice.toFixed(2)}`,
          '批量购买确认',
          {
            confirmButtonText: '确定购买',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 执行批量购买
        if (selectedCommodityType.value === 'buff') {
          for (const item of selectedCommodities.value) {
            await handleBuyBuffCommodity(item)
          }
        } else if (selectedCommodityType.value === 'yyyp') {
          for (const item of selectedCommodities.value) {
            await handleBuyCommodity(item)
          }
        }
        
        ElMessage.success('批量购买请求已发送')
        clearCommoditySelection()
        
      } catch (e) {
        if (e !== 'cancel') {
          console.error('批量购买失败:', e)
        }
      }
    }

    // 获取商品标题
    const getCommodityTitle = (item) => {
      if (!item) return ''
      return item.itemName || item.name || '商品详情'
    }

    // 从详情弹窗购买商品
    const handleBuyCommodityFromPreview = () => {
      commodityPreviewVisible.value = false
      if (commodityPreviewType.value === 'buff') {
        handleBuyBuffCommodity(commodityPreviewItem.value)
      } else if (commodityPreviewType.value === 'yyyp') {
        handleBuyCommodity(commodityPreviewItem.value)
      }
    }

    // 页面加载时获取Steam ID列表
    onMounted(async () => {
      await loadSteamIdList()
    })

    return {
      searchKeyword,
      searchResults,
      isSearching,
      searchSource,
      currentPage,
      pageSize,
      paginatedResults,
      filteredResults,
      steamIdList,
      selectedSteamId,
      selectedExterior,
      selectedStatTrak,
      showSearchResults,
      displayMode,
      toggleSearchResults,
      handleSearchWeapon,
      handleRefreshSearch,
      handleSteamIdChange,
      handleExteriorChange,
      handleStatTrakChange,
      querySearchAsync,
      handleSelect,
      getWeaponImage,
      handleImageError,
      handleCardClick,
      // 卡片弹出框
      showCardPopover,
      cardPopoverPosition,
      selectedCardItem,
      // 商品详情弹窗
      commodityPreviewVisible,
      commodityPreviewItem,
      commodityPreviewType,
      handleCommodityCardClick,
      getCommodityTitle,
      handleBuyCommodityFromPreview,
      // 多选模式
      isMultiSelectMode,
      selectedCommodities,
      selectedCommodityType,
      toggleMultiSelectMode,
      isCommoditySelected,
      toggleCommoditySelection,
      clearCommoditySelection,
      selectAllCommodities,
      handleBatchBuy,
      // BUFF商品列表
      buffCommodities,
      buffCurrentWeapon,
      buffTotalCount,
      buffBuyNum,
      buffRentNum,
      showBuffList,
      showBuffTable,
      buffCurrentPage,
      buffPageSize,
      buffLoadingMore,
      buffHasMore,
      buffTotalPage,
      paginatedBuffCommodities,
      toggleBuffList,
      handleRefreshBuff,
      handleBuyBuffCommodity,
      handleBuffPageChange,
      loadMoreBuffCommodities,
      handleBuffScroll,
      // 悠悠有品商品列表
      yyypCommodities,
      yyypCurrentWeapon,
      yyypTotalCount,
      showYYYPList,
      showYYYPTable,
      yyypCurrentPage,
      yyypPageSize,
      yyypLoadingMore,
      yyypHasMore,
      paginatedYYYPCommodities,
      toggleYYYPList,
      handleBuyCommodity,
      fetchSingleNameTag,
      showStickersDialog,
      closeYYYPList,
      handleYYYPPageChange,
      handleRefreshYYYP,
      handleSearchYYYPByRow,
      loadMoreYYYPCommodities,
      handleYYYPScroll,
      handleSearchBuffByRow,
      handleSearchCsFloatByRow,
      handleSearchAllPlatforms,
      activePopoverRow,
      togglePopover,
      selectPlatform,
      handleClearSearch,
      handleViewDetails,
      getRarityType,
      getRarityColor,
      getWeaponTypeColor,
      getFloatRangeType,
      getFloatRangeColor,
      getWearColor,
      getWearRange,
      getExteriorColor,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.item-search-container {
  position: relative;
  min-height: 100vh;
}

/* 搜索包装器 - 居中或左上角 */
.search-wrapper {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 10;
}

.search-wrapper.centered {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 800px;
}

.search-wrapper.top-left {
  margin-bottom: 1.5rem;
  width: 100%;
}

/* 搜索卡片 */
.search-card {
  padding: 2rem;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-wrapper.centered .search-card {
  padding: 3rem 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.search-wrapper.top-left .search-card {
  padding: 1rem 1.5rem;
}

/* 标题样式 */
.search-title {
  text-align: center;
  font-size: 3rem;
  font-weight: 700;
  color: #4CAF50;
  margin: 0 0 2rem 0;
  background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: fadeInDown 0.6s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.search-section {
  transition: all 0.5s ease;
}

.search-wrapper.centered .search-section {
  margin-bottom: 0;
}

.search-wrapper.top-left .search-section {
  margin-bottom: 0;
}

/* 搜索控件 */
.search-controls {
  display: flex;
  align-items: stretch;
  gap: 1rem;
  transition: all 0.5s ease;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
}

.search-controls.compact {
  gap: 0.75rem;
}

/* 按钮组 */
.button-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.search-wrapper.top-left .button-group {
  gap: 0.75rem;
}

.search-controls.compact .button-group {
  flex-wrap: nowrap;
}

/* Steam ID 选择框 */
.steam-id-select {
  transition: all 0.5s ease;
  min-width: 180px;
  width: 180px;
}

/* 外观选择框 */
.exterior-select {
  transition: all 0.5s ease;
  min-width: 150px;
  width: 150px;
}

/* StatTrak选择框 */
.stattrak-select {
  transition: all 0.5s ease;
  min-width: 140px;
  width: 140px;
}

/* 搜索输入框 */
.search-input {
  transition: all 0.5s ease;
  min-width: 300px;
  flex: 1;
}

/* el-autocomplete 样式适配 */
.search-input :deep(.el-input__wrapper) {
  background-color: #2a2a2a;
  box-shadow: 0 0 0 1px #444 inset;
}

.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4CAF50 inset;
}

.search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #4CAF50 inset !important;
}

.search-input :deep(.el-input__inner) {
  color: #fff;
}

.search-wrapper.centered .steam-id-select.large :deep(.el-input__wrapper) {
  padding: 1rem 1.5rem;
  font-size: 1.125rem;
}

.search-wrapper.centered .steam-id-select.large :deep(.el-input__inner) {
  font-size: 1.125rem;
}

.search-wrapper.centered .search-input.large :deep(.el-input__wrapper) {
  padding: 2rem 2.5rem;
  font-size: 2rem;
  height: 80px;
  min-height: 80px;
}

.search-wrapper.centered .search-input.large :deep(.el-input__inner) {
  font-size: 2rem;
  height: 80px;
  min-height: 80px;
}

/* 居中状态下的 autocomplete 样式 */
.search-wrapper.centered .search-input.large :deep(.el-autocomplete) {
  width: 100%;
}

.search-wrapper.centered .search-input.large :deep(.el-input) {
  width: 100%;
}

/* 居中状态下的按钮样式 */
.search-wrapper.centered .button-group {
  width: 100%;
  max-width: 600px;
}

.search-wrapper.centered .button-group .el-button {
  padding: 1rem 2rem;
  font-size: 1.125rem;
  height: auto;
  flex: 1;
  min-width: 160px;
}

.mb-4 {
  margin-bottom: 1rem;
}

.search-stats-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-default) 20%, var(--border-default) 80%, transparent);
  margin: 1.5rem 0;
}

.filter-status {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-default);
}

.filter-label {
  font-weight: 500;
  color: var(--text-primary);
  margin-right: 0.5rem;
}

.stats-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stats-section {
  flex: 1;
}

.stats-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-size: clamp(1rem, 1.8vw, 1.125rem);
  font-weight: 600;
}

.stats-grid-3x2 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: clamp(0.75rem, 2vw, 1rem);
  align-items: stretch;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
  background-color: #2a2a2a;
  border-radius: 0.375rem;
}

.stat-label {
  color: #ccc;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

.stat-value {
  font-weight: bold;
  color: #fff;
  font-size: clamp(0.875rem, 1.4vw, 1rem);
}

.table-card {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.price-text {
  color: #4CAF50;
  font-weight: 600;
}

.no-data {
  color: #888;
}

.id-text {
  color: #4CAF50;
  font-family: monospace;
  font-weight: 500;
}

.rarity-text {
  font-weight: 600;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

.weapon-name-text {
  font-weight: 500;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

.hash-name-text {
  color: #64B5F6;
  font-weight: 500;
  font-size: 0.95rem;
}

.clickable-item-name {
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clickable-item-name:hover {
  color: #4CAF50;
  transform: translateX(2px);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: nowrap;
  justify-content: center;
  align-items: center;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: clamp(1rem, 2vw, 1.5rem) 0;
}

.pagination-top {
  padding-bottom: clamp(0.8rem, 1.5vw, 1.2rem);
  padding-top: clamp(0.5rem, 1vw, 0.8rem);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: clamp(0.8rem, 1.5vw, 1.2rem);
}

.card-mode-wrapper {
  width: 100%;
}

.no-results-card {
  padding: clamp(2rem, 4vw, 3rem);
  text-align: center;
  animation: fadeInUp 0.5s ease-out;
}

/* Element Plus 组件深色主题适配 */
:deep(.el-input__wrapper) {
  background-color: #2a2a2a;
  box-shadow: 0 0 0 1px #444 inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4CAF50 inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #4CAF50 inset !important;
}

:deep(.el-input__inner) {
  color: #fff;
}

:deep(.el-select .el-input__wrapper) {
  background-color: #2a2a2a;
}

:deep(.el-button) {
  font-size: clamp(0.75rem, 1vw, 0.875rem);
  padding: clamp(0.5rem, 1vw, 0.625rem) clamp(0.75rem, 1.5vw, 1rem);
}

:deep(.el-table) {
  background-color: transparent;
  color: #fff;
}

:deep(.el-table th.el-table__cell) {
  background-color: #2a2a2a;
  color: #fff;
  border-bottom: 1px solid #444;
}

:deep(.el-table tr) {
  background-color: #1e1e1e;
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid #333;
}

:deep(.el-table__body tr:hover > td) {
  background-color: #2a2a2a !important;
}

:deep(.el-pagination) {
  color: #fff;
}

:deep(.el-pagination button) {
  background-color: #2a2a2a;
  color: #fff;
}

:deep(.el-pagination .el-pager li) {
  background-color: #2a2a2a;
  color: #fff;
}

:deep(.el-pagination .el-pager li.is-active) {
  background-color: #4CAF50;
  color: #fff;
}

/* 自动完成下拉框样式 */
.autocomplete-item {
  padding: 0;
  color: #fff;
  white-space: normal !important;
  word-wrap: break-word !important;
  word-break: break-word !important;
  line-height: 1.5;
  overflow: visible !important;
  text-overflow: clip !important;
}

:deep(.weapon-autocomplete-popper) {
  background-color: #2a2a2a !important;
  border: 1px solid #444 !important;
  max-width: 800px !important;
  min-width: 400px !important;
  width: auto !important;
}

:deep(.weapon-autocomplete-popper .el-autocomplete-suggestion__wrap) {
  background-color: #2a2a2a;
  max-height: 500px !important;
  overflow-y: auto;
}

:deep(.weapon-autocomplete-popper .el-autocomplete-suggestion__list) {
  padding: 0;
}

:deep(.weapon-autocomplete-popper li) {
  color: #fff !important;
  background-color: #2a2a2a !important;
  white-space: normal !important;
  word-wrap: break-word !important;
  word-break: break-word !important;
  line-height: 1.6 !important;
  padding: 0.75rem 1rem !important;
  min-height: auto !important;
  height: auto !important;
  overflow: visible !important;
  text-overflow: clip !important;
  border-bottom: 1px solid #333;
}

:deep(.weapon-autocomplete-popper li:hover) {
  background-color: #3a3a3a !important;
}

:deep(.weapon-autocomplete-popper li.highlighted) {
  background-color: #3a3a3a !important;
}

:deep(.el-autocomplete-suggestion) {
  background-color: #2a2a2a !important;
}

:deep(.el-autocomplete-suggestion__wrap) {
  background-color: #2a2a2a;
}

:deep(.el-autocomplete-suggestion li) {
  color: #fff;
  background-color: #2a2a2a;
  white-space: normal !important;
  word-wrap: break-word !important;
  line-height: 1.5 !important;
  padding: 0.75rem 1rem !important;
  height: auto !important;
}

:deep(.el-autocomplete-suggestion li:hover) {
  background-color: #3a3a3a !important;
}

:deep(.el-autocomplete-suggestion li.highlighted) {
  background-color: #3a3a3a !important;
}

@media (max-width: 768px) {
  .search-wrapper.centered {
    width: 95%;
    max-width: none;
  }
  
  .search-wrapper.centered .search-card {
    padding: 2rem 1.5rem;
  }
  
  .steam-id-select.large,
  .search-input.large {
    min-width: 100%;
  }
  
  .search-controls {
    flex-wrap: wrap;
  }
  
  .button-group {
    width: 100%;
  }
  
  .button-group .el-button {
    flex: 1;
    min-width: 100px;
  }
  
  .stats-grid-3x2 {
    grid-template-columns: 1fr;
  }
  
  .stat-item {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  :deep(.yyyp-commodities-dialog) {
    width: 95% !important;
  }
}

/* 折叠头部样式 */
.collapse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  transition: all 0.3s ease;
  user-select: none;
}

.collapse-header:hover {
  background-color: var(--el-fill-color);
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--el-text-color-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.collapse-title .el-icon {
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

/* 表格头部样式（无折叠时） */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
  border-radius: 8px 8px 0 0;
  margin-bottom: 0;
}

.table-title {
  color: var(--el-text-color-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

/* BUFF商品列表样式 */
.buff-commodity-list {
  margin-top: 1.5rem;
  animation: fadeInUp 0.5s ease-out;
}

/* BUFF折叠头部样式 */
.buff-collapse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  transition: all 0.3s ease;
  user-select: none;
}

.buff-collapse-header:hover {
  background-color: var(--el-fill-color);
}

.buff-collapse-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.buff-collapse-title {
  color: var(--el-text-color-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.buff-weapon-info {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.buff-weapon-info .weapon-name {
  font-weight: 600;
  color: var(--el-color-primary);
  font-size: 1.1rem;
}

.buff-weapon-info .weapon-id {
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
}

.buff-weapon-info .commodity-count {
  color: var(--el-color-success);
  font-weight: 600;
}

.buff-weapon-info .total-count {
  color: var(--el-color-primary);
  font-weight: 600;
  font-size: 1rem;
}

.buff-weapon-info .buy-count {
  color: var(--el-color-warning);
  font-weight: 600;
}

.buff-weapon-info .rent-count {
  color: var(--el-text-color-secondary);
  font-weight: 600;
}

:deep(.buff-commodity-list .el-table) {
  background-color: transparent;
}

:deep(.buff-commodity-list .el-table__header-wrapper) {
  background-color: var(--el-fill-color-light);
}

:deep(.buff-commodity-list .el-table__row:hover) {
  background-color: var(--el-fill-color-light);
}

/* 悠悠有品商品列表样式 */
.yyyp-commodity-list {
  margin-top: 1.5rem;
  animation: fadeInUp 0.5s ease-out;
}

/* 悠悠有品折叠头部样式 */
.yyyp-collapse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  transition: all 0.3s ease;
  user-select: none;
}

.yyyp-collapse-header:hover {
  background-color: var(--el-fill-color);
}

.yyyp-collapse-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.yyyp-collapse-title {
  color: var(--el-text-color-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.collapse-icon {
  color: var(--el-text-color-primary);
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.yyyp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 2px solid var(--el-border-color);
  margin-bottom: 1rem;
}

.yyyp-header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.yyyp-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--el-text-color-primary);
}

.yyyp-weapon-info {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.yyyp-weapon-info .weapon-name {
  font-weight: 600;
  color: var(--el-color-primary);
  font-size: 1.1rem;
}

.yyyp-weapon-info .weapon-id {
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
}

.yyyp-weapon-info .commodity-count {
  color: var(--el-color-success);
  font-weight: 600;
}

.yyyp-weapon-info .total-count {
  color: var(--el-color-primary);
  font-weight: 600;
  font-size: 1rem;
}

.commodity-icon {
  width: 80px;
  height: 60px;
  object-fit: contain;
  border-radius: 4px;
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  padding: 5px;
}

.price-text {
  color: #f56c6c;
  font-weight: bold;
  font-size: 1.1rem;
}

:deep(.yyyp-commodity-list .el-table) {
  background-color: transparent;
}

:deep(.yyyp-commodity-list .el-table__header-wrapper) {
  background-color: var(--el-fill-color-light);
}

:deep(.yyyp-commodity-list .el-table__row:hover) {
  background-color: var(--el-fill-color-light);
}

/* 印花对话框样式 */
:deep(.stickers-dialog) {
  border-radius: 8px;
}

:deep(.stickers-dialog .el-message-box__header) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 20px;
  border-bottom: none;
}

:deep(.stickers-dialog .el-message-box__title) {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

:deep(.stickers-dialog .el-message-box__headerbtn .el-message-box__close) {
  color: white;
  font-size: 20px;
}

:deep(.stickers-dialog .el-message-box__headerbtn .el-message-box__close:hover) {
  color: #f5f5f5;
}

:deep(.stickers-dialog .el-message-box__content) {
  padding: 20px;
  max-height: 600px;
  overflow-y: auto;
}

:deep(.stickers-dialog .el-message-box__btns) {
  padding: 15px 20px;
  border-top: 1px solid #dcdfe6;
}

/* 改名对话框样式 */
:deep(.nametag-dialog) {
  border-radius: 8px;
}

:deep(.nametag-dialog .el-message-box__header) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 20px;
  border-bottom: none;
}

:deep(.nametag-dialog .el-message-box__title) {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

:deep(.nametag-dialog .el-message-box__headerbtn .el-message-box__close) {
  color: white;
  font-size: 20px;
}

:deep(.nametag-dialog .el-message-box__headerbtn .el-message-box__close:hover) {
  color: #f5f5f5;
}

:deep(.nametag-dialog .el-message-box__content) {
  padding: 0;
}

:deep(.nametag-dialog .el-message-box__btns) {
  padding: 15px 20px;
  border-top: 1px solid #dcdfe6;
}

/* 搜索平台选择器样式 */
.search-platform-selector {
  padding: 8px;
}

.selector-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.selector-buttons .el-button {
  flex: 1;
  min-width: 80px;
  font-weight: 600;
}

.selector-buttons .buff-button {
  background-color: #1a1a1a;
  border-color: #1a1a1a;
  color: white;
}

.selector-buttons .buff-button:hover {
  background-color: #2a2a2a;
  border-color: #2a2a2a;
}

.selector-buttons .buff-button:active {
  background-color: #0a0a0a;
  border-color: #0a0a0a;
}

.selector-buttons .csfloat-button {
  background-color: #67c23a;
  border-color: #67c23a;
  color: white;
}

.selector-buttons .csfloat-button:hover {
  background-color: #85ce61;
  border-color: #85ce61;
}

.selector-buttons .csfloat-button:active {
  background-color: #5daf34;
  border-color: #5daf34;
}

.selector-buttons .all-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-weight: 700;
  flex-basis: 100%;
  margin-top: 4px;
}

.selector-buttons .all-button:hover {
  background: linear-gradient(135deg, #7c8ff0 0%, #8b5bb8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.selector-buttons .all-button:active {
  background: linear-gradient(135deg, #5568d3 0%, #63408c 100%);
  transform: translateY(0);
}

/* Popover 样式优化 */
:deep(.el-popover) {
  padding: 0 !important;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* 图片显示样式 */
.weapon-image-cell {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
}

.weapon-img {
  max-width: 100px;
  max-height: 60px;
  object-fit: contain;
  border-radius: 4px;
}

.no-image {
  color: #888;
  font-size: 12px;
}

/* 卡片模式样式 */
.card-grid-container {
  padding: 20px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.search-result-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
  width: 220px;
  height: 220px;
  position: relative;
}

.search-result-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  border-color: var(--primary-color);
}

.search-result-card .card-image {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.search-result-card .card-badges {
  position: absolute;
  top: 6px;
  left: 6px;
  display: flex;
  flex-direction: row;
  gap: 4px;
  z-index: 10;
  align-items: flex-start;
}

.search-result-card .card-badges .badge-item {
  font-size: 11px !important;
  padding: 3px 6px;
  font-weight: 600 !important;
  font-family: inherit !important;
  line-height: 1.2 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(4px);
}

.search-result-card .weapon-card-img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.search-result-card:hover .weapon-card-img {
  transform: scale(1.05);
}

.search-result-card .image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 14px;
}

.search-result-card .card-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.95) 0%, rgba(0, 0, 0, 0.85) 70%, transparent 100%);
  transform: translateY(0);
  transition: all 0.3s ease;
}

.search-result-card .card-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.2;
}

.search-result-card .card-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-bottom: 6px;
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: all 0.3s ease;
}

.search-result-card:hover .card-info {
  max-height: 200px;
  opacity: 1;
}

.search-result-card .info-row {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
}

.search-result-card .info-row span {
  color: #fff;
}

.search-result-card .info-label {
  color: #888 !important;
  min-width: 40px;
}

.search-result-card .rarity-text {
  font-weight: 600 !important;
  text-shadow: 0 0 4px currentColor;
}

.search-result-card .float-range-text {
  font-weight: 600 !important;
  text-shadow: 0 0 4px currentColor;
}

.search-result-card .info-row:has(.rarity-text) span:not(.info-label),
.search-result-card .info-row:has(.float-range-text) span:not(.info-label) {
  color: inherit !important;
}

.search-result-card .card-actions {
  display: flex;
  gap: 4px;
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: all 0.3s ease;
}

.search-result-card:hover .card-actions {
  max-height: 50px;
  opacity: 1;
}

.search-result-card .card-actions .el-button {
  flex: 1;
  font-size: 10px;
  padding: 4px 6px;
}

/* 头部操作按钮样式 */
.collapse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  user-select: none;
}

.collapse-header .header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.collapse-header:hover {
  background: var(--bg-hover);
}

/* 卡片弹出框样式 */
.card-popover-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 9999;
  backdrop-filter: blur(2px);
}

.card-popover-content {
  position: fixed;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  transform: translate(-50%, -50%);
  z-index: 10000;
  min-width: 240px;
  max-width: 280px;
}

.card-popover-content .popover-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  width: 100%;
}

.card-popover-content .popover-buttons .el-button {
  width: 100% !important;
  margin: 0 !important;
  flex: none !important;
}

/* 商品购买弹出框 - 紧凑样式 */
.commodity-popover-content {
  position: fixed;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
  transform: translate(-50%, -50%);
  z-index: 10000;
}

.commodity-popover-content .el-button {
  padding: 8px 20px !important;
  font-size: 13px !important;
}

/* 商品卡片网格布局 */
.commodity-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
  padding: 1rem;
  max-height: 380px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 滚动条样式 */
.commodity-card-grid::-webkit-scrollbar {
  width: 8px;
}

.commodity-card-grid::-webkit-scrollbar-track {
  background: var(--bg-tertiary);
  border-radius: 4px;
}

.commodity-card-grid::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

.commodity-card-grid::-webkit-scrollbar-thumb:hover {
  background: var(--el-color-primary);
}

/* 磨损值显示条样式 */
.float-bar-container {
  margin-top: 0.3rem;
  padding: 0;
  margin-bottom: 0.3rem;
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
}

/* 磨损值数字显示 */
.float-value {
  text-align: left;
  font-size: 0.7rem;
  color: #ccc;
  margin-bottom: 0.3rem;
}

/* 模板号覆盖层 - 左上角常态化显示 */
.paint-seed-overlay {
  position: absolute;
  top: 6px;
  left: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.7rem;
  font-weight: 600;
  z-index: 10;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
}

/* 印花覆盖层 - 左下角 */
.sticker-overlay {
  position: absolute;
  bottom: 4px;
  left: 4px;
  display: flex;
  gap: 3px;
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

/* 挂件覆盖层 - 右上角 */
.pendant-overlay {
  position: absolute;
  top: 4px;
  right: 4px;
  display: flex;
  gap: 3px;
  z-index: 5;
  pointer-events: none;
}

.pendant-item-overlay {
  position: relative;
  width: 36px;
  height: 36px;
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
  font-size: 1rem;
  font-weight: bold;
}

.commodity-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  aspect-ratio: 1 / 1;
  cursor: pointer;
}

.commodity-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border-color: var(--el-color-primary);
}

.commodity-card-image {
  width: 100%;
  height: 70%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  position: relative;
}

.commodity-card-image .commodity-icon {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.commodity-card-content {
  padding: 0.3rem 0.5rem;
  height: 30%;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  overflow: hidden;
}

.commodity-card-title {
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

.commodity-card-subtitle {
  font-size: 0.7rem;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.commodity-card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.75rem;
  overflow-y: auto;
}

.commodity-card-info .info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 20px;
}

.commodity-card-info .info-label {
  color: #999;
  font-size: 0.7rem;
  white-space: nowrap;
  flex-shrink: 0;
}

.commodity-card-info .info-value {
  color: #ccc;
  font-size: 0.7rem;
  text-align: right;
  flex: 1;
  margin-left: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.commodity-card-info .price-highlight {
  color: #fff;
  font-weight: bold;
  font-size: 0.75rem;
}

.commodity-card-info .description-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: normal;
  font-size: 0.7rem;
  line-height: 1.3;
}

.commodity-card-info .nametag-text {
  color: #e6a23c;
  font-weight: 600;
  font-size: 0.7rem;
}

.commodity-card-info .nametag-parse {
  cursor: pointer;
  user-select: none;
  color: #e6a23c;
  font-weight: 600;
  font-size: 0.7rem;
}

.commodity-card-info .nametag-parse:hover {
  opacity: 0.8;
}

.commodity-card-actions {
  margin-top: 0.5rem;
  flex-shrink: 0;
}

/* 商品详情弹窗样式 - 与inventory一致 */
.commodity-preview-dialog :deep(.el-dialog__header) {
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 20px;
}

.commodity-preview-dialog :deep(.el-dialog__title) {
  color: #fff;
  font-weight: bold;
  font-size: 1.1rem;
}

.commodity-preview-dialog :deep(.el-dialog__body) {
  background: var(--bg-secondary);
  padding: 1.5rem;
}

.commodity-preview-content {
  position: relative;
}

.preview-main-layout {
  display: flex;
  gap: 1.5rem;
}

.preview-left-section {
  flex: 0 0 55%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preview-image-section {
  width: 100%;
  height: 280px;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview-image {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.preview-float-section {
  padding: 0;
}

.preview-float-bar-container {
  margin-bottom: 0.5rem;
}

.preview-float-value {
  font-size: 1rem;
  font-weight: bold;
  color: #fff;
  margin-bottom: 0.25rem;
}

.preview-float-range {
  font-size: 0.9rem;
  color: #999;
}

.preview-prices {
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: 1rem;
}

.preview-price-row {
  display: flex;
  gap: 2rem;
  margin-bottom: 0.75rem;
}

.preview-price-row:last-child {
  margin-bottom: 0;
}

.preview-price-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-price-item.full-width {
  flex: 1;
}

.preview-price-label {
  color: #999;
  font-size: 0.9rem;
}

.preview-price-value {
  color: #fff;
  font-size: 0.95rem;
  font-weight: 600;
}

.preview-price-value.price-highlight {
  color: #f56c6c;
  font-size: 1.2rem;
  font-weight: bold;
}

.preview-price-value.nametag-text {
  color: #e6a23c;
}

.preview-price-value.nametag-parse {
  color: #e6a23c;
  cursor: pointer;
}

.preview-price-value.nametag-parse:hover {
  opacity: 0.8;
}

.preview-action-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.preview-action-buttons .el-button {
  padding: 10px 24px;
}

.preview-right-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preview-sticker-list-section {
  flex: 1;
}

.preview-sticker-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.preview-sticker-list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.preview-sticker-list-item:hover {
  background: var(--bg-hover);
}

.preview-sticker-list-item.pendant-item {
  border-left: 3px solid rgba(255, 215, 0, 0.6);
}

.preview-sticker-list-img-wrapper {
  width: 50px;
  height: 50px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.preview-sticker-list-img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.preview-sticker-list-placeholder {
  color: #666;
  font-size: 1.2rem;
}

.preview-sticker-list-name {
  flex: 1;
  color: #fff;
  font-size: 0.9rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-no-stickers {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 0.9rem;
}

.preview-bottom-right-button {
  position: absolute;
  bottom: 1.5rem;
  right: 1.5rem;
}

.preview-bottom-right-button .el-button {
  padding: 12px 32px;
  font-size: 1rem;
  font-weight: 600;
}

/* 多选模式样式 */
.commodity-card.multi-select-mode {
  cursor: pointer;
}

.commodity-card.selected {
  border-color: var(--el-color-success) !important;
  box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.3);
}

.selected-check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background: var(--el-color-success);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  z-index: 15;
  font-size: 14px;
}

/* 多选操作栏 */
.multi-select-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  z-index: 1000;
}

.multi-select-actions .selected-count {
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 16px;
}

.multi-select-actions .total-price {
  color: #f56c6c;
  font-weight: bold;
}

.multi-select-actions .action-buttons {
  display: flex;
  gap: 12px;
}

/* 悠悠有品滚动容器 */
.yyyp-scroll-container {
  max-height: 500px;
  overflow-y: auto;
}

/* BUFF滚动容器 */
.buff-scroll-container {
  max-height: 500px;
  overflow-y: auto;
}

/* 加载更多提示样式 */
.load-more-indicator {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  color: #999;
  font-size: 0.9rem;
}

.loading-more {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--el-color-primary);
}

.loading-more .is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.no-more-data {
  color: #666;
  font-size: 0.85rem;
}

.scroll-hint {
  color: #888;
  font-size: 0.85rem;
}
</style>

