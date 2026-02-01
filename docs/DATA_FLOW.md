# 数据流文档 (Data Flow)

本文档详细描述修仙世界模拟器中的数据流向和状态管理。

---

## 📊 总览图

```
┌──────────┐
│  用户     │
└────┬─────┘
     │ 点击/输入
     ▼
┌──────────────────────────────────────┐
│         Vue 前端应用                  │
│  ┌────────────────────────────────┐  │
│  │  User Event (点击角色/按钮)     │  │
│  └────────┬───────────────────────┘  │
│           ▼                           │
│  ┌────────────────────────────────┐  │
│  │  Component (处理事件)           │  │
│  └────────┬───────────────────────┘  │
│           ▼                           │
│  ┌────────────────────────────────┐  │
│  │  Pinia Store (更新状态)         │  │
│  └────────┬───────────────────────┘  │
│           ▼                           │
│  ┌────────────────────────────────┐  │
│  │  API Client (发起请求)          │  │
│  └────────┬───────────────────────┘  │
└───────────┼───────────────────────────┘
            │ HTTP/WebSocket
            ▼
┌──────────────────────────────────────┐
│        FastAPI 后端                   │
│  ┌────────────────────────────────┐  │
│  │  API Route (处理请求)           │  │
│  └────────┬───────────────────────┘  │
│           ▼                           │
│  ┌────────────────────────────────┐  │
│  │  Simulator (游戏逻辑)           │  │
│  └────────┬───────────────────────┘  │
│           ▼                           │
│  ┌────────────────────────────────┐  │
│  │  World/Avatar (更新状态)        │  │
│  └────────┬───────────────────────┘  │
│           ▼                           │
│  ┌────────────────────────────────┐  │
│  │  EventManager (生成事件)        │  │
│  └────────┬───────────────────────┘  │
│           ▼                           │
│  ┌────────────────────────────────┐  │
│  │  Response (返回数据)            │  │
│  └────────┬───────────────────────┘  │
└───────────┼───────────────────────────┘
            │
            ▼
     ┌────────────┐
     │  SQLite    │ (事件持久化)
     └────────────┘
```

---

## 🔄 核心数据流

### 1. 游戏初始化流程

```
[前端] 用户访问页面
  ↓
[前端] 建立 WebSocket 连接
  ↓
[前端] GET /api/init-status
  ↓
[后端] 返回 { status: "idle" }
  ↓
[前端] 显示"开始游戏"菜单
  ↓
[前端] 用户配置参数 (NPC数量、宗门数量等)
  ↓
[前端] POST /api/game/start
  {
    init_npc_num: 12,
    sect_num: 3,
    protagonist: "none",
    world_history: "..."
  }
  ↓
[后端] 保存配置到 local_config.yml
  ↓
[后端] 启动异步初始化任务 init_game_async()
  ↓
  ┌──────────────────────────────────────┐
  │  初始化流程（6个阶段）                 │
  ├──────────────────────────────────────┤
  │ 阶段 0: 扫描资源文件                  │
  │   scan_avatar_assets()                │
  │   → AVATAR_ASSETS = {males: [...], females: [...]}
  ├──────────────────────────────────────┤
  │ 阶段 1: 加载地图                      │
  │   load_cultivation_world_map()        │
  │   → game_map = Map(width=100, height=100)
  ├──────────────────────────────────────┤
  │ 阶段 2: 处理世界历史                  │
  │   如果有 world_history:               │
  │     HistoryManager.apply_history()    │
  │     → 调用 LLM 生成初始状态          │
  ├──────────────────────────────────────┤
  │ 阶段 3: 初始化宗门                    │
  │   从 sects_by_id 随机选择 N 个       │
  │   → existed_sects = [Sect1, Sect2, ...]
  ├──────────────────────────────────────┤
  │ 阶段 4: 生成角色                      │
  │   如果 protagonist != "none":         │
  │     spawn_protagonists()              │
  │   make_random_avatars()               │
  │   → final_avatars = {id: Avatar, ...} │
  ├──────────────────────────────────────┤
  │ 阶段 5: 检测 LLM 连通性               │
  │   test_connectivity()                 │
  │   如果失败: 标记 llm_check_failed     │
  ├──────────────────────────────────────┤
  │ 阶段 6: 生成初始事件                  │
  │   sim.step() (第一次)                 │
  │   → 生成角色诞生事件                  │
  └──────────────────────────────────────┘
  ↓
[后端] game_instance["init_status"] = "ready"
  ↓
[前端] 轮询 /api/init-status，检测到 ready
  ↓
[前端] GET /api/map
  ↓
[后端] 返回地图数据
  {
    width: 100,
    height: 100,
    data: [[tile_type, ...], ...],
    regions: [{id, name, type, x, y}, ...]
  }
  ↓
[前端] 渲染地图
  ↓
[前端] GET /api/state
  ↓
[后端] 返回当前游戏状态
  {
    year: 100,
    month: 1,
    avatars: [{id, name, x, y, ...}, ...],
    events: [...]
  }
  ↓
[前端] 渲染角色精灵
  ↓
[前端] 用户点击"开始"
  ↓
[前端] POST /api/control/resume
  ↓
[后端] game_instance["is_paused"] = False
  ↓
[后端] game_loop 开始运行
```

