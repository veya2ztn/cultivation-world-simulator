"""
MCP Server for Cultivation World Simulator

This server exposes the cultivation world through the Model Context Protocol (MCP),
allowing AI agents like Claude to interact with the world through:
- Tools: Actions to observe and interact with the world
- Resources: Real-time access to world state
- Prompts: Templates for different interaction modes

Usage:
    python src/mcp_server/server.py

For Claude Desktop integration, add to claude_desktop_config.json:
{
  "mcpServers": {
    "cultivation-world": {
      "command": "python",
      "args": ["E:/projects/cultivation-world-simulator/src/mcp_server/server.py"]
    }
  }
}
"""

import asyncio
import json
import sys
import os
from typing import Any, Optional

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    Prompt,
    PromptMessage,
    GetPromptResult,
)

from src.mcp_server.tools import (
    handle_get_world_status,
    handle_list_avatars,
    handle_get_avatar_info,
    handle_talk_to_avatar,
    handle_create_ai_avatar,
    handle_control_avatar,
    handle_analyze_relationships,
    handle_get_recent_events,
    handle_advance_time,
    handle_get_sect_info,
    handle_get_map_info,
    handle_search_locations,
    handle_analyze_power_structure,
    handle_predict_future,
)

from src.mcp_server.resources import (
    get_resource_list,
    handle_read_resource,
)

from src.mcp_server.prompts import (
    get_prompt_list,
    handle_get_prompt,
)

from src.mcp_server.permissions import PermissionLevel, check_permission
from src.mcp_server.invitations import get_invitation_manager
from src.sim.simulator import Simulator
from src.classes.world import World
from src.utils.config import load_config

# Initialize server
app = Server("cultivation-world-mcp")

# Validate invitation code and determine permission level
def validate_invitation() -> PermissionLevel:
    """
    Validate invitation code from environment variable.

    Returns:
        PermissionLevel based on valid invitation, or OBSERVER if no/invalid code
    """
    api_key = os.environ.get("CULTIVATION_WORLD_API_KEY", "").strip()

    if not api_key:
        print("Warning: No CULTIVATION_WORLD_API_KEY provided. Running in OBSERVER mode.",
              file=sys.stderr)
        return PermissionLevel.OBSERVER

    # Validate with invitation manager
    invitation_manager = get_invitation_manager()
    permission_level = invitation_manager.validate_code(api_key)

    if permission_level is None:
        print(f"Warning: Invalid or expired invitation code. Running in OBSERVER mode.",
              file=sys.stderr)
        return PermissionLevel.OBSERVER

    print(f"Invitation code validated. Permission level: {permission_level.value}",
          file=sys.stderr)
    return permission_level

# Global state
STATE = {
    "world": None,
    "sim": None,
    "permission_level": validate_invitation(),  # Validate invitation code
    "ai_avatar_id": None,  # ID of AI-controlled avatar (if any)
}


async def initialize_world():
    """Initialize the cultivation world if not already initialized."""
    if STATE["world"] is not None:
        return

    try:
        # Load configuration
        load_config()

        # Initialize world (simplified - in real scenario might load from save)
        from src.run.load_map import load_cultivation_world_map
        from src.sim.new_avatar import make_avatars

        world_map = load_cultivation_world_map()
        world = World(world_map)

        # Create initial avatars
        avatars = make_avatars(12)  # Create 12 NPCs
        for avatar in avatars:
            world.add_avatar(avatar)

        # Initialize simulator
        sim = Simulator(world)

        STATE["world"] = world
        STATE["sim"] = sim

        print("Cultivation world initialized successfully", file=sys.stderr)
    except Exception as e:
        print(f"Failed to initialize world: {e}", file=sys.stderr)
        raise


