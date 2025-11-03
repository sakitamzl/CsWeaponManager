<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  min-height: 100vh;
  background-color: #0d1117 !important;
  color: #000000;
  overflow: auto;
}

html, body {
  background-color: #0d1117 !important;
  color: #000000 !important;
  margin: 0;
  padding: 0;
}
</style>