<template>
  <!-- 背景图片网格轮播组件 -->
  <div class="showcase-background">
    <div class="showcase-grid">
      <div
        v-for="(image, index) in showcaseImages"
        :key="index"
        class="showcase-item"
        :style="{
          backgroundImage: `url(${image.url})`,
          animationDelay: `${index * 0.1}s`
        }"
        :title="image.alt"
      ></div>
    </div>
    <div class="background-overlay"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 背景图片网格轮播组件
 *
 * 功能：
 * - 展示多张背景图片组成的网格
 * - 实现平滑的淡入淡出动画
 * - 自动轮播切换图片
 */

// 展示图片数据
const showcaseImages = ref([
  { url: '/assets/showcase/cover_art.webp', alt: '艺术' },
  { url: '/assets/showcase/cover_baby.webp', alt: '婴儿' },
  { url: '/assets/showcase/cover_baking.webp', alt: '烘焙' },
  { url: '/assets/showcase/cover_beauty.webp', alt: '美容' },
  { url: '/assets/showcase/cover_books.webp', alt: '书籍' },
  { url: '/assets/showcase/cover_camping.webp', alt: '露营' },
  { url: '/assets/showcase/cover_career.webp', alt: '职业' },
  { url: '/assets/showcase/cover_cars.webp', alt: '汽车' },
  { url: '/assets/showcase/cover_coffee.webp', alt: '咖啡' },
  { url: '/assets/showcase/cover_digital_nomad.webp', alt: '数字游民' },
  { url: '/assets/showcase/cover_diy.webp', alt: 'DIY' },
  { url: '/assets/showcase/cover_drinks.webp', alt: '饮品' },
  { url: '/assets/showcase/cover_education.webp', alt: '教育' },
  { url: '/assets/showcase/cover_english.webp', alt: '英语' },
  { url: '/assets/showcase/cover_fashion.webp', alt: '时尚' },
  { url: '/assets/showcase/cover_finance.webp', alt: '金融' },
  { url: '/assets/showcase/cover_fitness.webp', alt: '健身' },
  { url: '/assets/showcase/cover_food.webp', alt: '食物' },
  { url: '/assets/showcase/cover_gaming.webp', alt: '游戏' },
  { url: '/assets/showcase/cover_hairstyle.webp', alt: '发型' },
  { url: '/assets/showcase/cover_hiking.webp', alt: '徒步' },
  { url: '/assets/showcase/cover_home_cooking.webp', alt: '家庭烹饪' },
  { url: '/assets/showcase/cover_home_decor.webp', alt: '家居装饰' },
  { url: '/assets/showcase/cover_jewelry.webp', alt: '珠宝' },
  { url: '/assets/showcase/cover_minimalist.webp', alt: '极简主义' },
  { url: '/assets/showcase/cover_movies.webp', alt: '电影' },
  { url: '/assets/showcase/cover_music.webp', alt: '音乐' },
  { url: '/assets/showcase/cover_nails.webp', alt: '美甲' },
  { url: '/assets/showcase/cover_office.webp', alt: '办公室' },
  { url: '/assets/showcase/cover_outdoor.webp', alt: '户外' },
  { url: '/assets/showcase/cover_parenting.webp', alt: '育儿' },
  { url: '/assets/showcase/cover_pets.webp', alt: '宠物' },
  { url: '/assets/showcase/cover_photography.webp', alt: '摄影' },
  { url: '/assets/showcase/cover_plants.webp', alt: '植物' },
  { url: '/assets/showcase/cover_psychology.webp', alt: '心理学' },
  { url: '/assets/showcase/cover_real_estate.webp', alt: '房地产' },
  { url: '/assets/showcase/cover_skincare.webp', alt: '护肤' },
  { url: '/assets/showcase/cover_stationery.webp', alt: '文具' },
  { url: '/assets/showcase/cover_tech.webp', alt: '科技' },
  { url: '/assets/showcase/cover_travel.webp', alt: '旅行' },
  { url: '/assets/showcase/cover_watches.webp', alt: '手表' },
  { url: '/assets/showcase/cover_wedding.webp', alt: '婚礼' },
  { url: '/assets/showcase/cover_yoga.webp', alt: '瑜伽' }
])

// 轮播定时器
let carouselInterval: number | null = null

// 当前显示的图片索引
const currentIndex = ref(0)

/**
 * 切换到下一张图片
 */
const nextImage = () => {
  currentIndex.value = (currentIndex.value + 1) % showcaseImages.value.length
}

// 组件挂载时启动轮播
onMounted(() => {
  carouselInterval = window.setInterval(nextImage, 5000)
})

// 组件卸载时清除轮播
onUnmounted(() => {
  if (carouselInterval) {
    clearInterval(carouselInterval)
  }
})
</script>

<style scoped>
/* 背景轮播容器 */
.showcase-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  overflow: hidden;
}

/* 背景遮罩 */
.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom, 
    rgba(255, 255, 255, 0.85), 
    rgba(255, 255, 255, 0.95)
  );
}

/* 图片网格 */
.showcase-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: repeat(6, 1fr);
  gap: 12px;
  width: 100%;
  height: 100%;
  padding: 20px;
  animation: fadeIn 1s ease-out;
}

/* 单个图片项 */
.showcase-item {
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  opacity: 0;
  animation: fadeInUp 0.6s ease-out forwards;
  transition: all 0.3s ease;
}

.showcase-item:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 0.6;
    transform: translateY(0);
  }
}
</style>