# MCP Server Setup Guide

This guide explains how to set up and use the Cultivation World MCP Server with Claude Desktop and other MCP-compatible AI agents.

## What is MCP?

Model Context Protocol (MCP) is an open protocol developed by Anthropic that enables AI applications to seamlessly connect with external data sources and tools. It provides a standardized way for AI agents like Claude to interact with your applications.

## Prerequisites

1. **Python 3.10+** installed
2. **Cultivation World Simulator** installed and configured
3. **Claude Desktop** (for Claude integration) or another MCP-compatible client

## Installation

### 1. Install MCP Dependencies

Add the MCP Python SDK to your requirements:

```bash
pip install mcp
```

Or add to `requirements.txt`:
```
mcp>=0.1.0
```

### 2. Verify Installation

Test that the MCP server can start:

```bash
python src/mcp_server/server.py
```

You should see:
```
Starting Cultivation World MCP Server...
Permission level: observer
```

Press Ctrl+C to stop.

## Claude Desktop Integration

### Configuration

1. **Locate Claude Desktop config file**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Edit the config file** to add the cultivation world MCP server:

```json
{
  "mcpServers": {
    "cultivation-world": {
      "command": "python",
      "args": [
        "E:/projects/cultivation-world-simulator/src/mcp_server/server.py"
      ],
      "env": {
        "PYTHONPATH": "E:/projects/cultivation-world-simulator"
      }
    }
  }
}
```

**Important**: Replace `E:/projects/cultivation-world-simulator` with your actual project path.

3. **Restart Claude Desktop**

### Verification

Open Claude Desktop and type:

```
Can you check what MCP servers are available?
```

Claude should respond mentioning the "cultivation-world" server.

Then try:

```
Use the cultivation world server to get the current world status.
```

Claude will use the `get_world_status` tool and show you the current state of the cultivation world!

## Usage Examples

### 1. Observer Mode (Default)

**What you can do**:
- View world status, avatars, events
- Analyze relationships and power structures
- Get sect and map information
- Make predictions about future developments

**Example prompts**:
```
Show me the current status of the cultivation world.

List all avatars in the 青云门 sect.

What are the recent major events?

Analyze the power structure of the cultivation world.

Who are the top 10 most powerful cultivators?
```

### 2. Participant Mode

To enable participant mode, you need to modify the server.py to set:
```python
STATE["permission_level"] = PermissionLevel.PARTICIPANT
```

**What you can do** (in addition to observer):
- Create your own avatar
- Talk to other avatars
- Control your avatar's actions

**Example prompts**:
```
Create an avatar named "云风子" who is a male cultivator with a brave personality.

Talk to avatar [avatar_id] and ask about their cultivation progress.

Have my avatar start cultivating.

Move my avatar to coordinates (50, 50).
```

### 3. Admin Mode

To enable admin mode:
```python
STATE["permission_level"] = PermissionLevel.ADMIN
```

**What you can do** (in addition to participant):
- Advance world time
- Full control over simulation

**Example prompts**:
```
Advance time by 12 months and show me what happened.
```

## Using Prompts

The MCP server provides pre-built prompts for different interaction modes:

### 1. Roleplay as God
```
Use the "roleplay_as_god" prompt with intention "observe the realm and identify worthy cultivators"
```

### 2. Roleplay as Avatar
```
Use the "roleplay_as_avatar" prompt to embody a cultivator
```

### 3. Storyteller
```
Use the "storyteller" prompt with style "epic" to create an epic narrative of recent events
```

### 4. Analyzer
```
Use the "analyzer" prompt with analysis_type "power_structure" to analyze the power dynamics
```

## Using Resources

Resources provide real-time streaming access to world data:

```
Read the resource "world://status"

Read the resource "world://events/major"

Read the resource "world://avatars/[avatar_id]"
```

## Troubleshooting

### Server won't start

**Error**: `ModuleNotFoundError: No module named 'mcp'`
- **Solution**: Install MCP: `pip install mcp`

**Error**: `ModuleNotFoundError: No module named 'src'`
- **Solution**: Make sure PYTHONPATH is set correctly in config

### Claude can't see the server

1. Check Claude Desktop config file is correct
2. Verify the path to server.py is absolute and correct
3. Restart Claude Desktop
4. Check Claude Desktop logs (Help → View Logs)

### Permission denied errors

**Error**: `Insufficient permission`
- **Solution**: The action requires higher permission level. Check the permission level in server.py STATE configuration.

### World initialization fails

**Error**: `Failed to initialize world`
- **Solution**:
  - Check that all dependencies are installed
  - Verify config files exist (static/local_config.yml)
  - Check Python console for detailed error messages

## Advanced Configuration

### Custom Permission Levels

Edit `src/mcp_server/server.py`:

```python
STATE = {
    "permission_level": PermissionLevel.PARTICIPANT,  # Change this
    # ...
}
```

### Pre-loading a Saved World

Modify the `initialize_world()` function in server.py to load from a save file:

```python
async def initialize_world():
    if STATE["world"] is not None:
        return

    # Load from save instead of creating new world
    from src.sim.load.load_game import load_game

    save_name = "my_world"  # Change to your save file
    world, sim = load_game(save_name)

    STATE["world"] = world
    STATE["sim"] = sim
```

### Adding Custom Tools

1. Add tool handler in `src/mcp_server/tools.py`
2. Register tool in `src/mcp_server/server.py` `list_tools()`
3. Add dispatch case in `call_tool()`

## API Reference

See [MCP_ARCHITECTURE.md](MCP_ARCHITECTURE.md) for detailed architecture documentation.

## Examples

See `tools/mcp_client_example.py` for example code using the MCP server programmatically.

## Security Considerations

1. **Local Only**: The MCP server runs locally via stdio, not exposed to network
2. **Permission Levels**: Control what AI can do through permission levels
3. **No Persistent Changes**: Observer mode is read-only
4. **Audit Trail**: All tool calls are logged to stderr

## Next Steps

1. Try the example prompts above
2. Read [MCP_ARCHITECTURE.md](MCP_ARCHITECTURE.md) to understand the architecture
3. Explore custom prompts and tools
4. Build your own MCP-compatible applications!

---

**Happy Cultivating! 🧙‍♂️✨**

For issues and questions, see the main project README or open an issue on GitHub.
