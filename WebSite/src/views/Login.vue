<template>
  <div class="login-container">
    <div class="login-box">
      <h1 class="login-title">CsWeaponManager</h1>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { apiUrls } from '@/config/api'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    
    try {
      const response = await axios.post(apiUrls.loginVerify(), {
        username: loginForm.username,
        password: loginForm.password
      })
      
      if (response.data.success) {
        // 登录成功，保存token到localStorage
        localStorage.setItem('isLoggedIn', 'true')
        localStorage.setItem('username', loginForm.username)
        localStorage.setItem('loginTime', new Date().getTime().toString())
        
        ElMessage.success(response.data.message || '登录成功')
        
        // 跳转到首页
        router.push('/')
      } else {
        ElMessage.error(response.data.message || '登录失败')
      }
    } catch (error) {
      console.error('登录失败:', error)
      ElMessage.error(error.response?.data?.message || '登录失败，请检查用户名和密码')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background-color: #2a2a2a;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #fff;
  font-size: 24px;
  font-weight: 600;
}

.login-form {
  width: 100%;
}

.login-button {
  width: 100%;
}

:deep(.el-input__inner) {
  background-color: #1e1e1e;
  border-color: #333;
  color: #fff;
}

:deep(.el-input__inner::placeholder) {
  color: #666;
}

:deep(.el-input__wrapper) {
  background-color: #1e1e1e;
  box-shadow: 0 0 0 1px #333 inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4CAF50 inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #4CAF50 inset;
}

:deep(.el-input__prefix) {
  color: #999;
}

:deep(.el-form-item__error) {
  color: #f56c6c;
}

@media (max-width: 768px) {
  .login-box {
    width: 90%;
    padding: 30px 20px;
  }
  
  .login-title {
    font-size: 20px;
  }
}
</style>

