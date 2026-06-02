from archon.generators.base import BaseGenerator


class ArchitectureGenerator(BaseGenerator):
    template_name = "ARCHITECTURE.md.j2"
    output_filename = "ARCHITECTURE.md"
