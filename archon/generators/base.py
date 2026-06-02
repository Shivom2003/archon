"""Base generator — loads Jinja2 templates and renders markdown."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from archon.models.spec import ArchitectSpec

# Templates live inside the package: archon/templates/
# This ensures they're included in the installed wheel.
_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _get_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


class BaseGenerator:
    """
    Renders a single markdown file from an ArchitectSpec using a Jinja2 template.
    Subclasses set `template_name` and `output_filename`.
    """

    template_name: str = ""        # e.g. "SPEC.md.j2"
    output_filename: str = ""      # e.g. "SPEC.md"

    def __init__(self, spec: ArchitectSpec) -> None:
        self.spec = spec
        self._env = _get_env()

    def render(self) -> str:
        """Render the template to a markdown string."""
        template = self._env.get_template(self.template_name)
        return template.render(spec=self.spec, **self._extra_context())

    def _extra_context(self) -> dict:
        """Override in subclasses to inject extra template variables."""
        return {}

    def write(self, output_dir: Path) -> Path:
        """Render and write to output_dir/output_filename. Returns the written path."""
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / self.output_filename
        path.write_text(self.render(), encoding="utf-8")
        return path
