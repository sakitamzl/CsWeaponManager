<template>
  <div class="onsaletransfer-content">
    <h2 class="page-title">过户商品</h2>
    <p class="page-desc">管理您在悠悠有品平台过户的所有饰品</p>

    <!-- 添加一个占位内容区域 -->
    <div class="content-area">
      <div class="placeholder-content">
        <p>暂无过户商品数据</p>
        <p class="hint-text">您的过户商品列表将显示在这里</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OnSaleTransfer',
  mounted() {
    console.log('OnSaleTransfer 组件已挂载')
  }
}
</script>

<style scoped src="../page-styles.css"></style>
