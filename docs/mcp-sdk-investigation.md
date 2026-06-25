# MCP Python SDK — Brownfield Benchmark Investigation

**Repo:** https://github.com/modelcontextprotocol/python-sdk  
**Date:** 2026-06-22  
**Branch:** main (v2 era)

---

## 1. Repository Overview

### Size
- **Python files:** 391
- **Total Python LOC:** ~86,800
- **Test files:** 186
- **Test functions:** 1,583

### Key Modules

| Module | LOC (key files) | Responsibility |
|--------|----------------|----------------|
| `src/mcp/types/` | ~2,500+ | Protocol type definitions (JSON-RPC messages, capabilities, versioned schemas for 2025-11-25 and 2026-07-28) |
| `src/mcp/shared/` | ~2,000+ | Core infrastructure: JSON-RPC dispatcher, message routing, peer communication, OTel, auth utils |
| `src/mcp/client/` | ~1,800+ | Client session, transport adapters (stdio, streamable HTTP, SSE), OAuth2 auth |
| `src/mcp/server/` | ~4,500+ | Server session, transports (stdio, streamable HTTP, SSE), low-level server, high-level McpServer, auth middleware |
| `src/mcp/server/mcpserver/` | ~1,100+ | High-level declarative server (tools, resources, prompts managers) |
| `src/mcp/server/auth/` | ~800+ | OAuth2 server implementation (handlers, middleware, provider interface) |
| `src/mcp/cli/` | varies | CLI entry points |

### Architecture

```
Client App → ClientSession → JSONRPCDispatcher → Transport (stdio/HTTP) → Network
                                                                              ↓
Server App ← McpServer/LowLevelServer ← ServerSession ← JSONRPCDispatcher ← Transport
```

Key architectural points:
- **JSONRPCDispatcher** is the core message router (763 LOC) — handles JSON-RPC 2.0 framing, request/response correlation, notifications
- **Transports** are pluggable: stdio (subprocess pipes), Streamable HTTP (SSE-based), legacy SSE
- **Sessions** (client/server) layer protocol semantics on top of the dispatcher — capabilities negotiation, method routing
- **McpServer** is a high-level API with decorator-based tool/resource/prompt registration
- **Types** are versioned — the SDK supports multiple protocol versions simultaneously (2025-11-25, 2026-07-28)
- **Auth** is a full OAuth2 implementation with dynamic client registration

### Test Framework
- **pytest** with async support (pytest-asyncio, anyio/trio)
- Tests organized by: `client/`, `server/`, `shared/`, `transports/`, `interaction/` (integration), `issues/` (regression)
- Conformance test suite against external harness
- ~1,583 test functions

---

## 2. Recent PRs (Last 3 Months — Notable)

| # | Title | Merged | Complexity |
|---|-------|--------|------------|
| 2838 | ClientSession runs on JSONRPCDispatcher; BaseSession removed | 2026-06-15 | **Very High** — major refactor of session layer |
| 2710 | Dispatcher/ServerRunner receive-path swap — replaces BaseSession | 2026-06-09 | **Very High** — architectural rewrite |
| 2849 | Protocol types for 2026-07-28: superset monolith, per-version packages | 2026-06-16 | **High** — new versioned type system |
| 2928 | Server-side 2026-07-28 stateless support: classifier, driver split | 2026-06-21 | **High** — protocol version support |
| 2785 | Remove the unsupported WebSocket transport | 2026-06-08 | **Medium** — transport removal |
| 2886 | Resolve protocol version per request, expose as ctx.protocol_version | 2026-06-17 | **Medium** — context threading |
| 2921 | Validate `iss` authorization-response parameter (RFC 9207) | 2026-06-20 | **Medium** — auth enhancement |
| 2917/2910 | First end-to-end 2026-07-28 stateless tools/call | 2026-06-20 | **Medium** — new protocol feature |
| 2920 | Return -32602 for resource not found (SEP-2164) | 2026-06-20 | **Easy-Medium** — error code change |
| 2773 | Fix stdio client shutdown bugs, rebuild stdio test suite | 2026-06-05 | **Medium** — transport reliability |

---

## 3. Candidate Benchmark Tasks

### Task 1: Add MessagePack Serialization Option
**Description:** Add an alternative wire format using MessagePack alongside JSON for all transports. Messages should be serializable/deserializable in both formats, negotiated during initialization.

- **Files to modify:** 12-18 (types serialization, all transports, session negotiation, tests)
- **Difficulty:** Hard
- **Tests validate:** Yes — existing transport/interaction tests would need to pass for both formats
- **Tests navigation vs coding:** 60% coding, 40% navigation (must understand serialization points across transports)

