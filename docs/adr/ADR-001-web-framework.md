# ADR-001: 选择 FastAPI 作为后端框架

## 状态
✅ 已采纳

## 上下文
需要选择一个 Python Web 框架来构建游戏后端服务器。主要候选框架：
- **FastAPI**: 现代异步框架
- **Flask**: 传统同步框架
- **Django**: 全栈框架

## 决策
选择 **FastAPI** 作为后端框架。

## 理由

### 1. 异步支持（核心需求）
游戏需要：
- **异步游戏循环**: 后台持续运行游戏模拟
- **并发 LLM 调用**: 同时为多个 NPC 调用 LLM API
- **WebSocket 实时推送**: 向所有客户端推送游戏状态

FastAPI 原生支持 `async/await`：
```python
# FastAPI 异步路由
@app.get("/api/state")
async def get_state():
    state = await sim.get_current_state()
    return state

# 异步游戏循环
async def game_loop():
    while True:
        events = await sim.step()  # 异步执行
        await manager.broadcast(events)  # 异步推送
        await asyncio.sleep(1.0)
```

Flask/Django 需要额外的异步库（如 gevent），集成复杂。

### 2. WebSocket 原生支持
FastAPI 基于 Starlette，原生支持 WebSocket：
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(response)
```

Flask 需要 Flask-SocketIO 扩展，Django 需要 Channels（复杂）。

### 3. 自动 API 文档
FastAPI 基于 Pydantic，自动生成 OpenAPI 文档：
- 访问 `/docs` 即可看到交互式 API 文档（Swagger UI）
- 访问 `/redoc` 可看到 ReDoc 风格文档

这对开发和 AI 理解 API 都很有帮助。

### 4. 类型安全
FastAPI 强制使用类型注解：
```python
class CreateAvatarRequest(BaseModel):
    name: str
    age: int
    realm: str

@app.post("/api/avatar/create")
async def create_avatar(req: CreateAvatarRequest):
    # 自动验证请求体
    # 自动生成 JSON Schema
    pass
```

提升代码质量，减少运行时错误。

### 5. 性能
FastAPI 基于 Starlette 和 Pydantic，性能优异：
- 与 Node.js 和 Go 相当
- 比 Flask/Django 快 2-3 倍

对于需要实时推送的游戏，性能很重要。

## 权衡

### 优点
- ✅ 异步支持完善
- ✅ WebSocket 原生支持
- ✅ 自动 API 文档
- ✅ 类型安全
- ✅ 性能优秀
- ✅ 学习曲线平缓（对熟悉 Flask 的开发者）

### 缺点
- ❌ 生态不如 Django 成熟（但我们不需要 ORM、Admin 等）
- ❌ 异步编程有学习成本（但团队已熟悉）

## 替代方案

### Flask
- **优点**: 简单、成熟、生态丰富
- **缺点**:
  - 异步支持不原生（需要 gevent/eventlet）
  - WebSocket 需要额外扩展
  - 性能较低

**为什么不选**: 异步和 WebSocket 是核心需求，Flask 支持不够好。

### Django
- **优点**: 全栈、ORM、Admin、成熟
- **缺点**:
  - 太重（我们不需要 ORM、模板引擎等）
  - 异步支持不完善（Django 3.1+ 才开始支持）
  - WebSocket 需要 Channels（配置复杂）

**为什么不选**: 过于臃肿，我们只需要 API 服务器。

## 后果

### 正面
- 游戏循环和 LLM 调用可以高效并发
- WebSocket 实时推送性能优秀
- API 文档自动生成，降低维护成本
- 类型注解提升代码质量

### 负面
- 团队需要理解异步编程（已通过培训解决）
- 某些同步库需要用 `asyncio.to_thread()` 包装

## 经验教训
- 异步编程确实提升了性能，100 个 NPC 并发决策时很流畅
- 自动 API 文档极大方便了前后端协作
- 类型注解帮助 IDE 提供更好的代码补全

## 相关决策
- [ADR-002: 选择 Vue 3 作为前端框架](ADR-002-frontend-framework.md)
- [ADR-004: LLM 集成架构设计](ADR-004-llm-integration.md)

---

**创建时间**: 2026-02-01
**作者**: 架构团队
**审核**: ✅
