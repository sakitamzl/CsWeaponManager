import { ref } from 'vue'

export default function useC5GameForm(props, { emit }) {
  const collapseState = ref(['config'])

  return {
    collapseState
  }
}

