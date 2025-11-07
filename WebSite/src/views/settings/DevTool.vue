<template>
  <div class="dev-tool-container">
    <!-- ADB证书管理区域 -->
    <div class="sync-section">
      <h2 class="section-title">ADB 设备管理 & Charles 证书安装</h2>
      
      <div class="sync-controls">
        <el-button 
          type="primary" 
          @click="scanAndLoadDevices"
          :loading="isLoadingDevices"
        >
          {{ isLoadingDevices ? '扫描中...' : '扫描局域网设备' }}
        </el-button>

        <el-select 
          v-model="selectedDevice" 
          placeholder="选择设备" 
          class="device-select"
          :disabled="devices.length === 0"
        >
          <el-option 
            v-for="device in devices" 
            :key="device.serial" 
            :label="`${device.model || '未知设备'} (${device.serial})`" 
            :value="device.serial"
          />
        </el-select>

        <el-button 
          type="warning" 
          @click="installCert"
          :disabled="!selectedDevice || isInstallingCert"
          :loading="isInstallingCert"
        >
          {{ isInstallingCert ? '安装中...' : '重新安装证书' }}
        </el-button>

        <el-button 
          type="danger" 
          @click="uninstallCert"
          :disabled="!selectedDevice || isUninstallingCert"
          :loading="isUninstallingCert"
        >
          {{ isUninstallingCert ? '卸载中...' : '卸载证书' }}
        </el-button>
      </div>

      <div v-if="deviceInfo && selectedDevice" class="device-info">
        <h3 class="info-title">设备信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">设备序列号:</span>
            <span class="info-value">{{ deviceInfo.serial || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">连接地址:</span>
            <span class="info-value">{{ deviceInfo.connection || deviceInfo.serial || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">设备型号:</span>
            <span class="info-value">{{ deviceInfo.model || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Android版本:</span>
            <span class="info-value">{{ deviceInfo.android_version || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">SDK版本:</span>
            <span class="info-value">{{ deviceInfo.sdk_version || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Root权限:</span>
            <span class="info-value" :class="deviceInfo.is_root ? 'success-text' : 'error-text'">
              {{ deviceInfo.is_root ? '✓ 已获取' : '✗ 未获取' }}
            </span>
          </div>
        </div>
      </div>

      <div v-if="certStatus" class="cert-status-info">
        <h3 class="info-title">证书状态</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">证书状态:</span>
            <span class="info-value" :class="certStatus.installed ? 'success-text' : 'warning-text'">
              {{ certStatus.installed ? '✓ 已安装' : '✗ 未安装' }}
            </span>
          </div>
          <div class="info-item" v-if="certStatus.cert_info">
            <span class="info-label">证书Hash:</span>
            <span class="info-value">{{ certStatus.cert_info.cert_hash || '未知' }}</span>
          </div>
          <div class="info-item" v-if="certStatus.cert_info">
            <span class="info-label">证书文件名:</span>
            <span class="info-value">{{ certStatus.cert_info.cert_filename || '未知' }}</span>
          </div>
        </div>
      </div>

      <div v-if="adbMessage" class="sync-info" :class="adbMessageType">
        <span class="sync-time">{{ adbMessage }}</span>
      </div>
    </div>

    <!-- 饰品映射同步区域 -->
    <div class="sync-section">
        <h2 class="section-title">平台饰品映射</h2>
        
        <div class="sync-controls">
          <el-select 
            v-model="selectedSteamId" 
            placeholder="选择 Steam ID" 
            class="steam-id-select"
            :disabled="isSyncing || isSyncingBuff"
          >
            <el-option 
              v-for="item in steamIdList" 
              :key="item.steamID || item.steam_id" 
              :label="`${item.dataName || '未命名'} (${item.steamID || item.steam_id || '无ID'})`" 
              :value="item.steamID || item.steam_id"
            />
          </el-select>
          
          <el-button 
            type="success" 
            @click="syncWeaponTemplates"
            :disabled="!selectedSteamId || isSyncing || isSyncingBuff"
            :loading="isSyncing"
          >
            {{ isSyncing ? '同步中...' : '获取悠悠有品饰品映射' }}
          </el-button>
          
          <el-button 
            type="success" 
            @click="syncBuffTemplates"
            :disabled="!selectedSteamId || isSyncing || isSyncingBuff"
            :loading="isSyncingBuff"
          >
            {{ isSyncingBuff ? '同步中...' : '获取BUFF饰品映射' }}
          </el-button>

          <el-button 
            type="primary" 
            @click="collectHashNamesFull"
            disabled
          >
            获取Steam饰品哈希
          </el-button>

          <el-button 
            type="warning" 
            @click="startCsqaqCrawlAll"
            disabled
          >
            全量采集 CSQAQ 商品
          </el-button>
        </div>
        
        <div v-if="lastSyncTime" class="sync-info">
          <span class="sync-time">最后同步时间: {{ lastSyncTime }}</span>
        </div>

        <div v-if="lastCollectTime" class="sync-info" style="margin-top: 0.5rem;">
          <span class="sync-time">最后采集时间: {{ lastCollectTime }}</span>
        </div>

        <div v-if="collectProgress" class="progress-info">
          <div class="progress-item">
            <span class="progress-label">采集进度:</span>
            <span class="progress-value">
              {{ collectProgress.total_success || 0 }} / {{ collectProgress.total_collected || 0 }}
            </span>
          </div>
          <div class="progress-item">
            <span class="progress-label">成功率:</span>
            <span class="progress-value success-rate">
              {{ collectProgress.success_rate || 0 }}%
            </span>
          </div>
        </div>

        <div v-if="csqaqStatus.message" class="sync-info" style="margin-top: 0.5rem;">
          <div class="status-row">
            <span class="status-label">消息:</span>
            <span class="status-value">{{ csqaqStatus.message }}</span>
          </div>
          <div v-if="csqaqStatus.total_goods > 0" class="status-row">
            <span class="status-label">已获取:</span>
            <span class="status-value highlight">{{ csqaqStatus.total_goods }} 个商品</span>
          </div>
          <div v-if="csqaqStatus.duration" class="status-row">
            <span class="status-label">耗时:</span>
            <span class="status-value">{{ csqaqStatus.duration.toFixed(2) }} 秒</span>
          </div>
        </div>
        
        <div v-if="lastCsqaqTime" class="sync-info" style="margin-top: 0.5rem;">
          <span class="sync-time">最后采集时间: {{ lastCsqaqTime }}</span>
        </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { API_CONFIG, apiUrls } from '@/config/api.js'

export default {
  name: 'DevTool',
  setup() {
    // ADB设备管理相关状态
    const devices = ref([])
    const selectedDevice = ref('')
    const deviceInfo = ref(null)
    const certStatus = ref(null)
    const isLoadingDevices = ref(false)
    const isCheckingCert = ref(false)
    const isInstallingCert = ref(false)
    const isUninstallingCert = ref(false)
    const adbMessage = ref('')
    const adbMessageType = ref('info')

    const selectedSteamId = ref('')
    const steamIdList = ref([])
    const isSyncing = ref(false)
    const isSyncingBuff = ref(false)
    const lastSyncTime = ref('')
    
    // Steam Hash Names 相关状态
    const isCollectingHashNames = ref(false)
    const lastCollectTime = ref('')
    const collectProgress = ref(null)

    // CSQAQ 相关状态
    const isCrawlingCsqaq = ref(false)
    const csqaqStatus = ref({
      status: 'idle',
      message: '',
      total_goods: 0,
      duration: null
    })
    const lastCsqaqTime = ref('')

    // ========== ADB设备管理功能 ==========
    
    // 扫描并加载设备
    const scanAndLoadDevices = async () => {
      isLoadingDevices.value = true
      adbMessage.value = ''
      
      try {
        // 1. 先扫描局域网设备
        adbMessage.value = '正在扫描局域网设备...'
        adbMessageType.value = 'info'
        
        const scanResponse = await axios.post(apiUrls.adbScan(), {
          timeout: 0.5,
          max_workers: 50
        })
        
        if (scanResponse.data.success && scanResponse.data.data.length > 0) {
          const discovered = scanResponse.data.data
          ElMessage.success(`发现 ${discovered.length} 个设备，正在连接...`)
          
          // 2. 连接发现的设备
          for (const address of discovered.slice(0, 3)) {  // 最多连接3个
            try {
              await axios.post(apiUrls.adbConnect(), { address })
            } catch (e) {
              console.warn(`连接设备 ${address} 失败:`, e)
            }
          }
          
          // 等待连接完成
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
        
        // 3. 获取设备列表
        const response = await axios.get(apiUrls.adbDevices())
        
        if (response.data.success) {
          devices.value = response.data.data
          
          if (devices.value.length > 0) {
            // 默认选择第一个设备
            if (!selectedDevice.value) {
              selectedDevice.value = devices.value[0].serial
              deviceInfo.value = devices.value[0]
            } else {
              // 更新已选设备的信息
              const selected = devices.value.find(d => d.serial === selectedDevice.value)
              if (selected) {
                deviceInfo.value = selected
              }
            }
            
            adbMessage.value = `找到 ${devices.value.length} 个设备`
            adbMessageType.value = 'success'
            ElMessage.success(response.data.message)
            
            // 自动检测证书状态
            await checkCertStatus()
          } else {
            adbMessage.value = '未找到任何设备。请确保：\n1. 设备已开启ADB调试\n2. MuMu模拟器已启动'
            adbMessageType.value = 'warning'
            ElMessage.warning('未找到任何设备')
          }
        } else {
          adbMessage.value = `获取设备失败: ${response.data.message}`
          adbMessageType.value = 'error'
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('扫描设备失败:', error)
        adbMessage.value = '扫描设备失败，请确保后端服务正在运行'
        adbMessageType.value = 'error'
        
        let errorMessage = '扫描设备失败'
        if (error.response) {
          errorMessage = error.response.data?.message || errorMessage
        } else if (error.request) {
          errorMessage = '无法连接到后端服务器'
        }
        ElMessage.error(errorMessage)
      } finally {
        isLoadingDevices.value = false
      }
    }

    // 检查证书状态（静默模式，不显示成功消息）
    const checkCertStatus = async (silent = false) => {
      if (!selectedDevice.value) {
        if (!silent) {
          ElMessage.warning('请先选择设备')
        }
        return
      }

      isCheckingCert.value = true
      if (!silent) {
        adbMessage.value = ''
      }

      try {
        const response = await axios.post(apiUrls.adbCertStatus(), {
          serial: selectedDevice.value
        })

        if (response.data.success) {
          certStatus.value = response.data.data
          if (!silent) {
            adbMessage.value = response.data.message
            adbMessageType.value = certStatus.value.installed ? 'success' : 'warning'
            ElMessage.success(response.data.message)
          }
        } else {
          if (!silent) {
            adbMessage.value = `检查失败: ${response.data.message}`
            adbMessageType.value = 'error'
            ElMessage.error(response.data.message)
          }
        }
      } catch (error) {
        console.error('检查证书状态失败:', error)
        if (!silent) {
          adbMessage.value = '检查证书状态失败'
          adbMessageType.value = 'error'
          
          let errorMessage = '检查证书状态失败'
          if (error.response) {
            errorMessage = error.response.data?.message || errorMessage
          }
          ElMessage.error(errorMessage)
        }
      } finally {
        isCheckingCert.value = false
      }
    }

    // 安装证书（强制重新安装）
    const installCert = async () => {
      if (!selectedDevice.value) {
        ElMessage.warning('请先选择设备')
        return
      }

      // 检查设备是否有root权限
      if (deviceInfo.value && !deviceInfo.value.is_root) {
        ElMessage.error('设备没有root权限，无法安装系统证书')
        return
      }

      try {
        const message = certStatus.value?.installed 
          ? '证书已安装，确定要重新安装Charles证书吗？此操作将覆盖现有证书。'
          : '确定要安装Charles证书到设备吗？此操作需要root权限。'
        
        await ElMessageBox.confirm(message, '确认安装', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
      } catch {
        return
      }

      isInstallingCert.value = true
      adbMessage.value = ''
      ElMessage.info('开始安装证书...')

      try {
        const response = await axios.post(apiUrls.adbCertInstall(), {
          serial: selectedDevice.value,
          force: true  // 强制重新安装
        })

        if (response.data.success) {
          adbMessage.value = '证书安装成功！建议重启设备以确保证书生效'
          adbMessageType.value = 'success'
          ElMessage.success(response.data.message)
          
          // 刷新证书状态
          setTimeout(() => {
            checkCertStatus(true)  // 静默检查
          }, 1000)
        } else {
          adbMessage.value = `安装失败: ${response.data.message}`
          adbMessageType.value = 'error'
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('安装证书失败:', error)
        adbMessage.value = '安装证书失败'
        adbMessageType.value = 'error'
        
        let errorMessage = '安装证书失败'
        if (error.response) {
          errorMessage = error.response.data?.message || errorMessage
        }
        ElMessage.error(errorMessage)
      } finally {
        isInstallingCert.value = false
      }
    }

    // 卸载证书
    const uninstallCert = async () => {
      if (!selectedDevice.value) {
        ElMessage.warning('请先选择设备')
        return
      }

      try {
        await ElMessageBox.confirm(
          '确定要卸载Charles证书吗？',
          '确认卸载',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch {
        return
      }

      isUninstallingCert.value = true
      adbMessage.value = ''
      ElMessage.info('开始卸载证书...')

      try {
        const response = await axios.post(apiUrls.adbCertUninstall(), {
          serial: selectedDevice.value
        })

        if (response.data.success) {
          adbMessage.value = '证书卸载成功'
          adbMessageType.value = 'success'
          ElMessage.success(response.data.message)
          
          // 刷新证书状态
          setTimeout(() => {
            checkCertStatus(true)  // 静默检查
          }, 1000)
        } else {
          adbMessage.value = `卸载失败: ${response.data.message}`
          adbMessageType.value = 'error'
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('卸载证书失败:', error)
        adbMessage.value = '卸载证书失败'
        adbMessageType.value = 'error'
        
        let errorMessage = '卸载证书失败'
        if (error.response) {
          errorMessage = error.response.data?.message || errorMessage
        }
        ElMessage.error(errorMessage)
      } finally {
        isUninstallingCert.value = false
      }
    }

    // ========== Steam ID 和饰品映射功能 ==========

    // 加载Steam ID列表
    const loadSteamIdList = async () => {
      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/webInventoryV1/steam_ids`)
        if (response.data.success && response.data.data.length > 0) {
          steamIdList.value = response.data.data
          console.log('已加载 Steam ID 列表:', steamIdList.value)
          // 默认选择第一个
          if (!selectedSteamId.value && steamIdList.value.length > 0) {
            const firstItem = steamIdList.value[0]
            selectedSteamId.value = firstItem.steamID || firstItem.steam_id || ''
          }
        }
      } catch (error) {
        console.error('加载Steam ID列表失败:', error)
        ElMessage.error('加载Steam ID列表失败')
      }
    }

    // 同步悠悠有品饰品映射
    const syncWeaponTemplates = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择 Steam ID')
        return
      }

      if (isSyncing.value) {
        return
      }

      try {
        await ElMessageBox.confirm(
          `确定要同步 Steam ID: ${selectedSteamId.value} 的悠悠有品饰品映射吗？此操作可能需要一些时间。`,
          '确认同步',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch {
        return
      }

      isSyncing.value = true
      ElMessage.info('开始同步饰品映射...')
      
      try {
        console.log('开始同步悠悠有品饰品映射, Steam ID:', selectedSteamId.value)
        
        const response = await axios.post(apiUrls.youpinSyncTemplates(), {
          steamId: selectedSteamId.value
        })

        if (response.data.success) {
          ElMessage.success(`同步成功！${response.data.message}`)
          console.log('同步结果:', response.data)
          lastSyncTime.value = new Date().toLocaleString('zh-CN')
        } else {
          ElMessage.error(`同步失败: ${response.data.message}`)
        }
      } catch (error) {
        console.error('同步饰品映射失败:', error)
        let errorMessage = '同步失败'
        
        if (error.response) {
          errorMessage = error.response.data?.message || `同步失败 (${error.response.status})`
        } else if (error.request) {
          errorMessage = '无法连接到爬虫服务器，请检查服务是否运行'
        } else {
          errorMessage = error.message || '同步失败'
        }
        
        ElMessage.error(errorMessage)
      } finally {
        isSyncing.value = false
      }
    }

    // 同步BUFF饰品映射
    const syncBuffTemplates = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择 Steam ID')
        return
      }

      if (isSyncingBuff.value) {
        return
      }

      try {
        await ElMessageBox.confirm(
          `确定要同步 Steam ID: ${selectedSteamId.value} 的BUFF饰品映射吗？此操作可能需要一些时间。`,
          '确认同步',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch {
        return
      }

      isSyncingBuff.value = true
      ElMessage.info('开始同步BUFF饰品映射...')

      try {
        console.log('开始同步BUFF饰品映射, Steam ID:', selectedSteamId.value)

        const response = await axios.post(apiUrls.buffSyncTemplates(), {
          steamId: selectedSteamId.value
        })

        if (response.data.success) {
          ElMessage.success(`同步成功！${response.data.message}`)
          console.log('同步结果:', response.data)
          lastSyncTime.value = new Date().toLocaleString('zh-CN')
        } else {
          ElMessage.error(`同步失败: ${response.data.message}`)
        }
      } catch (error) {
        console.error('同步BUFF饰品映射失败:', error)
        let errorMessage = '同步失败'

        if (error.response) {
          errorMessage = error.response.data?.message || `同步失败 (${error.response.status})`
        } else if (error.request) {
          errorMessage = '无法连接到爬虫服务器，请检查服务是否运行'
        } else {
          errorMessage = error.message || '同步失败'
        }

        ElMessage.error(errorMessage)
      } finally {
        isSyncingBuff.value = false
      }
    }

    // 完整采集Hash Names (全部)
    const collectHashNamesTest = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要采集Steam市场物品数据吗？测试模式将采集100条数据，预计需要2-3分钟。',
          '确认采集',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'info'
          }
        )
      } catch {
        return
      }

      isCollectingHashNames.value = true
      collectProgress.value = null
      ElMessage.info('开始采集Steam市场Hash Names (测试模式: 100条)...')

      try {
        const response = await axios.post(apiUrls.steamCollectHashNames(), {
          max_count: 100,
          batch_size: 50
        })

        if (response.data.success) {
          collectProgress.value = response.data.data
          lastCollectTime.value = new Date().toLocaleString('zh-CN')
          ElMessage.success(`采集完成！${response.data.message}`)
        } else {
          ElMessage.error(`采集失败: ${response.data.message}`)
        }
      } catch (error) {
        console.error('采集Hash Names失败:', error)
        let errorMessage = '采集失败'
        
        if (error.response) {
          errorMessage = error.response.data?.message || `采集失败 (${error.response.status})`
        } else if (error.request) {
          errorMessage = '无法连接到爬虫服务器，请检查服务是否运行'
        } else {
          errorMessage = error.message || '采集失败'
        }
        
        ElMessage.error(errorMessage)
      } finally {
        isCollectingHashNames.value = false
      }
    }

    // 完整采集Hash Names (全部)
    const collectHashNamesFull = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要完整采集Steam市场物品数据吗？这将采集约24000条数据，预计需要8-10分钟。期间请不要关闭页面。',
          '确认完整采集',
          {
            confirmButtonText: '确定采集',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch {
        return
      }

      isCollectingHashNames.value = true
      collectProgress.value = null
      ElMessage.info('开始完整采集Steam市场Hash Names，这可能需要较长时间，请耐心等待...')

      try {
        const response = await axios.post(apiUrls.steamCollectHashNames(), {
          batch_size: 100
        })

        if (response.data.success) {
          collectProgress.value = response.data.data
          lastCollectTime.value = new Date().toLocaleString('zh-CN')
          ElMessage.success(`采集完成！${response.data.message}`)
        } else {
          ElMessage.error(`采集失败: ${response.data.message}`)
        }
      } catch (error) {
        console.error('采集Hash Names失败:', error)
        let errorMessage = '采集失败'
        
        if (error.response) {
          errorMessage = error.response.data?.message || `采集失败 (${error.response.status})`
        } else if (error.request) {
          errorMessage = '无法连接到爬虫服务器，请检查服务是否运行'
        } else {
          errorMessage = error.message || '采集失败'
        }
        
        ElMessage.error(errorMessage)
      } finally {
        isCollectingHashNames.value = false
      }
    }

    // CSQAQ 全量采集
    const startCsqaqCrawlAll = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要全量采集 CSQAQ 商品数据吗？将爬取所有页面，预计需要较长时间。',
          '确认全量采集',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch {
        return
      }

      isCrawlingCsqaq.value = true
      ElMessage.info('开始全量采集 CSQAQ 商品数据...')

      try {
        const response = await axios.post(apiUrls.csqaqGetGoods(), {
          maxPages: null,  // 全量采集
          headless: true,  // 后台运行
          delayMin: 1,
          delayMax: 3,
          scrollLoad: true
        })

        if (response.data.success) {
          csqaqStatus.value = {
            status: 'completed',
            message: response.data.message,
            total_goods: response.data.data.total,
            duration: response.data.data.duration
          }
          lastCsqaqTime.value = new Date().toLocaleString('zh-CN')
          ElMessage.success(`全量采集成功！${response.data.message}`)
          console.log('CSQAQ全量采集结果:', response.data)
        } else {
          csqaqStatus.value = {
            status: 'error',
            message: response.data.message,
            total_goods: 0,
            duration: null
          }
          ElMessage.error(`采集失败: ${response.data.message}`)
        }
      } catch (error) {
        console.error('CSQAQ采集失败:', error)
        let errorMessage = '采集失败'

        if (error.response) {
          errorMessage = error.response.data?.message || `采集失败 (${error.response.status})`
        } else if (error.request) {
          errorMessage = '无法连接到爬虫服务器，请检查服务是否运行'
        } else {
          errorMessage = error.message || '采集失败'
        }

        csqaqStatus.value = {
          status: 'error',
          message: errorMessage,
          total_goods: 0,
          duration: null
        }
        ElMessage.error(errorMessage)
      } finally {
        isCrawlingCsqaq.value = false
      }
    }

    // 组件挂载时加载Steam ID列表
    onMounted(() => {
      loadSteamIdList()
    })

    return {
      // ADB设备管理
      devices,
      selectedDevice,
      deviceInfo,
      certStatus,
      isLoadingDevices,
      isCheckingCert,
      isInstallingCert,
      isUninstallingCert,
      adbMessage,
      adbMessageType,
      scanAndLoadDevices,
      checkCertStatus,
      installCert,
      uninstallCert,
      // Steam ID 和饰品映射
      selectedSteamId,
      steamIdList,
      isSyncing,
      isSyncingBuff,
      lastSyncTime,
      syncWeaponTemplates,
      syncBuffTemplates,
      // Steam Hash Names 相关
      isCollectingHashNames,
      lastCollectTime,
      collectProgress,
      collectHashNamesFull,
      // CSQAQ 相关
      isCrawlingCsqaq,
      csqaqStatus,
      lastCsqaqTime,
      startCsqaqCrawlAll
    }
  }
}
</script>

<style scoped>
.dev-tool-container {
  width: 100%;
  padding: 1rem;
  max-width: 1400px;
  margin: 0 auto;
}

.dev-title {
  font-size: 2rem;
  font-weight: bold;
  color: #4CAF50;
  margin-bottom: 0.5rem;
  text-align: center;
}

.dev-subtitle {
  text-align: center;
  color: #888;
  margin-bottom: 2rem;
  font-size: 0.9rem;
}

.sync-section {
  background-color: #2a2a2a;
  padding: 1.5rem;
  border-radius: 0.75rem;
  border: 1px solid #444;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #444;
}

.sync-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.steam-id-select {
  width: 200px;
  min-width: 180px;
}

.device-select {
  width: 300px;
  min-width: 280px;
}

.sync-info {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: rgba(76, 175, 80, 0.1);
  border-radius: 0.5rem;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.sync-info.success {
  background-color: rgba(76, 175, 80, 0.1);
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.sync-info.warning {
  background-color: rgba(230, 162, 60, 0.1);
  border: 1px solid rgba(230, 162, 60, 0.3);
}

.sync-info.error {
  background-color: rgba(245, 108, 108, 0.1);
  border: 1px solid rgba(245, 108, 108, 0.3);
}

.sync-info.info {
  background-color: rgba(64, 158, 255, 0.1);
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.device-info,
.cert-status-info {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #1e1e1e;
  border-radius: 0.5rem;
  border: 1px solid #444;
}

.info-title {
  font-size: 1rem;
  font-weight: 600;
  color: #4CAF50;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #444;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background-color: #2a2a2a;
  border-radius: 0.25rem;
}

.info-label {
  color: #888;
  font-size: 0.875rem;
  font-weight: 500;
}

.info-value {
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
}

.info-value.success-text {
  color: #4CAF50;
}

.info-value.error-text {
  color: #F56C6C;
}

.info-value.warning-text {
  color: #E6A23C;
}

.sync-time {
  color: #4CAF50;
  font-size: 0.875rem;
}

.tool-description {
  margin-bottom: 1rem;
  padding: 1rem;
  background-color: rgba(64, 158, 255, 0.05);
  border-radius: 0.5rem;
  border-left: 3px solid #409EFF;
}

.tool-desc-text {
  color: #aaa;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}

/* Element Plus 组件深色主题适配 */
:deep(.el-input__wrapper) {
  background-color: #1e1e1e;
  box-shadow: 0 0 0 1px #444 inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4CAF50 inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #4CAF50 inset !important;
}

:deep(.el-input__inner) {
  color: #fff;
}

:deep(.el-select .el-input__wrapper) {
  background-color: #1e1e1e;
}

:deep(.el-button) {
  font-size: 0.875rem;
  padding: 0.625rem 1rem;
}

/* CSQAQ 控制区域 */
.csqaq-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.control-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.control-label {
  color: #aaa;
  font-size: 0.875rem;
}

.page-input {
  width: 150px;
}

.status-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.status-label {
  color: #888;
  min-width: 60px;
  font-weight: 500;
}

.status-value {
  color: #fff;
}

.status-value.running {
  color: #409EFF;
  font-weight: 600;
}

.status-value.completed {
  color: #67C23A;
  font-weight: 600;
}

.status-value.error {
  color: #F56C6C;
  font-weight: 600;
}

.status-value.highlight {
  color: #E6A23C;
  font-weight: 600;
  font-size: 1.1rem;
}

/* 进度信息样式 */
.progress-info {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: rgba(64, 158, 255, 0.1);
  border-radius: 0.5rem;
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.progress-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.progress-item:last-child {
  margin-bottom: 0;
}

.progress-label {
  color: #888;
  font-size: 0.875rem;
}

.progress-value {
  color: #409EFF;
  font-weight: 600;
}

.progress-value.success-rate {
  color: #67C23A;
}

/* Element Plus 组件样式 */
:deep(.el-input-number) {
  background-color: #1e1e1e;
}

:deep(.el-input-number .el-input__wrapper) {
  background-color: #1e1e1e;
  box-shadow: 0 0 0 1px #444 inset;
}

:deep(.el-input-number .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4CAF50 inset;
}

:deep(.el-switch) {
  --el-switch-on-color: #4CAF50;
  --el-switch-off-color: #555;
}

:deep(.el-switch__core) {
  border-color: #444;
}

:deep(.el-switch__label) {
  color: #aaa;
}

:deep(.el-switch__label.is-active) {
  color: #4CAF50;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dev-tool-container {
    padding: 0.5rem;
  }

  .dev-title {
    font-size: 1.5rem;
  }

  .sync-section {
    padding: 1rem;
  }

  .section-title {
    font-size: 1.1rem;
  }

  .sync-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .steam-id-select {
    width: 100%;
  }

  .sync-controls .el-button {
    width: 100%;
  }

  .control-row {
    flex-direction: column;
    align-items: stretch;
  }

  .page-input {
    width: 100%;
  }

  .control-row .el-button {
    width: 100%;
  }
}
</style>

