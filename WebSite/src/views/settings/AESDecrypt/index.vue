<template>
  <div class="aes-decrypt-container">
    <!-- 未授权提示 -->
    <el-alert
      v-if="isAuthorized === false"
      title="未授权"
      type="warning"
      :closable="false"
      show-icon
      class="auth-alert"
    >
      <template #default>
        <div>
          <p>当前机器未授权，无法使用AES解密功能。</p>
          <p v-if="macAddresses.length > 0" class="mac-info">
            本机MAC地址: {{ macAddresses.join(', ') }}
          </p>
        </div>
      </template>
    </el-alert>

    <!-- 输入区域 -->
    <el-card class="input-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>输入加密数据</span>
          <el-button
            type="primary"
            size="small"
            :loading="loading"
            :disabled="isAuthorized === false"
            @click="handleDecrypt"
          >
            <el-icon><Unlock /></el-icon>
            解密
          </el-button>
        </div>
      </template>

      <el-form label-position="top">
        <el-form-item label="解密类型">
          <el-radio-group v-model="decryptMode" :disabled="isAuthorized === false">
            <el-radio value="response">响应体</el-radio>
            <el-radio value="request">请求体</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="SK头">
          <el-input
            v-model="skHeader"
            type="textarea"
            :rows="3"
            placeholder=""
            :disabled="isAuthorized === false"
          />
        </el-form-item>

        <el-form-item label="加密数据">
          <el-input
            v-model="encryptedBody"
            type="textarea"
            :rows="8"
            placeholder=""
            :disabled="isAuthorized === false"
          />
        </el-form-item>

        <el-form-item>
          <el-space>
            <el-button
              type="primary"
              :loading="loading"
              :disabled="isAuthorized === false"
              @click="handleDecrypt"
            >
              <el-icon><Unlock /></el-icon>
              解密
            </el-button>
            <el-button @click="handleClear">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 结果区域 -->
    <el-card v-if="decryptedJson" class="result-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>解密结果</span>
          <el-space>
            <el-button
              type="success"
              size="small"
              @click="handleCopy"
            >
              <el-icon><DocumentCopy /></el-icon>
              复制
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="handleDownload"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button
              size="small"
              @click="formatJson"
            >
              <el-icon><Operation /></el-icon>
              格式化
            </el-button>
          </el-space>
        </div>
      </template>

      <div class="json-viewer">
        <pre>{{ decryptedJson }}</pre>
      </div>
    </el-card>

  </div>
</template>

<script setup>
import { Unlock, Delete, Refresh, DocumentCopy, Download, Operation } from '@element-plus/icons-vue'
import { useAESDecrypt } from './useAESDecrypt.js'

const {
  decryptMode,
  skHeader,
  encryptedBody,
  decryptedResult,
  decryptedJson,
  loading,
  isAuthorized,
  macAddresses,
  handleDecrypt,
  handleClear,
  handleCopy,
  handleDownload,
  formatJson,
  checkLicense
} = useAESDecrypt()
</script>

<style scoped src="./styles.css"></style>
