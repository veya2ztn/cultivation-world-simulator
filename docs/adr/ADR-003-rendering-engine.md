# ADR-003: 选择 PixiJS 作为渲染引擎

## 状态
✅ 已采纳

## 上下文
游戏需要在浏览器中渲染 2D 地图，包括：
- **地形渲染**: 瓦片地图（100x100 格子）
- **角色渲染**: 可能有 100+ 个 NPC 同时在地图上
- **动画效果**: 角色移动、表情变化、特效
- **交互**: 点击角色查看详情、地图缩放拖动

主要候选技术：
- **原生 Canvas API**: 浏览器原生 API
- **PixiJS**: 2D WebGL 渲染引擎
- **Three.js**: 3D WebGL 渲染引擎
- **Phaser**: 游戏引擎

## 决策
选择 **PixiJS v8** 作为渲染引擎。

## 理由

### 1. 高性能 WebGL 渲染

PixiJS 使用 WebGL 进行硬件加速渲染，性能远超原生 Canvas API：

```typescript
// PixiJS 渲染 1000 个精灵
const app = new PIXI.Application({
  width: 1920,
  height: 1080,
  backgroundColor: 0x000000
})

for (let i = 0; i < 1000; i++) {
  const sprite = PIXI.Sprite.from('avatar.png')
  sprite.x = Math.random() * 1920
  sprite.y = Math.random() * 1080
  app.stage.addChild(sprite)
}

// WebGL 批量渲染，60fps 无压力
```

**性能对比**:
- **Canvas API**: 渲染 100 个精灵 ~30fps
- **PixiJS**: 渲染 1000+ 个精灵 ~60fps
- **性能提升**: 10x+ （WebGL 批量渲染 + GPU 加速）

### 2. 精灵系统强大

PixiJS 的精灵系统非常适合游戏开发：

```typescript
// 角色精灵类
class AvatarSprite extends PIXI.Container {
  private avatar: PIXI.Sprite
  private nameText: PIXI.Text
  private actionEmoji: PIXI.Text

  constructor(avatarData: Avatar) {
    super()

    // 头像
    this.avatar = PIXI.Sprite.from(avatarData.portrait)
    this.avatar.anchor.set(0.5)

    // 名字标签
    this.nameText = new PIXI.Text(avatarData.name, {
      fontSize: 12,
      fill: 0xffffff
    })
    this.nameText.anchor.set(0.5, 0)
    this.nameText.y = 20

    // 动作表情
    this.actionEmoji = new PIXI.Text(avatarData.actionEmoji, {
      fontSize: 16
    })
    this.actionEmoji.anchor.set(0.5)
    this.actionEmoji.y = -20

    this.addChild(this.avatar, this.nameText, this.actionEmoji)

    // 交互
    this.interactive = true
    this.on('pointerdown', () => {
      console.log(`Clicked on ${avatarData.name}`)
    })
  }

  update(delta: number) {
    // 每帧更新（动画、位置）
    this.actionEmoji.rotation += 0.05 * delta
  }
}
```

**优点**:
- 精灵树（Scene Graph）：父子关系自动计算变换
- 纹理管理：自动批量渲染相同纹理
- 内置动画：补间动画、精灵表动画
- 事件系统：点击、拖动、悬停

### 3. 瓦片地图支持

PixiJS 可以高效渲染瓦片地图：

```typescript
// 使用 TileSprite 或批量渲染
function renderMap(mapData: number[][], tileSize: number) {
  const container = new PIXI.Container()

  // 预加载纹理
  const tileTextures = {
    0: PIXI.Texture.from('grass.png'),
    1: PIXI.Texture.from('water.png'),
    2: PIXI.Texture.from('mountain.png')
  }

  // 批量创建精灵
  for (let y = 0; y < mapData.length; y++) {
    for (let x = 0; x < mapData[y].length; x++) {
      const tileType = mapData[y][x]
      const tile = new PIXI.Sprite(tileTextures[tileType])
      tile.x = x * tileSize
      tile.y = y * tileSize
      container.addChild(tile)
    }
  }

  return container
}
```

**优化**:
- 视口裁剪：只渲染可见区域的瓦片
- 纹理图集：将多个纹理合并到一张图，减少绘制调用
- 批量渲染：PixiJS 自动批量渲染相同材质

### 4. 视口管理（pixi-viewport）

PixiJS 有优秀的视口插件 `pixi-viewport`，支持地图缩放、拖动：

```typescript
import { Viewport } from 'pixi-viewport'

const viewport = new Viewport({
  screenWidth: 1920,
  screenHeight: 1080,
  worldWidth: 10000,
  worldHeight: 10000,
  interaction: app.renderer.plugins.interaction
})

// 启用功能
viewport
  .drag()        // 拖动地图
  .pinch()       // 双指缩放
  .wheel()       // 鼠标滚轮缩放
  .decelerate()  // 惯性滚动
  .clampZoom({   // 限制缩放范围
    minScale: 0.5,
    maxScale: 2.0
  })

app.stage.addChild(viewport)

// 所有游戏对象添加到 viewport
viewport.addChild(mapLayer)
viewport.addChild(avatarLayer)
```

