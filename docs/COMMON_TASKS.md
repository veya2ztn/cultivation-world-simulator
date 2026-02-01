# 常见开发任务指南

本文档提供实用的开发任务指南，帮助 AI 和开发者快速完成常见的开发任务。

每个任务包含：
- 任务描述
- 涉及的文件（带绝对路径）
- 详细步骤（带完整代码示例）
- 测试方法
- 常见陷阱和注意事项

---

## 目录

1. [如何添加新的角色动作（Action）](#1-如何添加新的角色动作action)
2. [如何添加新的 API 端点](#2-如何添加新的-api-端点)
3. [如何添加新的游戏事件类型](#3-如何添加新的游戏事件类型)
4. [如何添加新的 UI 面板](#4-如何添加新的-ui-面板)
5. [如何修改 LLM 提示词](#5-如何修改-llm-提示词)
6. [如何添加新的修仙境界](#6-如何添加新的修仙境界)
7. [如何添加新的宗门](#7-如何添加新的宗门)
8. [如何扩展存档格式](#8-如何扩展存档格式)
9. [如何添加新的测试用例](#9-如何添加新的测试用例)
10. [如何调试 WebSocket 通信](#10-如何调试-websocket-通信)

---

## 1. 如何添加新的角色动作（Action）

### 任务描述
创建一个新的角色动作类，让 NPC 和玩家能够执行该动作。

### 涉及的文件
- 新建文件：`src/classes/action/my_action.py`
- 注册文件：`src/classes/action/__init__.py`

### 详细步骤

#### 步骤 1：创建动作类文件

在 `src/classes/action/` 目录下创建新文件，例如 `meditate.py`：

```python
from __future__ import annotations

from src.i18n import t
from src.classes.action import TimedAction, register_action
from src.classes.event import Event


@register_action(actual=True)
class Meditate(TimedAction):
    """
    冥想动作，恢复精神力并提升悟性。
    """

    # 多语言 ID（需要在 i18n 文件中定义）
    ACTION_NAME_ID = "meditate_action_name"
    DESC_ID = "meditate_description"
    REQUIREMENTS_ID = "meditate_requirements"

    # 不需要翻译的常量
    EMOJI = "🧘"
    PARAMS = {}  # 如果需要参数，定义为 {"param_name": "description"}

    # 动作持续时间（月）
    duration_months = 3

    # 是否为大事（影响记忆系统）
    IS_MAJOR = False

    # 冷却时间（月）
    ACTION_CD_MONTHS = 0

    def _execute(self) -> None:
        """
        每月执行的逻辑
        """
        # 恢复精神力
        recovery = 10
        self.avatar.mental_power = min(
            self.avatar.max_mental_power,
            self.avatar.mental_power + recovery
        )

    def can_start(self) -> tuple[bool, str]:
        """
        检查是否可以开始执行

        Returns:
            (是否可以开始, 失败原因)
        """
        # 检查精神力是否已满
        if self.avatar.mental_power >= self.avatar.max_mental_power:
            return False, t("Mental power is already full")

        return True, ""

    def start(self) -> Event:
        """
        动作开始时的逻辑

        Returns:
            开始事件
        """
        content = t("{avatar} begins meditating at {location}",
                   avatar=self.avatar.name,
                   location=self.avatar.tile.location_name)
        return Event(self.world.month_stamp, content, related_avatars=[self.avatar.id])

    async def finish(self) -> list[Event]:
        """
        动作完成时的逻辑

        Returns:
            完成事件列表
        """
        content = t("{avatar} finishes meditation and feels refreshed",
                   avatar=self.avatar.name)
        event = Event(self.world.month_stamp, content, related_avatars=[self.avatar.id])
        return [event]
```

#### 步骤 2：在 `__init__.py` 中导入

编辑 `src/classes/action/__init__.py`，添加导入：

```python
# ... 其他导入 ...
from .meditate import Meditate  # 添加这一行
```

#### 步骤 3：添加多语言翻译

编辑国际化文件（假设使用 `.po` 文件），添加翻译键：

```po
msgid "meditate_action_name"
msgstr "冥想"

msgid "meditate_description"
msgstr "静心冥想，恢复精神力"

msgid "meditate_requirements"
msgstr "精神力未满"

msgid "Mental power is already full"
msgstr "精神力已满"

msgid "{avatar} begins meditating at {location}"
msgstr "{avatar}在{location}开始冥想"

msgid "{avatar} finishes meditation and feels refreshed"
msgstr "{avatar}冥想结束，精神焕发"
```

### 测试方法

#### 创建单元测试

在 `tests/test_action_meditate.py` 中创建测试：

```python
import pytest
from src.classes.action.meditate import Meditate
from src.classes.event import Event


class TestMeditate:
    """测试冥想动作"""

    @pytest.fixture
    def avatar_with_low_mental(self, dummy_avatar):
        """创建精神力低的角色"""
        dummy_avatar.mental_power = 50
        dummy_avatar.max_mental_power = 100
        return dummy_avatar

    def test_meditate_recovers_mental_power(self, avatar_with_low_mental):
        """测试冥想恢复精神力"""
        action = Meditate(avatar_with_low_mental, avatar_with_low_mental.world)

        # 检查能否开始
        can_start, reason = action.can_start()
        assert can_start is True

        # 执行一次
        action._execute()

        # 验证精神力恢复
        assert avatar_with_low_mental.mental_power == 60

    def test_cannot_meditate_when_full(self, dummy_avatar):
        """测试精神力满时无法冥想"""
        dummy_avatar.mental_power = 100
        dummy_avatar.max_mental_power = 100

        action = Meditate(dummy_avatar, dummy_avatar.world)
        can_start, reason = action.can_start()

        assert can_start is False
        assert "满" in reason
```

运行测试：

```bash
pytest tests/test_action_meditate.py -v
```

### 常见陷阱和注意事项

1. **装饰器必须使用**：`@register_action(actual=True)` 必须添加，否则动作不会被注册到系统中。

2. **继承正确的基类**：
   - `InstantAction`：一次性动作（立即完成）
   - `TimedAction`：持续性动作（需要设置 `duration_months`）

3. **多语言支持**：所有用户可见的文本都必须使用 `t()` 函数包裹，并定义对应的翻译键。

4. **事件创建**：
   - 使用 `Event()` 创建普通事件
   - 使用 `self.create_event()` 会自动带上 `IS_MAJOR` 属性

5. **异步方法**：`finish()` 必须是 `async`，即使内部没有异步操作。

6. **参数定义**：如果动作需要参数（如目标角色 ID），在 `PARAMS` 中定义，并在方法签名中接收。

---

## 2. 如何添加新的 API 端点

### 任务描述
添加一个新的 HTTP API 端点，让前端可以调用。

### 涉及的文件
- 主文件：`src/server/main.py`

### 详细步骤

#### 步骤 1：定义请求/响应模型

在 `src/server/main.py` 中添加 Pydantic 模型：

```python
# 在文件顶部导入区域添加
from pydantic import BaseModel

# 在其他模型定义附近添加
class MeditationRequest(BaseModel):
    """冥想请求"""
    avatar_id: str
    duration_hours: int = 3

class MeditationResponse(BaseModel):
    """冥想响应"""
    success: bool
    message: str
    new_mental_power: Optional[int] = None
```

#### 步骤 2：添加 API 路由

在 `src/server/main.py` 中添加路由函数：

```python
@app.post("/api/action/meditate")
async def start_meditation(request: MeditationRequest) -> MeditationResponse:
    """
    让指定角色开始冥想

    Args:
        request: 包含 avatar_id 和 duration_hours 的请求

    Returns:
        包含执行结果的响应
    """
    # 获取游戏实例
    world: World = game_instance.get("world")
    if not world:
        raise HTTPException(status_code=503, detail="Game not initialized")

    # 查找角色
    avatar = world.avatars.get(request.avatar_id)
    if not avatar:
        return MeditationResponse(
            success=False,
            message=f"Avatar {request.avatar_id} not found"
        )

    # 检查是否可以执行
    from src.classes.action.meditate import Meditate
    action = Meditate(avatar, world)
    can_start, reason = action.can_start()

    if not can_start:
        return MeditationResponse(
            success=False,
            message=reason
        )

    # 设置角色的当前动作
    avatar.set_action("Meditate", {})

    return MeditationResponse(
        success=True,
        message="Meditation started successfully",
        new_mental_power=avatar.mental_power
    )
```

#### 步骤 3：添加 GET 端点示例

```python
@app.get("/api/avatar/{avatar_id}/mental_status")
async def get_mental_status(avatar_id: str):
    """
    获取角色的精神状态

    Args:
        avatar_id: 角色 ID

    Returns:
        精神力信息
    """
    world: World = game_instance.get("world")
    if not world:
        raise HTTPException(status_code=503, detail="Game not initialized")

    avatar = world.avatars.get(avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    return {
        "avatar_id": avatar_id,
        "avatar_name": avatar.name,
        "mental_power": avatar.mental_power,
        "max_mental_power": avatar.max_mental_power,
        "mental_power_percent": round(avatar.mental_power / avatar.max_mental_power * 100, 2)
    }
```

### 测试方法

#### 使用 curl 测试

```bash
# POST 请求
curl -X POST http://localhost:8002/api/action/meditate \
  -H "Content-Type: application/json" \
  -d '{"avatar_id": "some-uuid", "duration_hours": 3}'

# GET 请求
curl http://localhost:8002/api/avatar/some-uuid/mental_status
```

#### 使用 pytest 测试

```python
# tests/test_api_meditation.py
import pytest
from fastapi.testclient import TestClient
from src.server.main import app

client = TestClient(app)


def test_start_meditation_success(init_game):
    """测试成功开始冥想"""
    # 假设 init_game fixture 初始化了游戏
    avatar_id = "test-avatar-id"

    response = client.post("/api/action/meditate", json={
        "avatar_id": avatar_id,
        "duration_hours": 3
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_get_mental_status(init_game):
    """测试获取精神状态"""
    avatar_id = "test-avatar-id"

    response = client.get(f"/api/avatar/{avatar_id}/mental_status")

    assert response.status_code == 200
    data = response.json()
    assert "mental_power" in data
    assert "max_mental_power" in data
```

### 常见陷阱和注意事项

1. **游戏实例检查**：始终检查 `game_instance` 是否已初始化。

2. **错误处理**：使用 `HTTPException` 返回适当的 HTTP 状态码。

3. **类型安全**：使用 Pydantic 模型确保请求和响应的类型正确。

4. **CORS 配置**：如果前端在不同端口，确保 CORS 中间件已配置。

5. **异步函数**：API 路由应该是 `async def`，即使内部没有异步操作（为未来扩展留空间）。

6. **文档字符串**：添加详细的 docstring，FastAPI 会自动生成 OpenAPI 文档。

---

## 3. 如何添加新的游戏事件类型

### 任务描述
扩展事件系统，添加新的事件类型字段或修改事件生成逻辑。

### 涉及的文件
- 事件定义：`src/classes/event.py`
- 事件管理：`src/classes/event_manager.py`
- 事件存储：`src/classes/event_storage.py`

### 详细步骤

#### 步骤 1：修改 Event 数据类

编辑 `src/classes/event.py`，添加新字段：

```python
@dataclass
class Event:
    month_stamp: MonthStamp
    content: str
    related_avatars: Optional[List[str]] = None
    is_major: bool = False
    is_story: bool = False

    # 新增字段：事件分类
    category: str = "general"  # general, combat, cultivation, social, etc.

    # 新增字段：事件重要性（1-10）
    importance: int = 5

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """转换为可序列化的字典"""
        return {
            "month_stamp": int(self.month_stamp),
            "content": self.content,
            "related_avatars": self.related_avatars,
            "is_major": self.is_major,
            "is_story": self.is_story,
            "category": self.category,  # 新增
            "importance": self.importance,  # 新增
            "id": self.id,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        """从字典重建Event"""
        return cls(
            month_stamp=MonthStamp(data["month_stamp"]),
            content=data["content"],
            related_avatars=data.get("related_avatars"),
            is_major=data.get("is_major", False),
            is_story=data.get("is_story", False),
            category=data.get("category", "general"),  # 新增
            importance=data.get("importance", 5),  # 新增
            id=data.get("id", str(uuid.uuid4())),
            created_at=data.get("created_at", time.time())
        )
```

#### 步骤 2：更新数据库 Schema

编辑 `src/classes/event_storage.py`，更新 SQL 表定义：

```python
def _init_db(self) -> None:
    """初始化数据库表"""
    with self._conn:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                month_stamp INTEGER NOT NULL,
                content TEXT NOT NULL,
                related_avatars TEXT,
                is_major INTEGER DEFAULT 0,
                is_story INTEGER DEFAULT 0,
                category TEXT DEFAULT 'general',  -- 新增
                importance INTEGER DEFAULT 5,     -- 新增
                created_at REAL
            )
        """)

        # 创建索引
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_month_stamp
            ON events(month_stamp)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_category
            ON events(category)
        """)  # 新增索引
```

#### 步骤 3：添加数据库迁移脚本

创建 `src/classes/event_storage_migration.py`：

```python
"""
事件数据库迁移脚本
用于为现有数据库添加新字段
"""
from pathlib import Path
import sqlite3


def migrate_add_category_and_importance(db_path: Path) -> None:
    """
    迁移：添加 category 和 importance 字段

    Args:
        db_path: 数据库文件路径
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查字段是否已存在
    cursor.execute("PRAGMA table_info(events)")
    columns = [row[1] for row in cursor.fetchall()]

    try:
        # 添加 category 字段
        if "category" not in columns:
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN category TEXT DEFAULT 'general'
            """)
            print(f"Added 'category' column to {db_path}")

        # 添加 importance 字段
        if "importance" not in columns:
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN importance INTEGER DEFAULT 5
            """)
            print(f"Added 'importance' column to {db_path}")

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_category
            ON events(category)
        """)

        conn.commit()
        print(f"Migration completed for {db_path}")

    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # 示例：迁移所有存档的事件数据库
    from src.utils.config import CONFIG

    saves_dir = CONFIG.paths.saves
    for save_file in saves_dir.glob("*_events.db"):
        print(f"Migrating {save_file}...")
        migrate_add_category_and_importance(save_file)
```

#### 步骤 4：在动作中使用新字段

修改动作类以使用新的事件字段：

```python
# src/classes/action/breakthrough.py
async def finish(self) -> list[Event]:
    """突破完成"""
    if success:
        content = t("{avatar} successfully broke through to {realm}!",
                   avatar=self.avatar.name, realm=str(new_realm))
        event = Event(
            self.world.month_stamp,
            content,
            related_avatars=[self.avatar.id],
            is_major=True,
            category="cultivation",  # 新增
            importance=9  # 新增：突破是重要事件
        )
    else:
        content = t("{avatar} failed to break through",
                   avatar=self.avatar.name)
        event = Event(
            self.world.month_stamp,
            content,
            related_avatars=[self.avatar.id],
            category="cultivation",  # 新增
            importance=6  # 新增
        )
    return [event]
```

### 测试方法

```python
# tests/test_event_category.py
import pytest
from src.classes.event import Event
from src.classes.calendar import MonthStamp


def test_event_with_category():
    """测试带分类的事件"""
    event = Event(
        month_stamp=MonthStamp(100),
        content="测试事件",
        category="combat",
        importance=8
    )

    assert event.category == "combat"
    assert event.importance == 8


def test_event_to_dict_includes_new_fields():
    """测试序列化包含新字段"""
    event = Event(
        month_stamp=MonthStamp(100),
        content="测试事件",
        category="social",
        importance=7
    )

    data = event.to_dict()
    assert data["category"] == "social"
    assert data["importance"] == 7


def test_event_from_dict_with_new_fields():
    """测试反序列化包含新字段"""
    data = {
        "month_stamp": 100,
        "content": "测试事件",
        "category": "cultivation",
        "importance": 9,
        "id": "test-id",
        "created_at": 1234567890.0
    }

    event = Event.from_dict(data)
    assert event.category == "cultivation"
    assert event.importance == 9
```

### 常见陷阱和注意事项

1. **向后兼容性**：添加新字段时必须提供默认值，确保旧存档可以加载。

2. **数据库迁移**：修改数据库 schema 后，必须提供迁移脚本处理现有数据库。

3. **序列化/反序列化**：`to_dict()` 和 `from_dict()` 必须同步更新。

4. **索引优化**：如果新字段会被频繁查询，创建对应的数据库索引。

5. **测试覆盖**：确保新字段在所有事件创建路径中都被正确设置。

---

## 4. 如何添加新的 UI 面板

### 任务描述
创建一个新的 Vue 组件作为游戏 UI 面板。

### 涉及的文件
- 新建组件：`web/src/components/panels/MentalStatusPanel.vue`
- 主布局：`web/src/components/layout/MainLayout.vue`（可选）
- 状态管理：`web/src/stores/ui.ts`（可选）

### 详细步骤

#### 步骤 1：创建 Vue 组件

创建 `web/src/components/panels/MentalStatusPanel.vue`：

```vue
<script setup lang="ts">
/**
 * 精神状态面板
 *
 * 功能:
 * - 显示所有角色的精神力状态
 * - 支持筛选精神力低的角色
 * - 提供一键冥想功能
 *
 * Props:
 * - visible: 是否显示面板
 *
 * Emits:
 * - close: 关闭面板时触发
 */
import { ref, computed, watch } from 'vue'
import { useWorldStore } from '@/stores/world'
import { NCard, NProgress, NButton, NSwitch } from 'naive-ui'
import { useI18n } from 'vue-i18n'

interface Props {
  visible: boolean
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

const worldStore = useWorldStore()
const showLowMentalOnly = ref(false)

// 计算角色列表
const avatars = computed(() => {
  let list = worldStore.avatarList.filter(a => !a.is_dead)

  if (showLowMentalOnly.value) {
    list = list.filter(a => {
      const percent = (a.mental_power / a.max_mental_power) * 100
      return percent < 50
    })
  }

  return list.sort((a, b) => {
    const percentA = (a.mental_power / a.max_mental_power) * 100
    const percentB = (b.mental_power / b.max_mental_power) * 100
    return percentA - percentB
  })
})

// 开始冥想
async function startMeditation(avatarId: string) {
  try {
    const response = await fetch('/api/action/meditate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ avatar_id: avatarId, duration_hours: 3 })
    })

    const data = await response.json()
    if (data.success) {
      console.log('Meditation started')
    }
  } catch (error) {
    console.error('Failed to start meditation:', error)
  }
}

// 获取状态颜色
function getStatusColor(percent: number): string {
  if (percent < 30) return 'error'
  if (percent < 60) return 'warning'
  return 'success'
}
</script>

<template>
  <NCard
    v-if="visible"
    :title="t('ui.mental_status_panel.title')"
    class="mental-status-panel"
    closable
    @close="emit('close')"
  >
    <!-- 筛选控制 -->
    <div class="filter-controls">
      <NSwitch v-model:value="showLowMentalOnly">
        <template #checked>{{ t('ui.mental_status_panel.show_low_only') }}</template>
        <template #unchecked>{{ t('ui.mental_status_panel.show_all') }}</template>
      </NSwitch>
    </div>

    <!-- 角色列表 -->
    <div class="avatar-list">
      <div
        v-for="avatar in avatars"
        :key="avatar.id"
        class="avatar-item"
      >
        <div class="avatar-name">{{ avatar.name }}</div>

        <NProgress
          :percentage="(avatar.mental_power / avatar.max_mental_power) * 100"
          :status="getStatusColor((avatar.mental_power / avatar.max_mental_power) * 100)"
          :show-indicator="true"
        >
          <template #default="{ percentage }">
            {{ avatar.mental_power }} / {{ avatar.max_mental_power }}
          </template>
        </NProgress>

        <NButton
          size="small"
          @click="startMeditation(avatar.id)"
          :disabled="avatar.mental_power >= avatar.max_mental_power"
        >
          {{ t('ui.mental_status_panel.meditate') }}
        </NButton>
      </div>
    </div>
  </NCard>
</template>

<style scoped lang="scss">
.mental-status-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 500px;
  max-height: 600px;
  overflow-y: auto;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.filter-controls {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}

.avatar-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.avatar-item {
  display: grid;
  grid-template-columns: 120px 1fr 80px;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.02);

  &:hover {
    background: rgba(0, 0, 0, 0.05);
  }
}

.avatar-name {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
```

#### 步骤 2：添加多语言支持

编辑 `web/src/locales/zh-CN.json`：

```json
{
  "ui": {
    "mental_status_panel": {
      "title": "精神状态",
      "show_low_only": "仅显示低精神力",
      "show_all": "显示全部",
      "meditate": "冥想"
    }
  }
}
```

#### 步骤 3：集成到主界面

编辑 `web/src/components/layout/MainLayout.vue`：

```vue
<script setup lang="ts">
import { ref } from 'vue'
import MentalStatusPanel from '@/components/panels/MentalStatusPanel.vue'

const showMentalStatusPanel = ref(false)
</script>

<template>
  <div class="main-layout">
    <!-- 顶部菜单 -->
    <div class="top-bar">
      <button @click="showMentalStatusPanel = true">
        精神状态
      </button>
    </div>

    <!-- 其他面板 -->

    <!-- 精神状态面板 -->
    <MentalStatusPanel
      :visible="showMentalStatusPanel"
      @close="showMentalStatusPanel = false"
    />
  </div>
</template>
```

### 测试方法

#### 手动测试

1. 启动开发服务器：
```bash
cd web
npm run dev
```

2. 在浏览器中打开 `http://localhost:5173`

3. 点击"精神状态"按钮，验证面板显示

4. 测试交互功能：
   - 切换筛选开关
   - 点击冥想按钮
   - 关闭面板

#### 单元测试

创建 `web/src/__tests__/MentalStatusPanel.test.ts`：

```typescript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import MentalStatusPanel from '@/components/panels/MentalStatusPanel.vue'
import { createPinia, setActivePinia } from 'pinia'

describe('MentalStatusPanel', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders when visible', () => {
    const wrapper = mount(MentalStatusPanel, {
      props: { visible: true }
    })

    expect(wrapper.find('.mental-status-panel').exists()).toBe(true)
  })

  it('does not render when not visible', () => {
    const wrapper = mount(MentalStatusPanel, {
      props: { visible: false }
    })

    expect(wrapper.find('.mental-status-panel').exists()).toBe(false)
  })

  it('emits close event when close button clicked', async () => {
    const wrapper = mount(MentalStatusPanel, {
      props: { visible: true }
    })

    await wrapper.find('.n-card__close').trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
```

### 常见陷阱和注意事项

1. **Props 和 Emits 类型**：使用 TypeScript 接口定义，确保类型安全。

2. **响应式数据**：使用 `ref()` 或 `reactive()` 创建响应式数据。

3. **Computed 性能**：避免在 computed 中执行昂贵操作，考虑使用 `watchEffect` 或 缓存。

4. **API 调用**：始终处理错误情况，提供用户反馈。

5. **样式隔离**：使用 `scoped` 确保样式不污染其他组件。

6. **国际化**：所有用户可见文本都应该使用 `t()` 函数。

---

## 5. 如何修改 LLM 提示词

### 任务描述
修改发送给 LLM 的提示词模板，改变 AI 的决策行为。

### 涉及的文件
- 提示词模板：`templates/ai.txt`（或其他模板文件）
- 提示词构建：`src/utils/llm/prompt.py`
- AI 决策：`src/classes/ai.py`

### 详细步骤

#### 步骤 1：找到提示词模板文件

提示词模板通常在 `templates/` 目录下，使用 Jinja2 语法。

查看 `templates/ai.txt`：

```jinja2
你是一个修仙世界的角色 {{avatar_name}}。

## 角色信息
{{avatar_info}}

## 世界信息
{{world_info}}

## 可用动作
{{general_action_infos}}

## 任务
根据上述信息，决定 {{avatar_name}} 接下来要做什么。

请返回 JSON 格式：
{
  "{{avatar_name}}": {
    "action_name_params_pairs": [
      ["ActionName", {"param": "value"}]
    ],
    "avatar_thinking": "角色的思考过程",
    "short_term_objective": "短期目标"
  }
}
```

#### 步骤 2：修改提示词内容

例如，让 AI 更重视人际关系：

```jinja2
你是一个修仙世界的角色 {{avatar_name}}。

## 核心原则
1. **人际关系优先**：优先考虑与其他角色的互动和关系维护
2. **长远规划**：不要只追求短期修为提升
3. **性格一致**：行为应符合你的性格设定

## 角色信息
{{avatar_info}}

## 世界信息
{{world_info}}

## 可用动作
{{general_action_infos}}

## 决策步骤
1. 回顾最近的事件和人际关系
2. 评估当前的短期和长期目标
3. 考虑周围其他角色的动向
4. 选择最符合性格和目标的动作

## 任务
根据上述信息和原则，决定 {{avatar_name}} 接下来要做什么。

请返回 JSON 格式：
{
  "{{avatar_name}}": {
    "action_name_params_pairs": [
      ["ActionName", {"param": "value"}]
    ],
    "avatar_thinking": "详细的思考过程，包括对人际关系的考虑",
    "short_term_objective": "短期目标（1-3个月内）"
  }
}
```

#### 步骤 3：修改提示词构建逻辑（可选）

如果需要动态添加内容，编辑 `src/classes/ai.py`：

```python
async def _decide(self, world: World, avatars_to_decide: list[Avatar]) -> dict[Avatar, tuple[ACTION_NAME_PARAMS_PAIRS, str, str]]:
    """异步决策逻辑"""
    general_action_infos = ACTION_INFOS_STR

    async def decide_one(avatar: Avatar):
        world_info = world.get_info(avatar=avatar, detailed=True)
        observed = world.get_observable_avatars(avatar)
        avatar_info = avatar.get_expanded_info(co_region_avatars=observed)

        # 添加人际关系摘要
        relationship_summary = avatar.get_relationship_summary()

        # 添加最近的重要事件
        recent_events = world.event_manager.get_major_events_by_avatar(
            avatar.id,
            limit=5
        )
        recent_events_text = "\n".join([e.content for e in recent_events])

        info = {
            "avatar_name": avatar.name,
            "avatar_info": avatar_info,
            "world_info": world_info,
            "general_action_infos": general_action_infos,
            "relationship_summary": relationship_summary,  # 新增
            "recent_important_events": recent_events_text,  # 新增
        }

        template_path = CONFIG.paths.templates / "ai.txt"
        res = await call_llm_with_task_name("action_decision", template_path, info)
        return avatar, res

    # ... 其余代码
```

然后在模板中使用这些变量：

```jinja2
## 最近重要事件
{{recent_important_events}}

## 人际关系摘要
{{relationship_summary}}
```

#### 步骤 4：添加提示词版本控制

创建 `templates/ai_v2.txt` 作为新版本，在配置中选择使用：

```python
# src/classes/ai.py
async def decide_one(avatar: Avatar):
    # ...

    # 根据配置选择模板版本
    template_version = CONFIG.ai.get("prompt_version", "v1")
    template_path = CONFIG.paths.templates / f"ai_{template_version}.txt"

    if not template_path.exists():
        # 回退到默认版本
        template_path = CONFIG.paths.templates / "ai.txt"

    res = await call_llm_with_task_name("action_decision", template_path, info)
    return avatar, res
```

### 测试方法

#### A/B 测试

创建测试脚本比较不同提示词的效果：

```python
# scripts/test_prompts.py
import asyncio
from src.classes.ai import LLMAI
from src.classes.world import World

async def test_prompt_versions():
    """测试不同版本的提示词"""
    world = create_test_world()
    avatars = list(world.avatars.values())[:5]

    # 测试 v1
    CONFIG.ai.prompt_version = "v1"
    ai_v1 = LLMAI()
    results_v1 = await ai_v1.decide(world, avatars)

    # 测试 v2
    CONFIG.ai.prompt_version = "v2"
    ai_v2 = LLMAI()
    results_v2 = await ai_v2.decide(world, avatars)

    # 比较结果
    print("=== V1 Results ===")
    for avatar, (actions, thinking, objective, _) in results_v1.items():
        print(f"{avatar.name}: {actions}")
        print(f"Thinking: {thinking}")
        print()

    print("=== V2 Results ===")
    for avatar, (actions, thinking, objective, _) in results_v2.items():
        print(f"{avatar.name}: {actions}")
        print(f"Thinking: {thinking}")
        print()

if __name__ == "__main__":
    asyncio.run(test_prompt_versions())
```

#### 记录和分析

启用 LLM 调用日志：

```python
# src/run/log.py
def log_llm_call(model_name: str, prompt: str, response: str):
    """记录 LLM 调用"""
    log_dir = Path("logs/llm_calls")
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{timestamp}_{model_name}.json"

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump({
            "model": model_name,
            "prompt": prompt,
            "response": response,
            "timestamp": timestamp
        }, f, ensure_ascii=False, indent=2)
```

然后分析日志，评估提示词效果。

### 常见陷阱和注意事项

1. **上下文长度限制**：提示词不能过长，注意 LLM 的 token 限制。

2. **JSON 格式要求**：提示词中的 JSON 示例必须准确，否则 LLM 容易返回错误格式。

3. **变量注入安全**：避免用户输入直接注入提示词，防止提示词注入攻击。

4. **版本兼容性**：修改提示词可能影响所有使用该模板的功能，充分测试。

5. **性能影响**：更长的提示词会增加 API 调用成本和延迟。

6. **模板缓存**：Jinja2 模板会被缓存，修改后需要重启服务器。

---

## 6. 如何添加新的修仙境界

### 任务描述
扩展修仙境界体系，添加更高级的境界（如化神期、合体期）。

### 涉及的文件
- 境界定义：`src/classes/cultivation.py`
- 配置文件：`static/default_config.yml`、`static/game_config.yml`

### 详细步骤

#### 步骤 1：修改 Realm 枚举

编辑 `src/classes/cultivation.py`：

```python
from enum import Enum
from functools import total_ordering

@total_ordering
class Realm(Enum):
    Qi_Refinement = "QI_REFINEMENT"                    # 练气
    Foundation_Establishment = "FOUNDATION_ESTABLISHMENT"  # 筑基
    Core_Formation = "CORE_FORMATION"                  # 金丹
    Nascent_Soul = "NASCENT_SOUL"                      # 元婴
    Spirit_Severing = "SPIRIT_SEVERING"                # 化神（新增）
    Void_Integration = "VOID_INTEGRATION"              # 合体（新增）
    Mahayana = "MAHAYANA"                              # 大乘（新增）

    def __str__(self) -> str:
        """返回境界的翻译名称"""
        from src.i18n import t
        return t(realm_msg_ids.get(self, self.value))

    @property
    def color_rgb(self) -> tuple[int, int, int]:
        """返回境界对应的RGB颜色值"""
        color_map = {
            Realm.Qi_Refinement: Color.COMMON_WHITE,
            Realm.Foundation_Establishment: Color.UNCOMMON_GREEN,
            Realm.Core_Formation: Color.EPIC_PURPLE,
            Realm.Nascent_Soul: Color.LEGENDARY_GOLD,
            Realm.Spirit_Severing: Color.MYTHIC_RED,        # 新增
            Realm.Void_Integration: Color.DIVINE_CYAN,      # 新增
            Realm.Mahayana: Color.TRANSCENDENT_RAINBOW,     # 新增
        }
        return color_map.get(self, Color.COMMON_WHITE)

# 境界顺序（用于比较）
REALM_ORDER = [
    Realm.Qi_Refinement,
    Realm.Foundation_Establishment,
    Realm.Core_Formation,
    Realm.Nascent_Soul,
    Realm.Spirit_Severing,      # 新增
    Realm.Void_Integration,      # 新增
    Realm.Mahayana,              # 新增
]

# 境界排名（用于 __lt__ 等比较）
REALM_RANK = {realm: i for i, realm in enumerate(REALM_ORDER)}

# 国际化 ID 映射
realm_msg_ids = {
    Realm.Qi_Refinement: "realm_qi_refinement",
    Realm.Foundation_Establishment: "realm_foundation_establishment",
    Realm.Core_Formation: "realm_core_formation",
    Realm.Nascent_Soul: "realm_nascent_soul",
    Realm.Spirit_Severing: "realm_spirit_severing",      # 新增
    Realm.Void_Integration: "realm_void_integration",    # 新增
    Realm.Mahayana: "realm_mahayana",                    # 新增
}
```

#### 步骤 2：添加颜色定义（如果需要新颜色）

编辑 `src/classes/color.py`：

```python
class Color:
    COMMON_WHITE = (255, 255, 255)
    UNCOMMON_GREEN = (0, 255, 0)
    EPIC_PURPLE = (160, 32, 240)
    LEGENDARY_GOLD = (255, 215, 0)
    MYTHIC_RED = (220, 20, 60)         # 新增
    DIVINE_CYAN = (0, 255, 255)        # 新增
    TRANSCENDENT_RAINBOW = (255, 105, 180)  # 新增（示例，实际可能需要渐变效果）
```

#### 步骤 3：添加多语言翻译

编辑 `.po` 文件：

```po
msgid "realm_spirit_severing"
msgstr "化神期"

msgid "realm_void_integration"
msgstr "合体期"

msgid "realm_mahayana"
msgstr "大乘期"
```

#### 步骤 4：调整突破难度和寿元配置

编辑 `static/game_config.yml`：

```yaml
cultivation:
  # 境界突破难度（成功率百分比）
  breakthrough_difficulty:
    QI_REFINEMENT: 90
    FOUNDATION_ESTABLISHMENT: 70
    CORE_FORMATION: 50
    NASCENT_SOUL: 30
    SPIRIT_SEVERING: 15       # 新增
    VOID_INTEGRATION: 8       # 新增
    MAHAYANA: 3               # 新增

  # 境界对应寿元增加
  lifespan_bonus:
    QI_REFINEMENT: 50
    FOUNDATION_ESTABLISHMENT: 100
    CORE_FORMATION: 300
    NASCENT_SOUL: 800
    SPIRIT_SEVERING: 2000     # 新增
    VOID_INTEGRATION: 5000    # 新增
    MAHAYANA: 10000           # 新增

  # 境界修炼速度倍率
  cultivation_speed_multiplier:
    QI_REFINEMENT: 1.0
    FOUNDATION_ESTABLISHMENT: 0.8
    CORE_FORMATION: 0.6
    NASCENT_SOUL: 0.4
    SPIRIT_SEVERING: 0.2      # 新增
    VOID_INTEGRATION: 0.1     # 新增
    MAHAYANA: 0.05            # 新增
```

#### 步骤 5：更新突破逻辑（如果需要特殊机制）

编辑 `src/classes/action/breakthrough.py`：

```python
async def finish(self) -> list[Event]:
    """突破完成"""
    current_realm = self.avatar.cultivation_progress.realm

    # 化神期及以上需要特殊条件
    if current_realm >= Realm.Nascent_Soul:
        # 检查是否有足够的感悟
        if not self._check_enlightenment():
            content = t("{avatar} lacks sufficient enlightenment for breakthrough",
                       avatar=self.avatar.name)
            event = Event(
                self.world.month_stamp,
                content,
                related_avatars=[self.avatar.id],
                is_major=True
            )
            return [event]

    # ... 原有的突破逻辑
```

#### 步骤 6：更新前端显示

编辑 `web/src/types/cultivation.ts`：

```typescript
export enum CultivationRealm {
  QI_REFINEMENT = "练气期",
  FOUNDATION_ESTABLISHMENT = "筑基期",
  CORE_FORMATION = "金丹期",
  NASCENT_SOUL = "元婴期",
  SPIRIT_SEVERING = "化神期",      // 新增
  VOID_INTEGRATION = "合体期",      // 新增
  MAHAYANA = "大乘期",              // 新增
}

// 境界颜色映射
export const REALM_COLORS: Record<CultivationRealm, string> = {
  [CultivationRealm.QI_REFINEMENT]: '#ffffff',
  [CultivationRealm.FOUNDATION_ESTABLISHMENT]: '#00ff00',
  [CultivationRealm.CORE_FORMATION]: '#a020f0',
  [CultivationRealm.NASCENT_SOUL]: '#ffd700',
  [CultivationRealm.SPIRIT_SEVERING]: '#dc143c',       // 新增
  [CultivationRealm.VOID_INTEGRATION]: '#00ffff',      // 新增
  [CultivationRealm.MAHAYANA]: '#ff69b4',              // 新增
}
```

### 测试方法

#### 创建测试用例

```python
# tests/test_new_realms.py
import pytest
from src.classes.cultivation import Realm, REALM_ORDER


def test_new_realms_in_order():
    """测试新境界在顺序中"""
    assert Realm.Spirit_Severing in REALM_ORDER
    assert Realm.Void_Integration in REALM_ORDER
    assert Realm.Mahayana in REALM_ORDER


def test_realm_comparison():
    """测试境界比较"""
    assert Realm.Spirit_Severing > Realm.Nascent_Soul
    assert Realm.Void_Integration > Realm.Spirit_Severing
    assert Realm.Mahayana > Realm.Void_Integration


def test_realm_color():
    """测试境界颜色"""
    assert Realm.Spirit_Severing.color_rgb is not None
    assert len(Realm.Spirit_Severing.color_rgb) == 3


def test_breakthrough_to_spirit_severing(dummy_avatar):
    """测试突破到化神期"""
    from src.classes.action.breakthrough import Breakthrough

    # 设置角色到元婴期巅峰
    dummy_avatar.cultivation_progress.realm = Realm.Nascent_Soul
    dummy_avatar.cultivation_progress.level = 30
    dummy_avatar.cultivation_progress.exp = 999999

    action = Breakthrough(dummy_avatar, dummy_avatar.world)
    # ... 测试突破逻辑
```

#### 游戏内测试

1. 启动游戏，创建测试角色
2. 使用控制台命令快速提升境界：
```python
# 在游戏控制台或测试脚本中
avatar.cultivation_progress.set_realm(Realm.Spirit_Severing)
```
3. 验证显示和功能正常

### 常见陷阱和注意事项

1. **枚举顺序**：必须更新 `REALM_ORDER` 和 `REALM_RANK`，否则比较会出错。

2. **配置同步**：所有相关配置项都要添加新境界的设置。

3. **向后兼容性**：旧存档中的角色不会自动更新，考虑迁移脚本。

4. **平衡性**：新境界的参数需要仔细调整，避免破坏游戏平衡。

5. **前后端一致**：前端的枚举定义必须与后端保持一致。

6. **翻译完整性**：确保所有支持的语言都添加了翻译。

---

## 7. 如何添加新的宗门

### 任务描述
向游戏中添加新的宗门，包括名称、描述、特色等。

### 涉及的文件
- 宗门数据：CSV 文件（根据语言版本）
  - `static/zh-CN/sects.csv`（中文）
  - `static/en-US/sects.csv`（英文）
  - `static/zh-TW/sects.csv`（繁体中文）
- 宗门类：`src/classes/sect.py`

### 详细步骤

#### 步骤 1：查看现有 CSV 格式

查看 `static/zh-CN/sects.csv`（如果不存在该路径，查找类似的数据文件）：

```csv
id,name,desc,alignment,specialty
1,青云门,正道大宗，以剑修闻名,righteous,sword
2,合欢宗,魔道宗门，修炼双修功法,demonic,dual_cultivation
3,百兽宗,中立宗门，擅长驯养妖兽,neutral,beast_taming
4,天机阁,正道宗门，精通炼丹炼器,righteous,crafting
```

#### 步骤 2：添加新宗门数据

编辑 CSV 文件，添加新行：

```csv
id,name,desc,alignment,specialty
1,青云门,正道大宗，以剑修闻名,righteous,sword
2,合欢宗,魔道宗门，修炼双修功法,demonic,dual_cultivation
3,百兽宗,中立宗门，擅长驯养妖兽,neutral,beast_taming
4,天机阁,正道宗门，精通炼丹炼器,righteous,crafting
5,万毒窟,魔道宗门，善用毒术与蛊虫,demonic,poison
6,星辰阁,正道宗门，观星悟道，精通阵法,righteous,formation
```

字段说明：
- `id`：唯一标识符（整数）
- `name`：宗门名称
- `desc`：宗门描述
- `alignment`：阵营（`righteous`/`demonic`/`neutral`）
- `specialty`：特长（自定义字符串）

#### 步骤 3：为其他语言添加翻译

编辑 `static/en-US/sects.csv`：

```csv
id,name,desc,alignment,specialty
5,Ten Thousand Poison Cave,A demonic sect skilled in poison and venomous insects,demonic,poison
6,Star Pavilion,A righteous sect that comprehends the Dao through stargazing and masters formations,righteous,formation
```

编辑 `static/zh-TW/sects.csv`：

```csv
id,name,desc,alignment,specialty
5,萬毒窟,魔道宗門，善用毒術與蠱蟲,demonic,poison
6,星辰閣,正道宗門，觀星悟道，精通陣法,righteous,formation
```

#### 步骤 4：配置宗门特殊能力（可选）

如果新宗门有特殊机制，编辑 `src/classes/sect.py`：

```python
class Sect:
    """宗门类"""

    def __init__(self, id: int, name: str, desc: str, alignment: str, specialty: str):
        self.id = id
        self.name = name
        self.desc = desc
        self.alignment = alignment
        self.specialty = specialty

    def get_cultivation_bonus(self, avatar: Avatar) -> float:
        """获取修炼加成"""
        bonuses = {
            "sword": 1.2,           # 剑修：修炼速度 +20%
            "dual_cultivation": 1.5,  # 双修：修炼速度 +50%
            "beast_taming": 1.1,    # 御兽：修炼速度 +10%
            "crafting": 1.0,        # 炼制：无修炼加成
            "poison": 1.15,         # 毒术：修炼速度 +15%（新增）
            "formation": 1.25,      # 阵法：修炼速度 +25%（新增）
        }
        return bonuses.get(self.specialty, 1.0)

    def get_special_actions(self) -> list[str]:
        """获取宗门特殊动作"""
        special_actions = {
            "poison": ["RefinePoisonAction", "PlantVenomousInsectAction"],  # 新增
            "formation": ["SetupFormationAction", "BreakFormationAction"],  # 新增
        }
        return special_actions.get(self.specialty, [])
```

#### 步骤 5：更新配置文件（指定初始宗门）

编辑 `static/game_config.yml`：

```yaml
game:
  sect_num: 6  # 增加宗门数量

  # 指定初始化时使用的宗门 ID（可选）
  initial_sects:
    - 1  # 青云门
    - 2  # 合欢宗
    - 3  # 百兽宗
    - 4  # 天机阁
    - 5  # 万毒窟（新增）
    - 6  # 星辰阁（新增）
```

#### 步骤 6：重启游戏加载数据

CSV 文件在服务器启动时加载，修改后需要重启：

```bash
# 停止服务器（Ctrl+C）
# 重新启动
python src/server/main.py
```

### 测试方法

#### 验证宗门加载

```python
# tests/test_new_sects.py
import pytest
from src.classes.sect import sects_by_id


def test_new_sects_loaded():
    """测试新宗门是否加载"""
    assert 5 in sects_by_id
    assert 6 in sects_by_id

    poison_sect = sects_by_id[5]
    assert poison_sect.name == "万毒窟"
    assert poison_sect.specialty == "poison"

    star_sect = sects_by_id[6]
    assert star_sect.name == "星辰阁"
    assert star_sect.specialty == "formation"


def test_sect_bonuses():
    """测试宗门加成"""
    poison_sect = sects_by_id[5]
    star_sect = sects_by_id[6]

    # 创建测试角色
    avatar = create_test_avatar()

    # 测试毒术宗门加成
    avatar.sect = poison_sect
    assert poison_sect.get_cultivation_bonus(avatar) == 1.15

    # 测试阵法宗门加成
    avatar.sect = star_sect
    assert star_sect.get_cultivation_bonus(avatar) == 1.25
```

#### 游戏内验证

1. 启动新游戏
2. 查看宗门列表，确认新宗门出现
3. 创建角色并加入新宗门
4. 验证特殊能力生效

### 常见陷阱和注意事项

1. **ID 唯一性**：宗门 ID 必须唯一，不能与现有宗门冲突。

2. **CSV 编码**：确保 CSV 文件使用 UTF-8 编码，避免中文乱码。

3. **逗号转义**：如果描述中有逗号，需要用引号包裹：
   ```csv
   5,"万毒窟","魔道宗门，善用毒术与蛊蟲",demonic,poison
   ```

4. **重启服务器**：CSV 修改不会热重载，必须重启。

5. **多语言一致性**：所有语言的 CSV 文件必须有相同的宗门 ID。

6. **阵营平衡**：添加新宗门时注意正邪平衡，避免阵营失衡。

---

## 8. 如何扩展存档格式

### 任务描述
添加新的数据字段到存档系统，并确保新旧存档兼容。

### 涉及的文件
- 存档保存：`src/sim/save/save_game.py`
- 存档加载：`src/sim/load/load_game.py`
- 角色序列化：`src/classes/avatar/avatar.py`（`to_save_dict`、`from_save_dict` 方法）

### 详细步骤

#### 步骤 1：添加新字段到数据类

假设要给 Avatar 添加"功德值"字段。

编辑 `src/classes/avatar/avatar.py`：

```python
class Avatar:
    """角色类"""

    def __init__(self, ...):
        # ... 现有字段 ...

        # 新增字段：功德值
        self.karma: int = 0  # 功德值，正数为善，负数为恶

    def to_save_dict(self) -> dict:
        """序列化为字典（用于存档）"""
        data = {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            # ... 其他现有字段 ...

            # 新增字段
            "karma": self.karma,
        }
        return data

    @classmethod
    def from_save_dict(cls, data: dict, world: World) -> "Avatar":
        """从字典重建对象（加载存档）"""
        avatar = cls(
            id=data["id"],
            name=data["name"],
            age=data["age"],
            # ... 其他现有字段 ...
        )

        # 新增字段（提供默认值以兼容旧存档）
        avatar.karma = data.get("karma", 0)

        return avatar
```

#### 步骤 2：更新存档版本号

编辑 `src/utils/config.py` 或配置文件：

```yaml
# static/default_config.yml
meta:
  version: "0.2.0"  # 从 0.1.0 升级到 0.2.0
  save_format_version: 2  # 存档格式版本
```

编辑 `src/sim/save/save_game.py`：

```python
def save_game(world: World, simulator: Simulator, existed_sects: List[Sect], save_path: Optional[Path] = None) -> tuple[bool, Optional[str]]:
    """保存游戏"""
    # ...

    meta = {
        "version": CONFIG.meta.version,
        "save_format_version": 2,  # 新版本
        "saved_at": datetime.now().isoformat(),
        # ...
    }

    # ...
```

#### 步骤 3：编写迁移函数

创建 `src/sim/load/migrations.py`：

```python
"""
存档迁移脚本
用于升级旧版本存档到新格式
"""
from typing import Any


def migrate_v1_to_v2(save_data: dict) -> dict:
    """
    从版本 1 迁移到版本 2

    变更：
    - Avatar 添加 karma 字段
    """
    print("Migrating save from v1 to v2...")

    # 更新元数据
    save_data["meta"]["save_format_version"] = 2

    # 为所有角色添加 karma 字段
    for avatar_data in save_data.get("avatars", []):
        if "karma" not in avatar_data:
            avatar_data["karma"] = 0  # 默认值
            print(f"  Added karma field to avatar {avatar_data.get('name', 'Unknown')}")

    print("Migration v1->v2 complete")
    return save_data


# 迁移链
MIGRATIONS = {
    1: migrate_v1_to_v2,
    # 未来可以添加更多：
    # 2: migrate_v2_to_v3,
    # 3: migrate_v3_to_v4,
}


def apply_migrations(save_data: dict) -> dict:
    """
    应用所有必要的迁移

    Args:
        save_data: 原始存档数据

    Returns:
        迁移后的存档数据
    """
    current_version = save_data.get("meta", {}).get("save_format_version", 1)
    target_version = max(MIGRATIONS.keys()) + 1  # 最新版本

    if current_version >= target_version:
        print(f"Save is already at version {current_version}, no migration needed")
        return save_data

    print(f"Migrating save from version {current_version} to {target_version}")

    # 依次应用迁移
    for version in range(current_version, target_version):
        if version in MIGRATIONS:
            save_data = MIGRATIONS[version](save_data)

    return save_data
```

#### 步骤 4：在加载时应用迁移

编辑 `src/sim/load/load_game.py`：

```python
from src.sim.load.migrations import apply_migrations


def load_game(save_path: Path) -> tuple[World, Simulator, List[Sect]]:
    """加载游戏存档"""
    with open(save_path, 'r', encoding='utf-8') as f:
        save_data = json.load(f)

    # 应用迁移
    save_data = apply_migrations(save_data)

    # 加载世界
    world = World.from_save_dict(save_data["world"])

    # 加载角色
    for avatar_data in save_data["avatars"]:
        avatar = Avatar.from_save_dict(avatar_data, world)
        world.add_avatar(avatar)

    # ...

    return world, simulator, existed_sects
```

#### 步骤 5：添加版本检查和警告

```python
def load_game(save_path: Path) -> tuple[World, Simulator, List[Sect]]:
    """加载游戏存档"""
    with open(save_path, 'r', encoding='utf-8') as f:
        save_data = json.load(f)

    # 检查版本
    save_version = save_data.get("meta", {}).get("version", "unknown")
    save_format = save_data.get("meta", {}).get("save_format_version", 1)
    current_version = CONFIG.meta.version

    print(f"Loading save: version {save_version}, format {save_format}")
    print(f"Current game version: {current_version}")

    # 警告：跨大版本加载
    if save_version.split('.')[0] != current_version.split('.')[0]:
        print("⚠️  WARNING: Loading save from different major version, may have compatibility issues")

    # 应用迁移
    save_data = apply_migrations(save_data)

    # ...
```

### 测试方法

#### 创建测试存档

```python
# tests/test_save_migration.py
import pytest
import json
from pathlib import Path
from src.sim.load.migrations import apply_migrations


@pytest.fixture
def v1_save_data():
    """模拟 v1 格式的存档数据"""
    return {
        "meta": {
            "version": "0.1.0",
            "save_format_version": 1,
            "saved_at": "2025-01-01T00:00:00"
        },
        "avatars": [
            {
                "id": "test-id-1",
                "name": "张三",
                "age": 25,
                # 注意：没有 karma 字段
            }
        ]
    }


def test_migration_v1_to_v2(v1_save_data):
    """测试 v1 到 v2 的迁移"""
    migrated = apply_migrations(v1_save_data)

    # 验证版本号更新
    assert migrated["meta"]["save_format_version"] == 2

    # 验证新字段被添加
    assert "karma" in migrated["avatars"][0]
    assert migrated["avatars"][0]["karma"] == 0


def test_load_old_save(v1_save_data, tmp_path):
    """测试加载旧版本存档"""
    # 创建临时存档文件
    save_file = tmp_path / "test_save.json"
    with open(save_file, 'w', encoding='utf-8') as f:
        json.dump(v1_save_data, f)

    # 加载存档
    world, simulator, sects = load_game(save_file)

    # 验证角色有 karma 字段
    avatar = list(world.avatars.values())[0]
    assert hasattr(avatar, 'karma')
    assert avatar.karma == 0
```

### 常见陷阱和注意事项

1. **默认值**：新字段必须有合理的默认值，确保旧存档加载后功能正常。

2. **向后兼容**：
   - 使用 `data.get("new_field", default_value)` 而不是 `data["new_field"]`
   - 不要删除旧字段，除非有充分理由

3. **迁移顺序**：迁移函数必须按版本顺序应用。

4. **测试覆盖**：为每个迁移版本创建测试用例。

5. **备份提醒**：在应用迁移前提醒用户备份存档。

6. **数据库迁移**：如果使用 SQLite 存储事件，也需要编写数据库迁移脚本（见第3节）。

---

## 9. 如何添加新的测试用例

### 任务描述
为新功能或现有功能编写单元测试，确保代码质量。

### 涉及的文件
- 测试文件：`tests/test_*.py`
- 测试配置：`tests/conftest.py`
- pytest 配置：`pytest.ini` 或 `pyproject.toml`

### 详细步骤

#### 步骤 1：理解项目测试结构

```
tests/
├── conftest.py           # pytest fixtures（共享测试夹具）
├── test_avatar.py        # Avatar 类测试
├── test_cultivation.py   # 修炼系统测试
├── test_action_*.py      # 各种动作测试
└── ...
```

#### 步骤 2：查看可用的 Fixtures

编辑 `tests/conftest.py`，查看或添加 fixtures：

```python
import pytest
from src.classes.avatar import Avatar
from src.classes.world import World
from src.classes.map import Map


@pytest.fixture
def dummy_world():
    """创建测试用的世界"""
    world = World(
        year=100,
        month=1,
        map=Map.create_test_map()
    )
    return world


@pytest.fixture
def dummy_avatar(dummy_world):
    """创建测试用的角色"""
    avatar = Avatar(
        id="test-avatar-001",
        name="测试角色",
        age=20,
        world=dummy_world
    )
    dummy_world.add_avatar(avatar)
    return avatar


@pytest.fixture
def init_game():
    """初始化完整的游戏环境（用于集成测试）"""
    from src.server.main import game_instance
    from src.sim.simulator import Simulator

    world = World.create_test_world()
    simulator = Simulator(world)

    game_instance["world"] = world
    game_instance["sim"] = simulator

    yield game_instance

    # 清理
    game_instance["world"] = None
    game_instance["sim"] = None
```

#### 步骤 3：编写单元测试

创建 `tests/test_karma_system.py`：

```python
"""
功德系统测试
"""
import pytest
from src.classes.avatar import Avatar


class TestKarmaSystem:
    """测试功德系统"""

    def test_initial_karma_is_zero(self, dummy_avatar):
        """测试初始功德值为 0"""
        assert dummy_avatar.karma == 0

    def test_good_deed_increases_karma(self, dummy_avatar):
        """测试善行增加功德"""
        from src.classes.action.help_mortals import HelpMortals

        action = HelpMortals(dummy_avatar, dummy_avatar.world)
        action.execute()

        assert dummy_avatar.karma > 0

    def test_evil_deed_decreases_karma(self, dummy_avatar):
        """测试恶行减少功德"""
        from src.classes.action.devour_mortals import DevourMortals

        action = DevourMortals(dummy_avatar, dummy_avatar.world)
        action.execute()

        assert dummy_avatar.karma < 0

    @pytest.mark.parametrize("karma_value,expected_title", [
        (1000, "大善人"),
        (100, "善人"),
        (0, "凡人"),
        (-100, "恶人"),
        (-1000, "大魔头"),
    ])
    def test_karma_title(self, dummy_avatar, karma_value, expected_title):
        """测试功德称号（参数化测试）"""
        dummy_avatar.karma = karma_value
        assert dummy_avatar.get_karma_title() == expected_title

    def test_karma_affects_tribulation_difficulty(self, dummy_avatar):
        """测试功德影响天劫难度"""
        from src.classes.action.breakthrough import Breakthrough

        # 高功德降低难度
        dummy_avatar.karma = 1000
        action = Breakthrough(dummy_avatar, dummy_avatar.world)
        difficulty_good = action.calculate_tribulation_difficulty()

        # 低功德增加难度
        dummy_avatar.karma = -1000
        difficulty_evil = action.calculate_tribulation_difficulty()

        assert difficulty_good < difficulty_evil


class TestKarmaSaveLoad:
    """测试功德的存档和加载"""

    def test_save_karma(self, dummy_avatar):
        """测试保存功德值"""
        dummy_avatar.karma = 500
        save_data = dummy_avatar.to_save_dict()

        assert "karma" in save_data
        assert save_data["karma"] == 500

    def test_load_karma(self, dummy_world):
        """测试加载功德值"""
        save_data = {
            "id": "test-id",
            "name": "测试",
            "age": 20,
            "karma": 300,
            # ... 其他必要字段
        }

        avatar = Avatar.from_save_dict(save_data, dummy_world)
        assert avatar.karma == 300

    def test_load_old_save_without_karma(self, dummy_world):
        """测试加载没有功德字段的旧存档"""
        save_data = {
            "id": "test-id",
            "name": "测试",
            "age": 20,
            # 注意：没有 karma 字段
        }

        avatar = Avatar.from_save_dict(save_data, dummy_world)
        assert avatar.karma == 0  # 应该有默认值
```

#### 步骤 4：编写集成测试

```python
# tests/test_karma_integration.py
import pytest
from src.sim.simulator import Simulator


@pytest.mark.integration
class TestKarmaIntegration:
    """功德系统集成测试"""

    def test_karma_affects_sect_reputation(self, init_game):
        """测试功德影响宗门声望"""
        world = init_game["world"]
        avatar = list(world.avatars.values())[0]

        # 设置高功德
        avatar.karma = 1000

        # 加入正道宗门
        righteous_sect = [s for s in world.sects if s.alignment == "righteous"][0]
        avatar.join_sect(righteous_sect)

        # 验证获得额外声望
        assert avatar.sect_reputation > 0

    @pytest.mark.asyncio
    async def test_karma_affects_npc_reactions(self, init_game):
        """测试功德影响 NPC 反应"""
        world = init_game["world"]
        simulator = init_game["sim"]

        evil_avatar = list(world.avatars.values())[0]
        evil_avatar.karma = -1000

        # 推进游戏，看其他 NPC 是否回避
        await simulator.step()

        # 验证其他 NPC 倾向于远离恶人
        nearby_avatars = world.get_avatars_in_range(
            evil_avatar.pos_x,
            evil_avatar.pos_y,
            radius=5
        )

        assert len(nearby_avatars) < 3  # 预期较少 NPC 靠近恶人
```

#### 步骤 5：运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_karma_system.py

# 运行特定类
pytest tests/test_karma_system.py::TestKarmaSystem

# 运行特定测试
pytest tests/test_karma_system.py::TestKarmaSystem::test_good_deed_increases_karma

# 显示详细输出
pytest -v

# 显示打印语句
pytest -s

# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 只运行集成测试
pytest -m integration

# 跳过集成测试
pytest -m "not integration"
```

### 测试最佳实践

#### 1. 测试命名规范

```python
# ✅ 好的命名
def test_karma_increases_when_helping_mortals()
def test_load_save_without_karma_field_uses_default()

# ❌ 不好的命名
def test_1()
def test_karma()
```

#### 2. 使用 AAA 模式（Arrange-Act-Assert）

```python
def test_karma_title():
    # Arrange（准备）
    avatar = create_test_avatar()
    avatar.karma = 1000

    # Act（执行）
    title = avatar.get_karma_title()

    # Assert（断言）
    assert title == "大善人"
```

#### 3. 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    (0, "凡人"),
    (100, "善人"),
    (-100, "恶人"),
])
def test_titles(input, expected, dummy_avatar):
    dummy_avatar.karma = input
    assert dummy_avatar.get_karma_title() == expected
```

#### 4. 使用 Mock 隔离外部依赖

```python
from unittest.mock import Mock, patch

def test_karma_event_with_llm(dummy_avatar):
    """测试功德事件（模拟 LLM 调用）"""
    with patch('src.utils.llm.call_llm') as mock_llm:
        mock_llm.return_value = '{"action": "help", "target": "mortal"}'

        # 执行测试
        result = dummy_avatar.decide_action()

        # 验证 LLM 被调用
        assert mock_llm.called
```

### 常见陷阱和注意事项

1. **测试隔离**：每个测试应该独立，不依赖其他测试的执行顺序。

2. **Fixture 作用域**：理解 `function`、`class`、`module`、`session` 作用域。

3. **异步测试**：使用 `@pytest.mark.asyncio` 标记异步测试。

4. **数据库清理**：测试数据库应该在测试后清理，避免污染。

5. **性能测试**：集成测试可能很慢，使用 `-m` 标记区分快速测试和慢速测试。

6. **CI/CD 集成**：确保测试在 CI 环境中也能通过。

---

## 10. 如何调试 WebSocket 通信

### 任务描述
调试前后端之间的 WebSocket 实时通信问题。

### 涉及的工具和文件
- 后端 WebSocket：`src/server/main.py`（`/ws` 端点）
- 前端连接：`web/src/stores/websocket.ts` 或类似文件
- 浏览器开发者工具

### 详细步骤

#### 步骤 1：检查后端 WebSocket 端点

查看 `src/server/main.py` 中的 WebSocket 处理：

```python
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """广播消息到所有连接"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Failed to send to connection: {e}")
                disconnected.append(connection)

        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点"""
    await manager.connect(websocket)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            print(f"📨 Received from client: {data}")

            # 处理消息
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
```

#### 步骤 2：添加详细日志

增强日志输出以便调试：

```python
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点（带详细日志）"""
    client_id = id(websocket)
    logger.info(f"[WS-{client_id}] Connection attempt")

    await manager.connect(websocket)
    logger.info(f"[WS-{client_id}] Connected successfully")

    try:
        while True:
            data = await websocket.receive_json()
            logger.debug(f"[WS-{client_id}] Received: {data}")

            # 处理消息
            response = handle_ws_message(data)

            if response:
                await websocket.send_json(response)
                logger.debug(f"[WS-{client_id}] Sent: {response}")

    except WebSocketDisconnect:
        logger.info(f"[WS-{client_id}] Client disconnected normally")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"[WS-{client_id}] Error: {e}", exc_info=True)
        manager.disconnect(websocket)
```

#### 步骤 3：使用浏览器开发者工具

##### Chrome/Edge DevTools

1. 打开开发者工具（F12）
2. 切换到 **Network** 标签
3. 筛选 `WS`（WebSocket）
4. 刷新页面，查看 WebSocket 连接
5. 点击连接，查看 **Messages** 标签

**查看消息**：
```
↑ {"type": "subscribe", "channel": "game_events"}
↓ {"type": "tick", "year": 100, "month": 1, "events": [...]}
```

##### 使用 Console 测试

在浏览器控制台手动建立 WebSocket 连接：

```javascript
// 建立连接
const ws = new WebSocket('ws://localhost:8002/ws')

// 监听打开事件
ws.onopen = () => {
  console.log('✅ WebSocket connected')
  ws.send(JSON.stringify({ type: 'ping' }))
}

// 监听消息
ws.onmessage = (event) => {
  console.log('📨 Received:', JSON.parse(event.data))
}

// 监听错误
ws.onerror = (error) => {
  console.error('❌ WebSocket error:', error)
}

// 监听关闭
ws.onclose = () => {
  console.log('❌ WebSocket closed')
}

// 发送测试消息
ws.send(JSON.stringify({ type: 'test', data: 'hello' }))

// 关闭连接
ws.close()
```

#### 步骤 4：检查前端 WebSocket 实现

查看前端连接代码（假设在 Pinia store 中）：

```typescript
// web/src/stores/websocket.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWebSocketStore = defineStore('websocket', () => {
  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5

  function connect() {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8002/ws'

    console.log(`🔌 Connecting to ${wsUrl}...`)
    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      console.log('✅ WebSocket connected')
      connected.value = true
      reconnectAttempts.value = 0
    }

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('📨 Received:', data)
        handleMessage(data)
      } catch (error) {
        console.error('Failed to parse message:', error)
      }
    }

    ws.value.onerror = (error) => {
      console.error('❌ WebSocket error:', error)
    }

    ws.value.onclose = (event) => {
      console.log('❌ WebSocket closed:', event.code, event.reason)
      connected.value = false

      // 自动重连
      if (reconnectAttempts.value < maxReconnectAttempts) {
        reconnectAttempts.value++
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.value), 30000)
        console.log(`🔄 Reconnecting in ${delay}ms... (attempt ${reconnectAttempts.value})`)
        setTimeout(connect, delay)
      }
    }
  }

  function send(data: any) {
    if (ws.value && connected.value) {
      ws.value.send(JSON.stringify(data))
      console.log('📤 Sent:', data)
    } else {
      console.warn('⚠️  WebSocket not connected, cannot send:', data)
    }
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close()
      ws.value = null
      connected.value = false
    }
  }

  return {
    connected,
    connect,
    send,
    disconnect
  }
})
```

#### 步骤 5：常见问题排查

##### 问题 1：连接失败（404 或 403）

**症状**：
```
WebSocket connection to 'ws://localhost:8002/ws' failed: Error during WebSocket handshake: Unexpected response code: 404
```

**排查**：
1. 检查 URL 是否正确
2. 确认后端服务器已启动
3. 检查 CORS 配置

**解决**：
```python
# src/server/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

##### 问题 2：连接后立即断开

**症状**：
```
✅ WebSocket connected
❌ WebSocket closed: 1006
```

**排查**：
1. 检查后端是否有未捕获的异常
2. 查看服务器日志
3. 检查心跳机制

**解决**：
添加心跳保活：

```typescript
// 前端：定期发送 ping
setInterval(() => {
  if (connected.value) {
    send({ type: 'ping' })
  }
}, 30000)  // 每 30 秒
```

```python
# 后端：处理 ping
if data.get("type") == "ping":
    await websocket.send_json({"type": "pong", "timestamp": time.time()})
```

##### 问题 3：消息未收到

**症状**：
- 前端发送成功，但后端没有日志
- 后端发送成功，但前端没收到

**排查**：
1. 检查消息格式是否为 JSON
2. 确认没有被浏览器拦截
3. 检查事件监听器是否正确注册

**解决**：
```typescript
// 确保 onmessage 在 connect 之前设置
ws.value.onmessage = (event) => {
  console.log('Raw message:', event.data)  // 先打印原始数据
  const data = JSON.parse(event.data)
  handleMessage(data)
}
```

##### 问题 4：生产环境连接失败（HTTPS 网站连接 WS）

**症状**：
```
Mixed Content: The page at 'https://example.com' was loaded over HTTPS, but attempted to connect to the insecure WebSocket endpoint 'ws://...'. This request has been blocked
```

**解决**：
使用 WSS（WebSocket Secure）：

```typescript
const wsUrl = window.location.protocol === 'https:'
  ? 'wss://example.com/ws'
  : 'ws://localhost:8002/ws'
```

配置 Nginx 反向代理：

```nginx
location /ws {
    proxy_pass http://localhost:8002/ws;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

#### 步骤 6：使用专业工具

##### Postman

1. 创建新的 WebSocket 请求
2. 输入 URL：`ws://localhost:8002/ws`
3. 点击 Connect
4. 发送 JSON 消息
5. 查看响应

##### wscat（命令行工具）

```bash
# 安装
npm install -g wscat

# 连接
wscat -c ws://localhost:8002/ws

# 发送消息
> {"type": "ping"}

# 查看响应
< {"type": "pong"}
```

### 测试 WebSocket

```python
# tests/test_websocket.py
import pytest
from fastapi.testclient import TestClient
from src.server.main import app


def test_websocket_connection():
    """测试 WebSocket 连接"""
    client = TestClient(app)

    with client.websocket_connect("/ws") as websocket:
        # 发送 ping
        websocket.send_json({"type": "ping"})

        # 接收 pong
        data = websocket.receive_json()
        assert data["type"] == "pong"


def test_websocket_broadcast(init_game):
    """测试 WebSocket 广播"""
    client = TestClient(app)

    with client.websocket_connect("/ws") as ws1, \
         client.websocket_connect("/ws") as ws2:

        # 模拟游戏事件
        from src.server.main import manager
        import asyncio

        asyncio.run(manager.broadcast({
            "type": "tick",
            "year": 100,
            "month": 1
        }))

        # 两个客户端都应该收到
        data1 = ws1.receive_json()
        data2 = ws2.receive_json()

        assert data1["type"] == "tick"
        assert data2["type"] == "tick"
```

### 常见陷阱和注意事项

1. **协议匹配**：HTTP 对应 WS，HTTPS 对应 WSS。

2. **CORS 配置**：WebSocket 升级请求也受 CORS 限制。

3. **连接数限制**：浏览器对同一域名的 WebSocket 连接数有限制（通常 6-8 个）。

4. **消息大小**：避免发送过大的消息，考虑分片或压缩。

5. **异常处理**：WebSocket 连接可能随时断开，必须处理 `onclose` 和 `onerror`。

6. **重连策略**：使用指数退避算法，避免频繁重连导致服务器负载过高。

---

## 附录

### 相关文档

- [系统架构](ARCHITECTURE.md) - 整体架构设计
- [API 文档](API.md) - API 接口说明
- [术语表](GLOSSARY.md) - 修仙术语与代码映射
- [快速上下文](.ai/context.md) - AI 开发者快速指南
- [编码规范](.ai/conventions.md) - 代码风格和约定

### 开发工具推荐

#### 后端开发
- **IDE**：PyCharm、VS Code
- **调试**：pdb、ipdb
- **性能分析**：cProfile、py-spy
- **代码质量**：pylint、mypy、black

#### 前端开发
- **IDE**：VS Code、WebStorm
- **调试**：Chrome DevTools、Vue DevTools
- **性能分析**：Lighthouse
- **代码质量**：ESLint、Prettier

#### 通用工具
- **版本控制**：Git、GitHub Desktop
- **API 测试**：Postman、curl
- **数据库管理**：DB Browser for SQLite
- **文档编写**：Typora、Obsidian

### 获取帮助

1. **查看日志**：`logs/` 目录和控制台输出
2. **检查配置**：`/api/config/llm/status`
3. **测试 LLM**：`/api/config/llm/test`
4. **查看游戏状态**：`/api/state`
5. **GitHub Issues**：https://github.com/AI-Cultivation/cultivation-world-simulator/issues

---

**最后更新**：2026-02-01
**维护者**：AI 开发团队
**版本**：v0.2.0
