# 编码规范和约定

## 🎯 设计原则

### 1. AI 可读性优先
- **详细的 Docstrings**: 每个类、函数必须有完整的文档字符串
- **类型注解**: 所有函数参数和返回值必须有类型
- **语义化命名**: 名称应该自解释，避免缩写
- **注释说明"为什么"**: 代码说明"怎么做"，注释说明"为什么这样做"

### 2. 模块化和单一职责
- 每个类只负责一件事
- 避免上帝类 (God Class)
- 函数长度 < 50 行（复杂逻辑拆分）

### 3. 显式优于隐式
- 避免魔法数字，使用常量
- 避免隐式类型转换
- 明确错误处理，不要吞掉异常

## 📝 Python 代码规范

### 文档字符串 (Google Style)

```python
class AvatarManager:
    """管理所有游戏角色的生命周期

    职责:
        - 注册和移除角色
        - 跟踪新生和死亡
        - 提供查询接口

    属性:
        avatars (Dict[str, Avatar]): 所有活着的角色，键为 avatar_id
        dead_avatars (Dict[str, Avatar]): 已死亡的角色
        newly_born (Set[str]): 本回合新生的角色 ID
        newly_dead (Set[str]): 本回合死亡的角色 ID

    示例:
        >>> manager = AvatarManager()
        >>> avatar = create_avatar("张三", realm=Realm.QI_REFINING)
        >>> manager.register_avatar(avatar, is_newly_born=True)
        >>> print(len(manager.avatars))
        1
    """

    def register_avatar(
        self,
        avatar: Avatar,
        is_newly_born: bool = False
    ) -> None:
        """注册一个角色到管理器

        Args:
            avatar: 要注册的角色对象
            is_newly_born: 是否是新生角色（触发新生事件）

        Raises:
            ValueError: 如果角色 ID 已存在

        注意:
            - 新生角色会被添加到 newly_born 集合，用于前端增量更新
            - 这个集合会在下一轮 tick 后被清空
        """
        if avatar.id in self.avatars:
            raise ValueError(f"Avatar {avatar.id} already exists")

        self.avatars[avatar.id] = avatar

        if is_newly_born:
            self.newly_born.add(avatar.id)
```

### 类型注解

```python
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

# ✅ 好的例子
def calculate_battle_power(
    avatar: Avatar,
    include_equipment: bool = True,
    buff_multiplier: float = 1.0
) -> int:
    """计算角色战斗力"""
    pass

@dataclass
class BattleResult:
    """战斗结果

    Attributes:
        winner_id: 胜利者 ID
        loser_id: 失败者 ID
        damage_dealt: 造成的伤害
        rounds: 战斗回合数
    """
    winner_id: str
    loser_id: str
    damage_dealt: int
    rounds: int

# ❌ 避免
def calc(a, b=True, c=1.0):  # 没有类型，参数名不清晰
    pass
```

### 命名约定

```python
# 类名: PascalCase
class CultivationManager:
    pass

# 函数/变量: snake_case
def calculate_cultivation_speed():
    base_speed = 10
    spiritual_root_bonus = 0.5

# 常量: UPPER_SNAKE_CASE
MAX_LIFESPAN = 500
DEFAULT_CULTIVATION_SPEED = 10

# 私有成员: _leading_underscore
class Avatar:
    def __init__(self):
        self._internal_state = {}

    def _calculate_hidden_bonus(self):
        """私有方法"""
        pass

# 枚举: PascalCase，成员 UPPER_CASE
class Realm(Enum):
    QI_REFINING = "炼气期"
    FOUNDATION_ESTABLISHMENT = "筑基期"
```

### 错误处理

```python
# ✅ 好的例子：明确的错误处理
async def call_llm_api(prompt: str) -> Optional[str]:
    """调用 LLM API

    Returns:
        API 返回的文本，失败时返回 None

    注意:
        - 网络错误会被捕获并记录日志
        - 返回 None 时调用者应该有降级策略（如使用规则 AI）
    """
    try:
        response = await client.chat.completions.create(...)
        return response.choices[0].message.content
    except httpx.TimeoutException as e:
        logger.error(f"LLM API timeout: {e}")
        return None
    except Exception as e:
        logger.error(f"LLM API error: {e}", exc_info=True)
        return None

# ❌ 避免：吞掉异常
try:
    result = some_function()
except:  # 太宽泛，而且没有处理
    pass
```

