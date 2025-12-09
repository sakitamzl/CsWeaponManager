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
import { ref, onMounted, computed, nextTick, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Document } from '@element-plus/icons-vue'
import axios from 'axios'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { API_CONFIG } from '@/config/api.js'
import TreeNode from '@/components/TreeNode.vue'

// 配置 marked 渲染器，为标题添加 ID
const renderer = new marked.Renderer()
const headingIds = new Map()

renderer.heading = function(text, level) {
  // 生成唯一的 ID
  const rawText = text.replace(/<[^>]*>/g, '') // 移除 HTML 标签
  let id = rawText
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w\u4e00-\u9fa5-]/g, '')
  
  // 处理重复 ID
  if (headingIds.has(id)) {
    const count = headingIds.get(id) + 1
    headingIds.set(id, count)
    id = `${id}-${count}`
  } else {
    headingIds.set(id, 0)
  }
  
  return `<h${level} id="${id}">${text}</h${level}>`
}

marked.setOptions({
  breaks: true,
  gfm: true,
  renderer: renderer
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
    const markdownContainer = ref(null)
    const tocItems = ref([])
    const activeAnchor = ref('')

    // 当前文件名
    const currentFileName = computed(() => {
      if (!selectedFilePath.value) return ''
      const parts = selectedFilePath.value.split('/')
      return parts[parts.length - 1].replace('.md', '')
    })

    // 从 Markdown 内容提取目录
    const extractTOC = (content) => {
      // 首先尝试解析 Markdown 中已有的目录章节
      const tocFromMarkdown = extractTOCFromMarkdown(content)
      if (tocFromMarkdown.length > 0) {
        return tocFromMarkdown
      }

      // 如果没有找到目录章节，则自动生成
      return extractTOCFromHeadings(content)
    }

    // 从 Markdown 目录章节中提取目录
    const extractTOCFromMarkdown = (content) => {
      const toc = []
      const lines = content.split('\n')
      let inTocSection = false
      let tocSectionEnded = false

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim()

        // 检测目录章节开始（## 目录 或 ## 📋 目录 等）
        if (/^##\s+.*目录.*$/i.test(line)) {
          inTocSection = true
          continue
        }

        // 如果在目录章节中
        if (inTocSection && !tocSectionEnded) {
          // 遇到下一个二级标题，目录章节结束
          if (/^##\s+/.test(line)) {
            tocSectionEnded = true
            break
          }

          // 解析目录链接：- [文本](#锚点) 或   - [文本](#锚点)（带缩进）
          const match = line.match(/^(\s*)-\s+\[(.+?)\]\(#(.+?)\)/)
          if (match) {
            const indent = match[1].length
            const text = match[2]
            const id = match[3]
            // 根据缩进计算层级（每2个空格为一级）
            const level = Math.floor(indent / 2) + 1
            
            toc.push({ level, text, id })
          }
        }
      }

      return toc
    }

    // 从所有标题自动生成目录
    const extractTOCFromHeadings = (content) => {
      const toc = []
      const lines = content.split('\n')
      const idMap = new Map()

      lines.forEach(line => {
        const match = line.match(/^(#{1,6})\s+(.+)$/)
        if (match) {
          const level = match[1].length
          const text = match[2].trim()
          
          // 生成 ID（与 renderer 保持一致）
          let id = text
            .toLowerCase()
            .replace(/\s+/g, '-')
            .replace(/[^\w\u4e00-\u9fa5-]/g, '')
          
          // 处理重复 ID
          if (idMap.has(id)) {
            const count = idMap.get(id) + 1
            idMap.set(id, count)
            id = `${id}-${count}`
          } else {
            idMap.set(id, 0)
          }
          
          toc.push({ level, text, id })
        }
      })

      return toc
    }

    // 渲染 markdown 为 HTML
    const renderedMarkdown = computed(() => {
      if (!markdownContent.value) return ''
      try {
        // 重置 headingIds
        headingIds.clear()
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
          // 提取目录
          tocItems.value = extractTOC(response.data.data.content)
          
          // 等待 DOM 更新后设置滚动监听
          await nextTick()
          setupScrollSpy()
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

    // 滚动到指定锚点
    const scrollToAnchor = (id) => {
      const element = document.getElementById(id)
      const container = markdownContainer.value
      
      if (element && container) {
        const offsetTop = element.offsetTop - container.offsetTop - 20
        container.scrollTo({
          top: offsetTop,
          behavior: 'smooth'
        })
      }
      activeAnchor.value = id
    }

    // 设置滚动监听
    let scrollTimeout = null
    const setupScrollSpy = () => {
      const container = markdownContainer.value
      if (!container) return

      const handleScroll = () => {
        if (scrollTimeout) {
          clearTimeout(scrollTimeout)
        }

        scrollTimeout = setTimeout(() => {
          const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6')
          const scrollTop = container.scrollTop
          
          let currentId = ''
          headings.forEach(heading => {
            const offsetTop = heading.offsetTop - container.offsetTop
            if (offsetTop <= scrollTop + 100) {
              currentId = heading.id
            }
          })

          if (currentId) {
            activeAnchor.value = currentId
          }
        }, 100)
      }

      container.addEventListener('scroll', handleScroll)
      
      // 清理函数
      onBeforeUnmount(() => {
        container.removeEventListener('scroll', handleScroll)
        if (scrollTimeout) {
          clearTimeout(scrollTimeout)
        }
      })
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
      onFileSelect,
      markdownContainer,
      tocItems,
      activeAnchor,
      scrollToAnchor
    }
  }
}
</script>

<style scoped>
.version-update-container {
  padding: 0;
  height: 100vh;
  overflow: hidden;
}

.doc-box {
  background-color: #1e1e1e;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  margin: 0;
  height: 100%;
  overflow: hidden;
}

.page-layout {
  display: flex;
  gap: 1.5rem;
  max-width: 100%;
  height: calc(100vh - 3rem);
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
  height: 100%;
  overflow: hidden;
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
  padding-right: 0.5rem;
  overflow-y: auto;
  flex: 1;
}

/* 右侧主内容区域 */
.main-content-area {
  flex: 1;
  min-width: 0;
  width: auto;
  display: flex;
  gap: 1.5rem;
  height: 100%;
  overflow: hidden;
}

.content-wrapper {
  flex: 1;
  min-width: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Markdown 目录导航 */
.toc-sidebar {
  width: 240px;
  min-width: 240px;
  flex-shrink: 0;
  background-color: #252525;
  border-radius: 0.5rem;
  padding: 1.5rem;
  border: 1px solid #333;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.toc-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #67c23a;
  margin: 0 0 1rem 0;
}

.toc-divider {
  height: 1px;
  background-color: #2f2f2f;
  border-radius: 1px;
  margin-bottom: 1rem;
}

.toc-nav {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  overflow-y: auto;
  flex: 1;
  padding-right: 0.5rem;
}

.toc-link {
  color: #b0b0b0;
  text-decoration: none;
  padding: 0.4rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  line-height: 1.4;
  transition: all 0.2s;
  border-left: 2px solid transparent;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.toc-link:hover {
  color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
}

.toc-link.active {
  color: #409eff;
  background-color: rgba(64, 158, 255, 0.15);
  border-left-color: #409eff;
  font-weight: 500;
}

.toc-level-1 {
  padding-left: 0.5rem;
  font-weight: 600;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.toc-level-1:first-child {
  margin-top: 0;
}

.toc-level-2 {
  padding-left: 1.2rem;
  font-size: 0.875rem;
  position: relative;
}

.toc-level-2::before {
  content: '';
  position: absolute;
  left: 0.6rem;
  top: 50%;
  width: 4px;
  height: 4px;
  background-color: #67c23a;
  border-radius: 50%;
  transform: translateY(-50%);
  opacity: 0.5;
}

.toc-level-3 {
  padding-left: 2rem;
  font-size: 0.8rem;
  position: relative;
}

.toc-level-3::before {
  content: '›';
  position: absolute;
  left: 1.2rem;
  color: #67c23a;
  opacity: 0.5;
  font-size: 0.9rem;
}

.toc-level-4 {
  padding-left: 2.8rem;
  font-size: 0.75rem;
  position: relative;
}

.toc-level-4::before {
  content: '·';
  position: absolute;
  left: 2rem;
  color: #67c23a;
  opacity: 0.4;
}

.toc-level-5,
.toc-level-6 {
  padding-left: 3.5rem;
  font-size: 0.7rem;
  color: #909399;
  opacity: 0.8;
}

.toc-nav::-webkit-scrollbar {
  width: 6px;
}

.toc-nav::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.toc-nav::-webkit-scrollbar-thumb {
  background: rgba(103, 194, 58, 0.3);
  border-radius: 3px;
}

.toc-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(103, 194, 58, 0.5);
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
  height: 100%;
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
  display: flex;
  flex-direction: column;
  height: 100%;
}

.content-header {
  padding: 1.5rem 2rem;
  background-color: #2a2a2a;
  border-bottom: 1px solid #333;
  flex-shrink: 0;
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
  overflow-y: auto;
  flex: 1;
  scroll-behavior: smooth;
}

.markdown-content::-webkit-scrollbar {
  width: 8px;
}

.markdown-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.markdown-content::-webkit-scrollbar-thumb {
  background: rgba(64, 158, 255, 0.3);
  border-radius: 4px;
}

.markdown-content::-webkit-scrollbar-thumb:hover {
  background: rgba(64, 158, 255, 0.5);
}

/* Markdown 内容样式 */
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  scroll-margin-top: 20px;
}

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
