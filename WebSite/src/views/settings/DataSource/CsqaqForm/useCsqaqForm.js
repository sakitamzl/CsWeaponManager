import { ref } from 'vue'

export default function useCsqaqForm(props, { emit }) {
  const collapseState = ref(['config'])

  // 更新表单数据
  const updateForm = (updates) => {
    emit('update:form', { ...props.form, ...updates })
  }

  return {
    collapseState
  }
}
