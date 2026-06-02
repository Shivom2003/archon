from archon.generators.base import BaseGenerator


class SpecGenerator(BaseGenerator):
    template_name = "SPEC.md.j2"
    output_filename = "SPEC.md"
