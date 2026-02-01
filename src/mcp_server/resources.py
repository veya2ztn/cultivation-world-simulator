"""
Resource Handlers for MCP Server

Implements resource endpoints for real-time access to world state.
Resources are URI-based and provide streaming access to world data.
"""

from typing import Any, Dict
import json

from mcp.types import Resource, TextContent

from src.classes.world import World
from src.sim.simulator import Simulator


def get_resource_list() -> list[Resource]:
    """
    List all available resources.

    Resources provide real-time access to world state data.
    """
    return [
        Resource(
            uri="world://status",
            name="World Status",
            description="Current world status including time, population, and sects",
            mimeType="application/json",
        ),
        Resource(
            uri="world://avatars",
            name="All Avatars",
            description="List of all avatars in the world",
            mimeType="application/json",
        ),
        Resource(
            uri="world://avatars/{avatar_id}",
            name="Avatar Details",
            description="Detailed information about a specific avatar (replace {avatar_id} with actual ID)",
            mimeType="application/json",
        ),
        Resource(
            uri="world://events/recent",
            name="Recent Events",
            description="Recent events in the world",
            mimeType="application/json",
        ),
        Resource(
            uri="world://events/major",
            name="Major Events",
            description="Major events only",
            mimeType="application/json",
        ),
        Resource(
            uri="world://sects",
            name="All Sects",
            description="Information about all sects",
            mimeType="application/json",
        ),
        Resource(
            uri="world://sects/{sect_id}",
            name="Sect Details",
            description="Detailed information about a specific sect (replace {sect_id} with actual ID)",
            mimeType="application/json",
        ),
        Resource(
            uri="world://map",
            name="World Map",
            description="World map information and overview",
            mimeType="application/json",
        ),
        Resource(
            uri="world://relationships",
            name="Relationship Network",
            description="All relationships between avatars",
            mimeType="application/json",
        ),
    ]


async def handle_read_resource(uri: str, world: World, sim: Simulator) -> str:
    """
    Read a specific resource by URI.

    Args:
        uri: Resource URI (e.g., "world://status")
        world: World instance
        sim: Simulator instance

    Returns:
        JSON string with resource data
    """
    # Import tool handlers
    from src.mcp_server.tools import (
        handle_get_world_status,
        handle_list_avatars,
        handle_get_avatar_info,
        handle_get_recent_events,
        handle_get_sect_info,
        handle_get_map_info,
        handle_analyze_relationships,
    )

    try:
        if uri == "world://status":
            data = await handle_get_world_status(world, sim)

        elif uri == "world://avatars":
            data = await handle_list_avatars(world, {"limit": 1000})

        elif uri.startswith("world://avatars/"):
            avatar_id = uri.replace("world://avatars/", "")
            data = await handle_get_avatar_info(world, {"avatar_id": avatar_id})

        elif uri == "world://events/recent":
            data = await handle_get_recent_events(world, {"limit": 50})

        elif uri == "world://events/major":
            data = await handle_get_recent_events(world, {"limit": 50, "major_only": True})

        elif uri == "world://sects":
            data = await handle_get_sect_info(world, {})

        elif uri.startswith("world://sects/"):
            sect_id = uri.replace("world://sects/", "")
            data = await handle_get_sect_info(world, {"sect_id": sect_id})

        elif uri == "world://map":
            data = await handle_get_map_info(world, {})

        elif uri == "world://relationships":
            data = await handle_analyze_relationships(world, {})

        else:
            raise ValueError(f"Unknown resource URI: {uri}")

        return json.dumps(data, ensure_ascii=False, indent=2)

    except Exception as e:
        error_data = {
            "error": str(e),
            "uri": uri
        }
        return json.dumps(error_data, ensure_ascii=False)
