# RestClient — Client Setup Patterns

## Creating a Bean (Spring Boot)

Inject the auto-configured `RestClient.Builder` — never call `RestClient.create()` in a Spring Boot application. Always also inject the `@ConfigurationProperties` record for the target service to supply the base URL:

```java
@Service
public class MyService {

    private final RestClient restClient;

    public MyService(RestClient.Builder restClientBuilder, OrderServiceProperties props) {
        this.restClient = restClientBuilder
            .baseUrl(props.baseUrl()) // never hardcode — always from @ConfigurationProperties
            .build();
    }
}
```

## Multiple Clients — Use `clone()`

`RestClient.Builder` is stateful — mutations affect all clients built from it. Clone before adding per-service config. Inject each service's `@ConfigurationProperties` record as a parameter to supply the base URL:

```java
@Configuration
public class HttpClientConfig {

    @Bean
    RestClient orderServiceClient(RestClient.Builder builder, OrderServiceProperties props) {
        return builder.clone()
            .baseUrl(props.baseUrl()) // never hardcode — always from @ConfigurationProperties
            .build();
    }

    @Bean
    RestClient inventoryServiceClient(RestClient.Builder builder, InventoryServiceProperties props) {
        return builder.clone()
            .baseUrl(props.baseUrl()) // never hardcode — always from @ConfigurationProperties
            .build();
    }
}
```

## Application-Wide Customization — `RestClientCustomizer`

Applies to every `RestClient.Builder` auto-configured by Spring Boot (e.g., default headers, observability interceptors):

```java
@Bean
RestClientCustomizer loggingCustomizer() {
    return builder -> builder.requestInterceptor(new LoggingClientHttpRequestInterceptor());
}
```

> `RestClientCustomizer` beans do **not** apply when you call `RestClient.create()`.

## Migrating from RestTemplate

```java
RestClient restClient = RestClient.create(existingRestTemplate);
// or
RestClient restClient = RestClient.builder(existingRestTemplate).baseUrl("...").build();
```

## `mutate()` — Variant from an Existing Client

Use `mutate()` on an already-built `RestClient` to create per-request or per-tenant variants without rebuilding from scratch. Inherits all transport, timeout, and interceptor settings.

```java
RestClient adminClient = baseClient.mutate()
    .defaultHeader("X-Admin-Key", adminKey)
    .build();
```

## Request Factory Selection

Spring Boot auto-detects the factory from the classpath. Detection order (highest priority first):

| Factory | Use case |
|---|---|
| `HttpComponentsClientHttpRequestFactory` | Production — best timeout control, connection pooling (Apache HttpClient 5) |
| `JettyClientHttpRequestFactory` | Jetty-based stacks |
| `JdkClientHttpRequestFactory` | JDK 11+ `HttpClient`, no extra dependency |
| `ReactorNettyClientRequestFactory` | When already using Project Reactor Netty |
| `SimpleClientHttpRequestFactory` | Development only — no connection pool, poor 4xx handling |

> **Avoid** `SimpleClientHttpRequestFactory` in production — no connection pool and may not surface 4xx status codes correctly.

Override the detected factory globally:
```properties
spring.http.client.factory=apache
```

Override via code (e.g., JDK with custom `ProxySelector`):
```java
@Bean
ClientHttpRequestFactoryBuilder<?> clientHttpRequestFactoryBuilder(ProxySelector proxySelector) {
    return ClientHttpRequestFactoryBuilder.jdk()
        .withHttpClientCustomizer(b -> b.proxy(proxySelector));
}
```

## Apache Connection Pool Sizing

Default limits (`maxTotal=25`, `defaultMaxPerRoute=5`) are far too low for any meaningful production load. Configure explicitly:

```java
@Bean
ClientHttpRequestFactoryBuilder<?> clientHttpRequestFactoryBuilder() {
    return ClientHttpRequestFactoryBuilder.apache()
        .withHttpClientCustomizer(builder -> builder
            .setConnectionManager(
                PoolingHttpClientConnectionManagerBuilder.create()
                    .setMaxConnTotal(200)
                    .setMaxConnPerRoute(50)
                    .build()
            )
        );
}
```

Tune `maxConnTotal` and `maxConnPerRoute` to your expected concurrency per downstream service.

---

## Virtual Threads and Factory Selection

When `spring.threads.virtual.enabled=true`, use `ClientHttpRequestFactoryBuilder.jdk()`. Apache HttpClient 5 (`httpComponents()`) can pin virtual threads on `synchronized` sections in its connection pool; the JDK `HttpClient` avoids this. The performance cost of occasional pinning is typically acceptable for short-duration HTTP I/O, but `jdk()` is the cleaner choice.

### Required customisation for `jdk()`

Two independent issues arise when using `jdk()` against local containerised mock servers (Mockoon, WireMock running in Docker/Rancher Desktop):

| Issue | Cause | Fix |
|---|---|---|
| Connect timeout | JDK `HttpClient` resolves `localhost` to `[::1]` (IPv6) first via RFC 6724. If the Docker networking layer only forwards on IPv4, the IPv6 attempt hangs — no refused connection, just a full timeout, so no automatic fallback to IPv4 | Use `127.0.0.1` in local/docker config instead of `localhost` |
| Stalled connection | JDK `HttpClient` defaults to `HttpClient.Version.HTTP_2` and sends an `Upgrade: h2c` header. Node.js-based servers (Mockoon) stall on the H2C handshake | Force `HTTP_1_1` via `withHttpClientCustomizer` |

Both fixes are required — they address different root causes. Fixing only HTTP/2 still leaves the IPv6 timeout.

### Full `jdk()` bean pattern (virtual threads)

```java
@Bean
public RestClient myServiceClient(RestClient.Builder builder, MyServiceProperties props) {
    ClientHttpRequestFactorySettings settings = ClientHttpRequestFactorySettings.defaults()
            .withConnectTimeout(Duration.ofMillis(props.timeoutMs()))
            .withReadTimeout(Duration.ofMillis(props.timeoutMs()));
    return builder.clone()
            .baseUrl(props.baseUrl())
            .requestFactory(ClientHttpRequestFactoryBuilder.jdk()
                    .withHttpClientCustomizer(http -> http.version(HttpClient.Version.HTTP_1_1))
                    .build(settings))
            .build();
}
```

### Local/docker config

```yaml
rest:
  api:
    my-service:
      base-url: http://127.0.0.1:3011   # 127.0.0.1, never localhost
      timeout-ms: 5000
```
