"""
Graph execution engine.
"""
from typing import Any, Dict, List, Optional
import logging
from app.models.state import WorkflowState
from app.models.graph import Graph, Node, ConditionalEdge
from app.models.api import ExecutionLog
from app.core.tools import get_tool_registry

logger = logging.getLogger(__name__)


class GraphEngine:
    """Engine for executing workflow graphs."""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.tool_registry = get_tool_registry()
        self.execution_log: List[ExecutionLog] = []
        self.step_counter = 0
        self.max_iterations = 100  # Prevent infinite loops
    
    def execute(self, initial_state: Dict[str, Any]) -> tuple[WorkflowState, List[ExecutionLog]]:
        """
        Execute the graph with the given initial state.
        Returns final state and execution log.
        """
        state = WorkflowState(data=initial_state)
        self.execution_log = []
        self.step_counter = 0
        
        current_node_name = self.graph.start_node
        visited_nodes = []
        
        logger.info(f"Starting graph execution: {self.graph.name}")
        
        while current_node_name and current_node_name != "END":
            if self.step_counter >= self.max_iterations:
                self._log_step(
                    current_node_name,
                    "error",
                    f"Maximum iterations ({self.max_iterations}) reached. Possible infinite loop.",
                    state
                )
                break
            
            # Get the node
            node = self.graph.get_node(current_node_name)
            if not node:
                self._log_step(
                    current_node_name,
                    "error",
                    f"Node '{current_node_name}' not found in graph",
                    state
                )
                break
            
            # Execute the node
            try:
                state = self._execute_node(node, state)
                self._log_step(
                    current_node_name,
                    "success",
                    f"Node '{current_node_name}' executed successfully",
                    state
                )
            except Exception as e:
                self._log_step(
                    current_node_name,
                    "error",
                    f"Error executing node '{current_node_name}': {str(e)}",
                    state
                )
                logger.error(f"Error in node {current_node_name}: {e}", exc_info=True)
                break
            
            # Get next node
            next_node = self.graph.get_next_node(current_node_name)
            
            if next_node is None:
                # No more nodes, end execution
                current_node_name = "END"
            elif isinstance(next_node, str):
                # Simple edge
                current_node_name = next_node
            elif isinstance(next_node, dict):
                # Conditional edge (from JSON)
                current_node_name = self._evaluate_condition(next_node, state)
            else:
                # ConditionalEdge object
                current_node_name = self._evaluate_conditional_edge(next_node, state)
            
            visited_nodes.append(current_node_name)
        
        logger.info(f"Graph execution completed. Total steps: {self.step_counter}")
        return state, self.execution_log
    
    def _execute_node(self, node: Node, state: WorkflowState) -> WorkflowState:
        """Execute a single node."""
        # Get the tool function
        if not self.tool_registry.has(node.function_name):
            raise ValueError(f"Function '{node.function_name}' not found in tool registry")
        
        tool_func = self.tool_registry.get(node.function_name)
        
        # Execute the function with the state
        result = tool_func(state)
        
        # Update state if function returns a new state or dict
        if isinstance(result, WorkflowState):
            return result
        elif isinstance(result, dict):
            state.update(result)
            return state
        else:
            # Function modified state in-place
            return state
    
    def _evaluate_condition(self, condition_dict: Dict[str, Any], state: WorkflowState) -> str:
        """Evaluate a condition from dictionary format."""
        condition_key = condition_dict.get("condition_key")
        operator = condition_dict.get("condition_operator")
        condition_value = condition_dict.get("condition_value")
        true_node = condition_dict.get("true_node")
        false_node = condition_dict.get("false_node")
        
        state_value = state.get(condition_key)
        
        result = self._compare_values(state_value, operator, condition_value)
        
        next_node = true_node if result else false_node
        logger.info(f"Condition: {state_value} {operator} {condition_value} = {result}, next: {next_node}")
        
        return next_node
    
    def _evaluate_conditional_edge(self, edge: ConditionalEdge, state: WorkflowState) -> str:
        """Evaluate a conditional edge."""
        state_value = state.get(edge.condition_key)
        
        result = self._compare_values(state_value, edge.condition_operator, edge.condition_value)
        
        next_node = edge.true_node if result else edge.false_node
        logger.info(f"Condition: {state_value} {edge.condition_operator} {edge.condition_value} = {result}, next: {next_node}")
        
        return next_node
    
    def _compare_values(self, left: Any, operator: str, right: Any) -> bool:
        """Compare two values using the given operator."""
        if operator == "<":
            return left < right
        elif operator == ">":
            return left > right
        elif operator == "<=":
            return left <= right
        elif operator == ">=":
            return left >= right
        elif operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def _log_step(self, node: str, status: str, message: str, state: WorkflowState) -> None:
        """Log an execution step."""
        self.step_counter += 1
        log_entry = ExecutionLog(
            step=self.step_counter,
            node=node,
            status=status,
            message=message,
            state_snapshot=state.to_dict()
        )
        self.execution_log.append(log_entry)
