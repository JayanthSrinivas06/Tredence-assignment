from typing import Any, Callable, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ConditionalEdge(BaseModel):
    condition_key: str = Field(..., description="Key in state to evaluate")
    condition_operator: str = Field(..., description="Operator: <, >, <=, >=, ==, !=")
    condition_value: Any = Field(..., description="Value to compare against")
    true_node: str = Field(..., description="Node to execute if condition is true")
    false_node: str = Field(..., description="Node to execute if condition is false")


class Node(BaseModel):
    name: str = Field(..., description="Unique node identifier")
    function_name: str = Field(..., description="Name of the function to execute")
    description: Optional[str] = Field(None, description="Node description")
    
    class Config:
        arbitrary_types_allowed = True


class Edge(BaseModel):
    from_node: str = Field(..., description="Source node name")
    to_node: Union[str, ConditionalEdge] = Field(..., description="Target node or conditional edge")
    
    class Config:
        arbitrary_types_allowed = True


class Graph(BaseModel):
    graph_id: Optional[str] = Field(None, description="Unique graph identifier")
    name: str = Field(..., description="Graph name")
    description: Optional[str] = Field(None, description="Graph description")
    nodes: List[Node] = Field(..., description="List of nodes in the graph")
    edges: List[Edge] = Field(..., description="List of edges connecting nodes")
    start_node: str = Field(..., description="Name of the starting node")
    
    class Config:
        arbitrary_types_allowed = True
    
    def get_node(self, name: str) -> Optional[Node]:
        for node in self.nodes:
            if node.name == name:
                return node
        return None
    
    def get_next_node(self, current_node: str) -> Optional[Union[str, ConditionalEdge]]:
        for edge in self.edges:
            if edge.from_node == current_node:
                return edge.to_node
        return None
