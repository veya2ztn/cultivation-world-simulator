"""
Example MCP Client for Cultivation World

This script demonstrates how to interact with the Cultivation World MCP Server
programmatically using the MCP Python SDK.

Usage:
    python tools/mcp_client_example.py
"""

import asyncio
import json
from mcp.client import Client
from mcp.client.stdio import stdio_client


async def example_observer_mode():
    """
    Example: Observer mode interactions.

    Demonstrates read-only access to the cultivation world.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Observer Mode")
    print("=" * 60)

    # Connect to MCP server
    async with stdio_client("python", ["src/mcp_server/server.py"]) as client:
        # Initialize client
        await client.initialize()

        print("\n[1] Getting world status...")
        result = await client.call_tool("get_world_status", {})
        print(json.dumps(json.loads(result[0].text), indent=2, ensure_ascii=False))

        print("\n[2] Listing top 5 avatars...")
        result = await client.call_tool("list_avatars", {"limit": 5})
        avatars_data = json.loads(result[0].text)
        print(f"Found {avatars_data['count']} avatars:")
        for avatar in avatars_data['avatars']:
            print(f"  - {avatar['name']} ({avatar['realm']}, {avatar['sect']})")

        print("\n[3] Getting recent major events...")
        result = await client.call_tool("get_recent_events", {
            "limit": 5,
            "major_only": True
        })
        events_data = json.loads(result[0].text)
        print(f"Recent {events_data['count']} major events:")
        for event in events_data['events']:
            print(f"  - {event['content']}")

        print("\n[4] Analyzing power structure...")
        result = await client.call_tool("analyze_power_structure", {
            "scope": "individual"
        })
        power_data = json.loads(result[0].text)
        print("Top 5 cultivators:")
        for cultivator in power_data['top_cultivators'][:5]:
            print(f"  {cultivator['rank']}. {cultivator['name']} - "
                  f"{cultivator['realm']} {cultivator['level']}层 "
                  f"({cultivator['sect']})")


async def example_resource_access():
    """
    Example: Accessing resources.

    Demonstrates URI-based resource access.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Resource Access")
    print("=" * 60)

    async with stdio_client("python", ["src/mcp_server/server.py"]) as client:
        await client.initialize()

        # List available resources
        print("\n[1] Listing available resources...")
        resources = await client.list_resources()
        print(f"Found {len(resources)} resources:")
        for resource in resources[:5]:  # Show first 5
            print(f"  - {resource.uri}: {resource.name}")

        # Read world status resource
        print("\n[2] Reading world://status resource...")
        content = await client.read_resource("world://status")
        status_data = json.loads(content)
        print(f"World Time: {status_data['time']['formatted']}")
        print(f"Population: {status_data['population']['living']} living, "
              f"{status_data['population']['dead']} dead")

        # Read events resource
        print("\n[3] Reading world://events/major resource...")
        content = await client.read_resource("world://events/major")
        events_data = json.loads(content)
        print(f"Major events: {events_data['count']}")


