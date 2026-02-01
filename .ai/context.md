# 修仙世界模拟器 - AI 开发者快速上下文

## 🎯 项目本质（一句话）
一个 AI 驱动的修仙世界模拟器，每个 NPC 都由 LLM 赋予智能，世界按规则运行，剧情自然涌现。

## 🏗️ 核心架构（5 秒理解）

```
┌─────────────────────────────────────────────────────────┐
│                    用户浏览器                              │
│  Vue 3 + PixiJS (地图渲染) + WebSocket (实时推送)          │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/WS
┌────────────────┴────────────────────────────────────────┐
│              FastAPI 后端 (Python 3.10+)                 │
│  ┌──────────────────────────────────────────────┐       │
│  │  Game Loop (异步)                             │       │
│  │  ↓                                            │       │
│  │  Simulator.step() → 每月推进                   │       │
│  │  ↓                                            │       │
│  │  所有 NPC 的 AI 决策 (规则AI + LLM AI)          │       │
│  │  ↓                                            │       │
│  │  事件生成 → WebSocket 推送到前端                │       │
│  └──────────────────────────────────────────────┘       │
│                                                          │
│  数据存储: SQLite (事件) + JSON (存档)                     │
└──────────────────────────────────────────────────────────┘
                 │ API Call
┌────────────────┴────────────────────────────────────────┐
│           LLM Provider (OpenAI/DeepSeek/Ollama)         │
│           用于 NPC 智能决策、对话、剧情生成                  │
└──────────────────────────────────────────────────────────┘
```

## 📁 核心目录职责

| 目录 | 职责 | 关键文件 |
|------|------|---------|
| `src/server/` | FastAPI 服务器、WebSocket、API 路由 | `main.py` (1870行，包含所有API) |
| `src/sim/` | 游戏模拟器核心、存档系统 | `simulator.py` |
| `src/classes/` | 游戏实体类（角色、宗门、动作等） | `avatar/`, `action/`, `sect.py` |
| `src/utils/llm/` | LLM 客户端封装 | `client.py` |
| `web/src/components/` | Vue 组件 | `game/`, `panels/` |
| `web/src/stores/` | Pinia 状态管理 | |
| `static/` | 配置文件 | `local_config.yml` (用户配置) |
| `assets/` | 游戏资源 | `saves/`, `males/`, `females/` |

## 🔑 关键概念映射（修仙术语 → 代码）

| 修仙概念 | 代码实体 | 位置 |
|---------|---------|------|
| 修士/角色 | `Avatar` | `src/classes/avatar/avatar.py` |
| 境界（炼气、筑基...） | `CultivationRealm` Enum | `src/classes/cultivation.py` |
| 宗门 | `Sect` | `src/classes/sect.py` |
| 功法 | `Technique` | `src/classes/technique.py` |
| 动作（修炼、战斗...） | `Action` 子类 | `src/classes/action/` |
| 天地灵机 | `CelestialPhenomenon` | `src/classes/celestial_phenomenon.py` |
| 事件 | `Event` | `src/classes/event.py` |
| 世界 | `World` | `src/classes/world.py` |
| 模拟器 | `Simulator` | `src/sim/simulator.py` |

## 🔄 数据流（关键路径）

### 1. 游戏循环 (每秒 1 次)
```python
# src/server/main.py:498
async def game_loop():
    while True:
        await asyncio.sleep(1.0)
        if not paused:
            events = await sim.step()  # 推进一个月
            # 广播状态更新到所有客户端
            await manager.broadcast({
                "type": "tick",
                "year": world.year,
                "month": world.month,
                "events": events,
                "avatars": avatar_updates
            })
```

### 2. Simulator.step() 流程
```
1. 月份+1
2. 遍历所有活人 NPC
3. 每个 NPC 决策下一步动作
   ├─ 规则 AI：检查是否需要突破、疗伤等
   └─ LLM AI：调用 LLM 做复杂决策
4. 执行所有动作
5. 结算长期动作
6. 生成事件
7. 返回事件列表
```

### 3. LLM 调用流程
```
NPC 需要决策 → 构造提示词（包含角色状态、记忆、周围环境）
→ 调用 LLM API (src/utils/llm/client.py)
→ 解析返回的 JSON
→ 执行对应动作
→ 生成事件记录
```

## 🎮 核心系统

### 1. 动作系统 (Action System)
- **位置**: `src/classes/action/`
- **机制**:
  - 短动作：立即执行（如移动）
  - 长动作：持续多个月（如修炼、闭关）
  - 多人动作：需要响应（如战斗、对话）
- **注册**: `src/classes/actions.py` 中注册所有动作

### 2. 事件系统 (Event System)
- **存储**: SQLite 数据库 (可分页查询)
- **类型**:
  - 普通事件：日常修炼、移动
  - 大事件：突破、战斗、死亡
  - 剧情事件：LLM 生成的小剧场
