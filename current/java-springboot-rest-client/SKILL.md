---
name: java-springboot-rest-client
description: 'Implement and configure Spring RestClient for synchronous HTTP calls in microservices. Use when: creating HTTP client beans, making GET/POST/PUT/PATCH/DELETE calls, handling errors from downstream services, using @HttpExchange declarative clients, configuring timeouts or interceptors, or migrating from RestTemplate. Covers builder setup, fluent API, error handling, type-safe responses, and HTTP Service interfaces.'
---

# Spring RestClient for Microservices

## When to Use This Skill

- Creating or configuring HTTP clients to call downstream REST APIs
- Writing `GET`, `POST`, `PUT`, `PATCH`, or `DELETE` requests
- Handling 4xx/5xx errors from downstream services
- Defining declarative HTTP clients using `@HttpExchange`
- Migrating away from deprecated `RestTemplate`
- Configuring `baseUrl`, auth headers, timeouts, or interceptors for a named client

---

## Key Concepts

| Concept | Summary |
|---|---|
| `RestClient` | Synchronous, fluent HTTP client (Spring 6.1+, preferred over `RestTemplate`) |
| `RestClient.Builder` | Used to configure base URL, headers, interceptors, factories |
| `.retrieve()` | Terminal operation that sends the request and returns a `ResponseSpec` |
| `.exchange()` | Low-level access to request/response — use when `retrieve()` is insufficient |
| `@HttpExchange` | Declarative interface-based client (analogous to Feign/OpenFeign) |
| `RestClientAdapter` | Bridges `RestClient` to `HttpServiceProxyFactory` for `@HttpExchange` proxies |
| `ParameterizedTypeReference` | Required for generic return types (e.g., `List<T>`, `Page<T>`) |
| `onStatus` / `defaultStatusHandler` | Customise how HTTP error codes are translated into exceptions |
| `RestClientCustomizer` | Spring Boot bean — applies additive customization to all `RestClient.Builder` instances |
| `RestClientSsl` | Spring Boot bean — apply SSL bundles to a `RestClient.Builder` via `.apply(ssl.fromBundle(...))` |
| `ClientHttpRequestFactoryBuilder` | Spring Boot 3.2+ — idiomatic way to create a factory with timeouts and SSL |
| `ClientHttpRequestFactorySettings` | Holds connect/read timeout + SSL bundle; passed to `ClientHttpRequestFactoryBuilder` |
| `@ConfigurationProperties` | Binds YAML/properties to a typed class — use to externalise base URLs, endpoint paths, timeouts, and credentials |

---

> ⚠️ **Mandatory Rule — No Hardcoded Configuration**
> Never hardcode base URLs, endpoint paths, timeouts, or credentials directly in a bean definition or service class. All such values **must** come from a `@ConfigurationProperties`-bound record injected as a parameter. See [references/configuration.md](./references/configuration.md) for the full binding and wiring pattern.

---

## 1. Creating a RestClient Bean

Always inject the auto-configured `RestClient.Builder` (never call `RestClient.create()` in Spring Boot). Clone the builder for each per-service client to prevent cross-contamination.

See [references/client-setup.md](./references/client-setup.md) for: clone pattern, `RestClientCustomizer`, migration from `RestTemplate`, `mutate()`, and factory/connection-pool configuration.

---

## 2. Making Requests — Fluent API

```java
// GET
Pet pet = restClient.get().uri("/pets/{id}", id).retrieve().body(Pet.class);

// POST
restClient.post().uri("/pets").contentType(MediaType.APPLICATION_JSON)
    .body(newPet).retrieve().toBodilessEntity();
```

For all HTTP verbs (GET with `ResponseEntity`, PUT, PATCH, DELETE, dynamic method, multipart), see [references/request-examples.md](./references/request-examples.md).

> Always use `ParameterizedTypeReference<List<T>>` for collections — `List.class` loses generic type info.

---

## 3. Error Handling

### Exception types

| Exception | When thrown | Retry? |
|---|---|---|
| `ResourceAccessException` | Network failure, connection refused, read timeout, I/O error | ✅ Yes — transient |
| `HttpServerErrorException` (5xx) | Server returned a 5xx response | ⚠️ Only if idempotent |
| `HttpClientErrorException` (4xx) | Server returned a 4xx response | ❌ No |
| `UnknownHttpStatusCodeException` | Unrecognised status code | ❌ No |

