<template>
  <div>
    <div class="settings-container">
      <div class="settings-section">
        <h3>登录设置</h3>
        <el-form :model="basicSettings" label-width="150px">
          <el-form-item label="启用登录验证">
            <el-switch 
              v-model="basicSettings.enableLogin" 
              active-text="开启"
              inactive-text="关闭"
              @change="handleLoginToggle"
            />
          </el-form-item>
          
          <el-form-item label="用户名" v-if="basicSettings.enableLogin">
            <el-input 
              v-model="basicSettings.username" 
              style="width: 300px;" 
              placeholder="请输入用户名"
            />
          </el-form-item>
          
          <el-form-item label="密码" v-if="basicSettings.enableLogin">
            <el-input 
              v-model="basicSettings.password" 
              type="password" 
              show-password
              style="width: 300px;" 
              placeholder="请输入密码"
            />
          </el-form-item>
          
          <el-form-item label="允许外网访问">
            <el-switch 
              v-model="basicSettings.allowExternalAccess" 
              active-text="开启"
              inactive-text="关闭"
              @change="handleExternalAccessToggle"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 保存按钮 -->
      <div class="save-actions">
        <el-button type="primary" size="large" @click="saveSettings">保存设置</el-button>
        <el-button size="large" @click="resetForm">重置</el-button>
      </div>
    </div>
  </div>
</template>


<script>
import { useSystemSettings } from './useSystemSettings.js'

export default {
  name: 'SystemSettings',
  setup() {
    return useSystemSettings()
  }
}
</script>

<style scoped src="./styles.css"></style>
