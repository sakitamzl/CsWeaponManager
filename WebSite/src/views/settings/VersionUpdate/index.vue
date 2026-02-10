<template>
  <div class="version-update-container">
    <div class="doc-box">
      <div class="page-layout">
        <!-- 左侧文档目录 -->
        <aside class="doc-sidebar">
          <div class="sidebar-header">
            <h3>文档目录</h3>
          </div>

          <div class="sidebar-divider"></div>

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
        </aside>

        <!-- 右侧内容区域 -->
        <div class="main-content-area">
          <!-- 版本检查区域 -->
          <div class="version-check-section">
            <div class="version-info-card">
              <div class="card-header">
                <h3>当前版本</h3>
                <el-button type="primary" @click="handleCheckUpdate" :loading="checkingUpdate">
                  <el-icon v-if="!checkingUpdate"><Refresh /></el-icon>
                  {{ checkingUpdate ? '检查中...' : '检查更新' }}
                </el-button>
              </div>
              <div class="card-body">
                <div class="version-display">
                  <span class="version-label">版本号：</span>
                  <span class="version-value">v{{ currentVersion }}</span>
                </div>
              </div>
            </div>

            <!-- 更新信息卡片 -->
            <div v-if="updateInfo" class="update-info-card">
              <div class="card-header">
                <h3>
                  <el-icon color="#67c23a"><SuccessFilled /></el-icon>
                  发现新版本
                </h3>
              </div>
              <div class="card-body">
                <div class="update-detail">
                  <div class="detail-item">
                    <span class="detail-label">最新版本：</span>
                    <span class="detail-value highlight">v{{ updateInfo.latest_version }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">发布日期：</span>
                    <span class="detail-value">{{ updateInfo.release_date }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">文件大小：</span>
                    <span class="detail-value">{{ updateInfo.file_size }}</span>
                  </div>
                  <div v-if="updateInfo.required" class="detail-item required-badge">
                    <el-tag type="danger" effect="dark">强制更新</el-tag>
                  </div>
                </div>

                <!-- 更新日志 -->
                <div class="changelog-section">
                  <h4>更新内容：</h4>
                  <ul class="changelog-list">
                    <li v-for="(item, index) in updateInfo.changelog" :key="index">{{ item }}</li>
                  </ul>
                </div>

                <!-- 更新按钮 -->
                <div class="update-actions">
                  <el-button
                    type="primary"
                    size="large"
                    @click="handleStartUpdate"
                    :loading="updating"
                    :disabled="updating"
                  >
                    <el-icon v-if="!updating"><Download /></el-icon>
                    {{ updateButtonText }}
                  </el-button>
                  <el-button
                    v-if="!updateInfo.required && !updating"
                    size="large"
                    @click="handleCancelUpdate"
                  >
                    稍后更新
                  </el-button>
                </div>

                <!-- 更新进度 -->
                <div v-if="updating" class="update-progress">
                  <el-progress :percentage="updateProgress" :status="updateStatus"></el-progress>
                  <p class="progress-text">{{ updateStatusText }}</p>
                </div>
              </div>
            </div>

            <!-- 没有更新时显示 -->
            <div v-else-if="!checkingUpdate && checkedOnce" class="no-update-card">
              <el-result
                icon="success"
                title="已是最新版本"
                sub-title="当前已经是最新版本，无需更新"
              >
              </el-result>
            </div>
          </div>
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

export default {
  name: 'VersionUpdate',
  setup() {
    return useVersionUpdate()
  }
}
</script>

<style scoped src="./styles.css"></style>