---

### 2. 游戏循环数据流（关键路径）

这是游戏的心跳，每秒执行一次：

```
┌─────────────────────────────────────────────────────────────┐
│  game_loop() - 每秒执行一次                                   │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
检查 is_paused
  ├─ True → continue (跳过本次循环)
  └─ False → 继续
  │
  ▼
await sim.step()
  │
  ┌─────────────────────────────────────────────────────────┐
  │  Simulator.step() 内部详细流程                           │
  └─────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│ 1. 时间推进                                                   │
│    world.month_stamp += 1                                    │
│    例如: 1200 (Year 100, Month 1) → 1201 (Year 100, Month 2) │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. 角色状态更新 (遍历所有活人)                                │
│    for avatar in world.avatar_manager.get_living_avatars():  │
│      ┌────────────────────────────────────────────────┐      │
│      │ 2.1 年龄增长                                    │      │
│      │     avatar.age += 1/12                          │      │
│      └────────────────────────────────────────────────┘      │
│      ┌────────────────────────────────────────────────┐      │
│      │ 2.2 寿元检查                                    │      │
│      │     if avatar.age > max_lifespan:               │      │
│      │       avatar.die(reason=DeathReason.OLD_AGE)    │      │
│      │       world.event_manager.add_event(...)        │      │
│      │       continue                                  │      │
│      └────────────────────────────────────────────────┘      │
│      ┌────────────────────────────────────────────────┐      │
│      │ 2.3 长期动作进度更新                            │      │
│      │     if avatar.current_action:                   │      │
│      │       avatar.current_action.progress += 1       │      │
│      │       if avatar.current_action.is_completed():  │      │
│      │         settled_actions.append(action)          │      │
│      └────────────────────────────────────────────────┘      │
│      ┌────────────────────────────────────────────────┐      │
│      │ 2.4 AI 决策新动作                               │      │
│      │     if avatar.current_action is None:           │      │
│      │       next_action = await avatar.decide()       │      │
│      │         ↓                                       │      │
│      │         判断是否使用 LLM AI                      │      │
│      │         ├─ 是 → call_llm_api() [异步]          │      │
│      │         └─ 否 → rule_based_decide()            │      │
│      │       avatar.start_action(next_action)          │      │
│      └────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. 结算完成的长期动作                                         │
│    for action in settled_actions:                            │
│      result = action.settle()                                │
│      if result.success:                                      │
│        apply_effects(avatar, result.effects)                 │
│        generate_event(action, result)                        │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. 处理多人动作响应                                           │
│    for mutual_action in pending_mutual_actions:              │
│      if mutual_action.has_response():                        │
│        execute_mutual_action(mutual_action)                  │
│        generate_event(...)                                   │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. 处理世界级事件                                             │
│    ┌──────────────────────────────────────────┐             │
│    │ 5.1 天地灵机变化                          │             │
│    │     if random() < phenomenon_change_rate: │             │
│    │       new_phenomenon = roll_phenomenon()  │             │
│    │       world.set_phenomenon(new_phenomenon)│             │
│    │       generate_event(...)                 │             │
│    └──────────────────────────────────────────┘             │
│    ┌──────────────────────────────────────────┐             │
│    │ 5.2 秘境开启                              │             │
│    │     for domain in hidden_domains:         │             │
│    │       if domain.should_open():            │             │
│    │         domain.open()                     │             │
│    │         generate_event(...)               │             │
│    └──────────────────────────────────────────┘             │
│    ┌──────────────────────────────────────────┐             │
│    │ 5.3 大型活动 (拍卖会、比武大会等)         │             │
│    │     if should_trigger_auction():          │             │
│    │       start_auction()                     │             │
│    └──────────────────────────────────────────┘             │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. 返回事件列表                                               │
│    return all_generated_events                               │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
返回到 game_loop
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│ 收集状态变更                                                  │
│   newly_born_ids = world.avatar_manager.pop_newly_born()     │
│   newly_dead_ids = world.avatar_manager.pop_newly_dead()     │
│   avatar_updates = []                                        │
│   ┌──────────────────────────────────────────────┐           │
│   │ 对于新生角色: 发送完整信息                    │           │
│   │   {id, name, x, y, gender, pic_id, action}   │           │
│   └──────────────────────────────────────────────┘           │
│   ┌──────────────────────────────────────────────┐           │
│   │ 对于死亡角色: 发送死亡标记                    │           │
│   │   {id, name, is_dead: true}                  │           │
│   └──────────────────────────────────────────────┘           │
│   ┌──────────────────────────────────────────────┐           │
│   │ 对于其他角色: 只发送位置更新 (限制前50个)      │           │
│   │   {id, x, y, action_emoji}                   │           │
│   └──────────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────┐
│ 构造广播消息                                                  │
│   message = {                                                │
│     type: "tick",                                            │
│     year: world.year,                                        │
│     month: world.month,                                      │
│     events: serialize_events(events),                        │
│     avatars: avatar_updates,                                 │
│     phenomenon: serialize_phenomenon(world.phenomenon),      │
│     active_domains: serialize_domains(world.domains)         │
│   }                                                          │
└──────────────────────────────────────────────────────────────┘
  │
  ▼
await manager.broadcast(message)
  │
  ┌────────────────────────────────────────┐
  │ 通过 WebSocket 发送给所有连接的客户端  │
  └────────────────────────────────────────┘
  │
  ▼
[前端] 接收 WebSocket 消息
  │
  ▼
[前端] 更新 Pinia Store
  │
  ┌────────────────────────────────────────┐
  │ gameStore.year = message.year          │
  │ gameStore.month = message.month        │
  │ eventStore.addEvents(message.events)   │
  │ avatarStore.updateAvatars(message.avatars) │
  └────────────────────────────────────────┘
  │
  ▼
[前端] Vue 响应式更新 UI
  │
  ┌────────────────────────────────────────┐
  │ 更新时间显示                            │
  │ 更新角色位置（PixiJS 精灵移动）          │
  │ 添加新事件到事件面板                    │
  │ 显示天地灵机图标                        │
  └────────────────────────────────────────┘
  │
  ▼
循环结束，等待下一秒
```

