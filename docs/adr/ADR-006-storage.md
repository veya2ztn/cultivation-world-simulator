# ADR-006: 选择 SQLite + JSON 作为存储方案

## 状态
✅ 已采纳

## 上下文
游戏需要持久化存储两类数据：
1. **游戏状态**: 世界、角色、宗门、地图（~10MB）
2. **事件历史**: 游戏过程中产生的所有事件（可能上万条）

### 需求
1. **轻量级部署**: 用户无需安装数据库（单文件部署）
2. **快速查询**: 支持事件分页查询、按角色筛选
3. **易于备份**: 存档可以直接复制文件
4. **跨平台**: Windows/Linux/macOS 都能用

### 数据特点
- **游戏状态**: 结构化、嵌套深、读写频率低（保存/加载时）
- **事件数据**: 量大（10,000+ 条）、线性增长、查询频繁

## 决策
采用 **SQLite（事件） + JSON（游戏状态）** 混合存储方案。

## 架构设计

### 1. 存档文件结构

每个存档包含两个文件：

```
assets/saves/
├── save_20260201_1430.json       # 游戏状态（JSON）
└── save_20260201_1430.db         # 事件数据库（SQLite）
```

### 2. JSON 存储（游戏状态）

#### 文件结构

```json
{
  "meta": {
    "version": "0.1.0",
    "save_time": "2026-02-01 14:30:00",
    "game_time": "Year 150, Month 3",
    "language": "zh-CN"
  },
  "world": {
    "month_stamp": 1803,
    "map": {
      "width": 100,
      "height": 100,
      "tiles": [[0, 1, 2, ...], ...]
    },
    "current_phenomenon": {
      "id": 1,
      "name": "灵气复苏",
      "rarity": "SR"
    }
  },
  "avatars": [
    {
      "id": "uuid-xxx",
      "name": "张三",
      "realm": "GOLDEN_CORE",
      "level": 15,
      "age": 125,
      "pos_x": 50,
      "pos_y": 30,
      "cultivation": {
        "progress": 500,
        "required": 1000,
        "technique": "九阳真经"
      },
      "items": {
        "magic_stones": 1000,
        "weapons": [{"name": "飞剑", ...}],
        "auxiliaries": [{"name": "护甲", ...}]
      },
      "relationships": [
        {"target_id": "uuid-yyy", "type": "friend", "value": 80}
      ],
      "memories": [
        {"content": "我击败了李四", "importance": 0.8}
      ],
      "objectives": [
        {"content": "加入青云门", "type": "user"}
      ]
    }
  ],
  "sects": [
    {
      "id": 1,
      "name": "青云门",
      "realm_range": ["QI_REFINING", "GOLDEN_CORE"],
      "member_ids": ["uuid-xxx", "uuid-yyy"]
    }
  ],
  "regions": [...]
}
```

#### 保存实现

```python
# src/sim/save/save_game.py
import json
from pathlib import Path

def save_game_state_to_json(world: World, save_path: Path):
    """保存游戏状态到 JSON"""

    data = {
        "meta": {
            "version": CONFIG.version,
            "save_time": datetime.now().isoformat(),
            "game_time": f"Year {world.current_year}, Month {world.current_month}",
            "language": CONFIG.system.language
        },
        "world": {
            "month_stamp": world.month_stamp,
            "map": world.map.to_dict(),
            "current_phenomenon": world.current_phenomenon.to_dict() if world.current_phenomenon else None
        },
        "avatars": [
            avatar.to_dict() for avatar in world.avatar_manager.all_avatars
        ],
        "sects": [
            sect.to_dict() for sect in world.sects
        ],
        "regions": [
            region.to_dict() for region in world.regions
        ]
    }

    # 写入 JSON（使用 indent 格式化，方便人工阅读）
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Game state saved to {save_path}")
```

#### 加载实现

```python
# src/sim/load/load_game.py
def load_game_state_from_json(save_path: Path) -> World:
    """从 JSON 加载游戏状态"""

    with open(save_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 重建世界
    world = World()
    world.month_stamp = data["world"]["month_stamp"]
    world.map = Map.from_dict(data["world"]["map"])
    world.current_phenomenon = Phenomenon.from_dict(data["world"]["current_phenomenon"]) if data["world"]["current_phenomenon"] else None

    # 重建角色
    for avatar_data in data["avatars"]:
        avatar = Avatar.from_dict(avatar_data)
        world.avatar_manager.add_avatar(avatar)

    # 重建宗门
    for sect_data in data["sects"]:
        sect = Sect.from_dict(sect_data)
        world.add_sect(sect)

    # 重建区域
    for region_data in data["regions"]:
        region = Region.from_dict(region_data)
        world.add_region(region)

    print(f"Game state loaded from {save_path}")
    return world
```

