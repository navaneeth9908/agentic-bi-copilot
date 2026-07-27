from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_packages_cli_runtime_without_local_artifacts():
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
    dockerignore = (PROJECT_ROOT / ".dockerignore").read_text(encoding="utf-8")

    assert "FROM python:3.11-slim" in dockerfile
    assert "pip install --no-cache-dir uv" in dockerfile
    assert "COPY pyproject.toml uv.lock README.md ./" in dockerfile
    assert "COPY src ./src" in dockerfile
    assert "COPY evals ./evals" in dockerfile
    assert "COPY docs ./docs" in dockerfile
    assert "uv sync --frozen --no-dev" in dockerfile
    assert "USER appuser" in dockerfile
    assert 'ENTRYPOINT ["python", "-m", "agentic_bi_copilot.cli"]' in dockerfile
    assert 'CMD ["--list-questions"]' in dockerfile

    for ignored_path in [
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "examples/*.sqlite",
        "*.db",
    ]:
        assert ignored_path in dockerignore


def test_github_actions_ci_runs_pytest_cli_smoke_and_docker_smoke():
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )

    assert "push:" in workflow
    assert "pull_request:" in workflow
    assert 'python-version: "3.11"' in workflow
    assert "uv sync --frozen --group dev" in workflow
    assert "uv run --group dev pytest tests/ -q" in workflow
    assert (
        'uv run python -m agentic_bi_copilot.cli "What is revenue by region?" --limit 2'
        in workflow
    )
    assert "uv run python -m agentic_bi_copilot.cli --completion-checklist" in workflow
    assert "docker build -t agentic-bi-copilot:ci ." in workflow
    assert (
        'docker run --rm agentic-bi-copilot:ci "What is revenue by region?" --limit 2'
        in workflow
    )
