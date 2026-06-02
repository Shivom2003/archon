"""
Archon CLI — entry point for all commands.

Commands:
  archon init      Run interview → generate .architect/
  archon show      Display current .architect/ spec
  archon update    Re-interview → update spec
  archon export    Re-export a specific file
  archon validate  Check spec against schema version
"""

import asyncio
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

load_dotenv()

console = Console()

DEFAULT_OUTPUT_DIR = Path(".architect")


# ── Helpers ──────────────────────────────────────────────────────────────────


def _load_spec(output_dir: Path):
    """Load ArchitectSpec from .architect/spec.json. Exits with error if missing."""
    from archon.models.spec import ArchitectSpec

    spec_path = output_dir / "spec.json"
    if not spec_path.exists():
        console.print("[red]No .architect/spec.json found.[/red] Run [bold]archon init[/bold] first.")
        raise SystemExit(1)
    return ArchitectSpec.from_json(spec_path.read_text(encoding="utf-8"))


def _write_all(spec, output_dir: Path) -> None:
    """Run all generators and write output files."""
    from archon.generators import all_generators

    generators = all_generators(spec)
    for gen in generators:
        path = gen.write(output_dir)
        console.print(f"  [green]✓[/green] {path.relative_to(output_dir.parent)}")

    # Also save the raw spec JSON for future re-exports
    spec_path = output_dir / "spec.json"
    spec_path.write_text(spec.to_json(), encoding="utf-8")
    console.print(f"  [green]✓[/green] {spec_path.relative_to(output_dir.parent)}")


# ── Commands ─────────────────────────────────────────────────────────────────


@click.group()
@click.version_option(package_name="archon")
def main() -> None:
    """Archon — AI-powered project architecture specification generator."""


@main.command()
@click.option(
    "--output-dir",
    "-o",
    default=str(DEFAULT_OUTPUT_DIR),
    show_default=True,
    help="Directory to write .architect/ files into.",
)
@click.option(
    "--model",
    "-m",
    default=None,
    help="Override the LLM model (default: claude-sonnet-4-5).",
)
@click.option(
    "--skip-phase2",
    is_flag=True,
    default=False,
    help="Skip the AI interview (Phase 2) and synthesise from Phase 1 only.",
)
def init(output_dir: str, model: str | None, skip_phase2: bool) -> None:
    """Run the full interview and generate .architect/ files."""
    asyncio.run(_init_async(Path(output_dir), model, skip_phase2))


async def _init_async(output_dir: Path, model: str | None, skip_phase2: bool) -> None:
    from archon.interviewer import run_phase1, run_phase2
    from archon.llm.registry import get_client
    from archon.session import InterviewSession, SessionState
    from archon.synthesizer import synthesize

    # Check for existing session
    session = InterviewSession.load(output_dir)
    if (
        session
        and session.state == SessionState.COMPLETE
        and not click.confirm(
            f"An existing spec for '{session.config.name}' was found. Overwrite?",
            default=False,
        )
    ):
        console.print("Aborted.")
        return

    session = InterviewSession()

    # Phase 1
    config = run_phase1()
    session.config = config
    session.state = SessionState.PHASE2
    session.save(output_dir)

    # Phase 2
    if not skip_phase2:
        llm = get_client(model)
        phase2 = await run_phase2(config, llm)
        session.phase2 = phase2
    else:
        from archon.models.interview import Phase2Data

        session.phase2 = Phase2Data()
        console.print("[yellow]Skipping Phase 2 (--skip-phase2 flag set).[/yellow]")

    session.state = SessionState.SYNTHESIZING
    session.save(output_dir)

    # Synthesis
    console.print()
    with console.status("[bold cyan]Generating architecture specification...[/bold cyan]", spinner="dots"):
        llm = get_client(model)
        spec = await synthesize(config, session.phase2, llm)

    session.spec = spec
    session.state = SessionState.COMPLETE
    session.save(output_dir)

    # Write all files
    console.print()
    console.print(Panel("[bold green]Writing .architect/ files[/bold green]", expand=False))
    _write_all(spec, output_dir)

    console.print()
    console.print(
        Panel(
            f"[bold green]Done![/bold green] Architecture spec for "
            f"[bold]{config.name}[/bold] written to [cyan]{output_dir}/[/cyan]\n\n"
            "Next steps:\n"
            "  1. Review [cyan].architect/SPEC.md[/cyan] for the overview\n"
            "  2. Read [cyan].architect/ROADMAP.md[/cyan] before starting Phase 1\n"
            "  3. Open your agentic tool and point it at [cyan].architect/CLAUDE.md[/cyan] "
            "(or AGENTS.md)",
            expand=False,
        )
    )


