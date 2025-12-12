"""
Code Review Mini-Agent Workflow Implementation.

This workflow analyzes Python code and iteratively improves quality.
Steps:
1. Extract functions from code
2. Check complexity
3. Detect issues
4. Suggest improvements
5. Loop until quality_score >= threshold
"""
import re
import ast
from typing import Dict, Any
from app.models.state import WorkflowState
from app.core.tools import register_tool


@register_tool("extract_functions")
def extract_functions(state: WorkflowState) -> WorkflowState:
    """Extract function definitions from Python code."""
    code = state.get("code", "")
    
    if not code:
        state.set("functions", [])
        state.set("function_count", 0)
        return state
    
    try:
        # Parse the code using AST
        tree = ast.parse(code)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function info
                func_info = {
                    "name": node.name,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "num_lines": (node.end_lineno - node.lineno + 1) if hasattr(node, 'end_lineno') else 1
                }
                functions.append(func_info)
        
        state.set("functions", functions)
        state.set("function_count", len(functions))
        
    except SyntaxError as e:
        state.set("functions", [])
        state.set("function_count", 0)
        state.set("parse_error", str(e))
    
    return state


@register_tool("check_complexity")
def check_complexity(state: WorkflowState) -> WorkflowState:
    """Check code complexity (simplified cyclomatic complexity)."""
    code = state.get("code", "")
    functions = state.get("functions", [])
    
    complexity_scores = []
    
    for func in functions:
        # Simple complexity: count decision points
        # In real implementation, use proper cyclomatic complexity
        func_name = func["name"]
        
        # Count if, for, while, and, or, except
        complexity = 1  # Base complexity
        
        # Extract function code (simplified)
        lines = code.split('\n')
        func_code = '\n'.join(lines[func["line_start"]-1:func["line_end"]])
        
        # Count decision points
        complexity += func_code.count('if ')
        complexity += func_code.count('elif ')
        complexity += func_code.count('for ')
        complexity += func_code.count('while ')
        complexity += func_code.count(' and ')
        complexity += func_code.count(' or ')
        complexity += func_code.count('except')
        
        complexity_scores.append({
            "function": func_name,
            "complexity": complexity,
            "lines": func["num_lines"]
        })
    
    # Calculate average complexity
    avg_complexity = sum(s["complexity"] for s in complexity_scores) / len(complexity_scores) if complexity_scores else 0
    
    state.set("complexity_scores", complexity_scores)
    state.set("avg_complexity", avg_complexity)
    
    return state


@register_tool("detect_issues")
def detect_issues(state: WorkflowState) -> WorkflowState:
    """Detect code quality issues."""
    functions = state.get("functions", [])
    complexity_scores = state.get("complexity_scores", [])
    
    issues = []
    
    for i, func in enumerate(functions):
        func_name = func["name"]
        num_lines = func["num_lines"]
        
        # Issue: Function too long
        if num_lines > 50:
            issues.append({
                "type": "long_function",
                "function": func_name,
                "severity": "medium",
                "message": f"Function '{func_name}' is {num_lines} lines long (recommended: < 50)"
            })
        
        # Issue: High complexity
        if i < len(complexity_scores):
            complexity = complexity_scores[i]["complexity"]
            if complexity > 10:
                issues.append({
                    "type": "high_complexity",
                    "function": func_name,
                    "severity": "high",
                    "message": f"Function '{func_name}' has complexity {complexity} (recommended: < 10)"
                })
        
        # Issue: Too many parameters
        if len(func["args"]) > 5:
            issues.append({
                "type": "too_many_params",
                "function": func_name,
                "severity": "low",
                "message": f"Function '{func_name}' has {len(func['args'])} parameters (recommended: < 5)"
            })
    
    state.set("issues", issues)
    state.set("issue_count", len(issues))
    
    return state


@register_tool("suggest_improvements")
def suggest_improvements(state: WorkflowState) -> WorkflowState:
    """Generate improvement suggestions based on detected issues."""
    issues = state.get("issues", [])
    
    suggestions = []
    
    for issue in issues:
        if issue["type"] == "long_function":
            suggestions.append({
                "function": issue["function"],
                "suggestion": "Consider breaking this function into smaller, more focused functions"
            })
        elif issue["type"] == "high_complexity":
            suggestions.append({
                "function": issue["function"],
                "suggestion": "Reduce complexity by extracting conditional logic into separate functions"
            })
        elif issue["type"] == "too_many_params":
            suggestions.append({
                "function": issue["function"],
                "suggestion": "Consider using a configuration object or dataclass to group related parameters"
            })
    
    state.set("suggestions", suggestions)
    
    return state


@register_tool("calculate_quality_score")
def calculate_quality_score(state: WorkflowState) -> WorkflowState:
    """Calculate overall code quality score (0-10)."""
    issue_count = state.get("issue_count", 0)
    avg_complexity = state.get("avg_complexity", 0)
    function_count = state.get("function_count", 1)
    
    # Start with perfect score
    score = 10.0
    
    # Deduct points for issues
    score -= min(issue_count * 0.5, 5)  # Max 5 points deduction for issues
    
    # Deduct points for high average complexity
    if avg_complexity > 10:
        score -= min((avg_complexity - 10) * 0.3, 3)  # Max 3 points for complexity
    
    # Ensure score is between 0 and 10
    score = max(0, min(10, score))
    
    state.set("quality_score", round(score, 2))
    state.set("iteration", state.get("iteration", 0) + 1)
    
    return state


def get_code_review_workflow_definition() -> Dict[str, Any]:
    """
    Get the code review workflow definition.
    This can be used to create the graph via API.
    """
    return {
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
                    "true_node": "analyze",  # Loop back if quality is low
                    "false_node": "END"  # End if quality is good
                }
            }
        ],
        "start_node": "extract"
    }