async def example_prompts():
    """
    Example: Using prompts.

    Demonstrates how to use predefined prompts for different interaction modes.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Using Prompts")
    print("=" * 60)

    async with stdio_client("python", ["src/mcp_server/server.py"]) as client:
        await client.initialize()

        # List available prompts
        print("\n[1] Listing available prompts...")
        prompts = await client.list_prompts()
        print(f"Found {len(prompts)} prompts:")
        for prompt in prompts:
            print(f"  - {prompt.name}: {prompt.description}")

        # Get "roleplay_as_god" prompt
        print("\n[2] Getting 'roleplay_as_god' prompt...")
        prompt_result = await client.get_prompt(
            "roleplay_as_god",
            {"intention": "observe the mortal realm and identify rising stars"}
        )
        print("Prompt content:")
        for message in prompt_result.messages:
            if hasattr(message.content, 'text'):
                # Print first 500 chars
                print(message.content.text[:500] + "...")

        # Get "analyzer" prompt
        print("\n[3] Getting 'analyzer' prompt...")
        prompt_result = await client.get_prompt(
            "analyzer",
            {"analysis_type": "trends"}
        )
        print("Analyzer prompt received (focused on trends)")


async def example_full_workflow():
    """
    Example: Complete workflow.

    Demonstrates a complete interaction workflow:
    1. Check world status
    2. Find interesting avatar
    3. Get avatar details
    4. Analyze their relationships
    5. Make predictions
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Complete Workflow")
    print("=" * 60)

    async with stdio_client("python", ["src/mcp_server/server.py"]) as client:
        await client.initialize()

        # Step 1: Get world status
        print("\n[Step 1] Checking world status...")
        result = await client.call_tool("get_world_status", {})
        world_data = json.loads(result[0].text)
        print(f"Current time: {world_data['time']['formatted']}")
        print(f"Living cultivators: {world_data['population']['living']}")

        # Step 2: Find highest realm cultivator
        print("\n[Step 2] Finding most powerful cultivator...")
        result = await client.call_tool("analyze_power_structure", {
            "scope": "individual"
        })
        power_data = json.loads(result[0].text)
        top_cultivator = power_data['top_cultivators'][0]
        print(f"Top cultivator: {top_cultivator['name']} "
              f"({top_cultivator['realm']} {top_cultivator['level']}层)")

        # Step 3: Get detailed info
        print("\n[Step 3] Getting detailed information...")
        # Note: We'd need the avatar_id here, which we don't have from power structure
        # In real scenario, we'd get this from list_avatars or power_structure would include it

        # Step 4: Check their sect
        sect_name = top_cultivator['sect']
        print(f"\n[Step 4] Checking their sect: {sect_name}")
        result = await client.call_tool("get_sect_info", {})
        sects_data = json.loads(result[0].text)
        for sect in sects_data['sects']:
            if sect['name'] == sect_name:
                print(f"Sect: {sect['name']}")
                print(f"Alignment: {sect['alignment']}")
                print(f"Members: {sect['member_count']}")

        # Step 5: Predict future
        print("\n[Step 5] Predicting future developments...")
        result = await client.call_tool("predict_future", {
            "focus": "general",
            "time_horizon": 12
        })
        prediction_data = json.loads(result[0].text)
        if "prediction" in prediction_data:
            print("Predicted trends:")
            for trend in prediction_data['prediction'].get('trends', [])[:3]:
                print(f"  - {trend}")
        else:
            print("(LLM prediction not available)")


async def example_error_handling():
    """
    Example: Error handling.

    Demonstrates how to handle various error conditions.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Error Handling")
    print("=" * 60)

    async with stdio_client("python", ["src/mcp_server/server.py"]) as client:
        await client.initialize()

        # Try to call non-existent tool
        print("\n[1] Calling non-existent tool...")
        try:
            result = await client.call_tool("nonexistent_tool", {})
            print(result[0].text)
        except Exception as e:
            print(f"Error (expected): {e}")

        # Try to read non-existent resource
        print("\n[2] Reading non-existent resource...")
        try:
            content = await client.read_resource("world://nonexistent")
            error_data = json.loads(content)
            if "error" in error_data:
                print(f"Error (expected): {error_data['error']}")
        except Exception as e:
            print(f"Error (expected): {e}")

        # Try to get info for non-existent avatar
        print("\n[3] Getting info for non-existent avatar...")
        result = await client.call_tool("get_avatar_info", {
            "avatar_id": "nonexistent_id"
        })
        response = json.loads(result[0].text)
        if "error" in response:
            print(f"Error (expected): {response['error']}")


async def main():
    """Run all examples."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Cultivation World MCP Client Examples                       ║
║  Demonstrates various ways to interact with the MCP server   ║
╚══════════════════════════════════════════════════════════════╝
""")

    try:
        await example_observer_mode()
        await example_resource_access()
        await example_prompts()
        await example_full_workflow()
        await example_error_handling()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
