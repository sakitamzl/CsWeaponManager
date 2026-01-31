<template>
  <div class="container" @click="handleContainerClick">
    <aside class="sidebar" :class="{ collapsed: isCollapsed }" @click.stop="handleSidebarClick">
      <div class="sidebar-header">
        <h1 v-if="!isCollapsed">CsWeaponManager</h1>
        <h1 v-else class="collapsed-title">CS</h1>
      </div>
      <ul>
        <li
          v-for="item in menuItems"
          :key="item.path"
          :class="{ active: $route.path === item.path }"
          @click.stop="handleMenuClick(item.path)"
          :title="isCollapsed ? item.title : ''"
        >
          <img :src="item.icon" :alt="item.title" class="menu-icon">
          <span v-if="!isCollapsed" class="menu-text">{{ item.title }}</span>
        </li>
      </ul>

      <!-- 空白填充区域,用于捕获点击事件 -->
      <div class="sidebar-spacer"></div>

      <!-- 用户信息和退出按钮 -->
      <div class="sidebar-footer" v-if="isLoggedIn" @click.stop>
        <div class="user-info" v-if="!isCollapsed">
          <span class="username">{{ username }}</span>
          <button @click.stop="handleLogout" class="logout-btn" title="退出登录">
            退出
          </button>
        </div>
        <button v-else @click.stop="handleLogout" class="logout-btn-icon" title="退出登录">
          🚪
        </button>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useLayout } from './useLayout.js'

export default {
  name: 'Layout',
  setup() {
    return useLayout()
  }
}
</script>

<style scoped src="./styles.css"></style>
