# ADR-008: 测试策略

## 状态
✅ 已采纳

## 上下文
修仙世界模拟器是一个复杂的系统，包含：
- **后端**: 游戏逻辑、AI 决策、LLM 集成、数据持久化
- **前端**: UI 渲染、PixiJS Canvas、状态管理、WebSocket 通信

需要设计一套完整的测试策略，确保：
1. **代码质量**: 减少 bug，提升可维护性
2. **重构信心**: 安全重构，不破坏功能
3. **文档作用**: 测试作为代码文档
4. **持续集成**: CI/CD 自动化测试

## 决策
采用 **pytest（后端） + Vitest（前端）** 的分层测试策略。

## 测试分层

### 测试金字塔

```
         ┌─────────────────┐
         │  E2E 测试 (5%)   │  端到端测试（浏览器自动化）
         └─────────────────┘
        ┌───────────────────┐
        │ 集成测试 (25%)     │  模块间交互测试
        └───────────────────┘
      ┌───────────────────────┐
      │  单元测试 (70%)        │  函数/类级别测试
      └───────────────────────┘
```

**原则**:
- **70% 单元测试**: 快速、独立、细粒度
- **25% 集成测试**: 测试模块间交互
- **5% E2E 测试**: 测试关键用户流程

## 后端测试（pytest）

### 1. 单元测试

#### 测试角色类

```python
# tests/test_avatar.py
import pytest
from src.classes.avatar import Avatar
from src.classes.realm import Realm

@pytest.fixture
def test_avatar():
    """测试角色 fixture"""
    return Avatar(
        name="张三",
        realm=Realm.QI_REFINING,
        age=20,
        x=50,
        y=50
    )

def test_avatar_creation(test_avatar):
    """测试角色创建"""
    assert test_avatar.name == "张三"
    assert test_avatar.realm == Realm.QI_REFINING
    assert test_avatar.age == 20
    assert test_avatar.is_alive

def test_cultivation_speed(test_avatar):
    """测试修炼速度计算"""
    speed = test_avatar.calculate_cultivation_speed()
    assert speed > 0
    assert isinstance(speed, (int, float))

def test_age_increase(test_avatar):
    """测试年龄增长"""
    old_age = test_avatar.age
    test_avatar.age_increase(months=12)
    assert test_avatar.age == old_age + 1

def test_death_by_lifespan(test_avatar):
    """测试寿元耗尽死亡"""
    test_avatar.age = test_avatar.max_lifespan + 1
    test_avatar.check_lifespan()
    assert not test_avatar.is_alive

@pytest.mark.parametrize("realm,expected_max_hp", [
    (Realm.QI_REFINING, 100),
    (Realm.FOUNDATION_ESTABLISHMENT, 200),
    (Realm.GOLDEN_CORE, 500),
])
def test_max_hp_by_realm(realm, expected_max_hp):
    """测试不同境界的生命值上限"""
    avatar = Avatar(name="测试", realm=realm)
    assert avatar.max_hp == expected_max_hp
```

#### 测试突破逻辑

```python
# tests/test_breakthrough.py
import pytest
from src.classes.avatar import Avatar
from src.classes.realm import Realm

@pytest.fixture
def avatar_ready_for_breakthrough():
    """准备突破的角色"""
    avatar = Avatar(name="李四", realm=Realm.QI_REFINING, level=15)
    avatar.cultivation_progress = avatar.cultivation_required
    return avatar

async def test_breakthrough_success(avatar_ready_for_breakthrough):
    """测试突破成功"""
    old_realm = avatar_ready_for_breakthrough.realm
    result = await avatar_ready_for_breakthrough.attempt_breakthrough()

    assert result.success
    assert avatar_ready_for_breakthrough.realm == Realm.FOUNDATION_ESTABLISHMENT
    assert avatar_ready_for_breakthrough.level == 1

async def test_breakthrough_failure_insufficient_progress():
    """测试修为不足无法突破"""
    avatar = Avatar(name="王五", realm=Realm.QI_REFINING, level=15)
    avatar.cultivation_progress = 0

    result = await avatar.attempt_breakthrough()
    assert not result.success
    assert result.reason == "cultivation_insufficient"

async def test_breakthrough_heavenly_tribulation():
    """测试天劫失败"""
    avatar = Avatar(name="赵六", realm=Realm.GOLDEN_CORE, level=15)
    avatar.cultivation_progress = avatar.cultivation_required

    # 模拟天劫失败（通过 mock）
    with pytest.mock.patch('src.classes.avatar.Avatar.survive_tribulation', return_value=False):
        result = await avatar.attempt_breakthrough()
        assert not result.success
        assert result.reason == "tribulation_failed"
        assert not avatar.is_alive
```

