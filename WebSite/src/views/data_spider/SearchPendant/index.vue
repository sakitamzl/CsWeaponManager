<template>
  <div class="spider-pendant-container">
    <div class="page-layout">
      <!-- 左侧配置管理栏 -->
      <aside 
        class="config-sidebar" 
        :class="{ collapsed: isConfigSectionsCollapsed }"
        @click="handleSidebarAreaClick"
      >
        <div class="sidebar-header clickable" @click.stop="toggleConfigSections">
          <div class="sidebar-header-row" :class="{ collapsed: isConfigSectionsCollapsed }">
            <div class="sidebar-header-title">配置管理</div>
            <div class="sidebar-header-actions">
              <el-button 
                type="success" 
                @click.stop="createNewConfig"
                :disabled="isCrawling"
              >
                <el-icon><Document /></el-icon>
                新建
              </el-button>
              
              <el-button 
                type="info" 
                @click.stop="loadConfigList"
              >
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </div>

        <div class="sidebar-divider" v-show="!isConfigSectionsCollapsed"></div>

        <div class="config-list" v-show="!isConfigSectionsCollapsed">
          <div 
            v-for="config in savedConfigs" 
            :key="config.id"
            class="config-item"
            :class="{ active: selectedConfigId === config.id }"
            @click="selectConfig(config.id)"
          >
            <div class="config-item-header">
              <div style="display: flex; align-items: center; gap: 8px; flex: 1;">
                <span class="config-name">{{ config.dataName }}</span>
                <el-tag 
                  :type="config.platformType === 'buff' ? 'warning' : (config.platformType === 'youpin' ? 'success' : 'info')" 
                  size="small"
                >
                  {{ getSourceLabel(config.platformType) }}
                </el-tag>
              </div>
            </div>
            <div v-if="config.description" class="config-description">
              {{ config.description }}
            </div>
          </div>

          <div v-if="savedConfigs.length === 0" class="empty-config">
            <el-empty description="暂无保存的配置" :image-size="80" />
          </div>
        </div>
      </aside>

      <!-- 右侧主内容区域 -->
      <div class="main-content-area">

      <!-- 统一的工具区域 -->
      <div class="unified-tool-section" :class="{ collapsed: isConfigSectionsCollapsed }">
        <div class="tool-section-header" @click="toggleConfigSections">
          <h2 class="section-title">爬取配置</h2>
          <el-button type="text" class="collapse-btn">
            <el-icon :size="20">
              <ArrowUp v-if="!isConfigSectionsCollapsed" />
              <ArrowDown v-else />
            </el-icon>
          </el-button>
        </div>
        
        <div class="tool-section-content" v-show="!isConfigSectionsCollapsed">
        <div class="tool-section">
        
        <div class="form-container">
          <el-form :model="crawlForm" label-width="120px" ref="crawlFormRef">
            <div class="form-row">
              <el-form-item label="配置名称" required class="form-item-quarter">
                <el-input 
                  v-model="crawlForm.configName" 
                  placeholder="请输入配置名称"
                  clearable
                />
              </el-form-item>

              <el-form-item label="平台类型" required class="form-item-quarter">
                <el-select 
                  v-model="crawlForm.platformType" 
                  placeholder="选择平台类型"
                  style="width: 100%;"
                  :disabled="!!selectedConfigId || (weaponIdList && weaponIdList.length > 0)"
                  @change="handlePlatformTypeChange"
                >
                  <el-option label="悠悠有品" value="youpin" />
                  <el-option label="BUFF" value="buff" />
                </el-select>
              </el-form-item>

              <el-form-item label="爬取账号" required class="form-item-quarter">
                <el-select 
                  v-model="crawlForm.crawlAccountId" 
                  placeholder="选择爬取账号"
                  style="width: 100%;"
                  filterable
                >
                  <el-option 
                    v-for="item in filteredSteamIdList" 
                    :key="item.steamID || item.steam_id" 
                    :label="`${item.dataName || '未命名'} (${item.steamID || item.steam_id || '无ID'})`" 
                    :value="item.steamID || item.steam_id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="购买账号" required class="form-item-quarter">
                <el-select 
                  v-model="crawlForm.steamId" 
                  placeholder="选择购买账号"
                  style="width: 100%;"
                  filterable
                >
                  <el-option 
                    v-for="item in filteredSteamIdList" 
                    :key="item.steamID || item.steam_id" 
                    :label="`${item.dataName || '未命名'} (${item.steamID || item.steam_id || '无ID'})`" 
                    :value="item.steamID || item.steam_id"
                  />
                </el-select>
              </el-form-item>
            </div>

            <el-form-item>
              <div class="custom-config-grid">
                <div class="custom-config-field">
                  <div class="field-label">查询间隔</div>
                  <div class="field-control no-spinner">
                    <el-input
                      v-model.number="customConfigForm['饰品自动查询间隔']"
                      type="number"
                      placeholder="例如 3"
                      min="1"
                      style="width: 100px;"
                    />
                  </div>
                </div>

                <div class="custom-config-field">
                  <div class="field-label">最大差价百分比 (%)</div>
                  <div class="field-control no-spinner">
                    <el-input
                      v-model.number="customConfigForm['最大差价百分比']"
                      type="number"
                      placeholder="例如 80"
                      min="0"
                      style="width: 100px;"
                    />
                  </div>
                </div>

                <div class="custom-config-field">
                  <div class="field-label">最大溢价</div>
                  <div class="field-control no-spinner">
                    <el-input
                      v-model.number="customConfigForm['最大溢价']"
                      type="number"
                      placeholder="例如 200"
                      min="0"
                      style="width: 100px;"
                    />
                  </div>
                </div>

                <div class="custom-config-field">
                  <div class="field-label">自动购买</div>
                  <div class="field-control">
                    <el-select
                      v-model="customConfigForm['是否自动购买']"
                      placeholder="请选择"
                      style="width: 100px;"
                    >
                      <el-option
                        v-for="option in booleanOptions"
                        :key="`auto-buy-${option.value}`"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                  </div>
                </div>

                <div class="custom-config-field">
                  <div class="field-label">印花板</div>
                  <div class="field-control">
                    <el-select
                      v-model="customConfigForm['印花板']"
                      placeholder="请选择"
                      style="width: 100px;"
                    >
                      <el-option
                        v-for="option in booleanOptions"
                        :key="`sticker-${option.value}`"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                  </div>
                </div>

                <div class="custom-config-field">
                  <div class="field-label">收益不少于</div>
                  <div class="field-control no-spinner">
                    <el-input
                      v-model.number="customConfigForm['收益不少于']"
                      type="number"
                      placeholder="例如 3"
                      style="width: 100px;"
                    />
                  </div>
                </div>
              </div>
            </el-form-item>

            <el-form-item>
              <template #label>
                <div class="collapsible-label">
                  <span class="label-text" @click="toggleWeaponList">
                    饰品列表 ({{ weaponIdList.length }})
                    <el-icon 
                      class="collapse-icon-inline" 
                      :class="{ 'is-collapsed': isWeaponListCollapsed }"
                    >
                      <ArrowUp v-if="!isWeaponListCollapsed" />
                      <ArrowDown v-else />
                    </el-icon>
                  </span>
                </div>
              </template>
              <div class="weapon-id-section" v-show="!isWeaponListCollapsed">
                <div class="weapon-id-tags">
                  <el-tag
                    v-for="weapon in weaponIdList"
                    :key="weapon.id"
                    closable
                    @close="removeWeaponId(weapon.id)"
                    type="primary"
                    size="large"
                  >
                    {{ weapon.name }} (ID: {{ weapon.id }})
                  </el-tag>
                </div>
                <el-button 
                  v-if="weaponIdList && weaponIdList.length > 0"
                  type="danger" 
                  size="small"
                  @click="clearAllWeaponIds"
                  style="margin-left: 10px;"
                >
                  <el-icon><Delete /></el-icon>
                  一键清空
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <div class="action-buttons">
          <el-button 
            type="success" 
            size="large"
            @click="saveConfig"
            :disabled="isCrawling"
          >
            <el-icon><Document /></el-icon>
            保存当前配置
          </el-button>

          <el-button 
            type="danger" 
            size="large"
            @click="deleteCurrentConfig"
            :disabled="isCrawling || !selectedConfigId"
          >
            <el-icon><Delete /></el-icon>
            删除当前配置
          </el-button>

          <el-button
            type="primary"
            size="large"
            @click="startCrawl"
            :disabled="isCrawling || !canStartCrawl"
            :loading="isCrawling"
          >
            {{ isCrawling ? '搜索中...' : '开始搜索' }}
          </el-button>

          <el-button
            type="danger"
            size="large"
            @click="stopCrawl"
            :disabled="!isCrawling"
          >
            停止搜索
          </el-button>
        </div>
        </div>

        <!-- 搜索饰品组件 -->
        <WeaponSearch 
          :platformType="crawlForm.platformType"
          @add-weapon="handleAddWeaponFromSearch"
          @add-all-weapons="handleAddAllWeaponsFromSearch"
        />

        </div>
        <!-- 结束 tool-section-content -->
      </div>
      <!-- 结束 unified-tool-section -->

      <!-- 查询结果区域 -->
      <div v-if="allCrawlItems && allCrawlItems.length > 0" class="result-section">
        <div class="result-header">
          <h2 class="section-title">查询结果 ({{ allCrawlItems.length }} 件)</h2>
          <el-button 
            type="danger" 
            size="small"
            @click="clearCrawlHistory"
            :disabled="isCrawling"
          >
            <el-icon><Delete /></el-icon>
            清空列表
          </el-button>
        </div>
        
        <!-- 统一商品列表 -->
        <el-table 
          :data="allCrawlItems" 
          style="width: 100%; min-width: max(1200px, 100%);"
          stripe
        >
          <el-table-column label="图标" width="80" fixed="left" align="center">
            <template #default="scope">
              <template v-if="getItemIconUrl(scope.row)">
                <a 
                  :href="getItemIconUrl(scope.row)" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="icon-link"
                >
                  <img 
                    :src="getItemIconUrl(scope.row)" 
                    class="weapon-icon"
                    :alt="scope.row.weapon_name || 'icon'"
                    referrerpolicy="no-referrer"
                  />
                </a>
              </template>
              <span v-else class="no-icon">-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="武器名称" min-width="260" fixed="left">
            <template #default="scope">
              <el-tooltip 
                :content="scope.row.weapon_name" 
                placement="top"
                :disabled="!scope.row.weapon_name || scope.row.weapon_name.length <= 20"
              >
                <div class="weapon-name-cell">{{ scope.row.weapon_name }}</div>
              </el-tooltip>
            </template>
          </el-table-column>
          
          <el-table-column label="价格" width="100">
              <template #default="scope">
                <span class="price">¥{{ scope.row.price }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="溢价" width="100">
              <template #default="scope">
                <el-tag type="danger" size="small">
                  {{ scope.row.spread.toFixed(2) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="手续费" width="100" align="center">
              <template #default="scope">
                <span class="commission-fee">¥{{ scope.row.commissionFee ? scope.row.commissionFee.toFixed(2) : '0.00' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="收益" width="120" align="center">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.priceDiff < 0 ? 'danger' : (scope.row.priceDiff < 3 ? 'warning' : 'success')" 
                  size="small"
                >
                  {{ scope.row.priceDiff >= 0 ? '+' : '' }}{{ scope.row.priceDiff.toFixed(2) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="磨损" width="240">
              <template #default="scope">
                {{ scope.row.abrade }}
              </template>
            </el-table-column>
            
            <el-table-column label="挂件" min-width="250">
              <template #default="scope">
                <div class="pendant-list">
                  <div
                    v-for="(pendant, index) in scope.row.pendants" 
                    :key="index"
                    class="pendant-item"
                  >
                    <img v-if="pendant.img" :src="pendant.img" class="pendant-img" :alt="pendant.name" />
                    <div class="pendant-info">
                      <div class="pendant-name">{{ pendant.name }}</div>
                      <div class="pendant-details">
                        <span class="pendant-price">¥{{ pendant.price }}</span>
                        <span class="pendant-pattern">模板: {{ pendant.pattern }}</span>
                      </div>
                    </div>
                  </div>
                  <span v-if="!scope.row.pendants || scope.row.pendants.length === 0" class="no-pendant">无挂件</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="卖家" min-width="150">
              <template #default="scope">
                {{ scope.row.userNickName || '未知' }}
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="scope">
                <el-button 
                  :type="getBuyButtonType(scope.row)"
                  size="small"
                  @click="handleBuyWeapon(scope.row)"
                  :loading="buyingItems[scope.row.id]"
                  :disabled="purchasedItems.has(scope.row.id)"
                >
                  {{ purchasedItems.has(scope.row.id) ? '已购买' : '购买' }}
                </el-button>
              </template>
            </el-table-column>
        </el-table>
      </div>

      </div>
      <!-- 结束 main-content-area -->
    </div>
    <!-- 结束 page-layout -->

  </div>
</template>

<script>
import { useSearchPendant } from './useSearchPendant.js'
import { Refresh, Document, Delete, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import WeaponSearch from '@/views/Units/weapon_search/index.vue'

export default {
  name: 'SearchPendant',
  components: {
    WeaponSearch,
    Refresh,
    Document,
    Delete,
    ArrowUp,
    ArrowDown
  },
  setup() {
    return useSearchPendant()
  }
}
</script>

<style scoped>
@import './styles.css';

.spider-pendant-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
  padding: 2rem;
}

.page-header {
  margin-bottom: 1rem;
  padding: 1rem;
}

.page-layout {
  display: flex;
  gap: 1.5rem;
  min-height: calc(100vh - 150px);
  max-width: 100%;
}

/* 左侧配置管理栏 */
.config-sidebar {
  width: 280px;
  min-width: 280px;
  flex-shrink: 0;
  background-color: #1e1e1e;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  height: auto;
  position: sticky;
  top: 1rem;
  transition: width 0.25s ease, min-width 0.25s ease;
}

.config-sidebar.collapsed {
  width: 48px;
  min-width: 48px;
}

.sidebar-header {
  margin-bottom: 1.25rem;
}

.sidebar-header-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #4CAF50;
  white-space: nowrap;
  margin-bottom: 0.5rem;
}

.sidebar-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  overflow: hidden;
  max-width: 100%;
  opacity: 1;
  transition: max-width 0.25s ease, opacity 0.25s ease;
}

.sidebar-header-row.collapsed {
  max-width: 0;
  opacity: 0;
  pointer-events: none;
}

.sidebar-header-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #4CAF50;
  white-space: nowrap;
}

.sidebar-header.clickable {
  cursor: pointer;
}

.sidebar-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #4CAF50;
  margin: 0;
}

.config-list {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1rem;
  padding-right: 0.5rem;
  padding-left: 0.25rem;
}

/* 优化配置列表中的标签显示 */
.config-item :deep(.el-tag) {
  flex-shrink: 0;
  font-size: 0.75rem;
  padding: 2px 8px;
  height: auto;
  line-height: 1.4;
  border-radius: 4px;
  font-weight: 500;
}

.config-item {
  background-color: #252525;
  border: 1px solid #333;
  border-radius: 0.5rem;
  padding: 0.875rem;
  margin-bottom: 0.625rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.config-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: transparent;
  transition: background-color 0.3s ease;
}

.config-item:hover {
  border-color: #4CAF50;
  background-color: #2a2a2a;
  transform: translateX(2px);
}

.config-item:hover::before {
  background-color: #4CAF50;
}

.config-item.active {
  border-color: #4CAF50;
  background-color: rgba(76, 175, 80, 0.15);
  box-shadow: 0 0 12px rgba(76, 175, 80, 0.4);
  transform: translateX(0);
}

.config-item.active::before {
  background-color: #4CAF50;
  width: 4px;
}

.config-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.375rem;
  gap: 0.5rem;
}

.config-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #fff;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.config-item.active .config-name {
  color: #4CAF50;
}

.config-item-meta {
  margin-bottom: 0.25rem;
}

.config-time {
  font-size: 0.75rem;
  color: #888;
}

.config-description {
  font-size: 0.8rem;
  color: #aaa;
  margin-top: 0.375rem;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  padding-left: 0.25rem;
}

.config-item.active .config-description {
  color: #bbb;
}

.empty-config {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  padding: 2rem 1rem;
}

.empty-config :deep(.el-empty__description) {
  color: #888;
  font-size: 0.9rem;
}

.sidebar-divider {
  height: 1px;
  background-color: #2f2f2f;
  border-radius: 1px;
  margin-bottom: 1rem;
  margin-top: 0.5rem;
}

.sidebar-header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-shrink: 0;
}

