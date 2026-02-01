# AI 开发者快速上手指南

欢迎加入修仙世界模拟器的开发！本指南专为 AI 开发者设计，帮助你在 5 分钟内理解项目并开始贡献。

---

## 🎯 5 分钟快速理解

### 项目是什么？
一个 **AI 驱动的修仙世界模拟器**，每个 NPC 都由大语言模型赋予智能，世界按规则运行，剧情自然涌现。

### 技术栈（一句话）
- **后端**: Python + FastAPI + 异步游戏循环
- **前端**: Vue 3 + PixiJS
- **AI**: LLM API (OpenAI/DeepSeek/Ollama)

### 核心文件（只需知道这 5 个）
1. `src/server/main.py` - 服务器入口（1870 行，包含所有 API）
2. `src/sim/simulator.py` - 游戏模拟器（核心逻辑）
3. `src/classes/avatar/avatar.py` - 角色类定义
4. `web/src/components/game/GameMap.vue` - 前端地图组件
5. `.ai/context.md` - **从这里开始！**（项目大脑）

### 关键概念（3 个）
1. **游戏循环**: 后台每秒推进一个游戏月，NPC 做决策、执行动作、生成事件
2. **双层 AI**: 规则 AI（快速、确定）+ LLM AI（智能、创造）
3. **WebSocket 推送**: 实时推送游戏状态到前端

---

## 📖 必读文档（按顺序）

### 第 1 步：理解全局（5 分钟）
📄 **`.ai/context.md`** - 项目大脑，一页纸总结
- 整体架构图
- 核心目录职责
- 关键概念映射
- 数据流简图

### 第 2 步：深入架构（15 分钟）
📄 **`docs/ARCHITECTURE.md`** - 系统架构文档
- 技术选型理由
- 模块详细划分
- API 设计
- 存储格式

### 第 3 步：理解数据流（10 分钟）
📄 **`docs/DATA_FLOW.md`** - 数据流文档
- 游戏循环详解
- LLM 调用流程
- 用户交互流程
- WebSocket 协议

### 第 4 步：查询术语（随时参考）
📄 **`docs/GLOSSARY.md`** - 术语表
- 修仙术语 → 代码映射
- 境界、动作、物品对照表
- 数据结构详解

---

## 🚀 快速开始开发

### 环境准备

```bash
# 1. 克隆项目
git clone https://github.com/AI-Cultivation/cultivation-world-simulator.git
cd cultivation-world-simulator

# 2. 安装后端依赖
pip install -r requirements.txt

# 3. 安装前端依赖
cd web && npm install && cd ..

# 4. 启动开发模式（自动打开浏览器）
python src/server/main.py --dev
```

### 配置 LLM

编辑 `static/local_config.yml`：

```yaml
llm:
  base_url: "https://api.deepseek.com"  # 或 OpenAI/Ollama
  key: "your-api-key-here"
  model_name: "deepseek-chat"
  fast_model_name: "deepseek-chat"
  mode: "default"
```

或者在前端界面直接配置（推荐）。

### 运行测试

```bash
# 后端测试
pytest

# 前端测试
cd web && npm run test
```

---

## 🎓 开发工作流

### 我想添加新功能

1. **阅读提示词模板**: `.ai/prompts/add_feature.md`
2. **查看类似功能**: 例如想加"炼丹"，参考 `src/classes/action/forge.py`（铸造）
3. **按照模板提问**: 复制提示词模板，填入你的需求
4. **AI 返回**: 影响文件列表、数据结构、实现代码、测试

### 我想修复 Bug

1. **阅读提示词模板**: `.ai/prompts/fix_bug.md`
2. **描述 Bug**: 复现步骤、期望行为、错误信息
3. **AI 返回**: 根因分析、修复代码、回归测试

### 我想重构代码

1. **阅读提示词模板**: `.ai/prompts/refactor.md`
2. **说明原因**: 代码重复、性能问题、可读性差等
3. **AI 返回**: 重构方案、风险评估、迁移步骤

---

## 🔍 常见任务速查

### 如何找到某个功能的代码？

