#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vue 组件生成器

根据输入参数自动生成符合规范的 Vue 3 组件文件。

用法:
    python tools/generate_component.py <组件名称> [选项]

示例:
    # 生成基础组件
    python tools/generate_component.py UserCard

    # 生成带 props 的组件
    python tools/generate_component.py AvatarCard --props "avatarId:string,showDetails:boolean"

    # 生成带 emits 的组件
    python tools/generate_component.py ConfirmDialog --emits "confirm,cancel"

    # 生成完整组件
    python tools/generate_component.py ItemList --props "items:Array" --emits "select,delete"
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


def to_kebab_case(pascal_str: str) -> str:
    """将 PascalCase 转换为 kebab-case"""
    result = []
    for i, char in enumerate(pascal_str):
        if char.isupper() and i > 0:
            result.append("-")
        result.append(char.lower())
    return "".join(result)


def to_camel_case(pascal_str: str) -> str:
    """将 PascalCase 转换为 camelCase"""
    if not pascal_str:
        return pascal_str
    return pascal_str[0].lower() + pascal_str[1:]


def parse_props(props_str: str) -> list:
    """解析 props 字符串

    Args:
        props_str: 格式为 "prop1:type1,prop2:type2"

    Returns:
        解析后的 props 列表
    """
    if not props_str:
        return []

    props = []
    for prop in props_str.split(","):
        if ":" in prop:
            name, type_str = prop.strip().split(":")
            props.append({
                "name": name.strip(),
                "type": type_str.strip()
            })

    return props


def parse_emits(emits_str: str) -> list:
    """解析 emits 字符串

    Args:
        emits_str: 格式为 "emit1,emit2,emit3"

    Returns:
        解析后的 emits 列表
    """
    if not emits_str:
        return []

    return [emit.strip() for emit in emits_str.split(",")]


def replace_template_vars(template: str, variables: dict) -> str:
    """替换模板中的变量占位符"""
    result = template
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    return result


