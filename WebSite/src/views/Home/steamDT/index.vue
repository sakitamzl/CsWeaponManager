<template>
  <div class="card chart-card steamdt-market-index">
    <div class="chart-header">
      <h3>SteamDT 大盘指数</h3>
    </div>

    <!-- 直接嵌入 SteamDT 页面 -->
    <div class="market-index-iframe-container" v-loading="iframeLoading">
      <iframe
        ref="steamdtIframe"
        src="https://steamdt.com/section?type=BROAD"
        frameborder="0"
        class="steamdt-iframe"
        @load="onIframeLoad"
      ></iframe>
    </div>
  </div>
</template>

<script setup>
import { useSteamDT } from './useSteamDT.js'

const {
  steamdtIframe,
  iframeLoading,
  onIframeLoad
} = useSteamDT()
</script>

<style scoped src="./styles.css"></style>
