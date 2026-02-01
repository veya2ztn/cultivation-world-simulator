# 修仙世界模拟器 - API 文档

## 📋 文档信息
- **版本**: v1.0
- **最后更新**: 2026-02-01
- **服务器地址**: `http://localhost:8002`
- **协议**: HTTP/HTTPS + WebSocket

---

## 📑 目录
- [概述](#概述)
- [认证](#认证)
- [通用响应格式](#通用响应格式)
- [错误码](#错误码)
- [REST API](#rest-api)
  - [游戏控制 API](#游戏控制-api)
  - [数据查询 API](#数据查询-api)
  - [角色管理 API](#角色管理-api)
  - [存档系统 API](#存档系统-api)
  - [配置管理 API](#配置管理-api)
  - [元数据 API](#元数据-api)
- [WebSocket 协议](#websocket-协议)
- [数据模型](#数据模型)

---

## 概述

修仙世界模拟器提供基于 FastAPI 的 RESTful API 和 WebSocket 实时通信接口。

### 基础信息

| 项目 | 值 |
|-----|-----|
| 基础 URL | `http://localhost:8002` |
| WebSocket URL | `ws://localhost:8002/ws` |
| API 前缀 | `/api` |
| 内容类型 | `application/json` |
| 字符编码 | UTF-8 |

### 技术栈
- **框架**: FastAPI 0.100+
- **WebSocket**: 原生 FastAPI WebSocket
- **数据存储**: SQLite (事件) + JSON (存档)

---

## 认证

当前版本为单机游戏，**无需认证**。所有 API 端点均可直接访问。

---

## 通用响应格式

### 成功响应

```json
{
  "status": "ok",
  "message": "操作成功",
  "data": { ... }  // 可选
}
```

### 错误响应

```json
{
  "detail": "错误信息描述"
}
```

---

## 错误码

| HTTP 状态码 | 含义 | 常见原因 |
|-----------|------|---------|
| **200** | 成功 | 请求正常处理 |
| **400** | 请求错误 | 参数格式错误、无效的文件名等 |
| **404** | 资源不存在 | 角色/区域/存档未找到 |
| **500** | 服务器错误 | 内部错误、数据库错误 |
| **503** | 服务不可用 | 游戏未初始化 |

---

## REST API

### 游戏控制 API

#### 1. 获取游戏状态

获取当前游戏世界的快照（包含时间、角色、事件）。

**端点**: `GET /api/state`

**请求参数**: 无

**响应示例**:
```json
{
  "status": "ok",
  "year": 150,
  "month": 3,
  "avatar_count": 12,
  "is_paused": false,
  "avatars": [
    {
      "id": "uuid-xxx",
      "name": "张三",
      "x": 50,
      "y": 30,
      "action": "修炼",
      "action_emoji": "🧘",
      "gender": "male",
      "pic_id": 1
    }
  ],
  "events": [
    {
      "id": "evt-xxx",
      "content": "张三突破到金丹期",
      "year": 150,
      "month": 3,
      "is_major": true,
      "related_avatar_ids": ["uuid-xxx"]
    }
  ],
  "phenomenon": {
    "id": 1,
    "name": "灵气复苏",
    "rarity": "SR",
    "duration_years": 10,
    "effect_desc": "修炼速度 +50%"
  }
}
```

---

#### 2. 暂停游戏

暂停游戏循环，世界时间停止流逝。

**端点**: `POST /api/control/pause`

**请求体**: 无

**响应示例**:
```json
{
  "status": "ok",
  "message": "Game paused"
}
```

---

#### 3. 恢复游戏

恢复游戏循环，世界时间继续流逝。

**端点**: `POST /api/control/resume`

**请求体**: 无

**响应示例**:
```json
{
  "status": "ok",
  "message": "Game resumed"
}
```

---

#### 4. 重置游戏

重置游戏到初始状态（返回主菜单）。

**端点**: `POST /api/control/reset`

**请求体**: 无

**响应示例**:
```json
{
  "status": "ok",
  "message": "Game reset to idle"
}
```

---

#### 5. 关闭服务器

关闭服务器进程（用于退出应用）。

**端点**: `POST /api/control/shutdown`

**请求体**: 无

**响应示例**:
```json
{
  "status": "shutting_down",
  "message": "Server is shutting down..."
}
```

**注意**: 此端点会在 1 秒后杀死服务器进程。

---

#### 6. 获取初始化状态

获取游戏初始化进度（用于加载界面）。

**端点**: `GET /api/init-status`

**请求参数**: 无

**响应示例**:
```json
{
  "status": "in_progress",
  "phase": 4,
  "phase_name": "generating_avatars",
  "progress": 55,
  "elapsed_seconds": 12.5,
  "error": null,
  "llm_check_failed": false,
  "llm_error_message": ""
}
```

**状态枚举**:
- `idle`: 未开始
- `pending`: 等待启动
- `in_progress`: 初始化中
- `ready`: 初始化完成
- `error`: 初始化失败

**阶段枚举** (phase_name):
- `scanning_assets`: 扫描资源文件
- `loading_map`: 加载地图
- `processing_history`: 应用历史背景
- `initializing_sects`: 初始化宗门
- `generating_avatars`: 生成角色
- `checking_llm`: 检测 LLM 连通性
- `generating_initial_events`: 生成初始事件

---

#### 7. 开始新游戏

使用配置启动新游戏。

**端点**: `POST /api/game/start`

**请求体**:
```json
{
  "init_npc_num": 12,
  "sect_num": 3,
  "protagonist": "random",
  "npc_awakening_rate_per_month": 0.01,
  "world_history": "这是一个灵气复苏的时代..."
}
```

**请求参数说明**:

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| init_npc_num | int | 是 | 初始 NPC 数量 (1-100) |
| sect_num | int | 是 | 宗门数量 (0-10) |
| protagonist | string | 是 | 主角模式: `none`, `random`, `all` |
| npc_awakening_rate_per_month | float | 是 | NPC 激活 LLM 概率 (0.0-1.0) |
| world_history | string | 否 | 世界背景设定 (可选) |

**响应示例**:
```json
{
  "status": "ok",
  "message": "Game initialization started"
}
```

**注意**: 此端点会保存配置到 `static/local_config.yml` 并异步启动初始化。使用 `/api/init-status` 轮询进度。

---

#### 8. 重新初始化游戏

在错误状态下重新初始化游戏。

**端点**: `POST /api/control/reinit`

**请求体**: 无

**响应示例**:
```json
{
  "status": "ok",
  "message": "Reinitialization started"
}
```

---

#### 9. 设置天地灵机

手动设置当前的天地灵机。

**端点**: `POST /api/control/set_phenomenon`

**请求体**:
```json
{
  "id": 1
}
```

**响应示例**:
```json
{
  "status": "ok",
  "message": "Phenomenon set to 灵气复苏"
}
```

---

### 数据查询 API

#### 1. 获取实体详情

获取角色、区域、宗门的详细信息。

**端点**: `GET /api/detail`

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| type | string | 是 | 实体类型: `avatar`, `region`, `sect` |
| id | string | 是 | 实体 ID |

**示例请求**:
```
GET /api/detail?type=avatar&id=uuid-xxx
```

**响应示例 (Avatar)**:
```json
{
  "basic": {
    "id": "uuid-xxx",
    "name": "张三",
    "realm": "金丹期",
    "level": 15,
    "age": 125,
    "lifespan": 500,
    "gender": "male",
    "sect_name": "青云门",
    "alignment": "正派"
  },
  "cultivation": {
    "progress": 75.5,
    "technique_name": "青云诀",
    "cultivation_speed": 1.2
  },
  "items": {
    "weapons": [
      {
        "id": 1,
        "name": "青锋剑",
        "grade": "金丹",
        "type": "剑"
      }
    ],
    "auxiliaries": [
      {
        "id": 2,
        "name": "护心镜",
        "grade": "金丹"
      }
    ],
    "elixirs": [
      {
        "id": 3,
        "name": "金丹",
        "count": 5
      }
    ]
  },
  "relationships": [
    {
      "target_id": "uuid-yyy",
      "target_name": "李四",
      "type": "好友",
      "value": 80
    }
  ],
  "memories": [
    {
      "content": "在洞府闭关十年",
      "importance": 0.8
    }
  ],
  "objectives": [
    {
      "content": "突破到元婴期",
      "type": "long_term"
    }
  ]
}
```

**响应示例 (Region)**:
```json
{
  "id": 1,
  "name": "青云峰",
  "type": "sect",
  "sect_id": 1,
  "sect_name": "青云门",
  "center_x": 50,
  "center_y": 30
}
```

**响应示例 (Sect)**:
```json
{
  "id": 1,
  "name": "青云门",
  "alignment": "正派",
  "main_technique": "青云诀",
  "member_count": 15,
  "avg_realm": "筑基期"
}
```

**错误响应**:
```json
{
  "detail": "Target not found"
}
```
状态码: `404`

---

#### 2. 分页查询事件

支持按角色、时间范围筛选事件。

**端点**: `GET /api/events`

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| avatar_id | string | 否 | 按单个角色筛选 |
| avatar_id_1 | string | 否 | Pair 查询：角色 1 |
| avatar_id_2 | string | 否 | Pair 查询：角色 2 (需同时提供 avatar_id_1) |
| cursor | string | 否 | 分页 cursor (上一页的 next_cursor) |
| limit | int | 否 | 每页数量 (默认 100, 最大 500) |

**示例请求**:
```
GET /api/events?avatar_id=uuid-xxx&limit=50
```

**响应示例**:
```json
{
  "events": [
    {
      "id": "evt-1",
      "text": "张三突破到金丹期",
      "content": "张三在洞府闭关十年，终于突破到金丹期。",
      "year": 150,
      "month": 3,
      "month_stamp": 1803,
      "related_avatar_ids": ["uuid-xxx"],
      "is_major": true,
      "is_story": false,
      "created_at": 1709280000.0
    }
  ],
  "next_cursor": "1803",
  "has_more": true
}
```

**分页逻辑**:
1. 第一次请求不传 cursor
2. 后续请求传入上一次响应的 next_cursor
3. 当 has_more 为 false 时表示无更多数据

---

#### 3. 清理历史事件

清理指定时间之前的事件（用户触发）。

**端点**: `DELETE /api/events/cleanup`

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| keep_major | bool | 否 | 是否保留大事件 (默认 true) |
| before_month_stamp | int | 否 | 删除此时间戳之前的事件 |

**示例请求**:
```
DELETE /api/events/cleanup?keep_major=true&before_month_stamp=1500
```

**响应示例**:
```json
{
  "deleted": 1234
}
```

---

#### 4. 获取地图数据

获取静态地图数据（仅需加载一次）。

**端点**: `GET /api/map`

**请求参数**: 无

**响应示例**:
```json
{
  "width": 100,
  "height": 100,
  "data": [
    ["GRASS", "GRASS", "MOUNTAIN", ...],
    ["WATER", "GRASS", "GRASS", ...],
    ...
  ],
  "regions": [
    {
      "id": 1,
      "name": "青云峰",
      "type": "sect",
      "x": 50,
      "y": 30,
      "sect_id": 1
    },
    {
      "id": 2,
      "name": "天机洞府",
      "type": "cultivation",
      "x": 70,
      "y": 40,
      "sub_type": "cave"
    }
  ],
  "config": {
    "tile_size": 32
  }
}
```

**地形类型**:
- `GRASS`: 草地
- `MOUNTAIN`: 山脉
- `WATER`: 水域
- `FOREST`: 森林
- `DESERT`: 沙漠

**区域类型**:
- `sect`: 宗门
- `city`: 城市
- `cultivation`: 修炼地点（洞府/遗迹）

---

### 角色管理 API

#### 1. 创建新角色

创建自定义角色。

**端点**: `POST /api/action/create_avatar`

**请求体**:
```json
{
  "surname": "张",
  "given_name": "三",
  "gender": "male",
  "age": 20,
  "level": 5,
  "sect_id": 1,
  "persona_ids": [1, 3],
  "pic_id": 5,
  "technique_id": 1,
  "weapon_id": 1,
  "auxiliary_id": 2,
  "alignment": "正派",
  "appearance": 8,
  "relations": [
    {
      "target_id": "uuid-yyy",
      "type": "好友",
      "value": 80
    }
  ]
}
```

**请求参数说明**:

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| surname | string | 否 | 姓 |
| given_name | string | 否 | 名 |
| gender | string | 否 | 性别: `male`, `female` (默认随机) |
| age | int | 否 | 年龄 (默认 18-30 随机) |
| level | int | 否 | 等级 1-120 (默认随机) |
| sect_id | int | 否 | 宗门 ID (默认散修) |
| persona_ids | int[] | 否 | 个性 ID 列表 (默认随机) |
| pic_id | int | 否 | 头像 ID (默认随机) |
| technique_id | int | 否 | 功法 ID (默认根据宗门) |
| weapon_id | int | 否 | 兵器 ID (默认随机) |
| auxiliary_id | int | 否 | 辅助装备 ID (默认随机) |
| alignment | string | 否 | 阵营: `正派`, `邪派`, `中立` (默认随机) |
| appearance | int | 否 | 容貌 1-10 (默认随机) |
| relations | object[] | 否 | 初始关系 (默认无) |

**响应示例**:
```json
{
  "status": "ok",
  "message": "Created avatar 张三",
  "avatar_id": "uuid-new"
}
```

**错误响应**:
```json
{
  "detail": "Invalid pic_id for selected gender"
}
```
状态码: `400`

---

#### 2. 删除角色

删除指定角色（不可恢复）。

**端点**: `POST /api/action/delete_avatar`

**请求体**:
```json
{
  "avatar_id": "uuid-xxx"
}
```

**响应示例**:
```json
{
  "status": "ok",
  "message": "Avatar deleted"
}
```

**错误响应**:
```json
{
  "detail": "Avatar not found"
}
```
状态码: `404`

---

#### 3. 设置长期目标

为角色设置长期目标（用于引导 AI 决策）。

**端点**: `POST /api/action/set_long_term_objective`

**请求体**:
```json
{
  "avatar_id": "uuid-xxx",
  "content": "加入青云门"
}
```

**响应示例**:
```json
{
  "status": "ok",
  "message": "Objective set"
}
```

---

#### 4. 清除长期目标

清除角色的用户设定目标。

**端点**: `POST /api/action/clear_long_term_objective`

**请求体**:
```json
{
  "avatar_id": "uuid-xxx"
}
```

**响应示例**:
```json
{
  "status": "ok",
  "message": "Objective cleared"
}
```

---

### 存档系统 API

#### 1. 获取存档列表

列出所有可用存档。

**端点**: `GET /api/saves`

**请求参数**: 无

**响应示例**:
```json
{
  "saves": [
    {
      "filename": "save_20260201_1430.json",
      "save_time": "2026-02-01 14:30:00",
      "game_time": "Year 150, Month 3",
      "version": "0.1.0"
    }
  ]
}
```

---

#### 2. 保存游戏

保存当前游戏状态。

**端点**: `POST /api/game/save`

**请求体**:
```json
{
  "filename": "my_save.json"
}
```

**请求参数说明**:

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| filename | string | 否 | 存档文件名 (默认自动生成时间戳) |

**响应示例**:
```json
{
  "status": "ok",
  "filename": "save_20260201_1430.json"
}
```

**错误响应**:
```json
{
  "detail": "Game not initialized"
}
```
状态码: `503`

---

#### 3. 加载游戏

加载指定存档。

**端点**: `POST /api/game/load`

**请求体**:
```json
{
  "filename": "save_20260201_1430.json"
}
```

**响应示例**:
```json
{
  "status": "ok",
  "message": "Game loaded"
}
```

**错误响应**:
```json
{
  "detail": "Invalid filename"
}
```
状态码: `400`

```json
{
  "detail": "File not found"
}
```
状态码: `404`

**注意**:
- 仅允许加载 `assets/saves/` 目录下的文件
- 文件名不能包含 `..`, `/`, `\`
- 加载过程异步进行，使用 `/api/init-status` 轮询进度

---

### 配置管理 API

#### 1. 获取当前游戏配置

**端点**: `GET /api/config/current`

**请求参数**: 无

**响应示例**:
```json
{
  "game": {
    "init_npc_num": 12,
    "sect_num": 3,
    "npc_awakening_rate_per_month": 0.01,
    "world_history": ""
  },
  "avatar": {
    "protagonist": "none"
  }
}
```

---

#### 2. 获取 LLM 配置

**端点**: `GET /api/config/llm`

**请求参数**: 无

**响应示例**:
```json
{
  "base_url": "https://api.deepseek.com",
  "api_key": "sk-xxx",
  "model_name": "deepseek-chat",
  "fast_model_name": "deepseek-chat",
  "mode": "default"
}
```

---

#### 3. 保存 LLM 配置

**端点**: `POST /api/config/llm/save`

**请求体**:
```json
{
  "base_url": "https://api.deepseek.com",
  "api_key": "sk-xxx",
  "model_name": "deepseek-chat",
  "fast_model_name": "deepseek-chat",
  "mode": "default"
}
```

**请求参数说明**:

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| base_url | string | 是 | API 基础 URL |
| api_key | string | 是 | API 密钥 |
| model_name | string | 是 | 智能模型名称 |
| fast_model_name | string | 是 | 快速模型名称 |
| mode | string | 是 | 模式: `default`, `normal`, `fast` |

**响应示例**:
```json
{
  "status": "ok",
  "message": "配置已保存"
}
```

---

#### 4. 测试 LLM 连接

**端点**: `POST /api/config/llm/test`

**请求体**:
```json
{
  "base_url": "https://api.deepseek.com",
  "api_key": "sk-xxx",
  "model_name": "deepseek-chat"
}
```

**响应示例 (成功)**:
```json
{
  "status": "ok",
  "message": "连接成功"
}
```

**响应示例 (失败)**:
```json
{
  "detail": "连接失败：API key is invalid"
}
```
状态码: `400`

---

#### 5. 获取 LLM 配置状态

**端点**: `GET /api/config/llm/status`

**请求参数**: 无

**响应示例**:
```json
{
  "configured": true
}
```

---

#### 6. 获取语言设置

**端点**: `GET /api/config/language`

**请求参数**: 无

**响应示例**:
```json
{
  "lang": "zh-CN"
}
```

---

#### 7. 设置语言

**端点**: `POST /api/config/language`

**请求体**:
```json
{
  "lang": "en-US"
}
```

**支持的语言**:
- `zh-CN`: 简体中文
- `en-US`: English

**响应示例**:
```json
{
  "status": "ok"
}
```

**注意**: 语言切换会重新加载所有游戏数据，建议在游戏开始前设置。

---

### 元数据 API

#### 1. 获取头像资源元数据

**端点**: `GET /api/meta/avatars`

**请求参数**: 无

**响应示例**:
```json
{
  "males": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  "females": [1, 2, 3, 4, 5, 6, 7, 8]
}
```

**说明**: 返回可用的男性和女性头像 ID 列表。

---

#### 2. 获取游戏数据元信息

获取所有宗门、个性、境界、功法、兵器、辅助装备等元数据。

**端点**: `GET /api/meta/game_data`

**请求参数**: 无

**响应示例**:
```json
{
  "sects": [
    {
      "id": 1,
      "name": "青云门",
      "alignment": "正派"
    }
  ],
  "personas": [
    {
      "id": 1,
      "name": "冷静",
      "desc": "遇事不慌",
      "rarity": "N"
    }
  ],
  "realms": [
    "炼气期",
    "筑基期",
    "金丹期",
    "元婴期"
  ],
  "techniques": [
    {
      "id": 1,
      "name": "青云诀",
      "grade": "玄级",
      "attribute": "木",
      "sect_id": 1
    }
  ],
  "weapons": [
    {
      "id": 1,
      "name": "青锋剑",
      "type": "剑",
      "grade": "金丹期"
    }
  ],
  "auxiliaries": [
    {
      "id": 1,
      "name": "护心镜",
      "grade": "金丹期"
    }
  ],
  "alignments": [
    {
      "value": "正派",
      "label": "正派"
    },
    {
      "value": "邪派",
      "label": "邪派"
    },
    {
      "value": "中立",
      "label": "中立"
    }
  ]
}
```

---

#### 3. 获取角色列表（简略）

用于角色管理界面。

**端点**: `GET /api/meta/avatar_list`

**请求参数**: 无

**响应示例**:
```json
{
  "avatars": [
    {
      "id": "uuid-xxx",
      "name": "张三",
      "sect_name": "青云门",
      "realm": "金丹期",
      "gender": "male",
      "age": 125
    }
  ]
}
```

---

#### 4. 获取天地灵机列表

**端点**: `GET /api/meta/phenomena`

**请求参数**: 无

**响应示例**:
```json
{
  "phenomena": [
    {
      "id": 1,
      "name": "灵气复苏",
      "desc": "天地灵气浓度大幅提升",
      "rarity": "SR",
      "duration_years": 10,
      "effect_desc": "修炼速度 +50%"
    }
  ]
}
```

---

## WebSocket 协议

### 连接

**URL**: `ws://localhost:8002/ws`

**握手**: 标准 WebSocket 握手

**示例 (JavaScript)**:
```javascript
const ws = new WebSocket('ws://localhost:8002/ws');

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleMessage(data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```

---

### 服务端推送消息类型

#### 1. tick 消息（游戏循环）

每秒推送一次游戏状态更新（如果游戏未暂停）。

**消息格式**:
```json
{
  "type": "tick",
  "year": 150,
  "month": 3,
  "events": [
    {
      "id": "evt-xxx",
      "text": "张三突破到金丹期",
      "content": "张三在洞府闭关十年，终于突破到金丹期。",
      "year": 150,
      "month": 3,
      "month_stamp": 1803,
      "related_avatar_ids": ["uuid-xxx"],
      "is_major": true,
      "is_story": false,
      "created_at": 1709280000.0
    }
  ],
  "avatars": [
    {
      "id": "uuid-xxx",
      "name": "张三",
      "x": 50,
      "y": 30,
      "gender": "male",
      "pic_id": 1,
      "action": "修炼",
      "action_emoji": "🧘",
      "is_dead": false
    },
    {
      "id": "uuid-yyy",
      "name": "李四",
      "is_dead": true,
      "action": "已故"
    }
  ],
  "phenomenon": {
    "id": 1,
    "name": "灵气复苏",
    "desc": "天地灵气浓度大幅提升",
    "rarity": "SR",
    "duration_years": 10,
    "effect_desc": "修炼速度 +50%"
  },
  "active_domains": [
    {
      "id": 1,
      "name": "天机秘境",
      "desc": "上古遗迹",
      "max_realm": "元婴期",
      "danger_prob": 0.3,
      "drop_prob": 0.5,
      "is_open": true,
      "cd_years": 50,
      "open_prob": 0.1
    }
  ]
}
```

**字段说明**:
- `events`: 本回合新发生的事件
- `avatars`: 角色状态更新（新生、死亡、位置变化）
- `phenomenon`: 当前天地灵机（可为 null）
- `active_domains`: 秘境状态列表

---

#### 2. llm_config_required 消息

在 LLM 连通性检测失败时推送。

**消息格式**:
```json
{
  "type": "llm_config_required",
  "error": "LLM 连接失败：API key is invalid"
}
```

**处理建议**: 前端应显示配置界面引导用户设置 LLM。

---

#### 3. toast 消息

系统消息通知。

**消息格式**:
```json
{
  "type": "toast",
  "level": "info",
  "message": "存档已保存",
  "language": "zh-CN"
}
```

**级别枚举**:
- `info`: 一般信息
- `success`: 成功提示
- `warning`: 警告
- `error`: 错误

**可选字段**:
- `language`: 当前语言设置（用于语言切换通知）

---

#### 4. game_reinitialized 消息

游戏重新初始化完成通知。

**消息格式**:
```json
{
  "type": "game_reinitialized",
  "message": "LLM 配置成功，游戏已恢复运行"
}
```

---

### 客户端发送消息

#### Ping-Pong 心跳

**发送**:
```json
"ping"
```

**响应**:
```json
{
  "type": "pong"
}
```

**注意**: 当前版本 WebSocket 主要用于服务端推送，客户端发送功能有限。

---

## 数据模型

### Avatar (角色)

```typescript
interface Avatar {
  id: string;
  name: string;
  realm: string;           // 境界
  level: number;           // 等级 1-120
  age: number;             // 年龄
  lifespan: number;        // 寿元
  gender: "male" | "female";
  sect_name: string;       // 宗门名称
  alignment: string;       // 阵营
  pos_x: number;           // X 坐标
  pos_y: number;           // Y 坐标
  action: string;          // 当前动作
  action_emoji: string;    // 动作表情
  pic_id: number;          // 头像 ID
  is_dead: boolean;        // 是否死亡
}
```

---

### Event (事件)

```typescript
interface Event {
  id: string;
  text: string;            // 简短描述
  content: string;         // 详细内容
  year: number;
  month: number;
  month_stamp: number;     // 时间戳 (year*12 + month)
  related_avatar_ids: string[];
  is_major: boolean;       // 是否大事件
  is_story: boolean;       // 是否剧情事件
  created_at: number;      // Unix 时间戳
}
```

---

### Region (区域)

```typescript
interface Region {
  id: number;
  name: string;
  type: "sect" | "city" | "cultivation";
  x: number;               // 中心 X 坐标
  y: number;               // 中心 Y 坐标
  sect_id?: number;        // 宗门 ID (仅 type=sect)
  sub_type?: string;       // 子类型 (仅 type=cultivation)
}
```

---

### Phenomenon (天地灵机)

```typescript
interface Phenomenon {
  id: number;
  name: string;
  desc: string;
  rarity: "N" | "R" | "SR" | "SSR";
  duration_years: number;
  effect_desc: string;
}
```

---

### Relationship (关系)

```typescript
interface Relationship {
  target_id: string;
  target_name: string;
  type: string;            // 好友、仇敌、师徒等
  value: number;           // 关系值 -100 ~ 100
}
```

---

### Sect (宗门)

```typescript
interface Sect {
  id: number;
  name: string;
  alignment: "正派" | "邪派" | "中立";
  main_technique: string;
  member_count: number;
  avg_realm: string;
}
```

---

### Technique (功法)

```typescript
interface Technique {
  id: number;
  name: string;
  grade: string;           // 黄级、玄级、地级、天级
  attribute: string;       // 金木水火土
  sect_id: number;
}
```

---

### Weapon (兵器)

```typescript
interface Weapon {
  id: number;
  name: string;
  type: string;            // 剑、刀、枪等
  grade: string;           // 境界等级
}
```

---

### Auxiliary (辅助装备)

```typescript
interface Auxiliary {
  id: number;
  name: string;
  grade: string;           // 境界等级
}
```

---

## 附录

### A. 时间戳转换

游戏使用 `month_stamp` 作为内部时间戳：

```
month_stamp = year * 12 + month
```

**示例**:
- Year 150, Month 3 → `150 * 12 + 3 = 1803`

**反向转换**:
```python
year = month_stamp // 12
month = month_stamp % 12
if month == 0:
    month = 12
    year -= 1
```

---

### B. 境界对应等级

| 境界 | 等级范围 |
|-----|---------|
| 炼气期 | 1-30 |
| 筑基期 | 31-60 |
| 金丹期 | 61-90 |
| 元婴期 | 91-120 |

---

### C. 阵营枚举

- `正派`: 正义、光明
- `邪派`: 邪恶、黑暗
- `中立`: 中立、混沌

---

### D. 稀有度枚举

- `N`: Normal (普通)
- `R`: Rare (稀有)
- `SR`: Super Rare (超稀有)
- `SSR`: Super Super Rare (超超稀有)

---

### E. 错误处理最佳实践

#### 1. 检查游戏状态
在调用游戏相关 API 前，先检查 `/api/init-status`:

```javascript
const status = await fetch('/api/init-status').then(r => r.json());
if (status.status !== 'ready') {
  // 处理未就绪状态
}
```

#### 2. 处理 WebSocket 断线
实现自动重连机制：

```javascript
function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:8002/ws');

  ws.onclose = () => {
    setTimeout(() => connectWebSocket(), 3000); // 3秒后重连
  };

  return ws;
}
```

#### 3. 处理 API 错误
统一错误处理：

```javascript
async function apiCall(url, options) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '请求失败');
    }
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    // 显示用户友好的错误提示
    throw error;
  }
}
```

---

### F. 性能优化建议

#### 1. 事件分页
使用分页避免一次加载过多事件：

```javascript
let cursor = null;
const events = [];

while (true) {
  const response = await fetch(`/api/events?cursor=${cursor}&limit=100`);
  const data = await response.json();

  events.push(...data.events);

  if (!data.has_more) break;
  cursor = data.next_cursor;
}
```

#### 2. WebSocket 消息节流
避免频繁更新 UI：

```javascript
let updatePending = false;

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (!updatePending) {
    updatePending = true;
    requestAnimationFrame(() => {
      updateUI(data);
      updatePending = false;
    });
  }
};
```

---

## 更新日志

### v1.0 (2026-02-01)
- 初始版本
- 包含所有核心 API 端点
- WebSocket 实时通信协议
- 完整数据模型定义

---

## 反馈与支持

- **GitHub**: https://github.com/AI-Cultivation/cultivation-world-simulator
- **Issues**: https://github.com/AI-Cultivation/cultivation-world-simulator/issues

---

**维护者**: AI 开发团队
**最后更新**: 2026-02-01
