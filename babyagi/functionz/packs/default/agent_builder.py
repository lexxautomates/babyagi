# agent_builder.py
"""
Agent Builder Module for BabyAGI Self-Building AI Agents
Integrates with Agent Lightning for tracking and monitoring
"""

from functionz.core.framework import func
import json
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

# Agent Lightning configuration
AGL_STORE_URL = os.getenv('AGL_STORE_URL', 'http://localhost:45993')
AGL_ENABLED = os.getenv('AGL_ENABLED', 'true').lower() == 'true'

# In-memory store for created agents (could be moved to database)
_created_agents: Dict[str, Dict] = {}

@func.register_function(
    metadata={
        "description": "Create a new AI agent with specified capabilities and register with Agent Lightning"
    },
    imports=["json", "uuid", "time", "datetime", "requests"],
    dependencies=["self_build"]
)
def create_agent(description: str, tools: List[str] = None, config: Dict = None) -> Dict:
    """
    Create a new AI agent based on description.
    
    Args:
        description: Natural language description of what the agent should do
        tools: List of tool names the agent should have access to
        config: Optional configuration (model, temperature, etc.)
    
    Returns:
        Dict with agent_id, status, and initial test results
    """
    agent_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    
    # Default tools if not specified
    if tools is None:
        tools = ["get_crypto_price", "get_crypto_market_summary", "search_crypto"]
    
    # Default config
    if config is None:
        config = {
            "model": os.getenv('OLLAMA_MODEL', 'llama3.2'),
            "temperature": 0.7,
            "max_tokens": 1000
        }
    
    # Create agent record
    agent = {
        "agent_id": agent_id,
        "description": description,
        "tools": tools,
        "config": config,
        "created_at": timestamp,
        "status": "initializing",
        "queries_processed": 0,
        "successful_queries": 0,
        "failed_queries": 0,
        "total_reward": 0.0,
        "test_results": []
    }
    
    # Register with Agent Lightning
    if AGL_ENABLED:
        try:
            import requests
            response = requests.post(
                f"{AGL_STORE_URL}/agent/register",
                json={
                    "agent_id": agent_id,
                    "description": description,
                    "tools": tools,
                    "config": config,
                    "created_at": timestamp
                },
                timeout=5
            )
            if response.status_code == 200:
                agent["agl_registered"] = True
                agent["agl_agent_id"] = response.json().get("agent_id", agent_id)
            else:
                agent["agl_registered"] = False
                agent["agl_error"] = response.text
        except Exception as e:
            agent["agl_registered"] = False
            agent["agl_error"] = str(e)
    else:
        agent["agl_registered"] = False
        agent["agl_error"] = "Agent Lightning disabled"
    
    # Store agent
    _created_agents[agent_id] = agent
    
    # Run self-build to generate test queries and validate
    try:
        # Import self_build function
        from babyagi.functionz.packs.drafts.self_build import self_build
        
        # Generate and process test queries
        test_results = self_build(description, X=3)
        
        agent["test_results"] = test_results
        agent["status"] = "active"
        agent["queries_processed"] = len(test_results)
        agent["successful_queries"] = sum(1 for r in test_results if r.get("output") and not r.get("error"))
        agent["failed_queries"] = sum(1 for r in test_results if r.get("error"))
        
    except Exception as e:
        agent["status"] = "error"
        agent["error"] = str(e)
    
    # Update in store
    _created_agents[agent_id] = agent
    
    return agent


@func.register_function(
    metadata={
        "description": "List all created AI agents"
    },
    imports=["json"]
)
def list_agents() -> List[Dict]:
    """
    List all created AI agents.
    
    Returns:
        List of agent dictionaries with summary info
    """
    agents = []
    for agent_id, agent in _created_agents.items():
        agents.append({
            "agent_id": agent_id,
            "description": agent.get("description", "")[:100],
            "status": agent.get("status", "unknown"),
            "created_at": agent.get("created_at"),
            "queries_processed": agent.get("queries_processed", 0),
            "success_rate": _calculate_success_rate(agent)
        })
    return agents