---

### 3. LLM AI 决策数据流

当 NPC 需要做决策时，如果使用 LLM AI：

```
avatar.decide()
  │
  ▼
检查是否需要使用 LLM
  ├─ 规则 AI 优先处理紧急情况
  │   if avatar.hp < 20%:
  │     return RestAction()  # 疗伤优先
  │   if avatar.can_breakthrough():
  │     return BreakthroughAction()  # 突破优先
  │
  └─ 检查 LLM 激活条件
      if random() < npc_awakening_rate:
        使用 LLM AI
      else:
        使用规则 AI
  │
  ▼ (使用 LLM AI)
┌────────────────────────────────────────────────────────┐
│ 构造提示词                                              │
│   prompt = f"""                                        │
│   你是修仙世界中的角色:{avatar.name}                    │
│                                                        │
│   # 基本信息                                           │
│   - 境界: {avatar.realm}                               │
│   - 年龄: {avatar.age}                                 │
│   - 宗门: {avatar.sect.name if avatar.sect else "散修"} │
│   - 当前位置: ({avatar.x}, {avatar.y})                 │
│                                                        │
│   # 当前状态                                           │
│   - 修为进度: {avatar.cultivation_progress}%           │
│   - 生命值: {avatar.hp}/{avatar.max_hp}                │
│   - 灵石: {avatar.magic_stones}                        │
│                                                        │
│   # 周围环境                                           │
│   {nearby_avatars}                                     │
│   {nearby_regions}                                     │
│                                                        │
│   # 最近记忆                                           │
│   {avatar.recent_memories}                             │
│                                                        │
│   # 长期目标                                           │
│   {avatar.long_term_objectives}                        │
│                                                        │
│   # 短期目标                                           │
│   {avatar.short_term_objectives}                       │
│                                                        │
│   请决定下一步动作，返回 JSON:                          │
│   {{                                                   │
│     "action": "move|cultivate|trade|...",              │
│     "target": "...",                                   │
│     "reasoning": "为什么做这个决定"                      │
│   }}                                                   │
│   """                                                  │
└────────────────────────────────────────────────────────┘
  │
  ▼
调用 LLM API
  │
  ┌────────────────────────────────────────────┐
  │ client.chat.completions.create(           │
  │   model=config.model_name,                 │
  │   messages=[                               │
  │     {"role": "system", "content": "..."},  │
  │     {"role": "user", "content": prompt}    │
  │   ],                                       │
  │   response_format={"type": "json_object"}  │
  │ )                                          │
  └────────────────────────────────────────────┘
  │
  ▼ (异步等待响应)
LLM 返回 JSON
  {
    "action": "cultivate",
    "target": null,
    "reasoning": "当前修为接近突破，应专心修炼"
  }
  │
  ▼
解析 JSON
  │
  ┌────────────────────────────────────────────┐
  │ action_type = response["action"]           │
  │ action_class = ACTION_REGISTRY[action_type]│
  │ action = action_class(avatar, ...)         │
  └────────────────────────────────────────────┘
  │
  ▼
返回动作
  │
  ▼
avatar.start_action(action)
  │
  ▼
生成事件
  Event(
    content=f"{avatar.name} 开始修炼。{reasoning}",
    related_avatars=[avatar.id]
  )
```

