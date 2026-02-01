#!/usr/bin/env python3
"""
AI 开发助手工具 (AI Development Assistant)

为 AI 开发者提供项目上下文和分析功能的命令行工具。

功能：
1. 生成模块依赖图 (Mermaid 格式)
2. 提取所有 API 端点
3. 分析代码变更影响
4. 生成测试覆盖率报告
5. 检查文档完整性
6. 生成新人上手指南

使用示例：
    python tools/ai_dev_assistant.py deps --format mermaid
    python tools/ai_dev_assistant.py api-list
    python tools/ai_dev_assistant.py impact --file src/classes/avatar.py
    python tools/ai_dev_assistant.py test-coverage
    python tools/ai_dev_assistant.py doc-check
    python tools/ai_dev_assistant.py onboarding

作者: AI Development Team
版本: 1.0.0
"""

import argparse
import ast
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class ImportInfo:
    """导入信息"""
    module: str  # 导入的模块名
    source_file: str  # 导入发生的源文件
    line_number: int  # 行号


@dataclass
class APIEndpoint:
    """API 端点信息"""
    path: str
    method: str
    function_name: str
    line_number: int
    docstring: Optional[str] = None


@dataclass
class ModuleInfo:
    """模块信息"""
    path: Path
    imports: List[ImportInfo]
    exports: Set[str]
    has_tests: bool = False
    has_readme: bool = False
    has_docstrings: bool = False


class ProgressIndicator:
    """简单的进度指示器"""

    def __init__(self, total: int, prefix: str = "Processing"):
        self.total = total
        self.current = 0
        self.prefix = prefix

    def update(self, increment: int = 1):
        """更新进度"""
        self.current += increment
        percent = (self.current / self.total) * 100 if self.total > 0 else 100
        bar_length = 40
        filled = int(bar_length * self.current / self.total) if self.total > 0 else bar_length
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f'\r{self.prefix}: [{bar}] {percent:.1f}% ({self.current}/{self.total})', end='', flush=True)

    def finish(self):
        """完成进度"""
        print()  # 换行


