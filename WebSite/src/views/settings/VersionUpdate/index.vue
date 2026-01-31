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
