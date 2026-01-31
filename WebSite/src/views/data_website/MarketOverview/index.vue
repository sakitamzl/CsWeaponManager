<template>
  <div class="market-overview-container">
    <div class="content-wrapper">
      <!-- 通用时间周期选择 -->
      <div class="period-selector">
        <el-button-group>
          <el-button 
            size="small"
            :type="queryForm.period === '1h' ? 'primary' : ''"
            @click="changePeriod('1h')"
          >
            1小时线
          </el-button>
          <el-button 
            size="small"
            :type="queryForm.period === '4h' ? 'primary' : ''"
            @click="changePeriod('4h')"
          >
            4小时线
          </el-button>
          <el-button 
            size="small"
            :type="queryForm.period === '1d' ? 'primary' : ''"
            @click="changePeriod('1d')"
          >
            日线
          </el-button>
          <el-button 
            size="small"
            :type="queryForm.period === '1w' ? 'primary' : ''"
            @click="changePeriod('1w')"
          >
            周线
          </el-button>
        </el-button-group>
        <el-tag v-if="lastUpdateTime" type="info" size="small" style="margin-left: 1rem;">
          更新: {{ lastUpdateTime }}
        </el-tag>
        <el-button size="small" @click="fetchAllData" :loading="loading" style="margin-left: 1rem;">
          <el-icon><Refresh /></el-icon>
          刷新全部
        </el-button>
      </div>

      <!-- CSQAQ K线图表 -->
      <el-card class="chart-card" v-loading="loadingCSQAQ">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <div class="title-with-icon">
                <img src="/icons/CSQAQ.png" alt="CSQAQ" class="title-icon" />
                <span class="chart-title">CSQAQ 市场指数K线图</span>
              </div>
              
              <!-- 市场统计信息 -->
              <div class="stats-inline" v-if="statsDataCSQAQ">
                <div class="stat-inline-item">
                  <span class="stat-inline-label">当前指数</span>
                  <span class="stat-inline-value" :class="{ 'up': statsDataCSQAQ.change > 0, 'down': statsDataCSQAQ.change < 0 }">
                    {{ statsDataCSQAQ.latest }}
                  </span>
                </div>
                <div class="stat-inline-item">
                  <span class="stat-inline-label">涨跌幅</span>
                  <span class="stat-inline-value" :class="{ 'up': statsDataCSQAQ.change > 0, 'down': statsDataCSQAQ.change < 0 }">
                    {{ statsDataCSQAQ.change > 0 ? '+' : '' }}{{ statsDataCSQAQ.change }}%
                  </span>
                </div>
                <div class="stat-inline-item">
                  <span class="stat-inline-label">最高</span>
                  <span class="stat-inline-value">{{ statsDataCSQAQ.high }}</span>
                </div>
                <div class="stat-inline-item">
                  <span class="stat-inline-label">最低</span>
                  <span class="stat-inline-value">{{ statsDataCSQAQ.low }}</span>
                </div>
              </div>
            </div>
          </div>
        </template>
        
        <div ref="chartRefCSQAQ" class="chart-container"></div>
      </el-card>

      <!-- SteamDT K线图表 -->
      <el-card class="chart-card" v-loading="loadingSteamDT" v-if="queryForm.period !== '4h'">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <div class="title-with-icon">
                <img src="/icons/steamdt.png" alt="SteamDT" class="title-icon steamdt-icon" />
                <span class="chart-title">SteamDT 市场指数K线图</span>
              </div>
              
              <!-- 市场统计信息 -->
              <div class="stats-inline" v-if="statsDataSteamDT">
                <div class="stat-inline-item">
                  <span class="stat-inline-label">当前指数</span>
                  <span class="stat-inline-value" :class="{ 'up': statsDataSteamDT.change > 0, 'down': statsDataSteamDT.change < 0 }">
                    {{ statsDataSteamDT.latest }}
                  </span>
                </div>
                <div class="stat-inline-item">
                  <span class="stat-inline-label">涨跌幅</span>
                  <span class="stat-inline-value" :class="{ 'up': statsDataSteamDT.change > 0, 'down': statsDataSteamDT.change < 0 }">
                    {{ statsDataSteamDT.change > 0 ? '+' : '' }}{{ statsDataSteamDT.change }}%
                  </span>
                </div>
                <div class="stat-inline-item">
                  <span class="stat-inline-label">最高</span>
                  <span class="stat-inline-value">{{ statsDataSteamDT.high }}</span>
                </div>
                <div class="stat-inline-item">
                  <span class="stat-inline-label">最低</span>
                  <span class="stat-inline-value">{{ statsDataSteamDT.low }}</span>
                </div>
              </div>
            </div>
          </div>
        </template>
        
        <div ref="chartRefSteamDT" class="chart-container"></div>
      </el-card>

      <!-- SteamDT 不支持 4小时线提示 -->
      <el-card class="chart-card" v-if="queryForm.period === '4h'">
        <div class="no-data-tip">
          <el-icon :size="48" color="#909399"><WarningFilled /></el-icon>
          <p>SteamDT 不支持 4小时线数据</p>
          <p class="tip-sub">请选择其他时间周期查看 SteamDT 数据</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { useMarketOverview } from './useMarketOverview.js'

const {
  loading,
  loadingSteamDT,
  loadingCSQAQ,
  chartRefSteamDT,
  chartRefCSQAQ,
  lastUpdateTime,
  statsDataSteamDT,
  statsDataCSQAQ,
  queryForm,
  changePeriod,
  fetchAllData,
  Refresh,
  WarningFilled
} = useMarketOverview()
</script>

<style scoped src="./styles.css"></style>