def generate_vue_component(
    component_name: str,
    props: list,
    emits: list,
    output_dir: str
):
    """生成 Vue 组件文件

    Args:
        component_name: 组件名称 (PascalCase)
        props: Props 列表
        emits: Emits 列表
        output_dir: 输出目录
    """
    # 读取模板
    template_path = Path(__file__).parent.parent / "templates" / "vue_component_template.vue"
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # 生成变量
    kebab_name = to_kebab_case(component_name)

    # Props
    prop_1 = props[0] if len(props) > 0 else {"name": "data", "type": "Object"}
    prop_2 = props[1] if len(props) > 1 else {"name": "showDetails", "type": "boolean"}

    # Emits
    emit_1 = emits[0] if len(emits) > 0 else "close"
    emit_2 = emits[1] if len(emits) > 1 else "update"

    # 准备变量
    variables = {
        "component_name": component_name,
        "component_description": f"{component_name} 组件",
        "component_class_name": kebab_name,
        "component_title": component_name,

        # Features
        "feature_1": "功能描述 1",
        "feature_2": "功能描述 2",
        "feature_3": "功能描述 3",

        # Props
        "prop_name_1": prop_1["name"],
        "prop_type_1": prop_1["type"],
        "prop_description_1": f"{prop_1['name']} 属性说明",
        "example_prop_value_1": f'"示例值"',

        "prop_name_2": prop_2["name"],
        "prop_type_2": prop_2["type"],
        "prop_description_2": f"{prop_2['name']} 属性说明（可选）",
        "prop_default_value_2": "false" if prop_2["type"] == "boolean" else "undefined",
        "example_prop_value_2": "true" if prop_2["type"] == "boolean" else '"示例值"',

        # Emits
        "emit_name_1": emit_1,
        "emit_description_1": f"{emit_1} 事件说明",
        "emit_param_1": "data",
        "emit_param_type_1": "any",
        "example_handler_1": f"handle{emit_1.capitalize()}",

        "emit_name_2": emit_2,
        "emit_description_2": f"{emit_2} 事件说明",
        "emit_param_2": "value",
        "emit_param_type_2": "string",
        "example_handler_2": f"handle{emit_2.capitalize()}",

        # Type imports
        "type_import_1": "SomeType",
        "type_import_2": "AnotherType",
        "type_module": "core",

        # State
        "state_name_1": "isLoading",
        "state_type_1": "boolean",
        "state_initial_value_1": "false",
        "state_description_1": "加载状态",

        "state_name_2": "items",
        "state_type_2": "Array<any>",
        "state_initial_value_2": "[]",
        "state_description_2": "数据列表",

        # Computed
        "computed_name_1": "hasData",
        "computed_description_1": "是否有数据",
        "computed_return_value_1": "items.value.length > 0",

        "computed_name_2": "displayText",
        "computed_description_2": "显示文本",
        "computed_return_value_2": "props.data?.name || '未命名'",

        # Methods
        "method_name_1": "handleClick",
        "method_description_1": "处理点击事件",
        "method_param_1": "item",
        "method_param_type_1": "any",
        "method_param_description_1": "点击的项目",

        "method_name_2": "loadData",
        "method_description_2": "加载数据",

        "handler_name": "handleKeydown",
        "handler_description": "处理键盘事件",
        "event_type": "KeyboardEvent",
        "event_description": "键盘事件对象",

        # Template
        "content_when_true": "有数据",
        "content_when_false": "暂无数据",
        "item": "item",
        "item_key_property": "id",
        "item_display_property": "name",
        "button_text_1": "确认",
        "button_text_2": "取消",
        "emit_value": "true",
    }

    # 生成代码
    code = replace_template_vars(template, variables)

    # 如果没有 props，简化代码
    if not props:
        code = code.replace("""interface Props {
  /** data 属性说明 */
  data: Object

  /** showDetails 属性说明（可选） */
  showDetails?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: false
})""", "// 此组件暂无 Props")

    # 如果没有 emits，简化代码
    if not emits:
        code = code.replace("""interface Emits {
  /** close 事件说明 */
  (e: 'close', data: any): void

  /** update 事件说明 */
  (e: 'update', value: string): void
}

const emit = defineEmits<Emits>()""", "// 此组件暂无 Emits")

    # 写入文件
    output_path = Path(output_dir) / f"{component_name}.vue"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"✅ 成功生成 Vue 组件文件: {output_path}")

    # 生成使用提示
    print("\n" + "="*60)
    print("📝 下一步操作:")
    print("="*60)
    print(f"\n1. 编辑组件并完善 TODO 部分:")
    print(f"   {output_path}")
    print(f"\n2. 在需要使用的父组件中导入:")
    print(f"   import {component_name} from '@/components/path/to/{component_name}.vue'")
    print(f"\n3. 在父组件模板中使用:")
    props_str = " ".join([f':{p["name"]}="{p["name"]}"' for p in props]) if props else ""
    emits_str = " ".join([f'@{e}="handle{e.capitalize()}"' for e in emits]) if emits else ""
    print(f"   <{component_name}{' ' + props_str if props_str else ''}{' ' + emits_str if emits_str else ''} />")
    print(f"\n4. 添加必要的类型定义到 web/src/types/")
    print(f"\n5. 创建组件测试文件（可选）:")
    print(f"   web/src/__tests__/{component_name}.test.ts")
    print(f"\n6. 在 Storybook 中查看组件（如果配置了）:")
    print(f"   npm run storybook")
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="生成符合规范的 Vue 3 组件文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成基础组件
  python tools/generate_component.py UserCard

  # 生成带 props 的组件
  python tools/generate_component.py AvatarCard --props "avatarId:string,showStats:boolean"

  # 生成带 emits 的组件
  python tools/generate_component.py ConfirmDialog --emits "confirm,cancel"

  # 生成完整组件
  python tools/generate_component.py ItemList \\
    --props "items:Array<Item>,selectedId:string" \\
    --emits "select,delete,refresh" \\
    --output web/src/components/game
        """
    )

    parser.add_argument(
        "name",
        help="组件名称 (PascalCase，例如: UserCard, AvatarDetail)"
    )

    parser.add_argument(
        "--props",
        default="",
        help='Props 定义，格式: "prop1:type1,prop2:type2" (例如: "avatarId:string,showDetails:boolean")'
    )

    parser.add_argument(
        "--emits",
        default="",
        help='Emits 定义，格式: "emit1,emit2,emit3" (例如: "close,update,select")'
    )

    parser.add_argument(
        "--output-dir",
        default="web/src/components",
        help="输出目录 (默认: web/src/components)"
    )

    args = parser.parse_args()

    # 验证组件名称
    if not args.name[0].isupper():
        print("❌ 错误: 组件名称必须是 PascalCase (首字母大写)")
        sys.exit(1)

    # 解析 props 和 emits
    props = parse_props(args.props)
    emits = parse_emits(args.emits)

    # 生成组件
    generate_vue_component(
        component_name=args.name,
        props=props,
        emits=emits,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
