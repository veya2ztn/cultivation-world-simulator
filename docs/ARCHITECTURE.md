# 修仙世界模拟器 - 系统架构文档

## 📋 文档信息
- **版本**: v1.0
- **最后更新**: 2026-02-01
- **维护者**: AI 开发团队
- **状态**: 活跃开发中

---

## 🎯 系统概述

### 项目愿景
创造一个真正"活着"的修仙世界，每个 NPC 都由大语言模型驱动，拥有独立的意识、记忆和目标。世界遵循严谨的修仙规则运行，剧情由 AI 和规则共同编织，自然涌现。

### 核心特性
1. **AI 驱动的 NPC**: 每个角色都有独立的 LLM 智能
2. **双层 AI 架构**: 规则 AI（确定性）+ LLM AI（创造性）
3. **实时模拟**: 异步游戏循环，WebSocket 实时推送
4. **完整的修仙体系**: 境界、功法、宗门、天劫、秘境等
5. **涌现式剧情**: 无预设剧本，一切由因果推演

### 技术栈总览

| 层次 | 技术选型 | 版本 | 选择理由 |
|------|---------|------|---------|
| **后端框架** | FastAPI | 0.100+ | 异步支持、WebSocket、自动文档 |
| **语言** | Python | 3.10+ | 生态丰富、LLM SDK 支持好 |
| **前端框架** | Vue 3 | 3.x | Composition API、TypeScript 支持 |
| **渲染引擎** | PixiJS | 8.x | 高性能 2D 渲染、硬件加速 |
| **状态管理** | Pinia | 3.x | Vue 3 官方推荐 |
| **构建工具** | Vite | 5.x | 极速 HMR、原生 ESM |
| **UI 库** | Naive UI | 2.x | Vue 3 原生、TypeScript 友好 |
| **数据存储** | SQLite + JSON | - | 轻量级、无需额外部署 |
| **LLM 集成** | OpenAI SDK | - | 兼容多种 LLM 提供商 |
| **配置管理** | OmegaConf | 2.3+ | YAML 配置、灵活合并 |
| **测试** | pytest + Vitest | - | 异步支持、覆盖率报告 |

---

## 🏗️ 系统架构

### 整体架构图