**为什么用 JSON？**
- ✅ 人类可读（可以手动编辑存档）
- ✅ 支持嵌套结构（角色关系、记忆、目标）
- ✅ Python 原生支持（无需额外依赖）
- ✅ 跨语言（前端也能直接读取）

### 3. SQLite 存储（事件历史）

#### 数据库结构

```sql
-- events 表
CREATE TABLE events (
    id TEXT PRIMARY KEY,              -- 事件 ID
    month_stamp INTEGER NOT NULL,     -- 时间戳（游戏月份）
    year INTEGER,                     -- 年份（冗余，方便查询）
    month INTEGER,                    -- 月份（冗余）
    content TEXT NOT NULL,            -- 事件内容（中文描述）
    is_major INTEGER DEFAULT 0,       -- 是否重大事件（1=是, 0=否）
    is_story INTEGER DEFAULT 0,       -- 是否剧情事件
    created_at REAL                   -- 创建时间戳（真实时间）
);

-- event_avatars 关联表（多对多）
CREATE TABLE event_avatars (
    event_id TEXT NOT NULL,
    avatar_id TEXT NOT NULL,
    PRIMARY KEY (event_id, avatar_id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);

-- 索引（优化查询性能）
CREATE INDEX idx_events_month_stamp ON events(month_stamp);
CREATE INDEX idx_events_major ON events(is_major);
CREATE INDEX idx_event_avatars_avatar ON event_avatars(avatar_id);
```

#### 插入事件

```python
# src/classes/event_manager.py
import sqlite3
from typing import List

class EventManager:
    """事件管理器（SQLite 后端）"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        """创建表"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                month_stamp INTEGER NOT NULL,
                year INTEGER,
                month INTEGER,
                content TEXT NOT NULL,
                is_major INTEGER DEFAULT 0,
                is_story INTEGER DEFAULT 0,
                created_at REAL
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS event_avatars (
                event_id TEXT NOT NULL,
                avatar_id TEXT NOT NULL,
                PRIMARY KEY (event_id, avatar_id)
            )
        ''')
        self.conn.commit()

    def add_event(self, event: Event):
        """添加事件"""
        self.conn.execute('''
            INSERT INTO events (id, month_stamp, year, month, content, is_major, is_story, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.id,
            event.month_stamp,
            event.year,
            event.month,
            event.content,
            1 if event.is_major else 0,
            1 if event.is_story else 0,
            time.time()
        ))

        # 插入关联的角色
        for avatar_id in event.related_avatar_ids:
            self.conn.execute('''
                INSERT OR IGNORE INTO event_avatars (event_id, avatar_id)
                VALUES (?, ?)
            ''', (event.id, avatar_id))

        self.conn.commit()
```

#### 分页查询

```python
def query_events(
    self,
    avatar_id: Optional[str] = None,
    cursor: Optional[int] = None,
    limit: int = 50
) -> dict:
    """分页查询事件（按时间倒序）"""

    # 构造 SQL 查询
    if avatar_id:
        # 查询某个角色相关的事件
        query = '''
            SELECT e.* FROM events e
            JOIN event_avatars ea ON e.id = ea.event_id
            WHERE ea.avatar_id = ?
            AND e.month_stamp < ?
            ORDER BY e.month_stamp DESC
            LIMIT ?
        '''
        params = (avatar_id, cursor or 999999, limit)
    else:
        # 查询所有事件
        query = '''
            SELECT * FROM events
            WHERE month_stamp < ?
            ORDER BY month_stamp DESC
            LIMIT ?
        '''
        params = (cursor or 999999, limit)

    cursor_obj = self.conn.execute(query, params)
    rows = cursor_obj.fetchall()

    events = [Event.from_db_row(row) for row in rows]

    # 返回新 cursor（最后一条事件的 month_stamp）
    new_cursor = events[-1].month_stamp if events else None

    return {
        "events": [e.to_dict() for e in events],
        "cursor": new_cursor,
        "has_more": len(events) == limit
    }
```

