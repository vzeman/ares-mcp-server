"""Main MCP server implementation for ARES API."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .api_client import AresAPIClient
from .tools import create_ares_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AresMCPServer:
    """MCP Server for ARES API integration."""
    
    def __init__(self):
        self.server = Server("ares-mcp-server")
        self.api_client = AresAPIClient()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP protocol handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Return available ARES API tools."""
            return create_ares_tools()
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]] = None) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool execution requests."""
            if arguments is None:
                arguments = {}
            
            try:
                if name == "ares_search_subject":
                    result = await self.api_client.search_subject(
                        ico=arguments.get("ico"),
                        name=arguments.get("name"),
                        address=arguments.get("address")
                    )
                    return [TextContent(type="text", text=result)]
                
                elif name == "ares_get_subject":
                    result = await self.api_client.get_subject(
                        ico=arguments["ico"]
                    )
                    return [TextContent(type="text", text=result)]
                
                elif name == "ares_get_extract":
                    result = await self.api_client.get_extract(
                        ico=arguments["ico"],
                        extract_type=arguments.get("extract_type", "standard")
                    )
                    return [TextContent(type="text", text=result)]
                
                elif name == "ares_validate_ico":
                    result = await self.api_client.validate_ico(
                        ico=arguments["ico"]
                    )
                    return [TextContent(type="text", text=result)]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ares-mcp-server",
                    server_version="0.1.0"
                )
            )


def main():
    """Main entry point."""
    server = AresMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()