```
┌────────────────────────────────────────────────────────────────┐
│                         用户浏览器                                │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Vue 3 前端应用 (SPA)                                     │    │
│  │  ├─ PixiJS Canvas (游戏世界渲染)                          │    │
│  │  ├─ Naive UI 组件 (面板、菜单)                            │    │
│  │  ├─ Pinia Store (状态管理)                               │    │
│  │  └─ WebSocket Client (实时通信)                          │    │
│  └────────────────────────────────────────────────────────┘    │
└───────────────┬────────────────────────────────────────────────┘
                │ HTTP/HTTPS + WebSocket
                │
┌───────────────▼────────────────────────────────────────────────┐
│                    FastAPI 后端服务器                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Layer (RESTful + WebSocket)                        │  │
│  │  ├─ /api/state      (游戏状态查询)                        │  │
│  │  ├─ /api/events     (事件分页查询)                        │  │
│  │  ├─ /api/control/*  (游戏控制)                            │  │
│  │  ├─ /ws             (WebSocket 实时推送)                  │  │
│  │  └─ /api/config/*   (配置管理)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Game Loop (异步后台循环)                                 │  │
│  │                                                            │  │
│  │  每秒执行一次:                                             │  │
│  │    1. 检查是否暂停                                         │  │
│  │    2. 调用 Simulator.step() 推进一个游戏月                │  │
│  │    3. 收集状态变更（新生、死亡、位置更新）                   │  │
│  │    4. 通过 WebSocket 广播到所有客户端                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  核心游戏引擎 (Simulator)                                  │  │
│  │                                                            │  │
│  │  Simulator.step() 流程:                                   │  │
│  │    ┌──────────────────────────────────────────────┐       │  │
│  │    │ 1. 月份 +1 (时间推进)                          │       │  │
│  │    └──────────────────────────────────────────────┘       │  │
│  │    ┌──────────────────────────────────────────────┐       │  │
│  │    │ 2. 遍历所有活着的 NPC                          │       │  │
│  │    │    ├─ 年龄增长、寿元检查                      │       │  │
│  │    │    ├─ 长期动作进度更新                        │       │  │
│  │    │    └─ AI 决策下一步动作                       │       │  │
│  │    └──────────────────────────────────────────────┘       │  │
│  │    ┌──────────────────────────────────────────────┐       │  │
│  │    │ 3. 执行所有新动作                              │       │  │
│  │    │    ├─ 短动作: 立即执行                        │       │  │
│  │    │    └─ 长动作: 记录开始时间                    │       │  │
│  │    └──────────────────────────────────────────────┘       │  │
│  │    ┌──────────────────────────────────────────────┐       │  │
│  │    │ 4. 结算完成的长期动作                          │       │  │
│  │    └──────────────────────────────────────────────┘       │  │
│  │    ┌──────────────────────────────────────────────┐       │  │
│  │    │ 5. 处理多人动作响应                            │       │  │
│  │    └──────────────────────────────────────────────┘       │  │
│  │    ┌──────────────────────────────────────────────┐       │  │
│  │    │ 6. 生成世界事件                                │       │  │
│  │    │    ├─ 天地灵机变化                            │       │  │
│  │    │    ├─ 秘境开启                                │       │  │
│  │    │    └─ 拍卖会、比武大会等                      │       │  │
│  │    └──────────────────────────────────────────────┘       │  │
│  │    ┌──────────────────────────────────────────────┐       │  │
│  │    │ 7. 返回事件列表                                │       │  │
│  │    └──────────────────────────────────────────────┘       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  数据层                                                    │  │
│  │  ├─ World (游戏世界状态)                                  │  │
│  │  ├─ AvatarManager (角色管理)                              │  │
│  │  ├─ EventManager (事件管理 → SQLite)                     │  │
│  │  └─ GatheringManager (秘境、拍卖会等)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────┬────────────────────────────────────────────────┘
                │ LLM API Calls
                │
┌───────────────▼────────────────────────────────────────────────┐
│           LLM Provider (OpenAI/DeepSeek/Ollama)                │
│                                                                  │
│  用于:                                                           │
│  • NPC 复杂决策（是否加入宗门、与谁结交等）                        │
│  • 对话生成（角色间交流）                                         │
│  • 小剧场生成（战斗、对话的文字描述）                              │
│  • 历史背景应用（根据用户设定的世界历史生成初始状态）                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🧩 模块划分

### 后端模块

#### 1. 服务器层 (`src/server/`)
- **main.py** (1870 行): FastAPI 应用入口
  - API 路由定义
  - WebSocket 连接管理
  - 游戏循环启动
  - 静态文件服务

**关键职责**:
- 接收前端请求并返回游戏状态
- 通过 WebSocket 推送实时更新
- 初始化游戏世界
- 管理游戏生命周期（暂停/恢复/保存/加载）

#### 2. 模拟器层 (`src/sim/`)
- **simulator.py**: 游戏模拟器核心
  - `Simulator.step()`: 推进游戏一个月
  - 协调各个子系统运行
- **save/**: 存档系统
  - `save_game.py`: 序列化世界状态到 JSON + SQLite
- **load/**: 加载系统
  - `load_game.py`: 反序列化存档

**关键职责**:
- 驱动游戏世界时间流逝
- 协调 NPC AI 决策
- 生成和结算事件

#### 3. 游戏实体层 (`src/classes/`)

##### 核心类

| 类名 | 文件 | 职责 |
|------|------|------|
| `World` | `world.py` | 游戏世界容器，持有地图、角色、事件管理器 |
| `Avatar` | `avatar/avatar.py` | 角色实体，包含属性、状态、AI |
| `AvatarManager` | `avatar_manager.py` | 管理所有角色的生命周期 |
| `Sect` | `sect.py` | 宗门，包含功法、成员、行事风格 |
| `Action` | `action/base.py` | 动作基类 |
| `Event` | `event.py` | 事件实体 |
| `EventManager` | `event_manager.py` | 事件管理，SQLite 持久化 |
| `Map` | `map.py` | 游戏地图，瓦片和区域 |
| `Region` | `region.py` | 区域（城市、宗门、洞府） |

##### 动作系统 (`action/`)
继承结构：
```
Action (抽象基类)
├─ Move (移动)
├─ Cultivate (修炼)
├─ Breakthrough (突破)
├─ Rest (疗伤)
├─ Trade (交易)
├─ Battle (战斗)
├─ Dialogue (对话)
├─ Forge (铸造)
├─ Alchemy (炼丹)
└─ ...
```

**动作类型**:
- **短动作**: 立即执行完成（如移动）
- **长动作**: 持续多个月（如修炼、闭关）
- **多人动作**: 需要对方响应（如战斗、对话）

#### 4. AI 系统 (`src/classes/ai.py` + `src/utils/llm/`)

**双层 AI 架构**:

```python
# 决策流程
if avatar.should_use_llm_ai():  # 根据觉醒率
    # LLM AI: 创造性决策
    action = await llm_decide_action(avatar)