**方法 1**: 查术语表
```
想找"突破" → 查 docs/GLOSSARY.md → BreakthroughAction → src/classes/action/breakthrough.py
```

**方法 2**: 全局搜索
```bash
# 搜索类名
grep -r "class BreakthroughAction" src/

# 搜索功能关键词
grep -r "突破" src/
```

**方法 3**: 使用 AI 助手工具（未来）
```bash
python tools/ai_dev_assistant.py find "突破功能"
```

### 如何理解一个模块？

1. **读 README**: 每个目录都有 `README.md`（如果没有，参考 `.ai/conventions.md` 创建）
2. **看类 Docstring**: 每个类都有文档字符串
3. **找测试用例**: `tests/test_xxx.py` 是最好的使用示例

### 如何添加新的 NPC 动作？

详见 **`docs/COMMON_TASKS.md`**（未来创建）。

简要步骤：
```python
# 1. 创建动作类
# src/classes/action/my_action.py
class MyAction(Action):
    name = "my_action"
    EMOJI = "🎯"
    duration = 3  # 持续 3 个月

    def execute(self, avatar: Avatar) -> ActionResult:
        # 实现逻辑
        pass

# 2. 注册动作
# src/classes/actions.py
from src.classes.action.my_action import MyAction

ACTION_REGISTRY["my_action"] = MyAction

# 3. 添加测试
# tests/test_my_action.py
def test_my_action():
    avatar = create_test_avatar()
    action = MyAction(avatar)
    result = action.execute(avatar)
    assert result.success is True
```

### 如何添加新的 API 端点？

详见 **`docs/COMMON_TASKS.md`**。

简要步骤：
```python
# src/server/main.py

@app.get("/api/my-endpoint")
async def my_endpoint(param: str = Query()):
    """我的新端点

    Args:
        param: 查询参数

    Returns:
        JSON 响应
    """
    world = game_instance.get("world")
    if not world:
        raise HTTPException(status_code=503, detail="World not initialized")

    # 处理逻辑
    result = do_something(param)

    return {"status": "ok", "data": result}
```

### 如何调试？

**后端调试**:
```python
# 添加日志
import logging
logger = logging.getLogger(__name__)
logger.info(f"Avatar {avatar.name} is doing {action.name}")

# 使用 print（开发时）
print(f"[Debug] Avatar state: {avatar.to_dict()}")

# 使用断点（VS Code/PyCharm）
breakpoint()  # Python 3.7+
```

**前端调试**:
```javascript
// 控制台日志
console.log("Avatar data:", avatar)

// Vue DevTools（浏览器扩展）
// 可以查看组件状态、Pinia Store

// 网络请求（浏览器开发者工具）
// Network 标签查看 API 请求
```

---

## 🧭 项目导航

### 后端文件结构速查

```
src/
├── server/
│   └── main.py              ← 🔴 所有 API 都在这里
├── sim/
│   ├── simulator.py         ← 🔴 游戏模拟器核心
│   ├── save/                ← 存档系统
│   └── load/                ← 加载系统
├── classes/
│   ├── avatar/              ← 角色相关
│   │   ├── avatar.py        ← 🔴 Avatar 类定义
│   │   └── planner.py       ← 角色 AI 决策
│   ├── action/              ← 所有动作
│   │   ├── base.py          ← Action 基类
│   │   ├── move.py
│   │   ├── cultivate.py
│   │   └── ...
│   ├── sect.py              ← 宗门
│   ├── event.py             ← 事件
│   ├── world.py             ← 世界
│   └── ...
├── utils/
│   ├── llm/                 ← LLM 客户端
│   │   ├── client.py        ← 🔴 LLM API 调用
│   │   └── config.py        ← LLM 配置
│   └── config.py            ← 全局配置加载
└── i18n/                    ← 国际化
```

### 前端文件结构速查

