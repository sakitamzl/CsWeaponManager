<template>
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
</template>

<script>
import useImageResourceForm from './useImageResourceForm.js'

export default {
  name: 'ImageResourceForm',
  setup() {
    return useImageResourceForm()
  }
}
</script>
<style scoped src="./styles.css"></style>