**错误处理**:
```
如果 LLM 调用失败:
  ├─ 网络超时 → 回退到规则 AI
  ├─ JSON 解析失败 → 回退到规则 AI
  ├─ 返回的动作不合法 → 回退到规则 AI
  └─ 记录错误日志
```

---

### 4. 用户交互数据流

#### 示例：查看角色详情

```
[前端] 用户点击地图上的角色精灵
  │
  ▼
[前端] AvatarSprite.vue 触发 @click 事件
  │
  ▼
[前端] 组件调用 avatarStore.selectAvatar(avatarId)
  │
  ▼
[前端] Store 更新 selectedAvatarId
  │
  ▼
[前端] 触发 watch，打开 AvatarPanel
  │
  ▼
[前端] AvatarPanel.vue mounted 时请求详情
  │
  ▼
[前端] avatarAPI.getDetail(avatarId)
  │
  ▼
GET /api/detail?type=avatar&id=xxx
  │
  ▼
[后端] API 路由处理器
  │
  ▼
[后端] avatar = world.avatar_manager.get_avatar(id)
  │
  ▼
[后端] info = avatar.get_structured_info()
  │
  ┌──────────────────────────────────────────┐
  │ avatar.get_structured_info() 内部        │
  ├──────────────────────────────────────────┤
  │ return {                                 │
  │   "basic": {                             │
  │     "id": self.id,                       │
  │     "name": self.name,                   │
  │     "realm": self.realm.value,           │
  │     "level": self.level,                 │
  │     "age": self.age,                     │
  │     ...                                  │
  │   },                                     │
  │   "cultivation": {                       │
  │     "progress": self.cultivation_exp,    │
  │     "technique": self.technique.name,    │
  │     "spiritual_roots": [...],            │
  │     ...                                  │
  │   },                                     │
  │   "items": {                             │
  │     "weapons": [...],                    │
  │     "auxiliaries": [...],                │
  │     "elixirs": [...],                    │
  │     "magic_stones": self.magic_stones    │
  │   },                                     │
  │   "relationships": [                     │
  │     {target_id, type, value}, ...        │
  │   ],                                     │
  │   "memories": [                          │
  │     {content, timestamp}, ...            │
  │   ],                                     │
  │   "objectives": {                        │
  │     "long_term": [...],                  │
  │     "short_term": [...]                  │
  │   }                                      │
  │ }                                        │
  └──────────────────────────────────────────┘
  │
  ▼
[后端] 返回 JSON
  │
  ▼
[前端] 接收响应
  │
  ▼
[前端] AvatarPanel 渲染数据
  │
  ┌──────────────────────────────────────────┐
  │ 显示基本信息卡片                          │
  │ 显示修炼进度条                            │
  │ 显示物品列表                              │
  │ 显示关系图                                │
  │ 显示记忆时间线                            │
  │ 显示目标清单                              │
  └──────────────────────────────────────────┘
```

