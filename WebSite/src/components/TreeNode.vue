<template>
  <div class="tree-node">
    <div
      class="tree-node-content"
      :class="{
        'is-directory': node.type === 'directory',
        'is-file': node.type === 'file',
        'is-selected': isSelected
      }"
      @click="handleSelect"
    >
      <span class="tree-node-icon">
        <span v-if="node.type === 'directory'" class="folder-icon">
          {{ expanded ? '📂' : '📁' }}
        </span>
        <span v-else class="file-icon">📄</span>
      </span>
      <span class="tree-node-label">{{ node.name }}</span>
    </div>
    <div v-if="node.type === 'directory' && expanded && node.children" class="tree-node-children">
      <TreeNode
        v-for="child in node.children"
        :key="child.path"
        :node="child"
        :selected-path="selectedPath"
        @select="$emit('select', $event)"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'TreeNode',
  props: {
    node: {
      type: Object,
      required: true
    },
    selectedPath: {
      type: String,
      default: ''
    }
  },
  emits: ['select'],
  setup(props, { emit }) {
    const expanded = ref(false)

    const toggleExpand = () => {
      if (props.node.type === 'directory') {
        expanded.value = !expanded.value
      }
    }

    const handleSelect = () => {
      if (props.node.type === 'file') {
        emit('select', props.node.path)
      } else {
        toggleExpand()
      }
    }

    const isSelected = computed(() => {
      return props.node.type === 'file' && props.node.path === props.selectedPath
    })

    return {
      expanded,
      toggleExpand,
      handleSelect,
      isSelected
    }
  }
}
</script>

<style scoped>
.tree-node {
  user-select: none;
}

.tree-node-content {
  display: flex;
  align-items: center;
  padding: 0.625rem 0.75rem;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
  color: #e0e0e0;
  margin-bottom: 0.25rem;
}

.tree-node-content:hover {
  background-color: #2a2a2a;
  border-color: #409eff;
}

.tree-node-content.is-selected {
  background-color: rgba(64, 158, 255, 0.1);
  border: 1px solid #409eff;
  color: #409eff;
  font-weight: 500;
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.3);
}

.tree-node-icon {
  margin-right: 0.5rem;
  font-size: 1rem;
  display: flex;
  align-items: center;
}

.tree-node-label {
  flex: 1;
  font-size: 0.9rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tree-node-children {
  padding-left: 1.25rem;
  margin-top: 0.25rem;
}
</style>