Exceptions thrown from status handlers must be typed — a generic `RuntimeException` will not match retry whitelists.

> **To make 5xx errors retryable with a `defaultStatusHandler`:** throw a typed domain exception from the handler and add that type to `@Retryable(retryFor)` and YAML `retry-exceptions`. `HttpServerErrorException` is only thrown when no status handler intercepts the response — do not add it to a retry whitelist when a handler is configured.

See [references/error-handling.md](./references/error-handling.md) for: `onStatus`, `defaultStatusHandler`, and low-level `exchange()` patterns.

---

## 4. Declarative HTTP Service Clients (`@HttpExchange`)

Preferred for stable, well-defined downstream APIs. Define an interface annotated with `@HttpExchange`/`@GetExchange`/etc., then wire it via `RestClientAdapter` → `HttpServiceProxyFactory`.

`defaultStatusHandler` configured on the underlying `RestClient` applies transparently to the proxy — no need to replicate error handling on the interface.

See [references/http-exchange.md](./references/http-exchange.md) for the full three-step implementation.

---

## 5. Configuration

Externalise all base URLs, timeouts, and credentials to `@ConfigurationProperties`. Use `ClientHttpRequestFactoryBuilder` + `ClientHttpRequestFactorySettings` for timeouts and SSL.

> ⚠️ Global `spring.http.client.*` properties are bypassed once you call `.requestFactory(...)` on the builder — configure `ClientHttpRequestFactorySettings` explicitly in that case.

See [references/configuration.md](./references/configuration.md) for: `@ConfigurationProperties` binding, timeout setup, SSL bundles, interceptors, and global properties.

---

## 6. Request Factory Selection

| Factory | Use case |
|---|---|
| `HttpComponentsClientHttpRequestFactory` | Production — Apache HttpClient 5, connection pooling, best timeout control. Can pin virtual threads on `synchronized` sections — `jdk()` is preferred when virtual threads are enabled |
| `JettyClientHttpRequestFactory` | Jetty-based stacks |
| `JdkClientHttpRequestFactory` | JDK 11+ `HttpClient`; virtual-thread-friendly. Requires `HTTP_1_1` customiser and `127.0.0.1` (not `localhost`) in local config — see gotchas below |
| `ReactorNettyClientRequestFactory` | When already using Project Reactor Netty |
| `SimpleClientHttpRequestFactory` | Development only — no connection pool, poor 4xx handling |

Apache HttpClient 5 default pool limits (`maxTotal=25`, `defaultMaxPerRoute=5`) are too low for production — see [references/client-setup.md](./references/client-setup.md) for pool sizing and factory override patterns.

> ⚠️ **`jdk()` + virtual threads — two independent gotchas for local development**
>
> **1. IPv6 resolution:** JDK `HttpClient` resolves `localhost` to `[::1]` (IPv6) first on macOS/Linux (RFC 6724). If your mock server (Mockoon, WireMock) listens on IPv4 only, the connection hangs rather than being refused — so there is no fast fallback, just a full timeout. Use `127.0.0.1` explicitly in local/docker config.
>
> **2. HTTP/2 upgrade probe (H2C):** JDK `HttpClient` defaults to `HttpClient.Version.HTTP_2` and sends an `Upgrade: h2c` header on every plain-HTTP connection. Node.js-based servers (Mockoon) stall on the H2C handshake. Force HTTP/1.1 via `.withHttpClientCustomizer(http -> http.version(HttpClient.Version.HTTP_1_1))`.
>
> These two issues are **independent** — fixing only HTTP/2 still leaves you with the IPv6 timeout. Both fixes are required together. See [references/client-setup.md](./references/client-setup.md) for the full virtual-threads bean pattern.

---

## 7. HTTP Message Conversion

- JSON (Jackson) is auto-configured when `jackson-databind` is on the classpath.
- For collections, always use `ParameterizedTypeReference<List<T>>`.
- For multipart form uploads, see [references/request-examples.md](./references/request-examples.md).

---

## 8. RestTemplate → RestClient Migration Cheat Sheet

