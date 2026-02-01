# ADR-002: 选择 Vue 3 作为前端框架

## 状态
✅ 已采纳

## 上下文
需要选择一个前端框架来构建游戏前端界面。主要候选框架：
- **Vue 3**: 渐进式框架，Composition API
- **React**: 组件化库，Hooks
- **Svelte**: 编译时框架，性能优秀

### 需求
1. **复杂状态管理**: 游戏有大量状态（角色、事件、地图）
2. **实时更新**: 需要通过 WebSocket 实时更新 UI
3. **高性能渲染**: 需要集成 PixiJS 进行 Canvas 渲染
4. **TypeScript 支持**: 类型安全和代码提示
5. **快速开发**: 开发效率高，学习曲线平缓

## 决策
选择 **Vue 3 + Composition API** 作为前端框架。

## 理由

### 1. Composition API 的优势

Vue 3 的 Composition API 非常适合复杂游戏逻辑：

```typescript
// 使用 Composition API 管理游戏状态
import { ref, computed, watch } from 'vue'
import { useWebSocket } from '@/composables/useWebSocket'

export function useGameState() {
  const currentYear = ref(100)
  const currentMonth = ref(1)
  const isPaused = ref(false)

  // 计算属性
  const gameTime = computed(() => `Year ${currentYear.value}, Month ${currentMonth.value}`)

  // WebSocket 实时更新
  const { onMessage } = useWebSocket()
  onMessage((msg) => {
    if (msg.type === 'tick') {
      currentYear.value = msg.year
      currentMonth.value = msg.month
    }
  })

  // 响应式监听
  watch(isPaused, (paused) => {
    console.log(`Game ${paused ? 'paused' : 'resumed'}`)
  })

  return { currentYear, currentMonth, isPaused, gameTime }
}
```

**优点**:
- 逻辑复用：可以抽取成可复用的 composables
- 类型推导：TypeScript 支持更好
- 代码组织：按功能而非生命周期组织代码

### 2. PixiJS 集成良好

Vue 3 有官方的 PixiJS 集成库 `vue3-pixi`：

```vue
<script setup lang="ts">
import { Application } from 'vue3-pixi'
import Viewport from './Viewport.vue'
import MapLayer from './MapLayer.vue'

const width = ref(1920)
const height = ref(1080)
</script>

<template>
  <Application
    :width="width"
    :height="height"
    :antialias="false"
    :background-color="0x000000"
  >
    <Viewport :screen-width="width" :screen-height="height">
      <MapLayer />
      <EntityLayer />
    </Viewport>
  </Application>
</template>
```

**优点**:
- 声明式：像写 HTML 一样写 Canvas 渲染
- 响应式：自动同步状态到 Canvas
- 组件化：可以拆分成多个 PixiJS 组件

React 的 `react-pixi` 不如 `vue3-pixi` 成熟，Svelte 没有官方 PixiJS 集成。

### 3. 状态管理生态成熟

Vue 3 有官方推荐的状态管理库 **Pinia**：

```typescript
// stores/gameStore.ts
import { defineStore } from 'pinia'

export const useGameStore = defineStore('game', () => {
  const year = ref(100)
  const month = ref(1)
  const avatars = ref<Avatar[]>([])

  async function fetchGameState() {
    const data = await gameAPI.getState()
    year.value = data.year
    month.value = data.month
    avatars.value = data.avatars
  }

  return { year, month, avatars, fetchGameState }
})
```

**优点**:
- TypeScript 原生支持
- Composition API 风格（与 Vue 3 一致）
- DevTools 集成（方便调试）
- 比 Vuex 更简洁

React 的 Redux/Zustand 和 Svelte 的 Store 都可以，但 Pinia 与 Vue 3 集成最好。

### 4. TypeScript 支持优秀

Vue 3 是用 TypeScript 重写的，类型支持非常好：

```typescript
// 组件 props 类型推导
const props = defineProps<{
  avatarId: string
  showDetails?: boolean
}>()

// emit 类型推导
const emit = defineEmits<{
  (e: 'avatarSelected', payload: { type: 'avatar'; id: string }): void
  (e: 'regionSelected', payload: { type: 'region'; id: string }): void
}>()

// computed 类型自动推导
const fullName = computed(() => `${props.firstName} ${props.lastName}`)
```