**为什么用 SQLite？**
- ✅ 轻量级（单文件数据库，无需安装）
- ✅ 支持 SQL 查询（分页、筛选、排序）
- ✅ 索引优化（查询速度快）
- ✅ 跨平台（Python 内置支持）
- ✅ 事务支持（数据一致性）

### 4. 存档管理

#### 保存流程

```python
def save_game(world: World, save_name: Optional[str] = None):
    """保存游戏"""

    # 生成存档文件名
    if not save_name:
        save_name = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    save_dir = Path(CONFIG.paths.saves)
    save_dir.mkdir(parents=True, exist_ok=True)

    json_path = save_dir / f"{save_name}.json"
    db_path = save_dir / f"{save_name}.db"

    # 保存游戏状态到 JSON
    save_game_state_to_json(world, json_path)

    # 复制事件数据库
    import shutil
    shutil.copy(world.event_manager.db_path, db_path)

    print(f"Game saved: {save_name}")
```

#### 加载流程

```python
def load_game(save_name: str) -> World:
    """加载游戏"""

    save_dir = Path(CONFIG.paths.saves)
    json_path = save_dir / f"{save_name}.json"
    db_path = save_dir / f"{save_name}.db"

    # 检查文件是否存在
    if not json_path.exists() or not db_path.exists():
        raise FileNotFoundError(f"Save file not found: {save_name}")

    # 加载游戏状态
    world = load_game_state_from_json(json_path)

    # 加载事件数据库
    world.event_manager = EventManager(db_path)

    print(f"Game loaded: {save_name}")
    return world
```

## 权衡

### 优点
- ✅ 轻量级（单文件，无需安装数据库）
- ✅ 快速查询（SQLite 索引优化）
- ✅ 易于备份（直接复制文件）
- ✅ 跨平台（Python 内置 SQLite）
- ✅ 人类可读（JSON 可以手动编辑）
- ✅ 职责分离（状态用 JSON，事件用 SQLite）

### 缺点
- ❌ JSON 不适合大文件（如果角色数量 > 1000，性能下降）
- ❌ SQLite 不适合高并发（但单机游戏不需要）

## 替代方案

### 方案 1: 纯 JSON
- **优点**: 实现简单、人类可读
- **缺点**:
  - 事件查询慢（需要遍历整个数组）
  - 无法分页（一次性加载所有事件）
  - 文件巨大（10,000 条事件 ~10MB）

**为什么不选**: 事件查询性能差。

### 方案 2: 纯 SQLite
- **优点**: 查询性能好、支持事务
- **缺点**:
  - 不适合存储嵌套结构（角色关系、记忆）
  - 不够直观（无法手动编辑）
  - 数据库 schema 变更麻烦

**为什么不选**: 不适合存储复杂游戏状态。

### 方案 3: PostgreSQL/MySQL
- **优点**: 功能强大、支持高并发
- **缺点**:
  - 需要安装数据库服务器（违背轻量级原则）
  - 部署复杂（用户需要配置数据库）

**为什么不选**: 过于重量级，不符合单机游戏需求。

### 方案 4: NoSQL（MongoDB/Redis）
- **优点**: 适合存储嵌套结构
- **缺点**:
  - 需要安装数据库服务器
  - 查询功能不如 SQL 强大

**为什么不选**: 部署复杂，轻量级需求不满足。

## 后果

### 正面
- 存档文件可以直接复制分享
- 事件查询速度快（分页加载 50 条 < 10ms）
- JSON 格式方便调试（可以手动修改存档）
- SQLite 轻量级，无需用户安装数据库

### 负面
- 需要维护两个文件（JSON + SQLite）
- JSON 不适合超大存档（如果角色数 > 1000）

## 经验教训
- SQLite 索引对查询性能提升巨大（从 500ms 降到 10ms）
- JSON `indent=2` 格式化让存档可读性提升
- 事件数据库单独文件便于备份和清理
- 使用 `ensure_ascii=False` 保存中文（避免乱码）

## 未来优化方向
- [ ] 支持压缩（gzip 压缩 JSON，减少文件大小）
- [ ] 支持增量存档（只保存变更）
- [ ] 引入 MessagePack 替代 JSON（二进制格式，更小更快）
- [ ] 分离角色数据（每个角色一个文件）

## 相关决策
- [ADR-005: 前后端状态同步方案](ADR-005-state-management.md)（事件分页查询）
- [ADR-001: 选择 FastAPI 作为后端框架](ADR-001-web-framework.md)

---

**创建时间**: 2026-02-01
**作者**: 后端团队
**审核**: ✅