| `RestTemplate` | `RestClient` equivalent |
|---|---|
| `getForObject(url, Class, vars)` | `.get().uri(url, vars).retrieve().body(Class)` |
| `getForEntity(url, Class, vars)` | `.get().uri(url, vars).retrieve().toEntity(Class)` |
| `postForEntity(url, body, Class)` | `.post().uri(url).body(body).retrieve().toEntity(Class)` |
| `put(url, body, vars)` | `.put().uri(url, vars).body(body).retrieve().toBodilessEntity()` |
| `delete(url, vars)` | `.delete().uri(url, vars).retrieve().toBodilessEntity()` |
| `exchange(url, method, entity, Class)` | `.method(method).uri(url).headers(...).body(...).retrieve().toEntity(Class)` |

---

## 9. Resilience Integration

**Dependencies:** `spring-retry`, `resilience4j-spring-boot3`, and `spring-boot-starter-aop` are all required. `@EnableRetry` must be on a `@Configuration` class — without it, `@Retryable` silently does nothing.

Place resilience annotations on the **service method** that calls the `RestClient`, not on the client bean itself.

**Annotation order:** `@Retryable` outermost → `@CircuitBreaker` → method body. Resilience4j's default aspect order already matches this. Pin with `retry-aspect-order: 98` and `circuit-breaker-aspect-order: 99`. This mirrors the ordering owned by the `resiliency-patterns-guide` skill — see [references/resilience-integration.md](./references/resilience-integration.md); if the two ever disagree, that skill wins.

**`CallNotPermittedException`:** Add to `ignoreExceptions` in your retry config — when the CB opens it throws this, and without excluding it Retry will exhaust its budget against an open circuit.

**Bulkhead:** `RestClient` is synchronous — use `THREADPOOL` bulkhead to isolate blocking thread usage. With virtual threads (`spring.threads.virtual.enabled=true`), `SEMAPHORE` is preferred.

See [references/resilience-integration.md](./references/resilience-integration.md) for the full service method template and YAML config.
For the full ordering rationale, comparison table, and decision guide, see the `resiliency-patterns-guide` skill.

| Here (rest-client) | Resilience configuration |
|---|---|
| Which exception types are thrown and when | Retry `maxAttempts`, backoff values, jitter |
| How to shape the service method | Circuit breaker window size, failure threshold, open duration |
| Annotation names and placement | Aspect ordering YAML |
| Bulkhead type selection | Thread pool / semaphore sizing |

---

## 10. Common Mistakes

| Mistake | Fix |
|---|---|
| Calling `retrieve()` without a terminal method | Chain `.body()`, `.toEntity()`, or `.toBodilessEntity()` |
| Using `List.class` for collections | Use `new ParameterizedTypeReference<List<T>>() {}` |
| Relying on `SimpleClientHttpRequestFactory` in prod | Switch to `HttpComponentsClientHttpRequestFactory` |
| Creating a new `RestClient` per request | Create once as a `@Bean` — `RestClient` is thread-safe |
| Not handling 4xx/5xx | Add `onStatus` or `defaultStatusHandler` |
| Calling `exchange()` when `retrieve()` suffices | Prefer `retrieve()` — simpler and applies status handlers |
| Calling `RestClient.create()` in a Spring Boot app | Inject the auto-configured `RestClient.Builder` |
| Mutating a shared `RestClient.Builder` | Call `builder.clone()` before adding per-service config |
| Throwing a generic `RuntimeException` from `defaultStatusHandler` | Throw a typed exception — generic types won't match retry whitelists |
| Using `spring.http.client.*` with a custom `requestFactory` | Those properties are bypassed — configure timeouts via `ClientHttpRequestFactorySettings` |
| Default Apache HttpClient pool limits in production | Set `maxConnTotal` and `maxConnPerRoute` — defaults (25/5) cause queuing under load |
| Hardcoding `baseUrl`, timeouts, or credentials | Bind to `@ConfigurationProperties` |
| Not excluding `CallNotPermittedException` from retry | Add to `ignoreExceptions` — when CB is open this exception will exhaust retry budget |
| Using `jdk()` with `localhost` in local/docker config | Use `127.0.0.1` — JDK `HttpClient` resolves `localhost` to `[::1]` (IPv6) first; Rancher Desktop's SSH tunnel is IPv4-only so the connection hangs (not refused), meaning no fast IPv4 fallback |
| Using `jdk()` without forcing `HTTP_1_1` | Add `.withHttpClientCustomizer(http -> http.version(HttpClient.Version.HTTP_1_1))` — the default `HTTP_2` setting sends an H2C upgrade probe that stalls Mockoon and similar Node.js mock servers |
