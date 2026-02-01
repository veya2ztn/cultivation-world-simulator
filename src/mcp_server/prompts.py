"""
Prompt Templates for MCP Server

Defines prompt templates for different interaction modes:
- roleplay_as_god: Interact with the world as a divine being
- roleplay_as_avatar: Roleplay as a specific avatar
- storyteller: Generate narrative descriptions of events
- analyzer: Analyze world state and make predictions
"""

from typing import Any, Dict, Optional
import json

from mcp.types import Prompt, PromptMessage, GetPromptResult, TextContent

from src.classes.world import World


def get_prompt_list() -> list[Prompt]:
    """List all available prompts."""
    return [
        Prompt(
            name="roleplay_as_god",
            description="Interact with the cultivation world as a divine being who can observe and influence events",
            arguments=[
                {
                    "name": "intention",
                    "description": "What you want to do in the world (e.g., 'observe the realm', 'send a trial', 'bless a cultivator')",
                    "required": True,
                }
            ]
        ),
        Prompt(
            name="roleplay_as_avatar",
            description="Roleplay as a specific avatar in the cultivation world",
            arguments=[
                {
                    "name": "avatar_id",
                    "description": "ID of the avatar to roleplay as (optional, will create new if not provided)",
                    "required": False,
                }
            ]
        ),
        Prompt(
            name="storyteller",
            description="Generate narrative descriptions and storytelling based on world events",
            arguments=[
                {
                    "name": "focus",
                    "description": "What to focus the story on (avatar_id, sect_id, or 'recent_events')",
                    "required": False,
                },
                {
                    "name": "style",
                    "description": "Narrative style (epic, poetic, dramatic, comedic)",
                    "required": False,
                }
            ]
        ),
        Prompt(
            name="analyzer",
            description="Analyze world state and provide insights about power dynamics, trends, and predictions",
            arguments=[
                {
                    "name": "analysis_type",
                    "description": "Type of analysis (power_structure, relationships, trends, predictions)",
                    "required": True,
                }
            ]
        ),
    ]


async def handle_get_prompt(
    name: str,
    arguments: Dict[str, str],
    world: World,
    ai_avatar_id: Optional[str]
) -> GetPromptResult:
    """
    Get a specific prompt with context filled in.

    Args:
        name: Prompt name
        arguments: Prompt arguments
        world: World instance
        ai_avatar_id: ID of AI-controlled avatar (if any)

    Returns:
        GetPromptResult with messages
    """
    if name == "roleplay_as_god":
        return await get_roleplay_as_god_prompt(arguments, world)

    elif name == "roleplay_as_avatar":
        return await get_roleplay_as_avatar_prompt(arguments, world, ai_avatar_id)

    elif name == "storyteller":
        return await get_storyteller_prompt(arguments, world)

    elif name == "analyzer":
        return await get_analyzer_prompt(arguments, world)

    else:
        raise ValueError(f"Unknown prompt: {name}")


async def get_roleplay_as_god_prompt(
    arguments: Dict[str, str],
    world: World
) -> GetPromptResult:
    """Generate prompt for god roleplay mode."""
    intention = arguments.get("intention", "观察修仙世界")

    # Get world status
    from src.mcp_server.tools import handle_get_world_status, handle_get_recent_events
    from src.sim.simulator import Simulator

    # Note: We'd need sim instance here, for now use basic info
    world_info = f"""
修仙历{world.calendar.year}年{world.calendar.month}月
在世修士：{len([a for a in world.avatars.values() if not a.is_dead])}人
宗门数量：{len(world.sects)}
"""

    # Get recent events
    recent_events = sorted(
        [e for e in world.event_manager.events if e.is_major],
        key=lambda e: e.month_stamp,
        reverse=True
    )[:5]

    events_text = "\n".join([f"- {e.content}" for e in recent_events])

    prompt_text = f"""
你是修仙世界的天道意志，拥有观察和影响世界的能力。

# 当前世界状态
{world_info}

# 最近重大事件
{events_text}

# 你的意图
{intention}

作为天道，你可以：
1. 观察世界状态：使用 get_world_status, list_avatars 等工具
2. 与修士沟通：使用 talk_to_avatar 工具（as_god=true）向修士传音
3. 影响世界：设置天地灵机、降下天劫等（需要admin权限）

请基于你的意图，决定采取什么行动。你的行动将影响修仙世界的发展。

提示：
- 天道应保持中立，不随意干预凡间事务
- 只在关键时刻施加影响
- 可以通过传音引导修士，但不直接控制
- 观察世界演化，见证修士的成长
"""

    return GetPromptResult(
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=prompt_text)
            )
        ]
    )


