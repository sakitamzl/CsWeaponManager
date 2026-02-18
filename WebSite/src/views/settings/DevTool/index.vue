<template>
  <div class="dev-tool-container">
    <!-- ADB 与网络证书安装 -->
    <AdbCertForm />

    <!-- 平台饰品映射 -->
    <WeaponMappingForm />

    <!-- 图片资源包 -->
    <ImageResourceForm />
  </div>
</template>


<script>
import AdbCertForm from './AdbCertForm/index.vue'
import WeaponMappingForm from './WeaponMappingForm/index.vue'
import ImageResourceForm from './ImageResourceForm/index.vue'

export default {
  name: 'DevTool',
  components: {
    AdbCertForm,
    WeaponMappingForm,
    ImageResourceForm
  }
}
</script>

<style scoped src="./styles.css"></style>
