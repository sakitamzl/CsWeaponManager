import { ref, onMounted, computed, nextTick, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { API_CONFIG, apiUrls } from '@/config/api.js'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

export function useVersionUpdate() {
  // 更新相关状态
  const currentVersion = ref('0.0.0')
  const checkingUpdate = ref(false)
  const checkedOnce = ref(false)
  const updateInfo = ref(null)
  const updating = ref(false)
  const updateProgress = ref(0)
  const updateStatus = ref('')
  const updateStatusText = ref('')
  const downloadSpeed = ref('')
  const localUpdateExists = ref(false)
  const localUpdateSize = ref('')
  const downloaded = ref(false)
  const headingIds = new Map()
  let currentFilePath = ''

  // 创建自定义 renderer
  const renderer = new marked.Renderer()

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

  // 处理图片路径
  renderer.image = function(href, title, text) {
    // 如果是相对路径，转换为 API 路径
    let imageSrc = href
    if (href && !href.startsWith('http://') && !href.startsWith('https://') && !href.startsWith('data:')) {
      // 获取当前文件的目录
      const fileDir = currentFilePath.substring(0, currentFilePath.lastIndexOf('/'))
      // 解析相对路径
      let resolvedPath = href
      if (href.startsWith('../')) {
        // 处理 ../ 路径
        const parts = fileDir.split('/')
        const upLevels = (href.match(/\.\.\//g) || []).length
        const remainingPath = href.replace(/\.\.\//g, '')
        const newParts = parts.slice(0, parts.length - upLevels)
        resolvedPath = [...newParts, remainingPath].join('/')
      } else if (href.startsWith('./')) {
        // 处理 ./ 路径
        resolvedPath = fileDir + '/' + href.substring(2)
      } else if (!href.startsWith('/')) {
        // 相对路径
        resolvedPath = fileDir + '/' + href
      }
      
      // 转换为 API 路径
      imageSrc = `${API_CONFIG.BASE_URL}/api/version/documents/image?path=${encodeURIComponent(resolvedPath)}`
    }
    
    const titleAttr = title ? ` title="${title}"` : ''
    const altAttr = text ? ` alt="${text}"` : ''
    return `<img src="${imageSrc}"${altAttr}${titleAttr} />`
  }

  marked.setOptions({
    breaks: true,
    gfm: true,
    renderer: renderer
  })

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
      const line = lines[i]
      const trimmedLine = line.trim()

      // 检测目录章节开始（## 目录 或 ## 📋 目录 等）
      if (/^##\s+.*目录.*$/i.test(trimmedLine)) {
        inTocSection = true
        continue
      }

      // 如果在目录章节中
      if (inTocSection && !tocSectionEnded) {
        // 遇到下一个二级标题或空行后的分隔符，目录章节结束
        if (/^##\s+/.test(trimmedLine) || /^---+$/.test(trimmedLine)) {
          tocSectionEnded = true
          break
        }

        // 解析目录链接：- [文本](#锚点) 或   - [文本](#锚点)（带缩进）
        // 使用原始行来保留缩进
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

  // 移除 Markdown 中的目录章节
  const removeTOCSection = (content) => {
    const lines = content.split('\n')
    const result = []
    let inTocSection = false
    let skipNextSeparator = false

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      const trimmedLine = line.trim()

      // 检测目录章节开始
      if (/^##\s+.*目录.*$/i.test(trimmedLine)) {
        inTocSection = true
        skipNextSeparator = true
        continue
      }

      // 如果在目录章节中
      if (inTocSection) {
        // 遇到下一个二级标题或分隔符，目录章节结束
        if (/^##\s+/.test(trimmedLine)) {
          inTocSection = false
          result.push(line)
        } else if (/^---+$/.test(trimmedLine) && skipNextSeparator) {
          inTocSection = false
          skipNextSeparator = false
          // 跳过目录后的分隔符
          continue
        }
        // 在目录章节中的行都跳过
        continue
      }

      result.push(line)
    }

    return result.join('\n')
  }

  // 渲染 markdown 为 HTML
  const renderedMarkdown = computed(() => {
    if (!markdownContent.value) return ''
    try {
      // 重置 headingIds
      headingIds.clear()
      // 移除目录章节后再渲染
      const contentWithoutTOC = removeTOCSection(markdownContent.value)
      const rawHtml = marked.parse(contentWithoutTOC)
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
        // 设置当前文件路径，用于解析图片相对路径
        currentFilePath = filePath
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

  // ============================================
  // 更新系统功能
  // ============================================

  // 获取当前版本
  const loadCurrentVersion = async () => {
    try {
      const response = await axios.get(apiUrls.getCurrentVersion())
      if (response.data.success) {
        currentVersion.value = response.data.data.version
      }
    } catch (err) {
      console.error('获取当前版本失败:', err)
    }
  }

  // 检查更新
  const handleCheckUpdate = async () => {
    checkingUpdate.value = true
    checkedOnce.value = true
    updateInfo.value = null

    try {
      const response = await axios.get(apiUrls.checkUpdate())

      if (response.data.success) {
        if (response.data.has_update) {
          updateInfo.value = response.data.data
          ElMessage.success('发现新版本！')
        } else {
          ElMessage.info('当前已是最新版本')
        }
      } else {
        ElMessage.error(response.data.error || '检查更新失败')
      }
    } catch (err) {
      console.error('检查更新失败:', err)
      const serverMsg = err.response?.data?.error
      if (serverMsg) {
        ElMessage.error(serverMsg)
      } else {
        ElMessage.error('检查更新失败，请稍后重试')
      }
    } finally {
      checkingUpdate.value = false
    }
  }

  // 下载更新包（SSE 流式进度）
  const handleDownloadUpdate = async () => {
    try {
      updating.value = true
      updateProgress.value = 0
      updateStatus.value = ''
      updateStatusText.value = '正在连接...'
      downloadSpeed.value = ''

      const response = await fetch(apiUrls.downloadUpdate(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ download_url: updateInfo.value.download_url })
      })

      if (!response.ok) {
        throw new Error(`服务器响应异常: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() // 保留未完成的行

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6))

            if (event.type === 'progress') {
              updateProgress.value = event.progress
              downloadSpeed.value = event.speed
              const dlSize = format_file_size(event.downloaded)
              const totalSize = format_file_size(event.total)
              updateStatusText.value = `${dlSize} / ${totalSize}`
            } else if (event.type === 'complete') {
              updateProgress.value = 100
              updateStatus.value = 'success'
              updateStatusText.value = '下载完成'
              downloadSpeed.value = ''
              downloaded.value = true
            } else if (event.type === 'error') {
              throw new Error(event.error)
            }
          } catch (parseErr) {
            if (parseErr.message && !parseErr.message.includes('JSON')) {
              throw parseErr
            }
          }
        }
      }

      if (!downloaded.value) {
        throw new Error('下载异常中断')
      }

      // 下载完成后弹出是否立即更新
      await ElMessageBox.confirm(
        '更新包下载完成，是否立即更新？更新将重启应用。',
        '下载完成',
        {
          confirmButtonText: '立即更新',
          cancelButtonText: '稍后更新',
          type: 'success'
        }
      )

      // 用户点击了立即更新
      await doApplyUpdate()

    } catch (err) {
      if (err === 'cancel') {
        // 用户选择稍后更新，保持下载完成状态
        updating.value = false
        return
      }

      console.error('下载更新失败:', err)
      updateStatus.value = 'exception'
      updateStatusText.value = '下载失败'
      downloadSpeed.value = ''
      ElMessage.error(err.message || '下载更新失败，请稍后重试')

      setTimeout(() => {
        updating.value = false
        updateProgress.value = 0
        updateStatus.value = ''
        updateStatusText.value = ''
      }, 3000)
    }
  }

  // 前端格式化文件大小
  const format_file_size = (bytes) => {
    let size = bytes
    for (const unit of ['B', 'KB', 'MB', 'GB']) {
      if (size < 1024.0) return `${size.toFixed(1)} ${unit}`
      size /= 1024.0
    }
    return `${size.toFixed(1)} TB`
  }

  // 执行更新（调用 update.bat）
  const doApplyUpdate = async () => {
    try {
      const response = await axios.post(apiUrls.applyUpdate())
      if (response.data.success) {
        ElMessage.success('更新程序已启动，应用即将重启')
      } else {
        throw new Error(response.data.error || '启动更新失败')
      }
    } catch (err) {
      console.error('执行更新失败:', err)
      const serverMsg = err.response?.data?.error
      ElMessage.error(serverMsg || err.message || '执行更新失败')
    }
  }

  // 立即更新按钮（本地已有更新包时直接调用）
  const handleApplyUpdate = async () => {
    try {
      await ElMessageBox.confirm(
        '确定要立即更新吗？更新将重启应用。',
        '确认更新',
        {
          confirmButtonText: '立即更新',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      await doApplyUpdate()
    } catch (err) {
      if (err === 'cancel') return
    }
  }

  // 取消更新
  const handleCancelUpdate = () => {
    updateInfo.value = null
    checkedOnce.value = false
  }

  // 检查本地是否已有更新包
  const checkLocalUpdate = async () => {
    try {
      const response = await axios.get(apiUrls.checkLocalUpdate())
      if (response.data.success && response.data.data.exists) {
        localUpdateExists.value = true
        localUpdateSize.value = response.data.data.file_size
      }
    } catch (err) {
      console.error('检查本地更新包失败:', err)
    }
  }

  onMounted(() => {
    loadFileTree()
    loadCurrentVersion()
    checkLocalUpdate()
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
    scrollToAnchor,
    // 更新系统
    currentVersion,
    checkingUpdate,
    checkedOnce,
    updateInfo,
    updating,
    updateProgress,
    updateStatus,
    updateStatusText,
    downloadSpeed,
    localUpdateExists,
    localUpdateSize,
    downloaded,
    handleCheckUpdate,
    handleDownloadUpdate,
    handleApplyUpdate,
    handleCancelUpdate
  }
}
