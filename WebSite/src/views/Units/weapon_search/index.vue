<template>
  <!-- 搜索饰品组件 -->
  <div class="weapon-search-component">
    <div class="search-section">
      <h2 class="section-title">搜索饰品</h2>
    
      <div class="search-container">
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
          
          <el-input 
            v-model.number="filters.priceMin" 
            placeholder="最低价格"
            type="number"
            clearable
            style="width: 150px;"
            class="no-spinner"
          />
          
          <el-input 
            v-model.number="filters.priceMax" 
            placeholder="最高价格"
            type="number"
            clearable
            style="width: 150px;"
            class="no-spinner"
          />
          
          <el-input 
            v-model.number="filters.minOnSaleCount" 
            placeholder="最小在售数量"
            type="number"
            clearable
            style="width: 150px;"
            class="no-spinner"
          />
        </div>
        
        <el-input
          v-model="keyword"
          placeholder="搜索饰品名称..."
          prefix-icon="Search"
          class="weapon-search-input"
          @keyup.enter="handleSearch"
          clearable
        >
          <template #append>
            <el-button 
              type="primary" 
              @click="handleSearch" 
              :loading="isSearching"
            >
              搜索
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 搜索结果表格 -->
      <div v-if="searchResults.length > 0" class="search-results-table">
        <div class="results-header" @click="toggleResults">
          <span class="results-title">
            搜索结果 ({{ searchResults.length }} 件)
          </span>
          <div class="results-actions" @click.stop>
            <el-button 
              type="success" 
              size="small"
              @click="handleAddAll"
              :disabled="searchResults.length === 0"
            >
              <el-icon><Document /></el-icon>
              一键添加全部
            </el-button>
            <el-button 
              type="text" 
              size="small"
              @click="handleClear"
            >
              清除结果
            </el-button>
            <el-button 
              type="text" 
              class="collapse-indicator"
            >
              <el-icon :size="16">
                <ArrowUp v-if="!isCollapsed" />
                <ArrowDown v-else />
              </el-icon>
            </el-button>
          </div>
        </div>
        
        <div v-show="!isCollapsed">
          <el-table 
              :data="searchResults" 
              style="width: 100%"
              :row-class-name="getRowClassName"
            >
            <el-table-column type="index" label="#" width="60" align="center" />
            
            <el-table-column label="饰品名称" min-width="250" show-overflow-tooltip>
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
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="价格" width="100" align="center">
              <template #default="{ row }">
                <span class="price-text" v-if="platformType === 'youpin' && row.yyyp_Price">
                  ¥{{ row.yyyp_Price }}
                </span>
                <span class="price-text" v-else-if="platformType === 'buff' && row.buff_Price">
                  ¥{{ row.buff_Price }}
                </span>
                <span class="price-text" v-else-if="platformType === 'steam' && row.yyyp_Price">
                  ¥{{ row.yyyp_Price }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="在售数量" width="100" align="center">
              <template #default="{ row }">
                <span class="count-text" v-if="platformType === 'youpin' && row.yyyp_OnSaleCount">
                  {{ row.yyyp_OnSaleCount }}
                </span>
                <span class="count-text" v-else-if="platformType === 'buff' && row.buff_OnSaleCount">
                  {{ row.buff_OnSaleCount }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column v-if="platformType === 'youpin'" label="悠悠有品ID" width="130" align="center">
              <template #default="{ row }">
                <el-tag type="warning" v-if="row.yyyp_id">{{ row.yyyp_id }}</el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column v-if="platformType === 'buff'" label="BUFF ID" width="110" align="center">
              <template #default="{ row }">
                <el-tag type="info" v-if="row.buff_id">{{ row.buff_id }}</el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column v-if="platformType === 'steam'" label="Steam Hash Name" width="220" align="center">
              <template #default="{ row }">
                <el-tag type="info" v-if="row.steam_hash_name">{{ row.steam_hash_name }}</el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="handleAddWeapon(row)"
                  :disabled="!getWeaponIdByPlatform(row)"
                >
                  添加ID
                </el-button>
              </template>
            </el-table-column>
            </el-table>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { useWeaponSearch } from './useWeaponSearch.js'

const {
  loading,
  keyword,
  weaponType,
  rarity,
  weaponResults,
  hasSearched,
  handleSearch,
  clearSearch,
  getRarityColor
} = useWeaponSearch()
</script>

<style scoped src="./styles.css"></style>
