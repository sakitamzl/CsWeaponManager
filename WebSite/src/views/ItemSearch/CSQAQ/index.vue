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

            <div
              class="good-detail-statistic"
              v-if="goodDetail.data.goods_info.statistic != null"
              @click="openStatisticDialog"
            >
              <span class="label">存世量</span>
              <span class="value">{{ formatStatistic(goodDetail.data.goods_info.statistic) }}</span>
              <span class="hint">点击查看</span>
            </div>

            <div class="good-detail-section" v-if="(goodDetail.data.container || []).length">
              <div class="section-title">所属武器箱</div>
              <div class="container-list">
                <div
                  v-for="c in goodDetail.data.container"
                  :key="c.id"
                  class="container-item"
                >
                  <img v-if="c.url" :src="c.url" class="container-img" alt="" />
                  <div class="container-info">
                    <div class="container-name">{{ c.name }}</div>
                    <div class="container-meta">
                      <span v-if="c.price != null">¥{{ formatPrice(c.price) }}</span>
                      <span v-if="c.comment" class="container-comment">{{ c.comment }}</span>
                      <span v-if="c.roi != null">ROI {{ formatRate(c.roi) }}%</span>
                    </div>
                  </div>
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
          <el-radio-group
            v-model="chartViewMode"
            size="small"
            class="chart-view-toggle"
            :disabled="(chartViewMode === 'line' && chartLoading) || (chartViewMode === 'kline' && klineLoading) || (chartViewMode === 'chips' && chipLoading)"
          >
            <el-radio-button
              v-for="mode in CHART_VIEW_MODES"
              :key="mode.value"
              :label="mode.value"
            >
              {{ mode.label }}
            </el-radio-button>
          </el-radio-group>
          <!-- 获利筹码：与切换按钮同一行显示全部汇总数据 -->
          <span v-if="chartViewMode === 'chips' && chipSummary" class="chart-controls-chip-summary">
            获利比例：{{ chipSummary.profitRatio }}%　平均成本：¥{{ chipSummary.avgCost.toFixed(2) }}　90%成本：{{ chipSummary.p90Low.toFixed(0) }}-{{ chipSummary.p90High.toFixed(0) }}　集中度：{{ chipSummary.concentration }}%
          </span>
          <!-- K 线图：1小时/4小时/日线/周线 + 平台下拉，默认日线、BUFF；加载中禁用切换 -->
          <template v-if="chartViewMode === 'kline'">
            <el-radio-group v-model="klinePeriod" size="small" class="chart-view-toggle kline-period-toggle" :disabled="klineLoading">
              <el-radio-button
                v-for="opt in KLINE_PERIOD_OPTIONS"
                :key="opt.value"
                :label="opt.value"
              >
                {{ opt.label }}
              </el-radio-button>
            </el-radio-group>
            <el-select v-model="klinePlatform" placeholder="平台" size="small" class="chart-select" :disabled="klineLoading">
              <el-option v-for="opt in KLINE_PLATFORM_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
            </el-select>
          </template>
          <!-- 走势图：数据类型、平台、周期、款式（存世量/获利筹码模式不显示下拉与刷新） -->
          <template v-else-if="chartViewMode !== 'chips' && chartViewMode !== 'statistic'">
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
          </template>
          <el-button
            v-if="chartViewMode !== 'chips' && chartViewMode !== 'statistic'"
            type="primary"
            size="small"
            :loading="chartViewMode === 'kline' ? klineLoading : chartLoading"
            @click="chartViewMode === 'kline' ? fetchKlineData() : fetchChartData()"
          >
            刷新
          </el-button>
        </div>
        <div
          class="chart-body"
          v-loading="chartViewMode !== 'statistic' && (chartLoading || (chartViewMode === 'kline' && klineLoading) || (chartViewMode === 'chips' && chipLoading))"
          :element-loading-text="chartViewMode === 'kline' ? '加载K线...' : chartViewMode === 'chips' ? '加载筹码...' : '加载图表...'"
        >
          <!-- 存世量模式：直接显示数值 -->
          <div v-if="chartViewMode === 'statistic'" class="chart-body-statistic">
            <span class="statistic-value-label">当前存世量</span>
            <span class="statistic-value-number">{{ statisticDisplayValue }}</span>
          </div>
          <template v-else>
            <div ref="csqaqChartRef" class="csqaq-chart-dom" />
            <div
              v-if="!(chartLoading || (chartViewMode === 'kline' && klineLoading) || (chartViewMode === 'chips' && chipLoading)) && (chartViewMode === 'kline' ? !klineData?.length : chartViewMode === 'chips' ? !chipData?.date?.length : !chartData?.timestamp?.length)"
              class="chart-empty"
            >
              暂无数据
            </div>
          </template>
        </div>
      </div>
    </div>
    <el-dialog
      v-model="statisticDialogVisible"
      title="存世量"
      width="400px"
      destroy-on-close
    >
      <div class="statistic-value-body">
        <span class="statistic-value-label">当前存世量</span>
        <span class="statistic-value-number">{{ statisticDisplayValue }}</span>
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
