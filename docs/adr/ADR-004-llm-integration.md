# ADR-004: LLM 集成架构设计

## 状态
✅ 已采纳

## 上下文
修仙世界模拟器的核心创新是"每个 NPC 都由 LLM 驱动"。需要设计一个高效、可靠、可扩展的 LLM 集成架构。

### 需求
1. **智能决策**: NPC 需要根据复杂情况做出合理决策
2. **高并发**: 可能有 100+ 个 NPC 同时需要决策
3. **容错性**: LLM API 可能失败，不能中断游戏
4. **成本控制**: 每次调用都有成本，需要优化
5. **可扩展**: 支持多种 LLM 提供商（OpenAI, DeepSeek, Ollama等）

## 决策
采用 **双层 AI 架构**：规则 AI（确定性）+ LLM AI（创造性）

## 架构设计

### 1. 双层 AI 架构

```python
async def avatar_decide_action(avatar: Avatar) -> Action:
    """角色决策下一步动作"""

    # 第一层：规则 AI（确定性逻辑）
    # 处理紧急情况和明确规则
    if avatar.hp < avatar.max_hp * 0.2:
        return RestAction(avatar)  # 生命值低 → 疗伤

    if avatar.can_breakthrough():
        return BreakthroughAction(avatar)  # 可以突破 → 突破

    if avatar.lifespan_remaining < 10:
        return SeekLifeExtensionAction(avatar)  # 寿元不足 → 寻求续命

    # 第二层：LLM AI（创造性决策）
    # 处理复杂、需要判断的情况
    if should_use_llm(avatar):
        try:
            action = await llm_decide_action(avatar)
            return action
        except LLMError as e:
            logger.warning(f"LLM failed for {avatar.name}, fallback to rule AI: {e}")
            # 失败 → 回退到规则 AI
            return rule_based_decide(avatar)

    # 默认：规则 AI
    return rule_based_decide(avatar)
```

**为什么双层？**
- **规则 AI 快且可靠**: 处理确定性逻辑（如生存需求），无网络延迟
- **LLM AI 智能但慢**: 处理创造性决策（如社交、策略），有延迟和失败风险
- **降级保护**: LLM 失败时回退到规则 AI，游戏不会中断

### 2. LLM 调用策略

#### 觉醒率（Awakening Rate）
不是所有 NPC 每次都用 LLM，而是根据概率：

```python
def should_use_llm(avatar: Avatar) -> bool:
    """判断是否使用 LLM"""
    # 主角永远使用 LLM
    if avatar.is_protagonist:
        return True

    # 其他 NPC 根据觉醒率
    awakening_rate = CONFIG.game.npc_awakening_rate_per_month
    return random.random() < awakening_rate
```

**配置示例**:
```yaml
game:
  npc_awakening_rate_per_month: 0.01  # 每月 1% 概率使用 LLM
```

**为什么不是 100%？**
- **成本控制**: 100 个 NPC 每月都调用 → 成本高
- **性能**: LLM 调用有延迟，全部用会很慢
- **剧情张弛**: 偶尔的智能决策更有惊喜感

#### 并发控制

```python
async def process_all_avatars(avatars: List[Avatar]):
    """批量处理所有角色决策"""
    # 限制并发数，避免打爆 LLM API
    semaphore = asyncio.Semaphore(10)  # 最多 10 个并发

    async def bounded_decide(avatar):
        async with semaphore:
            return await avatar.decide()

    results = await asyncio.gather(
        *[bounded_decide(a) for a in avatars],
        return_exceptions=True  # 捕获异常，不中断其他任务
    )

    # 处理结果
    for avatar, result in zip(avatars, results):
        if isinstance(result, Exception):
            logger.error(f"Avatar {avatar.name} decision failed: {result}")
            # 使用规则 AI 兜底
            avatar.start_action(rule_based_decide(avatar))
        else:
            avatar.start_action(result)
```

### 3. 提示词工程

#### 提示词模板

