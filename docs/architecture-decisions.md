# Architecture Decision Records (ADR)

## Enterprise Engineering Intelligence MCP

**Document status:** Living document  
**Version:** 1.0  
**Last updated:** October 2026

## 1. Purpose

This document records the key architectural decisions behind Enterprise Engineering Intelligence MCP.

The project aims to provide an AI-powered interface to enterprise information across GitHub, Notion, and HubSpot. It uses the Model Context Protocol (MCP) to expose system capabilities as tools and LangGraph to orchestrate interactions between a language model and those tools.

These decisions explain the reasoning behind the selected technologies, their trade-offs, and the direction for future development.

## 2. System Context

Enterprise information is distributed across multiple systems:

- **GitHub:** Repositories, issues, pull requests, and code changes.
- **Notion:** Technical documentation, project notes, and organizational knowledge.
- **HubSpot:** Customer, company, and CRM information.

The proposed architecture provides a unified AI interaction layer over these systems while keeping integrations modular.

### High-Level Architecture

```text
                  User / AI Client
                         |
                         v
                  AI Orchestration
                      LangGraph
                         |
                         v
                  Language Model
                       Groq
                         |
                         v
                     MCP Client
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
          GitHub       Notion      HubSpot
          Adapter      Adapter     Adapter
             |           |           |
             v           v           v
          GitHub API  Notion API  HubSpot API
```

**Implementation note:** GitHub tools, Groq integration, and LangGraph orchestration are implemented. Notion and HubSpot are planned integrations. The diagram represents the target architecture rather than claiming that every integration is operational.

---

## ADR-001: Use the Model Context Protocol for Tool Integration

**Status:** Accepted and implemented for GitHub.

### Context

The application needs to expose external-system operations to AI clients in a consistent, reusable way. Implementing a different custom tool interface for every AI client would create unnecessary coupling.

### Decision

Use the Model Context Protocol (MCP) to expose external-system capabilities as tools.

The current GitHub MCP server uses FastMCP and exposes repository, issue, and pull request operations.

### Alternatives considered

- Custom function-calling interfaces tied to one model provider.
- Direct API calls embedded in the AI orchestration layer.
- A proprietary tool protocol for each client.

### Rationale

MCP separates the definition and implementation of tools from the AI client that consumes them. Compatible clients can discover and invoke the tools without requiring the GitHub API logic to be duplicated in every client.

### Trade-offs

**Benefits**
- Reusable tool interfaces.
- Separation between integrations and orchestration.
- Potential compatibility with multiple MCP-enabled AI clients.

**Costs**
- An additional client-server communication layer.
- Tool schemas and transport configuration must be maintained.
- MCP compatibility does not guarantee identical behavior across every AI client.

### Consequences

Each external system can be integrated behind its own MCP tool interface, allowing GitHub, Notion, and HubSpot to evolve independently.

---

## ADR-002: Use LangGraph for AI Workflow Orchestration

**Status:** Accepted and implemented for the current tool-calling workflow.

### Context

The assistant must decide when external information is required, call the relevant tools, process their responses, and generate a final answer.

A simple direct model call is insufficient for workflows that need multiple tool interactions.

### Decision

Use LangGraph to manage the model-and-tool execution loop.

The current graph includes:
- An agent node that invokes the language model.
- A tool node that executes requested tools.
- Conditional routing that determines whether the model should call a tool or finish responding.

### Alternatives considered

- A single LLM request without tool calling.
- A custom orchestration loop implemented manually.
- A fixed sequence of API calls for every request.

### Rationale

LangGraph provides explicit workflow structure and supports extending the application toward multi-step engineering investigations.

### Trade-offs

**Benefits**
- Clear separation between model reasoning and tool execution.
- Support for conditional routing and multi-step workflows.
- A foundation for stateful workflows and controlled retries.

**Costs**
- Additional framework complexity.
- Workflow behavior requires testing and observability.
- An orchestration framework does not automatically guarantee correct reasoning or safe tool usage.

### Consequences

Future workflows can introduce dedicated nodes for issue investigation, pull request analysis, documentation retrieval, and evidence-backed reporting.

Persistent state and advanced workflow routing remain future enhancements.

---

## ADR-003: Use Groq for Language Model Inference

**Status:** Accepted and implemented.

### Context

The application requires a language model capable of interpreting natural-language requests, selecting tools, and synthesizing information returned by those tools.

### Decision

Use Groq through its supported model APIs and the LangChain Groq integration.

The model identifier is configured through environment-based application settings rather than being embedded throughout the codebase.

### Alternatives considered

- Other hosted model providers.
- Locally hosted language models.
- A model-independent inference gateway.

### Rationale

Groq provides a hosted inference service and integrates with the selected LangChain orchestration stack.

### Trade-offs

**Benefits**
- Managed model inference.
- Straightforward integration with the existing Python stack.
- Model configuration can be changed without redesigning the whole application.

**Costs**
- Dependence on an external provider.
- Model availability, latency, capabilities, and pricing may change.
- Requests may involve transmitting user queries and retrieved context to the provider.

### Consequences

Model selection must be validated against tool-calling reliability, response quality, structured-output requirements, latency, cost, and data-handling policies.

The architecture does not assume that every Groq model supports identical tool-calling or structured-output features.

---

## ADR-004: Use Python and an Asynchronous API Client

**Status:** Accepted and implemented for GitHub.

### Context

The project requires API integrations, asynchronous tool execution, validation, testing, and compatibility with MCP and LangGraph.

### Decision

Use Python 3.12 and HTTPX for asynchronous communication with external REST APIs.

Use Pydantic Settings to validate and load application configuration.

### Alternatives considered

- Synchronous HTTP clients.
- A Node.js or TypeScript implementation.
- Separate languages and runtime environments for each integration.

### Rationale

Python has mature support for AI orchestration and MCP. HTTPX provides asynchronous requests, timeout controls, and testable HTTP behavior.

### Trade-offs

**Benefits**
- Strong ecosystem for AI and API integrations.
- Non-blocking network requests.
- Shared patterns across future integrations.

**Costs**
- Asynchronous code requires careful error handling and testing.
- Dependency versions must be managed.
- Runtime and package compatibility must be maintained.

### Consequences

Integration clients should share consistent timeout
