import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api'

export function useAESDecrypt() {
  // 表单数据
  const decryptMode = ref('response') // 'request' 或 'response'
  const skHeader = ref('')
  const encryptedBody = ref('')
  const decryptedResult = ref(null)
  const decryptedJson = ref('')

  // UI状态
  const loading = ref(false)
  const isAuthorized = ref(null)
  const macAddresses = ref([])

  // 检查license授权状态
  const checkLicense = async () => {
    try {
      const url = apiUrls.aesCheckLicense()
      const response = await fetch(url)
      const result = await response.json()

      if (result.success) {
        isAuthorized.value = result.authorized
        macAddresses.value = result.mac_addresses || []

        if (!result.authorized) {
          ElMessage.warning({
            message: '当前机器未授权，无法使用AES解密功能',
            duration: 5000
          })
        }
      } else {
        ElMessage.error('检查授权状态失败: ' + result.error)
      }
    } catch (error) {
      console.error('检查license失败:', error)
      ElMessage.error('检查授权状态失败: ' + error.message)
    }
  }

  // 解密数据
  const handleDecrypt = async () => {
    // 验证输入
    if (!skHeader.value.trim()) {
      ElMessage.warning('请输入SK头')
      return
    }

    if (!encryptedBody.value.trim()) {
      ElMessage.warning('请输入加密数据')
      return
    }

    // 检查授权
    if (isAuthorized.value === false) {
      ElMessage.error('当前机器未授权，无法使用此功能')
      return
    }

    loading.value = true

    try {
      const url = apiUrls.aesDecrypt()
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          sk_header: skHeader.value.trim(),
          encrypted_body: encryptedBody.value.trim(),
          decrypt_mode: decryptMode.value // 传递解密模式
        })
      })

      const result = await response.json()

      if (result.success) {
        decryptedResult.value = result.data
        decryptedJson.value = JSON.stringify(result.data, null, 2)

        ElMessage.success('解密成功！')
      } else {
        // 处理不同类型的错误
        if (result.error_type === 'license_error') {
          ElMessage.error({
            message: '授权验证失败: ' + result.error,
            duration: 5000
          })
          // 重新检查授权状态
          await checkLicense()
        } else if (result.error_type === 'value_error') {
          ElMessage.error('参数错误: ' + result.error)
        } else if (result.error_type === 'json_error') {
          ElMessage.error('JSON解析错误: ' + result.error)
        } else {
          ElMessage.error('解密失败: ' + result.error)
        }

        decryptedResult.value = null
        decryptedJson.value = ''
      }
    } catch (error) {
      console.error('解密请求失败:', error)
      ElMessage.error('解密请求失败: ' + error.message)
      decryptedResult.value = null
      decryptedJson.value = ''
    } finally {
      loading.value = false
    }
  }

  // 清空表单
  const handleClear = () => {
    skHeader.value = ''
    encryptedBody.value = ''
    decryptedResult.value = null
    decryptedJson.value = ''
  }

  // 复制结果
  const handleCopy = async () => {
    if (!decryptedJson.value) {
      ElMessage.warning('没有可复制的内容')
      return
    }

    try {
      await navigator.clipboard.writeText(decryptedJson.value)
      ElMessage.success('已复制到剪贴板')
    } catch (error) {
      console.error('复制失败:', error)
      ElMessage.error('复制失败: ' + error.message)
    }
  }

  // 下载结果
  const handleDownload = () => {
    if (!decryptedJson.value) {
      ElMessage.warning('没有可下载的内容')
      return
    }

    try {
      const blob = new Blob([decryptedJson.value], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `decrypted_${Date.now()}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      ElMessage.success('下载成功')
    } catch (error) {
      console.error('下载失败:', error)
      ElMessage.error('下载失败: ' + error.message)
    }
  }

  // 格式化JSON
  const formatJson = () => {
    if (!decryptedJson.value) {
      return
    }

    try {
      const parsed = JSON.parse(decryptedJson.value)
      decryptedJson.value = JSON.stringify(parsed, null, 2)
    } catch (error) {
      ElMessage.error('JSON格式化失败: ' + error.message)
    }
  }

  // 组件挂载时检查授权
  onMounted(() => {
    checkLicense()
  })

  return {
    // 数据
    decryptMode,
    skHeader,
    encryptedBody,
    decryptedResult,
    decryptedJson,

    // 状态
    loading,
    isAuthorized,
    macAddresses,

    // 方法
    handleDecrypt,
    handleClear,
    handleCopy,
    handleDownload,
    formatJson,
    checkLicense
  }
}
