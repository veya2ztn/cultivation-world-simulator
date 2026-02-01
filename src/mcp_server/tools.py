"""
Tool Handlers for MCP Server

Implements all tool functions that AI agents can call to interact with the cultivation world.
"""

from typing import Any, Dict, List, Optional
import json
from datetime import datetime

from src.classes.world import World
from src.classes.avatar.avatar import Avatar
from src.classes.cultivation import CultivationRealm
from src.sim.simulator import Simulator


async def handle_get_world_status(world: World, sim: Simulator) -> Dict[str, Any]:
    """
    Get current world status.

    Returns:
        Dictionary with world information including:
        - time: Current time (year, month, total months)
        - population: Avatar counts and statistics
        - sects: Sect information
        - celestial_phenomena: Active phenomena
    """
    avatars = list(world.avatars.values())
    living_avatars = [a for a in avatars if not a.is_dead]

    # Calculate statistics
    realm_distribution = {}
    for avatar in living_avatars:
        realm_name = avatar.realm.value if avatar.realm else "未知"
        realm_distribution[realm_name] = realm_distribution.get(realm_name, 0) + 1

    sect_distribution = {}
    for avatar in living_avatars:
        sect_name = avatar.sect.name if avatar.sect else "散修"
        sect_distribution[sect_name] = sect_distribution.get(sect_name, 0) + 1

    return {
        "time": {
            "year": world.calendar.year,
            "month": world.calendar.month,
            "month_stamp": world.month_stamp,
            "formatted": f"修仙历{world.calendar.year}年{world.calendar.month}月"
        },
        "population": {
            "total": len(avatars),
            "living": len(living_avatars),
            "dead": len(avatars) - len(living_avatars),
            "by_realm": realm_distribution,
            "by_sect": sect_distribution,
        },
        "sects": {
            sect.id: {
                "name": sect.name,
                "alignment": sect.alignment.value if sect.alignment else "中立",
                "member_count": len([a for a in living_avatars if a.sect and a.sect.id == sect.id]),
                "leader_id": sect.leader_id if hasattr(sect, 'leader_id') else None,
            }
            for sect in world.sects.values()
        },
        "celestial_phenomena": {
            "active": world.celestial_phenomenon.name if world.celestial_phenomenon else None,
            "qi_modifier": world.celestial_phenomenon.spiritual_qi_modifier if world.celestial_phenomenon else 1.0,
        },
        "notable_stats": {
            "highest_realm": max((a.realm.value for a in living_avatars), default="无"),
            "average_age": sum(a.age for a in living_avatars) / len(living_avatars) if living_avatars else 0,
            "total_events": len(world.event_manager.events),
        }
    }


