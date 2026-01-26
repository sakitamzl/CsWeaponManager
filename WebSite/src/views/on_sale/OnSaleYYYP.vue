<template>
  <div>
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
        <div style="margin-left: auto;">
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

    <!-- 统计信息 -->
    <div class="inventory-stats">
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

    <!-- 卡片显示 -->
    <div class="card-container" v-if="displayMode === 'card'">
      <!-- 多选模式下的操作按钮 -->
      <div v-if="isMultiSelectMode && selectedItems.length > 0" class="multi-select-actions">
        <div class="selected-count">
          已选择 {{ selectedItems.length }} 件物品
        </div>
        <div class="action-buttons">
          <el-button type="danger" @click="selectedItems = []">清空选择</el-button>
          <el-button type="success">批量改价</el-button>
          <el-button type="primary">批量下架</el-button>
        </div>
      </div>

      <div v-loading="loading" class="card-grid">
        <div
          v-for="item in currentDisplayData"
          :key="item.id"
          class="inventory-card"
          :class="{ 
            'selected': isItemSelected(item.id), 
            'multi-select-mode': isMultiSelectMode
          }"
          @click="handleCardClick(item)"
        >
          <div class="card-image">
            <img
              v-if="getWeaponImage(item.steam_hash_name)"
              :src="getWeaponImage(item.steam_hash_name)"
              :alt="item.item_name"
              class="weapon-image"
              @error="(e) => handleImageError(e, item.steam_hash_name)"
            />
            <div v-else class="image-placeholder">
              <span>无图片</span>
            </div>
            <!-- 贴纸覆盖层 - 左下角 -->
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
            <!-- 挂件覆盖层 - 右上角 -->
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
                  <div class="float-segment fn" title="崭新出厂 (0.00 - 0.07)"></div>
                  <div class="float-segment mw" title="略有磨损 (0.07 - 0.15)"></div>
                  <div class="float-segment ft" title="久经沙场 (0.15 - 0.38)"></div>
                  <div class="float-segment ww" title="破损不堪 (0.38 - 0.45)"></div>
                  <div class="float-segment bs" title="战痕累累 (0.45 - 1.00)"></div>
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
              <!-- 第一行：售价和购入价 -->
              <div class="price-row">
                <div class="price-group">
                  <span class="price-label">售价:</span>
                  <span class="price-value sale-price">¥{{ parseFloat(item.sale_price).toFixed(2) }}</span>
                </div>
                <div class="price-group" v-if="item.buy_price">
                  <span class="price-label">购入:</span>
                  <span class="price-value">¥{{ parseFloat(item.buy_price).toFixed(2) }}</span>
                </div>
              </div>
              <!-- 第二行：预期收益 -->
              <div class="price-row" v-if="item.buy_price">
                <div class="price-group">
                  <span class="price-label">预期收益:</span>
                  <span 
                    class="price-value"
                    :class="getPriceDiffClass(item.sale_price, item.buy_price)"
                  >
                    {{ (parseFloat(item.sale_price) - parseFloat(item.buy_price)) >= 0 ? '+' : '' }}¥{{ Math.abs(parseFloat(item.sale_price) - parseFloat(item.buy_price)).toFixed(2) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="card-footer">
              <div class="card-tags">
                <el-tag v-if="item.rename" type="info" size="small" class="rename-tag">
                  <span class="tag-icon">🏷️</span>{{ item.rename }}
                </el-tag>
                <el-tag v-if="item.on_sale_time" type="success" size="small">
                  {{ formatOnSaleTime(item.on_sale_time) }}
                </el-tag>
              </div>
              <div class="card-actions">
                <el-button size="small" type="success" @click.stop="handleUpdatePrice(item)">
                  改价
                </el-button>
                <el-button size="small" type="primary" @click.stop="handleRemoveFromSale(item)">
                  下架
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="table-footer">
        <span>共 {{ currentDisplayData.length }} 条数据</span>
      </div>
    </div>

    <!-- 列表显示 -->
    <div class="table-container" v-if="displayMode === 'list'">
      <el-table
        :data="currentDisplayData"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        :row-style="{ backgroundColor: 'transparent' }"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        height="calc(100vh - 400px)"
        @row-click="openPreview"
      >
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
              <div class="item-extras" v-if="hasExtras(scope.row)">
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
                <div class="pendant-list" v-if="scope.row.pendant">
                  <img
                    v-if="parsePendant(scope.row.pendant)?.image"
                    :src="parsePendant(scope.row.pendant).image"
                    :alt="parsePendant(scope.row.pendant)?.name"
                    class="pendant-img"
                    @error="(e) => e.target.style.display = 'none'"
                  />
                </div>
                <div class="rename-text" v-if="scope.row.rename">
                  <span class="rename-value">{{ scope.row.rename }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="weapon_type" label="类型" min-width="100" />
        <el-table-column prop="platform" label="平台" width="120">
          <template #default="scope">
            <el-tag :type="getPlatformTagType(scope.row.platform)" size="small">
              {{ getPlatformLabel(scope.row.platform) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="weapon_float" label="磨损值" min-width="220">
          <template #default="scope">
            <div v-if="scope.row.weapon_float">
              <div style="font-family: monospace; font-size: 0.85rem; margin-bottom: 4px;">
                {{ scope.row.weapon_float }}
              </div>
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
        <el-table-column prop="sale_price" label="售价" width="150">
          <template #default="scope">
            <span style="color: #fff; font-weight: bold;">¥{{ parseFloat(scope.row.sale_price).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="buy_price" label="购入价" width="150">
          <template #default="scope">
            <span v-if="scope.row.buy_price" style="color: #fff;">¥{{ parseFloat(scope.row.buy_price).toFixed(2) }}</span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="预期收益" width="150">
          <template #default="scope">
            <span 
              v-if="scope.row.buy_price"
              :class="getPriceDiffClass(scope.row.sale_price, scope.row.buy_price)"
              style="font-weight: bold;"
            >
              {{ (parseFloat(scope.row.sale_price) - parseFloat(scope.row.buy_price)) >= 0 ? '+' : '' }}¥{{ Math.abs(parseFloat(scope.row.sale_price) - parseFloat(scope.row.buy_price)).toFixed(2) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="on_sale_time" label="上架时间" width="180">
          <template #default="scope">
            <span v-if="scope.row.on_sale_time" style="color: #9E9E9E;">
              {{ scope.row.on_sale_time }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button size="small" type="success" @click.stop="handleUpdatePrice(scope.row)">
              改价
            </el-button>
            <el-button size="small" type="primary" @click.stop="handleRemoveFromSale(scope.row)">
              下架
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-footer">
        <span>共 {{ currentDisplayData.length }} 条数据</span>
      </div>
    </div>

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
                <el-button type="primary" @click="handleRemoveFromSale(previewItem)">下架商品</el-button>
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

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { API_CONFIG, apiUrls } from '@/config/api.js'

export default {
  name: 'OnSale',
  setup() {
    const loading = ref(false)
    const updating = ref(false)
    const onSaleData = ref([])
    const accountList = ref([])
    const selectedAccount = ref('')
    const searchText = ref('')
    const weaponTypeFilter = ref('')
    const floatRangeFilter = ref('')
    const displayMode = ref('card')
    
    // 交易类型
    const selectedTradeType = ref('sale') // 默认选择"出售"
    const tradeTypes = ref([
      { value: 'sale', label: '出售', icon: '💰' },
      { value: 'lease', label: '租赁', icon: '🔄' },
      { value: 'sublease', label: '转租', icon: '🔁' },
      { value: 'presale', label: '预售', icon: '⏰' },
      { value: 'transfer', label: '过户', icon: '📝' },
      { value: 'private_sale', label: '私密出售', icon: '🔒' },
      { value: 'private_rent', label: '私募出租', icon: '🔐' }
    ])
    
    // 图片404缓存
    const image404Cache = ref(new Set())
    
    // 多选模式相关
    const isMultiSelectMode = ref(true) // 默认开启多选模式
    const selectedItems = ref([])
    
    // 弹窗相关
    const updatePriceDialogVisible = ref(false)
    const previewVisible = ref(false)
    const selectedItem = ref(null)
    const previewItem = ref(null)
    const updatePriceForm = ref({
      newPrice: ''
    })

    // 统计数据
    const onSaleStats = computed(() => {
      const totalCount = onSaleData.value.length
      const totalPrice = onSaleData.value.reduce((sum, item) => sum + parseFloat(item.sale_price || 0), 0)
      const avgPrice = totalCount > 0 ? (totalPrice / totalCount) : 0
      const expectedProfit = onSaleData.value.reduce((sum, item) => {
        if (item.buy_price) {
          return sum + (parseFloat(item.sale_price) - parseFloat(item.buy_price))
        }
        return sum
      }, 0)

      return {
        totalCount,
        totalPrice: totalPrice.toFixed(2),
        avgPrice: avgPrice.toFixed(2),
        expectedProfit: expectedProfit.toFixed(2)
      }
    })

    // 当前显示数据
    const currentDisplayData = computed(() => {
      let filtered = onSaleData.value

      // 搜索过滤
      if (searchText.value) {
        const search = searchText.value.toLowerCase()
        filtered = filtered.filter(item => 
          item.item_name?.toLowerCase().includes(search) ||
          item.steam_hash_name?.toLowerCase().includes(search)
        )
      }

      // 只显示悠悠有品平台的数据
      filtered = filtered.filter(item => item.platform === 'yyyp')

      // 交易类型过滤
      if (selectedTradeType.value) {
        filtered = filtered.filter(item => {
          // 如果数据库中有 trade_type 字段，使用它；否则默认为 'sale'
          const itemTradeType = item.trade_type || 'sale'
          return itemTradeType === selectedTradeType.value
        })
      }

      // 账号过滤
      if (selectedAccount.value) {
        filtered = filtered.filter(item => item.account_id === selectedAccount.value)
      }

      // 武器类型过滤
      if (weaponTypeFilter.value) {
        filtered = filtered.filter(item => item.weapon_type === weaponTypeFilter.value)
      }

      // 磨损等级过滤
      if (floatRangeFilter.value) {
        filtered = filtered.filter(item => item.float_range === floatRangeFilter.value)
      }

      return filtered
    })

    // 获取每个交易类型的数量
    const getTradeTypeCount = (tradeType) => {
      return onSaleData.value.filter(item => {
        const itemTradeType = item.trade_type || 'sale'
        return itemTradeType === tradeType && item.platform === 'yyyp'
      }).length
    }

    // 处理交易类型切换
    const handleTradeTypeChange = (tradeType) => {
      selectedTradeType.value = tradeType
      // 切换交易类型时重新加载数据
      loadOnSaleData()
    }

    // 加载在售数据
    const loadOnSaleData = async () => {
      if (!selectedAccount.value) {
        ElMessage.warning('请选择账号')
        return
      }
      
      loading.value = true
      try {
        const response = await axios.post(apiUrls.getOnSaleItems(), {
          platform: 'yyyp',
          account_id: selectedAccount.value,
          trade_type: selectedTradeType.value  // 添加交易类型参数
        })
        if (response.data && response.data.success) {
          onSaleData.value = response.data.data || []
          ElMessage.success('加载成功')
        } else {
          ElMessage.error(response.data?.message || '加载失败')
        }
      } catch (error) {
        console.error('加载在售数据失败:', error)
        ElMessage.error('加载失败: ' + error.message)
      } finally {
        loading.value = false
      }
    }

    // 加载账号列表
    const loadAccountList = async () => {
      try {
        const response = await axios.get(apiUrls.getYYYPAccounts())
        if (response.data && response.data.success) {
          accountList.value = response.data.data || []
          if (accountList.value.length > 0) {
            selectedAccount.value = accountList.value[0].id
            // 默认查询第一个账号的数据
            loadOnSaleData()
          } else {
            ElMessage.warning('没有找到悠悠有品账号')
          }
        }
      } catch (error) {
        console.error('加载账号列表失败:', error)
        ElMessage.error('加载账号列表失败: ' + error.message)
      }
    }

    // 处理账号变化
    const handleAccountChange = () => {
      loadOnSaleData()
    }

    // 重置筛选
    const handleReset = () => {
      searchText.value = ''
      weaponTypeFilter.value = ''
      floatRangeFilter.value = ''
      loadOnSaleData()
    }

    // 打开改价弹窗
    const handleUpdatePrice = (item) => {
      selectedItem.value = item
      updatePriceForm.value.newPrice = item.sale_price
      updatePriceDialogVisible.value = true
      previewVisible.value = false
    }

    // 校验价格输入
    const validatePriceInput = () => {
      let value = updatePriceForm.value.newPrice
      
      if (!value) {
        return
      }
      
      // 转换为字符串
      value = String(value)
      
      // 移除非数字和小数点的字符
      value = value.replace(/[^\d.]/g, '')
      
      // 不允许以多个0开头（除非是0.xx）
      if (value.length > 1 && value[0] === '0' && value[1] !== '.') {
        value = value.replace(/^0+/, '0')
      }
      
      // 只保留第一个小数点
      const parts = value.split('.')
      if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('')
      }
      
      // 限制小数点后最多两位
      if (parts.length === 2 && parts[1].length > 2) {
        value = parts[0] + '.' + parts[1].substring(0, 2)
      }
      
      updatePriceForm.value.newPrice = value
    }

    // 确认改价
    const confirmUpdatePrice = async () => {
      const price = updatePriceForm.value.newPrice
      
      // 验证价格
      if (!price || price.trim() === '') {
        ElMessage.warning('请输入售价')
        return
      }
      
      const priceFloat = parseFloat(price)
      if (isNaN(priceFloat) || priceFloat <= 0) {
        ElMessage.warning('请输入有效的价格（大于0）')
        return
      }
      
      // 验证小数位数
      const parts = price.split('.')
      if (parts.length === 2 && parts[1].length > 2) {
        ElMessage.warning('价格最多保留两位小数')
        return
      }

      updating.value = true
      try {
        const response = await axios.post(apiUrls.updateSalePrice(), {
          id: selectedItem.value.id,
          new_price: price,  // 直接传递原始字符串
          account_id: selectedAccount.value
        })

        if (response.data && response.data.success) {
          ElMessage.success('改价成功')
          updatePriceDialogVisible.value = false
          loadOnSaleData()
        } else {
          ElMessage.error(response.data?.message || '改价失败')
        }
      } catch (error) {
        console.error('改价失败:', error)
        ElMessage.error('改价失败: ' + error.message)
      } finally {
        updating.value = false
      }
    }

    // 下架商品
    const handleRemoveFromSale = async (item) => {
      try {
        await ElMessageBox.confirm(
          `确定要下架 "${getCardTitle(item)}" 吗？`,
          '确认下架',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        loading.value = true
        const response = await axios.post(apiUrls.removeFromSale(), {
          id: item.id,
          account_id: selectedAccount.value
        })

        if (response.data && response.data.success) {
          ElMessage.success('下架成功')
          previewVisible.value = false
          loadOnSaleData()
        } else {
          ElMessage.error(response.data?.message || '下架失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('下架失败:', error)
          ElMessage.error('下架失败: ' + error.message)
        }
      } finally {
        loading.value = false
      }
    }

    // 打开预览
    const openPreview = (item) => {
      previewItem.value = item
      previewVisible.value = true
    }

    // 工具函数
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

    const handleImageError = (e, steamHashName) => {
      // 将失败的steam_hash_name添加到404缓存中
      if (steamHashName) {
        image404Cache.value.add(steamHashName)
      }
      
      // 移除错误监听器，防止重复触发
      e.target.onerror = null
      
      // 隐藏图片，不设置data URI，避免将图片数据加载到内存
      e.target.style.display = 'none'
    }

    const getCardTitle = (item) => {
      if (!item) return ''
      return item.item_name || item.steam_hash_name || '未知物品'
    }

    const getItemTitle = (item) => {
      return getCardTitle(item)
    }

    const hasExtras = (item) => {
      return item.sticker || item.pendant || item.rename
    }

    const parseStickers = (stickerData) => {
      if (!stickerData) return []
      try {
        if (typeof stickerData === 'string') {
          return JSON.parse(stickerData)
        }
        return Array.isArray(stickerData) ? stickerData : []
      } catch (e) {
        return []
      }
    }

    const parsePendant = (pendantData) => {
      if (!pendantData) return null
      try {
        if (typeof pendantData === 'string') {
          return JSON.parse(pendantData)
        }
        return pendantData
      } catch (e) {
        return null
      }
    }

    const getPlatformLabel = (platform) => {
      const labels = {
        'yyyp': '悠悠有品',
        'buff': 'BUFF',
        'csfloat': 'CSFloat'
      }
      return labels[platform] || platform
    }

    const getPlatformTagType = (platform) => {
      const types = {
        'yyyp': 'success',
        'buff': 'warning',
        'csfloat': 'info'
      }
      return types[platform] || 'default'
    }

    // 多选模式相关函数
    const toggleMultiSelectMode = () => {
      isMultiSelectMode.value = !isMultiSelectMode.value
      if (!isMultiSelectMode.value) {
        // 退出多选模式时清空选择
        selectedItems.value = []
      }
    }

    const isItemSelected = (itemId) => {
      return selectedItems.value.some(item => item.id === itemId)
    }

    const toggleItemSelection = (item) => {
      const index = selectedItems.value.findIndex(i => i.id === item.id)
      if (index > -1) {
        selectedItems.value.splice(index, 1)
      } else {
        selectedItems.value.push(item)
      }
    }

    const handleCardClick = (item) => {
      if (isMultiSelectMode.value) {
        toggleItemSelection(item)
      } else {
        openPreview(item)
      }
    }

    const formatOnSaleTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      const now = new Date()
      const diff = now - date
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      
      if (days === 0) return '今天上架'
      if (days === 1) return '昨天上架'
      if (days < 7) return `${days}天前`
      return date.toLocaleDateString('zh-CN')
    }

    // 获取价格差异样式类
    const getPriceDiffClass = (salePrice, buyPrice) => {
      if (!salePrice || !buyPrice) return ''
      const diff = parseFloat(salePrice) - parseFloat(buyPrice)
      if (diff === 0) return 'price-equal'
      return diff > 0 ? 'price-profit' : 'price-loss'
    }

    onMounted(() => {
      loadAccountList()
    })

    return {
      loading,
      updating,
      onSaleData,
      accountList,
      selectedAccount,
      searchText,
      weaponTypeFilter,
      floatRangeFilter,
      displayMode,
      selectedTradeType,
      tradeTypes,
      isMultiSelectMode,
      selectedItems,
      updatePriceDialogVisible,
      previewVisible,
      selectedItem,
      previewItem,
      updatePriceForm,
      onSaleStats,
      currentDisplayData,
      loadOnSaleData,
      loadAccountList,
      handleAccountChange,
      handleReset,
      handleUpdatePrice,
      validatePriceInput,
      confirmUpdatePrice,
      handleRemoveFromSale,
      openPreview,
      getWeaponImage,
      handleImageError,
      getCardTitle,
      getItemTitle,
      hasExtras,
      parseStickers,
      parsePendant,
      getPlatformLabel,
      getPlatformTagType,
      formatOnSaleTime,
      toggleMultiSelectMode,
      isItemSelected,
      toggleItemSelection,
      handleCardClick,
      getPriceDiffClass,
      getTradeTypeCount,
      handleTradeTypeChange
    }
  }
}
</script>

<style scoped>
/* 交易类型选择栏样式 */
.trade-type-bar {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary);
  border-radius: 8px;
  overflow-x: auto;
}

.trade-type-tabs {
  display: flex;
  gap: 0.5rem;
  min-width: max-content;
}

.trade-type-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: var(--bg-tertiary);
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  position: relative;
  user-select: none;
}

.trade-type-tab:hover {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.3);
  transform: translateY(-2px);
}

.trade-type-tab.active {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2) 0%, rgba(64, 158, 255, 0.1) 100%);
  border-color: var(--el-color-primary);
  box-shadow: 0 0 12px rgba(64, 158, 255, 0.3);
}

.trade-type-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.trade-type-label {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-primary);
}

.trade-type-tab.active .trade-type-label {
  color: var(--el-color-primary);
  font-weight: 600;
}

.trade-type-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: bold;
  color: var(--text-secondary);
}

.trade-type-tab.active .trade-type-count {
  background: var(--el-color-primary);
  color: #fff;
}

/* 筛选器样式 */
.filters {
  margin-bottom: 1rem;
  padding: 1rem;
}

.search-input {
  width: 300px;
}

.account-select {
  width: 250px;
}

.platform-select,
.type-select,
.wear-select {
  width: 150px;
}

/* 统计信息样式 */
.inventory-stats {
  margin-bottom: 1rem;
}

.grid {
  display: grid;
  gap: 1rem;
}

.grid-4 {
  grid-template-columns: repeat(4, 1fr);
}

.card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 1rem;
}

.card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: normal;
}

.stat-number {
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text-primary);
}

