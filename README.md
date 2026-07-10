# Copilot Agents

Extended agents for GitHub Copilot in VS Code, built on top of default system
prompts. Tested only with DeepSeek API, but should work with any
OpenAI-compatible API.

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

Create a new custom agent with `Chat: Configure Custom Agent...` command and
select one of the provided templates.