```
web/src/
├── components/
│   ├── game/
│   │   ├── GameMap.vue      ← 🔴 地图渲染
│   │   └── AvatarSprite.vue ← 角色精灵
│   ├── panels/              ← 各种面板
│   │   ├── AvatarPanel.vue  ← 角色详情
│   │   ├── EventPanel.vue   ← 事件列表
│   │   └── ...
│   └── SystemMenu.vue       ← 系统菜单
├── stores/                  ← Pinia Store
│   ├── gameStore.ts         ← 🔴 游戏状态
│   ├── avatarStore.ts       ← 角色状态
│   └── eventStore.ts        ← 事件状态
├── api/                     ← API 调用封装
│   ├── game.ts
│   ├── avatar.ts
│   └── ...
└── types/                   ← TypeScript 类型
```

---

## 📚 编码规范速查

详见 **`.ai/conventions.md`**。

### 命名约定

```python
# 类名: PascalCase
class AvatarManager:
    pass

# 函数/变量: snake_case
def calculate_cultivation_speed():
    base_speed = 10

# 常量: UPPER_SNAKE_CASE
MAX_LIFESPAN = 500

# 私有成员: _leading_underscore
self._internal_state = {}
```

### 文档字符串（必须）

```python
def my_function(param1: int, param2: str) -> bool:
    """简短描述（一句话）

    详细说明（可选，如果逻辑复杂）。

    Args:
        param1: 参数 1 说明
        param2: 参数 2 说明

    Returns:
        返回值说明

    Raises:
        ValueError: 什么情况下抛出

    Example:
        >>> my_function(1, "test")
        True
    """
    pass
```

### 类型注解（必须）

```python
from typing import List, Optional, Dict

def process_avatars(
    avatars: List[Avatar],
    filter_realm: Optional[CultivationRealm] = None
) -> Dict[str, Avatar]:
    """处理角色列表"""
    pass
```

---

## 🆘 遇到问题？

### 问题解决流程

1. **查文档**:
   - `.ai/context.md` - 全局理解
   - `docs/ARCHITECTURE.md` - 架构问题
   - `docs/GLOSSARY.md` - 术语问题

2. **查代码**:
   - 搜索类名、函数名
   - 查看测试用例
   - 查看类 Docstring

3. **使用 AI 提示词**:
   - `.ai/prompts/add_feature.md`
   - `.ai/prompts/fix_bug.md`
   - `.ai/prompts/refactor.md`

4. **提问**:
   - GitHub Issues
   - 开发者群组

### 常见错误

#### 错误 1: LLM API 调用失败
```
LLMError: Connection timeout
```

**解决**:
1. 检查 `static/local_config.yml` 中的 API 配置
2. 测试连通性: `/api/config/llm/test`
3. 查看日志: 控制台输出

#### 错误 2: 存档加载失败
```
JSONDecodeError: Expecting value
```

**解决**:
1. 检查存档文件是否损坏
2. 查看存档版本是否兼容
3. 使用最新代码重新保存

#### 错误 3: 前端无法连接后端
```
WebSocket connection failed
```

**解决**:
1. 确认后端已启动: `http://localhost:8002/api/state`
2. 检查端口占用
3. 查看浏览器控制台错误

---

## 🎯 下一步

### 完成第一个任务

选择一个简单的任务练手：
- [ ] 添加一个新的性格特质（Persona）
- [ ] 添加一个新的丹药类型
- [ ] 优化某个提示词
- [ ] 编写一个缺失的测试用例

### 深入学习

1. **阅读 ADR**: `docs/adr/` 了解设计决策
2. **阅读测试**: `tests/` 学习如何使用 API
3. **实践**: 运行游戏，观察 NPC 行为
4. **贡献**: 提交 PR，改进项目

---

## 📞 联系我们

- **GitHub Issues**: https://github.com/AI-Cultivation/cultivation-world-simulator/issues
- **QQ 群**: 1071821688（进群问题：肥桥今天吃什么）
- **B 站**: https://space.bilibili.com/527346837

---

**记住这 3 个文件，你就能开始开发**:
1. `.ai/context.md` - 项目大脑
2. `.ai/conventions.md` - 编码规范
3. `docs/GLOSSARY.md` - 术语表

**Happy Coding! 🚀**
