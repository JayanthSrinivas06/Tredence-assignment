"""
State management models for the workflow engine.
"""
from typing import Any, Dict
from pydantic import BaseModel, Field


class WorkflowState(BaseModel):
    """
    Base state model that flows through the workflow.
    Can be extended with specific fields for different workflows.
    """
    data: Dict[str, Any] = Field(default_factory=dict, description="State data dictionary")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for tracking")
    
    class Config:
        arbitrary_types_allowed = True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from state data."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in state data."""
        self.data[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple values in state data."""
        self.data.update(updates)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "data": self.data,
            "metadata": self.metadata
        }
