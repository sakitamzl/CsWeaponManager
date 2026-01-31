<template>
  <div class="on-sale-lease-content">
    <h2 class="page-title">租赁商品</h2>
    <p class="page-desc">管理您在悠悠有品平台上架租赁的所有饰品</p>

    <!-- 添加一个占位内容区域 -->
    <div class="content-area">
      <div class="placeholder-content">
        <p>暂无租赁商品数据</p>
        <p class="hint-text">您的租赁商品列表将显示在这里</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OnSaleLease',
  mounted() {
    console.log('OnSaleLease 组件已挂载')
  }
}
</script>

<style scoped src="../page-styles.css"></style>
