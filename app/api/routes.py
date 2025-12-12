"""
FastAPI routes for the workflow engine.
"""
from fastapi import APIRouter, HTTPException
import uuid
import logging
from app.models.api import (
    CreateGraphRequest,
    CreateGraphResponse,
    RunGraphRequest,
    RunGraphResponse,
    StateResponse
)
from app.models.graph import Graph, Node, Edge
from app.storage import get_storage
from app.core.engine import GraphEngine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/graph/create", response_model=CreateGraphResponse)
async def create_graph(request: CreateGraphRequest):
    """
    Create a new workflow graph.
    
    Args:
        request: Graph definition including nodes and edges
    
    Returns:
        Graph ID and success message
    """
    try:
        # Convert request to Graph model
        nodes = [Node(**node_data) for node_data in request.nodes]
        edges = [Edge(**edge_data) for edge_data in request.edges]
        
        graph = Graph(
            name=request.name,
            description=request.description,
            nodes=nodes,
            edges=edges,
            start_node=request.start_node
        )
        
        # Save graph
        storage = get_storage()
        graph_id = storage.save_graph(graph)
        
        logger.info(f"Created graph: {graph_id} - {graph.name}")
        
        return CreateGraphResponse(
            graph_id=graph_id,
            message=f"Graph '{graph.name}' created successfully"
        )
    
    except Exception as e:
        logger.error(f"Error creating graph: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error creating graph: {str(e)}")


@router.post("/graph/run", response_model=RunGraphResponse)
async def run_graph(request: RunGraphRequest):
    """
    Execute a workflow graph with the given initial state.
    
    Args:
        request: Graph ID and initial state
    
    Returns:
        Run ID, final state, and execution log
    """
    try:
        # Get graph from storage
        storage = get_storage()
        graph = storage.get_graph(request.graph_id)
        
        if not graph:
            raise HTTPException(status_code=404, detail=f"Graph '{request.graph_id}' not found")
        
        # Create engine and execute
        engine = GraphEngine(graph)
        final_state, execution_log = engine.execute(request.initial_state)
        
        # Generate run ID
        run_id = str(uuid.uuid4())
        
        # Save run
        storage.save_run(
            run_id=run_id,
            graph_id=request.graph_id,
            state=final_state,
            execution_log=execution_log,
            status="completed"
        )
        
        logger.info(f"Executed graph {request.graph_id}, run ID: {run_id}")
        
        return RunGraphResponse(
            run_id=run_id,
            graph_id=request.graph_id,
            final_state=final_state.to_dict(),
            execution_log=execution_log,
            status="completed"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running graph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error running graph: {str(e)}")


@router.get("/graph/state/{run_id}", response_model=StateResponse)
async def get_state(run_id: str):
    """
    Get the state of a workflow run.
    
    Args:
        run_id: Unique run identifier
    
    Returns:
        Current state and execution log
    """
    try:
        storage = get_storage()
        run = storage.get_run(run_id)
        
        if not run:
            raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
        
        return StateResponse(
            run_id=run_id,
            graph_id=run["graph_id"],
            current_state=run["state"].to_dict(),
            status=run["status"],
            execution_log=run["execution_log"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting state: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting state: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Agent Workflow Engine"}
