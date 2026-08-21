# RestClient — Configuration Patterns

## Externalise with `@ConfigurationProperties`

Never hardcode base URLs, timeouts, or credentials in bean definitions.

### application.yml

```yaml
rest:
  api:
    order-service:
      base-url: "https://order-service"
      timeout-ms: 5000
    payment-service:
      base-url: "https://payment-service"
      token-endpoint: "/api/v1/tokens"
      client-id: "${PAYMENT_SERVICE_CLIENT_ID}"
      client-secret: "${PAYMENT_SERVICE_CLIENT_SECRET}"
      timeout-ms: 3000
```

> ⚠️ **Never store real credentials in `application.yml`** — use `${ENV_VAR}` placeholders resolved from environment variables or a secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager).

### Binding class (Java record — Spring Boot 3+)

```java
@ConfigurationProperties(prefix = "rest.api.payment-service")
public record PaymentServiceProperties(
    String baseUrl,
    String tokenEndpoint,
    String clientId,
    String clientSecret,
    int timeoutMs
) {}
```

### Registering and injecting

```java
@Configuration
@EnableConfigurationProperties(PaymentServiceProperties.class)
public class HttpClientConfig {

    @Bean
    RestClient paymentServiceClient(RestClient.Builder builder,
                                    PaymentServiceProperties props) {
        ClientHttpRequestFactorySettings settings = ClientHttpRequestFactorySettings.defaults()
            .withConnectTimeout(Duration.ofMillis(props.timeoutMs()))
            .withReadTimeout(Duration.ofMillis(props.timeoutMs()));
        ClientHttpRequestFactory factory = ClientHttpRequestFactoryBuilder.detect().build(settings);

        return builder.clone()
            .baseUrl(props.baseUrl())
            .requestFactory(factory)
            .build();
    }
}
```

Endpoint paths (e.g. `tokenEndpoint`) are best injected into the service layer that uses the `RestClient` rather than on the client bean itself — the bean only needs `baseUrl` and transport settings.

## Timeout Configuration (`ClientHttpRequestFactorySettings`)

Spring Boot's idiomatic API — works across all underlying HTTP libraries:

```java
@Bean
RestClient myServiceClient(RestClient.Builder builder, MyServiceProperties props) {
    ClientHttpRequestFactorySettings settings = ClientHttpRequestFactorySettings.defaults()
        .withConnectTimeout(Duration.ofSeconds(2))
        .withReadTimeout(Duration.ofSeconds(5));
    ClientHttpRequestFactory requestFactory = ClientHttpRequestFactoryBuilder.detect().build(settings);
    return builder.clone()
        .baseUrl(props.baseUrl())
        .requestFactory(requestFactory)
        .build();
}
```

## Timeout + SSL Bundle

```java
@Bean
RestClient myServiceClient(RestClient.Builder builder, SslBundles sslBundles) {
    ClientHttpRequestFactorySettings settings = ClientHttpRequestFactorySettings
        .ofSslBundle(sslBundles.getBundle("mybundle"))
        .withConnectTimeout(Duration.ofSeconds(2))
        .withReadTimeout(Duration.ofSeconds(5));
    ClientHttpRequestFactory requestFactory = ClientHttpRequestFactoryBuilder.detect().build(settings);
    return builder.clone()
        .baseUrl("https://my-service")
        .requestFactory(requestFactory)
        .build();
}
```

## SSL Bundle Only — via `RestClientSsl`

```java
@Service
public class MyService {

    private final RestClient restClient;

    public MyService(RestClient.Builder builder, RestClientSsl ssl) {
        this.restClient = builder
            .baseUrl("https://secure-service")
            .apply(ssl.fromBundle("mybundle"))
            .build();
    }
}
```

## Global Timeouts via Properties

Applies to all `RestClient` instances auto-configured by Spring Boot:

```properties
spring.http.client.connect-timeout=2s
spring.http.client.read-timeout=5s
spring.http.client.redirects=dont-follow
spring.http.client.factory=apache
```

> ⚠️ These properties are **bypassed** when you call `.requestFactory(...)` on the builder. Use `ClientHttpRequestFactorySettings` explicitly in that case.

## Request Interceptor (e.g., Auth Token)

```java
@Bean
RestClient myServiceClient(RestClient.Builder builder) {
    return builder.clone()
        .baseUrl("https://my-service")
        .requestInterceptor((request, body, execution) -> {
            request.getHeaders().setBearerAuth(tokenProvider.getToken());
            return execution.execute(request, body);
        })
        .build();
}
```
