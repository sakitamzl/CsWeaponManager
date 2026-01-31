<template>
  <div class="item-search-container">
    <el-card class="search-card">
      <!-- 搜索区域 -->
      <div class="search-section">
        <div class="search-filters">
          <el-select 
            v-model="filters.weaponType" 
            placeholder="选择武器类型"
            clearable
            style="width: 200px;"
            @change="handleWeaponTypeChange"
          >
            <el-option label="全部武器" value="" />
            <el-option label="手枪" value="手枪" />
            <el-option label="步枪" value="步枪" />
            <el-option label="狙击步枪" value="狙击步枪" />
            <el-option label="冲锋枪" value="冲锋枪" />
            <el-option label="霰弹枪" value="霰弹枪" />
            <el-option label="机枪" value="机枪" />
            <el-option label="挂件" value="挂件" />
            <el-option label="挂件（纪念品）" value="挂件（纪念品）" />
            <el-option label="匕首" value="匕首" />
            <el-option label="手套" value="手套" />
            <el-option label="探员" value="探员" />
            <el-option label="印花" value="印花" />
            <el-option label="涂鸦" value="涂鸦" />
            <el-option label="音乐盒" value="音乐盒" />
            <el-option label="收藏品" value="收藏品" />
            <el-option label="容器" value="容器" />
          </el-select>
          
          <el-select 
            v-model="filters.weaponName" 
            placeholder="选择武器名称"
            clearable
            filterable
            style="width: 200px;"
            :loading="isLoadingWeaponNames"
            @focus="loadWeaponNamesIfNeeded"
          >
            <el-option label="全部" value="" />
            <el-option 
              v-for="name in weaponNameList" 
              :key="name" 
              :label="name" 
              :value="name"
            />
          </el-select>
          
          <el-select 
            v-model="filters.rarity" 
            placeholder="选择稀有度"
            clearable
            style="width: 200px;"
          >
            <el-option label="全部稀有度" value="" />
            <el-option label="违禁" value="违禁">
              <span :style="{ color: getRarityColor('违禁'), fontWeight: 600 }">违禁</span>
            </el-option>
            <el-option label="隐秘" value="隐秘">
              <span :style="{ color: getRarityColor('隐秘'), fontWeight: 600 }">隐秘</span>
            </el-option>
            <el-option label="保密" value="保密">
              <span :style="{ color: getRarityColor('保密'), fontWeight: 600 }">保密</span>
            </el-option>
            <el-option label="受限" value="受限">
              <span :style="{ color: getRarityColor('受限'), fontWeight: 600 }">受限</span>
            </el-option>
            <el-option label="军规级" value="军规级">
              <span :style="{ color: getRarityColor('军规级'), fontWeight: 600 }">军规级</span>
            </el-option>
            <el-option label="工业级" value="工业级">
              <span :style="{ color: getRarityColor('工业级'), fontWeight: 600 }">工业级</span>
            </el-option>
            <el-option label="消费级" value="消费级">
              <span :style="{ color: getRarityColor('消费级'), fontWeight: 600 }">消费级</span>
            </el-option>
            <el-option label="普通级" value="普通级">
              <span :style="{ color: getRarityColor('普通级'), fontWeight: 600 }">普通级</span>
            </el-option>
          </el-select>
        </div>
        
        <el-input
          v-model="keyword"
          placeholder="搜索饰品名称..."
          prefix-icon="Search"
          class="weapon-search-input"
          @keyup.enter="performSearch"
          clearable
        >
          <template #append>
            <el-button 
              type="primary" 
              @click="performSearch" 
              :loading="isSearching"
            >
              搜索
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 搜索结果 -->
      <div v-if="searchResults.length > 0" class="results-section">
        <div class="results-header">
          <span class="results-title">搜索结果 ({{ searchResults.length }} 件)</span>
          <div class="results-actions">
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
            <el-button 
              type="text" 
              size="small"
              @click="handleClear"
            >
              清除结果
            </el-button>
          </div>
        </div>
        
        <!-- 列表显示 -->
        <div v-show="displayMode === 'list'">
          <el-table 
            :data="searchResults" 
            style="width: 100%"
            stripe
          >
          <el-table-column type="index" label="#" width="60" align="center" />
          
          <el-table-column label="图片" width="144" align="center">
            <template #default="{ row }">
              <div class="weapon-image-cell">
                <img
                  v-if="getWeaponImage(row.steam_hash_name)"
                  :src="getWeaponImage(row.steam_hash_name)"
                  :alt="row.market_listing_item_name"
                  class="weapon-img"
                  @error="(e) => handleImageError(e, row.steam_hash_name)"
                />
                <span v-else class="no-image">无图</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="饰品名称" min-width="300" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="weapon-name">{{ row.market_listing_item_name }}</span>
            </template>
          </el-table-column>
          
          <el-table-column label="武器类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small" type="info">{{ row.weapon_type || '-' }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="稀有度" width="100" align="center">
            <template #default="{ row }">
              <span 
                v-if="row.rarity"
                class="rarity-tag"
                :style="{ color: getRarityColor(row.rarity), fontWeight: 600 }"
              >
                {{ row.rarity }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="CSQAQ ID" width="150" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.csqaq_id" type="success" size="large">
                {{ row.csqaq_id }}
              </el-tag>
              <el-tag v-else type="info" size="small">未映射</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="悠悠有品价格" width="130" align="center">
            <template #default="{ row }">
              <span v-if="row.yyyp_Price" class="price">¥{{ row.yyyp_Price }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="在售数量" width="110" align="center">
            <template #default="{ row }">
              {{ row.on_sale_count || 0 }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="160" align="center" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small"
                @click="handleSearchCSQAQ(row)"
                :disabled="!row.csqaq_id"
                :loading="searchingItems[row.csqaq_id]"
              >
                搜索
              </el-button>
              <el-button 
                type="success" 
                size="small"
                @click="handleOpenCSQAQ(row)"
                :disabled="!row.csqaq_id"
              >
                跳转QAQ
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        </div>

        <!-- 卡片显示 -->
        <div v-show="displayMode === 'card'" class="card-grid">
          <div
            v-for="item in searchResults"
            :key="item.market_listing_item_name"
            class="item-card"
          >
            <div class="card-image">
              <img
                v-if="getWeaponImage(item.steam_hash_name)"
                :src="getWeaponImage(item.steam_hash_name)"
                :alt="item.market_listing_item_name"
                class="weapon-image"
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
                <div class="info-row">
                  <span class="info-label">类型:</span>
                  <el-tag size="small" type="info">{{ item.weapon_type || '-' }}</el-tag>
                </div>
                <div class="info-row">
                  <span class="info-label">稀有度:</span>
                  <span 
                    v-if="item.rarity"
                    class="rarity-tag"
                    :style="{ color: getRarityColor(item.rarity), fontWeight: 600 }"
                  >
                    {{ item.rarity }}
                  </span>
                  <span v-else>-</span>
                </div>
                <div class="info-row">
                  <span class="info-label">CSQAQ ID:</span>
                  <el-tag v-if="item.csqaq_id" type="success" size="small">
                    {{ item.csqaq_id }}
                  </el-tag>
                  <el-tag v-else type="info" size="small">未映射</el-tag>
                </div>
                <div class="info-row">
                  <span class="info-label">悠悠有品:</span>
                  <span v-if="item.yyyp_Price" class="price">¥{{ item.yyyp_Price }}</span>
                  <span v-else>-</span>
                </div>
                <div class="info-row">
                  <span class="info-label">在售:</span>
                  <span>{{ item.on_sale_count || 0 }} 件</span>
                </div>
              </div>
              <div class="card-actions">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="handleSearchCSQAQ(item)"
                  :disabled="!item.csqaq_id"
                  :loading="searchingItems[item.csqaq_id]"
                  style="flex: 1;"
                >
                  搜索
                </el-button>
                <el-button 
                  type="success" 
                  size="small"
                  @click="handleOpenCSQAQ(item)"
                  :disabled="!item.csqaq_id"
                  style="flex: 1;"
                >
                  跳转QAQ
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!isSearching && searchResults.length === 0 && hasSearched" class="empty-state">
        <el-empty description="未找到相关饰品" />
      </div>

      <!-- 详细信息区域 -->
      <div v-if="currentItemDetail" class="detail-section-wrapper">
        <el-card class="detail-card">
          <template #header>
            <div class="detail-card-header">
              <span>饰品详细信息</span>
              <el-button type="text" @click="closeDetail">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </template>

          <div v-if="loadingDetail" class="detail-loading">
            <el-icon class="is-loading" :size="40"><Loading /></el-icon>
            <p>加载中...</p>
          </div>
          
          <div v-else class="detail-content">
        <div class="detail-header">
          <!-- 使用本地武器图片，与搜索结果一致 -->
          <div class="item-image-container">
            <img 
              v-if="getWeaponImage(currentItemDetail.goods_info.steam_market_hash_name)" 
              :src="getWeaponImage(currentItemDetail.goods_info.steam_market_hash_name)" 
              class="item-image"
              alt="饰品图片"
              @error="(e) => handleImageError(e, currentItemDetail.goods_info.steam_market_hash_name)"
            />
            <div v-else class="item-image-placeholder">
              <span>无图片</span>
            </div>
          </div>
          <div class="item-info">
            <h2 class="item-name">{{ currentItemDetail.goods_info.name }}</h2>
            <div class="item-tags">
              <el-tag type="warning">{{ currentItemDetail.goods_info.rarity_localized_name }}</el-tag>
              <el-tag type="info">{{ currentItemDetail.goods_info.exterior_localized_name }}</el-tag>
              <el-tag type="success">{{ currentItemDetail.goods_info.type_localized_name }}</el-tag>
            </div>
          </div>
          <div class="basic-info-box">
            <h3 class="section-title">基本信息</h3>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="存世量">
                <span class="highlight-value">{{ currentItemDetail.goods_info.statistic }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="CSQAQ ID">
                {{ currentItemDetail.goods_info.id }}
              </el-descriptions-item>
              <el-descriptions-item label="BUFF ID">
                {{ currentItemDetail.goods_info.buff_id }}
              </el-descriptions-item>
              <el-descriptions-item label="悠悠有品 ID">
                {{ currentItemDetail.goods_info.yyyp_id }}
              </el-descriptions-item>
              <el-descriptions-item label="磨损范围" :span="2">
                {{ currentItemDetail.goods_info.min_float }} - {{ currentItemDetail.goods_info.max_float }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <el-divider />

        <div class="detail-section">
          <h3 class="section-title">价格信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="BUFF售价">
              <span class="price-value">¥{{ currentItemDetail.goods_info.buff_sell_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="BUFF在售">
              {{ currentItemDetail.goods_info.buff_sell_num }}
            </el-descriptions-item>
            <el-descriptions-item label="BUFF求购价">
              <span class="price-value">¥{{ currentItemDetail.goods_info.buff_buy_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="BUFF求购">
              {{ currentItemDetail.goods_info.buff_buy_num }}
            </el-descriptions-item>
            <el-descriptions-item label="悠悠有品售价">
              <span class="price-value">¥{{ currentItemDetail.goods_info.yyyp_sell_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="悠悠有品在售">
              {{ currentItemDetail.goods_info.yyyp_sell_num }}
            </el-descriptions-item>
            <el-descriptions-item label="Steam价格">
              <span class="price-value">¥{{ currentItemDetail.goods_info.steam_buy_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="Steam在售">
              {{ currentItemDetail.goods_info.steam_buy_num }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h3 class="section-title">租赁信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="租赁价格">
              <span class="price-value">¥{{ currentItemDetail.goods_info.yyyp_lease_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="租赁数量">
              {{ currentItemDetail.goods_info.yyyp_lease_num }}
            </el-descriptions-item>
            <el-descriptions-item label="长租价格">
              <span class="price-value">¥{{ currentItemDetail.goods_info.yyyp_long_lease_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="租赁年化">
              {{ currentItemDetail.goods_info.yyyp_lease_annual }}%
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- K线图预留区域 -->
        <div class="detail-section">
          <h3 class="section-title">价格走势</h3>
          <div class="chart-placeholder">
            <p>K线图功能开发中...</p>
          </div>
        </div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { useItemSearch } from './useItemSearch.js'

const {
  keyword,
  isSearching,
  searchResults,
  hasSearched,
  weaponNameList,
  isLoadingWeaponNames,
  searchingItems,
  currentItemDetail,
  loadingDetail,
  displayMode,
  image404Cache,
  filters,
  getRarityColor,
  performSearch,
  handleWeaponTypeChange,
  loadWeaponNamesIfNeeded,
  resetFilters,
  getWeaponImage,
  getItemDetail,
  handleImageError,
  closeDetail,
  Loading,
  Close
} = useItemSearch()
</script>

<style scoped src="./styles.css"></style>
