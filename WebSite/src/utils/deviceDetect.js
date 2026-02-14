/**
 * 设备类型检测工具
 * 用于判断当前设备类型并返回相应的标识
 */

/**
 * 获取设备类型
 * @returns {string} 设备类型: 'desktop' | 'ipad' | 'mobile'
 */
export function getDeviceType() {
  const ua = navigator.userAgent.toLowerCase()
  const width = window.innerWidth
  const height = window.innerHeight

  // 检测是否为 iPad
  const isIPad = /ipad/.test(ua) ||
                 (navigator.maxTouchPoints && navigator.maxTouchPoints > 2 && /macintosh/.test(ua))

  // 检测是否为移动设备
  const isMobile = /android|webos|iphone|ipod|blackberry|iemobile|opera mini/.test(ua)

  // 根据屏幕宽度判断
  if (isIPad || (width >= 768 && width <= 1366 && !isMobile)) {
    return 'ipad'
  } else if (isMobile || width < 768) {
    return 'mobile'
  } else {
    return 'desktop'
  }
}

/**
 * 获取设备详细信息
 * @returns {Object} 设备信息对象
 */
export function getDeviceInfo() {
  const deviceType = getDeviceType()
  const width = window.innerWidth
  const height = window.innerHeight
  const ua = navigator.userAgent

  return {
    deviceType,
    width,
    height,
    userAgent: ua,
    isIPad: deviceType === 'ipad',
    isMobile: deviceType === 'mobile',
    isDesktop: deviceType === 'desktop'
  }
}

/**
 * 应用设备类型到 body 元素
 * 会添加 'device-desktop' | 'device-ipad' | 'device-mobile' 类
 */
export function applyDeviceClass() {
  const deviceType = getDeviceType()
  const body = document.body

  // 移除所有设备类型类
  body.classList.remove('device-desktop', 'device-ipad', 'device-mobile')

  // 添加当前设备类型类
  body.classList.add(`device-${deviceType}`)

  return deviceType
}

/**
 * 监听窗口大小变化,自动更新设备类型
 */
export function watchDeviceType(callback) {
  let currentDeviceType = getDeviceType()

  const handleResize = () => {
    const newDeviceType = getDeviceType()

    if (newDeviceType !== currentDeviceType) {
      currentDeviceType = newDeviceType
      applyDeviceClass()

      if (callback && typeof callback === 'function') {
        callback(newDeviceType)
      }
    }
  }

  window.addEventListener('resize', handleResize)

  // 初始化时应用一次
  applyDeviceClass()

  // 返回取消监听的函数
  return () => {
    window.removeEventListener('resize', handleResize)
  }
}