@main.command()
@click.option("--output-dir", "-o", default=str(DEFAULT_OUTPUT_DIR), show_default=True)
def show(output_dir: str) -> None:
    """Display the current architecture spec in the terminal."""
    spec = _load_spec(Path(output_dir))

    console.print(
        Panel(
            f"[bold cyan]{spec.project.name}[/bold cyan]  "
            f"[dim]v{spec.schema_version} · {spec.generated_at.strftime('%Y-%m-%d')}[/dim]",
            expand=False,
        )
    )
    console.print(f"\n{spec.project.description}\n")

    # Summary table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("Type", spec.project.project_type.label)
    table.add_row("Consumer Scale", spec.project.consumer_scale.label)
    table.add_row("Dev Scale", spec.project.dev_scale.label)
    table.add_row("Architecture", spec.architecture.architecture_style)
    table.add_row("Tools", ", ".join(t.label for t in spec.project.agentic_tools))
    table.add_row("Est. turns", str(spec.roadmap.total_estimated_turns))
    console.print(table)
    console.print()

    # Feature tree
    tree = Tree("[bold]Core Features[/bold]")
    for f in spec.phase2.core_features:
        tree.add(f"[cyan]{f.name}[/cyan] [{f.priority.value}]  {f.description}")
    console.print(tree)
    console.print()

    # Roadmap summary
    rtable = Table(title="Roadmap", show_header=True, header_style="bold")
    rtable.add_column("Phase", style="cyan")
    rtable.add_column("Name")
    rtable.add_column("Agent")
    rtable.add_column("Turns", justify="right")
    rtable.add_column("Checkpoint?", justify="center")
    for phase in spec.roadmap.phases:
        rtable.add_row(
            str(phase.number),
            phase.name,
            phase.primary_agent.label,
            str(phase.estimated_turns_total),
            "⚠️" if phase.checkpoint else "—",
        )
    console.print(rtable)
    console.print()

    console.print(
        f"[dim]Files: {Path(output_dir).resolve()}[/dim]  "
        "[dim]Run [bold]archon show --help[/bold] for more options[/dim]"
    )


@main.command()
@click.option("--output-dir", "-o", default=str(DEFAULT_OUTPUT_DIR), show_default=True)
@click.option("--model", "-m", default=None)
def update(output_dir: str, model: str | None) -> None:
    """Re-run the interview and update the architecture spec."""
    console.print("[yellow]Re-running interview — existing spec will be updated.[/yellow]")
    asyncio.run(_init_async(Path(output_dir), model, skip_phase2=False))


@main.command()
@click.option("--output-dir", "-o", default=str(DEFAULT_OUTPUT_DIR), show_default=True)
@click.option(
    "--format",
    "-f",
    "fmt",
    type=click.Choice(
        [
            "spec-md",
            "architecture-md",
            "roadmap-md",
            "decisions-md",
            "agents-md",
            "claude-md",
            "all",
        ],
        case_sensitive=False,
    ),
    default="all",
    show_default=True,
    help="Which file to regenerate.",
)
def export(output_dir: str, fmt: str) -> None:
    """Re-export one or all .architect/ files from the saved spec."""
    from archon.generators import (
        AgentsMdGenerator,
        ArchitectureGenerator,
        ClaudeMdGenerator,
        DecisionsGenerator,
        RoadmapGenerator,
        SpecGenerator,
        all_generators,
    )

    spec = _load_spec(Path(output_dir))
    out = Path(output_dir)

    generator_map = {
        "spec-md": SpecGenerator,
        "architecture-md": ArchitectureGenerator,
        "roadmap-md": RoadmapGenerator,
        "decisions-md": DecisionsGenerator,
        "agents-md": AgentsMdGenerator,
        "claude-md": ClaudeMdGenerator,
    }

    gens = all_generators(spec) if fmt == "all" else [generator_map[fmt](spec)]

    for gen in gens:
        path = gen.write(out)
        console.print(f"  [green]✓[/green] Exported {path}")


@main.command()
@click.option("--output-dir", "-o", default=str(DEFAULT_OUTPUT_DIR), show_default=True)
def validate(output_dir: str) -> None:
    """Validate the .architect/ spec against the current schema."""
    try:
        spec = _load_spec(Path(output_dir))
        console.print(
            f"[green]✓[/green] Valid — schema v{spec.schema_version}, "
            f"project: [bold]{spec.project.name}[/bold], "
            f"{len(spec.roadmap.phases)} phases, "
            f"{len(spec.decisions)} ADRs."
        )
    except Exception as e:
        console.print(f"[red]✗ Validation failed:[/red] {e}")
        raise SystemExit(1) from None
