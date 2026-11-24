# Ground-Truth Repositories & Architecture Stack

This document tracks the core repositories, APIs, and toolkits powering the 100 SaaS/developer app research pipeline.

---

## 1. Core Agent & Dogfooding (Composio Stack)
- **`ComposioHQ/composio`**
  - **Repo**: [github.com/ComposioHQ/composio](https://github.com/ComposioHQ/composio)
  - **Role**: Core SDK & tooling adapter. Powers app actions, authentication orchestration, and Gemini provider integrations.
- **`ComposioHQ/composio-mcp-plugin`**
  - **Endpoint**: `https://connect.composio.dev/mcp`
  - **Meta-tools**: `COMPOSIO_SEARCH_TOOLS`, `COMPOSIO_MULTI_EXECUTE_TOOL`, `COMPOSIO_REMOTE_WORKBENCH`.
- **`ComposioHQ/awesome-claude-skills (mcp-builder)`**
  - **Reference**: [mcp-builder SKILL.md](https://github.com/ComposioHQ/awesome-claude-skills/blob/master/mcp-builder/SKILL.md?plain=1)
  - **Role**: Composio's canonical standards for MCP server evaluation (workflow design, auth patterns, error contracts, Tier classification).

---

## 2. Doc Scraping & Browser Verification
- **`firecrawl/firecrawl` & `firecrawl-py`**
  - **Repo**: [github.com/firecrawl/firecrawl](https://github.com/firecrawl/firecrawl)
  - **Role**: Markdown extraction from complex JS-heavy documentation portals (Stoplight, ReadMe, Swagger UI). Supports Keyless free tier.
- **`browser-use/browser-use`**
  - **Repo**: [github.com/browser-use/browser-use](https://github.com/browser-use/browser-use)
  - **Role**: Headless Chrome/CDP agent for Pass 2 deep verification on the ~10–15 JS-gated, Cloudflare-protected, or dynamic auth portals.

---

## 3. Ground-Truth Registries (Zero-Hallucination Deterministic Layer)
- **Official MCP Registry (`modelcontextprotocol/registry`)**
  - **Endpoint**: `https://registry.modelcontextprotocol.io/v0.1/servers?search={query}&version=latest`
  - **Role**: Deterministic verification of published official MCP servers.
- **APIs-guru OpenAPI Directory (`APIs-guru/openapi-directory`)**
  - **Endpoint**: `https://api.apis.guru/v2/list.json`
  - **Role**: The "Wikipedia for Web APIs" containing machine-readable OpenAPI 2.0/3.x definitions.
- **Awesome MCP Catalogs (`punkpeye/awesome-mcp-servers` & `awesome-remote-mcp-servers`)**
  - **Repo**: [github.com/punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
  - **Role**: Curated community MCP listings for catching non-registry open-source implementations.
