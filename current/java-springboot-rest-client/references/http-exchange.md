# RestClient — `@HttpExchange` Declarative Clients

Preferred for stable, well-defined downstream APIs.

## Step 1: Define the Interface

```java
@HttpExchange(url = "/pets", accept = MediaType.APPLICATION_JSON_VALUE)
public interface PetServiceClient {

    @GetExchange("/{id}")
    Pet getById(@PathVariable long id);

    @GetExchange
    List<Pet> findAll(@RequestParam(required = false) String status);

    @PostExchange
    ResponseEntity<Void> create(@RequestBody Pet pet);

    @PutExchange("/{id}")
    void update(@PathVariable long id, @RequestBody Pet pet);

    @DeleteExchange("/{id}")
    void delete(@PathVariable long id);
}
```

## Step 2: Create the Proxy Bean

```java
@Bean
PetServiceClient petServiceClient(RestClient.Builder builder, PetServiceProperties props) {
    RestClient restClient = builder.clone()
        .baseUrl(props.baseUrl()) // baseUrl injected via PetServiceProperties — see configuration.md
        .defaultStatusHandler(HttpStatusCode::is4xxClientError, (req, res) -> {
            throw new PetServiceClientException(res.getStatusCode());
        })
        .defaultStatusHandler(HttpStatusCode::is5xxServerError, (req, res) -> {
            throw new PetServiceUnavailableException(res.getStatusCode());
        })
        .build();
    RestClientAdapter adapter = RestClientAdapter.create(restClient);
    HttpServiceProxyFactory factory = HttpServiceProxyFactory.builderFor(adapter).build();
    return factory.createClient(PetServiceClient.class);
}
```

## Step 3: Inject and Use

```java
@Service
public class PetApplicationService {

    private final PetServiceClient petServiceClient;

    public PetApplicationService(PetServiceClient petServiceClient) {
        this.petServiceClient = petServiceClient;
    }

    public Pet getPet(long id) {
        return petServiceClient.getById(id);
    }
}
```

## Notes

- `defaultStatusHandler` configured on the underlying `RestClient` bean applies transparently to `@HttpExchange` proxy clients — the proxy calls through the same `RestClient` instance. No need to replicate error handling on the interface.
- If an `@HttpExchange` method returns `void`, the status handler still fires. Declare the method as `ResponseEntity<Void>` only if the calling code needs to inspect the status or headers.