React 的 TypeScript 支持也很好，但需要写更多的类型注解。Svelte 的 TypeScript 支持不如前两者。

### 5. 开发体验优秀

Vue 3 + Vite 的开发体验极佳：

```bash
# 极速 HMR（热模块替换）
npm run dev  # 启动开发服务器，<200ms 热更新

# 快速构建
npm run build  # 生产构建，1-2 秒
```

**优点**:
- Vite 原生 ESM，启动速度快
- HMR 快（修改代码 < 200ms 生效）
- 开箱即用（无需复杂配置）

React 通常用 Webpack，启动慢。Svelte 也用 Vite，体验相当。

### 6. UI 库生态丰富

Vue 3 有优秀的 UI 库 **Naive UI**：

```vue
<script setup lang="ts">
import { NButton, NCard, NDataTable } from 'naive-ui'
</script>

<template>
  <NCard title="角色列表">
    <NDataTable :columns="columns" :data="avatars" />
    <NButton @click="createAvatar">创建角色</NButton>
  </NCard>
</template>
```

**优点**:
- TypeScript 原生
- Vue 3 Composition API 风格
- 组件丰富（100+ 组件）
- 文档完善

React 有 Ant Design/Material UI，Svelte 有 Carbon Components，但 Naive UI 更适合 Vue 3。

## 权衡

### 优点
- ✅ Composition API 适合复杂状态管理
- ✅ PixiJS 集成优秀（vue3-pixi）
- ✅ TypeScript 支持好
- ✅ Pinia 状态管理简洁
- ✅ Vite 开发体验极佳
- ✅ 学习曲线平缓（对熟悉 Vue 2 的开发者）

### 缺点
- ❌ 生态不如 React 庞大（但游戏需要的库都有）
- ❌ Composition API 有学习成本（但比 Hooks 简单）

## 替代方案

### React
- **优点**: 生态最大、就业市场需求高、社区活跃
- **缺点**:
  - Hooks 学习曲线陡峭（useEffect 依赖问题）
  - 需要额外的状态管理库（Redux/Zustand）
  - PixiJS 集成不如 Vue 3（react-pixi 不成熟）
  - 开发体验不如 Vue 3 + Vite（通常用 Webpack）

**为什么不选**: PixiJS 集成不够好，Hooks 复杂度高。

### Svelte
- **优点**: 性能最好（编译时优化）、代码简洁、学习曲线最平缓
- **缺点**:
  - 生态小（第三方库少）
  - 没有官方 PixiJS 集成
  - TypeScript 支持不如 Vue 3/React
  - 企业采用率低（不确定性）

**为什么不选**: 生态太小，PixiJS 集成需要自己封装。

## 后果

### 正面
- Composition API 让复杂游戏逻辑更易管理
- vue3-pixi 让 PixiJS 渲染像写 HTML 一样简单
- Pinia 状态管理清晰，易于调试
- Vite 开发体验极佳，热更新快
- TypeScript 类型推导减少运行时错误

### 负面
- 团队需要学习 Composition API（已通过文档和培训解决）
- 部分 Vue 2 开发者不适应新的 API 风格（但 Vue 3 也兼容 Options API）

## 经验教训
- Composition API 的 `ref` 和 `reactive` 在大型应用中，`ref` 更适合（类型推导更好）
- vue3-pixi 渲染大量精灵时，需要优化（使用视口裁剪、精灵池）
- Pinia 的 DevTools 对调试游戏状态非常有帮助
- Vite 的 HMR 极大提升了开发效率

## 相关决策
- [ADR-001: 选择 FastAPI 作为后端框架](ADR-001-web-framework.md)
- [ADR-003: 选择 PixiJS 作为渲染引擎](ADR-003-rendering-engine.md)
- [ADR-005: 前后端状态同步方案](ADR-005-state-management.md)

---

**创建时间**: 2026-02-01
**作者**: 前端团队
**审核**: ✅
