# 术语表 (Glossary)

本文档列出修仙世界模拟器中的关键术语及其代码映射，帮助开发者（特别是 AI）快速理解项目。

---

## 🎯 修仙术语 → 代码映射

### 核心概念

| 修仙术语 | 英文/代码 | 类名/枚举 | 位置 | 说明 |
|---------|---------|----------|------|------|
| 修士/角色 | Avatar/Cultivator | `Avatar` | `src/classes/avatar/avatar.py` | 游戏中的角色实体 |
| 境界 | Realm | `CultivationRealm` (Enum) | `src/classes/cultivation.py` | 修炼层次（炼气、筑基等） |
| 修为 | Cultivation Progress | `cultivation_exp` (int) | `Avatar.cultivation_exp` | 当前境界内的修炼进度 |
| 灵根 | Spiritual Root | `SpiritualRoot` | `src/classes/root.py` | 修炼天赋（五行属性） |
| 功法 | Technique | `Technique` | `src/classes/technique.py` | 修炼方法 |
| 宗门 | Sect | `Sect` | `src/classes/sect.py` | 修仙组织 |
| 散修 | Rogue Cultivator | `sect=None` | - | 不属于任何宗门的修士 |
| 寿元 | Lifespan | `max_lifespan` (int) | `Avatar.max_lifespan` | 角色的生命上限 |
| 灵气 | Spiritual Qi | `spiritual_qi` | `Region.spiritual_qi` | 修炼资源 |
| 天地灵机 | Celestial Phenomenon | `CelestialPhenomenon` | `src/classes/celestial_phenomenon.py` | 影响全世界的灵气事件 |

### 境界体系

| 境界（中文） | 境界（英文） | 枚举值 | 等级范围 | 说明 |
|------------|------------|--------|---------|------|
| 炼气期 | Qi Refining | `QI_REFINING` | 1-30 | 初级境界 |
| 筑基期 | Foundation Establishment | `FOUNDATION_ESTABLISHMENT` | 31-60 | 中级境界 |
| 金丹期 | Golden Core | `GOLDEN_CORE` | 61-90 | 高级境界 |
| 元婴期 | Nascent Soul | `NASCENT_SOUL` | 91-120 | 顶级境界 |

**代码定义**:
```python
# src/classes/cultivation.py
class CultivationRealm(Enum):
    QI_REFINING = "炼气期"
    FOUNDATION_ESTABLISHMENT = "筑基期"
    GOLDEN_CORE = "金丹期"
    NASCENT_SOUL = "元婴期"

REALM_ORDER = [
    CultivationRealm.QI_REFINING,
    CultivationRealm.FOUNDATION_ESTABLISHMENT,
    CultivationRealm.GOLDEN_CORE,
    CultivationRealm.NASCENT_SOUL
]
```

### 动作系统

| 动作（中文） | 动作（英文） | 类名 | 位置 | 类型 | 说明 |
|------------|------------|------|------|------|------|
| 移动 | Move | `MoveAction` | `src/classes/action/move.py` | 短动作 | 移动到新位置 |
| 修炼 | Cultivate | `CultivateAction` | `src/classes/action/cultivate.py` | 长动作 | 提升修为 |
| 突破 | Breakthrough | `BreakthroughAction` | `src/classes/action/breakthrough.py` | 长动作 | 尝试进入下一境界 |
| 疗伤 | Rest/Heal | `RestAction` | `src/classes/action/rest.py` | 长动作 | 恢复生命值 |
| 战斗 | Battle | `BattleAction` | `src/classes/action/battle.py` | 多人动作 | 与其他角色战斗 |
| 对话 | Dialogue | `DialogueAction` | `src/classes/action/dialogue.py` | 多人动作 | 与其他角色对话 |
| 交易 | Trade | `TradeAction` | `src/classes/action/trade.py` | 多人动作 | 买卖物品 |
| 铸造 | Forge | `ForgeAction` | `src/classes/action/forge.py` | 长动作 | 打造武器 |
| 炼丹 | Alchemy | `AlchemyAction` | `src/classes/action/alchemy.py` | 长动作 | 炼制丹药 |
| 闭关 | Seclusion | `SeclusionAction` | `src/classes/action/seclusion.py` | 长动作 | 长时间专心修炼 |

**动作类型说明**:
- **短动作**: 立即执行完成（当月结算）
- **长动作**: 持续多个月，有进度条
- **多人动作**: 需要对方响应，有发起者和响应者

### 物品系统

