<template>
  <div class="c5game-form">
    <el-collapse v-model="collapseState">
      <el-collapse-item title="C5 GAME 配置" name="config">
        <el-form-item label="API地址" required>
          <el-input v-model="form.apiUrl" placeholder="请输入API地址" />
        </el-form-item>

        <el-form-item label="API密钥" required>
          <el-input
            v-model="form.apiKey"
            type="textarea"
            :rows="2"
            placeholder="请输入API密钥"
          />
        </el-form-item>

        <el-form-item label="休眠时间(秒)">
          <el-input-number
            v-model="form.sleepTime"
            :min="1"
            :max="86400"
            style="width: 100%;"
          />
        </el-form-item>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
import useC5GameForm from './useC5GameForm.js'

export default {
  name: 'C5GameForm',
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
    return useC5GameForm(props, { emit })
  }
}
</script>

<style scoped src="./styles.css"></style>