#### 示例：设置角色目标

```
[前端] 用户在 AvatarPanel 输入目标文本
  │
  ▼
[前端] 用户点击"设置目标"按钮
  │
  ▼
[前端] 组件调用 avatarAPI.setObjective(avatarId, content)
  │
  ▼
POST /api/action/set_long_term_objective
{
  "avatar_id": "xxx",
  "content": "加入青云门"
}
  │
  ▼
[后端] API 路由处理器
  │
  ▼
[后端] avatar = world.avatar_manager.get_avatar(avatar_id)
  │
  ▼
[后端] set_user_long_term_objective(avatar, content)
  │
  ┌──────────────────────────────────────────┐
  │ set_user_long_term_objective() 内部      │
  ├──────────────────────────────────────────┤
  │ objective = UserObjective(              │
  │   content=content,                       │
  │   priority="user",  # 最高优先级         │
  │   created_at=current_time                │
  │ )                                        │
  │ avatar.objectives.add(objective)         │
  │ # 清除与此冲突的 AI 生成目标             │
  │ avatar.objectives.remove_conflicting()   │
  └──────────────────────────────────────────┘
  │
  ▼
[后端] 返回成功
  {"status": "ok", "message": "Objective set"}
  │
  ▼
[前端] 显示提示
  "目标已设置 ✓"
  │
  ▼
[前端] 刷新 AvatarPanel 数据
  │
  ▼
下一次 AI 决策时，LLM 提示词会包含这个用户目标
  # 长期目标
  - [用户设定] 加入青云门 (最高优先级)
  - [AI生成] 突破到筑基期
  │
  ▼
LLM 会优先考虑用户目标，做出相应决策
  例如: 移动到青云门驻地、寻找推荐人等
```

---

### 5. 存档与加载数据流

#### 保存游戏

```
[前端] 用户点击"保存游戏"
  │
  ▼
POST /api/game/save
  │
  ▼
[后端] API 路由处理器
  │
  ▼
[后端] save_game(world, sim, existed_sects)
  │
  ┌──────────────────────────────────────────┐
  │ save_game() 内部流程                     │
  ├──────────────────────────────────────────┤
  │ 1. 生成文件名                            │
  │    timestamp = datetime.now()            │
  │    filename = f"save_{timestamp}.json"   │
  │                                          │
  │ 2. 序列化世界状态                        │
  │    data = {                              │
  │      "meta": {                           │
  │        "version": "0.1.0",               │
  │        "save_time": timestamp,           │
  │        "game_time": f"Year {y}, Month {m}",│
  │        "language": current_language      │
  │      },                                  │
  │      "world": {                          │
  │        "month_stamp": world.month_stamp, │
  │        "phenomenon": ...,                │
  │        "map": ...                        │
  │      },                                  │
  │      "avatars": [                        │
  │        avatar.to_dict() for avatar in avatars │
  │      ],                                  │
  │      "sects": [...],                     │
  │      "regions": [...]                    │
  │    }                                     │
  │                                          │
  │ 3. 写入 JSON 文件                        │
  │    with open(filename, 'w') as f:        │
  │      json.dump(data, f, indent=2)        │
  │                                          │
  │ 4. 事件数据库已自动持久化到 SQLite        │
  │    (EventManager 实时写入)               │
  └──────────────────────────────────────────┘
  │
  ▼
[后端] 返回成功
  {"status": "ok", "filename": "save_xxx.json"}
  │
  ▼
[前端] 显示提示
  "游戏已保存: save_xxx.json ✓"
```

#### 加载游戏

