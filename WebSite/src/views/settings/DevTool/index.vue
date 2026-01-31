<template>
  <div class="dev-tool-container">
    <!-- ADB证书管理区域 -->
    <div class="sync-section">
      <h2 class="section-title">ADB 与网络证书安装</h2>
      
      <div class="sync-controls">
        <el-button 
          type="primary" 
          @click="scanAndLoadDevices"
          :loading="isLoadingDevices"
        >
          {{ isLoadingDevices ? '扫描中...' : '扫描局域网设备' }}
        </el-button>

        <el-button 
          type="success" 
          @click="connectManualDevice"
          :disabled="isConnectingManual"
          :loading="isConnectingManual"
        >
          手动连接设备
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
          <template v-if="isInstallingCert">安装中...</template>
          <template v-else-if="certStatus && certStatus.installed">重新安装证书</template>
          <template v-else>安装证书</template>
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
          <!-- 悠悠有品饰品映射 -->
          <div class="control-group">
            <el-select 
              v-model="selectedSteamIdYoupin" 
              placeholder="选择 Steam ID" 
              class="steam-id-select"
              :disabled="isSyncing"
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
              :disabled="!selectedSteamIdYoupin || isSyncing"
              :loading="isSyncing"
            >
              {{ isSyncing ? '同步中...' : '获取悠悠有品饰品映射' }}
            </el-button>
          </div>
          
          <!-- BUFF饰品映射 -->
          <div class="control-group">
            <el-select 
              v-model="selectedSteamIdBuff" 
              placeholder="选择 Steam ID" 
              class="steam-id-select"
              :disabled="isSyncingBuff"
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
              @click="syncBuffTemplates"
              :disabled="!selectedSteamIdBuff || isSyncingBuff"
              :loading="isSyncingBuff"
            >
              {{ isSyncingBuff ? '同步中...' : '获取BUFF饰品映射' }}
            </el-button>
          </div>

          <!-- CSQAQ商品采集 -->
          <div class="control-group">
            <el-upload
              ref="csqaqUploadRef"
              :action="apiUrls.csqaqUploadMapping()"
              :auto-upload="false"
              :show-file-list="true"
              :limit="1"
              accept=".txt"
              :on-change="handleCsqaqFileChange"
              :on-success="handleCsqaqUploadSuccess"
              :on-error="handleCsqaqUploadError"
              :before-upload="beforeCsqaqUpload"
            >
              <el-button
                type="success"
                :loading="isUploadingCsqaq"
              >
                {{ isUploadingCsqaq ? '上传中...' : '选择CSQAQ映射文件' }}
              </el-button>
            </el-upload>
            <el-button
              type="primary"
              @click="submitCsqaqUpload"
              :disabled="!csqaqFileSelected || isUploadingCsqaq"
              :loading="isUploadingCsqaq"
            >
              {{ isUploadingCsqaq ? '处理中...' : '提交上传' }}
            </el-button>
          </div>
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

        <div v-if="csqaqUploadResult" class="sync-info" style="margin-top: 1rem;">
          <div class="status-row">
            <span class="status-label">上传结果:</span>
            <span class="status-value" :class="csqaqUploadResult.success ? 'success-text' : 'error'">
              {{ csqaqUploadResult.message }}
            </span>
          </div>
          <div v-if="csqaqUploadResult.total > 0" class="status-row">
            <span class="status-label">总记录数:</span>
            <span class="status-value">{{ csqaqUploadResult.total }}</span>
          </div>
          <div v-if="csqaqUploadResult.updated > 0" class="status-row">
            <span class="status-label">更新:</span>
            <span class="status-value success-text">{{ csqaqUploadResult.updated }}</span>
          </div>
          <div v-if="csqaqUploadResult.inserted > 0" class="status-row">
            <span class="status-label">新增:</span>
            <span class="status-value success-text">{{ csqaqUploadResult.inserted }}</span>
          </div>
          <div v-if="csqaqUploadResult.failed > 0" class="status-row">
            <span class="status-label">失败:</span>
            <span class="status-value error">{{ csqaqUploadResult.failed }}</span>
          </div>
        </div>
    </div>

    <!-- 图片资源包 -->
    <div class="sync-section">
      <h2 class="section-title">图片资源包</h2>

      <div class="sync-controls">
        <el-button
          type="primary"
          @click="downloadWeaponIcons"
          :loading="isDownloadingIcons"
        >
          {{ isDownloadingIcons ? '下载中...' : '下载武器图标' }}
        </el-button>
      </div>

      <div v-if="iconDownloadResult" class="sync-info" style="margin-top: 1rem;">
        <div class="status-row">
          <span class="status-label">本次待处理:</span>
          <span class="status-value">{{ iconDownloadResult.total }}</span>
        </div>
        <div class="status-row">
          <span class="status-label">成功下载:</span>
          <span class="status-value success-text">{{ iconDownloadResult.downloaded }}</span>
        </div>
        <div class="status-row">
          <span class="status-label">跳过/失败:</span>
          <span class="status-value">
            {{ iconDownloadResult.skipped }} / {{ iconDownloadResult.failed }}
          </span>
        </div>
        <div class="status-row">
          <span class="status-label">剩余待下载:</span>
          <span class="status-value">{{ iconDownloadResult.pending_remaining }}</span>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { useDevTool } from './useDevTool.js'

export default {
  name: 'DevTool',
  setup() {
    return useDevTool()
  }
}
</script>

<style scoped src="./styles.css"></style>
