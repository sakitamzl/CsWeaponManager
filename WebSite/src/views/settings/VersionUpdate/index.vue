<template>
  <div class="version-update-container">
    <div class="doc-box">
      <div class="page-layout">
        <!-- 左侧区域：版本更新 + 文档目录 -->
        <aside class="left-sidebar">
          <!-- 版本检查区域（紧凑版） -->
          <div class="version-check-section">
            <div class="version-header">
              <h3>版本管理</h3>
            </div>

            <div class="version-info">
              <div class="current-version">
                <span class="label">当前版本</span>
                <span class="value">v{{ currentVersion }}</span>
              </div>

              <el-button
                type="primary"
                size="small"
                @click="handleCheckUpdate"
                :loading="checkingUpdate"
                style="width: 100%;"
              >
                <el-icon v-if="!checkingUpdate"><Refresh /></el-icon>
                {{ checkingUpdate ? '检查中...' : '检查更新' }}
              </el-button>
            </div>

            <!-- 发现新版本 -->
            <div v-if="updateInfo" class="update-alert">
              <div style="font-size: 13px; font-weight: 600; color: #67c23a;">
                发现新版本 v{{ updateInfo.latest_version }}
              </div>
              <div style="font-size: 12px; margin-top: 8px; color: #ccc;">
                <div>发布日期: {{ updateInfo.release_date }}</div>
                <div style="margin-top: 4px;">大小: {{ updateInfo.file_size }}</div>
                <!-- 已下载：显示立即更新 -->
                <el-button
                  v-if="downloaded || localUpdateExists"
                  type="success"
                  size="small"
                  style="width: 100%; margin-top: 10px;"
                  @click="handleApplyUpdate"
                >
                  立即更新
                </el-button>
                <!-- 未下载：显示下载按钮 -->
                <el-button
                  v-else
                  type="success"
                  size="small"
                  style="width: 100%; margin-top: 10px;"
                  @click="handleDownloadUpdate"
                  :loading="updating"
                >
                  {{ updating ? updateStatusText : '下载更新' }}
                </el-button>
                <div v-if="updating" style="margin-top: 10px;">
                  <el-progress :percentage="updateProgress" :status="updateStatus" />
                  <div v-if="downloadSpeed" style="font-size: 11px; color: #999; margin-top: 4px; text-align: center;">
                    {{ updateStatusText }} · {{ downloadSpeed }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 无更新提示 -->
            <div v-else-if="!checkingUpdate && checkedOnce" class="no-update">
              <span style="font-size: 12px; color: #67c23a;">已是最新版本</span>
            </div>
          </div>

          <div class="sidebar-divider"></div>

          <!-- 文档目录 -->
          <div class="doc-sidebar">
            <div class="sidebar-header">
              <h3>文档目录</h3>
            </div>

            <div v-if="treeLoading" class="tree-loading">
              <el-icon class="is-loading">
                <Loading />
              </el-icon>
              <p>加载中...</p>
            </div>

            <div v-else-if="treeError" class="tree-error">
              <el-alert type="error" :title="treeError" show-icon :closable="false" />
            </div>

            <div v-else class="doc-list">
              <TreeNode
                v-for="item in fileTree"
                :key="item.path"
                :node="item"
                :selected-path="selectedFilePath"
                @select="onFileSelect"
              />
            </div>
          </div>
        </aside>

        <!-- 右侧内容区域 -->
        <div class="main-content-area">
          <!-- Markdown 目录导航 -->
          <aside v-if="tocItems.length > 0 && !contentLoading && !contentError && selectedFilePath" class="toc-sidebar">
            <div class="toc-header">
              <h3>目录导航</h3>
            </div>
            <div class="toc-divider"></div>
            <nav class="toc-nav">
              <a
                v-for="item in tocItems"
                :key="item.id"
                :href="`#${item.id}`"
                :class="['toc-link', `toc-level-${item.level}`, { active: activeAnchor === item.id }]"
                @click.prevent="scrollToAnchor(item.id)"
              >
                {{ item.text }}
              </a>
            </nav>
          </aside>

          <div class="content-wrapper">
            <!-- 加载状态 -->
            <div v-if="contentLoading" class="loading-container">
              <el-icon class="is-loading" :size="40">
                <Loading />
              </el-icon>
              <p>加载文档中...</p>
            </div>

            <!-- 错误提示 -->
            <div v-else-if="contentError" class="error-container">
              <el-alert
                type="error"
                :title="contentError"
                show-icon
                :closable="false"
              />
            </div>

            <!-- 空状态 -->
            <div v-else-if="!selectedFilePath" class="empty-state">
              <el-icon :size="80" color="#909399">
                <Document />
              </el-icon>
              <p>请从左侧选择一个文档查看</p>
            </div>

            <!-- Markdown 内容显示 -->
            <div v-else class="content-section">
              <div class="content-header">
                <h2>{{ currentFileName }}</h2>
              </div>
              <div ref="markdownContainer" class="markdown-content" v-html="renderedMarkdown"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { useVersionUpdate } from './useVersionUpdate.js'
import TreeNode from './TreeNode.vue'
import { Loading, Document, Refresh, Download, SuccessFilled } from '@element-plus/icons-vue'

export default {
  name: 'VersionUpdate',
  components: {
    TreeNode,
    Loading,
    Document,
    Refresh,
    Download,
    SuccessFilled
  },
  setup() {
    return useVersionUpdate()
  }
}
</script>

<style scoped src="./styles.css"></style>
