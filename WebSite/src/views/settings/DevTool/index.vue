<template>
  <div class="dev-tool-container">
    <!-- SteamDT 数据拦截扩展 -->
    <BrowserExtension />

    <!-- ADB 与网络证书安装 -->
    <AdbCertForm />

    <!-- 平台饰品映射 -->
    <WeaponMappingForm />

    <!-- 图片资源包 -->
    <ImageResourceForm />
  </div>
</template>


<script>
import BrowserExtension from './BrowserExtension/index.vue'
import AdbCertForm from './AdbCertForm/index.vue'
import WeaponMappingForm from './WeaponMappingForm/index.vue'
import ImageResourceForm from './ImageResourceForm/index.vue'

export default {
  name: 'DevTool',
  components: {
    BrowserExtension,
    AdbCertForm,
    WeaponMappingForm,
    ImageResourceForm
  }
}
</script>

<style scoped src="./styles.css"></style>
