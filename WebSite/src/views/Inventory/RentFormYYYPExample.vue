<template>
  <div class="rent-form-example">
    <div class="example-container">
      <h1>悠悠有品出租表单示例</h1>
      <p class="description">这是一个基于截图设计的悠悠有品出租表单组件示例</p>

      <div class="form-preview">
        <RentFormYYYP
          @cancel="handleCancel"
          @submit="handleSubmit"
        />
      </div>

      <!-- 提交结果显示 -->
      <div v-if="submitResult" class="submit-result">
        <h3>提交的数据:</h3>
        <pre>{{ JSON.stringify(submitResult, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import RentFormYYYP from './RentFormYYYP.vue'

export default {
  name: 'RentFormYYYPExample',
  components: {
    RentFormYYYP
  },
  setup() {
    const submitResult = ref(null)

    const handleCancel = () => {
      ElMessage.info('取消操作')
      submitResult.value = null
    }

    const handleSubmit = (data) => {
      ElMessage.success('表单提交成功!')
      submitResult.value = data
      console.log('提交的数据:', data)
    }

    return {
      submitResult,
      handleCancel,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.rent-form-example {
  min-height: 100vh;
  background: #0a0a0a;
  padding: 2rem;
}

.example-container {
  max-width: 600px;
  margin: 0 auto;
}

h1 {
  color: #fff;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  text-align: center;
}

.description {
  color: #999;
  text-align: center;
  margin-bottom: 2rem;
}

.form-preview {
  background: #1a1a1a;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  height: 700px;
}

.submit-result {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #1a1a1a;
  border-radius: 8px;
  border: 2px solid #409EFF;
}

.submit-result h3 {
  color: #fff;
  margin-bottom: 1rem;
}

.submit-result pre {
  color: #67C23A;
  background: #0a0a0a;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.9rem;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .rent-form-example {
    padding: 1rem;
  }

  .form-preview {
    height: 600px;
  }
}
</style>
