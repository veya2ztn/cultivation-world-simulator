"""
Permission System for MCP Server

Defines different permission levels for AI agents accessing the cultivation world:
- OBSERVER: Read-only access, can view world state but not interact
- PARTICIPANT: Can create an avatar and interact with the world
- ADMIN: Full control including time manipulation and world state modification
"""

from enum import Enum
from typing import Optional


class PermissionLevel(Enum):
    """Permission levels for MCP server access."""
    OBSERVER = "observer"      # Read-only access
    PARTICIPANT = "participant"  # Can interact through an avatar
    ADMIN = "admin"            # Full control


class PermissionError(Exception):
    """Raised when permission check fails."""
    pass


def check_permission(current_level: PermissionLevel, required_level: PermissionLevel):
    """
    Check if current permission level is sufficient.

    Permission hierarchy: OBSERVER < PARTICIPANT < ADMIN

    Args:
        current_level: Current permission level
        required_level: Required permission level

    Raises:
        PermissionError: If permission is insufficient
    """
    hierarchy = {
        PermissionLevel.OBSERVER: 0,
        PermissionLevel.PARTICIPANT: 1,
        PermissionLevel.ADMIN: 2,
    }

    if hierarchy[current_level] < hierarchy[required_level]:
        raise PermissionError(
            f"Insufficient permission. Required: {required_level.value}, "
            f"Current: {current_level.value}"
        )


def get_permission_description(level: PermissionLevel) -> str:
    """Get human-readable description of permission level."""
    descriptions = {
        PermissionLevel.OBSERVER: (
            "Observer mode - Read-only access. You can view world state, "
            "avatars, events, and relationships, but cannot interact with the world."
        ),
        PermissionLevel.PARTICIPANT: (
            "Participant mode - Interactive access. You can create an avatar, "
            "talk to other avatars, and participate in the world's story."
        ),
        PermissionLevel.ADMIN: (
            "Admin mode - Full control. You can manipulate time, modify world state, "
            "and have complete control over the simulation."
        ),
    }
    return descriptions[level]


def get_available_actions(level: PermissionLevel) -> list[str]:
    """Get list of available actions for a permission level."""
    observer_actions = [
        "get_world_status",
        "list_avatars",
        "get_avatar_info",
        "analyze_relationships",
        "get_recent_events",
        "get_sect_info",
        "get_map_info",
        "search_locations",
        "analyze_power_structure",
        "predict_future",
    ]

    participant_actions = observer_actions + [
        "talk_to_avatar",
        "create_ai_avatar",
        "control_avatar",
    ]

    admin_actions = participant_actions + [
        "advance_time",
        # Future: save_world, load_world, modify_avatar, etc.
    ]

    if level == PermissionLevel.OBSERVER:
        return observer_actions
    elif level == PermissionLevel.PARTICIPANT:
        return participant_actions
    elif level == PermissionLevel.ADMIN:
        return admin_actions
    else:
        return []