/* 卡片网格样式 */
.card-container {
  margin-top: 1rem;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
  padding: 1rem 0;
}

.inventory-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  overflow: visible;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  height: 340px;
}

.inventory-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.card-image {
  position: relative;
  width: 100%;
  height: 150px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-image img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.image-placeholder {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* 贴纸和挂件覆盖层 */
.sticker-overlay {
  position: absolute;
  bottom: 8px;
  left: 8px;
  display: flex;
  gap: 4px;
  z-index: 2;
}

.sticker-item-overlay {
  width: 32px;
  height: 32px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.sticker-img-overlay {
  width: 28px;
  height: 28px;
  object-fit: contain;
}

.sticker-placeholder-overlay {
  color: #999;
  font-size: 12px;
}

.pendant-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
}

.pendant-item-overlay {
  width: 36px;
  height: 36px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.pendant-img-overlay {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.pendant-placeholder-overlay {
  font-size: 18px;
}

/* 平台标签 */
.platform-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 2;
}

/* 卡片内容 */
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

/* 磨损值显示条 */
.float-bar-container {
  margin-top: 0.3rem;
  padding: 0;
  margin-bottom: 0;
}

.float-bar {
  position: relative;
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
  display: flex;
}

.float-segment {
  flex: 1;
  height: 100%;
}

.float-segment.fn {
  background: #4CAF50;
  flex: 0.07;
}

.float-segment.mw {
  background: #8BC34A;
  flex: 0.08;
}

.float-segment.ft {
  background: #FFC107;
  flex: 0.23;
}

.float-segment.ww {
  background: #FF9800;
  flex: 0.07;
}

.float-segment.bs {
  background: #F44336;
  flex: 0.55;
}

.float-pointer {
  position: absolute;
  top: -2px;
  width: 2px;
  height: 10px;
  background: #fff;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.5);
  transform: translateX(-50%);
  z-index: 1;
}

.float-value {
  text-align: left;
  font-size: 0.75rem;
  color: #ccc;
  font-family: monospace;
  margin-top: 0.2rem;
  margin-bottom: 0;
  font-weight: 500;
}

/* 价格显示 */
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

.price-profit {
  color: #f56c6c;
}

.price-loss {
  color: #4CAF50;
}

.price-equal {
  color: #fff;
}

.sale-price {
  color: #4CAF50;
}

/* 卡片底部 */
.card-footer {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.rename-tag {
  max-width: 100%;
}

.tag-icon {
  margin-right: 0.25rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.card-actions .el-button {
  flex: 1;
}

/* 列表样式 */
.table-container {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 1rem;
}

.weapon-image-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
}

.weapon-img {
  max-width: 120px;
  max-height: 80px;
  object-fit: contain;
}

.no-image {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.item-name-cell {
  padding: 0.5rem 0;
}

.item-title {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.item-extras {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.sticker-list,
.pendant-list {
  display: flex;
  gap: 0.25rem;
}

.sticker-item {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sticker-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.sticker-placeholder {
  color: #999;
  font-size: 10px;
}

.pendant-img {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.rename-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.rename-value {
  font-style: italic;
}

.table-footer {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* 改价弹窗样式 */
.update-price-content {
  padding: 1rem 0;
}

.update-price-dialog :deep(.el-dialog__header) {
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 1.5rem;
}

.update-price-dialog :deep(.el-dialog__title) {
  color: #fff;
  font-weight: bold;
  font-size: 1.1rem;
}

.update-price-dialog :deep(.el-dialog__body) {
  background: var(--bg-secondary);
  padding: 1.5rem;
}

.update-price-dialog :deep(.el-dialog__footer) {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: 1rem 1.5rem;
}

.item-preview {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.preview-thumb {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

.item-info {
  flex: 1;
}

.item-name {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.current-price {
  font-size: 0.9rem;
  color: var(--text-secondary);
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

.preview-info-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preview-float-section {
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.preview-float-bar-container {
  margin-bottom: 0.75rem;
}

.preview-float-value {
  font-family: monospace;
  font-size: 1.1rem;
  color: var(--text-primary);
  font-weight: 500;
}

.preview-prices {
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.preview-price-row {
  display: flex;
  gap: 2rem;
}

.preview-price-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.preview-price-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.preview-price-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.preview-action-buttons {
  display: flex;
  gap: 0.75rem;
}

.preview-action-buttons .el-button {
  flex: 1;
}

.preview-rename {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-rename-icon {
  font-size: 1.5rem;
}

.preview-rename-text {
  font-size: 1rem;
  color: #fff;
  font-weight: 500;
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
  color: #999;
  font-size: 1.2rem;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }

  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }

  .preview-dialog {
    width: 95% !important;
  }

  .preview-main-layout {
    flex-direction: column;
  }
  
  .inventory-card {
    height: 320px;
  }
}

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
</style>
