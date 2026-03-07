<template>
  <div class="sync-section">
    <h2 class="section-title">平台饰品映射</h2>
    
    <div class="sync-controls">
      <!-- 悠悠有品饰品映射（key1=youpin key2=config 的账号） -->
      <div class="control-group">
        <el-select 
          v-model="selectedSteamIdYoupin" 
          placeholder="选择悠悠有品账号" 
          class="steam-id-select"
          :disabled="isSyncing"
        >
          <el-option 
            v-for="item in youpinConfigList" 
            :key="item.dataID + '_' + (item.steamID || '')" 
            :label="`${item.dataName || '未命名'} (${item.steamID || '无ID'})`" 
            :value="item.steamID || ''"
          />
        </el-select>
        
        <el-button 
          class="mapping-btn"
          type="success" 
          @click="syncWeaponTemplates"
          :disabled="!selectedSteamIdYoupin || isSyncing"
          :loading="isSyncing"
        >
          {{ isSyncing ? '同步中...' : '获取悠悠有品饰品映射' }}
        </el-button>
      </div>
      
      <!-- BUFF饰品映射（key1=buff key2=config 的账号） -->
      <div class="control-group">
        <el-select 
          v-model="selectedSteamIdBuff" 
          placeholder="选择BUFF账号" 
          class="steam-id-select"
          :disabled="isSyncingBuff"
        >
          <el-option 
            v-for="item in buffConfigList" 
            :key="item.dataID + '_' + (item.steamID || '')" 
            :label="`${item.dataName || '未命名'} (${item.steamID || '无ID'})`" 
            :value="item.steamID || ''"
          />
        </el-select>
        
        <el-button 
          class="mapping-btn"
          type="success" 
          @click="syncBuffTemplates"
          :disabled="!selectedSteamIdBuff || isSyncingBuff"
          :loading="isSyncingBuff"
        >
          {{ isSyncingBuff ? '同步中...' : '获取BUFF饰品映射' }}
        </el-button>
      </div>

      <!-- CSQAQ商品采集 -->
      <div class="control-group csqaq-group">
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
          class="csqaq-upload-inline"
        >
          <el-button
            class="csqaq-btn"
            type="success"
            :loading="isUploadingCsqaq"
          >
            {{ isUploadingCsqaq ? '上传中...' : '选择CSQAQ映射文件' }}
          </el-button>
        </el-upload>
        <el-button
          class="csqaq-btn"
          type="primary"
          @click="submitCsqaqUpload"
          :disabled="!csqaqFileSelected || isUploadingCsqaq"
          :loading="isUploadingCsqaq"
        >
          {{ isUploadingCsqaq ? '处理中...' : '提交上传' }}
        </el-button>
        <span class="csqaq-file-path">
          文件获取方法：
          <a href="https://docs.csqaq.com/api-337690892" target="_blank" rel="noopener noreferrer">获取全量站内饰品ID - CSQAQ API 文档</a>
        </span>
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
</template>

<script>
import useWeaponMappingForm from './useWeaponMappingForm.js'

export default {
  name: 'WeaponMappingForm',
  setup() {
    return useWeaponMappingForm()
  }
}
</script>
<style scoped src="./styles.css"></style>
