"""
{{module_description}}

这个模块定义了 {{class_name}} 类。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Any

if TYPE_CHECKING:
    from src.classes.world import World
    from src.classes.avatar import Avatar


class {{class_name}}:
    """{{class_description}}

    职责:
        - {{responsibility_1}}
        - {{responsibility_2}}
        - {{responsibility_3}}

    属性:
        {{attribute_name_1}} ({{attribute_type_1}}): {{attribute_description_1}}
        {{attribute_name_2}} ({{attribute_type_2}}): {{attribute_description_2}}

    示例:
        >>> {{example_usage}}
    """

    def __init__(
        self,
        {{init_param_1}}: {{init_param_1_type}},
        {{init_param_2}}: {{init_param_2_type}} = {{init_param_2_default}},
    ) -> None:
        """初始化 {{class_name}}

        Args:
            {{init_param_1}}: {{init_param_1_description}}
            {{init_param_2}}: {{init_param_2_description}}

        Raises:
            ValueError: 如果 {{validation_condition}}
        """
        self.{{attribute_name_1}} = {{init_param_1}}
        self.{{attribute_name_2}} = {{init_param_2}}

    def {{method_name}}(
        self,
        {{method_param_1}}: {{method_param_1_type}},
        {{method_param_2}}: {{method_param_2_type}} = {{method_param_2_default}},
    ) -> {{method_return_type}}:
        """{{method_description}}

        Args:
            {{method_param_1}}: {{method_param_1_description}}
            {{method_param_2}}: {{method_param_2_description}}

        Returns:
            {{method_return_description}}

        Raises:
            {{exception_type}}: {{exception_condition}}

        注意:
            - {{important_note_1}}
            - {{important_note_2}}
        """
        # TODO: 实现方法逻辑
        pass

    def __str__(self) -> str:
        """返回对象的字符串表示"""
        return f"{{class_name}}({{display_attributes}})"

    def __repr__(self) -> str:
        """返回对象的开发者表示"""
        return f"{{class_name}}({{repr_attributes}})"