### 2. 集成测试

#### 测试游戏模拟器

```python
# tests/test_simulator.py
import pytest
from src.sim.simulator import Simulator
from src.classes.world import World

@pytest.fixture
async def simulator():
    """创建模拟器 fixture"""
    world = World()
    # 添加一些测试角色
    for i in range(5):
        avatar = Avatar(name=f"NPC-{i}", realm=Realm.QI_REFINING)
        world.avatar_manager.add_avatar(avatar)

    sim = Simulator(world)
    return sim

async def test_simulator_step(simulator):
    """测试模拟器推进一步"""
    old_month = simulator.world.month_stamp

    events = await simulator.step()

    # 时间推进
    assert simulator.world.month_stamp == old_month + 1

    # 生成了事件
    assert len(events) > 0

    # 所有角色都更新了
    for avatar in simulator.world.living_avatars:
        assert avatar.age > 0

async def test_simulator_death_event(simulator):
    """测试角色死亡事件"""
    # 找一个角色，设置寿元即将耗尽
    avatar = simulator.world.living_avatars[0]
    avatar.age = avatar.max_lifespan

    events = await simulator.step()

    # 应该生成死亡事件
    death_events = [e for e in events if "坐化" in e.content or "death" in e.content.lower()]
    assert len(death_events) > 0

    # 角色已死亡
    assert not avatar.is_alive
```

#### 测试 LLM 集成

```python
# tests/test_llm_integration.py
import pytest
from src.utils.llm.client import call_llm_api, LLMMode
from src.utils.llm.prompts import build_decision_prompt
from src.classes.avatar import Avatar

@pytest.mark.asyncio
@pytest.mark.integration
async def test_llm_api_call():
    """测试 LLM API 调用"""
    prompt = "你好，请返回 JSON: {\"message\": \"Hello\"}"

    response = await call_llm_api(prompt, mode=LLMMode.FAST)

    assert response is not None
    assert len(response) > 0

@pytest.mark.asyncio
@pytest.mark.integration
async def test_llm_decision_for_avatar():
    """测试 LLM 为角色生成决策"""
    avatar = Avatar(name="测试角色", realm=Realm.QI_REFINING)

    prompt = build_decision_prompt(avatar)
    response = await call_llm_api(prompt, mode=LLMMode.NORMAL)

    # 解析 JSON
    import json
    data = json.loads(response)

    assert "action" in data
    assert data["action"] in ["cultivate", "move", "rest", "breakthrough"]

@pytest.mark.asyncio
async def test_llm_fallback_on_failure(monkeypatch):
    """测试 LLM 失败时回退到规则 AI"""
    # 模拟 LLM API 失败
    async def mock_llm_call(*args, **kwargs):
        raise Exception("API 失败")

    monkeypatch.setattr("src.utils.llm.client.call_llm_api", mock_llm_call)

    avatar = Avatar(name="测试", realm=Realm.QI_REFINING)
    action = await avatar.decide_action()

    # 应该回退到规则 AI
    assert action is not None
```

### 3. 测试配置

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 异步测试支持
asyncio_mode = auto

# 标记
markers =
    slow: 慢速测试
    integration: 集成测试（需要外部服务）
    unit: 单元测试

# 覆盖率
addopts =
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
```

```bash
# 运行测试
pytest                    # 运行所有测试
pytest tests/test_avatar.py  # 运行单个文件
pytest -m unit           # 只运行单元测试
pytest -m "not integration"  # 跳过集成测试
pytest -k "test_breakthrough"  # 运行名称包含 breakthrough 的测试
pytest --cov             # 生成覆盖率报告
```

## 前端测试（Vitest）

### 1. 单元测试（组件）

#### 测试 AvatarPanel 组件

```typescript
// web/src/components/__tests__/AvatarPanel.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import AvatarPanel from '@/components/game/panels/info/AvatarDetail.vue'