else:
    # 规则 AI: 确定性决策
    action = rule_based_decide(avatar)
```

**规则 AI** (`src/classes/ai.py`):
- 基于条件的决策树
- 处理生存需求（疗伤、突破）
- 快速、确定、可预测

**LLM AI** (`src/utils/llm/client.py`):
- 调用 LLM API 做复杂决策
- 提示词包含：角色状态、记忆、周围环境、长短期目标
- 返回 JSON，解析后执行动作
- 容错：失败时回退到规则 AI

#### 5. 工具层 (`src/utils/`)
- **config.py**: 配置加载和管理（OmegaConf）
- **llm/**: LLM 客户端封装
  - `client.py`: API 调用
  - `config.py`: LLM 配置（模式切换）
- **df.py**: CSV 数据加载
- **protagonist.py**: 主角生成逻辑

---

### 前端模块

#### 1. 组件层 (`web/src/components/`)

##### 游戏组件 (`game/`)
- **GameMap.vue**: PixiJS 地图渲染
  - 瓦片地形
  - 角色精灵
  - 区域标记

- **AvatarSprite.vue**: 角色精灵
  - 头像显示
  - 动作表情（emoji）
  - 点击交互

##### 面板组件 (`panels/`)
- **AvatarPanel.vue**: 角色详情面板
- **EventPanel.vue**: 事件列表面板
- **SectPanel.vue**: 宗门详情面板
- **MapPanel.vue**: 地图导航面板

##### 布局组件 (`layout/`)
- **MainLayout.vue**: 主布局
- **TopBar.vue**: 顶部工具栏

##### 系统组件
- **SystemMenu.vue**: 系统菜单（保存、加载、设置）
- **LoadingOverlay.vue**: 加载进度覆盖层
- **SplashLayer.vue**: 开始界面

#### 2. 状态管理 (`web/src/stores/`)
使用 Pinia 管理全局状态：

- **gameStore.ts**: 游戏状态
  - 当前年月
  - 是否暂停
  - 初始化状态

- **avatarStore.ts**: 角色状态
  - 所有角色数据
  - 选中的角色

- **eventStore.ts**: 事件状态
  - 最近事件列表
  - 分页加载

- **configStore.ts**: 配置状态
  - LLM 配置
  - 语言设置

#### 3. API 层 (`web/src/api/`)
封装所有后端 API 调用：

```typescript
// api/game.ts
export const gameAPI = {
  getState: () => axios.get('/api/state'),
  pause: () => axios.post('/api/control/pause'),
  resume: () => axios.post('/api/control/resume'),
  save: () => axios.post('/api/game/save'),
  load: (filename: string) => axios.post('/api/game/load', { filename })
}

// api/avatar.ts
export const avatarAPI = {
  getDetail: (id: string) => axios.get(`/api/detail?type=avatar&id=${id}`),
  createAvatar: (data: CreateAvatarRequest) =>
    axios.post('/api/action/create_avatar', data)
}
```

---

## 🔄 数据流详解

### 1. 游戏启动流程

```
用户访问 http://localhost:8123
  ↓
前端加载
  ↓
建立 WebSocket 连接 → 后端 /ws
  ↓
前端请求游戏状态 → GET /api/init-status
  ↓
后端检查初始化状态
  ├─ 如果 idle: 前端显示"开始游戏"菜单
  ├─ 如果 in_progress: 前端显示加载进度
  └─ 如果 ready: 前端请求地图和初始数据
      ↓
      GET /api/map (地图数据，只请求一次)
      GET /api/state (当前游戏状态)
      ↓
      前端渲染游戏世界
      ↓
      用户点击"开始"
      ↓
      POST /api/control/resume
      ↓
      后端 game_loop 开始推送 tick 消息
