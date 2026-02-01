#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动作类生成器

根据输入参数自动生成符合规范的动作类文件和注册代码。

用法:
    python tools/generate_action.py <动作名称> [选项]

示例:
    # 生成即时动作
    python tools/generate_action.py Meditate --type instant --emoji 🧘

    # 生成长态动作
    python tools/generate_action.py Retreat --type timed --duration 3 --emoji 🏔️

    # 生成带参数的动作
    python tools/generate_action.py Trade --params "target_id:str,item_id:str" --emoji 💰
"""
import argparse
import os
import sys
from pathlib import Path

# 设置标准输出编码为 UTF-8（Windows 兼容性）
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")


# 模板变量替换
def replace_template_vars(template: str, variables: dict) -> str:
    """替换模板中的变量占位符

    Args:
        template: 模板字符串
        variables: 变量字典

    Returns:
        替换后的字符串
    """
    result = template
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))

    # 处理条件块
    if "{{#if_timed_action}}" in result:
        if variables.get("action_type") == "timed":
            result = result.replace("{{#if_timed_action}}", "")
            result = result.replace("{{/if_timed_action}}", "")
        else:
            # 移除整个条件块
            start = result.find("{{#if_timed_action}}")
            end = result.find("{{/if_timed_action}}") + len("{{/if_timed_action}}")
            if start != -1 and end != -1:
                result = result[:start] + result[end:]

    return result


def parse_params(params_str: str) -> dict:
    """解析参数字符串

    Args:
        params_str: 格式为 "param1:type1,param2:type2"

    Returns:
        解析后的参数字典
    """
    if not params_str:
        return {}

    params = {}
    for param in params_str.split(","):
        if ":" in param:
            name, type_str = param.strip().split(":")
            params[name.strip()] = type_str.strip()

    return params


def generate_action(
    action_name: str,
    action_type: str,
    duration: int,
    emoji: str,
    params: dict,
    is_major: bool,
    allow_gathering: bool,
    allow_world_events: bool,
    output_dir: str
):
    """生成动作类文件

    Args:
        action_name: 动作类名 (PascalCase)
        action_type: 动作类型 (instant/timed)
        duration: 持续时间（仅对 timed 类型有效）
        emoji: 动作图标
        params: 动作参数字典
        is_major: 是否为大事
        allow_gathering: 是否允许参与聚会
        allow_world_events: 是否允许触发世界事件
        output_dir: 输出目录
    """
    # 读取模板
    template_path = Path(__file__).parent.parent / "templates" / "action_template.py"
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # 确定基类
    base_class = "InstantAction" if action_type == "instant" else "TimedAction"

    # 准备参数
    param_items = list(params.items())
    param_name_1 = param_items[0][0] if len(param_items) > 0 else "param_1"
    param_type_1 = param_items[0][1] if len(param_items) > 0 else "Any"
    param_name_2 = param_items[1][0] if len(param_items) > 1 else "param_2"
    param_type_2 = param_items[1][1] if len(param_items) > 1 else "Any"

    # 构建参数字典字符串
    params_dict_str = "{\n"
    for pname, ptype in params.items():
        params_dict_str += f'        "{pname}": "{ptype}",\n'
    params_dict_str += "    }" if params else "{}"

    # 构建 _execute 参数列表
    execute_params = ", ".join([f"{pname}: {ptype}" for pname, ptype in params.items()])
    if not execute_params:
        execute_params = ""

    # 准备变量
    variables = {
        "action_name": action_name,
        "action_name_lower": action_name.lower(),
        "action_description": f"{action_name} 动作",
        "action_purpose": "执行特定操作",
        "action_type": action_type,
        "base_action_class": base_class,
        "duration_description": f"{duration} 个月" if action_type == "timed" else "立即完成",
        "duration_months": duration,
        "emoji": emoji,
        "is_major": "True" if is_major else "False",
        "allow_gathering": "True" if allow_gathering else "False",
        "allow_world_events": "True" if allow_world_events else "False",
        "feature_1": "功能描述 1",
        "feature_2": "功能描述 2",
        "feature_3": "功能描述 3",
        "param_name_1": param_name_1,
        "param_type_1": param_type_1,
        "param_description_1": f"{param_name_1} 参数说明",
        "param_name_2": param_name_2,
        "param_type_2": param_type_2,
        "param_description_2": f"{param_name_2} 参数说明",
        "params_dict": params_dict_str,
        "execute_params": execute_params,
        "example_usage": f"action.execute({', '.join([f'{p}=...' for p in params.keys()])})" if params else "action.execute()",
        "action_description_cn": f"{action_name} 操作",
        "execution_note_1": "注意事项 1",
        "execution_note_2": "注意事项 2",
    }

    # 生成代码
    code = replace_template_vars(template, variables)

    # 简化参数部分 - 如果没有参数，使用更简洁的版本
    if not params:
        # 简化 PARAMS
        code = code.replace('PARAMS = {\n        "param_1": "Any",\n        "param_2": "Any",\n    }', 'PARAMS = {}')
        # 简化 _execute 签名
        code = code.replace("def _execute(self, param_1: Any, param_2: Any) -> None:", "def _execute(self) -> None:")
        code = code.replace("""        Args:
            param_1: param_1 参数说明
            param_2: param_2 参数说明

        注意:""", """        注意:""")

    # 写入文件
    output_file = Path(output_dir) / f"{action_name.lower()}.py"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"✅ 成功生成动作类文件: {output_file}")

    # 生成注册提示
    print("\n" + "="*60)
    print("📝 下一步操作:")
    print("="*60)
    print(f"\n1. 编辑文件并完善 TODO 部分:")
    print(f"   {output_file}")
    print(f"\n2. 在 src/classes/action/__init__.py 中导入动作:")
    print(f"   from .{action_name.lower()} import {action_name}")
    print(f"\n3. 添加翻译条目到 assets/locales/zh-CN/actions.csv:")
    print(f"   {action_name.lower()}_action_name,{action_name},动作名称")
    print(f"   {action_name.lower()}_description,动作描述,动作描述")
    print(f"   {action_name.lower()}_requirements,执行条件,执行条件")
    print(f"\n4. 创建测试文件 tests/test_action_{action_name.lower()}.py")
    print(f"\n5. 运行测试:")
    print(f"   pytest tests/test_action_{action_name.lower()}.py -v")
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="生成符合规范的动作类文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成即时动作
  python tools/generate_action.py Meditate --type instant --emoji 🧘

  # 生成长态动作
  python tools/generate_action.py Retreat --type timed --duration 3 --emoji 🏔️

  # 生成带参数的动作
  python tools/generate_action.py Trade --params "target_id:str,item_id:str" --emoji 💰

  # 生成大事动作
  python tools/generate_action.py Breakthrough --type timed --duration 1 --major --emoji ⚡
        """
    )

    parser.add_argument(
        "name",
        help="动作类名 (PascalCase，例如: Meditate, Retreat)"
    )

    parser.add_argument(
        "--type",
        choices=["instant", "timed"],
        default="instant",
        help="动作类型: instant (即时) 或 timed (长态，默认: instant)"
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=1,
        help="长态动作持续时间（月份，默认: 1）"
    )

    parser.add_argument(
        "--emoji",
        default="⭐",
        help="动作图标 emoji (默认: ⭐)"
    )

    parser.add_argument(
        "--params",
        default="",
        help='动作参数，格式: "param1:type1,param2:type2" (例如: "target_id:str,amount:int")'
    )

    parser.add_argument(
        "--major",
        action="store_true",
        help="是否为大事（影响长期记忆）"
    )

    parser.add_argument(
        "--no-gathering",
        action="store_true",
        help="不允许参与聚会"
    )

    parser.add_argument(
        "--no-world-events",
        action="store_true",
        help="不允许触发世界随机事件"
    )

    parser.add_argument(
        "--output-dir",
        default="src/classes/action",
        help="输出目录 (默认: src/classes/action)"
    )

    args = parser.parse_args()

    # 验证动作名称
    if not args.name[0].isupper():
        print("❌ 错误: 动作名称必须是 PascalCase (首字母大写)")
        sys.exit(1)

    # 解析参数
    params = parse_params(args.params)

    # 生成动作
    generate_action(
        action_name=args.name,
        action_type=args.type,
        duration=args.duration,
        emoji=args.emoji,
        params=params,
        is_major=args.major,
        allow_gathering=not args.no_gathering,
        allow_world_events=not args.no_world_events,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