```python
def build_llm_prompt(avatar: Avatar) -> str:
    """构造 LLM 提示词"""

    # 收集上下文
    nearby_avatars = get_nearby_avatars(avatar, radius=5)
    nearby_regions = get_nearby_regions(avatar, radius=3)
    recent_memories = avatar.get_recent_memories(limit=5)

    prompt = f"""
你是修仙世界中的角色：{avatar.name}

# 基本信息
- 境界：{avatar.realm.value} {avatar.level}层
- 年龄：{avatar.age} 岁（寿元上限：{avatar.max_lifespan}）
- 宗门：{avatar.sect.name if avatar.sect else "散修"}
- 性格：{", ".join([p.name for p in avatar.personas])}

# 当前状态
- 修为进度：{avatar.cultivation_progress}/{avatar.cultivation_required} ({avatar.cultivation_progress_percent}%)
- 生命值：{avatar.hp}/{avatar.max_hp}
- 灵石：{avatar.magic_stones}
- 位置：({avatar.x}, {avatar.y})

# 周围环境
## 附近的人
{format_nearby_avatars(nearby_avatars)}

## 附近的区域
{format_nearby_regions(nearby_regions)}

# 最近记忆
{format_memories(recent_memories)}

# 长期目标
{format_objectives(avatar.long_term_objectives)}

# 短期目标
{format_objectives(avatar.short_term_objectives)}

# 可用动作
{format_available_actions(avatar)}

请根据以上信息，决定下一步动作。返回 JSON 格式：
{{
    "action": "action_name",  // 动作名称
    "target": "target_id或null",  // 目标对象（如果需要）
    "reasoning": "为什么做这个决定",  // 决策理由（用于生成事件描述）
    "thought": "角色的内心想法"  // 可选，角色的心理活动
}}

注意：
1. 优先考虑长期目标，但也要关注生存需求
2. 决策要符合角色性格和当前境界
3. 避免过于冒险的决定（除非性格是"冒险"）
"""
    return prompt
```

#### 提示词优化
- **动态调整**: 根据境界、性格调整提示词细节
- **上下文窗口**: 只包含最相关的信息，避免超长提示词
- **结构化输出**: 强制返回 JSON，方便解析

### 4. 多模型支持

#### 配置抽象

```python
class LLMConfig:
    """LLM 配置"""
    base_url: str
    api_key: str
    model_name: str  # 智能模型（复杂决策）
    fast_model_name: str  # 快速模型（简单任务）

    @classmethod
    def from_mode(cls, mode: LLMMode):
        """根据模式加载配置"""
        if mode == LLMMode.NORMAL:
            return cls(model_name=CONFIG.llm.model_name)
        elif mode == LLMMode.FAST:
            return cls(model_name=CONFIG.llm.fast_model_name)
```

#### 客户端抽象

```python
async def call_llm_api(
    prompt: str,
    mode: LLMMode = LLMMode.NORMAL
) -> str:
    """调用 LLM API（支持多种提供商）"""

    config = LLMConfig.from_mode(mode)

    # 使用 OpenAI SDK（兼容多种提供商）
    client = AsyncOpenAI(
        base_url=config.base_url,
        api_key=config.api_key
    )

    try:
        response = await client.chat.completions.create(
            model=config.model_name,
            messages=[
                {"role": "system", "content": "你是一个修仙世界的角色..."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},  # 强制返回 JSON
            timeout=30.0
        )
        return response.choices[0].message.content
    except httpx.TimeoutException:
        raise LLMTimeoutError("LLM API timeout")
    except Exception as e:
        raise LLMError(f"LLM API error: {e}")
```

**支持的提供商**:
- OpenAI (gpt-4, gpt-3.5-turbo)
- DeepSeek (deepseek-chat)
- Ollama (本地模型，如 llama2)
- 任何兼容 OpenAI API 的提供商

### 5. 错误处理与降级

#### 分层错误处理

```python
async def llm_decide_action(avatar: Avatar) -> Action:
    """LLM 决策动作（带完整错误处理）"""

    try:
        # 1. 构造提示词
        prompt = build_llm_prompt(avatar)

        # 2. 调用 LLM
        response_text = await call_llm_api(prompt, mode=LLMMode.NORMAL)

        # 3. 解析 JSON
        response_data = json.loads(response_text)

        # 4. 验证响应
        if "action" not in response_data:
            raise ValueError("Response missing 'action' field")

        action_name = response_data["action"]
        if action_name not in ACTION_REGISTRY:
            raise ValueError(f"Unknown action: {action_name}")

        # 5. 创建动作
        action_class = ACTION_REGISTRY[action_name]
        action = action_class.from_llm_response(avatar, response_data)

        # 6. 记录思考过程（用于记忆）
        if "thought" in response_data:
            avatar.add_memory(
                Memory(content=response_data["thought"], type="thought")
            )

        return action

    except LLMTimeoutError:
        logger.warning(f"{avatar.name} LLM timeout, fallback to rule AI")
        return rule_based_decide(avatar)

    except json.JSONDecodeError as e:
        logger.error(f"{avatar.name} LLM returned invalid JSON: {e}")
        return rule_based_decide(avatar)

    except ValueError as e:
        logger.error(f"{avatar.name} LLM response validation failed: {e}")
        return rule_based_decide(avatar)

    except Exception as e:
        logger.error(f"{avatar.name} LLM unexpected error: {e}", exc_info=True)
        return rule_based_decide(avatar)
```