```
[前端] 用户选择存档文件
  │
  ▼
POST /api/game/load
{
  "filename": "save_xxx.json"
}
  │
  ▼
[后端] API 路由处理器
  │
  ▼
[后端] load_game(save_path)
  │
  ┌──────────────────────────────────────────┐
  │ load_game() 内部流程                     │
  ├──────────────────────────────────────────┤
  │ 1. 读取 JSON 文件                        │
  │    with open(save_path) as f:            │
  │      data = json.load(f)                 │
  │                                          │
  │ 2. 检查语言设置                          │
  │    save_lang = data["meta"]["language"]  │
  │    if save_lang != current_lang:         │
  │      switch_language(save_lang)          │
  │      reload_static_data()                │
  │                                          │
  │ 3. 重建世界状态                          │
  │    world = World.from_dict(data["world"])│
  │    world.month_stamp = data["month_stamp"]│
  │                                          │
  │ 4. 重建所有角色                          │
  │    for avatar_data in data["avatars"]:   │
  │      avatar = Avatar.from_dict(avatar_data)│
  │      world.avatar_manager.register(avatar)│
  │                                          │
  │ 5. 重建宗门                              │
  │    sects = [Sect.from_dict(s) for s in data["sects"]]│
  │                                          │
  │ 6. 关联 SQLite 事件数据库                │
  │    db_path = save_path.replace('.json', '.db')│
  │    event_manager = EventManager(db_path) │
  │                                          │
  │ 7. 创建新的 Simulator                    │
  │    sim = Simulator(world)                │
  │                                          │
  │ 8. 返回                                  │
  │    return world, sim, sects              │
  └──────────────────────────────────────────┘
  │
  ▼
[后端] 替换全局实例
  game_instance["world"] = new_world
  game_instance["sim"] = new_sim
  │
  ▼
[后端] 返回成功
  {"status": "ok", "message": "Game loaded"}
  │
  ▼
[前端] 刷新所有数据
  ├─ GET /api/map (重新加载地图)
  ├─ GET /api/state (获取当前状态)
  └─ 清空 eventStore，重新分页加载事件
  │
  ▼
[前端] 重新渲染游戏世界
```

---

## 📡 WebSocket 消息详解

### 客户端 → 服务端

目前只有心跳：
```json
"ping"
```

响应：
```json
{"type": "pong"}
```

### 服务端 → 客户端

#### 1. tick 消息（游戏循环推送）

```json
{
  "type": "tick",
  "year": 150,
  "month": 5,
  "events": [
    {
      "id": "evt-1803-0",
      "content": "张三突破到金丹期，引发天地异象",
      "year": 150,
      "month": 5,
      "month_stamp": 1803,
      "related_avatar_ids": ["uuid-xxx"],
      "is_major": true,
      "is_story": false,
      "created_at": 1738467890.5
    }
  ],
  "avatars": [
    {
      "id": "uuid-xxx",
      "name": "张三",
      "x": 50,
      "y": 30,
      "gender": "male",
      "pic_id": 42,
      "action": "突破",
      "action_emoji": "⚡",
      "is_dead": false
    }
  ],
  "phenomenon": {
    "id": 3,
    "name": "灵气复苏",
    "desc": "天地间灵气浓度大增",
    "rarity": "SR",
    "duration_years": 10,
    "effect_desc": "修炼速度 +50%"
  },
  "active_domains": [
    {
      "id": 1,
      "name": "青冥秘境",
      "desc": "远古修士遗留的秘境",
      "max_realm": "GOLDEN_CORE",
      "danger_prob": 0.3,
      "drop_prob": 0.8,
      "is_open": true,
      "cd_years": 100,
      "open_prob": 0.05
    }
  ]
}
```

#### 2. llm_config_required 消息

```json
{
  "type": "llm_config_required",
  "error": "LLM 连接失败: API Key 无效"
}
```

前端应该：
- 显示 LLM 配置对话框
- 暂停游戏（自动暂停）
- 提示用户配置 API

#### 3. toast 消息

```json
{
  "type": "toast",
  "level": "info",  // info/warning/error/success
  "message": "存档已保存",
  "language": "zh-CN"  // 可选，用于语言切换提示
}
```

---

## 🔁 状态同步策略

### 增量更新 vs 全量更新

#### 增量更新（推荐）
用于高频数据（角色位置、动作）：
```javascript
// 只发送变化的角色
avatars: [
  { id: "xxx", x: 51, y: 30 },  // 只更新位置
  { id: "yyy", action_emoji: "💊" }  // 只更新动作
]
```

