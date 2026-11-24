# Composio MCP Builder Guidelines & Classification Framework

Derived from Composio's `mcp-builder` guidelines:

### 1. Buildability Tier Definitions
- **Tier 1 (Instant / Direct Build)**:
  - Public REST/GraphQL API available.
  - Self-serve credentialing (instant API key or free developer OAuth app creation).
  - Open machine-readable specification (OpenAPI, Swagger, Postman, GraphQL schema).
  - No partner/sales wall.
- **Tier 2 (Moderate Effort / Friction)**:
  - Documented public API exists.
  - Auth requires trial account, credit card verification, or OAuth app review.
  - No unified OpenAPI spec, but clean documentation allows rapid SDK/tool scaffolding.
- **Tier 3 (Partner-Gated / Blocked / Custom)**:
  - Sales wall, enterprise NDA, or manual partner onboarding required (e.g. DealCloud, PitchBook).
  - Proprietary protocols without public developer access.
  - High compliance hurdle (strict financial/banking licensing).

### 2. Core Auth Classification
- **OAuth2**: Authorization Code (with PKCE), Client Credentials, Refresh token lifecycle.
- **API Key**: Bearer token, custom header (e.g., `X-API-Key`), query param.
- **Basic Auth / Session Token**: Username/Password, cookie/session headers.
- **Partner Gated**: Requires manual enterprise credential issuance.

### 3. MCP Server & Tool Surface Architecture
- **Workflow-Centric Actions**: Read vs Write separation, safe idempotent actions vs dangerous mutations.
- **Pagination & Rate Limits**: Cursor vs offset pagination contracts.
- **Error Handling**: Standardized HTTP status error mapping for LLM recovery.
