# RestClient — Resilience Integration

## Service Method Shape

A `RestClient` bean handles HTTP mechanics. Resilience annotations (`@Retryable`, `@CircuitBreaker`, `@Bulkhead`) sit on the **service method**, not on the client bean or the HTTP call itself.

```java
@Service
public class OrderServiceClient {

    private final RestClient restClient;

    public OrderServiceClient(RestClient.Builder builder, OrderServiceProperties props) {
        this.restClient = builder.clone()
            .baseUrl(props.baseUrl()) // baseUrl injected via OrderServiceProperties — see configuration.md
            .defaultStatusHandler(HttpStatusCode::is4xxClientError, (req, res) -> {
                throw new OrderClientException(res.getStatusCode());          // non-retryable
            })
            .defaultStatusHandler(HttpStatusCode::is5xxServerError, (req, res) -> {
                throw new OrderServiceUnavailableException(res.getStatusCode()); // retryable
            })
            .build();
    }

    @Retryable(
        retryFor = { ResourceAccessException.class, OrderServiceUnavailableException.class },
        maxAttempts = 3,
        backoff = @Backoff(delay = 200, multiplier = 2, random = true)
    )
    @CircuitBreaker(name = "orderService", fallbackMethod = "getOrderFallback")
    @Bulkhead(name = "orderService", type = Bulkhead.Type.SEMAPHORE) // SEMAPHORE: default for virtual-thread services; on non-virtual-thread platforms use THREADPOOL (requires CompletableFuture<T> return type)
    public Order getOrder(UUID orderId) {
        return restClient.get()
            .uri("/orders/{id}", orderId)
            .retrieve()
            .body(Order.class);
    }

    // Must be at least package-private. Runs outside any failed transaction context.
    Order getOrderFallback(UUID orderId, Throwable cause) {
        log.warn("orderService circuit open or retries exhausted for orderId={}", orderId, cause);
        throw new OrderServiceUnavailableException("orderService unavailable");
    }
}
```

## YAML Configuration

```yaml
spring:
  threads:
    virtual:
      enabled: true  # virtual threads enabled — SEMAPHORE bulkhead preferred over THREADPOOL

resilience4j:
  retry:
    retry-aspect-order: 98
    instances:
      default:
        max-attempts: 3
        wait-duration: 200ms
        exponential-backoff-multiplier: 2
        enable-randomized-wait: true
        randomized-wait-factor: 0.2
        retry-exceptions:
          - org.springframework.web.client.ResourceAccessException
          - com.example.OrderServiceUnavailableException  # typed domain exception thrown by the 5xx defaultStatusHandler — do NOT add HttpServerErrorException directly
        ignore-exceptions:
          - org.springframework.web.client.HttpClientErrorException
          - io.github.resilience4j.circuitbreaker.CallNotPermittedException
  circuitbreaker:
    circuit-breaker-aspect-order: 99
    instances:
      orderService:
        sliding-window-type: COUNT_BASED
        sliding-window-size: 50
        failure-rate-threshold: 50
        wait-duration-in-open-state: 30s
        slow-call-rate-threshold: 80
        slow-call-duration-threshold: 2s
        automatic-transition-from-open-to-half-open-enabled: true
  bulkhead:
    instances:
      orderService:
        max-concurrent-calls: 20
        max-wait-duration: 0
```

## Cross-Reference

**Load [resiliency-patterns-guide/SKILL.md](../../resiliency-patterns-guide/SKILL.md) for the full aspect ordering rationale, ordering comparison table, transaction boundary rules, and decision guide.**