class DependencyAnalyzer:
    """依赖分析器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.modules: Dict[str, ModuleInfo] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)

    def analyze(self):
        """分析所有 Python 文件的依赖"""
        python_files = list(self.src_dir.rglob("*.py"))
        progress = ProgressIndicator(len(python_files), "分析依赖")

        for file_path in python_files:
            if "__pycache__" in str(file_path):
                continue

            try:
                imports = self._extract_imports(file_path)
                module_name = self._get_module_name(file_path)

                self.modules[module_name] = ModuleInfo(
                    path=file_path,
                    imports=imports,
                    exports=self._extract_exports(file_path)
                )

                # 构建依赖关系
                for imp in imports:
                    if imp.module.startswith("src."):
                        self.dependencies[module_name].add(imp.module)

                progress.update()
            except Exception as e:
                print(f"\n警告: 解析 {file_path} 失败: {e}")
                progress.update()

        progress.finish()
        return self.dependencies

    def _get_module_name(self, file_path: Path) -> str:
        """获取模块名称"""
        relative = file_path.relative_to(self.project_root)
        parts = relative.parts
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        else:
            parts = parts[:-1] + (parts[-1].replace(".py", ""),)
        return ".".join(parts)

    def _extract_imports(self, file_path: Path) -> List[ImportInfo]:
        """提取文件中的导入语句"""
        imports = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(ImportInfo(
                            module=alias.name,
                            source_file=str(file_path),
                            line_number=node.lineno
                        ))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(ImportInfo(
                            module=node.module,
                            source_file=str(file_path),
                            line_number=node.lineno
                        ))
        except Exception as e:
            # 静默处理语法错误
            pass

        return imports

    def _extract_exports(self, file_path: Path) -> Set[str]:
        """提取模块导出的类和函数"""
        exports = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith('_'):
                        exports.add(node.name)
        except Exception:
            pass

        return exports

    def find_circular_dependencies(self) -> List[List[str]]:
        """查找循环依赖"""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(module: str, path: List[str]):
            visited.add(module)
            rec_stack.add(module)
            path.append(module)

            for dep in self.dependencies.get(module, []):
                if dep not in visited:
                    dfs(dep, path.copy())
                elif dep in rec_stack:
                    # 找到循环
                    cycle_start = path.index(dep)
                    cycle = path[cycle_start:] + [dep]
                    if cycle not in cycles:
                        cycles.append(cycle)

            rec_stack.remove(module)

        for module in self.dependencies:
            if module not in visited:
                dfs(module, [])

        return cycles

    def generate_mermaid(self, max_depth: int = 2) -> str:
        """生成 Mermaid 格式的依赖图"""
        lines = ["```mermaid", "graph TD"]

        # 只显示核心模块
        core_modules = {
            "src.server.main",
            "src.sim.simulator",
            "src.classes.world",
            "src.classes.avatar",
            "src.classes.action",
            "src.utils.llm.client"
        }

        processed = set()

        for module in core_modules:
            if module in self.dependencies:
                short_name = self._shorten_module_name(module)
                lines.append(f'    {self._safe_id(module)}["{short_name}"]')
                processed.add(module)

                for dep in self.dependencies[module]:
                    if dep.startswith("src."):
                        dep_short = self._shorten_module_name(dep)
                        if dep not in processed:
                            lines.append(f'    {self._safe_id(dep)}["{dep_short}"]')
                            processed.add(dep)
                        lines.append(f'    {self._safe_id(module)} --> {self._safe_id(dep)}')

        lines.append("```")
        return "\n".join(lines)

    def _shorten_module_name(self, module: str) -> str:
        """缩短模块名"""
        parts = module.split(".")
        if len(parts) > 2:
            return f"{parts[1]}.{parts[-1]}"
        return module

    def _safe_id(self, module: str) -> str:
        """生成安全的 Mermaid ID"""
        return module.replace(".", "_").replace("-", "_")


class APIExtractor:
    """API 端点提取器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.main_file = project_root / "src" / "server" / "main.py"

    def extract_endpoints(self) -> List[APIEndpoint]:
        """提取所有 API 端点"""
        endpoints = []

        if not self.main_file.exists():
            print(f"错误: 找不到 {self.main_file}")
            return endpoints

        with open(self.main_file, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content, filename=str(self.main_file))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 检查装饰器
                for decorator in node.decorator_list:
                    endpoint = self._parse_decorator(decorator, node)
                    if endpoint:
                        endpoints.append(endpoint)

        return endpoints

    def _parse_decorator(self, decorator, function_node) -> Optional[APIEndpoint]:
        """解析装饰器获取 API 信息"""
        method = None
        path = None

        # @app.get("/path")
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                method = decorator.func.attr.upper()
                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                    path = decorator.args[0].value

        # @app.websocket("/ws")
        elif isinstance(decorator, ast.Attribute):
            if decorator.attr == "websocket":
                method = "WS"

        if method and path:
            docstring = ast.get_docstring(function_node)
            return APIEndpoint(
                path=path,
                method=method,
                function_name=function_node.name,
                line_number=function_node.lineno,
                docstring=docstring
            )

        return None

    def generate_json(self, endpoints: List[APIEndpoint]) -> str:
        """生成 JSON 格式的 API 列表"""
        data = []
        for ep in sorted(endpoints, key=lambda x: x.path):
            data.append({
                "path": ep.path,
                "method": ep.method,
                "function": ep.function_name,
                "line": ep.line_number,
                "description": ep.docstring.split('\n')[0] if ep.docstring else None
            })
        return json.dumps(data, indent=2, ensure_ascii=False)

    def generate_markdown(self, endpoints: List[APIEndpoint]) -> str:
        """生成 Markdown 格式的 API 列表"""
        lines = ["# API 端点列表", ""]

        # 按方法分组
        by_method = defaultdict(list)
        for ep in endpoints:
            by_method[ep.method].append(ep)

        for method in ["GET", "POST", "DELETE", "WS"]:
            if method in by_method:
                lines.append(f"## {method} 请求")
                lines.append("")

                for ep in sorted(by_method[method], key=lambda x: x.path):
                    lines.append(f"### `{ep.path}`")
                    lines.append("")
                    lines.append(f"- **函数**: `{ep.function_name}`")
                    lines.append(f"- **位置**: `main.py:{ep.line_number}`")
                    if ep.docstring:
                        lines.append(f"- **说明**: {ep.docstring.split(chr(10))[0]}")
                    lines.append("")

        return "\n".join(lines)


class ImpactAnalyzer:
    """变更影响分析器"""

    def __init__(self, dependency_analyzer: DependencyAnalyzer):
        self.analyzer = dependency_analyzer

    def analyze_impact(self, changed_file: str) -> Set[str]:
        """分析文件变更的影响范围"""
        changed_file_path = Path(changed_file)

        # 转换为模块名
        if changed_file_path.is_absolute():
            try:
                module_name = self.analyzer._get_module_name(changed_file_path)
            except ValueError:
                print(f"错误: {changed_file} 不在项目中")
                return set()
        else:
            # 相对路径，尝试找到对应模块
            module_name = changed_file.replace("/", ".").replace("\\", ".").replace(".py", "")

        # 找到所有依赖这个模块的模块
        affected = set()

        def find_dependents(module: str):
            for mod, deps in self.analyzer.dependencies.items():
                if module in deps and mod not in affected:
                    affected.add(mod)
                    find_dependents(mod)

        find_dependents(module_name)
        affected.add(module_name)

        return affected


