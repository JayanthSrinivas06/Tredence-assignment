from typing import Any, Dict
from pydantic import BaseModel, Field


class WorkflowState(BaseModel):
    data: Dict[str, Any] = Field(default_factory=dict, description="State data dictionary")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for tracking")
    
    class Config:
        arbitrary_types_allowed = True
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        self.data.update(updates)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data,
            "metadata": self.metadata
        }
