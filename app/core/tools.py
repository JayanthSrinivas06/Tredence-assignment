"""
Tool registry for managing callable tools/functions.
"""
from typing import Any, Callable, Dict
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for managing tools (functions) that can be called by nodes."""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable) -> None:
        """Register a tool function."""
        self._tools[name] = func
        logger.info(f"Registered tool: {name}")
    
    def get(self, name: str) -> Callable:
        """Get a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        return self._tools[name]
    
    def has(self, name: str) -> bool:
        """Check if a tool exists."""
        return name in self._tools
    
    def list_tools(self) -> list:
        """List all registered tools."""
        return list(self._tools.keys())


# Global tool registry instance
_global_registry = ToolRegistry()


def register_tool(name: str):
    """Decorator to register a tool function."""
    def decorator(func: Callable):
        _global_registry.register(name, func)
        return func
    return decorator


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return _global_registry
