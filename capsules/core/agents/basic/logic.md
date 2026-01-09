# Basic Agent Capsule: UX Orchestrator

## Description
The Basic Agent Capsule encapsulates the User Experience (UX) Orchestration layer of HyperSync. It serves as the primary interface for user interaction, translating natural language intents into actionable system operations via "Playbooks".

## Components

### UX Orchestrator
The central coordinator that manages the user interaction flow. It delegates specific tasks to sub-agents (mocked in this capsule) and ensures a coherent user experience.

### Intent Parser
Analyzes user input to identify the underlying intent. It matches input against a library of Playbooks to determine the appropriate course of action.

### Playbooks
Markdown-based definitions of workflows. Each playbook represents a specific capability or task the user can perform (e.g., "create_extension", "help").

## Usage
This capsule is designed to be the entry point for the CLI or Chat interface. It requires a directory of Playbooks to function effectively.
