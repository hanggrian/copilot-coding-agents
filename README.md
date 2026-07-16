# Coding Agents

Coding agents for GitHub Copilot in VS Code, built on top of default agents.
Tested only with OpenAI-compatible API.

## Download

Put the agent Markdown files in:

- `.github/agents/` for repository-specific agents.
- `~/.copilot/agents/` for global agents.

## Agents

### Explain

A read-only agent with a tendency to show KaTeX math and Mermaid diagrams when
explaining technical concepts. Helpful to understand codebase of a new project.

```mermaid
stateDiagram-v2
  [*] --> Clarify
  Clarify --> Research
  Research --> [*]
```

### Maintain

Runs validation tasks and fixes issues that arise, one at a time. Suitable for
regression testing after changes have been made.

```mermaid
stateDiagram-v2
  [*] --> Analyze
  Analyze --> Edit
  Edit --> Validate
  Validate --> Edit : still failing
  Validate --> [*] : success
```

### Inspect

A long-running agent to find bugs in the codebase, creating a bug report for
escalation while giving the option to fix immediately. Pair with a frontier
model for best results.

```mermaid
stateDiagram-v2
  [*] --> Assess
  Assess --> Investigate
  Investigate --> Fix
  Fix --> [*]

  state Fix {
    Edit --> Validate
  }
```

## Usage

Switch between agents in `VSCode > Chat > Set Agent`.