.sidebar-header-actions .el-button {
  min-width: 64px;
}

/* 右侧主内容区域 */
.main-content-area {
  flex: 1;
  min-width: 0;
  width: auto;
  overflow-x: hidden;
}

/* 统一工具区域容器 */
.unified-tool-section {
  background-color: #1e1e1e;
  border-radius: 1rem;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.unified-tool-section.collapsed {
  padding: 1rem 2rem;
}

.tool-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 1rem;
  background-color: #2a2a2a;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  user-select: none;
  transition: all 0.3s ease;
}

.tool-section-header:hover {
  background-color: #333;
}

.tool-section-header .section-title {
  color: #fff;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  flex: 1;
}

.unified-tool-section.collapsed .tool-section-header {
  margin-bottom: 0;
}

.collapse-btn {
  padding: 0.25rem;
  color: #4CAF50;
  transition: transform 0.3s ease;
}

.collapse-btn:hover {
  color: #66BB6A;
  transform: scale(1.1);
}

.main-section-title {
  color: #fff;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.tool-section-content {
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-card {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #252525;
  border-radius: 0.75rem;
  border: 1px solid #333;
}

.search-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #252525;
  border-radius: 0.75rem;
  border: 1px solid #333;
}

.search-container {
  margin-bottom: 1.5rem;
}