### 魔法数字 → 常量

```python
# ❌ 不好
if avatar.age > 150:
    avatar.die()

# ✅ 好
MORTAL_MAX_LIFESPAN = 150  # 凡人最大寿元

if avatar.age > MORTAL_MAX_LIFESPAN:
    avatar.die()
```

## 🎨 TypeScript/Vue 规范

### 组件结构

```vue
<script setup lang="ts">
/**
 * 角色详情面板
 *
 * 功能:
 * - 显示角色的境界、属性、装备
 * - 支持设置长期目标
 * - 显示角色的人际关系
 *
 * Props:
 * - avatarId: 要显示的角色 ID
 *
 * Emits:
 * - close: 关闭面板时触发
 */
import { ref, computed, watch } from 'vue'
import type { Avatar } from '@/types/avatar'

interface Props {
  avatarId: string
}

interface Emits {
  (e: 'close'): void
  (e: 'update', avatarId: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 组件逻辑...
</script>

<template>
  <!-- 模板内容 -->
</template>

<style scoped lang="scss">
/* 样式 */
</style>
```

### 类型定义

```typescript
// web/src/types/avatar.ts

/**
 * 角色基础信息
 */
export interface Avatar {
  /** 角色唯一 ID (UUID) */
  id: string

  /** 角色姓名 */
  name: string

  /** 修炼境界 */
  realm: CultivationRealm

  /** 境界内等级 (1-30) */
  level: number

  /** 年龄 */
  age: number

  /** 所属宗门 ID，散修为 null */
  sect_id: number | null

  /** 当前位置 X 坐标 */
  pos_x: number

  /** 当前位置 Y 坐标 */
  pos_y: number
}

/**
 * 修炼境界枚举
 */
export enum CultivationRealm {
  QI_REFINING = "炼气期",
  FOUNDATION_ESTABLISHMENT = "筑基期",
  GOLDEN_CORE = "金丹期",
  NASCENT_SOUL = "元婴期"
}
```

### 命名约定

```typescript
// 组件文件: PascalCase.vue
AvatarDetailPanel.vue
SystemMenu.vue

// 工具函数文件: camelCase.ts
formatDate.ts
apiClient.ts

// 类型文件: camelCase.ts
avatar.ts
event.ts

// 常量文件: UPPER_SNAKE_CASE.ts 或 constants.ts
REALMS.ts
constants.ts
```

## 📁 文件组织

### 后端文件组织

```
src/classes/
├── __init__.py          # 空文件或导出主要类
├── avatar/
│   ├── __init__.py      # 导出 Avatar
│   ├── avatar.py        # Avatar 类定义
│   ├── planner.py       # AvatarPlanner (决策逻辑)
│   └── metrics.py       # AvatarMetrics (数据统计)
├── action/
│   ├── __init__.py      # 导出所有 Action
│   ├── base.py          # Action 基类
│   ├── move.py          # Move Action
│   └── cultivate.py     # Cultivate Action
└── README.md            # 模块总览
```

**规则**:
1. 一个文件只定义一个主要类
2. 相关的小类可以放在同一文件
3. 每个目录必须有 `__init__.py` 和 `README.md`

### 前端文件组织

```
web/src/components/
├── game/
│   ├── GameMap.vue         # 游戏地图
│   ├── AvatarSprite.vue    # 角色精灵
│   └── RegionMarker.vue    # 区域标记
├── panels/
│   ├── AvatarPanel.vue     # 角色面板
│   ├── EventPanel.vue      # 事件面板
│   └── SectPanel.vue       # 宗门面板
├── layout/
│   ├── MainLayout.vue      # 主布局
│   └── TopBar.vue          # 顶部栏
└── README.md               # 组件总览
```

## 🧪 测试规范

### 测试文件命名

```
tests/
├── test_avatar.py          # 测试 Avatar 类
├── test_cultivation.py     # 测试修炼系统
└── test_battle.py          # 测试战斗系统

web/src/__tests__/
├── AvatarPanel.test.ts     # 测试 AvatarPanel 组件
└── formatDate.test.ts      # 测试工具函数
```

