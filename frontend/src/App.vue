<template>
  <div id="app">
    <el-config-provider :locale="$i18n.locale">
      <!-- 导航栏，首页隐藏，其他页面显示 -->
      <Navigation v-if="$route.path !== '/'" />
      <!-- 主内容区域 -->
      <main class="main-content" :class="{ 'has-navigation': $route.path !== '/' }">
        <router-view />
      </main>
    </el-config-provider>
  </div>
</template>

<script setup lang="ts">
import Navigation from './components/Navigation.vue'
</script>

<style lang="scss">
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  width: 100vw;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: var(--el-bg-color-page);
}

/* 主内容区域样式 */
.main-content {
  /* 首页不需要顶部边距 */
  padding-top: 0;
  
  /* 非首页页面，当导航栏显示时，添加顶部边距 */
  &.has-navigation {
    padding-top: 24px;
  }
}
</style>