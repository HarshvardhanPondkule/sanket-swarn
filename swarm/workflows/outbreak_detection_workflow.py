"""
Outbreak Detection Workflow
Defines the coordinated workflow for swarm agents
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class WorkflowStep:
    """Represents a step in the workflow"""
    name: str
    description: str
    agent_action: str
    parallel: bool = False
    timeout: int = 30
    condition: str = None
    depends_on: List[str] = None
    agent_selector: str = None


class OutbreakDetectionWorkflow:
    """
    Multi-agent workflow for outbreak detection
    Coordinates agent actions in sequence
    """
    
    name = "outbreak_detection"
    description = "Coordinated workflow for detecting disease outbreaks"
    
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self.steps = self._define_steps()
    
    def _define_steps(self) -> List[WorkflowStep]:
        """Define workflow steps"""
        return [
            WorkflowStep(
                name="local_analysis",
                description="Each agent analyzes its local data",
                agent_action="analyze_symptoms",
                parallel=True,
                timeout=30
            ),
            
            WorkflowStep(
                name="neighbor_consultation",
                description="Agents query neighbors if anomaly detected",
                agent_action="query_neighbors",
                condition="anomaly_detected == true",
                parallel=True,
                timeout=60
            ),
            
            WorkflowStep(
                name="collective_reasoning",
                description="Agents synthesize neighbor responses",
                agent_action="reason_about_collective_evidence",
                depends_on=["neighbor_consultation"],
                parallel=True,
                timeout=45
            ),
            
            WorkflowStep(
                name="consensus_proposal",
                description="Agent with strongest evidence proposes action",
                agent_action="propose_consensus",
                agent_selector="max_outbreak_belief",
                timeout=30
            ),
            
            WorkflowStep(
                name="voting",
                description="All agents vote on proposal",
                agent_action="vote",
                depends_on=["consensus_proposal"],
                parallel=True,
                timeout=60
            ),
            
            WorkflowStep(
                name="quantum_escalation",
                description="Escalate to quantum if consensus reached",
                agent_action="escalate_to_quantum",
                condition="consensus_reached == true",
                agent_selector="proposer",
                timeout=120
            )
        ]
    
    async def execute(self, trigger_data: Dict) -> Dict:
        """
        Execute the workflow
        """
        if not self.orchestrator:
            return {"error": "Orchestrator not configured"}
        
        results = {
            "workflow": self.name,
            "trigger_data": trigger_data,
            "step_results": {}
        }
        
        # Execute each step
        for step in self.steps:
            try:
                step_result = await self._execute_step(step, results)
                results["step_results"][step.name] = step_result
                
                # Check if we should continue
                if not self._should_continue(step, step_result):
                    break
                    
            except Exception as e:
                results["step_results"][step.name] = {"error": str(e)}
                break
        
        return results
    
    async def _execute_step(self, step: WorkflowStep, context: Dict) -> Dict:
        """Execute a single workflow step"""
        
        # Check condition
        if step.condition and not self._evaluate_condition(step.condition, context):
            return {"skipped": True, "reason": f"Condition not met: {step.condition}"}
        
        # Check dependencies
        if step.depends_on:
            for dep in step.depends_on:
                if dep not in context.get("step_results", {}):
                    return {"skipped": True, "reason": f"Dependency not met: {dep}"}
        
        # Select agents
        agents = self._select_agents(step)
        
        # Execute action
        if step.parallel:
            # Execute on all agents in parallel
            results = {}
            for agent_id, agent in agents.items():
                try:
                    result = await self._execute_agent_action(agent, step.agent_action, context)
                    results[agent_id] = result
                except Exception as e:
                    results[agent_id] = {"error": str(e)}
            return {"parallel_results": results}
        else:
            # Execute on selected agent
            if agents:
                agent_id, agent = next(iter(agents.items()))
                return await self._execute_agent_action(agent, step.agent_action, context)
            return {"error": "No agent selected"}
    
    def _select_agents(self, step: WorkflowStep) -> Dict:
        """Select agents for the step"""
        if not self.orchestrator:
            return {}
        
        all_agents = self.orchestrator.agents
        
        if step.agent_selector == "max_outbreak_belief":
            # Select agent with highest outbreak belief
            max_agent = max(all_agents.items(), key=lambda x: x[1].outbreak_belief)
            return {max_agent[0]: max_agent[1]}
        elif step.agent_selector == "proposer":
            # Return first agent (simplified)
            return {list(all_agents.keys())[0]: list(all_agents.values())[0]}
        else:
            # Return all agents
            return all_agents
    
    async def _execute_agent_action(self, agent, action: str, context: Dict) -> Dict:
        """Execute an action on an agent"""
        # Map action to agent method
        if action == "analyze_symptoms":
            return {"action": action, "risk_level": agent.risk_level}
        elif action == "query_neighbors":
            return {"action": action, "neighbors_queried": True}
        elif action == "propose_consensus":
            return {"action": action, "proposal_made": True}
        elif action == "vote":
            return {"action": action, "vote": "approve"}
        elif action == "escalate_to_quantum":
            return {"action": action, "escalated": True}
        else:
            return {"action": action, "status": "completed"}
    
    def _evaluate_condition(self, condition: str, context: Dict) -> bool:
        """Evaluate a condition string"""
        # Simple condition evaluation
        if "anomaly_detected == true" in condition:
            # Check if any agent detected anomaly
            step_results = context.get("step_results", {})
            local_analysis = step_results.get("local_analysis", {})
            parallel_results = local_analysis.get("parallel_results", {})
            
            for result in parallel_results.values():
                if result.get("risk_level") in ["high", "critical"]:
                    return True
            return False
        
        elif "consensus_reached == true" in condition:
            # Check if consensus was reached
            step_results = context.get("step_results", {})
            voting = step_results.get("voting", {})
            return voting.get("consensus_reached", False)
        
        return True
    
    def _should_continue(self, step: WorkflowStep, result: Dict) -> bool:
        """Check if workflow should continue after this step"""
        if result.get("error"):
            return False
        if result.get("skipped"):
            return True  # Continue even if step was skipped
        return True