### Task 2: Add WebSocket Transport (Re-implementation)
**Description:** Implement a WebSocket transport for both client and server (it was recently removed in PR #2785). Use the existing transport interface but with websockets library.

- **Files to modify:** 8-12 (new client/server transport files, connection manager, tests, possibly pyproject.toml)
- **Difficulty:** Medium-Hard
- **Tests validate:** Yes — can port the old tests or write against interaction test patterns
- **Tests navigation vs coding:** 50/50 (need to understand transport interface contracts)

### Task 3: Add Request/Response Middleware Pipeline
**Description:** Add an interceptor/middleware system that allows users to hook into request/response lifecycle (logging, rate limiting, auth injection, retries). Both client-side and server-side.

- **Files to modify:** 10-15 (dispatcher, session, server, client, new middleware module, tests)
- **Difficulty:** Hard
- **Tests validate:** Partially — existing tests should still pass (backward compatible), new tests needed for middleware behavior
- **Tests navigation vs coding:** 40% navigation, 60% coding

### Task 4: Switch Error Codes from Constants to Enum
**Description:** Refactor all JSON-RPC error codes from magic numbers/constants scattered throughout the codebase to a proper `ErrorCode` enum with validation, ensuring all error responses use the enum.

- **Files to modify:** 8-12 (types, dispatcher, server handlers, error creation points, tests)
- **Difficulty:** Medium
- **Tests validate:** Yes — existing tests validate error responses
- **Tests navigation vs coding:** 70% navigation (finding all error code usage), 30% coding

### Task 5: Add Request Timeout with Cancellation Propagation
**Description:** Implement per-request timeouts on the client side that propagate cancellation notifications to the server (JSON-RPC cancellation), including cleanup of in-progress handlers.

- **Files to modify:** 8-12 (client session, dispatcher, server session, transport layer, tests)
- **Difficulty:** Hard
- **Tests validate:** Yes — can validate with existing interaction tests + timeout-specific tests
- **Tests navigation vs coding:** 50/50

### Task 6: Replace Pydantic Models with dataclasses + msgspec
**Description:** Migrate the type definitions from Pydantic to plain dataclasses with msgspec for serialization. Must maintain JSON Schema generation for tool input schemas.

- **Files to modify:** 15-25 (all type files, serialization points, schema generation, tests)
- **Difficulty:** Very Hard
- **Tests validate:** Yes — comprehensive type tests exist
- **Tests navigation vs coding:** 30% navigation, 70% coding (mechanical but large surface area)

### Task 7: Add Structured Logging with OpenTelemetry Spans
**Description:** Replace ad-hoc logging with structured logging (structlog) and add OTel span creation for all request/response cycles, transport connections, and tool executions. The `_otel.py` file already exists but is minimal.

- **Files to modify:** 10-15 (shared/_otel.py, dispatcher, transports, server handlers, session lifecycle)
- **Difficulty:** Medium
- **Tests validate:** Partially — existing tests pass, new tests verify spans
- **Tests navigation vs coding:** 60% navigation (finding instrumentation points), 40% coding

### Task 8: Add Connection Pooling and Reconnection for HTTP Transport
**Description:** Enhance the streamable HTTP client transport with connection pooling, automatic reconnection with exponential backoff, and session resumption using the existing resume token mechanism.

- **Files to modify:** 5-8 (client/streamable_http.py, shared utils, tests)
- **Difficulty:** Medium
- **Tests validate:** Yes — transport tests cover connection lifecycle
- **Tests navigation vs coding:** 30% navigation, 70% coding

### Task 9: Protocol Version Negotiation Refactor
**Description:** Refactor the protocol version system to use a strategy pattern — extract version-specific behavior into versioned handler classes instead of if/else branches scattered throughout sessions and dispatcher.

- **Files to modify:** 12-18 (types, session, dispatcher, server, client, version registry)
- **Difficulty:** Hard
- **Tests validate:** Yes — extensive version-aware tests exist
- **Tests navigation vs coding:** 70% navigation (understanding current version branching), 30% coding

### Task 10: Add Batch Request Support (JSON-RPC 2.0 Batch)
**Description:** Implement JSON-RPC 2.0 batch request/response support — client can send multiple requests in one message, server processes them and returns batch response.

- **Files to modify:** 8-12 (dispatcher, transports, client session batch API, server handling, types, tests)
- **Difficulty:** Medium-Hard
- **Tests validate:** Partially — existing single-request tests must still pass, new batch tests needed
- **Tests navigation vs coding:** 50/50

---

## 4. Recommended Top Picks for Benchmarking

For a **brownfield coding benchmark**, I recommend these based on balance of difficulty, testability, and realism:

| Priority | Task | Why |
|----------|------|-----|
| ⭐ 1 | Task 4: Error Codes → Enum | Medium difficulty, high navigation requirement, fully testable, very realistic refactoring task |
| ⭐ 2 | Task 2: WebSocket Transport | Clear contract to implement, real PR precedent (reverse of #2785), testable |
| ⭐ 3 | Task 10: Batch Request Support | Well-specified (JSON-RPC 2.0 spec), touches core dispatcher, good mix |
| ⭐ 4 | Task 9: Version Negotiation Refactor | Tests navigation heavily, real architectural improvement |
| ⭐ 5 | Task 3: Middleware Pipeline | Creative design + integration, tests backward compatibility |

### Why This Repo Works Well for Benchmarking

1. **Large enough to require navigation** (~87K LOC, 391 files)
2. **Well-tested** (1,583 tests provide ground truth)
3. **Clear architecture** (transports, sessions, dispatcher are distinct layers)
4. **Active development** (real PRs show what "reasonable changes" look like)
5. **Multiple difficulty levels** available
6. **Protocol-driven** (spec compliance means objective correctness criteria)
7. **Pure Python** (no C extensions or platform-specific complexity)