| 物品（中文） | 物品（英文） | 类名 | 位置 | 说明 |
|------------|------------|------|------|------|
| 灵石 | Magic Stone | `magic_stones` (int) | `Avatar.magic_stones` | 修仙世界的货币 |
| 丹药 | Elixir | `Elixir` | `src/classes/elixir.py` | 药品，提升修为或恢复 |
| 兵器 | Weapon | `Weapon` | `src/classes/weapon.py` | 武器，提升战斗力 |
| 法宝 | Auxiliary | `Auxiliary` | `src/classes/auxiliary.py` | 辅助装备（护甲、饰品） |
| 灵药 | Spirit Herb | `Material` | `src/classes/material.py` | 炼丹材料 |
| 矿石 | Ore | `Material` | `src/classes/material.py` | 铸造材料 |

### 事件系统

| 事件类型（中文） | 事件类型（英文） | 字段 | 说明 |
|----------------|----------------|------|------|
| 普通事件 | Normal Event | `is_major=False` | 日常活动（移动、修炼） |
| 大事件 | Major Event | `is_major=True` | 重要事件（突破、死亡、战斗） |
| 剧情事件 | Story Event | `is_story=True` | LLM 生成的剧情描述 |

**代码定义**:
```python
# src/classes/event.py
@dataclass
class Event:
    id: str
    content: str  # 事件描述文本
    month_stamp: int  # 时间戳
    related_avatars: List[str]  # 相关角色 ID
    is_major: bool = False  # 是否为大事
    is_story: bool = False  # 是否为剧情
    created_at: float = 0.0  # 创建时间（Unix时间戳）
```

### 世界元素

| 元素（中文） | 元素（英文） | 类名 | 位置 | 说明 |
|------------|------------|------|------|------|
| 世界 | World | `World` | `src/classes/world.py` | 游戏世界容器 |
| 地图 | Map | `Map` | `src/classes/map.py` | 游戏地图（瓦片） |
| 区域 | Region | `Region` | `src/classes/region.py` | 地图上的功能区域 |
| 城市 | City | `CityRegion` | `src/classes/region.py` | 城市区域 |
| 宗门驻地 | Sect Region | `SectRegion` | `src/classes/sect_region.py` | 宗门所在地 |
| 洞府 | Cave Abode | `CultivationRegion` | `src/classes/region.py` | 修炼场所 |
| 秘境 | Hidden Domain | `HiddenDomain` | `src/classes/gathering/hidden_domain.py` | 探险副本 |
| 天劫 | Tribulation | `Tribulation` | `src/classes/tribulation.py` | 突破时的劫难 |
| 心魔 | Inner Demon | `InnerDemon` | `src/classes/tribulation.py` | 修炼时的心理障碍 |

### AI 系统

| 术语（中文） | 术语（英文） | 代码实体 | 说明 |
|------------|------------|---------|------|
| 规则 AI | Rule-based AI | `rule_based_decide()` | 基于条件的确定性决策 |
| LLM AI | LLM AI | `llm_decide_action()` | 基于大语言模型的创造性决策 |
| 觉醒率 | Awakening Rate | `npc_awakening_rate_per_month` | NPC 激活 LLM AI 的概率 |
| 提示词 | Prompt | `build_llm_prompt()` | 发送给 LLM 的输入文本 |
| 记忆 | Memory | `Memory` | 角色的短期记忆 |
| 目标 | Objective | `Objective` | 角色的长短期目标 |
| 性格 | Persona | `Persona` | 角色的性格特质 |

---

## 🔧 技术术语

### 后端术语

| 术语 | 说明 | 示例 |
|------|------|------|
| `game_instance` | 全局游戏实例字典 | `game_instance["world"]` |
| `game_loop` | 后台游戏循环函数 | 每秒执行一次 |
| `Simulator` | 游戏模拟器类 | `Simulator.step()` 推进一个月 |
| `AvatarManager` | 角色管理器 | 管理所有角色的生命周期 |
| `EventManager` | 事件管理器 | 管理事件的存储和查询 |
| `month_stamp` | 月份时间戳 | 从游戏开始的总月数 |
| `newly_born` | 新生角色集合 | 本回合新生的角色 ID |
| `newly_dead` | 死亡角色集合 | 本回合死亡的角色 ID |

### 前端术语

| 术语 | 说明 | 示例 |
|------|------|------|
| `gameStore` | 游戏状态 Store | Pinia Store |
| `avatarStore` | 角色状态 Store | Pinia Store |
| `eventStore` | 事件状态 Store | Pinia Store |
| `PixiJS` | 2D 渲染引擎 | 用于渲染地图和角色 |
| `AvatarSprite` | 角色精灵组件 | Vue 组件 |
| `tick` | 游戏循环推送消息 | WebSocket 消息类型 |

### 配置术语

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `init_npc_num` | 初始 NPC 数量 | 12 |
| `sect_num` | 宗门数量 | 3 |
| `start_year` | 游戏起始年份 | 100 |
| `npc_awakening_rate_per_month` | NPC 激活 LLM 概率 | 0.01 (1%) |
| `world_history` | 世界背景设定 | 空字符串 |
| `language` | 语言设置 | "zh-CN" |