#### 全量更新
用于低频数据（地图、配置）：
```javascript
// 首次加载时发送完整地图
map: {
  width: 100,
  height: 100,
  data: [[...], [...], ...]  // 完整瓦片数据
}
```

### 冲突解决

**原则**: 服务端为真实数据源（Single Source of Truth）

前端状态与服务端冲突时：
1. **立即使用前端状态**（乐观更新，提升响应速度）
2. **等待服务端确认**
3. **如果冲突，以服务端为准**

示例：
```typescript
// 用户设置角色目标
async function setObjective(avatarId: string, content: string) {
  // 1. 乐观更新前端
  avatarStore.updateObjective(avatarId, content)

  try {
    // 2. 请求服务端
    await avatarAPI.setObjective(avatarId, content)
    // 3. 成功 → 前端状态正确
  } catch (error) {
    // 4. 失败 → 回滚前端状态
    avatarStore.rollbackObjective(avatarId)
    showError("设置失败: " + error.message)
  }
}
```

---

## 📊 性能优化策略

### 1. WebSocket 推送优化

**问题**: 100 个角色每秒都推送完整数据 → 过大

**优化**:
```python
# 只推送变化的角色
avatar_updates = []

# 新生角色：完整数据
for aid in newly_born:
    avatar_updates.append(full_avatar_data(aid))

# 死亡角色：只发 is_dead 标记
for aid in newly_dead:
    avatar_updates.append({"id": aid, "is_dead": true})

# 其他角色：只发位置（限制数量）
for avatar in living_avatars[:50]:  # 只发前 50 个
    avatar_updates.append({"id": avatar.id, "x": avatar.x, "y": avatar.y})
```

### 2. 事件查询优化

**问题**: 一次查询上万条事件 → 内存爆炸

**优化**: 分页查询 + 懒加载
```python
# 后端分页
def get_events_paginated(cursor=None, limit=100):
    query = "SELECT * FROM events WHERE month_stamp < ? ORDER BY month_stamp DESC LIMIT ?"
    return db.execute(query, (cursor or 999999, limit))

# 前端无限滚动
async function loadMoreEvents() {
  if (loading.value || !hasMore.value) return
  const { events, next_cursor, has_more } = await eventAPI.getEvents(cursor.value)
  eventStore.appendEvents(events)
  cursor.value = next_cursor
  hasMore.value = has_more
}
```

### 3. LLM 调用优化

**问题**: 100 个 NPC 同时调用 LLM → API 限流

**优化**:
```python
# 批量并发（限制并发数）
async def process_avatars(avatars):
    semaphore = asyncio.Semaphore(10)  # 最多 10 个并发

    async def bounded_decide(avatar):
        async with semaphore:
            return await avatar.decide()

    results = await asyncio.gather(*[bounded_decide(a) for a in avatars])
```

**降级策略**:
```python
# LLM 失败 → 回退到规则 AI
try:
    action = await llm_decide(avatar)
except LLMError:
    logger.warning(f"{avatar.name} LLM failed, fallback to rule AI")
    action = rule_based_decide(avatar)
```

---

## 🎯 总结

### 关键数据流路径

1. **游戏循环** (每秒):
   ```
   game_loop → sim.step() → AI决策 → 执行动作 → 生成事件 → WebSocket推送 → 前端更新
   ```

2. **用户交互**:
   ```
   前端事件 → API请求 → 后端处理 → 返回结果 → 前端更新
   ```

3. **LLM 决策**:
   ```
   avatar.decide() → 构造提示词 → 调用LLM → 解析响应 → 执行动作
   ```

4. **存档系统**:
   ```
   保存: world → JSON序列化 → 写入文件
   加载: 读取文件 → JSON反序列化 → 重建world
   ```

### 数据流设计原则

1. **单向数据流**: 服务端 → 前端（通过 WebSocket 推送）
2. **单一真实来源**: 服务端是数据的唯一真实来源
3. **增量更新**: 只推送变化的数据，减少带宽
4. **乐观更新**: 前端先更新，服务端确认后同步
5. **容错降级**: 关键路径有降级策略（如 LLM 失败 → 规则 AI）

---

**相关文档**:
- [系统架构](ARCHITECTURE.md)
- [API 文档](API.md)
- [模块依赖图](MODULE_MAP.md)
