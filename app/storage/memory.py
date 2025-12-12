from typing import Dict, Optional, Any
import uuid
from app.models.graph import Graph
from app.models.state import WorkflowState
from app.models.api import ExecutionLog
import threading


class InMemoryStorage:
    def __init__(self):
        self._graphs: Dict[str, Graph] = {}
        self._runs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def save_graph(self, graph: Graph) -> str:
        with self._lock:
            if not graph.graph_id:
                graph.graph_id = str(uuid.uuid4())
            self._graphs[graph.graph_id] = graph
            return graph.graph_id
    
    def get_graph(self, graph_id: str) -> Optional[Graph]:
        with self._lock:
            return self._graphs.get(graph_id)
    
    def save_run(self, run_id: str, graph_id: str, state: WorkflowState, 
                 execution_log: list, status: str) -> None:
        with self._lock:
            self._runs[run_id] = {
                "run_id": run_id,
                "graph_id": graph_id,
                "state": state,
                "execution_log": execution_log,
                "status": status
            }
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._runs.get(run_id)
    
    def list_graphs(self) -> list:
        with self._lock:
            return list(self._graphs.keys())
    
    def list_runs(self) -> list:
        with self._lock:
            return list(self._runs.keys())


# Global storage instance
_storage = InMemoryStorage()


def get_storage() -> InMemoryStorage:
    
    return _storage
