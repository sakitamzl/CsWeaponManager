<template>
  <div class="onsaleinstant-content">
    <h2 class="page-title">秒到账商品</h2>
    <p class="page-desc">管理您的秒到账商品</p>

    <!-- 添加一个占位内容区域 -->
    <div class="content-area">
      <div class="placeholder-content">
        <p>暂无秒到账商品数据</p>
        <p class="hint-text">您的秒到账商品列表将显示在这里</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OnSaleInstant',
  mounted() {
    console.log('OnSaleInstant 组件已挂载')
  }
}
</script>

<style scoped src="../page-styles.css"></style>