class TestCoverageChecker:
    """测试覆盖率检查器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.tests_dir = project_root / "tests"

    def check_coverage(self) -> Dict[str, bool]:
        """检查测试覆盖率"""
        coverage = {}

        # 获取所有源文件
        src_files = [f for f in self.src_dir.rglob("*.py") if "__pycache__" not in str(f)]

        progress = ProgressIndicator(len(src_files), "检查测试覆盖")

        for src_file in src_files:
            # 跳过 __init__.py
            if src_file.name == "__init__.py":
                progress.update()
                continue

            # 查找对应的测试文件
            relative_path = src_file.relative_to(self.src_dir)
            test_file_name = f"test_{src_file.stem}.py"

            # 可能的测试文件位置
            possible_test_files = [
                self.tests_dir / test_file_name,
                self.tests_dir / relative_path.parent / test_file_name
            ]

            has_test = any(tf.exists() for tf in possible_test_files)
            coverage[str(relative_path)] = has_test

            progress.update()

        progress.finish()
        return coverage

    def generate_report(self, coverage: Dict[str, bool]) -> str:
        """生成覆盖率报告"""
        total = len(coverage)
        covered = sum(1 for has_test in coverage.values() if has_test)
        uncovered = total - covered
        percentage = (covered / total * 100) if total > 0 else 0

        lines = [
            "# 测试覆盖率报告",
            "",
            f"**总计**: {total} 个模块",
            f"**已覆盖**: {covered} 个 ({percentage:.1f}%)",
            f"**未覆盖**: {uncovered} 个",
            "",
            "## 缺少测试的模块",
            ""
        ]

        for module, has_test in sorted(coverage.items()):
            if not has_test:
                lines.append(f"- `{module}`")

        return "\n".join(lines)


class DocChecker:
    """文档完整性检查器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"

    def check_documentation(self) -> Dict[str, Dict]:
        """检查文档完整性"""
        results = {}
        python_files = [f for f in self.src_dir.rglob("*.py") if "__pycache__" not in str(f)]

        progress = ProgressIndicator(len(python_files), "检查文档")

        for file_path in python_files:
            results[str(file_path.relative_to(self.project_root))] = self._check_file(file_path)
            progress.update()

        progress.finish()
        return results

    def _check_file(self, file_path: Path) -> Dict:
        """检查单个文件的文档"""
        result = {
            "has_module_docstring": False,
            "classes_without_docstring": [],
            "functions_without_docstring": [],
            "functions_without_type_hints": []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))

            # 检查模块 docstring
            result["has_module_docstring"] = ast.get_docstring(tree) is not None

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if not ast.get_docstring(node):
                        result["classes_without_docstring"].append(node.name)

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # 跳过私有函数
                    if node.name.startswith('_') and not node.name.startswith('__'):
                        continue

                    if not ast.get_docstring(node):
                        result["functions_without_docstring"].append(node.name)

                    # 检查类型注解
                    if not node.returns or not all(arg.annotation for arg in node.args.args if arg.arg != 'self'):
                        result["functions_without_type_hints"].append(node.name)

        except Exception:
            pass

        return result

    def generate_report(self, results: Dict[str, Dict]) -> str:
        """生成文档检查报告"""
        lines = ["# 文档完整性检查报告", ""]

        # 统计
        total_files = len(results)
        files_with_module_doc = sum(1 for r in results.values() if r["has_module_docstring"])
        total_undocumented_classes = sum(len(r["classes_without_docstring"]) for r in results.values())
        total_undocumented_functions = sum(len(r["functions_without_docstring"]) for r in results.values())

        lines.extend([
            "## 统计",
            "",
            f"- 总文件数: {total_files}",
            f"- 有模块 docstring: {files_with_module_doc} ({files_with_module_doc/total_files*100:.1f}%)",
            f"- 缺少 docstring 的类: {total_undocumented_classes}",
            f"- 缺少 docstring 的函数: {total_undocumented_functions}",
            "",
            "## 详细报告",
            ""
        ])

        for file_path, result in sorted(results.items()):
            issues = []
            if not result["has_module_docstring"]:
                issues.append("缺少模块 docstring")
            if result["classes_without_docstring"]:
                issues.append(f"{len(result['classes_without_docstring'])} 个类缺少 docstring")
            if result["functions_without_docstring"]:
                issues.append(f"{len(result['functions_without_docstring'])} 个函数缺少 docstring")

            if issues:
                lines.append(f"### `{file_path}`")
                lines.append("")
                for issue in issues:
                    lines.append(f"- {issue}")
                lines.append("")

        return "\n".join(lines)