**优点**:
- 开箱即用（无需自己实现）
- 平滑滚动（惯性、边界弹性）
- 触摸支持（移动端适配）

### 5. Vue 3 集成优秀

PixiJS 有官方 Vue 3 集成库 `vue3-pixi`：

```vue
<script setup lang="ts">
import { Application, Container, Sprite } from 'vue3-pixi'
import { ref } from 'vue'

const avatars = ref<Avatar[]>([])

function onAvatarClick(avatar: Avatar) {
  console.log(`Clicked on ${avatar.name}`)
}
</script>

<template>
  <Application :width="1920" :height="1080">
    <Container>
      <!-- 瓦片地图 -->
      <Sprite
        v-for="(tile, idx) in tiles"
        :key="idx"
        :texture="tile.texture"
        :x="tile.x"
        :y="tile.y"
      />

      <!-- 角色精灵 -->
      <Sprite
        v-for="avatar in avatars"
        :key="avatar.id"
        :texture="avatar.portrait"
        :x="avatar.x"
        :y="avatar.y"
        :interactive="true"
        @pointerdown="onAvatarClick(avatar)"
      />
    </Container>
  </Application>
</template>
```

**优点**:
- 声明式：像写 HTML 一样写 Canvas 渲染
- 响应式：自动同步 Vue 状态到 PixiJS
- 组件化：可以拆分成多个 PixiJS 组件

### 6. 生态丰富

PixiJS 生态丰富，有大量插件：
- **pixi-viewport**: 视口管理（缩放、拖动）
- **@pixi/particle-emitter**: 粒子系统（特效）
- **pixi-filters**: 滤镜（模糊、发光）
- **@pixi/sound**: 音频播放
- **pixi-spine**: Spine 骨骼动画

## 权衡

### 优点
- ✅ 性能优秀（WebGL 硬件加速）
- ✅ 精灵系统强大
- ✅ 瓦片地图支持好
- ✅ 视口管理插件成熟
- ✅ Vue 3 集成优秀
- ✅ 生态丰富（插件多）
- ✅ 文档完善（官方文档 + 社区教程）
- ✅ 学习曲线平缓（API 简单）

### 缺点
- ❌ 只支持 2D（但我们不需要 3D）
- ❌ 包体积较大（~500KB gzipped，但可以按需加载）

## 替代方案

### 原生 Canvas API
- **优点**: 无需依赖、包体积小、浏览器原生支持
- **缺点**:
  - 性能差（无 WebGL 加速）
  - 需要手动管理精灵（变换、碰撞检测）
  - 没有精灵树（Scene Graph）
  - 交互需要自己实现

**为什么不选**: 性能不够，开发效率低。

### Three.js
- **优点**: 3D 渲染、生态最大、功能最强
- **缺点**:
  - 过于复杂（3D 相机、灯光、材质）
  - 性能开销大（3D 渲染成本高）
  - 2D 游戏用 3D 引擎是杀鸡用牛刀
  - 学习曲线陡峭

**为什么不选**: 我们只需要 2D，Three.js 过于复杂。

### Phaser
- **优点**: 完整的游戏引擎、内置物理引擎、音频系统、场景管理
- **缺点**:
  - 太重（我们不需要物理引擎、音频系统）
  - 与 Vue 3 集成不好（Phaser 自己管理 DOM）
  - API 较复杂（学习曲线陡峭）
  - 文档不够完善（相比 PixiJS）

**为什么不选**: 功能过多，我们只需要渲染引擎。

## 后果

### 正面
- 渲染 100+ 个 NPC 时仍然保持 60fps
- vue3-pixi 让开发体验极佳（声明式 Canvas）
- pixi-viewport 让地图交互开箱即用
- 精灵系统让角色管理简单（Scene Graph）

### 负面
- 需要学习 PixiJS API（已通过文档和示例解决）
- 包体积增加 ~500KB（但对现代网络可接受）

## 经验教训
- 使用视口裁剪（Viewport culling）可以大幅提升性能
- 纹理图集（Texture Atlas）可以减少绘制调用
- PixiJS v8 的性能比 v7 提升 30%+（更好的批量渲染）
- 像素风游戏必须关闭 `antialias`（否则模糊）

## 未来优化方向
- [ ] 使用 WebWorker 进行地图预渲染
- [ ] 使用 OffscreenCanvas 提升性能
- [ ] 引入精灵池（Sprite Pool）减少 GC
- [ ] 使用 PixiJS 的 ParticleContainer 渲染大量静态精灵

## 相关决策
- [ADR-002: 选择 Vue 3 作为前端框架](ADR-002-frontend-framework.md)
- [ADR-005: 前后端状态同步方案](ADR-005-state-management.md)

---

**创建时间**: 2026-02-01
**作者**: 前端团队
**审核**: ✅
