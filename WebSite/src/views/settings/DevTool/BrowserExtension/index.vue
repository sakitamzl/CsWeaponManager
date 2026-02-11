<template>
  <div class="browser-extension-card">
    <el-card class="setting-card">
      <template #header>
        <div class="card-header">
          <span>SteamDT 数据拦截扩展</span>
          <el-tag v-if="extensionInstalled" type="success" size="small">已安装</el-tag>
          <el-tag v-else type="info" size="small">未安装</el-tag>
        </div>
      </template>

      <div class="extension-content">
        <el-alert
          title="功能说明"
          type="info"
          :closable="false"
          style="margin-bottom: 1rem;"
        >
          <template #default>
            <p>该浏览器扩展用于监听 SteamDT 网站的 API 请求,自动提取大盘指数和 K 线数据,提供给主页展示。</p>
            <p style="margin-top: 0.5rem;">支持浏览器:Chrome、Edge、Brave 等基于 Chromium 的浏览器</p>
          </template>
        </el-alert>

        <!-- 扩展状态 -->
        <div class="extension-status-panel">
          <div class="status-item">
            <span class="label">扩展状态:</span>
            <span class="value" :class="extensionInstalled ? 'success' : 'warning'">
              {{ extensionInstalled ? '已安装并运行' : '未检测到扩展' }}
            </span>
          </div>
          <div v-if="extensionInstalled && lastUpdate" class="status-item">
            <span class="label">最后更新:</span>
            <span class="value">{{ formatTime(lastUpdate) }}</span>
          </div>
        </div>

        <!-- 一键安装按钮 -->
        <div v-if="!extensionInstalled" class="one-click-install">
          <el-button
            type="primary"
            size="large"
            @click="oneClickInstall"
            :icon="Download"
          >
            🚀 一键安装扩展
          </el-button>
          <p class="install-hint">点击后会自动完成大部分安装步骤,您只需完成最后确认</p>
        </div>

        <!-- 安装步骤 -->
        <div class="install-steps">
          <h4>安装步骤:</h4>
          <ol>
            <li>
              <strong>打开浏览器扩展页面</strong>
              <el-button
                type="primary"
                size="small"
                @click="openExtensionPage"
                style="margin-left: 1rem;"
              >
                打开扩展页面
              </el-button>
            </li>
            <li>
              <strong>启用开发者模式</strong>
              <p class="step-desc">在扩展页面右上角,打开"开发者模式"开关</p>
            </li>
            <li>
              <strong>加载扩展</strong>
              <el-button
                type="success"
                size="small"
                @click="showExtensionPath"
                style="margin-left: 1rem;"
              >
                复制扩展路径
              </el-button>
              <p class="step-desc">点击"加载已解压的扩展程序",选择扩展目录</p>
            </li>
            <li>
              <strong>刷新页面</strong>
              <el-button
                type="primary"
                size="small"
                @click="refreshPage"
                style="margin-left: 1rem;"
              >
                刷新页面
              </el-button>
              <p class="step-desc">安装完成后刷新页面即可生效</p>
            </li>
          </ol>
        </div>

        <!-- 扩展路径显示 -->
        <div v-if="showPath" class="extension-path">
          <el-alert type="success" :closable="false">
            <template #default>
              <p><strong>扩展目录路径:</strong></p>
              <code>{{ extensionPath }}</code>
              <el-button
                type="primary"
                size="small"
                @click="copyPath"
                style="margin-left: 1rem;"
              >
                {{ copied ? '已复制' : '复制路径' }}
              </el-button>
            </template>
          </el-alert>
        </div>

        <!-- 测试按钮 -->
        <div v-if="extensionInstalled" class="test-section">
          <h4>扩展测试:</h4>
          <el-button type="primary" @click="testExtension">
            测试数据拦截
          </el-button>
          <el-button @click="checkExtensionStatus">
            刷新扩展状态
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { useBrowserExtension } from './useBrowserExtension.js'

const {
  extensionInstalled,
  lastUpdate,
  showPath,
  extensionPath,
  copied,
  oneClickInstall,
  openExtensionPage,
  showExtensionPath,
  copyPath,
  refreshPage,
  testExtension,
  checkExtensionStatus,
  formatTime
} = useBrowserExtension()
</script>

<style scoped src="./styles.css"></style>