.search-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.weapon-search-input {
  width: 100%;
}

.search-results-table {
  margin-top: 1rem;
  border: 1px solid #333;
  border-top: none;
  border-radius: 0 0 0.5rem 0.5rem;
  overflow: hidden;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: #2a2a2a;
  border-radius: 0.5rem 0.5rem 0 0;
  border: 1px solid #333;
  border-bottom: none;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s ease;
}

.results-header:hover {
  background-color: #333;
}

.results-title {
  font-size: 1rem;
  font-weight: 600;
  color: #4CAF50;
}

.results-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

/* 可折叠标签样式 */
.collapsible-label {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
}

.collapsible-label .label-text {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  cursor: pointer;
  user-select: none;
  transition: color 0.2s ease;
}

.collapsible-label .label-text:hover {
  color: #409EFF;
}

.collapsible-label .collapse-icon-inline {
  font-size: 0.875rem;
  transition: transform 0.3s ease;
  color: inherit;
}

.collapsible-label .collapse-icon-inline.is-collapsed {
  transform: rotate(0deg);
}

.weapon-name {
  color: #fff;
  font-weight: 500;
}

/* 武器图标和名称样式已移至 resultSection.css */

.hash-name-text {
  color: #aaa;
  font-size: 0.875rem;
}

.no-data {
  color: #666;
  font-size: 0.875rem;
}