async def handle_list_avatars(
    world: World,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    List avatars with optional filtering.

    Args:
        args: Filter parameters (sect_id, realm, min_level, limit)

    Returns:
        List of avatars matching the criteria
    """
    avatars = list(world.avatars.values())

    # Apply filters
    if "sect_id" in args:
        avatars = [a for a in avatars if a.sect and a.sect.id == args["sect_id"]]

    if "realm" in args:
        realm_filter = args["realm"]
        avatars = [a for a in avatars if a.realm and a.realm.value == realm_filter]

    if "min_level" in args:
        min_level = args["min_level"]
        avatars = [a for a in avatars if a.level >= min_level]

    # Apply limit
    limit = args.get("limit", 50)
    avatars = avatars[:limit]

    return {
        "count": len(avatars),
        "avatars": [
            {
                "id": a.id,
                "name": a.name,
                "gender": a.gender.value if a.gender else "未知",
                "age": a.age,
                "realm": a.realm.value if a.realm else "凡人",
                "level": a.level,
                "sect": a.sect.name if a.sect else "散修",
                "is_dead": a.is_dead,
                "position": {"x": a.pos_x, "y": a.pos_y},
                "hp": f"{a.hp}/{a.max_hp}",
                "current_action": a.current_action.action.name if a.current_action else "无",
            }
            for a in avatars
        ]
    }


async def handle_get_avatar_info(
    world: World,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get detailed information about a specific avatar.

    Args:
        args: Must contain avatar_id

    Returns:
        Detailed avatar information
    """
    avatar_id = args["avatar_id"]
    avatar = world.avatars.get(avatar_id)

    if not avatar:
        raise ValueError(f"Avatar {avatar_id} not found")

    # Get relationships
    relationships = []
    if hasattr(avatar, 'relationships'):
        for rel in avatar.relationships:
            target = world.avatars.get(rel.target_id)
            if target:
                relationships.append({
                    "target_name": target.name,
                    "target_id": target.id,
                    "type": rel.relationship_type.value if hasattr(rel, 'relationship_type') else "未知",
                    "level": rel.level if hasattr(rel, 'level') else 0,
                })

    # Get recent memories
    memories = []
    if hasattr(avatar, 'memories'):
        recent_memories = sorted(avatar.memories, key=lambda m: m.created_at, reverse=True)[:10]
        memories = [
            {
                "content": m.content,
                "type": m.memory_type if hasattr(m, 'memory_type') else "general",
                "created_at": m.created_at if hasattr(m, 'created_at') else None,
            }
            for m in recent_memories
        ]

    # Get objectives
    objectives = []
    if hasattr(avatar, 'long_term_objectives'):
        objectives.extend([
            {"type": "long_term", "description": obj.description}
            for obj in avatar.long_term_objectives
        ])
    if hasattr(avatar, 'short_term_objectives'):
        objectives.extend([
            {"type": "short_term", "description": obj.description}
            for obj in avatar.short_term_objectives
        ])

    return {
        "basic_info": {
            "id": avatar.id,
            "name": avatar.name,
            "gender": avatar.gender.value if avatar.gender else "未知",
            "age": avatar.age,
            "max_lifespan": avatar.max_lifespan,
            "is_dead": avatar.is_dead,
        },
        "cultivation": {
            "realm": avatar.realm.value if avatar.realm else "凡人",
            "level": avatar.level,
            "cultivation_exp": avatar.cultivation_exp if hasattr(avatar, 'cultivation_exp') else 0,
            "spiritual_roots": [sr.name for sr in avatar.spiritual_roots] if hasattr(avatar, 'spiritual_roots') else [],
        },
        "combat": {
            "hp": avatar.hp,
            "max_hp": avatar.max_hp,
            "attack": avatar.attack,
            "defense": avatar.defense,
        },
        "social": {
            "sect": avatar.sect.name if avatar.sect else "散修",
            "relationships": relationships,
        },
        "inventory": {
            "magic_stones": avatar.magic_stones if hasattr(avatar, 'magic_stones') else 0,
            "weapons": [w.name for w in avatar.weapons] if hasattr(avatar, 'weapons') else [],
            "auxiliaries": [a.name for a in avatar.auxiliaries] if hasattr(avatar, 'auxiliaries') else [],
            "elixirs": [e.name for e in avatar.elixirs] if hasattr(avatar, 'elixirs') else [],
        },
        "personality": {
            "personas": [p.name for p in avatar.personas] if hasattr(avatar, 'personas') else [],
            "memories": memories,
            "objectives": objectives,
        },
        "status": {
            "position": {"x": avatar.pos_x, "y": avatar.pos_y},
            "current_action": {
                "name": avatar.current_action.action.name if avatar.current_action else "无",
                "progress": avatar.current_action.progress if avatar.current_action and hasattr(avatar.current_action, 'progress') else 0,
                "duration": avatar.current_action.action.duration if avatar.current_action else 0,
            } if avatar.current_action else None,
        }
    }


async def handle_talk_to_avatar(
    world: World,
    sim: Simulator,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Talk to an avatar (requires LLM to generate response).

    Args:
        args: Must contain avatar_id and message, optional as_god

    Returns:
        Avatar's response
    """
    avatar_id = args["avatar_id"]
    message = args["message"]
    as_god = args.get("as_god", False)

    avatar = world.avatars.get(avatar_id)
    if not avatar:
        raise ValueError(f"Avatar {avatar_id} not found")

    if avatar.is_dead:
        return {
            "avatar_id": avatar_id,
            "avatar_name": avatar.name,
            "response": f"{avatar.name}已经仙逝，无法回应。",
            "is_dead": True,
        }

    # Use LLM to generate response
    from src.utils.llm.client import call_llm

    speaker = "天道之声" if as_god else "神秘访客"

    prompt = f"""
你是修仙世界中的角色：{avatar.name}

# 基本信息
- 境界：{avatar.realm.value if avatar.realm else '凡人'} {avatar.level}层
- 年龄：{avatar.age}岁
- 宗门：{avatar.sect.name if avatar.sect else '散修'}
- 性格：{', '.join([p.name for p in avatar.personas]) if hasattr(avatar, 'personas') else '普通'}

{'# 有一个' + speaker + '向你传音：' if not as_god else '# 天道之音在你耳边响起：'}
"{message}"

请以{avatar.name}的身份回应。回应要符合角色的性格、境界和当前处境。

只返回你的回应内容，不要包含其他说明。
"""

    try:
        response = await call_llm(prompt, mode="fast")

        # Create a memory of this interaction
        if hasattr(avatar, 'add_memory'):
            from src.classes.memory import Memory
            avatar.add_memory(Memory(
                content=f"{speaker}问：{message}。我答：{response}",
                memory_type="dialogue"
            ))

        return {
            "avatar_id": avatar_id,
            "avatar_name": avatar.name,
            "message_sent": message,
            "response": response,
            "is_dead": False,
        }

    except Exception as e:
        # Fallback to simple response if LLM fails
        return {
            "avatar_id": avatar_id,
            "avatar_name": avatar.name,
            "message_sent": message,
            "response": f"{avatar.name}沉思片刻，似乎在思考如何回应...",
            "error": str(e),
        }


async def handle_create_ai_avatar(
    world: World,
    sim: Simulator,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new AI-controlled avatar.

    Args:
        args: Must contain name, gender, optional persona and sect_id

    Returns:
        Created avatar information
    """
    from src.sim.new_avatar import create_avatar_from_request
    from src.classes.gender import Gender

    name = args["name"]
    gender = Gender.MALE if args["gender"].lower() == "male" else Gender.FEMALE

    # Create avatar
    avatar = create_avatar_from_request({
        "name": name,
        "gender": gender.value,
        "age": 16,  # Start as young cultivator
    })

    # Add custom persona if provided
    if "persona" in args:
        from src.classes.persona import Persona
        custom_persona = Persona(
            id=f"custom_{avatar.id}",
            name="AI驱动",
            description=args["persona"],
        )
        if hasattr(avatar, 'personas'):
            avatar.personas.append(custom_persona)

    # Join sect if specified
    if "sect_id" in args:
        sect = world.sects.get(args["sect_id"])
        if sect:
            avatar.sect = sect

    # Add to world
    world.add_avatar(avatar)

    return {
        "avatar_id": avatar.id,
        "name": avatar.name,
        "gender": avatar.gender.value,
        "realm": avatar.realm.value if avatar.realm else "凡人",
        "sect": avatar.sect.name if avatar.sect else "散修",
        "message": f"成功创建AI控制的角色：{avatar.name}",
    }


async def handle_control_avatar(
    world: World,
    sim: Simulator,
    ai_avatar_id: str,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Control an AI avatar's action.

    Args:
        ai_avatar_id: ID of AI-controlled avatar
        args: Must contain action, optional target_id and parameters

    Returns:
        Action result
    """
    avatar = world.avatars.get(ai_avatar_id)
    if not avatar:
        raise ValueError(f"AI avatar {ai_avatar_id} not found")

    if avatar.is_dead:
        return {
            "success": False,
            "message": f"{avatar.name}已死亡，无法执行动作",
        }

    action_name = args["action"]
    target_id = args.get("target_id")
    parameters = args.get("parameters", {})

    # Map action name to action class
    from src.classes.actions import ACTION_REGISTRY

    if action_name not in ACTION_REGISTRY:
        available_actions = ", ".join(ACTION_REGISTRY.keys())
        raise ValueError(f"Unknown action: {action_name}. Available: {available_actions}")

    action_class = ACTION_REGISTRY[action_name]

    # Create action instance
    try:
        if target_id:
            action = action_class(avatar, target_id=target_id, **parameters)
        else:
            action = action_class(avatar, **parameters)

        # Start action
        from src.classes.action_instance import ActionInstance
        action_instance = ActionInstance(action)
        avatar.current_action = action_instance

        return {
            "success": True,
            "avatar_id": ai_avatar_id,
            "avatar_name": avatar.name,
            "action": action_name,
            "message": f"{avatar.name}开始{action.EMOJI}{action.name}",
            "duration": action.duration,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"执行动作失败：{str(e)}",
        }


async def handle_analyze_relationships(
    world: World,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze relationship network.

    Args:
        args: Optional avatar_id (center of analysis) and relationship_types

    Returns:
        Relationship network data
    """
    avatar_id = args.get("avatar_id")
    relationship_types = args.get("relationship_types", [])

    if avatar_id:
        # Analyze relationships for specific avatar
        avatar = world.avatars.get(avatar_id)
        if not avatar:
            raise ValueError(f"Avatar {avatar_id} not found")

        relationships = []
        if hasattr(avatar, 'relationships'):
            for rel in avatar.relationships:
                if relationship_types and rel.relationship_type.value not in relationship_types:
                    continue

                target = world.avatars.get(rel.target_id)
                if target:
                    relationships.append({
                        "source": avatar.name,
                        "target": target.name,
                        "type": rel.relationship_type.value if hasattr(rel, 'relationship_type') else "未知",
                        "level": rel.level if hasattr(rel, 'level') else 0,
                        "description": f"{avatar.name}与{target.name}的关系：{rel.relationship_type.value}",
                    })

        return {
            "center_avatar": avatar.name,
            "relationship_count": len(relationships),
            "relationships": relationships,
        }
    else:
        # Analyze all relationships in world
        all_relationships = []
        for avatar in world.avatars.values():
            if hasattr(avatar, 'relationships'):
                for rel in avatar.relationships:
                    if relationship_types and rel.relationship_type.value not in relationship_types:
                        continue

                    target = world.avatars.get(rel.target_id)
                    if target:
                        all_relationships.append({
                            "source": avatar.name,
                            "source_id": avatar.id,
                            "target": target.name,
                            "target_id": target.id,
                            "type": rel.relationship_type.value if hasattr(rel, 'relationship_type') else "未知",
                            "level": rel.level if hasattr(rel, 'level') else 0,
                        })

        return {
            "total_relationships": len(all_relationships),
            "relationships": all_relationships,
        }


async def handle_get_recent_events(
    world: World,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get recent events.

    Args:
        args: Optional limit, major_only, avatar_id

    Returns:
        List of recent events
    """
    limit = args.get("limit", 20)
    major_only = args.get("major_only", False)
    avatar_id = args.get("avatar_id")

    events = world.event_manager.events

    # Filter by avatar
    if avatar_id:
        events = [e for e in events if avatar_id in e.related_avatars]

    # Filter by major
    if major_only:
        events = [e for e in events if e.is_major]

    # Sort by time (most recent first)
    events = sorted(events, key=lambda e: e.month_stamp, reverse=True)

    # Apply limit
    events = events[:limit]

    return {
        "count": len(events),
        "events": [
            {
                "id": e.id,
                "content": e.content,
                "month_stamp": e.month_stamp,
                "is_major": e.is_major,
                "is_story": e.is_story,
                "related_avatars": [
                    world.avatars[aid].name
                    for aid in e.related_avatars
                    if aid in world.avatars
                ],
            }
            for e in events
        ]
    }


async def handle_advance_time(
    world: World,
    sim: Simulator,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Advance world time (ADMIN only).

    Args:
        args: Must contain months (1-120)

    Returns:
        Summary of what happened during the time advance
    """
    months = args["months"]

    if months < 1 or months > 120:
        raise ValueError("Months must be between 1 and 120")

    initial_month = world.month_stamp
    events_before = len(world.event_manager.events)

    # Advance time
    for _ in range(months):
        await sim.step()

    final_month = world.month_stamp
    events_after = len(world.event_manager.events)
    new_events = events_after - events_before

    # Get summary of recent major events
    recent_major_events = [
        e for e in world.event_manager.events
        if e.is_major and e.month_stamp > initial_month
    ]

    return {
        "months_advanced": months,
        "initial_month": initial_month,
        "final_month": final_month,
        "new_events_count": new_events,
        "major_events": [
            {
                "content": e.content,
                "month_stamp": e.month_stamp,
                "related_avatars": [
                    world.avatars[aid].name
                    for aid in e.related_avatars
                    if aid in world.avatars
                ],
            }
            for e in recent_major_events[:10]  # Show up to 10 major events
        ]
    }


async def handle_get_sect_info(
    world: World,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """Get information about sects."""
    sect_id = args.get("sect_id")

    if sect_id:
        sect = world.sects.get(sect_id)
        if not sect:
            raise ValueError(f"Sect {sect_id} not found")

        members = [a for a in world.avatars.values() if a.sect and a.sect.id == sect_id and not a.is_dead]

        return {
            "id": sect.id,
            "name": sect.name,
            "alignment": sect.alignment.value if sect.alignment else "中立",
            "description": sect.description if hasattr(sect, 'description') else "",
            "member_count": len(members),
            "members": [
                {
                    "name": a.name,
                    "id": a.id,
                    "realm": a.realm.value if a.realm else "凡人",
                    "level": a.level,
                }
                for a in members
            ]
        }
    else:
        # List all sects
        return {
            "sects": [
                {
                    "id": sect.id,
                    "name": sect.name,
                    "alignment": sect.alignment.value if sect.alignment else "中立",
                    "member_count": len([a for a in world.avatars.values() if a.sect and a.sect.id == sect.id and not a.is_dead]),
                }
                for sect in world.sects.values()
            ]
        }


async def handle_get_map_info(
    world: World,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """Get map information."""
    x = args.get("x")
    y = args.get("y")
    radius = args.get("radius", 5)

    if x is not None and y is not None:
        # Get tile info
        tile = world.map.get_tile(x, y)
        nearby_avatars = [
            a for a in world.avatars.values()
            if abs(a.pos_x - x) <= radius and abs(a.pos_y - y) <= radius and not a.is_dead
        ]

        return {
            "position": {"x": x, "y": y},
            "tile_type": tile.tile_type if tile else "unknown",
            "nearby_avatars": [
                {
                    "name": a.name,
                    "id": a.id,
                    "position": {"x": a.pos_x, "y": a.pos_y},
                    "distance": abs(a.pos_x - x) + abs(a.pos_y - y),
                }
                for a in nearby_avatars
            ],
        }
    else:
        # Get map overview
        return {
            "width": world.map.width,
            "height": world.map.height,
            "regions": len(world.regions),
            "avatars_on_map": len([a for a in world.avatars.values() if not a.is_dead]),
        }


async def handle_search_locations(
    world: World,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """Search for locations."""
    location_type = args.get("location_type")
    name_query = args.get("name_query")

    results = []

    # Search in regions
    for region in world.regions.values():
        match = True

        if location_type:
            region_type = type(region).__name__.lower()
            if location_type.lower() not in region_type:
                match = False

        if name_query:
            if name_query.lower() not in region.name.lower():
                match = False

        if match:
            results.append({
                "name": region.name,
                "type": type(region).__name__,
                "position": {"x": region.x, "y": region.y} if hasattr(region, 'x') else None,
            })

    return {
        "count": len(results),
        "locations": results,
    }


async def handle_analyze_power_structure(
    world: World,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze power dynamics."""
    scope = args.get("scope", "world")

    living_avatars = [a for a in world.avatars.values() if not a.is_dead]

    if scope == "individual":
        # Top 10 most powerful individuals
        sorted_avatars = sorted(
            living_avatars,
            key=lambda a: (a.realm.value if a.realm else "", a.level, a.attack),
            reverse=True
        )[:10]

        return {
            "scope": "individual",
            "top_cultivators": [
                {
                    "rank": i + 1,
                    "name": a.name,
                    "realm": a.realm.value if a.realm else "凡人",
                    "level": a.level,
                    "sect": a.sect.name if a.sect else "散修",
                    "combat_power": a.attack + a.defense,
                }
                for i, a in enumerate(sorted_avatars)
            ]
        }

    elif scope == "sect":
        # Sect power ranking
        sect_power = {}
        for sect in world.sects.values():
            members = [a for a in living_avatars if a.sect and a.sect.id == sect.id]
            total_power = sum(a.attack + a.defense for a in members)
            avg_realm = sum(a.level for a in members) / len(members) if members else 0

            sect_power[sect.id] = {
                "name": sect.name,
                "member_count": len(members),
                "total_power": total_power,
                "average_realm": avg_realm,
            }

        sorted_sects = sorted(
            sect_power.items(),
            key=lambda x: x[1]["total_power"],
            reverse=True
        )

        return {
            "scope": "sect",
            "sect_ranking": [
                {
                    "rank": i + 1,
                    "sect_id": sect_id,
                    **data
                }
                for i, (sect_id, data) in enumerate(sorted_sects)
            ]
        }

    else:  # world
        return {
            "scope": "world",
            "summary": {
                "total_cultivators": len(living_avatars),
                "sects": len(world.sects),
                "highest_realm": max((a.realm.value for a in living_avatars), default="无"),
                "average_level": sum(a.level for a in living_avatars) / len(living_avatars) if living_avatars else 0,
                "realm_distribution": {
                    realm.value: len([a for a in living_avatars if a.realm == realm])
                    for realm in CultivationRealm
                },
            }
        }


async def handle_predict_future(
    world: World,
    sim: Simulator,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    AI-powered prediction of future developments.

    This uses LLM to analyze current state and predict possible outcomes.
    """
    focus = args.get("focus", "general")
    time_horizon = args.get("time_horizon", 12)

    # Gather context for prediction
    from src.utils.llm.client import call_llm

    # Build context
    world_status = await handle_get_world_status(world, sim)
    recent_events = await handle_get_recent_events(world, {"limit": 10, "major_only": True})

    context = f"""
分析修仙世界当前状态，预测未来{time_horizon}个月可能发生的事件。

# 当前世界状态
时间：{world_status['time']['formatted']}
人口：{world_status['population']['living']}人在世
境界分布：{json.dumps(world_status['population']['by_realm'], ensure_ascii=False)}

# 最近重大事件
{json.dumps([e['content'] for e in recent_events['events']], ensure_ascii=False, indent=2)}

请分析：
1. 当前世界的主要趋势
2. 可能发生的重大事件（如突破、战斗、宗门冲突等）
3. 潜在的危机或机遇
4. 对未来{time_horizon}个月的预测

以JSON格式返回：
{{
    "trends": ["趋势1", "趋势2", ...],
    "predicted_events": [
        {{"event": "事件描述", "probability": "高/中/低", "timeframe": "几个月内"}},
        ...
    ],
    "risks": ["风险1", ...],
    "opportunities": ["机遇1", ...]
}}
"""

    try:
        response = await call_llm(context, mode="normal")
        prediction = json.loads(response)

        return {
            "focus": focus,
            "time_horizon_months": time_horizon,
            "prediction": prediction,
            "generated_at": world_status['time']['formatted'],
        }
    except Exception as e:
        return {
            "error": f"预测失败：{str(e)}",
            "fallback": "由于LLM不可用，无法生成预测。请稍后再试。",
        }
