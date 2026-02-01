# 代码重构提示词模板

## 使用场景
当需要重构现有代码以提升质量、性能或可维护性时

## 提示词模板

```
我需要重构修仙世界模拟器中的代码：

## 重构目标
[要重构的模块/类/函数]

## 重构原因
- [ ] 代码重复
- [ ] 性能问题
- [ ] 可读性差
- [ ] 违反设计原则
- [ ] 难以测试
- [ ] 其他：[说明]

## 当前问题
[详细描述当前代码的问题]

## 期望改进
[重构后应该达到的目标]

## 约束
- [ ] 必须保持向后兼容
- [ ] 不能影响性能
- [ ] 必须有完整测试覆盖
- [ ] 其他：[说明]

## 请帮我：
1. 评估重构的风险和收益
2. 设计重构方案
3. 提供重构后的代码
4. 创建/更新测试用例
5. 提供迁移指南（如果有 API 变更）

## 上下文
- 当前代码位置：[文件路径]
- 依赖关系：[哪些地方调用了这段代码]
- 相关文档：[如果有]
```

## 示例：重构 Avatar 类

```
我需要重构修仙世界模拟器中的代码：

## 重构目标
`src/classes/avatar/avatar.py` 中的 Avatar 类

## 重构原因
- ✅ 代码重复：很多属性计算逻辑重复
- ✅ 可读性差：Avatar 类超过 1000 行，职责过多
- ✅ 难以测试：属性之间耦合严重
- ✅ 违反设计原则：违反单一职责原则

## 当前问题
1. Avatar 类包含太多职责：
   - 基础属性管理
   - 修炼逻辑
   - 战斗逻辑
   - 社交逻辑
   - AI 决策
   - 物品管理

2. 代码重复：
   - 战斗力计算在多处重复
   - 寿元检查逻辑散布在各处

3. 测试困难：
   - 创建一个可测试的 Avatar 需要初始化太多依赖

## 期望改进
1. 拆分 Avatar 为多个协作类：
   - `Avatar`: 只管理基础属性
   - `CultivationManager`: 管理修炼
   - `CombatManager`: 管理战斗
   - `SocialManager`: 管理社交
   - `InventoryManager`: 管理物品

2. 消除重复代码

3. 提升可测试性

## 约束
- ✅ 必须保持向后兼容（API 不能破坏）
- ✅ 不能影响性能
- ✅ 必须有完整测试覆盖
- ✅ 旧存档必须能加载

## 请帮我：
1. 评估重构的风险和收益
2. 设计类结构（类图）
3. 提供重构后的代码
4. 创建迁移测试（确保行为一致）
5. 提供重构步骤（分阶段进行）

## 上下文
- 当前代码：`src/classes/avatar/avatar.py` (约 1200 行)
- 依赖关系：几乎所有模块都依赖 Avatar
- 测试文件：`tests/test_avatar.py`
```

## 输出期望

### 1. 风险评估
```markdown
## 重构风险评估

### 高风险点
1. Avatar 被广泛依赖，改动影响范围大
2. 存档格式可能需要调整

### 低风险点
1. 内部实现重构，外部 API 可以保持不变
2. 有较好的测试覆盖

### 建议
采用 Strangler Fig 模式，逐步迁移功能，保持旧接口不变
```

### 2. 重构方案
```markdown
## 类结构设计

\```
┌──────────────────────────────────────┐
│           Avatar (Facade)            │
│  - id, name, age, realm              │
│  - cultivation: CultivationManager   │
│  - combat: CombatManager             │
│  - social: SocialManager             │
│  - inventory: InventoryManager       │
│                                      │
│  + 保持旧 API 兼容                    │
│  + 内部委托给各个 Manager              │
└──────────────────────────────────────┘
         │           │           │
         ▼           ▼           ▼
  Cultivation   Combat      Social
   Manager      Manager     Manager
\```

## 重构步骤（分 3 阶段）

### 阶段 1: 提取 Manager 类（不破坏兼容性）
1. 创建 CultivationManager
2. 将修炼逻辑移动到 CultivationManager
3. Avatar 内部使用 CultivationManager
4. 保持 Avatar 的公开 API 不变（通过委托）

### 阶段 2: 迁移其他功能
1. 提取 CombatManager
2. 提取 SocialManager
3. 提取 InventoryManager

### 阶段 3: 清理和优化
1. 移除重复代码
2. 统一接口
3. 更新文档
```

### 3. 重构代码示例
```python
# 展示关键部分的重构代码
```

### 4. 迁移测试
```python
# 确保重构后行为一致的测试
```

### 5. 迁移指南
```markdown
## 对开发者的影响

### 无影响（推荐用法）
\```python
# 旧代码仍然工作
avatar.cultivation_speed  # 仍然可用
avatar.calculate_battle_power()  # 仍然可用
\```

### 新的推荐用法
\```python
# 新代码可以使用更清晰的接口
avatar.cultivation.speed
avatar.combat.calculate_power()
\```

### 弃用警告
无。所有旧 API 保持兼容。
```