.price-text {
  color: #67C23A;
  font-weight: 600;
  font-size: 0.95rem;
}

.count-text {
  color: #409EFF;
  font-weight: 500;
  font-size: 0.9rem;
}

.rarity-text {
  font-weight: 600;
  font-size: 0.9rem;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
}

.platform-tip {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.5rem;
  color: #E6A23C;
  font-size: 0.75rem;
}

.load-more-container {
  text-align: center;
  padding: 1rem;
  color: #909399;
  font-size: 0.875rem;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #409EFF;
}

.no-more-data {
  color: #909399;
}

.can-load-more {
  color: #606266;
}

.weapon-row {
  cursor: pointer;
}

.weapon-row:hover {
  background-color: rgba(76, 175, 80, 0.1) !important;
}

.tool-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #444;
}

.form-container {
  background-color: #2a2a2a;
  padding: 1.5rem;
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0;
}

/* 垂直堆叠的表单行 */
.form-row-stacked {
  flex-direction: column;
  gap: 0;
}

.form-item-full {
  width: 100%;
  margin-bottom: 18px;
}

.form-item-half {
  flex: 1;
  margin-bottom: 18px;
}

.form-item-third {
  flex: 1;
  margin-bottom: 18px;
}

.form-item-quarter {
  flex: 1;
  margin-bottom: 18px;
}

