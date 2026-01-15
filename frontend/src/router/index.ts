import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
      meta: {
        title: '逸流 - 多平台图文生成器'
      }
    },
    {
      path: '/outline',
      name: 'Outline',
      component: () => import('@/views/OutlineView.vue'),
      meta: {
        title: '编辑大纲 - 逸流'
      }
    },
    {
      path: '/generate',
      name: 'Generate',
      component: () => import('@/views/GenerateView.vue'),
      meta: {
        title: '生成图片 - 逸流'
      }
    },
    {
      path: '/result',
      name: 'Result',
      component: () => import('@/views/ResultView.vue'),
      meta: {
        title: '生成结果 - 逸流'
      }
    },
    {
      path: '/config',
      name: 'Config',
      component: () => import('@/views/Config.vue'),
      meta: {
        title: '配置管理 - 逸流'
      }
    },
    {
      path: '/history',
      name: 'History',
      component: () => import('@/views/History.vue'),
      meta: {
        title: '历史记录 - 逸流'
      }
    },
    {
      path: '/inspiration',
      name: 'Inspiration',
      component: () => import('@/views/InspirationView.vue'),
      meta: {
        title: '灵感获取 - 逸流'
      }
    },
    {
      path: '/batch',
      name: 'Batch',
      component: () => import('@/views/Batch.vue'),
      meta: {
        title: '批量生成 - 逸流'
      }
    }
  ]
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta?.title) {
    document.title = to.meta.title as string
  }
  next()
})

export default router