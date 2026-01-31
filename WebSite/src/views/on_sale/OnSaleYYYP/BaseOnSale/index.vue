<template>
  <div>
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
          @keyup.enter="handleSearch"
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
        <el-button type="primary" @click="handleSearch" :loading="loading">
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

    <!-- 统计信息插槽 -->
    <slot name="stats"></slot>

    <!-- 内容区域插槽 -->
    <slot name="content"></slot>
  </div>
</template>

<script>
import { useOnSaleCommon } from './useOnSaleCommon.js'

export default {
  name: 'BaseOnSale',
  props: {
    accountList: {
      type: Array,
      default: () => []
    },
    selectedAccount: {
      type: [String, Number],
      default: ''
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:selectedAccount', 'account-change', 'search', 'reset'],
  setup(props, { emit }) {
    const {
      displayMode,
      searchText,
      weaponTypeFilter,
      floatRangeFilter,
      isMultiSelectMode,
      toggleMultiSelectMode,
      handleReset: resetFilters
    } = useOnSaleCommon()

    const handleAccountChange = () => {
      emit('account-change')
    }

    const handleSearch = () => {
      emit('search', {
        searchText: searchText.value,
        weaponTypeFilter: weaponTypeFilter.value,
        floatRangeFilter: floatRangeFilter.value
      })
    }

    const handleReset = () => {
      resetFilters()
      emit('reset')
    }

    return {
      displayMode,
      searchText,
      weaponTypeFilter,
      floatRangeFilter,
      isMultiSelectMode,
      toggleMultiSelectMode,
      handleAccountChange,
      handleSearch,
      handleReset
    }
  }
}
</script>
