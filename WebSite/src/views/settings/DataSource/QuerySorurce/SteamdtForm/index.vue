<template>
  <div class="steamdt-form">
    <el-collapse v-model="collapseState">
      <el-collapse-item title="SteamDT配置" name="config">
        <el-form-item label="API_KEY" required>
          <el-input 
            v-model="form.steamdtApiKey" 
            type="textarea"
            :rows="3"
            placeholder="请输入API_KEY"
          />
        </el-form-item>
        <el-form-item label="回调域名" required>
          <el-input 
            v-model="form.steamdtCallbackDomain" 
            placeholder="请输入回调域名"
          />
        </el-form-item>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
import useSteamdtForm from './useSteamdtForm.js'

export default {
  name: 'SteamdtForm',
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
    return useSteamdtForm(props, { emit })
  }
}
</script>
<style scoped src="./styles.css"></style>
