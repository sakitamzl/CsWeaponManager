<template>
  <div>
    <!-- 筛选器 -->
    <div class="filters card">
      <div class="flex flex-wrap gap-4 items-center">
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
          <p class="stat-number" :style="{ color: onSaleStats.expectedProfit >= 0 ? '#4CAF50' : '#f56c6c' }">
            {{ onSaleStats.expectedProfit >= 0 ? '+' : '' }}¥{{ onSaleStats.expectedProfit }}
          </p>
        </div>
      </div>
    </div>

    <!-- 卡片显示 -->
    <div class="card-container" v-if="displayMode === 'card'">
      <div v-loading="loading" class="card-grid">
        <div
          v-for="item in currentDisplayData"
          :key="item.id"
          class="inventory-card"
          @click="openPreview(item)"
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
            <!-- 平台标签 -->
            <div class="platform-badge">
              <el-tag :type="getPlatformTagType(item.platform)" size="small">
                {{ getPlatformLabel(item.platform) }}
              </el-tag>
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
                    :style="{ color: (parseFloat(item.sale_price) - parseFloat(item.buy_price)) >= 0 ? '#4CAF50' : '#f56c6c' }"
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
                <el-button size="small" type="warning" @click.stop="handleUpdatePrice(item)">
                  改价
                </el-button>
                <el-button size="small" type="danger" @click.stop="handleRemoveFromSale(item)">
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
              :style="{ 
                color: (parseFloat(scope.row.sale_price) - parseFloat(scope.row.buy_price)) >= 0 ? '#4CAF50' : '#f56c6c',
                fontWeight: 'bold'
              }"
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
            <el-button size="small" type="warning" @click.stop="handleUpdatePrice(scope.row)">
              改价
            </el-button>
            <el-button size="small" type="danger" @click.stop="handleRemoveFromSale(scope.row)">
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
              placeholder="请输入新的售价"
              type="number"
              step="0.01"
            >
              <template #prepend>¥</template>
            </el-input>
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
                      :style="{ color: (parseFloat(previewItem.sale_price) - parseFloat(previewItem.buy_price)) >= 0 ? '#4CAF50' : '#f56c6c' }"
                    >
                      {{ (parseFloat(previewItem.sale_price) - parseFloat(previewItem.buy_price)) >= 0 ? '+' : '' }}¥{{ Math.abs(parseFloat(previewItem.sale_price) - parseFloat(previewItem.buy_price)).toFixed(2) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="preview-action-buttons">
                <el-button type="warning" @click="handleUpdatePrice(previewItem)">修改售价</el-button>
                <el-button type="danger" @click="handleRemoveFromSale(previewItem)">下架商品</el-button>
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
    const searchText = ref('')
    const platformFilter = ref('')
    const weaponTypeFilter = ref('')
    const floatRangeFilter = ref('')
    const displayMode = ref('card')
    
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

      // 平台过滤
      if (platformFilter.value) {
        filtered = filtered.filter(item => item.platform === platformFilter.value)
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

    // 加载在售数据
    const loadOnSaleData = async () => {
      loading.value = true
      try {
        const response = await axios.get(apiUrls.getOnSaleItems())
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

    // 重置筛选
    const handleReset = () => {
      searchText.value = ''
      platformFilter.value = ''
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

    // 确认改价
    const confirmUpdatePrice = async () => {
      if (!updatePriceForm.value.newPrice || parseFloat(updatePriceForm.value.newPrice) <= 0) {
        ElMessage.warning('请输入有效的价格')
        return
      }

      updating.value = true
      try {
        const response = await axios.post(apiUrls.updateSalePrice(), {
          id: selectedItem.value.id,
          new_price: updatePriceForm.value.newPrice
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
          id: item.id
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
      if (!steamHashName) return null
      return `${API_CONFIG.baseURL}/weapon_imgs/${encodeURIComponent(steamHashName)}.png`
    }

    const handleImageError = (e, steamHashName) => {
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

    onMounted(() => {
      loadOnSaleData()
    })

    return {
      loading,
      updating,
      onSaleData,
      searchText,
      platformFilter,
      weaponTypeFilter,
      floatRangeFilter,
      displayMode,
      updatePriceDialogVisible,
      previewVisible,
      selectedItem,
      previewItem,
      updatePriceForm,
      onSaleStats,
      currentDisplayData,
      loadOnSaleData,
      handleReset,
      handleUpdatePrice,
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
      formatOnSaleTime
    }
  }
}
</script>

<style scoped>
/* 筛选器样式 */
.filters {
  margin-bottom: 1rem;
  padding: 1rem;
}

.search-input {
  width: 300px;
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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  padding: 1rem 0;
}

.inventory-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid var(--border-color);
}

.inventory-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.card-image {
  position: relative;
  width: 100%;
  height: 180px;
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
  padding: 1rem;
}

.card-title {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-info {
  margin-bottom: 0.75rem;
}

/* 磨损值显示条 */
.float-bar-container {
  margin-bottom: 0.5rem;
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
  font-family: monospace;
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

/* 价格显示 */
.card-prices {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.price-group {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.price-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.price-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.sale-price {
  color: #4CAF50;
  font-size: 1rem;
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
.preview-dialog {
  --el-dialog-bg-color: var(--bg-secondary);
}

.preview-content {
  padding: 1rem;
}

.preview-main-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.preview-left-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.preview-image-section {
  width: 100%;
  height: 300px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.preview-image-placeholder {
  color: var(--text-secondary);
  font-size: 1.2rem;
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

.preview-right-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preview-rename {
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-rename-icon {
  font-size: 1.5rem;
}

.preview-rename-text {
  font-size: 1rem;
  color: var(--text-primary);
  font-weight: 500;
}

.preview-sticker-list-section,
.preview-pendant-section {
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.preview-sticker-list,
.preview-pendant-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.preview-sticker-list-item,
.preview-pendant-list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.preview-sticker-list-img-wrapper,
.preview-pendant-list-img-wrapper {
  width: 48px;
  height: 48px;
  background: var(--bg-secondary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.preview-sticker-list-img,
.preview-pendant-list-img {
  max-width: 40px;
  max-height: 40px;
  object-fit: contain;
}

.preview-sticker-list-placeholder,
.preview-pendant-list-placeholder {
  color: var(--text-secondary);
  font-size: 1.2rem;
}

.preview-sticker-list-name,
.preview-pendant-list-name {
  font-size: 0.9rem;
  color: var(--text-primary);
  flex: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }

  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }

  .preview-main-layout {
    grid-template-columns: 1fr;
  }
}
</style>
