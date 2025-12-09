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
            <div class="markdown-content" v-html="renderedMarkdown"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Document } from '@element-plus/icons-vue'
import axios from 'axios'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { API_CONFIG } from '@/config/api.js'
import TreeNode from '@/components/TreeNode.vue'

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true
})

export default {
  name: 'VersionUpdate',
  components: {
    Loading,
    Document,
    TreeNode
  },
  setup() {
    const treeLoading = ref(true)
    const treeError = ref(null)
    const fileTree = ref([])

    const contentLoading = ref(false)
    const contentError = ref(null)
    const selectedFilePath = ref('')
    const markdownContent = ref('')

    // 当前文件名
    const currentFileName = computed(() => {
      if (!selectedFilePath.value) return ''
      const parts = selectedFilePath.value.split('/')
      return parts[parts.length - 1].replace('.md', '')
    })

    // 渲染 markdown 为 HTML
    const renderedMarkdown = computed(() => {
      if (!markdownContent.value) return ''
      try {
        const rawHtml = marked.parse(markdownContent.value)
        return DOMPurify.sanitize(rawHtml)
      } catch (error) {
        console.error('Markdown 解析失败:', error)
        return '<p>Markdown 解析失败</p>'
      }
    })

    // 加载目录树
    const loadFileTree = async () => {
      treeLoading.value = true
      treeError.value = null

      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/api/version/documents/tree`)

        if (response.data.success) {
          fileTree.value = response.data.data

          // 自动选择 updateLog.md
          const updateLogFile = findFileInTree(fileTree.value, 'updateLog.md')
          if (updateLogFile) {
            await loadFile(updateLogFile.path)
          }
        } else {
          treeError.value = response.data.error || '加载文档目录失败'
        }
      } catch (err) {
        console.error('加载文档目录失败:', err)
        treeError.value = '无法连接到服务器，请检查后端服务是否运行'
      } finally {
        treeLoading.value = false
      }
    }

    // 在树中查找文件
    const findFileInTree = (tree, fileName) => {
      for (const node of tree) {
        if (node.type === 'file' && node.name === fileName) {
          return node
        }
        if (node.type === 'directory' && node.children) {
          const found = findFileInTree(node.children, fileName)
          if (found) return found
        }
      }
      return null
    }

    // 加载文件内容
    const loadFile = async (filePath) => {
      if (!filePath) return

      contentLoading.value = true
      contentError.value = null
      selectedFilePath.value = filePath

      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/api/version/documents/file`, {
          params: { path: filePath }
        })

        if (response.data.success) {
          markdownContent.value = response.data.data.content
        } else {
          contentError.value = response.data.error || '加载文档失败'
        }
      } catch (err) {
        console.error('加载文档失败:', err)
        contentError.value = '无法加载文档内容'
      } finally {
        contentLoading.value = false
      }
    }

    // 文件选择事件
    const onFileSelect = (filePath) => {
      loadFile(filePath)
    }

    onMounted(() => {
      loadFileTree()
    })

    return {
      treeLoading,
      treeError,
      fileTree,
      contentLoading,
      contentError,
      selectedFilePath,
      currentFileName,
      renderedMarkdown,
      onFileSelect
    }
  }
}
</script>

<style scoped>
.version-update-container {
  padding: 0;
}

.doc-box {
  background-color: #1e1e1e;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  margin: 0;
}

.page-layout {
  display: flex;
  gap: 1.5rem;
  min-height: calc(100vh - 180px);
  max-width: 100%;
}

/* 左侧文档目录 */
.doc-sidebar {
  width: 280px;
  min-width: 280px;
  flex-shrink: 0;
  background-color: #252525;
  border-radius: 0.5rem;
  padding: 1.5rem;
  border: 1px solid #333;
  display: flex;
  flex-direction: column;
  height: auto;
  align-self: stretch;
}

.sidebar-header {
  margin-bottom: 1rem;
}

.sidebar-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #409eff;
  margin: 0;
}

.sidebar-divider {
  height: 1px;
  background-color: #2f2f2f;
  border-radius: 1px;
  margin-bottom: 1rem;
}

.tree-loading,
.tree-error {
  padding: 2rem 1rem;
  text-align: center;
  color: #b0b0b0;
}

.tree-loading p {
  margin-top: 0.5rem;
  font-size: 0.875rem;
}

.doc-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 0.5rem;
}

/* 右侧主内容区域 */
.main-content-area {
  flex: 1;
  min-width: 0;
  width: auto;
  overflow-x: hidden;
}

.loading-container,
.empty-state,
.error-container {
  background-color: #252525;
  border-radius: 0.5rem;
  padding: 4rem 2rem;
  border: 1px solid #333;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #b0b0b0;
  min-height: 400px;
}

.loading-container p,
.empty-state p {
  margin-top: 1rem;
  font-size: 1rem;
}

.content-section {
  background-color: #252525;
  border-radius: 0.5rem;
  border: 1px solid #333;
  overflow: hidden;
}

.content-header {
  padding: 1.5rem 2rem;
  background-color: #2a2a2a;
  border-bottom: 1px solid #333;
}

.content-header h2 {
  color: #409eff;
  font-size: 1.5rem;
  margin: 0;
  font-weight: 600;
}

.markdown-content {
  padding: 2rem;
  color: #e0e0e0;
  line-height: 1.8;
}

/* Markdown 内容样式 */
.markdown-content :deep(h1) {
  color: #ffffff;
  font-size: 2rem;
  font-weight: 700;
  margin: 2rem 0 1.5rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(64, 158, 255, 0.3);
}

.markdown-content :deep(h1:first-child) {
  margin-top: 0;
}

.markdown-content :deep(h2) {
  color: #409eff;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 1.8rem 0 1rem 0;
  padding-left: 0.5rem;
  border-left: 4px solid #409eff;
}

.markdown-content :deep(h3) {
  color: #67c23a;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 1.5rem 0 0.8rem 0;
}

.markdown-content :deep(h4) {
  color: #e6a23c;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 1.2rem 0 0.6rem 0;
}

.markdown-content :deep(p) {
  margin: 0.8rem 0;
  color: #e0e0e0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 1rem 0;
  padding-left: 2rem;
}

.markdown-content :deep(li) {
  margin: 0.5rem 0;
  color: #e0e0e0;
}

.markdown-content :deep(code) {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(64, 158, 255, 0.2);
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
  overflow-x: auto;
}

.markdown-content :deep(pre code) {
  background: transparent;
  color: #67c23a;
  padding: 0;
  font-size: 0.9rem;
  line-height: 1.6;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #b0b0b0;
  font-style: italic;
}

.markdown-content :deep(a) {
  color: #409eff;
  text-decoration: none;
  transition: color 0.3s;
}

.markdown-content :deep(a:hover) {
  color: #66b1ff;
  text-decoration: underline;
}

.markdown-content :deep(strong) {
  color: #ffffff;
  font-weight: 600;
}

.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid rgba(58, 58, 58, 0.8);
  margin: 2rem 0;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #2f2f2f;
  padding: 0.75rem;
  text-align: left;
}

.markdown-content :deep(th) {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
  font-weight: 600;
}

.markdown-content :deep(tr:nth-child(even)) {
  background: rgba(35, 35, 35, 0.3);
}

/* 滚动条样式 */
.doc-list::-webkit-scrollbar {
  width: 6px;
}

.doc-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.doc-list::-webkit-scrollbar-thumb {
  background: rgba(64, 158, 255, 0.3);
  border-radius: 3px;
}

.doc-list::-webkit-scrollbar-thumb:hover {
  background: rgba(64, 158, 255, 0.5);
}
</style>
