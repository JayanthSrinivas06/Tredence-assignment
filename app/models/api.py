from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.graph import Graph


class CreateGraphRequest(BaseModel):
    name: str = Field(..., description="Graph name")
    description: Optional[str] = Field(None, description="Graph description")
    nodes: List[Dict[str, Any]] = Field(..., description="List of node definitions")
    edges: List[Dict[str, Any]] = Field(..., description="List of edge definitions")
    start_node: str = Field(..., description="Starting node name")


class CreateGraphResponse(BaseModel):
    graph_id: str = Field(..., description="Unique graph identifier")
    message: str = Field(..., description="Success message")


class RunGraphRequest(BaseModel):
    graph_id: str = Field(..., description="Graph identifier to run")
    initial_state: Dict[str, Any] = Field(default_factory=dict, description="Initial state data")


class ExecutionLog(BaseModel):
    step: int = Field(..., description="Step number")
    node: str = Field(..., description="Node name")
    status: str = Field(..., description="Execution status")
    message: Optional[str] = Field(None, description="Log message")
    state_snapshot: Optional[Dict[str, Any]] = Field(None, description="State after execution")


class RunGraphResponse(BaseModel):
    run_id: str = Field(..., description="Unique run identifier")
    graph_id: str = Field(..., description="Graph identifier")
    final_state: Dict[str, Any] = Field(..., description="Final state after execution")
    execution_log: List[ExecutionLog] = Field(..., description="Execution log")
    status: str = Field(..., description="Overall execution status")


class StateResponse(BaseModel):
    run_id: str = Field(..., description="Run identifier")
    graph_id: str = Field(..., description="Graph identifier")
    current_state: Dict[str, Any] = Field(..., description="Current state")
    status: str = Field(..., description="Execution status")
    execution_log: List[ExecutionLog] = Field(..., description="Execution log so far")
