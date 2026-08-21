# RestClient — Error Handling Patterns

## Exception Type Reference

| Exception | When thrown | Retry? |
|---|---|---|
| `ResourceAccessException` | Network failure, connection refused, read timeout, I/O error | ✅ Yes — transient |
| `HttpServerErrorException` (5xx) | Server returned a 5xx response | ⚠️ Only if the operation is idempotent |
| `HttpClientErrorException` (4xx) | Server returned a 4xx response | ❌ No — not a transient fault |
| `UnknownHttpStatusCodeException` | Unrecognised status code | ❌ No |

> Exceptions thrown from `defaultStatusHandler` or `onStatus` handlers must be types your retry layer is configured to act on. Throw a typed exception — a generic `RuntimeException` will not be matched by retry whitelists.

## Per-Request Status Handler (`onStatus`)

```java
Pet pet = restClient.get()
    .uri("/pets/{id}", id)
    .retrieve()
    .onStatus(HttpStatusCode::is4xxClientError, (request, response) -> {
        throw new PetNotFoundException(id, response.getStatusCode());
    })
    .body(Pet.class);
```

## Bean-Level Default Status Handler

```java
@Bean
RestClient orderServiceClient(RestClient.Builder builder, OrderServiceProperties props) {
    return builder
        .baseUrl(props.baseUrl()) // baseUrl injected via OrderServiceProperties — see configuration.md
        .defaultStatusHandler(
            HttpStatusCode::isError,
            (request, response) -> {
                throw new DownstreamServiceException(
                    request.getURI(), response.getStatusCode());
            })
        .build();
}
```

## Low-Level `exchange()` — Full Control

Use only when you need both request and response simultaneously, or need to stream the body manually. Note: default status handlers do **not** apply when using `exchange()`.

```java
Pet result = restClient.get()
    .uri("/pets/{id}", id)
    .accept(MediaType.APPLICATION_JSON)
    .exchange((request, response) -> {
        if (response.getStatusCode().is4xxClientError()) {
            throw new PetNotFoundException(id, response.getStatusCode());
        }
        return objectMapper.readValue(response.getBody(), Pet.class);
    });
```
