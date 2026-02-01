# ADR-005: 前后端状态同步方案

## 状态
✅ 已采纳

## 上下文
修仙世界模拟器是一个实时游戏，后端每秒推进游戏时间（一个游戏月），前端需要实时显示：
- **游戏时间**: 当前年月
- **角色状态**: 位置、动作、生命值、境界
- **事件流**: 新发生的事件（突破、战斗、死亡等）
- **世界现象**: 灵气复苏、天地异象等

### 需求
1. **实时性**: 延迟 < 100ms
2. **高效性**: 不能每次都传输全部数据（浪费带宽）
3. **可靠性**: 网络断开时能自动重连
4. **可扩展性**: 支持多个客户端同时连接

### 数据量
- **初始数据**: ~10MB（地图 + 100 个角色完整数据）
- **增量更新**: ~10KB/秒（只传变更的角色和事件）

## 决策
采用 **WebSocket 实时推送 + 增量更新** 方案。

## 架构设计

### 1. WebSocket 连接管理

#### 后端（FastAPI + Starlette）

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """接受新连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """广播消息到所有客户端"""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to client: {e}")
                dead_connections.append(connection)

        # 清理死连接
        for connection in dead_connections:
            self.disconnect(connection)

# 全局连接管理器
manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点"""
    await manager.connect(websocket)
    try:
        # 保持连接（接收客户端心跳）
        while True:
            data = await websocket.receive_text()
            # 可以处理客户端发来的消息（如心跳、命令）
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

#### 前端（Vue 3 + WebSocket API）

```typescript
// composables/useWebSocket.ts
import { ref, onMounted, onUnmounted } from 'vue'

export function useWebSocket() {
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const messageHandlers: Array<(msg: any) => void> = []

  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${window.location.host}/ws`

    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      console.log('WebSocket connected')
      isConnected.value = true
    }

    ws.value.onmessage = (event) => {
      const message = JSON.parse(event.data)
      // 分发消息到所有监听器
      messageHandlers.forEach(handler => handler(message))
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.value.onclose = () => {
      console.log('WebSocket disconnected')
      isConnected.value = false
      // 自动重连（3 秒后）
      setTimeout(() => {
        console.log('Reconnecting...')
        connect()
      }, 3000)
    }
  }

  function onMessage(handler: (msg: any) => void) {
    messageHandlers.push(handler)
  }

  function send(message: any) {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(message))
    }
  }

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    ws.value?.close()
  })

  return { isConnected, onMessage, send }
}
```

### 2. 增量更新策略

#### 游戏循环推送（后端）

```python
async def game_loop():
    """游戏主循环"""
    while True:
        if is_paused:
            await asyncio.sleep(0.1)
            continue

        # 执行一步模拟
        events = await simulator.step()

        # 收集状态变更
        updates = collect_state_changes()

        # 构造增量更新消息
        message = {
            "type": "tick",
            "year": world.current_year,
            "month": world.current_month,
            "events": serialize_events(events),  # 新事件
            "avatars": updates["avatars"],        # 变更的角色
            "newly_born": updates["newly_born"],  # 新生角色 ID
            "newly_dead": updates["newly_dead"],  # 死亡角色 ID
            "phenomenon": world.current_phenomenon.to_dict() if world.current_phenomenon else None
        }

        # 广播到所有客户端
        await manager.broadcast(message)

        # 控制推送频率（1 秒 1 次）
        await asyncio.sleep(1.0)

def collect_state_changes() -> dict:
    """收集状态变更（增量）"""
    return {
        "avatars": [
            {
                "id": avatar.id,
                "x": avatar.x,
                "y": avatar.y,
                "action_emoji": avatar.current_action_emoji,
                "hp": avatar.hp,
                "realm": avatar.realm.value,
                # 只传输必要字段
            }
            for avatar in world.living_avatars
            if avatar.has_changed  # 只传输变更的角色
        ],
        "newly_born": [a.id for a in world.newly_born_avatars],
        "newly_dead": [a.id for a in world.newly_dead_avatars]
    }
```

#### 前端状态更新（增量合并）

```typescript
// stores/gameStore.ts
import { defineStore } from 'pinia'
import { useWebSocket } from '@/composables/useWebSocket'

