import { ref } from 'vue'

export default function useIGXEForm(props, { emit }) {
  const collapseState = ref(['config'])

  return {
    collapseState
  }
}

