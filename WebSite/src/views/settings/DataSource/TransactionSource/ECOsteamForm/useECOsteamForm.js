import { ref } from 'vue'

export default function useECOsteamForm(props, { emit }) {
  const collapseState = ref(['config'])

  return {
    collapseState
  }
}