.form-hint {
  color: #888;
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

.weapon-id-section {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
}

.weapon-id-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  min-width: 140px;
}

/* 结果区域样式已移至 resultSection.css */

/* 价格区间提示样式 */
.price-range-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

/* 隐藏数字输入框的加减器 */
.no-spinner :deep(input[type="number"]::-webkit-outer-spin-button),
.no-spinner :deep(input[type="number"]::-webkit-inner-spin-button) {
  -webkit-appearance: none;
  appearance: none;
  margin: 0;
}

.no-spinner :deep(input[type="number"]) {
  -moz-appearance: textfield;
  appearance: textfield;
}

.no-spinner :deep(input[type="number"]::-webkit-inner-spin-button),
.no-spinner :deep(input[type="number"]::-webkit-outer-spin-button) {
  -webkit-appearance: none;
  margin: 0;
}

.result-info {
  display: grid;
  gap: 1rem;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #333;
}

.result-item:last-child {
  border-bottom: none;
}

.result-label {
  color: #888;
  font-weight: 500;
}

.result-value {
  color: #fff;
  font-weight: 600;
}

.result-value.success {
  color: #67C23A;
}

.result-value.error {
  color: #F56C6C;
}

.result-value.highlight {
  color: #E6A23C;
  font-size: 1.1rem;
}