```

### 2. 游戏循环数据流

```
game_loop (每秒一次)
  ↓
检查 is_paused → 如果暂停则跳过
  ↓
await sim.step()
  ↓
  ┌─────────────────────────────────────┐
  │ Simulator.step() 内部流程            │
  ├─────────────────────────────────────┤
  │ 1. world.month_stamp += 1           │
  │ 2. for avatar in living_avatars:    │
  │      avatar.age += 1/12             │
  │      avatar.update_actions()        │
  │      avatar.decide_next_action()    │
  │         ↓                            │
  │      if needs_llm:                  │
  │         call LLM API ────────┐      │
  │      else:                   │      │
  │         rule_based_ai()      │      │
  │ 3. execute_all_actions()     │      │
  │ 4. settle_long_actions()     │      │
  │ 5. handle_gatherings()       │      │
  │ 6. generate_events()         │      │
  │ 7. return events             │      │
  └─────────────────┬────────────┘      │
                    │                   │
                    ▼                   ▼
              返回事件列表       LLM Provider
                    │                (异步调用)
                    ↓                   │
收集状态变更:                            │
  - newly_born_ids                     │
  - newly_dead_ids                     │
  - avatar_updates (位置、动作)          │
                    │                   │
                    ↓                   │
构造广播消息:      ◄─────────────────────┘
{
  type: "tick",
  year: 100,
  month: 5,
  events: [...],
  avatars: [...],
  phenomenon: {...}
}
                    ↓
await manager.broadcast(message)
                    ↓
        所有连接的 WebSocket 客户端
                    ↓
           前端更新 UI
```

### 3. 用户交互流程

#### 例子：查看角色详情

```
用户点击地图上的角色
  ↓
前端触发 onClick 事件
  ↓
avatarStore.selectAvatar(avatarId)
  ↓
打开 AvatarPanel
  ↓
发起 API 请求: GET /api/detail?type=avatar&id=xxx
  ↓
后端查询 world.avatar_manager.get_avatar(id)
  ↓
调用 avatar.get_structured_info()
  ↓
返回 JSON:
{
  "basic": { name, realm, age, ... },
  "cultivation": { progress, technique, ... },
  "items": { weapons, auxiliaries, elixirs, ... },
  "relationships": [...],
  "memories": [...],
  "objectives": [...]
}
  ↓
前端渲染面板
```

#### 例子：设置角色目标

```
用户在 AvatarPanel 输入目标文本
  ↓
点击"设置目标"按钮
  ↓
POST /api/action/set_long_term_objective
{
  "avatar_id": "xxx",
  "content": "加入青云门"
}
  ↓
后端调用 set_user_long_term_objective(avatar, content)
  ↓
avatar.objectives.add(UserObjective(...))
  ↓
返回成功
  ↓
前端显示提示："目标已设置"
  ↓
下次 AI 决策时会考虑这个目标
```

---

## 💾 数据存储

### 存档格式

每个存档包含两个文件：

```
assets/saves/
├── save_20260201_1430.json       # 世界状态（JSON）
└── save_20260201_1430.db         # 事件数据库（SQLite）
```

#### JSON 文件结构

```json
{
  "meta": {
    "version": "0.1.0",
    "save_time": "2026-02-01 14:30:00",
    "game_time": "Year 150, Month 3",
    "language": "zh-CN"
  },
  "world": {
    "month_stamp": 1803,  // Year 150, Month 3
    "map": { ... },
    "current_phenomenon": { ... }
  },
  "avatars": [
    {
      "id": "uuid-xxx",
      "name": "张三",
      "realm": "GOLDEN_CORE",
      "level": 15,
      "age": 125,
      "sect_id": 1,
      "pos_x": 50,
      "pos_y": 30,
      "cultivation_progress": { ... },
      "items": { ... },
      "relationships": [ ... ],
      "memories": [ ... ]
    },
    // ... 其他角色
  ],
  "sects": [ ... ],
  "regions": [ ... ]
}
```

#### SQLite 数据库结构

```sql
-- events 表
CREATE TABLE events (
    id TEXT PRIMARY KEY,
    month_stamp INTEGER NOT NULL,
    year INTEGER,
    month INTEGER,
    content TEXT NOT NULL,
    is_major INTEGER DEFAULT 0,
    is_story INTEGER DEFAULT 0,
    created_at REAL
);

