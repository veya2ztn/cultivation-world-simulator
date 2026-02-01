# 添加新功能提示词模板

## 使用场景
当需要添加一个新功能时（如新的角色动作、新的游戏机制等）

## 提示词模板

```
我需要在修仙世界模拟器中添加一个新功能：[功能名称]

## 功能描述
[详细描述新功能的作用、触发条件、效果等]

## 需求分析
1. 涉及的游戏实体：[角色/宗门/物品等]
2. 数据结构变更：[是否需要新增属性/类]
3. 前端展示：[是否需要 UI 变更]
4. LLM 集成：[是否需要 AI 决策]

## 请帮我：
1. 分析这个功能需要修改哪些文件
2. 设计数据结构（Python 类定义）
3. 编写实现代码（包含完整的 docstring 和类型注解）
4. 创建对应的测试用例
5. 更新相关文档

## 上下文
- 项目结构：参考 `.ai/context.md`
- 编码规范：参考 `.ai/conventions.md`
- 类似功能参考：[如果有类似功能，指出位置]

## 约束
- 保持代码风格一致
- 确保向后兼容（旧存档能加载）
- 性能要求：[如果有]
```

## 示例：添加"炼丹"功能

```
我需要在修仙世界模拟器中添加一个新功能：炼丹系统

## 功能描述
- 角色可以通过消耗灵药和灵石来炼制丹药
- 炼丹需要一定的炼丹技能等级
- 炼丹可能成功或失败（根据技能等级和丹药品级）
- 成功后获得丹药，可以服用提升修为或出售

## 需求分析
1. 涉及的游戏实体：角色、物品（灵药、灵石、丹药）
2. 数据结构变更：
   - 需要新增 AlchemySkill 类（炼丹技能）
   - 需要新增 Elixir 类（已存在，可能需扩展）
   - 需要新增 AlchemyRecipe 类（丹方）
3. 前端展示：需要炼丹界面，显示配方、材料、成功率
4. LLM 集成：角色决定何时炼丹（如缺少丹药时）

## 请帮我：
1. 分析这个功能需要修改哪些文件
2. 设计数据结构（AlchemySkill, AlchemyRecipe 等）
3. 编写炼丹动作类（AlchemyAction）
4. 创建炼丹 API 端点
5. 创建前端炼丹面板组件
6. 编写测试用例
7. 更新文档

## 上下文
- 项目结构：参考 `.ai/context.md`
- 编码规范：参考 `.ai/conventions.md`
- 类似功能参考：`src/classes/action/forge.py`（铸造系统，逻辑相似）

## 约束
- 保持与现有物品系统兼容
- 确保炼丹不会破坏游戏平衡
- 性能要求：炼丹是长动作，不影响主循环性能
```

## 输出期望

AI 应该返回：

### 1. 影响分析
```
## 影响的文件
### 新增文件
- src/classes/alchemy_skill.py
- src/classes/alchemy_recipe.py
- src/classes/action/alchemy.py
- web/src/components/panels/AlchemyPanel.vue
- tests/test_alchemy.py

### 修改文件
- src/classes/avatar/avatar.py (添加 alchemy_skill 属性)
- src/classes/actions.py (注册 AlchemyAction)
- src/server/main.py (添加炼丹 API)
- static/recipes.csv (炼丹配方数据)

### 需要更新的文档
- docs/ARCHITECTURE.md (添加炼丹系统说明)
- docs/COMMON_TASKS.md (添加"如何添加新配方"任务)
```

### 2. 数据结构设计
```python
# 完整的类定义，带 docstring 和类型注解
```

### 3. 实现代码
```python
# 可以直接使用的代码
```

### 4. 测试用例
```python
# 完整的测试代码
```

### 5. 文档更新
```markdown
# 更新的文档内容
```
