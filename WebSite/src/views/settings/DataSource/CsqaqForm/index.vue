<template>
  <div class="csqaq-form">
    <el-collapse v-model="collapseState">
      <el-collapse-item title="CSQAQ配置" name="config">
        <el-form-item label="ApiToken" required>
          <el-input 
            v-model="form.csqaqApiToken" 
            type="textarea"
            :rows="3"
            placeholder="请输入ApiToken"
          />
        </el-form-item>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
import useCsqaqForm from './useCsqaqForm.js'

export default {
  name: 'CsqaqForm',
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
  setup(props, { emit }) {
    return useCsqaqForm(props, { emit })
  }
}
</script>
<style scoped src="./styles.css"></style>
