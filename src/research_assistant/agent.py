"""The research project formatting agent and its single skill."""

from pathlib import Path

from agents import Agent, Runner, function_tool

from research_assistant.provider import build_model
from research_assistant.scaffold import format_project


AGENT_INSTRUCTIONS = """You are a concise research project assistant.

You may answer questions about the research project structure. You have exactly
one action skill: format_research_project. Call it only when the user asks you
to create, organize, initialize, or preview the project structure. The skill is
additive and never overwrites existing work. After using it, briefly summarize
the result and remind the user that existing files were preserved.
"""


def create_agent(project_path: Path) -> Agent:
    """Create an agent whose formatting skill is bound to one project path."""

    resolved_path = project_path.expanduser().resolve()

    @function_tool(name_override="format_research_project")
    def format_current_project(dry_run: bool = False) -> str:
        """Create a maintainable structure in the current research project.

        Args:
            dry_run: If true, only describe changes without writing files.
        """

        return format_project(resolved_path, dry_run=dry_run).as_text()

    return Agent(
        name="Research project formatter",
        instructions=(
            f"{AGENT_INSTRUCTIONS}\nThe current project is {resolved_path}. "
            "Never operate on another path."
        ),
        model=build_model(),
        tools=[format_current_project],
    )


async def run_chat_agent(path: Path, message: str) -> str:
    """Send one message to the agent for a specific project folder."""

    if not message.strip():
        raise ValueError("Message cannot be empty.")

    result = await Runner.run(create_agent(path), message)
    return str(result.final_output)


async def run_format_agent(path: Path, *, dry_run: bool = False) -> str:
    """Ask the agent to format one project folder."""

    request = (
        "Format the current research project. "
        f"Set dry_run to {str(dry_run).lower()}."
    )
    return await run_chat_agent(path, request)