-- event_avatars 关联表（多对多）
CREATE TABLE event_avatars (
    event_id TEXT NOT NULL,
    avatar_id TEXT NOT NULL,
    PRIMARY KEY (event_id, avatar_id)
);

-- 索引
CREATE INDEX idx_events_month_stamp ON events(month_stamp);
CREATE INDEX idx_events_major ON events(is_major);
CREATE INDEX idx_event_avatars_avatar ON event_avatars(avatar_id);
```

**为什么分离事件存储？**
- 事件数量巨大（上万条），JSON 性能差
- SQLite 支持高效的分页查询
- 支持按角色、时间范围筛选

---

## 🔌 API 接口设计

### RESTful API

#### 游戏控制

| 端点 | 方法 | 描述 | 请求 | 响应 |
|-----|------|------|------|------|
| `/api/state` | GET | 获取游戏快照 | - | `{ year, month, avatars[], events[] }` |
| `/api/control/pause` | POST | 暂停游戏 | - | `{ status: "ok" }` |
| `/api/control/resume` | POST | 恢复游戏 | - | `{ status: "ok" }` |
| `/api/control/reset` | POST | 重置游戏 | - | `{ status: "ok" }` |

#### 数据查询

| 端点 | 方法 | 描述 | 查询参数 |
|-----|------|------|---------|
| `/api/detail` | GET | 获取实体详情 | `type`, `id` |
| `/api/events` | GET | 分页查询事件 | `avatar_id`, `cursor`, `limit` |
| `/api/map` | GET | 获取地图数据 | - |

#### 角色管理

| 端点 | 方法 | 描述 |
|-----|------|------|
| `/api/action/create_avatar` | POST | 创建新角色 |
| `/api/action/delete_avatar` | POST | 删除角色 |
| `/api/action/set_long_term_objective` | POST | 设置目标 |

#### 存档系统

| 端点 | 方法 | 描述 |
|-----|------|------|
| `/api/saves` | GET | 获取存档列表 |
| `/api/game/save` | POST | 保存游戏 |
| `/api/game/load` | POST | 加载存档 |

#### 配置管理

| 端点 | 方法 | 描述 |
|-----|------|------|
| `/api/config/llm` | GET | 获取 LLM 配置 |
| `/api/config/llm/save` | POST | 保存 LLM 配置 |
| `/api/config/llm/test` | POST | 测试 LLM 连接 |
| `/api/config/language` | GET/POST | 语言设置 |

### WebSocket 协议

#### 连接
```
ws://localhost:8002/ws
```

#### 服务端推送消息类型

##### 1. tick 消息（游戏循环）
```json
{
  "type": "tick",
  "year": 150,
  "month": 3,
  "events": [
    {
      "id": "evt-xxx",
      "content": "张三突破到金丹期",
      "is_major": true,
      "related_avatar_ids": ["uuid-xxx"]
    }
  ],
  "avatars": [
    {
      "id": "uuid-xxx",
      "name": "张三",
      "x": 50,
      "y": 30,
      "action_emoji": "🧘"
    }
  ],
  "phenomenon": {
    "id": 1,
    "name": "灵气复苏",
    "rarity": "SR"
  }
}
```

##### 2. llm_config_required 消息
```json
{
  "type": "llm_config_required",
  "error": "LLM 连接失败，请配置 API"
}
```

##### 3. toast 消息
```json
{
  "type": "toast",
  "level": "info",
  "message": "存档已保存"
}
```

---

## ⚙️ 配置系统

### 配置文件优先级

```
1. static/default_config.yml    (默认配置，不要修改)
2. static/game_config.yml        (游戏规则配置)
3. static/local_config.yml       (用户配置，优先级最高)
```

### 关键配置项

```yaml
# LLM 配置
llm:
  base_url: "https://api.deepseek.com"
  key: "sk-xxx"
  model_name: "deepseek-chat"      # 智能模型（复杂决策）
  fast_model_name: "deepseek-chat" # 快速模型（简单任务）
  mode: "default"                  # default/normal/fast

