"""
MCP Server Package for Cultivation World Simulator

This package provides Model Context Protocol (MCP) server implementation
for AI agents to interact with the cultivation world.

Main components:
- server.py: MCP server entry point
- tools.py: Tool implementations for world interaction
- resources.py: Resource endpoints for real-time data access
- prompts.py: Prompt templates for different interaction modes
- permissions.py: Permission system for access control
"""

__version__ = "1.0.0"

from src.mcp_server.permissions import PermissionLevel, check_permission

__all__ = [
    "PermissionLevel",
    "check_permission",
]
