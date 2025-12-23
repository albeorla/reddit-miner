# Track Specification: CI/CD Pipeline and Pre-commit Hooks

## Overview
This track implements a lightweight GitHub Actions pipeline to automate code quality checks (linting, formatting, and testing) and integrates pre-commit hooks for local development. It also ensures the project README reflects current test coverage via a third-party badge.

## Functional Requirements
1.  **GitHub Actions Workflow:**
    - Create a `.github/workflows/ci.yml` file.
    - Trigger the workflow on every `push` and `pull_request` to the `main` branch.
    - **Linting:** Execute `ruff check` to ensure code quality.
    - **Formatting:** Execute `ruff format --check` to ensure consistent code style.
    - **Testing & Coverage:** Run `pytest --cov=src` and generate a coverage report (e.g., XML).
2.  **Coverage Badge:**
    - Integrate the CI pipeline with a third-party service (e.g., Codecov) to host coverage reports.
    - Add the resulting coverage badge to the `README.md`.
3.  **Pre-commit Integration:**
    - Configure `pre-commit` to run locally before commits.
    - **Hooks:** Include `ruff check --fix` and `ruff format`.
4.  **README Updates:**
    - Clean up the `README.md` and ensure it has clear instructions for running tests and linting locally.

## Non-Functional Requirements
- **Efficiency:** The GitHub Actions pipeline should be fast and lightweight.
- **Developer Experience:** Pre-commit hooks should be easy to install and run automatically.

## Acceptance Criteria
- [ ] GitHub Actions workflow passes successfully on a Pull Request.
- [ ] `pre-commit` hooks correctly identify and fix (or report) linting/formatting issues locally.
- [ ] `README.md` displays a live coverage badge.
- [ ] `README.md` documentation for testing and linting is verified as accurate.

## Out of Scope
- Automated deployment (CD).
- Security scanning beyond basic linting.
- Integration testing with live Reddit API (remain mocked).
