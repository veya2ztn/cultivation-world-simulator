#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 端点生成器

根据输入参数自动生成符合规范的 FastAPI 端点代码。

用法:
    python tools/generate_api.py <端点名称> [选项]

示例:
    # 生成基础 CRUD 端点
    python tools/generate_api.py items --methods get,post,delete --prefix /api/items

    # 生成带路径参数的端点
    python tools/generate_api.py avatar_detail --path "/{avatar_id}" --methods get

    # 生成完整的 REST API
    python tools/generate_api.py sects --full-crud
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


def to_pascal_case(snake_str: str) -> str:
    """将 snake_case 转换为 PascalCase"""
    return "".join(word.capitalize() for word in snake_str.split("_"))


def to_camel_case(snake_str: str) -> str:
    """将 snake_case 转换为 camelCase"""
    components = snake_str.split("_")
    return components[0] + "".join(x.capitalize() for x in components[1:])


def replace_template_vars(template: str, variables: dict) -> str:
    """替换模板中的变量占位符"""
    result = template
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    return result


def generate_api_endpoint(
    endpoint_name: str,
    endpoint_prefix: str,
    endpoint_path: str,
    methods: list,
    tag: str,
    output_file: str
):
    """生成 API 端点文件

    Args:
        endpoint_name: 端点名称 (snake_case)
        endpoint_prefix: 路由前缀
        endpoint_path: 端点路径
        methods: HTTP 方法列表
        tag: API 标签
        output_file: 输出文件路径
    """
    # 读取模板
    template_path = Path(__file__).parent.parent / "templates" / "api_endpoint_template.py"
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # 生成类名
    pascal_name = to_pascal_case(endpoint_name)

    # 准备变量
    variables = {
        "endpoint_description": f"{pascal_name} API 端点",
        "api_purpose": endpoint_name.replace("_", " "),
        "endpoint_prefix": endpoint_prefix,
        "endpoint_tag": tag,
        "endpoint_name": endpoint_name,

        # Request Model
        "request_model_name": f"{pascal_name}Request",
        "request_description": f"{pascal_name} 请求数据",
        "request_field_1": "name",
        "request_field_1_type": "str",
        "request_field_1_description": "名称",
        "request_field_1_example": '"示例名称"',
        "request_field_2": "description",
        "request_field_2_type": "Optional[str]",
        "request_field_2_default": "None",
        "request_field_2_description": "描述（可选）",
        "request_field_2_example": '"示例描述"',

        # Response Item Model
        "response_item_model_name": f"{pascal_name}Item",
        "response_item_description": f"{pascal_name} 项目数据",
        "response_item_field_1": "id",
        "response_item_field_1_type": "str",
        "response_item_field_1_description": "项目 ID",
        "response_item_field_2": "name",
        "response_item_field_2_type": "str",
        "response_item_field_2_description": "项目名称",

        # Response Model
        "response_model_name": f"{pascal_name}Response",
        "response_description": f"{pascal_name} 响应数据",
        "response_field_1": "data",
        "response_field_1_type": f"List[{pascal_name}Item]",
        "response_field_1_description": "数据列表",
        "response_field_2": "total",
        "response_field_2_type": "int",
        "response_field_2_description": "总数",

        # GET Endpoint
        "endpoint_path": endpoint_path if endpoint_path else "",
        "endpoint_summary": f"获取 {endpoint_name.replace('_', ' ')}",
        "endpoint_detailed_description": f"获取 {endpoint_name.replace('_', ' ')} 的详细信息",
        "endpoint_function_name": f"get_{endpoint_name}",
        "endpoint_function_description": f"获取 {endpoint_name.replace('_', ' ')} 数据",
        "path_param": "id",
        "path_param_type": "str",
        "path_param_description": "资源 ID",
        "path_param_example": '"example-id"',
        "query_param": "limit",
        "query_param_type": "int",
        "query_param_default": "100",
        "query_param_description": "返回数量限制",
        "query_param_example": "100",
        "response_return_description": "包含数据的响应对象",
        "not_found_condition": "资源不存在时",
        "bad_request_condition": "请求参数无效时",
        "endpoint_note_1": "此端点支持分页查询",
        "endpoint_note_2": "返回的数据已按创建时间排序",

        # POST Endpoint
        "post_endpoint_summary": f"创建 {endpoint_name.replace('_', ' ')}",
        "post_endpoint_description": f"创建新的 {endpoint_name.replace('_', ' ')}",
        "post_endpoint_function_name": f"create_{endpoint_name}",
        "post_endpoint_function_description": f"创建新的 {endpoint_name.replace('_', ' ')}",
        "request_body_description": "创建请求数据",
        "post_response_description": "创建成功后的响应",
        "post_bad_request_condition": "请求数据无效时",
        "post_endpoint_note_1": "名称必须唯一",
        "post_endpoint_note_2": "创建后会自动生成唯一 ID",

        # DELETE Endpoint
        "delete_endpoint_summary": f"删除 {endpoint_name.replace('_', ' ')}",
        "delete_endpoint_description": f"根据 ID 删除 {endpoint_name.replace('_', ' ')}",
        "delete_endpoint_function_name": f"delete_{endpoint_name}",
        "delete_endpoint_function_description": f"删除指定的 {endpoint_name.replace('_', ' ')}",
        "delete_not_found_condition": "资源不存在时",
        "delete_endpoint_note_1": "删除操作不可恢复",

        # Common
        "resource_type": pascal_name,
        "validation_condition": "参数验证失败",
        "validation_error_message": "无效的请求参数",
        "required_field": "name",
    }

    # 生成代码
    code = replace_template_vars(template, variables)

    # 根据 methods 删除不需要的端点
    if "get" not in methods:
        # 删除 GET 端点
        start = code.find("@router.get(")
        if start != -1:
            end = code.find("\n\n@router.post(", start)
            if end != -1:
                code = code[:start] + code[end+2:]

    if "post" not in methods:
        # 删除 POST 端点
        start = code.find("@router.post(")
        if start != -1:
            end = code.find("\n\n@router.delete(", start)
            if end != -1:
                code = code[:start] + code[end+2:]
            else:
                # POST 是最后一个端点
                code = code[:start]

    if "delete" not in methods:
        # 删除 DELETE 端点
        start = code.find("@router.delete(")
        if start != -1:
            code = code[:start]

    # 写入文件
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"✅ 成功生成 API 端点文件: {output_path}")

    # 生成使用提示
    print("\n" + "="*60)
    print("📝 下一步操作:")
    print("="*60)
    print(f"\n1. 编辑文件并完善 TODO 部分:")
    print(f"   {output_path}")
    print(f"\n2. 在主应用中注册路由:")
    print(f"   # 在 src/main.py 或相应的路由文件中")
    print(f"   from .api.{endpoint_name} import router as {endpoint_name}_router")
    print(f"   app.include_router({endpoint_name}_router)")
    print(f"\n3. 测试 API 端点:")
    print(f"   # 启动服务器后访问")
    print(f"   http://localhost:8000/docs#{tag}")
    print(f"\n4. 创建 API 测试文件:")
    print(f"   tests/test_api_{endpoint_name}.py")
    print(f"\n5. 运行测试:")
    print(f"   pytest tests/test_api_{endpoint_name}.py -v")
    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="生成符合规范的 FastAPI 端点代码",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成基础 GET 端点
  python tools/generate_api.py items --methods get --prefix /api/items

  # 生成完整 CRUD 端点
  python tools/generate_api.py sects --methods get,post,delete --prefix /api/sects

  # 生成带路径参数的端点
  python tools/generate_api.py avatar_stats --path "/{avatar_id}/stats" --methods get

  # 使用 --full-crud 快速生成完整 REST API
  python tools/generate_api.py regions --full-crud
        """
    )

    parser.add_argument(
        "name",
        help="端点名称 (snake_case，例如: items, avatar_detail)"
    )

    parser.add_argument(
        "--prefix",
        default="/api",
        help="路由前缀 (默认: /api)"
    )

    parser.add_argument(
        "--path",
        default="",
        help='端点路径 (例如: /{id}, /{avatar_id}/stats)'
    )

    parser.add_argument(
        "--methods",
        default="get",
        help='HTTP 方法，逗号分隔 (例如: get,post,delete，默认: get)'
    )

    parser.add_argument(
        "--tag",
        default="",
        help="API 标签（用于文档分组，默认使用端点名称）"
    )

    parser.add_argument(
        "--full-crud",
        action="store_true",
        help="生成完整的 CRUD 端点 (等同于 --methods get,post,delete)"
    )

    parser.add_argument(
        "--output",
        default="",
        help="输出文件路径 (默认: src/api/<name>.py)"
    )

    args = parser.parse_args()

    # 验证端点名称
    if not args.name.islower() and "_" not in args.name:
        print("⚠️  警告: 建议使用 snake_case 格式的端点名称")

    # 处理 methods
    if args.full_crud:
        methods = ["get", "post", "delete"]
    else:
        methods = [m.strip().lower() for m in args.methods.split(",")]

    # 验证 methods
    valid_methods = {"get", "post", "put", "delete", "patch"}
    for method in methods:
        if method not in valid_methods:
            print(f"❌ 错误: 无效的 HTTP 方法 '{method}'")
            print(f"   支持的方法: {', '.join(valid_methods)}")
            sys.exit(1)

    # 确定输出文件
    if args.output:
        output_file = args.output
    else:
        output_file = f"src/api/{args.name}.py"

    # 确定标签
    tag = args.tag if args.tag else args.name.replace("_", " ").title()

    # 生成 API 端点
    generate_api_endpoint(
        endpoint_name=args.name,
        endpoint_prefix=args.prefix,
        endpoint_path=args.path,
        methods=methods,
        tag=tag,
        output_file=output_file
    )


if __name__ == "__main__":
    main()
