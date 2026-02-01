# 开发工具目录 (Tools Directory)

本目录包含项目开发所需的各种工具和脚本。

## 🚀 核心工具

### 1. AI 开发助手 (ai_dev_assistant.py) ⭐ NEW

**用途**: 为 AI 开发者提供项目分析和文档生成功能

**功能**:
- 生成模块依赖图 (Mermaid/JSON)
- 提取所有 API 端点
- 分析代码变更影响
- 生成测试覆盖率报告
- 检查文档完整性
- 生成新人上手指南

**使用示例**:
```bash
# 查看帮助
python tools/ai_dev_assistant.py --help

# 生成依赖图
python tools/ai_dev_assistant.py deps --format mermaid --output docs/MODULE_MAP.md

# 提取 API 列表
python tools/ai_dev_assistant.py api-list --format json --output docs/api-endpoints.json

# 分析影响
python tools/ai_dev_assistant.py impact --file src/classes/avatar.py

# 检查测试覆盖率
python tools/ai_dev_assistant.py test-coverage --output docs/TEST_COVERAGE.md

# 检查文档
python tools/ai_dev_assistant.py doc-check --output docs/DOC_STATUS.md

# 生成上手指南
python tools/ai_dev_assistant.py onboarding --output docs/ONBOARDING.md
```

**详细文档**: [ai_dev_assistant_README.md](./ai_dev_assistant_README.md)

---

### 2. 代码生成器 (generate_*.py)

完整的代码生成工具链，支持快速创建符合规范的代码文件。

- **generate_action.py**: 生成新动作类的样板代码
- **generate_api.py**: 生成 API 文档
- **generate_component.py**: 生成 Vue 组件样板代码

**详细文档**: 参见本目录下的 [代码生成工具使用指南](#代码生成工具使用指南)

---

### 3. 国际化工具 (i18n/)

处理多语言翻译和本地化

---

### 4. 图片生成工具 (img_gen/, img_gemini/)

生成游戏资源图片

---

### 5. 地图创建工具 (map_creator/)

创建和编辑游戏地图

---

### 6. 打包工具 (package/)

构建和打包应用

---

### 7. 资源处理 (process_assets.py)

处理和优化游戏资源

---

### 8. 数据提取 (extract/)

从各种源提取数据

---

## 📁 工具库 (lib/)

提供可复用的工具模块：

- `ast_utils.py`: AST 解析工具（提取类名、函数名、导入等）
- `file_utils.py`: 文件操作工具（查找文件、读取文件等）

**使用示例**:
```python
from tools.lib.ast_utils import extract_class_names
from tools.lib.file_utils import find_python_files

# 查找所有 Python 文件
files = find_python_files(Path('src'))

# 提取类名
for file in files:
    classes = extract_class_names(file)
    print(f"{file}: {classes}")
```

---

## 📂 目录结构

```
tools/
├── ai_dev_assistant.py       # AI 开发助手 (新)
├── ai_dev_assistant_README.md # 详细文档
├── test_ai_dev_assistant.py   # 测试脚本
├── lib/                      # 工具库 (新)
│   ├── __init__.py
│   ├── ast_utils.py          # AST 解析
│   └── file_utils.py         # 文件工具
├── extract/                  # 数据提取工具
├── generate_action.py        # 生成动作代码
├── generate_api.py           # 生成 API 文档
├── generate_component.py     # 生成组件代码
├── i18n/                     # 国际化工具
├── img_gemini/               # Gemini 图片生成
├── img_gen/                  # 图片生成工具
├── map_creator/              # 地图创建工具
├── package/                  # 打包脚本
└── process_assets.py         # 资源处理
```

---

## 🎯 快速开始

### 方式 1: 运行 AI 开发助手

```bash
# 生成完整的项目分析报告
python tools/ai_dev_assistant.py deps --output docs/MODULE_DEPS.md
python tools/ai_dev_assistant.py api-list --output docs/API_LIST.json
python tools/ai_dev_assistant.py test-coverage --output docs/COVERAGE.md
python tools/ai_dev_assistant.py doc-check --output docs/DOC_CHECK.md
python tools/ai_dev_assistant.py onboarding --output docs/ONBOARDING.md
```

### 方式 2: 生成代码

```bash
# 生成新动作类
python tools/generate_action.py MyAction --type instant --emoji ⚡

# 生成 Vue 组件
python tools/generate_component.py MyComponent --props "title:string"

# 生成 API 端点
python tools/generate_api.py my_endpoint --full-crud
```

### 方式 3: 运行测试

```bash
# 测试 AI 开发助手工具
python tools/test_ai_dev_assistant.py
```

---

## 📚 工具对比

| 工具 | 用途 | 输出格式 | 适用场景 |
|------|------|---------|---------|
| `ai_dev_assistant.py` | 项目分析 | Markdown/JSON | 理解项目、生成文档、代码审查 |
| `generate_action.py` | 代码生成 | Python 文件 | 快速创建新动作类 |
| `generate_api.py` | API 生成 | Python 文件 | 快速创建 API 端点 |
| `generate_component.py` | 组件生成 | Vue 文件 | 快速创建 UI 组件 |

---

## 🔗 相关文档

- [AI 开发助手详细文档](./ai_dev_assistant_README.md)
- [编码规范](../.ai/conventions.md)
- [项目快速上下文](../.ai/context.md)
- [架构文档](../docs/ARCHITECTURE.md)

---

## 🤝 贡献

欢迎贡献新的工具和模板！

贡献步骤:
1. Fork 本项目
2. 创建功能分支: `git checkout -b feature/new-tool`
3. 提交更改: `git commit -m "feat(tools): add new tool"`
4. 推送分支: `git push origin feature/new-tool`
5. 创建 Pull Request

---

## 📝 更新日志

### 2026-02-01
- ✨ 新增 AI 开发助手工具 (`ai_dev_assistant.py`)
- ✨ 新增工具库 (`lib/`)
- ✨ 新增自动化测试脚本 (`test_ai_dev_assistant.py`)
- 📝 更新工具文档

---

**最后更新**: 2026-02-01
**维护者**: AI Development Team
