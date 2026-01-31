<template>
  <div class="youpin-form">
    <!-- 登录方式选择 -->
    <el-form-item label="登录方式" required>
      <el-radio-group v-model="form.yyypLoginMethod">
        <el-radio label="sms">短信登录</el-radio>
        <el-radio label="capture">通过抓包获取</el-radio>
      </el-radio-group>
    </el-form-item>

    <!-- 短信登录方式 -->
    <template v-if="form.yyypLoginMethod === 'sms'">
      <el-form-item v-if="!isEditMode" label="Session ID" required>
        <div style="display: flex; gap: 10px;">
          <el-input 
            v-model="form.yyypSessionId" 
            placeholder="点击生成按钮生成Session ID"
            style="flex: 1;"
            readonly
            disabled
          />
          <el-button 
            type="primary" 
            @click="handleGenerateSessionId"
            :loading="generatingSessionId"
          >
            生成SessionID
          </el-button>
        </div>
      </el-form-item>
      <el-form-item v-if="!isEditMode" label="Device ID" required>
        <div style="display: flex; gap: 10px;">
          <el-input 
            v-model="form.yyypDeviceId" 
            placeholder="点击生成按钮生成Device ID"
            style="flex: 1;"
            readonly
            disabled
          />
          <el-button 
            type="primary" 
            @click="handleGenerateDeviceId"
            :loading="generatingDeviceId"
          >
            生成DeviceID
          </el-button>
        </div>
      </el-form-item>
      <el-form-item label="手机号">
        <el-input 
          v-model="form.yyypPhone" 
          :placeholder="isEditMode ? '手机号' : '请输入手机号'"
          :disabled="isEditMode"
          :readonly="isEditMode"
          maxlength="11"
        />
      </el-form-item>
      
      <el-form-item label="验证码">
        <div style="display: flex; gap: 10px;">
          <el-input 
            v-model="form.yyypSmsCode" 
            placeholder="请输入短信验证码"
            maxlength="6"
            style="flex: 1;"
          />
          <el-button 
            type="primary" 
            @click="handleSendSmsCode"
            :disabled="smsCodeCountdown > 0"
            :loading="sendingSmsCode"
          >
            {{ smsCodeCountdown > 0 ? `${smsCodeCountdown}秒后重试` : '发送验证码' }}
          </el-button>
        </div>
      </el-form-item>
      <el-form-item>
        <el-button 
          type="success" 
          @click="handleYyypSmsLogin" 
          :loading="yyypSmsLoginLoading"
          style="width: 100%;"
        >
          <el-icon style="margin-right: 5px;"><Grid /></el-icon>
          {{ isEditMode ? (yyypSmsLoginLoading ? '登录中...' : '重新登录') : (yyypSmsLoginLoading ? '登录中...' : '短信登录') }}
        </el-button>
        <div v-if="yyypSmsLoginStatus === 'success'" style="margin-top: 10px; padding: 10px; background: #f6ffed; border-radius: 4px; border-left: 3px solid #52c41a;">
          <div style="color: #52c41a; font-weight: 500;">
            <el-icon><CircleCheck /></el-icon> 登录成功！配置信息已自动填充
          </div>
        </div>
      </el-form-item>
    </template>

    <!-- 通过抓包获取方式 -->
    <template v-else-if="form.yyypLoginMethod === 'capture'">
      <el-form-item>
        <el-button 
          type="success" 
          @click="startYyypTokenCollection" 
          :loading="yyypTokenLoading"
          :disabled="yyypTokenStatus === 'success'"
          style="width: 100%;"
        >
          <el-icon style="margin-right: 5px;"><Grid /></el-icon>
          {{ yyypTokenLoading ? '正在获取令牌...' : yyypTokenStatus === 'success' ? '✓ 令牌已获取' : (isEditMode ? '重新获取悠悠有品令牌' : '一键获取悠悠有品令牌') }}
        </el-button>
        <div v-if="yyypTokenStatus === 'waiting'" style="margin-top: 10px; padding: 10px; background: #fff7e6; border-radius: 4px; border-left: 3px solid #faad14;">
          <div style="color: #faad14; font-weight: 500; margin-bottom: 5px;">
            <el-icon><Loading /></el-icon> 等待手机APP访问...
          </div>
          <div style="color: #666; font-size: 12px;">
            1. 在手机WiFi设置中配置代理: <strong>{{ proxyAddress || '...' }}</strong><br/>
            2. 打开悠悠有品APP并登录<br/>
            3. 系统将自动获取令牌
          </div>
        </div>
        <div v-if="yyypTokenStatus === 'success'" style="margin-top: 10px; padding: 10px; background: #f6ffed; border-radius: 4px; border-left: 3px solid #52c41a;">
          <div style="color: #52c41a; font-weight: 500;">
            <el-icon><CircleCheck /></el-icon> 令牌获取成功!
          </div>
        </div>
      </el-form-item>
    </template>
    
    <!-- 基础配置 -->
    <el-collapse v-model="basicCollapse" style="margin-bottom: 20px;">
      <el-collapse-item title="基础配置" name="basic">
        <el-form-item label="手机号" required>
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="应用版本" required>
          <el-input v-model="form.appVersion" placeholder="请输入应用版本" />
        </el-form-item>
        <el-form-item label="应用类型" required>
          <el-input v-model="form.appType" placeholder="请输入应用类型" />
        </el-form-item>
        <el-form-item label="用户ID" required>
          <el-input v-model="form.userId" placeholder="请输入用户ID" />
        </el-form-item>
        <el-form-item label="SteamID" required>
          <el-input v-model="form.steamId" placeholder="请输入SteamID" />
        </el-form-item>
      </el-collapse-item>
    </el-collapse>
    
    <!-- 认证令牌配置 -->
    <el-collapse v-model="tokenCollapse" style="margin-bottom: 20px;">
      <el-collapse-item title="认证令牌配置" name="token">
        <el-form-item label="Session ID" required>
          <el-input v-model="form.sessionid" placeholder="请输入Session ID" />
        </el-form-item>
        <el-form-item label="Token" required>
          <el-input 
            v-model="form.token" 
            type="textarea"
            :rows="2"
            placeholder="请输入Token"
          />
        </el-form-item>
      </el-collapse-item>
    </el-collapse>
    
    <!-- 设备信息配置 -->
    <el-collapse v-model="deviceCollapse" style="margin-bottom: 20px;">
      <el-collapse-item title="设备信息配置" name="device">
        <el-form-item label="设备名称" required>
          <el-input v-model="form.deviceName" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="Device Token" required>
          <el-input v-model="form.devicetoken" placeholder="请输入Device Token" />
        </el-form-item>
        <el-form-item label="Device ID" required>
          <el-input v-model="form.deviceid" placeholder="请输入Device ID" />
        </el-form-item>
        <el-form-item label="Device Info" required>
          <el-input 
            v-model="form.deviceInfo" 
            type="textarea"
            :rows="2"
            placeholder="请输入Device Info (JSON格式)"
          />
        </el-form-item>
      </el-collapse-item>
    </el-collapse>
    
    <!-- 高级密钥配置 -->
    <el-collapse v-model="advancedCollapse">
      <el-collapse-item title="高级密钥配置" name="advanced">
        <el-form-item label="Device UK" required>
          <el-input 
            v-model="form.deviceuk" 
            type="textarea"
            :rows="2"
            placeholder="请输入Device UK"
          />
        </el-form-item>
        <el-form-item label="UK" required>
          <el-input 
            v-model="form.uk" 
            type="textarea"
            :rows="2"
            placeholder="请输入UK"
          />
        </el-form-item>
        <el-form-item label="SK" required>
          <el-input 
            v-model="form.sk" 
            type="textarea"
            :rows="3"
            placeholder="请输入SK"
          />
        </el-form-item>
        <el-form-item label="Tracestate" required>
          <el-input 
            v-model="form.tracestate" 
            type="textarea"
            :rows="2"
            placeholder="请输入Tracestate"
          />
        </el-form-item>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
import useYoupinForm from './useYoupinForm.js'
import { Grid, Loading, CircleCheck } from '@element-plus/icons-vue'

export default {
  name: 'YoupinForm',
  components: {
    Grid,
    Loading,
    CircleCheck
  },
  props: {
    form: {
      type: Object,
      required: true
    },
    isEditMode: {
      type: Boolean,
      default: false
    },
    proxyAddress: {
      type: String,
      default: ''
    }
  },
  emits: ['update:form', 'update:proxyAddress'],
  setup(props, { emit }) {
    return useYoupinForm(props, { emit })
  }
}
</script>
<style scoped src="./styles.css"></style>