class OnboardingGenerator:
    """新人上手指南生成器"""

    def __init__(self, project_root: Path, dependency_analyzer: DependencyAnalyzer):
        self.project_root = project_root
        self.analyzer = dependency_analyzer

    def generate_guide(self) -> str:
        """生成上手指南"""
        lines = [
            "# 新人上手指南",
            "",
            "## 项目概览",
            "",
            "修仙世界模拟器是一个 AI 驱动的修仙世界模拟游戏。",
            "",
            "## 核心文件（按重要性排序）",
            ""
        ]

        # 定义核心文件及其说明
        core_files = [
            ("src/server/main.py", "FastAPI 服务器主文件，包含所有 API 端点和游戏循环"),
            ("src/sim/simulator.py", "游戏模拟器核心，控制游戏推进"),
            ("src/classes/world.py", "世界类，管理游戏世界状态"),
            ("src/classes/avatar/core.py", "角色核心类"),
            ("src/classes/action/action.py", "动作系统基类"),
            ("src/utils/llm/client.py", "LLM 客户端封装"),
        ]

        for file_path, description in core_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                lines.append(f"### `{file_path}`")
                lines.append("")
                lines.append(description)
                lines.append("")

                # 添加文件统计
                with open(full_path, 'r', encoding='utf-8') as f:
                    line_count = len(f.readlines())
                lines.append(f"- 代码行数: ~{line_count}")
                lines.append("")

        lines.extend([
            "## 学习路径建议",
            "",
            "### 第 1 天：熟悉项目结构",
            "",
            "1. 阅读 `README.md` 了解项目背景",
            "2. 阅读 `.ai/context.md` 了解快速上下文",
            "3. 运行项目，体验游戏",
            "",
            "### 第 2-3 天：理解核心流程",
            "",
            "1. 阅读 `src/server/main.py` 理解服务器启动流程",
            "2. 阅读 `src/sim/simulator.py` 理解游戏循环",
            "3. 调试一个完整的游戏 tick，观察数据流",
            "",
            "### 第 4-5 天：深入业务逻辑",
            "",
            "1. 阅读 `src/classes/avatar/` 理解角色系统",
            "2. 阅读 `src/classes/action/` 理解动作系统",
            "3. 尝试添加一个简单的动作",
            "",
            "### 第 6-7 天：掌握 AI 系统",
            "",
            "1. 阅读 `src/utils/llm/` 理解 LLM 集成",
            "2. 阅读 `src/classes/ai.py` 理解 AI 决策",
            "3. 尝试优化 AI 提示词",
            "",
            "## 常见任务",
            "",
            "### 添加新的 API 端点",
            "",
            "在 `src/server/main.py` 中添加新的路由函数：",
            "",
            "```python",
            "@app.get('/api/your-endpoint')",
            "def your_endpoint():",
            '    """你的端点说明"""',
            "    return {'status': 'ok'}",
            "```",
            "",
            "### 添加新的动作",
            "",
            "1. 在 `src/classes/action/` 创建新文件",
            "2. 继承 `Action` 基类",
            "3. 在 `src/classes/actions.py` 注册",
            "",
            "### 运行测试",
            "",
            "```bash",
            "pytest",
            "pytest --cov=src  # 带覆盖率",
            "```",
            "",
            "## 开发工具",
            "",
            "- 本工具: `python tools/ai_dev_assistant.py --help`",
            "- API 文档生成: `python tools/generate_api.py`",
            "- 代码生成工具: `tools/generate_*.py`",
            "",
            "## 获取帮助",
            "",
            "- 查看 `docs/` 目录下的详细文档",
            "- 提交 GitHub Issue",
            "- 查看测试文件了解使用示例",
            ""
        ])

        return "\n".join(lines)


