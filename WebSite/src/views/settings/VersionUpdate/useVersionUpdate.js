import { ref, onMounted, computed, nextTick, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { API_CONFIG } from '@/config/api.js'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

export function useVersionUpdate() {
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
