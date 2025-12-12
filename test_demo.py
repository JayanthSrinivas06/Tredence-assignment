"""
Sample test/demo script for the Agent Workflow Engine.
This demonstrates how to use the API programmatically.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_health():
    print("Testing health endpoint...")

    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

    return response.status_code == 200


def create_code_review_graph():
    print("Creating Code Review workflow graph...")
    
    graph_data = {
        "name": "Code Review Mini-Agent",
        "description": "Analyzes Python code and iteratively improves quality",
        "nodes": [
            {
                "name": "extract",
                "function_name": "extract_functions",
                "description": "Extract function definitions from code"
            },
            {
                "name": "analyze",
                "function_name": "check_complexity",
                "description": "Check code complexity"
            },
            {
                "name": "detect",
                "function_name": "detect_issues",
                "description": "Detect code quality issues"
            },
            {
                "name": "suggest",
                "function_name": "suggest_improvements",
                "description": "Generate improvement suggestions"
            },
            {
                "name": "score",
                "function_name": "calculate_quality_score",
                "description": "Calculate quality score"
            }
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
    }
    
    response = requests.post(f"{BASE_URL}/graph/create", json=graph_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}\n")
    
    return result.get("graph_id")


def run_code_review(graph_id):
    """Run the code review workflow with sample code."""
    print("Running Code Review workflow...")
    
    # Sample Python code with some quality issues
    sample_code = """
def complex_function(a, b, c, d, e, f, g):
    '''A function with too many parameters and high complexity.'''
    result = 0
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    for i in range(100):
                        for j in range(50):
                            if i % 2 == 0:
                                if j % 2 == 0:
                                    result += i * j
                                else:
                                    result -= i * j
                            else:
                                result += i + j
    return result + e + f + g

def another_long_function():
    '''This function is very long.'''
    x = 1
    y = 2
    z = 3
    # Imagine 50+ more lines here
    for i in range(10):
        x += i
        y += i * 2
        z += i * 3
    return x + y + z
"""
    
    run_data = {
        "graph_id": graph_id,
        "initial_state": {
            "code": sample_code,
            "iteration": 0
        }
    }
    
    response = requests.post(f"{BASE_URL}/graph/run", json=run_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"\n{'='*60}")
    print("EXECUTION RESULTS")
    print(f"{'='*60}")
    print(f"Run ID: {result.get('run_id')}")
    print(f"Status: {result.get('status')}")
    print(f"\nFinal State:")
    final_state = result.get('final_state', {}).get('data', {})
    print(f"  - Functions Found: {final_state.get('function_count', 0)}")
    print(f"  - Issues Detected: {final_state.get('issue_count', 0)}")
    print(f"  - Quality Score: {final_state.get('quality_score', 0)}/10")
    print(f"  - Iterations: {final_state.get('iteration', 0)}")
    
    print(f"\n{'='*60}")
    print("EXECUTION LOG")
    print(f"{'='*60}")
    for log in result.get('execution_log', []):
        print(f"Step {log['step']}: {log['node']} - {log['status']}")
        print(f"  Message: {log['message']}")
    
    print(f"\n{'='*60}")
    print("DETECTED ISSUES")
    print(f"{'='*60}")
    issues = final_state.get('issues', [])
    for i, issue in enumerate(issues, 1):
        print(f"{i}. [{issue['severity'].upper()}] {issue['type']}")
        print(f"   Function: {issue['function']}")
        print(f"   {issue['message']}")
    
    print(f"\n{'='*60}")
    print("SUGGESTIONS")
    print(f"{'='*60}")
    suggestions = final_state.get('suggestions', [])
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. Function: {suggestion['function']}")
        print(f"   {suggestion['suggestion']}")
    
    print(f"\n{'='*60}\n")
    
    return result.get('run_id')


def get_run_state(run_id):
    """Get the state of a completed run."""
    print(f"Retrieving state for run: {run_id}...")
    
    response = requests.get(f"{BASE_URL}/graph/state/{run_id}")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Run Status: {result.get('status')}\n")
    
    return result


def main():
    """Main test function."""
    print("\n" + "="*60)
    print("AGENT WORKFLOW ENGINE - DEMO")
    print("="*60 + "\n")
    
    try:
        # Test health
        if not test_health():
            print("❌ Server is not running. Please start the server first.")
            print("Run: start.bat")
            return
        
        print("✅ Server is healthy\n")
        
        # Create graph
        graph_id = create_code_review_graph()
        if not graph_id:
            print("❌ Failed to create graph")
            return
        
        print(f"✅ Graph created: {graph_id}\n")
        
        # Run workflow
        run_id = run_code_review(graph_id)
        if not run_id:
            print("❌ Failed to run workflow")
            return
        
        print(f"✅ Workflow completed: {run_id}\n")
        
        # Get state (optional verification)
        state = get_run_state(run_id)
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print("Please make sure the server is running:")
        print("  1. Run: start.bat")
        print("  2. Wait for server to start")
        print("  3. Run this script again\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")


if __name__ == "__main__":
    main()
