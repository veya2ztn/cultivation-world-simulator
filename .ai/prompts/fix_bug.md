# 修复 Bug 提示词模板

## 使用场景
当发现 Bug 需要修复时

## 提示词模板

```
我在修仙世界模拟器中发现了一个 Bug：

## Bug 描述
[清晰描述 Bug 的表现]

## 复现步骤
1. [步骤 1]
2. [步骤 2]
3. [观察到的错误行为]

## 期望行为
[应该发生什么]

## 错误信息（如果有）
\```
[错误堆栈、日志等]
\```

## 环境信息
- Python 版本: [版本]
- 浏览器: [如果是前端问题]
- 存档文件: [如果与特定存档相关]

## 可能的原因（如果有猜测）
[你的初步分析]

## 请帮我：
1. 分析 Bug 的根本原因
2. 定位到具体的代码位置
3. 提供修复方案（含代码）
4. 编写回归测试，防止再次出现
5. 评估修复的影响范围

## 上下文
- 项目结构：参考 `.ai/context.md`
- 相关代码：[如果知道大概位置]
```

## 示例：修复"NPC 修炼速度异常"

```
我在修仙世界模拟器中发现了一个 Bug：

## Bug 描述
某些 NPC 的修炼速度突然变成负数，导致修为倒退

## 复现步骤
1. 启动游戏，等待 10 个游戏年
2. 查看某个炼气期 NPC 的修为进度
3. 发现修为从 500 降到 480

## 期望行为
修为应该持续增长（或至少不会倒退）

## 错误信息
控制台输出：
\```
[Warning] Avatar 张三 cultivation speed: -5.2
[Warning] Negative cultivation detected, clamping to 0
\```

## 环境信息
- Python 版本: 3.12
- 发生时机: 游戏运行约 10 年后
- 存档文件: save_20260201.json

## 可能的原因
怀疑是天地灵气变动导致的计算错误，或者是境界突破失败后的副作用计算有问题

## 请帮我：
1. 分析 Bug 的根本原因
2. 定位到具体的代码位置
3. 提供修复方案
4. 编写测试防止复发
5. 检查是否有类似问题

## 上下文
- 项目结构：参考 `.ai/context.md`
- 相关代码：可能在 `src/classes/cultivation.py` 或 `src/classes/action/cultivate.py`
```

## 输出期望

### 1. 根因分析
```markdown
## Bug 根本原因
在 `src/classes/action/cultivate.py:142` 中，当天地灵气为负时（罕见但可能），
修炼速度计算没有做下限保护：

\```python
# 问题代码
cultivation_speed = base_speed * spiritual_qi_multiplier  # 可能为负
\```

## 触发条件
- 天地灵机为"灭世之兆"（灵气倍率 -0.5）
- 角色在灵气贫瘠区域（灵气倍率 0.5）
- 两者相乘：base_speed * (-0.5) * 0.5 = 负数
```

### 2. 修复方案
```python
# 修复后的代码
cultivation_speed = max(0, base_speed * spiritual_qi_multiplier)
# 确保修炼速度永远不为负
```

### 3. 回归测试
```python
def test_cultivation_speed_never_negative():
    """测试极端情况下修炼速度不为负"""
    # Given: 灭世之兆 + 贫瘠区域
    phenomenon = CelestialPhenomenon(qi_multiplier=-0.5)
    region = Region(qi_multiplier=0.5)

    # When: 计算修炼速度
    speed = calculate_cultivation_speed(
        base_speed=10,
        phenomenon=phenomenon,
        region=region
    )

    # Then: 应该被钳制到 0
    assert speed >= 0
```

### 4. 影响评估
```markdown
## 影响范围
- 只影响计算逻辑，不影响数据结构
- 不需要迁移旧存档
- 建议检查其他速度计算是否有类似问题（如战斗力、移动速度）
```