async def get_roleplay_as_avatar_prompt(
    arguments: Dict[str, str],
    world: World,
    ai_avatar_id: Optional[str]
) -> GetPromptResult:
    """Generate prompt for avatar roleplay mode."""
    avatar_id = arguments.get("avatar_id") or ai_avatar_id

    if not avatar_id:
        # Prompt to create new avatar
        prompt_text = """
你即将在修仙世界中创建一个角色并扮演他/她。

首先，使用 create_ai_avatar 工具创建你的角色：
- 选择姓名、性别
- 描述性格特质
- 选择加入的宗门（或选择散修）

创建完成后，你将扮演这个角色，体验修仙之路：
- 修炼提升境界
- 与其他修士交流
- 探索世界，寻找机缘
- 面对挑战，做出选择

你准备好开始修仙之旅了吗？
"""
    else:
        # Get avatar info
        from src.mcp_server.tools import handle_get_avatar_info

        try:
            avatar_info = await handle_get_avatar_info(world, {"avatar_id": avatar_id})

            prompt_text = f"""
你正在扮演修仙世界中的角色：{avatar_info['basic_info']['name']}

# 角色信息
- 性别：{avatar_info['basic_info']['gender']}
- 年龄：{avatar_info['basic_info']['age']}岁（寿元上限{avatar_info['basic_info']['max_lifespan']}）
- 境界：{avatar_info['cultivation']['realm']} {avatar_info['cultivation']['level']}层
- 宗门：{avatar_info['social']['sect']}
- 生命值：{avatar_info['combat']['hp']}/{avatar_info['combat']['max_hp']}
- 灵石：{avatar_info['inventory']['magic_stones']}

# 性格特质
{', '.join(avatar_info['personality']['personas']) if avatar_info['personality']['personas'] else '未设定'}

# 当前状态
位置：({avatar_info['status']['position']['x']}, {avatar_info['status']['position']['y']})
当前动作：{avatar_info['status']['current_action']['name'] if avatar_info['status']['current_action'] else '无'}

作为{avatar_info['basic_info']['name']}，你可以：
1. 观察周围环境：使用 get_map_info, list_avatars 等工具
2. 与其他修士交流：使用 talk_to_avatar 工具
3. 执行动作：使用 control_avatar 工具（修炼、移动、战斗等）
4. 查看最近发生的事件：使用 get_recent_events 工具

请基于角色的性格和当前处境，决定下一步行动。记住，你是{avatar_info['basic_info']['name']}，要保持角色一致性。
"""
        except Exception as e:
            prompt_text = f"无法获取角色信息：{str(e)}"

    return GetPromptResult(
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=prompt_text)
            )
        ]
    )


async def get_storyteller_prompt(
    arguments: Dict[str, str],
    world: World
) -> GetPromptResult:
    """Generate prompt for storyteller mode."""
    focus = arguments.get("focus", "recent_events")
    style = arguments.get("style", "epic")

    # Get recent events
    from src.mcp_server.tools import handle_get_recent_events

    recent_events = await handle_get_recent_events(
        world,
        {"limit": 10, "major_only": True}
    )

    events_text = "\n".join([
        f"{i+1}. {e['content']}"
        for i, e in enumerate(recent_events['events'])
    ])

    style_descriptions = {
        "epic": "宏大史诗般的叙事，强调命运、天道与修士的抗争",
        "poetic": "诗意优美的描写，注重意境和韵味",
        "dramatic": "戏剧性的叙述，突出冲突和转折",
        "comedic": "轻松幽默的风格，展现修仙世界的趣味面",
    }

    prompt_text = f"""
你是修仙世界的说书人，负责将世界中发生的事件编织成精彩的故事。

# 叙事风格
{style_descriptions.get(style, style)}

# 最近发生的重大事件
{events_text}

# 世界背景
时间：修仙历{world.calendar.year}年{world.calendar.month}月
在世修士：{len([a for a in world.avatars.values() if not a.is_dead])}人
主要宗门：{', '.join([s.name for s in list(world.sects.values())[:3]])}

请基于这些事件，创作一段{style}风格的叙事。你可以：
1. 串联多个事件，形成连贯的故事线
2. 深入描写关键人物的内心活动
3. 渲染修仙世界的氛围和意境
4. 添加适当的细节和想象，但不偏离事实

开始你的叙述吧，修仙世界的故事等待被传颂...
"""

    return GetPromptResult(
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=prompt_text)
            )
        ]
    )


async def get_analyzer_prompt(
    arguments: Dict[str, str],
    world: World
) -> GetPromptResult:
    """Generate prompt for analyzer mode."""
    analysis_type = arguments.get("analysis_type", "trends")

    # Get world data
    from src.mcp_server.tools import (
        handle_get_world_status,
        handle_analyze_power_structure,
        handle_analyze_relationships,
    )

    analysis_prompts = {
        "power_structure": """
分析修仙世界当前的权力结构：

使用 analyze_power_structure 工具获取：
1. 个人实力排名（top cultivators）
2. 宗门势力对比
3. 整体实力分布

请分析：
- 谁掌握着最大的权力？
- 势力平衡如何？是否存在一家独大？
- 潜在的冲突点在哪里？
- 未来可能的权力变动
""",
        "relationships": """
分析修仙世界的人际关系网络：

使用 analyze_relationships 工具获取关系数据，然后分析：
- 关键人物的社交网络
- 门派内部的关系结构
- 潜在的联盟和对立
- 关系网络对世界格局的影响
""",
        "trends": """
分析修仙世界的发展趋势：

综合使用 get_world_status, get_recent_events 等工具，分析：
- 整体修为水平的变化趋势
- 重大事件的模式和规律
- 宗门势力的消长
- 可能的未来走向

提供数据驱动的洞察和预测。
""",
        "predictions": """
基于当前世界状态预测未来发展：

使用 predict_future 工具，结合其他数据分析：
- 未来可能发生的重大事件
- 关键角色的命运走向
- 宗门格局的变化
- 世界面临的机遇和挑战

给出有理有据的预测，并说明依据。
""",
    }

    prompt_text = analysis_prompts.get(
        analysis_type,
        "请指定分析类型：power_structure, relationships, trends, 或 predictions"
    )

    full_prompt = f"""
你是修仙世界的智者，擅长分析世界状态、预测未来走向。

# 分析任务
{prompt_text}

# 当前世界概况
时间：修仙历{world.calendar.year}年{world.calendar.month}月
在世修士：{len([a for a in world.avatars.values() if not a.is_dead])}人
宗门数量：{len(world.sects)}

请使用可用的工具收集数据，然后进行深入分析。你的分析应该：
1. 基于数据和事实
2. 揭示隐藏的模式和联系
3. 提供有洞察力的观点
4. 对未来做出合理预测（如果适用）
"""

    return GetPromptResult(
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=full_prompt)
            )
        ]
    )