describe('AvatarPanel', () => {
  it('renders avatar name', () => {
    const pinia = createPinia()
    const wrapper = mount(AvatarPanel, {
      global: { plugins: [pinia] },
      props: {
        avatarId: 'test-id'
      }
    })

    expect(wrapper.text()).toContain('张三')
  })

  it('displays cultivation progress', () => {
    const wrapper = mount(AvatarPanel, {
      props: {
        avatarId: 'test-id'
      }
    })

    expect(wrapper.find('.cultivation-progress').exists()).toBe(true)
  })

  it('emits close event when close button clicked', async () => {
    const wrapper = mount(AvatarPanel)

    await wrapper.find('.close-button').trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
```

### 2. 集成测试（Store）

```typescript
// web/src/stores/__tests__/gameStore.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useGameStore } from '@/stores/gameStore'

describe('GameStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with default values', () => {
    const store = useGameStore()

    expect(store.year).toBe(100)
    expect(store.month).toBe(1)
    expect(store.isPaused).toBe(true)
  })

  it('updates time on tick message', () => {
    const store = useGameStore()

    store.handleTickMessage({
      type: 'tick',
      year: 150,
      month: 5,
      events: [],
      avatars: []
    })

    expect(store.year).toBe(150)
    expect(store.month).toBe(5)
  })

  it('pauses and resumes game', async () => {
    const store = useGameStore()

    await store.pause()
    expect(store.isPaused).toBe(true)

    await store.resume()
    expect(store.isPaused).toBe(false)
  })
})
```

### 3. API Mock

```typescript
// web/src/api/__tests__/game.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { rest } from 'msw'
import { setupServer } from 'msw/node'
import { gameAPI } from '@/api/game'

// 模拟后端 API
const server = setupServer(
  rest.get('/api/state', (req, res, ctx) => {
    return res(ctx.json({
      year: 150,
      month: 3,
      avatars: []
    }))
  }),

  rest.post('/api/control/pause', (req, res, ctx) => {
    return res(ctx.json({ status: 'ok' }))
  })
)

beforeEach(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('gameAPI', () => {
  it('fetches game state', async () => {
    const state = await gameAPI.getState()

    expect(state.year).toBe(150)
    expect(state.month).toBe(3)
  })

  it('pauses game', async () => {
    const result = await gameAPI.pause()

    expect(result.status).toBe('ok')
  })
})
```

### 4. 测试配置

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: ['node_modules/', 'tests/', '**/*.d.ts']
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
```

```bash
# 运行测试
npm run test           # 运行所有测试
npm run test:run       # 运行一次（CI 模式）
npm run test:coverage  # 生成覆盖率报告
```

## 覆盖率要求

### 目标

| 层次 | 覆盖率目标 | 说明 |
|-----|----------|------|
| **核心逻辑** | > 80% | Avatar, Simulator, Action 等 |
| **工具函数** | > 70% | utils, llm, config 等 |
| **API 路由** | > 60% | FastAPI 路由 |
| **UI 组件** | > 50% | Vue 组件 |

### 覆盖率报告

```bash
# 后端覆盖率
pytest --cov --cov-report=html
# 生成 htmlcov/index.html

# 前端覆盖率
npm run test:coverage
# 生成 coverage/index.html
```

## 持续集成（CI/CD）

### GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run tests
        run: pytest --cov --cov-fail-under=70

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd web && npm install
      - name: Run tests
        run: cd web && npm run test:run
```

## 权衡

### 优点
- ✅ pytest 简单易用，异步支持好
- ✅ Vitest 速度快（Vite 驱动）
- ✅ 分层测试覆盖全面
- ✅ Mock 工具强大（msw, pytest.mock）
- ✅ 覆盖率报告清晰

### 缺点
- ❌ 测试代码需要维护（与功能代码同步）
- ❌ E2E 测试慢（但比例小，影响有限）

## 替代方案

### 方案 1: unittest（Python 标准库）
- **优点**: 标准库，无需安装
- **缺点**:
  - 语法繁琐（`self.assertEqual`）
  - 异步支持差
  - fixture 不够灵活

**为什么不选**: pytest 更现代、更好用。

### 方案 2: Jest（前端）
- **优点**: 生态最大、社区活跃
- **缺点**:
  - 速度慢（需要 Babel 转译）
  - 配置复杂
  - 不如 Vitest 与 Vite 集成好

**为什么不选**: Vitest 速度快，与 Vite 无缝集成。

## 后果

### 正面
- 测试覆盖率达标，代码质量提升
- 重构时有信心（测试保障）
- CI/CD 自动化，减少手动测试

### 负面
- 测试代码需要维护（增加工作量）
- 集成测试依赖外部服务（如 LLM API）

## 经验教训
- pytest fixture 极大提升测试复用性
- msw 模拟 API 比手动 mock 更可靠
- 覆盖率不是越高越好，70-80% 是性价比最高的
- E2E 测试比例不宜过高（慢且脆弱）

## 未来优化方向
- [ ] 引入 Playwright 做 E2E 测试
- [ ] 使用 pytest-xdist 并行测试
- [ ] 引入变异测试（Mutation Testing）
- [ ] 测试数据生成器（Faker）

## 相关决策
- [ADR-001: 选择 FastAPI 作为后端框架](ADR-001-web-framework.md)（pytest-asyncio 支持）
- [ADR-002: 选择 Vue 3 作为前端框架](ADR-002-frontend-framework.md)（Vitest 集成）

---

**创建时间**: 2026-02-01
**作者**: 测试团队
**审核**: ✅
