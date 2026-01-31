<template>
  <div class="onsalerentedout-content">
    <h2 class="page-title">已租出商品</h2>
    <p class="page-desc">查看您已经租出的所有饰品</p>

    <!-- 添加一个占位内容区域 -->
    <div class="content-area">
      <div class="placeholder-content">
        <p>暂无已租出商品数据</p>
        <p class="hint-text">您的已租出商品列表将显示在这里</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OnSaleRentedOut',
  mounted() {
    console.log('OnSaleRentedOut 组件已挂载')
  }
}
</script>

<style scoped src="../page-styles.css"></style>