---

## 📐 数据结构映射

### Avatar (角色)

```python
class Avatar:
    # 基础属性
    id: str                    # 唯一 ID (UUID)
    name: str                  # 姓名
    gender: Gender             # 性别（男/女）
    age: int                   # 年龄
    max_lifespan: int          # 寿元上限

    # 修炼属性
    realm: CultivationRealm    # 境界
    level: int                 # 境界内等级 (1-30)
    cultivation_exp: int       # 修为经验值
    spiritual_roots: List[SpiritualRoot]  # 灵根

    # 战斗属性
    hp: int                    # 当前生命值
    max_hp: int                # 最大生命值
    attack: int                # 攻击力
    defense: int               # 防御力

    # 物品
    magic_stones: int          # 灵石数量
    weapons: List[Weapon]      # 武器
    auxiliaries: List[Auxiliary]  # 辅助装备
    elixirs: List[Elixir]      # 丹药

    # 社交
    sect: Optional[Sect]       # 所属宗门
    relationships: List[Relationship]  # 人际关系

    # AI
    personas: List[Persona]    # 性格特质
    memories: List[Memory]     # 记忆
    objectives: List[Objective]  # 目标

    # 位置
    pos_x: int                 # X 坐标
    pos_y: int                 # Y 坐标

    # 当前状态
    current_action: Optional[ActionInstance]  # 当前动作
```

### Event (事件)

```python
@dataclass
class Event:
    id: str                    # 事件 ID
    content: str               # 事件描述
    month_stamp: int           # 时间戳（月）
    related_avatars: List[str]  # 相关角色 ID
    is_major: bool             # 是否为大事
    is_story: bool             # 是否为剧情
    created_at: float          # 创建时间（Unix）
```

### Action (动作)

```python
class Action:
    name: str                  # 动作名称
    EMOJI: str                 # 动作表情符号
    duration: int              # 持续时间（月）
    is_long_action: bool       # 是否为长动作
    is_mutual_action: bool     # 是否为多人动作

    def execute(avatar: Avatar) -> ActionResult:
        """执行动作"""
        pass

    def settle(avatar: Avatar) -> ActionResult:
        """结算动作（长动作完成时）"""
        pass
```

---

## 🌍 世界观术语

### 修仙等级体系

```
凡人
  ↓ (开始修炼)
炼气期 (1-30层)
  ↓ (筑基突破)
筑基期 (31-60层)
  ↓ (结丹突破)
金丹期 (61-90层)
  ↓ (化婴突破)
元婴期 (91-120层)
  ↓ (飞升)
上界（未实现）
```

### 宗门类型

| 宗门 | 阵营 | 特色 |
|------|------|------|
| 青云门 | 正道 | 剑修为主，重视正义 |
| 合欢宗 | 魔道 | 双修功法，阴阳互补 |
| 百兽宗 | 中立 | 御兽为主，与妖兽共生 |
| 天机阁 | 正道 | 炼丹、炼器、阵法 |
| ...（可扩展） | | |

### 灵根属性

| 灵根 | 五行 | 对应功法 |
|------|------|---------|
| 金灵根 | 金 | 剑修、攻击型 |
| 木灵根 | 木 | 生命、恢复型 |
| 水灵根 | 水 | 柔和、控制型 |
| 火灵根 | 火 | 爆发、攻击型 |
| 土灵根 | 土 | 防御、稳固型 |
| 天灵根 | 全属性 | 天才，罕见 |
| 伪灵根 | 无 | 修炼困难 |

---

## 🔗 常见缩写

| 缩写 | 全称 | 说明 |
|------|------|------|
| NPC | Non-Player Character | 非玩家角色 |
| LLM | Large Language Model | 大语言模型 |
| AI | Artificial Intelligence | 人工智能 |
| API | Application Programming Interface | 应用程序接口 |
| WS | WebSocket | WebSocket 协议 |
| JSON | JavaScript Object Notation | 数据格式 |
| YAML | YAML Ain't Markup Language | 配置文件格式 |
| CSV | Comma-Separated Values | 表格数据格式 |
| DB | Database | 数据库 |
| UUID | Universally Unique Identifier | 通用唯一标识符 |

---

## 📚 相关文档

- [系统架构](ARCHITECTURE.md) - 整体架构设计
- [数据流](DATA_FLOW.md) - 数据流向详解
- [API 文档](API.md) - API 接口说明
- [常见任务](COMMON_TASKS.md) - 开发任务指南

---

**维护说明**:
- 当添加新的游戏概念时，更新此术语表
- 保持中英文对照一致
- 提供代码位置，方便查找