# ============================================================================
# Tool Handlers
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="get_world_status",
            description="Get current world status including time, population, sects, and celestial phenomena",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_avatars",
            description="List all avatars in the world with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "sect_id": {
                        "type": "string",
                        "description": "Filter by sect ID"
                    },
                    "realm": {
                        "type": "string",
                        "description": "Filter by cultivation realm"
                    },
                    "min_level": {
                        "type": "integer",
                        "description": "Minimum level"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 50
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_avatar_info",
            description="Get detailed information about a specific avatar",
            inputSchema={
                "type": "object",
                "properties": {
                    "avatar_id": {
                        "type": "string",
                        "description": "Avatar ID"
                    }
                },
                "required": ["avatar_id"]
            }
        ),
        Tool(
            name="talk_to_avatar",
            description="Send a message to an avatar and get their response (requires PARTICIPANT permission)",
            inputSchema={
                "type": "object",
                "properties": {
                    "avatar_id": {
                        "type": "string",
                        "description": "Avatar ID to talk to"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message to send"
                    },
                    "as_god": {
                        "type": "boolean",
                        "description": "Whether to speak as a divine being (default: false)",
                        "default": False
                    }
                },
                "required": ["avatar_id", "message"]
            }
        ),
        Tool(
            name="create_ai_avatar",
            description="Create a new AI-controlled avatar (requires PARTICIPANT permission)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Avatar name"
                    },
                    "gender": {
                        "type": "string",
                        "enum": ["male", "female"],
                        "description": "Avatar gender"
                    },
                    "persona": {
                        "type": "string",
                        "description": "Personality description"
                    },
                    "sect_id": {
                        "type": "string",
                        "description": "Sect to join (optional)"
                    }
                },
                "required": ["name", "gender"]
            }
        ),
        Tool(
            name="control_avatar",
            description="Control an AI avatar's action (requires PARTICIPANT permission with AI avatar)",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (move, cultivate, rest, etc.)"
                    },
                    "target_id": {
                        "type": "string",
                        "description": "Target avatar/location ID (if applicable)"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Additional action parameters"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="analyze_relationships",
            description="Analyze relationship network between avatars",
            inputSchema={
                "type": "object",
                "properties": {
                    "avatar_id": {
                        "type": "string",
                        "description": "Center avatar ID (optional, shows all relationships if not specified)"
                    },
                    "relationship_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by relationship types (friend, enemy, master, disciple, etc.)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_recent_events",
            description="Get recent events in the world",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of events to retrieve",
                        "default": 20
                    },
                    "major_only": {
                        "type": "boolean",
                        "description": "Only show major events",
                        "default": False
                    },
                    "avatar_id": {
                        "type": "string",
                        "description": "Filter events related to specific avatar"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="advance_time",
            description="Advance world time by specified months (requires ADMIN permission)",
            inputSchema={
                "type": "object",
                "properties": {
                    "months": {
                        "type": "integer",
                        "description": "Number of months to advance",
                        "minimum": 1,
                        "maximum": 120
                    }
                },
                "required": ["months"]
            }
        ),
        Tool(
            name="get_sect_info",
            description="Get information about a sect",
            inputSchema={
                "type": "object",
                "properties": {
                    "sect_id": {
                        "type": "string",
                        "description": "Sect ID (optional, shows all sects if not specified)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_map_info",
            description="Get map information including regions and locations",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (optional)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (optional)"
                    },
                    "radius": {
                        "type": "integer",
                        "description": "Search radius around coordinates",
                        "default": 5
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="search_locations",
            description="Search for specific locations by type or name",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_type": {
                        "type": "string",
                        "description": "Type of location (sect, city, cave, hidden_domain, etc.)"
                    },
                    "name_query": {
                        "type": "string",
                        "description": "Search by name"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="analyze_power_structure",
            description="Analyze current power dynamics and influence in the world",
            inputSchema={
                "type": "object",
                "properties": {
                    "scope": {
                        "type": "string",
                        "enum": ["individual", "sect", "realm", "world"],
                        "description": "Scope of analysis",
                        "default": "world"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="predict_future",
            description="AI-powered prediction of possible future developments based on current state",
            inputSchema={
                "type": "object",
                "properties": {
                    "focus": {
                        "type": "string",
                        "description": "What to focus prediction on (avatar_id, sect_id, or general trends)"
                    },
                    "time_horizon": {
                        "type": "integer",
                        "description": "Months ahead to predict",
                        "default": 12
                    }
                },
                "required": []
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    await initialize_world()

    try:
        # Dispatch to appropriate handler
        if name == "get_world_status":
            result = await handle_get_world_status(STATE["world"], STATE["sim"])
        elif name == "list_avatars":
            result = await handle_list_avatars(STATE["world"], arguments)
        elif name == "get_avatar_info":
            result = await handle_get_avatar_info(STATE["world"], arguments)
        elif name == "talk_to_avatar":
            check_permission(STATE["permission_level"], PermissionLevel.PARTICIPANT)
            result = await handle_talk_to_avatar(STATE["world"], STATE["sim"], arguments)
        elif name == "create_ai_avatar":
            check_permission(STATE["permission_level"], PermissionLevel.PARTICIPANT)
            result = await handle_create_ai_avatar(STATE["world"], STATE["sim"], arguments)
            # Store AI avatar ID
            if "avatar_id" in result:
                STATE["ai_avatar_id"] = result["avatar_id"]
        elif name == "control_avatar":
            check_permission(STATE["permission_level"], PermissionLevel.PARTICIPANT)
            if not STATE["ai_avatar_id"]:
                raise ValueError("No AI avatar created. Use create_ai_avatar first.")
            result = await handle_control_avatar(
                STATE["world"], STATE["sim"], STATE["ai_avatar_id"], arguments
            )
        elif name == "analyze_relationships":
            result = await handle_analyze_relationships(STATE["world"], arguments)
        elif name == "get_recent_events":
            result = await handle_get_recent_events(STATE["world"], arguments)
        elif name == "advance_time":
            check_permission(STATE["permission_level"], PermissionLevel.ADMIN)
            result = await handle_advance_time(STATE["world"], STATE["sim"], arguments)
        elif name == "get_sect_info":
            result = await handle_get_sect_info(STATE["world"], arguments)
        elif name == "get_map_info":
            result = await handle_get_map_info(STATE["world"], arguments)
        elif name == "search_locations":
            result = await handle_search_locations(STATE["world"], arguments)
        elif name == "analyze_power_structure":
            result = await handle_analyze_power_structure(STATE["world"], arguments)
        elif name == "predict_future":
            result = await handle_predict_future(STATE["world"], STATE["sim"], arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "tool": name
        }, ensure_ascii=False))]


# ============================================================================
# Resource Handlers
# ============================================================================

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List all available resources."""
    return get_resource_list()


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource."""
    await initialize_world()
    return await handle_read_resource(uri, STATE["world"], STATE["sim"])


# ============================================================================
# Prompt Handlers
# ============================================================================

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List all available prompts."""
    return get_prompt_list()


@app.get_prompt()
async def get_prompt(name: str, arguments: Optional[dict[str, str]] = None) -> GetPromptResult:
    """Get a specific prompt."""
    await initialize_world()
    return await handle_get_prompt(name, arguments or {}, STATE["world"], STATE["ai_avatar_id"])


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Main entry point for the MCP server."""
    print("Starting Cultivation World MCP Server...", file=sys.stderr)
    print(f"Permission level: {STATE['permission_level'].value}", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
