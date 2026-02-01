"""
{{endpoint_description}}

此模块提供 {{api_purpose}} 相关的 API 端点。
"""
from fastapi import APIRouter, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from src.classes.world import World

# 创建路由器
router = APIRouter(
    prefix="/{{endpoint_prefix}}",
    tags=["{{endpoint_tag}}"]
)


# ==================== 请求/响应模型 ====================

class {{request_model_name}}(BaseModel):
    """{{request_description}}

    Attributes:
        {{request_field_1}}: {{request_field_1_description}}
        {{request_field_2}}: {{request_field_2_description}}
    """
    {{request_field_1}}: {{request_field_1_type}} = Field(
        ...,
        description="{{request_field_1_description}}",
        example={{request_field_1_example}}
    )
    {{request_field_2}}: {{request_field_2_type}} = Field(
        {{request_field_2_default}},
        description="{{request_field_2_description}}",
        example={{request_field_2_example}}
    )


class {{response_item_model_name}}(BaseModel):
    """{{response_item_description}}

    Attributes:
        {{response_item_field_1}}: {{response_item_field_1_description}}
        {{response_item_field_2}}: {{response_item_field_2_description}}
    """
    {{response_item_field_1}}: {{response_item_field_1_type}}
    {{response_item_field_2}}: {{response_item_field_2_type}}


class {{response_model_name}}(BaseModel):
    """{{response_description}}

    Attributes:
        {{response_field_1}}: {{response_field_1_description}}
        {{response_field_2}}: {{response_field_2_description}}
    """
    {{response_field_1}}: {{response_field_1_type}}
    {{response_field_2}}: {{response_field_2_type}}


# ==================== API 端点 ====================

@router.get(
    "/{{endpoint_path}}",
    response_model={{response_model_name}},
    summary="{{endpoint_summary}}",
    description="{{endpoint_detailed_description}}"
)
async def {{endpoint_function_name}}(
    {{path_param}}: {{path_param_type}} = Path(
        ...,
        description="{{path_param_description}}",
        example={{path_param_example}}
    ),
    {{query_param}}: {{query_param_type}} = Query(
        {{query_param_default}},
        description="{{query_param_description}}",
        example={{query_param_example}}
    )
) -> {{response_model_name}}:
    """{{endpoint_function_description}}

    Args:
        {{path_param}}: {{path_param_description}}
        {{query_param}}: {{query_param_description}}

    Returns:
        {{response_model_name}}: {{response_return_description}}

    Raises:
        HTTPException: 404 - {{not_found_condition}}
        HTTPException: 400 - {{bad_request_condition}}

    注意:
        - {{endpoint_note_1}}
        - {{endpoint_note_2}}
    """
    try:
        # 获取世界实例
        from src.main import get_world
        world: World = get_world()

        # TODO: 实现业务逻辑
        # 示例：验证参数
        # if {{validation_condition}}:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="{{validation_error_message}}"
        #     )

        # 示例：查找资源
        # resource = world.{{find_resource_method}}({{path_param}})
        # if not resource:
        #     raise HTTPException(
        #         status_code=404,
        #         detail=f"{{resource_type}} with ID {{path_param}} not found"
        #     )

        # 示例：构建响应
        # result = {{response_model_name}}(
        #     {{response_field_1}}={{value_1}},
        #     {{response_field_2}}={{value_2}}
        # )

        # return result

        pass

    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 捕获其他异常并转换为 500 错误
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/{{endpoint_path}}",
    response_model={{response_model_name}},
    summary="{{post_endpoint_summary}}",
    description="{{post_endpoint_description}}"
)
async def {{post_endpoint_function_name}}(
    request: {{request_model_name}} = Body(..., description="{{request_body_description}}")
) -> {{response_model_name}}:
    """{{post_endpoint_function_description}}

    Args:
        request: {{request_body_description}}

    Returns:
        {{response_model_name}}: {{post_response_description}}

    Raises:
        HTTPException: 400 - {{post_bad_request_condition}}
        HTTPException: 500 - 内部服务器错误

    注意:
        - {{post_endpoint_note_1}}
        - {{post_endpoint_note_2}}
    """
    try:
        # 获取世界实例
        from src.main import get_world
        world: World = get_world()

        # TODO: 实现创建/更新逻辑
        # 示例：验证请求
        # if not request.{{required_field}}:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="{{required_field}} is required"
        #     )

        # 示例：执行操作
        # result = world.{{operation_method}}(
        #     {{param_1}}=request.{{request_field_1}},
        #     {{param_2}}=request.{{request_field_2}}
        # )

        # 示例：返回结果
        # return {{response_model_name}}(
        #     {{response_field_1}}={{result_value_1}},
        #     {{response_field_2}}={{result_value_2}}
        # )

        pass

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete(
    "/{{endpoint_path}}/{{{path_param}}}",
    summary="{{delete_endpoint_summary}}",
    description="{{delete_endpoint_description}}"
)
async def {{delete_endpoint_function_name}}(
    {{path_param}}: {{path_param_type}} = Path(..., description="{{path_param_description}}")
) -> Dict[str, str]:
    """{{delete_endpoint_function_description}}

    Args:
        {{path_param}}: {{path_param_description}}

    Returns:
        Dict[str, str]: 包含成功消息的字典

    Raises:
        HTTPException: 404 - {{delete_not_found_condition}}
        HTTPException: 500 - 内部服务器错误

    注意:
        - {{delete_endpoint_note_1}}
    """
    try:
        # 获取世界实例
        from src.main import get_world
        world: World = get_world()

        # TODO: 实现删除逻辑
        # 示例：查找并删除
        # success = world.{{delete_method}}({{path_param}})
        # if not success:
        #     raise HTTPException(
        #         status_code=404,
        #         detail=f"{{resource_type}} with ID {{path_param}} not found"
        #     )

        return {"message": f"{{resource_type}} {{path_param}} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
