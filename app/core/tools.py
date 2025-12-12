from typing import Any, Callable, Dict
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable) -> None:
        self._tools[name] = func
        logger.info(f"Registered tool: {name}")
    
    def get(self, name: str) -> Callable:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        return self._tools[name]
    
    def has(self, name: str) -> bool:

        return name in self._tools
    
    def list_tools(self) -> list:
        
        return list(self._tools.keys())


# Global tool registry instance
_global_registry = ToolRegistry()


def register_tool(name: str):
    def decorator(func: Callable):
        _global_registry.register(name, func)
        return func

    return decorator


def get_tool_registry() -> ToolRegistry:
    return _global_registry