# 游戏参数
game:
  init_npc_num: 12                 # 初始 NPC 数量
  sect_num: 3                      # 宗门数量
  start_year: 100                  # 起始年份
  npc_awakening_rate_per_month: 0.01  # NPC 激活 LLM 概率
  world_history: ""                # 世界背景设定

# 角色配置
avatar:
  protagonist: "none"              # none/random/all

# 系统配置
system:
  language: "zh-CN"                # zh-CN/en-US

# 路径配置（自动生成，不要手动修改）
paths:
  assets: "assets/zh-CN"
  saves: "assets/saves"
```

---

## 🧪 测试策略

### 后端测试

使用 pytest + pytest-asyncio：

```python
# tests/test_avatar.py
import pytest
from src.classes.avatar import Avatar

@pytest.fixture
def test_avatar():
    return Avatar(name="测试角色", realm=Realm.QI_REFINING)

async def test_cultivation_speed(test_avatar):
    """测试修炼速度计算"""
    speed = test_avatar.calculate_cultivation_speed()
    assert speed > 0

async def test_breakthrough(test_avatar):
    """测试境界突破"""
    test_avatar.cultivation_exp = 1000
    result = await test_avatar.attempt_breakthrough()
    assert result.success is True
```

**覆盖率要求**:
- 核心逻辑（Avatar, Simulator）> 80%
- 工具函数 > 70%

### 前端测试

使用 Vitest + Vue Testing Library：

```typescript
// web/src/__tests__/AvatarPanel.test.ts
import { mount } from '@vue/test-utils'
import AvatarPanel from '@/components/panels/AvatarPanel.vue'

describe('AvatarPanel', () => {
  it('renders avatar info', () => {
    const wrapper = mount(AvatarPanel, {
      props: {
        avatarId: 'test-id'
      }
    })
    expect(wrapper.text()).toContain('张三')
  })
})
```

---

## 🚀 部署架构

### 开发环境
```
Python 后端 (localhost:8002)
  +
Vite 开发服务器 (localhost:5173)
```

### Docker 部署
```
┌─────────────────────┐      ┌──────────────────────┐
│  Frontend Container │      │  Backend Container   │
│  (Nginx)            │      │  (Uvicorn)           │
│  Port: 8123         │◄────►│  Port: 8002          │
└─────────────────────┘      └──────────────────────┘
         │                            │
         │                            │
         └────────────────┬───────────┘
                          │
                  ┌───────▼────────┐
                  │  Docker Network│
                  └────────────────┘
```

---

## 📊 性能考量

### 瓶颈分析

| 组件 | 性能瓶颈 | 优化策略 |
|------|---------|---------|
| **LLM 调用** | 网络延迟、API 限流 | 异步并发、降级到规则 AI、缓存结果 |
| **事件数据库** | 数据量大 | 分页查询、定期清理、索引优化 |
| **WebSocket 推送** | 数据量大 | 增量更新、限制推送频率 |
| **PixiJS 渲染** | 角色数量多 | 视口裁剪、精灵池、降低更新频率 |

### 扩展性

**当前限制**:
- NPC 数量 < 100（LLM 调用并发限制）
- 事件总数 < 100,000（SQLite 性能）

**扩展方案**:
- 使用 Redis 缓存 LLM 结果
- 使用 PostgreSQL 替代 SQLite
- 分区存储（按年份分表）
- 前端虚拟滚动

---

## 🔮 未来扩展方向

### 短期 (1-3 个月)
- [ ] 完善测试覆盖率
- [ ] 添加更多动作类型（阵法、夺舍、重生）
- [ ] 优化 LLM 提示词
- [ ] 支持自定义 Mod

### 中期 (3-6 个月)
- [ ] 多人在线模式
- [ ] 历史视频化（生成动画）
- [ ] 移动端适配

### 长期 (6-12 个月)
- [ ] MCP Agent 化（修士自主调用工具）
- [ ] 3D 渲染（Three.js）
- [ ] 分布式部署（支持更多 NPC）

---

## 📚 延伸阅读

- [数据流文档](DATA_FLOW.md)
- [API 文档](API.md)
- [模块依赖图](MODULE_MAP.md)
- [架构决策记录](adr/)
- [常见开发任务](COMMON_TASKS.md)

---

**维护指南**:
- 当添加新功能时，更新本文档对应章节
- 当架构发生重大变更时，创建 ADR 记录
- 每个版本发布前，审查文档准确性

