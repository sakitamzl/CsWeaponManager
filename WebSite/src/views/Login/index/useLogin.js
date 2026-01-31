import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

export function useLogin() {
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
}
