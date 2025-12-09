<template>
  <div>
    <div class="settings-container">
      <div class="settings-section">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading" :size="40">
            <Loading />
          </el-icon>
          <p>加载更新日志中...</p>
        </div>

        <!-- 错误提示 -->
        <el-alert
          v-else-if="error"
          type="error"
          :title="error"
          show-icon
          :closable="false"
        />

        <!-- Markdown 内容显示 -->
        <div v-else class="markdown-container" v-html="renderedMarkdown"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import axios from 'axios'
import { API_CONFIG } from '@/config/api.js'

export default {
  name: 'VersionUpdate',
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const markdownContent = ref('')

    // 简单的 markdown 解析器
    const parseMarkdown = (md) => {
      if (!md) return ''
      
      let html = md
      
      // 转义 HTML 特殊字符
      const escapeHtml = (text) => {
        const map = {
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#039;'
        }
        return text.replace(/[&<>"']/g, m => map[m])
      }
      
      // 处理代码块
      html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code class="language-${lang || 'text'}">${escapeHtml(code.trim())}</code></pre>`
      })
      
      // 处理行内代码
      html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
      
      // 处理标题
      html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>')
      html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
      html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
      html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')
      
      // 处理粗体
      html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      
      // 处理列表
      html = html.replace(/^\d+\.\s+(.*)$/gim, '<li>$1</li>')
      html = html.replace(/^[-*]\s+(.*)$/gim, '<li>$1</li>')
      
      // 包装连续的 li 标签
      html = html.replace(/(<li>.*<\/li>\n?)+/g, match => {
        return '<ul>' + match + '</ul>'
      })
      
      // 处理段落
      html = html.split('\n\n').map(para => {
        para = para.trim()
        if (!para) return ''
        if (para.startsWith('<h') || para.startsWith('<ul') || para.startsWith('<pre')) {
          return para
        }
        return '<p>' + para.replace(/\n/g, '<br>') + '</p>'
      }).join('\n')
      
      return html
    }

    // 渲染 markdown 为 HTML
    const renderedMarkdown = computed(() => {
      return parseMarkdown(markdownContent.value)
    })

    // 加载更新日志
    const loadUpdateLog = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/api/version/update-log`)
        
        if (response.data.success) {
          markdownContent.value = response.data.data.content
        } else {
          error.value = response.data.error || '加载更新日志失败'
        }
      } catch (err) {
        console.error('加载更新日志失败:', err)
        error.value = '无法连接到服务器，请检查后端服务是否运行'
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadUpdateLog()
    })

    return {
      loading,
      error,
      renderedMarkdown
    }
  },
  components: {
    Loading
  }
}
</script>

<style scoped>
.settings-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.settings-section {
  background: rgba(26, 26, 26, 0.6);
  border-radius: 12px;
  padding: 2rem;
  backdrop-filter: blur(10px);
}

.settings-section h3 {
  color: #ffffff;
  font-size: 1.5rem;
  margin-bottom: 2rem;
  font-weight: 600;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #b0b0b0;
}

.loading-container p {
  margin-top: 1rem;
  font-size: 1rem;
}

/* Markdown 内容样式 */
.markdown-container {
  color: #e0e0e0;
  line-height: 1.8;
}

.markdown-container :deep(h1) {
  color: #ffffff;
  font-size: 2rem;
  font-weight: 700;
  margin: 2rem 0 1.5rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(64, 158, 255, 0.3);
}

.markdown-container :deep(h2) {
  color: #409eff;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 1.8rem 0 1rem 0;
  padding-left: 0.5rem;
  border-left: 4px solid #409eff;
}

.markdown-container :deep(h3) {
  color: #67c23a;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 1.5rem 0 0.8rem 0;
}

.markdown-container :deep(h4) {
  color: #e6a23c;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 1.2rem 0 0.6rem 0;
}

.markdown-container :deep(p) {
  margin: 0.8rem 0;
  color: #e0e0e0;
}

.markdown-container :deep(ul),
.markdown-container :deep(ol) {
  margin: 1rem 0;
  padding-left: 2rem;
}

.markdown-container :deep(li) {
  margin: 0.5rem 0;
  color: #e0e0e0;
}

.markdown-container :deep(code) {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-container :deep(pre) {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(64, 158, 255, 0.2);
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
  overflow-x: auto;
}

.markdown-container :deep(pre code) {
  background: transparent;
  color: #67c23a;
  padding: 0;
  font-size: 0.9rem;
  line-height: 1.6;
}

.markdown-container :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #b0b0b0;
  font-style: italic;
}

.markdown-container :deep(a) {
  color: #409eff;
  text-decoration: none;
  transition: color 0.3s;
}

.markdown-container :deep(a:hover) {
  color: #66b1ff;
  text-decoration: underline;
}

.markdown-container :deep(strong) {
  color: #ffffff;
  font-weight: 600;
}

.markdown-container :deep(hr) {
  border: none;
  border-top: 1px solid rgba(58, 58, 58, 0.8);
  margin: 2rem 0;
}

.markdown-container :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.markdown-container :deep(th),
.markdown-container :deep(td) {
  border: 1px solid rgba(58, 58, 58, 0.8);
  padding: 0.75rem;
  text-align: left;
}

.markdown-container :deep(th) {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
  font-weight: 600;
}

.markdown-container :deep(tr:nth-child(even)) {
  background: rgba(35, 35, 35, 0.3);
}
</style>