/* Element Plus 组件深色主题适配 */
:deep(.el-input__wrapper) {
  background-color: #1e1e1e;
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

:deep(.el-textarea__inner) {
  background-color: #1e1e1e;
  color: #fff;
  border-color: #444;
}

:deep(.el-textarea__inner:hover) {
  border-color: #4CAF50;
}

:deep(.el-textarea__inner:focus) {
  border-color: #4CAF50;
}

:deep(.el-select .el-input__wrapper) {
  background-color: #1e1e1e;
}

:deep(.el-form-item__label) {
  color: #aaa;
}

:deep(.el-switch) {
  --el-switch-on-color: #4CAF50;
  --el-switch-off-color: #555;
}

/* 自定义配置表单 */
.custom-config-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem 2.5rem;
  align-items: center;
}

.custom-config-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 48px;
  flex: 0 0 auto;
}

.custom-config-field .field-label {
  min-width: auto;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  white-space: nowrap;
  flex-shrink: 0;
}

.custom-config-field .field-control {
  flex: 0 0 100px;
  width: 100px;
}

/* 响应式设计 */
/* 大屏幕优化 */
@media (min-width: 1920px) {
  .config-sidebar {
    width: 320px;
    min-width: 320px;
  }
}

/* iPad Pro 横屏 (1024px - 1366px) */
@media (min-width: 1024px) and (max-width: 1366px) {
  .spider-pendant-container {
    padding: 1.5rem;
  }

  .page-layout {
    gap: 1rem;
  }

  .config-sidebar {
    width: 240px;
    min-width: 240px;
    padding: 1.25rem;
  }

  .unified-tool-section {
    padding: 1.25rem 1.5rem;
  }

  .form-container {
    padding: 1.25rem;
  }

  .custom-config-grid {
    gap: 1rem 1.5rem;
  }

  .custom-config-field {
    flex: 0 0 calc(33.333% - 1rem);
    min-width: 200px;
  }

  .custom-config-field .field-label {
    min-width: 100px;
    font-size: 0.85rem;
  }

  .form-row {
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .form-item-quarter {
    flex: 0 0 calc(50% - 0.375rem);
    min-width: 0;
  }

  .action-buttons {
    gap: 0.75rem;
  }

  .action-buttons .el-button {
    min-width: 120px;
    font-size: 0.9rem;
  }

  /* 表格优化 */
  .result-section {
    padding: 1.25rem;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .result-section :deep(.el-table) {
    font-size: 0.875rem;
    min-width: 1200px;
  }

  .result-section :deep(.el-table th),
  .result-section :deep(.el-table td) {
    padding: 8px 6px;
  }

  .result-section :deep(.el-table__header-wrapper),
  .result-section :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }

  .weapon-icon {
    width: 50px;
    height: 50px;
  }

  .pendant-img {
    width: 50px;
    height: 50px;
    max-width: 50px;
    max-height: 50px;
    min-width: 50px;
    min-height: 50px;
  }

  .pendant-name {
    font-size: 13px;
  }

  .pendant-details {
    font-size: 11px;
    gap: 8px;
  }

  .section-title {
    font-size: 1.3rem;
  }

  .tool-section-header .section-title {
    font-size: 1.1rem;
  }

  /* 优化按钮大小 */
  .result-section :deep(.el-button--small) {
    padding: 5px 10px;
    font-size: 0.8rem;
  }

  /* 触摸优化 */
  .config-item,
  .action-buttons .el-button,
  .result-section :deep(.el-button) {
    -webkit-tap-highlight-color: rgba(76, 175, 80, 0.2);
    touch-action: manipulation;
  }

  /* 优化输入框在 iPad 上的显示 */
  .form-container :deep(.el-input),
  .form-container :deep(.el-select) {
    font-size: 0.9rem;
  }

  /* 优化标签间距 */
  .weapon-id-tags {
    gap: 6px;
  }

  .weapon-id-tags :deep(.el-tag) {
    margin: 0;
    font-size: 0.85rem;
    padding: 4px 8px;
  }

  /* 配置管理优化 */
  .config-item {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .config-name {
    font-size: 0.9rem;
  }

  .config-item :deep(.el-tag) {
    font-size: 0.7rem;
    padding: 2px 6px;
  }

  .config-description {
    font-size: 0.75rem;
  }
}

/* iPad 竖屏 / 小屏幕平板 (768px - 1024px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .spider-pendant-container {
    padding: 1rem;
  }

  .page-layout {
    flex-direction: column;
    gap: 1rem;
  }

  .config-sidebar {
    width: 100%;
    min-width: 100%;
    max-width: 100%;
    max-height: 350px;
    position: static;
    margin-bottom: 0;
  }

  .config-list {
    max-height: 200px;
  }

  .unified-tool-section {
    padding: 1rem 1.25rem;
  }

  .form-container {
    padding: 1rem;
  }

  .custom-config-grid {
    gap: 0.75rem 1rem;
  }

  .custom-config-field {
    flex: 0 0 calc(50% - 0.5rem);
    min-width: 180px;
  }

  .custom-config-field .field-label {
    min-width: 90px;
    font-size: 0.8rem;
  }

  .form-row {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .form-item-quarter {
    flex: 0 0 calc(50% - 0.25rem);
    min-width: 0;
  }

  .action-buttons {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .action-buttons .el-button {
    flex: 1 1 calc(50% - 0.25rem);
    min-width: 140px;
  }

  /* 表格优化 */
  .result-section {
    padding: 1rem;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .result-section :deep(.el-table) {
    font-size: 0.85rem;
    min-width: 1200px;
  }

  .result-section :deep(.el-table th),
  .result-section :deep(.el-table td) {
    padding: 6px 4px;
  }

  .result-section :deep(.el-table__header-wrapper),
  .result-section :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }

  .weapon-icon {
    width: 45px;
    height: 45px;
  }

  .pendant-img {
    width: 45px;
    height: 45px;
    max-width: 45px;
    max-height: 45px;
    min-width: 45px;
    min-height: 45px;
  }

  .pendant-name {
    font-size: 12px;
  }

  .pendant-details {
    font-size: 10px;
    gap: 6px;
  }

  /* 优化按钮大小 */
  .result-section :deep(.el-button--small) {
    padding: 4px 8px;
    font-size: 0.75rem;
  }

  /* 优化标签显示 */
  .result-section :deep(.el-tag) {
    font-size: 0.75rem;
    padding: 2px 6px;
  }

  /* 触摸优化 */
  .config-item,
  .action-buttons .el-button,
  .result-section :deep(.el-button) {
    -webkit-tap-highlight-color: rgba(76, 175, 80, 0.2);
    touch-action: manipulation;
    min-height: 36px;
  }

  /* 优化输入框在 iPad 上的显示 */
  .form-container :deep(.el-input),
  .form-container :deep(.el-select) {
    font-size: 0.85rem;
  }

  /* 优化标签间距 */
  .weapon-id-tags {
    gap: 6px;
  }

  .weapon-id-tags :deep(.el-tag) {
    margin: 0;
    font-size: 0.8rem;
    padding: 3px 6px;
  }

  /* 配置管理优化 */
  .config-item {
    padding: 0.625rem;
    margin-bottom: 0.5rem;
  }

  .config-name {
    font-size: 0.85rem;
  }

  .config-item :deep(.el-tag) {
    font-size: 0.65rem;
    padding: 1px 5px;
  }

  .config-description {
    font-size: 0.7rem;
  }

  .config-list {
    padding-right: 0.25rem;
  }

  .sidebar-header-actions {
    flex-direction: column;
    gap: 0.375rem;
  }

  .sidebar-header-actions .el-button {
    width: 100%;
    min-width: auto;
    font-size: 0.8rem;
    padding: 6px 12px;
  }
}

/* 中等屏幕 */
@media (max-width: 1440px) and (min-width: 1367px) {
  .config-sidebar {
    width: 260px;
    min-width: 260px;
    padding: 1rem;
  }
}

/* 小屏幕 - 切换为垂直布局 */
@media (max-width: 1024px) {
  .page-layout {
    flex-direction: column;
  }

  .config-sidebar {
    width: 100%;
    min-width: 100%;
    max-width: 100%;
    max-height: 400px;
    position: static;
    margin-bottom: 1rem;
  }

  .config-list {
    max-height: 250px;
  }
}

@media (max-width: 768px) {
  .spider-sticker-container {
    padding: 1rem;
  }

  .page-header {
    padding: 0.5rem;
  }

  .back-button {
    width: 100%;
  }

  .config-sidebar {
    padding: 1rem;
  }

  .sidebar-header-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .search-section {
    padding: 1rem;
  }

  .form-container {
    padding: 1rem;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-item-half {
    width: 100%;
  }

  .form-item-third {
    width: 100%;
  }

  .form-item-quarter {
    width: 100%;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .el-button {
    width: 100%;
  }
}

/* 滚动条样式 */
.config-list::-webkit-scrollbar {
  width: 8px;
}

.config-list::-webkit-scrollbar-track {
  background: #1a1a1a;
  border-radius: 4px;
}

.config-list::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

.config-list::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>


