from archon.generators.base import BaseGenerator


class DecisionsGenerator(BaseGenerator):
    template_name = "DECISIONS.md.j2"
    output_filename = "DECISIONS.md"
