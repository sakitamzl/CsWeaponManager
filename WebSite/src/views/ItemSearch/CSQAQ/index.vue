<template>
  <div v-if="visible" class="card chart-card">
    <div class="chart-row">
      <div class="chart-left">
        <!-- 红框区域已隐藏：标题、饰品名、磨损条件按钮 -->
        <div class="good-detail-panel" v-loading="goodDetailLoading" element-loading-text="加载详情...">
          <template v-if="goodDetail?.data?.goods_info">
            <div class="good-detail-overview">
              <div class="overview-card overview-card--today" v-if="hasTodayStat(goodDetail.data.goods_info)">
                <span class="overview-card-label">今日{{ getTodayDir(goodDetail.data.goods_info) }}</span>
                <span class="overview-card-value">{{ formatTodayOverviewValue(goodDetail.data.goods_info) }}</span>
              </div>
              <div class="overview-card overview-card--week" v-if="hasWeekStat(goodDetail.data.goods_info)">
                <span class="overview-card-label">本周{{ getWeekDir(goodDetail.data.goods_info) }}</span>
                <span class="overview-card-value">{{ formatWeekOverviewValue(goodDetail.data.goods_info) }}</span>
              </div>
            </div>

            <div class="good-detail-platforms">
              <div class="platform-block" v-if="hasBuffData(goodDetail.data.goods_info)">
                <div class="platform-title">BUFF <span class="platform-arrow">→</span></div>
                <div class="platform-grid">
                  <div class="platform-col">
                    <div class="platform-row"><span class="label">在售价:</span><span class="value">¥{{ formatPrice(goodDetail.data.goods_info.buff_sell_price) }}</span></div>
                    <div class="platform-row"><span class="label">求购价:</span><span class="value">¥{{ formatPrice(goodDetail.data.goods_info.buff_buy_price) }}</span></div>
                  </div>
                  <div class="platform-col">
                    <div class="platform-row"><span class="label">在售数:</span><span class="value">{{ goodDetail.data.goods_info.buff_sell_num ?? '-' }} 件</span></div>
                    <div class="platform-row"><span class="label">求购数:</span><span class="value">{{ goodDetail.data.goods_info.buff_buy_num ?? '-' }} 件</span></div>
                  </div>
                </div>
              </div>
              <div class="platform-block" v-if="hasYyypData(goodDetail.data.goods_info)">
                <div class="platform-title">悠悠有品 <el-tag v-if="isYyypPriceLow(goodDetail.data.goods_info)" type="success" size="small" class="tag-low">低</el-tag><span class="platform-arrow">→</span></div>
                <div class="platform-grid">
                  <div class="platform-col">
                    <div class="platform-row"><span class="label">在售价:</span><span class="value">¥{{ formatPrice(goodDetail.data.goods_info.yyyp_sell_price) }}</span></div>
                    <div class="platform-row"><span class="label">求购价:</span><span class="value">¥{{ formatPrice(goodDetail.data.goods_info.yyyp_buy_price) }}</span></div>
                  </div>
                  <div class="platform-col">
                    <div class="platform-row"><span class="label">在售数:</span><span class="value">{{ goodDetail.data.goods_info.yyyp_sell_num ?? '-' }} 件</span></div>
                    <div class="platform-row"><span class="label">求购数:</span><span class="value">{{ goodDetail.data.goods_info.yyyp_buy_num ?? '-' }} 件</span></div>
                  </div>
                </div>
              </div>
              <div class="platform-block" v-if="hasSteamData(goodDetail.data.goods_info)">
                <div class="platform-title">Steam <span class="platform-arrow">→</span></div>
                <div class="platform-grid">
                  <div class="platform-col">
                    <div class="platform-row"><span class="label">在售价:</span><span class="value">¥{{ formatPrice(goodDetail.data.goods_info.steam_sell_price) }}</span></div>
                    <div class="platform-row"><span class="label">求购价:</span><span class="value">¥{{ formatPrice(goodDetail.data.goods_info.steam_buy_price) }}</span></div>
                  </div>
                  <div class="platform-col">
                    <div class="platform-row"><span class="label">在售数:</span><span class="value">{{ goodDetail.data.goods_info.steam_sell_num ?? '-' }} 件</span></div>
                    <div class="platform-row"><span class="label">求购数:</span><span class="value">{{ goodDetail.data.goods_info.steam_buy_num ?? '-' }} 件</span></div>
                  </div>
                </div>
              </div>
              <div class="platform-block" v-if="hasR8Data(goodDetail.data.goods_info)">
                <div class="platform-title">R8GAME <span class="platform-arrow">→</span></div>
                <div class="platform-grid">
                  <div class="platform-col">
                    <div class="platform-row"><span class="label">在售价:</span><span class="value">¥{{ formatPrice(goodDetail.data.goods_info.r8_sell_price) }}</span></div>
                  </div>
                  <div class="platform-col">
                    <div class="platform-row"><span class="label">在售数:</span><span class="value">{{ goodDetail.data.goods_info.r8_sell_num ?? '-' }} 件</span></div>
                  </div>
                </div>
              </div>
            </div>

            <div class="good-detail-section" v-if="hasYyypLeaseData(goodDetail.data.goods_info)">
              <div class="section-title">悠悠有品·租赁</div>
              <div class="section-two-col">
                <div class="section-col">
                  <div class="good-detail-row"><span class="label">短租价格:</span><span class="value">¥{{ formatPrice(goodDetail.data.goods_info.yyyp_lease_price) }}/天</span></div>
                  <div class="good-detail-row"><span class="label">长租价格:</span><span class="value">¥{{ formatPrice(goodDetail.data.goods_info.yyyp_long_lease_price) }}/天</span></div>
                  <div class="good-detail-row"><span class="label">过户底价:</span><span class="value">¥{{ formatPrice(goodDetail.data.goods_info.yyyp_transfer_price) }}</span></div>
                </div>
                <div class="section-col">
                  <div class="good-detail-row" v-if="goodDetail.data.goods_info.yyyp_lease_annual != null"><span class="label">短租年收益:</span><span class="value">{{ formatRate(goodDetail.data.goods_info.yyyp_lease_annual) }}%</span></div>
                  <div class="good-detail-row" v-if="goodDetail.data.goods_info.yyyp_long_lease_annual != null"><span class="label">长租年收益:</span><span class="value">{{ formatRate(goodDetail.data.goods_info.yyyp_long_lease_annual) }}%</span></div>
                  <div class="good-detail-row"><span class="label">在租数量:</span><span class="value">{{ goodDetail.data.goods_info.yyyp_lease_num ?? '-' }} 件</span></div>
                </div>
              </div>
            </div>

            <div class="good-detail-section" v-if="hasSteamConversionData(goodDetail.data.goods_info)">
              <div class="section-title">Steam·挂刀套现</div>
              <div class="section-two-col">
                <div class="section-col">
                  <div class="good-detail-row" v-if="goodDetail.data.goods_info.steam_buff_buy_conversion != null"><span class="label">Steam求购挂刀:</span><span class="value">{{ formatDecimal(goodDetail.data.goods_info.steam_buff_buy_conversion) }}</span></div>
                  <div class="good-detail-row" v-if="goodDetail.data.goods_info.steam_buff_sell_conversion != null"><span class="label">Steam在售挂刀:</span><span class="value">{{ formatDecimal(goodDetail.data.goods_info.steam_buff_sell_conversion) }}</span></div>
                  <div class="good-detail-row" v-if="goodDetail.data.goods_info.turnover_number != null"><span class="label">Steam日成交量:</span><span class="value">{{ goodDetail.data.goods_info.turnover_number }} 件</span></div>
                </div>
                <div class="section-col">
                  <div class="good-detail-row" v-if="goodDetail.data.goods_info.buff_steam_buy_conversion != null"><span class="label">BUFF求购套现:</span><span class="value">{{ formatDecimal(goodDetail.data.goods_info.buff_steam_buy_conversion) }}</span></div>
                  <div class="good-detail-row" v-if="goodDetail.data.goods_info.buff_steam_sell_conversion != null"><span class="label">BUFF售价套现:</span><span class="value">{{ formatDecimal(goodDetail.data.goods_info.buff_steam_sell_conversion) }}</span></div>
                  <div class="good-detail-row" v-if="goodDetail.data.goods_info.turnover_avg_price != null"><span class="label">日成交均价:</span><span class="value">¥{{ formatPrice(goodDetail.data.goods_info.turnover_avg_price) }}</span></div>
                </div>
              </div>
            </div>

            <div class="good-detail-row time-row" v-if="goodDetail.data.goods_info.updated_at">
              <span class="label">更新时间</span>
              <span class="value time">{{ formatUpdatedAt(goodDetail.data.goods_info.updated_at) }}</span>
            </div>
          </template>
          <div v-else-if="!goodDetailLoading" class="good-detail-empty">暂无饰品详情</div>
        </div>
      </div>
      <div class="chart-right">
        <div class="chart-controls">
          <el-radio-group v-model="chartViewMode" size="small" class="chart-view-toggle">
            <el-radio-button
              v-for="mode in CHART_VIEW_MODES"
              :key="mode.value"
              :label="mode.value"
            >
              {{ mode.label }}
            </el-radio-button>
          </el-radio-group>
          <el-select v-model="chartKey" placeholder="数据类型" size="small" class="chart-select">
            <el-option v-for="opt in CHART_KEY_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-select v-model="chartPlatform" placeholder="平台" size="small" class="chart-select">
            <el-option v-for="opt in CHART_PLATFORM_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-select v-model="chartPeriod" placeholder="周期" size="small" class="chart-select">
            <el-option v-for="opt in CHART_PERIOD_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-select v-if="showChartStyleSelect" v-model="chartStyle" placeholder="款式" size="small" class="chart-select">
            <el-option v-for="opt in CHART_STYLE_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-button type="primary" size="small" :loading="chartLoading" @click="fetchChartData">刷新</el-button>
        </div>
        <div class="chart-body" v-loading="chartLoading" element-loading-text="加载图表...">
          <div ref="csqaqChartRef" class="csqaq-chart-dom" />
          <div v-if="!chartLoading && !chartData?.timestamp?.length" class="chart-empty">暂无数据</div>
        </div>
      </div>
    </div>
    <el-dialog
      v-model="statisticDialogVisible"
      title="存世量走势"
      width="70%"
      destroy-on-close
    >
      <div class="statistic-chart-body" v-loading="statisticLoading" element-loading-text="加载存世量...">
        <div ref="statisticChartRef" class="csqaq-chart-dom statistic-chart-dom" />
        <div v-if="!statisticLoading && !statisticData?.length" class="chart-empty">暂无存世量数据</div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { computed, toRef, watch } from 'vue'
import { useCSQAQ } from './useCSQAQ.js'

export default {
  name: 'ItemSearchCSQAQ',
  props: {
    chartWeapon: { type: Object, default: null },
    showYYYPList: { type: Boolean, default: false },
    showBuffList: { type: Boolean, default: false },
    statisticDialogTrigger: { type: Number, default: 0 }
  },
  setup(props, { emit }) {
    const chartWeaponRef = toRef(props, 'chartWeapon')
    const showYYYPListRef = toRef(props, 'showYYYPList')
    const showBuffListRef = toRef(props, 'showBuffList')
    const statisticTriggerRef = toRef(props, 'statisticDialogTrigger')

    const visible = computed(() => !!props.chartWeapon)

    const csqaqState = useCSQAQ(chartWeaponRef, showYYYPListRef, showBuffListRef, {
      onStatisticLoaded: (value) => emit('statistic-loaded', value)
    })

    watch(statisticTriggerRef, (val, oldVal) => {
      if (val !== oldVal && val > 0 && csqaqState.openStatisticDialog) {
        csqaqState.openStatisticDialog()
      }
    })

    return {
      visible,
      chartWeapon: chartWeaponRef,
      ...csqaqState
    }
  }
}
</script>

<style scoped src="./styles.css"></style>
