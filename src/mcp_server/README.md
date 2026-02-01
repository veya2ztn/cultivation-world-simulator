# MCP Server Module

Model Context Protocol server implementation for the Cultivation World Simulator.

## Overview

This module exposes the cultivation world through the Model Context Protocol (MCP), allowing AI agents like Claude to interact with the simulation through a standardized interface.

## Architecture

```
src/mcp_server/
├── __init__.py          # Package initialization
├── server.py            # MCP server entry point
├── tools.py             # Tool implementations (14+ tools)
├── resources.py         # Resource handlers (URI-based data access)
├── prompts.py           # Prompt templates for interaction modes
└── permissions.py       # Permission system (Observer/Participant/Admin)
```

## Quick Start

### 1. Installation

```bash
pip install mcp
```

### 2. Run the Server

```bash
python src/mcp_server/server.py
```

### 3. Configure Claude Desktop

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cultivation-world": {
      "command": "python",
      "args": ["E:/projects/cultivation-world-simulator/src/mcp_server/server.py"]
    }
  }
}
```

### 4. Test in Claude Desktop

```
Show me the status of the cultivation world.
```

## Components

### Server (`server.py`)

Main MCP server implementation:
- Handles protocol communication (stdio transport)
- Manages world state and initialization
- Dispatches tool calls, resource reads, and prompt requests
- Enforces permission system

### Tools (`tools.py`)

14+ tools for world interaction:

**Observation** (Observer permission):
- `get_world_status`: World overview
- `list_avatars`: List/filter avatars
- `get_avatar_info`: Detailed avatar info
- `get_recent_events`: Event history
- `get_sect_info`: Sect information
- `get_map_info`: Map data
- `search_locations`: Location search
- `analyze_relationships`: Social network
- `analyze_power_structure`: Power dynamics
- `predict_future`: AI predictions

**Interaction** (Participant permission):
- `talk_to_avatar`: Send messages, get responses
- `create_ai_avatar`: Create AI-controlled avatar
- `control_avatar`: Control AI avatar actions

**Administration** (Admin permission):
- `advance_time`: Fast-forward simulation

### Resources (`resources.py`)

URI-based real-time data access:
- `world://status`: Current world state
- `world://avatars`: All avatars
- `world://avatars/{id}`: Specific avatar
- `world://events/recent`: Recent events
- `world://events/major`: Major events
- `world://sects`: All sects
- `world://sects/{id}`: Specific sect
- `world://map`: Map overview
- `world://relationships`: Relationship network

### Prompts (`prompts.py`)

Interaction mode templates:
- `roleplay_as_god`: Divine observer/influencer
- `roleplay_as_avatar`: First-person cultivation
- `storyteller`: Narrative generation
- `analyzer`: Data-driven analysis

### Permissions (`permissions.py`)

Three-tier access control:
- **Observer**: Read-only (default)
- **Participant**: Interaction through avatar
- **Admin**: Full control

## Usage Examples

### Observer Mode

```python
# Get world status
result = await client.call_tool("get_world_status", {})

# List avatars in a sect
result = await client.call_tool("list_avatars", {
    "sect_id": "qingyun",
    "limit": 10
})

# Analyze power structure
result = await client.call_tool("analyze_power_structure", {
    "scope": "individual"
})
```

### Participant Mode

```python
# Create AI avatar
result = await client.call_tool("create_ai_avatar", {
    "name": "云风子",
    "gender": "male",
    "persona": "Brave and righteous cultivator"
})

# Talk to another avatar
result = await client.call_tool("talk_to_avatar", {
    "avatar_id": "avatar_123",
    "message": "前辈可否指点修炼之道？"
})

# Control avatar action
result = await client.call_tool("control_avatar", {
    "action": "cultivate"
})
```

### Resource Access

```python
# Read world status
content = await client.read_resource("world://status")

# Read specific avatar
content = await client.read_resource("world://avatars/avatar_123")

# Read major events
content = await client.read_resource("world://events/major")
```

### Using Prompts

```python
# Get god roleplay prompt
prompt = await client.get_prompt("roleplay_as_god", {
    "intention": "observe and guide worthy cultivators"
})

# Get storyteller prompt
prompt = await client.get_prompt("storyteller", {
    "focus": "recent_events",
    "style": "epic"
})
```

## Permission Configuration

Default permission level is OBSERVER. To change, edit `server.py`:

```python
STATE = {
    "permission_level": PermissionLevel.PARTICIPANT,  # or ADMIN
    # ...
}
```

## Testing

### Unit Tests

```bash
pytest tests/test_mcp_tools.py
pytest tests/test_mcp_resources.py
pytest tests/test_mcp_permissions.py
```

### Example Client

```bash
python tools/mcp_client_example.py
```

## Documentation

- **[MCP Setup Guide](../../docs/MCP_SETUP.md)**: Complete setup instructions
- **[MCP Architecture](../../docs/MCP_ARCHITECTURE.md)**: Detailed architecture documentation

## Key Features

✅ **AI-Native**: Designed specifically for AI agent interaction
✅ **Type-Safe**: JSON Schema for all tools
✅ **Real-Time**: Resource streaming for live data
✅ **Contextual**: Rich prompts with world state
✅ **Secure**: Permission-based access control
✅ **Extensible**: Easy to add new tools/resources/prompts
✅ **Local-First**: stdio transport, no network exposure

## Future Enhancements

- [ ] Transaction support (rollback on error)
- [ ] Multi-client support
- [ ] Event subscriptions (real-time updates)
- [ ] Richer prompts with images
- [ ] Persistent world mode
- [ ] Rate limiting and quotas
- [ ] Audit logging

## Troubleshooting

### Server won't start

```bash
# Install MCP
pip install mcp

# Verify Python path
echo $PYTHONPATH
```

### Claude can't see server

1. Check config file path is correct
2. Use absolute paths in config
3. Restart Claude Desktop
4. Check logs: Help → View Logs

### Permission errors

Check permission level in `server.py` STATE configuration.

## Contributing

When adding new tools:
1. Implement handler in `tools.py`
2. Register in `server.py` `list_tools()`
3. Add dispatch in `call_tool()`
4. Update tests
5. Update documentation

## License

Same as main project.

---

For detailed documentation, see:
- [MCP Setup Guide](../../docs/MCP_SETUP.md)
- [MCP Architecture](../../docs/MCP_ARCHITECTURE.md)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