- **管理**: `src/classes/event_manager.py`

### 3. AI 系统 (双层 AI)
- **规则 AI**: 基于条件的决策（如生命值低 → 疗伤）
- **LLM AI**: 复杂决策（如是否加入宗门、与人交往）
- **切换**: 根据 `npc_awakening_rate` 概率激活 LLM AI

### 4. 存档系统
- **格式**: JSON (世界状态) + SQLite (事件数据库)
- **位置**: `assets/saves/`
- **保存**: `src/sim/save/save_game.py`
- **加载**: `src/sim/load/load_game.py`

## 🔌 API 端点（关键）

| 端点 | 方法 | 用途 |
|-----|------|-----|
| `/ws` | WebSocket | 实时游戏状态推送 |
| `/api/state` | GET | 获取当前游戏快照 |
| `/api/map` | GET | 获取地图数据（首次加载） |
| `/api/events` | GET | 分页查询事件 |
| `/api/detail?type=avatar&id=xxx` | GET | 获取角色/区域详情 |
| `/api/control/pause` | POST | 暂停游戏 |
| `/api/control/resume` | POST | 恢复游戏 |
| `/api/game/save` | POST | 保存游戏 |
| `/api/game/load` | POST | 加载存档 |
| `/api/config/llm` | GET/POST | LLM 配置 |
| `/api/action/create_avatar` | POST | 创建新角色 |

## ⚙️ 配置系统

### 配置加载顺序
```
1. static/default_config.yml (默认配置)
2. static/game_config.yml (游戏规则)
3. static/local_config.yml (用户配置，覆盖前两者)
```

### 关键配置项
```yaml
llm:
  base_url: "https://api.deepseek.com"
  key: "sk-xxx"
  model_name: "deepseek-chat"
  fast_model_name: "deepseek-chat"
  mode: "default"  # default/normal/fast

game:
  init_npc_num: 12           # 初始 NPC 数量
  sect_num: 3                # 宗门数量
  start_year: 100            # 起始年份
  npc_awakening_rate_per_month: 0.01  # NPC 激活 LLM 概率
  world_history: "..."       # 世界背景设定

system:
  language: "zh-CN"          # 语言设置 (zh-CN/en-US)
```

## 🧪 测试

- **后端**: pytest (`pytest` 或 `pytest --cov=src`)
- **前端**: Vitest (`cd web && npm run test`)
- **测试位置**: `tests/` (后端), `web/src/__tests__/` (前端)

## 🚀 启动方式

### 开发模式（推荐）
```bash
python src/server/main.py --dev
# 自动启动前端 (localhost:5173) 和后端 (localhost:8002)
```

### Docker 部署
```bash
docker-compose up -d --build
# 前端: localhost:8123, 后端: localhost:8002
```

## ⚠️ 常见陷阱

1. **修改 CSV 数据后需重启**: `static/` 下的 CSV 文件在启动时加载
2. **LLM 调用失败会回退到规则 AI**: 不会中断游戏
3. **WebSocket 断开后游戏自动暂停**: 节省资源
4. **修改存档格式需要迁移脚本**: 否则旧存档无法加载
5. **前端开发时使用代理**: Vite 代理 `/api` 到后端 8002 端口

## 📊 性能特征

- **NPC 数量**: 推荐 < 100（LLM 调用并发限制）
- **事件数据库**: 定期清理，保留大事件
- **WebSocket 推送**: 增量更新，只发送变化的角色
- **前端渲染**: PixiJS 硬件加速，支持大地图

## 🔮 扩展点

1. **添加新动作**: 继承 `Action` 基类，在 `actions.py` 注册
2. **添加新事件类型**: 修改 `Event` 类，更新数据库 schema
3. **添加新 NPC 决策逻辑**: 修改 `src/classes/ai.py`
4. **添加新 API**: 在 `src/server/main.py` 添加路由
5. **添加新 UI 面板**: 在 `web/src/components/panels/` 创建组件

## 📚 深入阅读

- 完整架构: `docs/ARCHITECTURE.md`
- API 文档: `docs/API.md`
- 数据流: `docs/DATA_FLOW.md`
- 常见任务: `docs/COMMON_TASKS.md`
- 架构决策: `docs/adr/`

## 🆘 遇到问题？

1. **查看日志**: 控制台输出 + `logs/` 目录
2. **检查 LLM 配置**: `/api/config/llm/status`
3. **测试连通性**: `/api/config/llm/test`
4. **查看游戏状态**: `/api/state`
5. **GitHub Issues**: https://github.com/AI-Cultivation/cultivation-world-simulator/issues

---

**最后更新**: 2026-02-01
**维护者**: AI 开发团队
**版本**: v0.1.0
