"""MCP tool definitions for ARES API."""

from typing import List
from mcp.types import Tool


def create_ares_tools() -> List[Tool]:
    """Create and return ARES API tools for MCP."""
    
    return [
        Tool(
            name="ares_search_subject",
            description="Search for economic subjects in Czech ARES registry",
            inputSchema={
                "type": "object",
                "properties": {
                    "ico": {
                        "type": "string",
                        "description": "Company identification number (IČO) - 8 digits"
                    },
                    "name": {
                        "type": "string",
                        "description": "Company name or part of it"
                    },
                    "address": {
                        "type": "string",
                        "description": "Company address or part of it"
                    }
                },
                "anyOf": [
                    {"required": ["ico"]},
                    {"required": ["name"]},
                    {"required": ["address"]}
                ]
            }
        ),
        Tool(
            name="ares_get_subject",
            description="Get detailed information about a specific economic subject by IČO",
            inputSchema={
                "type": "object",
                "properties": {
                    "ico": {
                        "type": "string",
                        "description": "Company identification number (IČO) - 8 digits"
                    }
                },
                "required": ["ico"]
            }
        ),
        Tool(
            name="ares_get_extract",
            description="Get business register extract for a company",
            inputSchema={
                "type": "object",
                "properties": {
                    "ico": {
                        "type": "string",
                        "description": "Company identification number (IČO) - 8 digits"
                    },
                    "extract_type": {
                        "type": "string",
                        "description": "Type of extract: 'standard' (default), 'complete', or 'basic'",
                        "enum": ["standard", "complete", "basic"],
                        "default": "standard"
                    }
                },
                "required": ["ico"]
            }
        ),
        Tool(
            name="ares_validate_ico",
            description="Validate if IČO is correctly formatted and exists in ARES",
            inputSchema={
                "type": "object",
                "properties": {
                    "ico": {
                        "type": "string",
                        "description": "Company identification number (IČO) to validate"
                    }
                },
                "required": ["ico"]
            }
        )
    ]