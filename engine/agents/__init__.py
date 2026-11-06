"""AI_Flow autonomous agents package.
Importing this package automatically registers all 30 skills and 60 personas in AgentRegistry.
"""

from engine.agents import phase1_architecture
from engine.agents import phase2_execution
from engine.agents import phase3_release
from engine.agents import phase4_design_frontend
from engine.agents import phase5_api_data_perf
from engine.agents import phase6_devops_finops
from engine.agents import phase7_freelance_ops
from engine.agents import phase8_growth_founder

__all__ = [
    "phase1_architecture",
    "phase2_execution",
    "phase3_release",
    "phase4_design_frontend",
    "phase5_api_data_perf",
    "phase6_devops_finops",
    "phase7_freelance_ops",
    "phase8_growth_founder",
]