### 测试结构

```python
# tests/test_avatar.py
import pytest
from src.classes.avatar import Avatar
from src.classes.cultivation import Realm

class TestAvatarCreation:
    """测试角色创建功能"""

    def test_create_basic_avatar(self):
        """测试创建基础角色"""
        avatar = Avatar(
            name="张三",
            realm=Realm.QI_REFINING,
            level=1
        )

        assert avatar.name == "张三"
        assert avatar.realm == Realm.QI_REFINING
        assert avatar.level == 1

    def test_create_avatar_with_sect(self):
        """测试创建带宗门的角色"""
        # Given: 一个宗门
        sect = Sect(id=1, name="青云门")

        # When: 创建角色并加入宗门
        avatar = Avatar(name="李四", sect=sect)

        # Then: 角色应该属于该宗门
        assert avatar.sect == sect
        assert avatar.sect_id == 1

class TestCultivation:
    """测试修炼系统"""

    @pytest.fixture
    def avatar(self):
        """测试用角色"""
        return Avatar(name="王五", realm=Realm.QI_REFINING, level=9)

    def test_breakthrough_success(self, avatar):
        """测试突破成功"""
        # Given: 角色满足突破条件
        avatar.cultivation_exp = 1000

        # When: 尝试突破
        result = avatar.attempt_breakthrough()

        # Then: 应该突破成功
        assert result.success is True
        assert avatar.realm == Realm.FOUNDATION_ESTABLISHMENT
```

## 📊 性能规范

### 1. 数据库查询
```python
# ✅ 好：使用分页
events = event_manager.get_events_paginated(limit=100, cursor=cursor)

# ❌ 避免：一次加载所有数据
all_events = event_manager.get_all_events()  # 可能有上万条
```

### 2. LLM 调用
```python
# ✅ 好：批量处理
async def process_avatars_batch(avatars: List[Avatar]):
    """批量处理角色决策，使用 asyncio.gather 并发"""
    tasks = [avatar.make_decision() for avatar in avatars]
    results = await asyncio.gather(*tasks, return_exceptions=True)

# ❌ 避免：串行调用
for avatar in avatars:
    await avatar.make_decision()  # 太慢
```

### 3. 前端渲染
```typescript
// ✅ 好：虚拟滚动
<VirtualList :items="events" :item-height="50" />

// ❌ 避免：渲染所有元素
<div v-for="event in allEvents">...</div>  // 可能上千个
```

## 🔄 Git 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 添加测试
- `chore`: 构建/工具变更

**示例**:
```
feat(avatar): add spiritual root system

- Add SpiritualRoot class with five elements
- Implement cultivation speed calculation based on roots
- Add tests for root compatibility

Closes #123
```

## 🚨 关键路径标记

使用注释标记关键代码：

```python
# 🔴 CRITICAL PATH: 游戏主循环
# 任何修改必须：
# 1. 充分测试性能
# 2. 确保异常不会中断循环
# 3. 更新相关文档
async def game_loop():
    pass

# ⚠️ PERFORMANCE CRITICAL: 每秒调用一次
def update_all_avatars():
    pass

# 💡 DESIGN DECISION: 为什么用双层 AI
# 原因：规则 AI 处理确定性逻辑（快），LLM AI 处理创造性逻辑（慢但智能）
# 详见: docs/adr/ADR-004-llm-integration.md
def avatar_ai_decision():
    pass
```

## 📚 文档规范

### README.md 模板

```markdown
# 模块名称

## 用途
简短描述（1-2句话）

## 核心类/函数
- `ClassName`: 做什么
- `function_name()`: 做什么

## 依赖关系
- 依赖于: ModuleA, ModuleB
- 被依赖于: ModuleX, ModuleY

## 使用示例
\```python
from src.module import ClassName

obj = ClassName()
result = obj.do_something()
\```

## 注意事项
- 重要的约束
- 常见陷阱
```

---

**遵循这些规范，让 AI 能够：**
1. ✅ 快速理解代码意图
2. ✅ 准确定位修改位置
3. ✅ 自动生成测试用例
4. ✅ 评估变更影响范围
5. ✅ 提供高质量的重构建议
