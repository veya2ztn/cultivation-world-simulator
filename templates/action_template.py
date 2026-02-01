"""
{{action_description}}

这个动作允许角色 {{action_purpose}}
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from src.classes.action import {{base_action_class}}, register_action
from src.classes.event import Event
from src.classes.action_runtime import ActionResult, ActionStatus

if TYPE_CHECKING:
    from src.classes.avatar import Avatar
    from src.classes.world import World


@register_action(actual=True)
class {{action_name}}({{base_action_class}}):
    """{{action_description}}

    动作类型: {{action_type}}
    持续时间: {{duration_description}}

    功能:
        - {{feature_1}}
        - {{feature_2}}
        - {{feature_3}}

    参数:
        {{param_name_1}}: {{param_description_1}}
        {{param_name_2}}: {{param_description_2}}

    示例:
        >>> action = {{action_name}}(avatar, world)
        >>> {{example_usage}}
    """

    # 多语言 ID
    ACTION_NAME_ID = "{{action_name_lower}}_action_name"
    DESC_ID = "{{action_name_lower}}_description"
    REQUIREMENTS_ID = "{{action_name_lower}}_requirements"

    # 动作属性
    EMOJI = "{{emoji}}"
    PARAMS = {
        "{{param_name_1}}": "{{param_type_1}}",
        "{{param_name_2}}": "{{param_type_2}}",
    }

    # 是否为大事（影响长期记忆）
    IS_MAJOR = {{is_major}}

    # 是否允许参与聚会
    ALLOW_GATHERING = {{allow_gathering}}

    # 是否允许触发世界随机事件
    ALLOW_WORLD_EVENTS = {{allow_world_events}}

    {{#if_timed_action}}
    # 长态动作持续时间（月份）
    duration_months = {{duration_months}}
    {{/if_timed_action}}

    def can_start(self, **params) -> tuple[bool, str]:
        """检查是否可以开始执行此动作

        Args:
            **params: 动作参数

        Returns:
            (可以执行, 失败原因)
        """
        # TODO: 实现检查逻辑
        # 示例检查：
        # if self.avatar.hp <= 0:
        #     return False, "角色已死亡，无法执行动作"
        # if {{some_condition}}:
        #     return False, "{{failure_reason}}"

        return True, ""

    def start(self, **params) -> Event | None:
        """动作开始时执行

        Args:
            **params: 动作参数

        Returns:
            开始事件（如果有）
        """
        # TODO: 实现开始逻辑
        # 可选：创建开始事件
        # event = self.create_event(
        #     content=f"{self.avatar.name} 开始 {{action_description_cn}}",
        #     related_avatars=[self.avatar.id]
        # )
        # return event

        return None

    def _execute(self, {{param_name_1}}: {{param_type_1}}, {{param_name_2}}: {{param_type_2}}) -> None:
        """执行动作的核心逻辑

        Args:
            {{param_name_1}}: {{param_description_1}}
            {{param_name_2}}: {{param_description_2}}

        注意:
            - {{execution_note_1}}
            - {{execution_note_2}}
        """
        # TODO: 实现动作逻辑

        # 示例：修改角色属性
        # self.avatar.{{some_attribute}} += {{some_value}}

        # 示例：与世界交互
        # tile = self.world.map.get_tile(self.avatar.pos_x, self.avatar.pos_y)
        # {{interaction_logic}}

        pass

    async def finish(self, **params) -> list[Event]:
        """动作完成时执行

        Args:
            **params: 动作参数

        Returns:
            完成时产生的事件列表
        """
        # TODO: 实现完成逻辑
        events = []

        # 示例：创建完成事件
        # event = self.create_event(
        #     content=f"{self.avatar.name} 完成了 {{action_description_cn}}",
        #     related_avatars=[self.avatar.id]
        # )
        # events.append(event)

        return events

    def get_save_data(self) -> dict:
        """获取需要存档的运行时数据"""
        data = super().get_save_data()
        # TODO: 添加需要保存的自定义数据
        # data['custom_field'] = self.custom_field
        return data

    def load_save_data(self, data: dict) -> None:
        """加载运行时数据"""
        super().load_save_data(data)
        # TODO: 加载自定义数据
        # self.custom_field = data.get('custom_field', default_value)
