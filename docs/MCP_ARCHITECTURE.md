**# MCP Architecture Documentation

## Overview

The Cultivation World MCP Server provides a Model Context Protocol interface for AI agents to interact with the cultivation world simulator. This document describes the architecture, components, and design decisions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (Claude)                         │
│                                                               │
│  - Natural language understanding                            │
│  - Tool selection and orchestration                          │
│  - Context management                                        │
└───────────────┬─────────────────────────────────────────────┘
                │
                │ MCP Protocol (stdio)
                │
┌───────────────▼─────────────────────────────────────────────┐
│              MCP Server (src/mcp_server/)                    │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │   Tools     │  │  Resources   │  │     Prompts        │ │
│  │             │  │              │  │                    │ │
│  │ 14+ actions │  │ URI-based    │  │ Roleplay modes     │ │
│  │ for world   │  │ real-time    │  │ Interaction        │ │
│  │ interaction │  │ data access  │  │ templates          │ │
│  └─────────────┘  └──────────────┘  └────────────────────┘ │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Permission System                             │   │
│  │  Observer │ Participant │ Admin                       │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────┬─────────────────────────────────────────────┘
                │
                │ Python API
                │
┌───────────────▼─────────────────────────────────────────────┐
│        Cultivation World Simulator                           │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐ │
│  │  World   │  │ Simulator │  │  Avatars  │  │   Events   │ │
│  └──────────┘  └──────────┘  └───────────┘  └────────────┘ │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐                 │
│  │   Sects  │  │   Map    │  │  Actions  │                 │
│  └──────────┘  └──────────┘  └───────────┘                 │
└───────────────────────────────────────────────────────────────┘
```

## Components

### 1. MCP Server (`server.py`)

**Responsibility**: Main entry point, handles MCP protocol communication

**Key Functions**:
- `main()`: Entry point, starts stdio server
- `initialize_world()`: Lazy initialization of world state
- `list_tools()`: Returns available tools
- `call_tool()`: Dispatches tool calls to handlers
- `list_resources()`: Returns available resources
- `read_resource()`: Reads resource by URI
- `list_prompts()`: Returns available prompts
- `get_prompt()`: Returns prompt with context

**State Management**:
```python
STATE = {
    "world": World,              # World instance
    "sim": Simulator,            # Simulator instance
    "permission_level": PermissionLevel,  # Access level
    "ai_avatar_id": str,         # AI-controlled avatar (if any)
}
```

### 2. Tools (`tools.py`)

**Responsibility**: Implement actions that AI can perform

**Tool Categories**:

#### Observation Tools (Observer permission)
- `get_world_status`: World overview (time, population, sects)
- `list_avatars`: List avatars with filtering
- `get_avatar_info`: Detailed avatar information
- `get_recent_events`: Recent events in world
- `get_sect_info`: Sect information
- `get_map_info`: Map and location data
- `search_locations`: Search for specific locations
- `analyze_relationships`: Relationship network analysis
- `analyze_power_structure`: Power dynamics analysis
- `predict_future`: AI-powered predictions

#### Interaction Tools (Participant permission)
- `talk_to_avatar`: Send message to avatar, get LLM response
- `create_ai_avatar`: Create new AI-controlled avatar
- `control_avatar`: Control AI avatar's actions

#### Admin Tools (Admin permission)
- `advance_time`: Advance world time by specified months

**Tool Signature**:
```python
async def handle_tool_name(
    world: World,
    sim: Simulator,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Tool implementation.

    Args:
        world: World instance
        sim: Simulator instance
        args: Tool arguments from AI

    Returns:
        Result dictionary (will be JSON serialized)
    """
    pass
```

### 3. Resources (`resources.py`)

**Responsibility**: Provide URI-based access to world data

**Resource URIs**:
- `world://status`: Current world status
- `world://avatars`: All avatars
- `world://avatars/{avatar_id}`: Specific avatar
- `world://events/recent`: Recent events
- `world://events/major`: Major events only
- `world://sects`: All sects
- `world://sects/{sect_id}`: Specific sect
- `world://map`: World map overview
- `world://relationships`: Relationship network

**Resource Handler**:
```python
async def handle_read_resource(
    uri: str,
    world: World,
    sim: Simulator
) -> str:
    """
    Read resource by URI.

    Returns: JSON string with resource data
    """
    pass
```

### 4. Prompts (`prompts.py`)

**Responsibility**: Provide interaction templates for different modes

**Available Prompts**:

#### `roleplay_as_god`
- Interact as divine being
- Can observe and influence world
- God-mode perspective

**Arguments**:
- `intention`: What you want to do

**Use Case**: High-level observation and occasional divine intervention

#### `roleplay_as_avatar`
- Embody a specific cultivator
- First-person experience
- Action-driven gameplay

**Arguments**:
- `avatar_id`: Avatar to roleplay (optional)

**Use Case**: Experience cultivation journey from avatar's perspective

#### `storyteller`
- Generate narrative descriptions
- Different styles (epic, poetic, dramatic, comedic)
- Story-focused interaction

**Arguments**:
- `focus`: What to focus on (optional)
- `style`: Narrative style (optional)

**Use Case**: Create engaging narratives from world events

#### `analyzer`
- Data-driven analysis
- Multiple analysis types
- Prediction and insights

**Arguments**:
- `analysis_type`: Type of analysis (required)
  - `power_structure`: Analyze power dynamics
  - `relationships`: Analyze social networks
  - `trends`: Identify trends and patterns
  - `predictions`: Predict future developments

**Use Case**: Deep understanding of world dynamics

### 5. Permissions (`permissions.py`)

**Responsibility**: Access control for different permission levels

**Permission Hierarchy**:

```
OBSERVER (Level 0)
  └─ Read-only access
  └─ Can view world state
  └─ Cannot interact

PARTICIPANT (Level 1)
  └─ All OBSERVER permissions
  └─ Can create avatar
  └─ Can talk to avatars
  └─ Can control AI avatar

ADMIN (Level 2)
  └─ All PARTICIPANT permissions
  └─ Can advance time
  └─ Full control over simulation
```

**Permission Check**:
```python
check_permission(
    current_level: PermissionLevel,
    required_level: PermissionLevel
) -> None  # Raises PermissionError if insufficient
```

## Data Flow

### Tool Call Flow

```
1. AI decides to call a tool
   ↓
2. Claude Desktop sends MCP request
   {
     "method": "tools/call",
     "params": {
       "name": "get_world_status",
       "arguments": {}
     }
   }
   ↓
3. MCP Server receives request
   ↓
4. call_tool() dispatcher
   ↓
5. Permission check
   ↓
6. initialize_world() (if needed)
   ↓
7. Tool handler (e.g., handle_get_world_status)
   ↓
8. Access World/Simulator
   ↓
9. Return result as JSON
   ↓
10. MCP Server sends response
   ↓
11. AI processes result and responds to user
```

### Resource Read Flow

```
1. AI wants to read resource
   ↓
2. Claude Desktop sends MCP request
   {
     "method": "resources/read",
     "params": {
       "uri": "world://status"
     }
   }
   ↓
3. MCP Server routes to handle_read_resource()
   ↓
4. Parse URI and dispatch to tool handler
   ↓
5. Return JSON data
   ↓
6. AI uses data in response
```

### Prompt Flow

```
1. AI uses a prompt
   ↓
2. Claude Desktop sends get_prompt request
   {
     "method": "prompts/get",
     "params": {
       "name": "roleplay_as_god",
       "arguments": {"intention": "observe"}
     }
   }
   ↓
3. MCP Server generates prompt with context
   - Queries current world state
   - Fills in template with live data
   ↓
4. Returns PromptMessage with context
   ↓
5. AI uses prompt as system message
   ↓
6. User interaction begins in this mode
```

## Design Decisions

### Why MCP over REST API?

| Aspect | MCP | REST API |
|--------|-----|----------|
| **Discovery** | Built-in tool/resource discovery | Manual documentation |
| **Type Safety** | JSON Schema for all tools | Requires separate OpenAPI spec |
| **Streaming** | Native resource streaming | Requires SSE or WebSocket |
| **Context** | Prompts provide rich context | Need to build separately |
| **AI Native** | Designed for AI agents | Generic, needs adaptation |
| **Local-First** | stdio transport, secure | Requires authentication layer |

**Decision**: MCP is superior for AI-native interaction. We can still provide REST API alongside for compatibility.

### Why Three-Layer Architecture?

**Tools**: Actions the AI can perform
- Pros: Clear, actionable, composable
- Use: When AI needs to do something

**Resources**: Real-time data access
- Pros: Streaming, efficient, cacheable
- Use: When AI needs current state

**Prompts**: Interaction templates
- Pros: Rich context, mode switching, guided interaction
- Use: When starting new interaction mode

**Decision**: Three layers cover different use cases. Tools for actions, Resources for data, Prompts for modes.

### Why Permission System?

**Problem**: Don't want AI to accidentally:
- Destroy the world (advance time by 1000 years)
- Mess up user's save
- Create unintended side effects

**Solution**: Three permission levels
- Observer: Safe, read-only
- Participant: Controlled interaction through avatar
- Admin: Full power (for trusted scenarios)

**Decision**: Default to Observer, require explicit upgrade for interaction/admin.

### World Initialization Strategy

**Options**:
1. Initialize on startup (eager)
2. Initialize on first request (lazy)
3. Keep running instance (persistent)

**Decision**: Lazy initialization
- Pros: Faster startup, works if world not configured
- Cons: First request slower

Future: Could support persistent mode with `--persistent` flag.

## Error Handling

### Tool Call Errors

```python
try:
    result = await handle_tool(world, args)
    return [TextContent(type="text", text=json.dumps(result))]
except PermissionError as e:
    return [TextContent(type="text", text=json.dumps({
        "error": "permission_denied",
        "message": str(e)
    }))]
except ValueError as e:
    return [TextContent(type="text", text=json.dumps({
        "error": "invalid_argument",
        "message": str(e)
    }))]
except Exception as e:
    return [TextContent(type="text", text=json.dumps({
        "error": "internal_error",
        "message": str(e)
    }))]
```

### Graceful Degradation

- If LLM unavailable: Return fallback response
- If world not initialized: Auto-initialize
- If avatar not found: Clear error message

## Performance Considerations

### Lazy Loading

- World initialized on first request
- Avatars loaded as needed
- Events paginated

### Caching

Currently no caching, but could add:
- Resource response caching (short TTL)
- Avatar info caching
- Event query caching

### Concurrency

- MCP server is single-threaded (stdio)
- World access is synchronous
- For multi-client: Consider adding lock

## Security

### Threat Model

**Threats**:
1. Malicious prompts trying to extract sensitive data
2. AI accidentally breaking the simulation
3. Resource exhaustion (infinite loops, etc.)

**Mitigations**:
1. Permission system limits what AI can do
2. Observer mode is read-only by default
3. Tool calls are logged to stderr
4. stdio transport means local-only access

### Future Enhancements

- [ ] Audit log of all tool calls
- [ ] Rate limiting on expensive operations
- [ ] Sandbox mode (copy-on-write world)
- [ ] User confirmation for destructive actions

## Extension Points

### Adding New Tools

1. Implement handler in `tools.py`:
```python
async def handle_my_tool(world: World, args: Dict) -> Dict:
    # Implementation
    pass
```

2. Register in `server.py` `list_tools()`:
```python
Tool(
    name="my_tool",
    description="What it does",
    inputSchema={...}
)
```

3. Add dispatch case in `call_tool()`:
```python
elif name == "my_tool":
    result = await handle_my_tool(STATE["world"], arguments)
```

### Adding New Resources

1. Add URI to `get_resource_list()` in `resources.py`
2. Add handler case in `handle_read_resource()`

### Adding New Prompts

1. Add to `get_prompt_list()` in `prompts.py`
2. Implement handler in `handle_get_prompt()`

## Testing

### Unit Tests

```python
# tests/test_mcp_tools.py
import pytest
from src.mcp_server.tools import handle_get_world_status

@pytest.mark.asyncio
async def test_get_world_status(sample_world):
    result = await handle_get_world_status(sample_world, None)
    assert "time" in result
    assert "population" in result
```

### Integration Tests

```python
# tests/test_mcp_integration.py
@pytest.mark.asyncio
async def test_full_flow():
    # Start server
    # Send MCP request
    # Verify response
    pass
```

### Manual Testing

Use `tools/mcp_client_example.py` for manual testing.

## Monitoring

### Logging

All logs go to stderr:
```
Starting Cultivation World MCP Server...
Permission level: observer
Cultivation world initialized successfully
[Tool Call] get_world_status -> success
[Tool Call] talk_to_avatar -> permission_denied
```

### Metrics

Future: Add metrics for:
- Tool call counts
- Resource access patterns
- Error rates
- Response times

## Future Roadmap

### Short Term
- [ ] Add more tools (modify avatar, create events, etc.)
- [ ] Improve error messages
- [ ] Add rate limiting
- [ ] Better LLM fallbacks

### Medium Term
- [ ] Multi-client support
- [ ] Persistent world mode
- [ ] Transaction support (rollback on error)
- [ ] Richer prompts with images

### Long Term
- [ ] GraphQL-style resource queries
- [ ] Event subscription (real-time updates)
- [ ] Collaborative multi-AI scenarios
- [ ] Integration with other MCP servers

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/anthropics/python-sdk)
- [Claude Desktop Integration](https://claude.ai/docs)

---

**Last Updated**: 2026-02-01
**Version**: 1.0.0