def main():
    """主函数"""
    # 修复 Windows 控制台编码问题
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="AI 开发助手工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python tools/ai_dev_assistant.py deps --format mermaid
  python tools/ai_dev_assistant.py api-list --output docs/api.json
  python tools/ai_dev_assistant.py impact --file src/classes/avatar.py
  python tools/ai_dev_assistant.py test-coverage
  python tools/ai_dev_assistant.py doc-check
  python tools/ai_dev_assistant.py onboarding --output docs/ONBOARDING.md
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # deps 命令
    deps_parser = subparsers.add_parser("deps", help="生成模块依赖图")
    deps_parser.add_argument("--format", choices=["mermaid", "json"], default="mermaid", help="输出格式")
    deps_parser.add_argument("--output", "-o", help="输出文件路径")

    # api-list 命令
    api_parser = subparsers.add_parser("api-list", help="提取所有 API 端点")
    api_parser.add_argument("--format", choices=["json", "markdown"], default="json", help="输出格式")
    api_parser.add_argument("--output", "-o", help="输出文件路径")

    # impact 命令
    impact_parser = subparsers.add_parser("impact", help="分析代码变更影响")
    impact_parser.add_argument("--file", "-f", required=True, help="修改的文件路径")

    # test-coverage 命令
    test_parser = subparsers.add_parser("test-coverage", help="生成测试覆盖率报告")
    test_parser.add_argument("--output", "-o", help="输出文件路径")

    # doc-check 命令
    doc_parser = subparsers.add_parser("doc-check", help="检查文档完整性")
    doc_parser.add_argument("--output", "-o", help="输出文件路径")

    # onboarding 命令
    onboarding_parser = subparsers.add_parser("onboarding", help="生成新人上手指南")
    onboarding_parser.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        # 执行命令
        if args.command == "deps":
            print("正在分析模块依赖...")
            analyzer = DependencyAnalyzer(PROJECT_ROOT)
            deps = analyzer.analyze()

            # 检查循环依赖
            cycles = analyzer.find_circular_dependencies()
            if cycles:
                print(f"\n[警告] 发现 {len(cycles)} 个循环依赖:")
                for cycle in cycles:
                    print(f"  - {' -> '.join(cycle)}")
            else:
                print("\n[OK] 未发现循环依赖")

            # 生成输出
            if args.format == "mermaid":
                output = analyzer.generate_mermaid()
            else:
                output = json.dumps({k: list(v) for k, v in deps.items()}, indent=2)

            if args.output:
                Path(args.output).write_text(output, encoding='utf-8')
                print(f"\n[OK] 依赖图已保存到 {args.output}")
            else:
                print("\n" + output)

        elif args.command == "api-list":
            print("正在提取 API 端点...")
            extractor = APIExtractor(PROJECT_ROOT)
            endpoints = extractor.extract_endpoints()

            print(f"\n[OK] 找到 {len(endpoints)} 个 API 端点")

            if args.format == "json":
                output = extractor.generate_json(endpoints)
            else:
                output = extractor.generate_markdown(endpoints)

            if args.output:
                Path(args.output).write_text(output, encoding='utf-8')
                print(f"[OK] API 列表已保存到 {args.output}")
            else:
                print("\n" + output)

        elif args.command == "impact":
            print("正在分析影响范围...")
            analyzer = DependencyAnalyzer(PROJECT_ROOT)
            analyzer.analyze()

            impact_analyzer = ImpactAnalyzer(analyzer)
            affected = impact_analyzer.analyze_impact(args.file)

            print(f"\n文件 {args.file} 的变更会影响以下 {len(affected)} 个模块:")
            for module in sorted(affected):
                print(f"  - {module}")

        elif args.command == "test-coverage":
            print("正在检查测试覆盖率...")
            checker = TestCoverageChecker(PROJECT_ROOT)
            coverage = checker.check_coverage()
            report = checker.generate_report(coverage)

            if args.output:
                Path(args.output).write_text(report, encoding='utf-8')
                print(f"\n[OK] 测试覆盖率报告已保存到 {args.output}")
            else:
                print("\n" + report)

        elif args.command == "doc-check":
            print("正在检查文档完整性...")
            checker = DocChecker(PROJECT_ROOT)
            results = checker.check_documentation()
            report = checker.generate_report(results)

            if args.output:
                Path(args.output).write_text(report, encoding='utf-8')
                print(f"\n[OK] 文档检查报告已保存到 {args.output}")
            else:
                print("\n" + report)

        elif args.command == "onboarding":
            print("正在生成新人上手指南...")
            analyzer = DependencyAnalyzer(PROJECT_ROOT)
            analyzer.analyze()

            generator = OnboardingGenerator(PROJECT_ROOT, analyzer)
            guide = generator.generate_guide()

            if args.output:
                Path(args.output).write_text(guide, encoding='utf-8')
                print(f"\n[OK] 上手指南已保存到 {args.output}")
            else:
                print("\n" + guide)

        return 0

    except KeyboardInterrupt:
        print("\n\n已取消")
        return 1
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
