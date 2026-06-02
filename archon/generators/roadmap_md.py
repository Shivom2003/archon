from archon.generators.base import BaseGenerator
from archon.models.spec import ArchitectSpec
from archon.plan_registry import get_plan_config


class RoadmapGenerator(BaseGenerator):
    template_name = "ROADMAP.md.j2"
    output_filename = "ROADMAP.md"

    def _extra_context(self) -> dict:
        """Inject checkpoint data keyed by phase number."""
        spec = self.spec
        plan_configs = {
            tool: get_plan_config(tool, spec.project.get_subscription(tool) or "pro")
            for tool in spec.project.agentic_tools
        }
        return {"plan_configs": plan_configs}