export const useGameStore = defineStore('game', () => {
  const year = ref(100)
  const month = ref(1)
  const avatars = ref<Map<string, Avatar>>(new Map())

  const { onMessage } = useWebSocket()

  onMessage((msg) => {
    if (msg.type === 'tick') {
      // 更新时间
      year.value = msg.year
      month.value = msg.month

      // 增量更新角色
      msg.avatars.forEach((update: any) => {
        const existing = avatars.value.get(update.id)
        if (existing) {
          // 合并变更（只更新变化的字段）
          Object.assign(existing, update)
        } else {
          // 新角色（从 newly_born）
          avatars.value.set(update.id, update)
        }
      })

      // 移除死亡角色
      msg.newly_dead?.forEach((id: string) => {
        avatars.value.delete(id)
      })

      // 添加新生角色
      msg.newly_born?.forEach((id: string) => {
        // 需要异步加载完整数据
        fetchAvatarDetail(id)
      })
    }
  })

  return { year, month, avatars }
})
```

### 3. 初始数据加载（HTTP REST）

初始数据量大，通过 HTTP REST API 加载：

```typescript
// 前端初始化流程
async function initializeGame() {
  // 1. 建立 WebSocket 连接（自动）
  const { isConnected } = useWebSocket()
  await until(isConnected).toBe(true)

  // 2. 加载地图数据（只加载一次）
  const mapData = await gameAPI.getMap()
  worldStore.setMap(mapData)

  // 3. 加载初始游戏状态
  const state = await gameAPI.getState()
  gameStore.setYear(state.year)
  gameStore.setMonth(state.month)
  gameStore.setAvatars(state.avatars)

  // 4. 开始接收增量更新（WebSocket）
  console.log('Game initialized')
}
```

**为什么分离？**
- **地图**: 只加载一次（不变）
- **初始状态**: HTTP 加载（较大）
- **实时更新**: WebSocket 推送（小且频繁）

### 4. 事件流分页加载

事件数量巨大，使用分页查询（HTTP REST）：

```typescript
// 前端分页加载事件
async function loadMoreEvents(cursor?: number) {
  const response = await eventAPI.getEvents({
    avatar_id: selectedAvatarId.value,
    cursor: cursor,  // 上次最后一条事件的 month_stamp
    limit: 50        // 每次加载 50 条
  })

  events.value.push(...response.events)
  hasMore.value = response.has_more

  return response.cursor  // 返回新 cursor
}
```

**为什么不用 WebSocket？**
- 历史事件不需要实时推送
- 分页查询更高效（按需加载）
- HTTP REST 有缓存（浏览器缓存 + CDN）

### 5. 冲突解决

#### 客户端主动操作

用户主动操作（如创建角色、设置目标）通过 HTTP POST：

```typescript
// 用户创建角色
async function createAvatar(data: CreateAvatarRequest) {
  // 发送 HTTP POST 请求
  const response = await avatarAPI.createAvatar(data)

  // 等待 WebSocket 推送新角色
  // 不需要立即添加到本地状态（避免冲突）
  return response
}
```

**冲突处理**:
- **客户端操作 → HTTP POST → 后端处理 → WebSocket 广播**
- 所有状态变更都由服务器推送（客户端不自行修改）
- 避免客户端和服务器状态不一致

#### 网络断开恢复

```typescript
// WebSocket 重连后重新加载状态
ws.value.onopen = async () => {
  console.log('WebSocket reconnected')

  // 重新加载当前状态（避免丢失数据）
  const state = await gameAPI.getState()
  gameStore.syncState(state)
}
```

## 权衡

### 优点
- ✅ 实时性高（WebSocket 延迟 < 100ms）
- ✅ 带宽效率高（增量更新，每秒 ~10KB）
- ✅ 自动重连（网络断开不影响游戏）
- ✅ 多客户端支持（广播机制）
- ✅ 职责清晰（初始加载用 HTTP，实时更新用 WebSocket）

### 缺点
- ❌ WebSocket 需要维持长连接（服务器资源占用）
- ❌ 需要处理网络不稳定（重连、数据丢失）

## 替代方案

### 方案 1: 轮询（HTTP Polling）
- **优点**: 实现简单、无需 WebSocket
- **缺点**:
  - 延迟高（轮询间隔至少 1 秒）
  - 带宽浪费（大部分请求无新数据）
  - 服务器压力大（大量无效请求）

**为什么不选**: 延迟高，带宽浪费。

### 方案 2: Server-Sent Events (SSE)
- **优点**: 单向推送、HTTP 协议、自动重连
- **缺点**:
  - 只能服务器 → 客户端（不支持客户端 → 服务器）
  - 浏览器连接数限制（HTTP/1.1 最多 6 个）
  - 不支持二进制数据

**为什么不选**: 单向通信不够灵活。

### 方案 3: 全量推送（每次推送完整状态）
- **优点**: 实现简单、无需增量合并
- **缺点**:
  - 带宽浪费（每次 ~10MB）
  - 性能差（JSON 序列化/反序列化慢）

**为什么不选**: 带宽消耗太大。

## 后果

### 正面
- WebSocket 推送延迟 < 100ms，游戏体验流畅
- 增量更新带宽效率高（~10KB/秒）
- 自动重连机制可靠（网络不稳定也能玩）
- 多客户端同时观看同一个世界

### 负面
- 需要处理 WebSocket 断线重连
- 增量合并需要小心（避免状态不一致）

## 经验教训
- WebSocket 心跳包很重要（检测死连接）
- 增量更新需要标记哪些字段变更（避免传输不必要的数据）
- 客户端操作必须通过 HTTP POST（避免冲突）
- 重连后需要重新同步状态（避免数据丢失）

## 未来优化方向
- [ ] 引入消息队列（Redis Pub/Sub）支持分布式部署
- [ ] 使用二进制协议（如 MessagePack）压缩数据
- [ ] 引入差异算法（Diff）进一步减少传输量
- [ ] 支持客户端缓存（Service Worker）

## 相关决策
- [ADR-001: 选择 FastAPI 作为后端框架](ADR-001-web-framework.md)（WebSocket 原生支持）
- [ADR-002: 选择 Vue 3 作为前端框架](ADR-002-frontend-framework.md)
- [ADR-006: 选择 SQLite + JSON 作为存储方案](ADR-006-storage.md)（事件分页查询）

---

**创建时间**: 2026-02-01
**作者**: 全栈团队
**审核**: ✅
