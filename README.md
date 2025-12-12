# Agent Workflow Engine

A minimal workflow/graph engine for executing agent workflows with nodes, edges, state management, branching, and looping capabilities. Built with FastAPI and Python.

## Overview

This project implements a simplified version of a workflow engine (similar to LangGraph) that allows you to:
- Define workflows as graphs with nodes and edges
- Execute nodes sequentially with shared state
- Support conditional branching based on state values
- Implement loops until conditions are met
- Track execution with detailed logs

## Features

### Core Engine
- **Nodes**: Python functions that read and modify shared state
- **State Management**: Pydantic-based state that flows through the workflow
- **Edges**: Simple and conditional routing between nodes
- **Branching**: Conditional routing based on state values (>, <, >=, <=, ==, !=)
- **Looping**: Support for iterative execution until conditions are met
- **Execution Logging**: Step-by-step execution tracking

### API Endpoints
- `POST /graph/create` - Create a new workflow graph
- `POST /graph/run` - Execute a graph with initial state
- `GET /graph/state/{run_id}` - Retrieve execution state and logs
- `GET /health` - Health check endpoint

### Sample Workflow: Code Review Mini-Agent

The project includes a complete implementation of a code review workflow that:
1. **Extracts functions** from Python code using AST parsing
2. **Checks complexity** using simplified cyclomatic complexity
3. **Detects issues** like long functions, high complexity, too many parameters
4. **Suggests improvements** based on detected issues
5. **Calculates quality score** (0-10 scale)
6. **Loops** until quality score >= 7.0 or max iterations reached

## Project Structure

```
agent-workflow-engine/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   ├── graph.py           # Graph, Node, Edge models
│   │   ├── state.py           # State management
│   │   └── api.py             # API request/response models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py          # Graph execution engine
│   │   └── tools.py           # Tool registry
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── code_review.py     # Code review workflow
│   ├── storage/
│   │   ├── __init__.py
│   │   └── memory.py          # In-memory storage
│   └── api/
│       ├── __init__.py
│       └── routes.py          # API endpoints
├── requirements.txt
├── start.bat                   # Windows startup script
├── .gitignore
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start (Windows)

1. **Start the server**: In your terminal, run:
   ```bash
   .\start.bat
   ```
   This will create a virtual environment, install dependencies, and start the FastAPI server on `http://localhost:8000`

2. **Run the test demo**: In a new terminal, run:
   ```bash
   python test_demo.py
   ```
   Watch the test results for sample code workflows defined in `test_demo.py`

### Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Usage

### Access API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Example: Create and Run Code Review Workflow

#### 1. Create the Graph

```bash
curl -X POST "http://localhost:8000/graph/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Code Review Mini-Agent",
    "description": "Analyzes Python code quality",
    "nodes": [
      {"name": "extract", "function_name": "extract_functions"},
      {"name": "analyze", "function_name": "check_complexity"},
      {"name": "detect", "function_name": "detect_issues"},
      {"name": "suggest", "function_name": "suggest_improvements"},
      {"name": "score", "function_name": "calculate_quality_score"}
    ],
    "edges": [
      {"from_node": "extract", "to_node": "analyze"},
      {"from_node": "analyze", "to_node": "detect"},
      {"from_node": "detect", "to_node": "suggest"},
      {"from_node": "suggest", "to_node": "score"},
      {
        "from_node": "score",
        "to_node": {
          "condition_key": "quality_score",
          "condition_operator": "<",
          "condition_value": 7.0,
          "true_node": "analyze",
          "false_node": "END"
        }
      }
    ],
    "start_node": "extract"
  }'
```

#### 2. Run the Graph

```bash
curl -X POST "http://localhost:8000/graph/run" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "<graph_id_from_step_1>",
    "initial_state": {
      "code": "def long_function(a, b, c, d, e, f):\n    if a > 0:\n        if b > 0:\n            if c > 0:\n                for i in range(100):\n                    print(i)\n    return a + b"
    }
  }'
```

#### 3. Get Execution State

```bash
curl "http://localhost:8000/graph/state/<run_id>"
```

## What the Engine Supports

✅ **Node Execution**: Execute Python functions as workflow nodes  
✅ **State Flow**: Pydantic-based state management across nodes  
✅ **Simple Edges**: Direct node-to-node transitions  
✅ **Conditional Branching**: Route based on state values with operators (<, >, <=, >=, ==, !=)  
✅ **Looping**: Repeat nodes until conditions are met  
✅ **Tool Registry**: Register and manage callable functions  
✅ **Execution Logging**: Track each step with state snapshots  
✅ **In-Memory Storage**: Store graphs and runs (thread-safe)  
✅ **Error Handling**: Graceful error handling with detailed messages  
✅ **Cycle Detection**: Prevent infinite loops with max iteration limit  

## Architecture

### State Management
- Uses Pydantic models for type safety and validation
- State flows through nodes as a dictionary-like object
- Each node can read and modify the state

### Graph Execution
- Engine traverses the graph starting from `start_node`
- Each node executes its associated tool function
- Edges determine the next node (simple or conditional)
- Execution continues until reaching "END" or max iterations

### Tool Registry
- Global registry for all callable tools
- Tools are registered using the `@register_tool` decorator
- Nodes reference tools by name

## Future Improvements

Given more time, I would add:

1. **Async Execution**: Support for async/await in node functions
2. **WebSocket Streaming**: Real-time execution log streaming
3. **Persistent Storage**: SQLite/PostgreSQL backend option
4. **Parallel Execution**: Run independent nodes in parallel
5. **Graph Validation**: Validate graph structure before execution
6. **Dynamic Graph Modification**: Modify graphs during execution
7. **Better Error Recovery**: Retry logic and fallback nodes
8. **Metrics & Monitoring**: Execution time, success rates, etc.
9. **Graph Visualization**: Visual representation of workflows
10. **More Workflow Examples**: Additional sample workflows
11. **Unit Tests**: Comprehensive test coverage
12. **Authentication**: API key or JWT-based auth
13. **Rate Limiting**: Prevent abuse of API endpoints
14. **Caching**: Cache execution results for identical inputs

## Technical Decisions

### Why In-Memory Storage?
- Simplicity and speed for MVP
- Easy to upgrade to persistent storage later
- Thread-safe implementation with locks

### Why Pydantic?
- Type safety and validation
- Excellent FastAPI integration
- Clear data models

### Why Simple Conditional Logic?
- Covers most use cases
- Easy to understand and debug
- Can be extended to support complex expressions

## Testing

You can test the API using:
- **Swagger UI**: http://localhost:8000/docs (interactive testing)
- **cURL**: Command-line HTTP requests
- **Postman**: Import the OpenAPI schema from `/openapi.json`
- **Python requests**: Write custom test scripts

## License

This project is created as part of an AI Engineering internship assignment.

## Author

Created for Tredence AI Engineering Internship Assignment
