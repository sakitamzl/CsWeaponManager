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
import RentFormYYYP from '../RentFormYYYP/index.vue'
import { useRentFormYYYPExample } from './useRentFormYYYPExample.js'

export default {
  name: 'RentFormYYYPExample',
  components: {
    RentFormYYYP
  },
  setup() {
    return useRentFormYYYPExample()
  }
}
</script>

<style scoped src="./styles.css"></style>
