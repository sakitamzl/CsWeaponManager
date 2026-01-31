<template>
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
</template>

<script>
import { watch } from 'vue'
import useAdbCertForm from './useAdbCertForm.js'

export default {
  name: 'AdbCertForm',
  setup() {
    const form = useAdbCertForm()
    
    // 监听设备选择变化
    watch(() => form.selectedDevice.value, () => {
      if (form.selectedDevice.value && form.devices.value.length > 0) {
        const selected = form.devices.value.find(d => d.serial === form.selectedDevice.value)
        if (selected) {
          form.deviceInfo.value = selected
          form.checkCertStatus(true)  // 自动检查证书状态
        }
      }
    })
    
    return form
  }
}
</script>
<style scoped src="./styles.css"></style>
