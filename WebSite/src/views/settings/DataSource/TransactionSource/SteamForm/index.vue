<template>
  <div class="steam-form">
    <!-- Cookie获取方式选择 -->
    <el-form-item label="获取方式" required>
      <el-radio-group v-model="form.steamCookieMethod">
        <el-radio label="qrcode">扫码登录</el-radio>
        <el-radio label="password">账号密码登录</el-radio>
        <el-radio label="manual">手动输入</el-radio>
      </el-radio-group>
    </el-form-item>

    <!-- 扫码登录 -->
    <template v-if="form.steamCookieMethod === 'qrcode'">
      <el-form-item label="登录二维码">
        <div 
          @click="steamQRStatus !== 'success' ? handleGenerateQRCode() : null"
          :style="{
            textAlign: 'center', 
            padding: '20px', 
            background: '#f5f5f5', 
            borderRadius: '8px',
            cursor: steamQRStatus === 'success' ? 'default' : 'pointer',
            transition: 'all 0.3s'
          }"
          @mouseenter="$event.currentTarget.style.background = steamQRStatus === 'success' ? '#f5f5f5' : '#e8e8e8'"
          @mouseleave="$event.currentTarget.style.background = '#f5f5f5'"
        >
          <div v-if="!steamQRCode && !steamQRLoading">
            <el-icon :size="80" color="#409EFF"><Grid /></el-icon>
            <p style="color: #409EFF; margin-top: 10px; font-weight: 500;">点击获取Steam登录二维码</p>
          </div>
          <div v-else-if="steamQRLoading">
            <el-icon :size="80" class="is-loading" color="#409EFF"><Loading /></el-icon>
            <p style="color: #409EFF; margin-top: 10px;">正在获取二维码...</p>
          </div>
          <div v-else>
            <img :src="steamQRCode" alt="Steam登录二维码" style="width: 200px; height: 200px;" />
            <p style="color: #666; margin-top: 10px; font-size: 14px;">
              请使用Steam手机APP扫描二维码
            </p>
            <el-tag :type="steamQRStatus === 'waiting' ? 'info' : steamQRStatus === 'success' ? 'success' : 'warning'" style="margin-top: 10px;">
              {{ getSteamQRStatusText() }}
            </el-tag>
            <div v-if="steamQRStatus === 'expired'" style="margin-top: 10px;">
              <el-link type="primary" :underline="false" @click.stop="handleGenerateQRCode">
                点击刷新二维码
              </el-link>
            </div>
          </div>
        </div>
      </el-form-item>
    </template>

    <!-- 账号密码登录 -->
    <template v-else-if="form.steamCookieMethod === 'password'">
      <el-form-item label="Steam用户名" required>
        <el-input 
          v-model="form.steamUsername" 
          placeholder="请输入Steam用户名"
        />
      </el-form-item>
      <el-form-item label="Steam密码" required>
        <el-input 
          v-model="form.steamPassword" 
          type="password"
          show-password
          placeholder="请输入Steam密码"
        />
      </el-form-item>
      <el-form-item label="Steam PIN">
        <el-input 
          v-model="form.steamTwofactorCode" 
          placeholder="请输入5位Steam Guard验证码（如需要）"
          maxlength="5"
        />
        <div style="color: #999; font-size: 12px; margin-top: 5px;">
          如果您的账号启用了Steam Guard手机令牌，请在此输入验证码
        </div>
      </el-form-item>
      <el-form-item>
        <el-button 
          type="success" 
          @click="handleSteamLogin" 
          :loading="steamLoginLoading"
          style="width: 100%;"
        >
          {{ isEditMode ? (steamLoginLoading ? '登录中...' : '重新登录获取Cookie') : (steamLoginLoading ? '登录中...' : '立即登录获取Cookie') }}
        </el-button>
      </el-form-item>
      <!-- 自动获取的 SteamID 显示 -->
      <el-form-item v-if="form.steamID" label="当前SteamID">
        <el-input v-model="form.steamID" disabled />
      </el-form-item>
    </template>

    <!-- 手动输入Cookie -->
    <template v-else-if="form.steamCookieMethod === 'manual'">
    </template>

    <!-- 登录状态提示 -->
    <el-alert
      v-if="form.steamLoginMessage"
      :title="form.steamLoginMessage"
      :type="form.steamLoginSuccess ? 'success' : 'warning'"
      :closable="false"
      show-icon
      style="margin-top: 10px;"
    />

    <!-- Steam配置 -->
    <el-collapse v-model="collapseState" :style="isEditMode ? '' : 'margin-top: 20px;'">
      <el-collapse-item title="Steam配置" name="config">
        <el-form-item label="SteamID" required>
          <el-input 
            v-model="form.steamID" 
            placeholder="请输入SteamID"
          />
        </el-form-item>

        <el-form-item label="基础Cookies">
          <el-input
            v-model="form.steamBaseCookies"
            type="textarea"
            :rows="3"
            :placeholder="isEditMode ? '扫码登录成功后自动填入，可手动粘贴基础Cookie' : '扫码登录成功后将自动填入，可手动粘贴基础Cookie'"
          />
          <div style="color: #999; font-size: 12px; margin-top: 4px;">
            {{ isEditMode ? '基础Cookies为扫码后立即返回的Cookie，建议与库存Cookies一同保存。' : '基础Cookies为扫码后立即返回的原始Cookie，建议同时保存以备验证。' }}
          </div>
        </el-form-item>
        <el-form-item label="库存Cookies" required>
          <el-input
            v-model="form.steamInventoryCookies"
            type="textarea"
            :rows="3"
            placeholder="访问库存页后的完整Cookie，采集库存时将使用该值"
          />
          <div style="color: #999; font-size: 12px; margin-top: 4px;">
            {{ isEditMode ? '若手动维护，请保证此Cookie可访问 <code>inventory/730/16</code>。' : '若使用手动方式，请先填写基础Cookies，再填写库存Cookies。' }}
          </div>
        </el-form-item>
        
        <el-form-item v-if="isEditMode" label="更新频率">
          <el-select v-model="form.updateFreq" placeholder="选择更新频率" style="width: 100%;">
            <el-option label="每15分钟" value="15min" />
            <el-option label="每小时" value="1hour" />
            <el-option label="每3小时" value="3hour" />
            <el-option label="每6小时" value="6hour" />
            <el-option label="每12小时" value="12hour" />
            <el-option label="每天" value="daily" />
          </el-select>
        </el-form-item>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
import useSteamForm from './useSteamForm.js'
import { Grid, Loading } from '@element-plus/icons-vue'

export default {
  name: 'SteamForm',
  components: {
    Grid,
    Loading
  },
  props: {
    form: {
      type: Object,
      required: true
    },
    isEditMode: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:form'],
  setup(props, context) {
    return useSteamForm(props, context)
  }
}
</script>
<style scoped src="./styles.css"></style>