#### 降级策略
1. **LLM 超时** → 规则 AI
2. **JSON 解析失败** → 规则 AI
3. **返回无效动作** → 规则 AI
4. **API 额度耗尽** → 全局切换到规则 AI，通知用户

### 6. 缓存优化

#### 提示词缓存
对于重复的上下文（如世界规则、角色性格描述），使用提示词缓存：

```python
# 使用 Anthropic 的提示词缓存（如果支持）
response = await client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "修仙世界规则...",  # 固定内容
            "cache_control": {"type": "ephemeral"}  # 标记为可缓存
        },
        {
            "type": "text",
            "text": f"你是 {avatar.name}..."  # 动态内容
        }
    ],
    messages=[...]
)
```

#### 决策结果缓存
对于类似情况，缓存决策结果（实验性）：

```python
def get_cached_decision(avatar: Avatar, context_hash: str) -> Optional[Action]:
    """获取缓存的决策"""
    # 如果上下文相似（如连续修炼），直接返回缓存
    cache_key = f"{avatar.id}:{context_hash}"
    return decision_cache.get(cache_key)
```

**注意**: 缓存会降低决策多样性，需要权衡。

## 权衡

### 优点
- ✅ 双层 AI 确保稳定性（LLM 失败不影响游戏）
- ✅ 觉醒率控制成本和性能
- ✅ 并发控制避免打爆 API
- ✅ 提示词工程确保决策质量
- ✅ 多模型支持灵活扩展
- ✅ 完善的错误处理和降级

### 缺点
- ❌ 提示词工程需要持续优化
- ❌ 低觉醒率下，部分 NPC 行为简单（但这是有意设计）
- ❌ LLM 调用有延迟（但通过异步并发缓解）

## 替代方案

### 方案 1: 纯 LLM（所有 NPC 都用 LLM）
- **优点**: 所有 NPC 都很智能
- **缺点**:
  - 成本高（100 个 NPC 每月调用 → 上千次）
  - 性能差（延迟高）
  - 不稳定（API 失败游戏就卡住）

**为什么不选**: 成本和性能无法接受。

### 方案 2: 纯规则 AI
- **优点**: 快、稳定、免费
- **缺点**: NPC 行为机械、可预测，缺乏创造力

**为什么不选**: 违背项目核心理念"AI 驱动的 NPC"。

### 方案 3: 混合队列（所有决策都排队，异步处理）
- **优点**: 更高的并发
- **缺点**: 决策延迟更高，游戏体验差

**为什么不选**: 实时性差。

## 后果

### 正面
- NPC 决策既智能又稳定
- 成本可控（通过觉醒率调节）
- LLM 失败时游戏不会中断
- 支持多种 LLM 提供商，用户可选择便宜的模型

### 负面
- 提示词工程需要持续优化
- 需要监控 LLM API 调用次数和成本

## 经验教训
- **觉醒率 1%** 是个不错的平衡点：既有智能决策，成本又可控
- **并发限制 10** 在 DeepSeek API 上表现良好
- **提示词越清晰，LLM 返回的 JSON 越规范**
- **强制 JSON 格式** 比让 LLM 自由输出可靠得多

## 未来优化方向
- [ ] 引入向量数据库，存储角色长期记忆
- [ ] 使用 Function Calling 替代 JSON 解析
- [ ] 尝试本地小模型（如 Llama 3.1）降低成本
- [ ] 引入决策树，减少 LLM 调用次数

## 相关决策
- [ADR-001: 选择 FastAPI](ADR-001-web-framework.md) (异步支持对 LLM 并发很重要)
- [ADR-005: 状态管理架构](ADR-005-state-management.md)

---

**创建时间**: 2026-02-01
**作者**: AI 团队
**审核**: ✅