@func.register_function(
    metadata={
        "description": "Get detailed information about a specific agent"
    },
    imports=["json"]
)
def get_agent(agent_id: str) -> Optional[Dict]:
    """
    Get detailed information about a specific agent.
    
    Args:
        agent_id: The agent's unique identifier
    
    Returns:
        Agent dictionary or None if not found
    """
    return _created_agents.get(agent_id)


@func.register_function(
    metadata={
        "description": "Test an agent with a specific query"
    },
    imports=["json", "requests"],
    dependencies=["process_user_input"]
)
def test_agent(agent_id: str, query: str) -> Dict:
    """
    Test an agent with a specific query.
    
    Args:
        agent_id: The agent's unique identifier
        query: The test query to run
    
    Returns:
        Dict with test results
    """
    agent = _created_agents.get(agent_id)
    if not agent:
        return {"error": f"Agent {agent_id} not found"}
    
    start_time = time.time()
    
    try:
        # Process the query through BabyAGI
        from babyagi.functionz.packs.default.function_calling_chat import process_user_input
        result = process_user_input(query)
        
        elapsed_time = time.time() - start_time
        
        # Update agent stats
        agent["queries_processed"] = agent.get("queries_processed", 0) + 1
        agent["successful_queries"] = agent.get("successful_queries", 0) + 1
        
        # Emit reward to Agent Lightning
        if AGL_ENABLED and agent.get("agl_registered"):
            try:
                import requests
                requests.post(
                    f"{AGL_STORE_URL}/reward",
                    json={
                        "agent_id": agent_id,
                        "reward": 1.0,
                        "query": query,
                        "elapsed_time": elapsed_time
                    },
                    timeout=5
                )
                agent["total_reward"] = agent.get("total_reward", 0) + 1.0
            except Exception:
                pass
        
        return {
            "agent_id": agent_id,
            "query": query,
            "result": result,
            "elapsed_time": elapsed_time,
            "status": "success"
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        agent["failed_queries"] = agent.get("failed_queries", 0) + 1
        
        return {
            "agent_id": agent_id,
            "query": query,
            "error": str(e),
            "elapsed_time": elapsed_time,
            "status": "error"
        }


@func.register_function(
    metadata={
        "description": "Delete an agent"
    },
    imports=["json"]
)
def delete_agent(agent_id: str) -> Dict:
    """
    Delete an agent.
    
    Args:
        agent_id: The agent's unique identifier
    
    Returns:
        Dict with deletion status
    """
    if agent_id not in _created_agents:
        return {"error": f"Agent {agent_id} not found", "deleted": False}
    
    del _created_agents[agent_id]
    
    return {"agent_id": agent_id, "deleted": True}


@func.register_function(
    metadata={
        "description": "Get agent statistics for dashboard"
    },
    imports=["json", "requests"]
)
def get_agent_stats() -> Dict:
    """
    Get overall statistics about created agents.
    
    Returns:
        Dict with aggregate statistics
    """
    total_agents = len(_created_agents)
    active_agents = sum(1 for a in _created_agents.values() if a.get("status") == "active")
    total_queries = sum(a.get("queries_processed", 0) for a in _created_agents.values())
    total_successful = sum(a.get("successful_queries", 0) for a in _created_agents.values())
    total_failed = sum(a.get("failed_queries", 0) for a in _created_agents.values())
    
    # Get Agent Lightning stats if available
    agl_stats = {}
    if AGL_ENABLED:
        try:
            import requests
            response = requests.get(f"{AGL_STORE_URL}/stats", timeout=5)
            if response.status_code == 200:
                agl_stats = response.json()
        except Exception:
            agl_stats = {"error": "Could not fetch Agent Lightning stats"}
    
    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "total_queries": total_queries,
        "successful_queries": total_successful,
        "failed_queries": total_failed,
        "success_rate": round(total_successful / total_queries * 100, 1) if total_queries > 0 else 0,
        "agl_stats": agl_stats
    }


def _calculate_success_rate(agent: Dict) -> float:
    """Calculate success rate for an agent."""
    total = agent.get("queries_processed", 0)
    successful = agent.get("successful_queries", 0)
    if total == 0:
        return 0.0
    return round(successful / total * 100, 1)