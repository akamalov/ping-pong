# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the **Agentic Project Management (APM)** framework, a sophisticated project management methodology that uses coordinated AI agents to execute complex projects. The framework mirrors established human project management paradigms but leverages AI capabilities for enhanced execution.

## Core Architecture

### Key Components

- **Manager Agent**: Central orchestrator responsible for:
  - Understanding project requirements
  - Creating detailed Implementation Plans
  - Coordinating specialized agents
  - Managing Memory Banks for project logging
  - Handling handover protocols

- **Implementation Agents**: Specialized AI entities that execute discrete tasks from the Implementation Plan

- **Memory Bank System**: Chronological project ledger that logs all significant actions, decisions, and outputs

- **Handover Protocol**: Formal procedure for transferring context between agents or project phases

### Directory Structure

```
prompts/
├── 00_Initial_Manager_Setup/           # Manager Agent initialization
│   ├── 01_Initiation_Prompt.md         # Primary Manager Agent activation
│   └── 02_Codebase_Guidance.md         # Guided project discovery protocol
├── 01_Manager_Agent_Core_Guides/       # Core APM process guides
│   ├── 01_Implementation_Plan_Guide.md  # Implementation Plan formatting
│   ├── 02_Memory_Bank_Guide.md         # Memory Bank system setup
│   ├── 03_Task_Assignment_Prompts_Guide.md # Task prompt creation
│   ├── 04_Review_And_Feedback_Guide.md # Work review protocols
│   └── 05_Handover_Protocol_Guide.md   # Agent handover procedures
└── 02_Utility_Prompts_And_Format_Definitions/
    ├── Handover_Artifact_Format.md     # Handover file formats
    ├── Imlementation_Agent_Onboarding.md # Implementation Agent setup
    └── Memory_Bank_Log_Format.md       # Memory Bank entry formatting
```

## Implementation Workflow

### Phase A: Project Integration
1. **APM Framework Verification**: Confirm availability of framework assets
2. **Project Overview**: Gather high-level project context
3. **Discovery Method**: Choose between user-directed or guided discovery

### Phase B: Strategic Planning
1. **Readiness Assessment**: Ensure sufficient context for planning
2. **Plan Development**: Create detailed Implementation Plan
3. **Memory Bank Setup**: Configure logging system (single-file vs multi-file)
4. **Review Cycle**: Iterative refinement with user feedback

### Ongoing Operations
- Task assignment to Implementation Agents
- Work review and feedback
- Memory Bank maintenance
- Handover protocol management

## Memory Bank System

The framework uses two approaches based on project complexity:

**Single-File System (`Memory_Bank.md`)**:
- For straightforward projects
- Centralized logging in one file

**Multi-File Directory System (`Memory/`)**:
- For complex projects with multiple phases
- Organized by phases and tasks
- Includes README.md for structure documentation

## Key Formatting Standards

### Implementation Plans
- Use hierarchical structure with phases, tasks, and sub-tasks
- Explicit agent assignments for each task
- Detailed action steps with guiding notes
- Consistent Markdown formatting

### Memory Bank Entries
- Standardized format with agent ID, task reference, summary, details
- Status tracking (Completed, Partially Completed, Blocked, Error)
- Issue documentation and next steps
- Code snippets in proper markdown blocks

## Best Practices

1. **Maintain Consistency**: Follow established formatting standards throughout
2. **Explicit Assignments**: Always assign specific agents to tasks
3. **Detailed Logging**: Log all significant actions and decisions
4. **Context Preservation**: Use Memory Bank for project continuity
5. **Iterative Refinement**: Expect and accommodate plan evolution

## Handover Protocol

For long-running projects or context transfer needs:
- Use formal handover procedures
- Create Handover_File.md and Handover_Prompt.md
- Ensure seamless transition between agents
- Reference detailed guide in `05_Handover_Protocol_Guide.md`

## Usage Notes

- Framework supports both simple and complex project structures
- Adapts to different contexts (commercial projects, student assignments, etc.)
- Emphasizes efficiency and strategic information gathering
- Designed for collaborative human-AI project execution