#!/usr/bin/env python3
"""
AI 开发助手工具测试脚本

快速验证工具的所有功能是否正常工作。
"""

import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

def run_command(cmd: list, description: str) -> bool:
    """运行命令并检查结果"""
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:
            print(f"[OK] {description} 成功")
            return True
        else:
            print(f"[FAIL] {description} 失败")
            print(f"错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] {description} 执行异常: {e}")
        return False


def main():
    """运行所有测试"""
    print("开始测试 AI 开发助手工具...")

    tests = [
        # 测试 1: 显示帮助
        (
            ["python", "tools/ai_dev_assistant.py", "--help"],
            "显示帮助信息"
        ),

        # 测试 2: 生成依赖图 (Mermaid)
        (
            ["python", "tools/ai_dev_assistant.py", "deps", "--format", "mermaid",
             "--output", "docs/test_deps.md"],
            "生成 Mermaid 依赖图"
        ),

        # 测试 3: 生成依赖图 (JSON)
        (
            ["python", "tools/ai_dev_assistant.py", "deps", "--format", "json",
             "--output", "docs/test_deps.json"],
            "生成 JSON 依赖图"
        ),

        # 测试 4: 提取 API 列表 (JSON)
        (
            ["python", "tools/ai_dev_assistant.py", "api-list", "--format", "json",
             "--output", "docs/test_api.json"],
            "提取 API 端点 (JSON)"
        ),

        # 测试 5: 提取 API 列表 (Markdown)
        (
            ["python", "tools/ai_dev_assistant.py", "api-list", "--format", "markdown",
             "--output", "docs/test_api.md"],
            "提取 API 端点 (Markdown)"
        ),

        # 测试 6: 分析变更影响
        (
            ["python", "tools/ai_dev_assistant.py", "impact", "--file", "src/classes/world.py"],
            "分析代码变更影响"
        ),

        # 测试 7: 检查测试覆盖率
        (
            ["python", "tools/ai_dev_assistant.py", "test-coverage",
             "--output", "docs/test_coverage.md"],
            "生成测试覆盖率报告"
        ),

        # 测试 8: 检查文档完整性
        (
            ["python", "tools/ai_dev_assistant.py", "doc-check",
             "--output", "docs/test_doc_check.md"],
            "检查文档完整性"
        ),

        # 测试 9: 生成新人上手指南
        (
            ["python", "tools/ai_dev_assistant.py", "onboarding",
             "--output", "docs/test_onboarding.md"],
            "生成新人上手指南"
        ),
    ]

    results = []
    for cmd, desc in tests:
        success = run_command(cmd, desc)
        results.append((desc, success))

    # 打印总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for desc, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {desc}")

    print(f"\n总计: {passed}/{total} 通过")

    # 清理测试文件
    print(f"\n{'='*60}")
    print("清理测试文件...")
    print(f"{'='*60}")

    test_files = [
        "docs/test_deps.md",
        "docs/test_deps.json",
        "docs/test_api.json",
        "docs/test_api.md",
        "docs/test_coverage.md",
        "docs/test_doc_check.md",
        "docs/test_onboarding.md",
    ]

    for file in test_files:
        file_path = PROJECT_ROOT / file
        if file_path.exists():
            file_path.unlink()
            print(f"[OK] 删除 {file}")

    # 返回退出码
    if passed == total:
        print("\n所有测试通过!")
        return 0
    else:
        print(f"\n{total - passed} 个测试失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
