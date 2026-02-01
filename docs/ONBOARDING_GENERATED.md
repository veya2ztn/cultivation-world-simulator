# 新人上手指南

## 项目概览

修仙世界模拟器是一个 AI 驱动的修仙世界模拟游戏。

## 核心文件（按重要性排序）

### `src/server/main.py`

FastAPI 服务器主文件，包含所有 API 端点和游戏循环

- 代码行数: ~1872

### `src/sim/simulator.py`

游戏模拟器核心，控制游戏推进

- 代码行数: ~510

### `src/classes/world.py`

世界类，管理游戏世界状态

- 代码行数: ~131

### `src/classes/avatar/core.py`

角色核心类

- 代码行数: ~441

### `src/classes/action/action.py`

动作系统基类

- 代码行数: ~262

### `src/utils/llm/client.py`

LLM 客户端封装

- 代码行数: ~183

## 学习路径建议

### 第 1 天：熟悉项目结构

1. 阅读 `README.md` 了解项目背景
2. 阅读 `.ai/context.md` 了解快速上下文
3. 运行项目，体验游戏

### 第 2-3 天：理解核心流程

1. 阅读 `src/server/main.py` 理解服务器启动流程
2. 阅读 `src/sim/simulator.py` 理解游戏循环
3. 调试一个完整的游戏 tick，观察数据流

### 第 4-5 天：深入业务逻辑

1. 阅读 `src/classes/avatar/` 理解角色系统
2. 阅读 `src/classes/action/` 理解动作系统
3. 尝试添加一个简单的动作

### 第 6-7 天：掌握 AI 系统

1. 阅读 `src/utils/llm/` 理解 LLM 集成
2. 阅读 `src/classes/ai.py` 理解 AI 决策
3. 尝试优化 AI 提示词

## 常见任务

### 添加新的 API 端点

在 `src/server/main.py` 中添加新的路由函数：

```python
@app.get('/api/your-endpoint')
def your_endpoint():
    """你的端点说明"""
    return {'status': 'ok'}
```

### 添加新的动作

1. 在 `src/classes/action/` 创建新文件
2. 继承 `Action` 基类
3. 在 `src/classes/actions.py` 注册

### 运行测试

```bash
pytest
pytest --cov=src  # 带覆盖率
```

## 开发工具

- 本工具: `python tools/ai_dev_assistant.py --help`
- API 文档生成: `python tools/generate_api.py`
- 代码生成工具: `tools/generate_*.py`

## 获取帮助

- 查看 `docs/` 目录下的详细文档
- 提交 GitHub Issue
- 查看测试文件了解使用示例
