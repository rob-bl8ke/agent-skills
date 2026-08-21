# RestClient — Request Examples

## GET — body only

```java
Pet pet = restClient.get()
    .uri("/pets/{id}", id)
    .accept(MediaType.APPLICATION_JSON)
    .retrieve()
    .body(Pet.class);
```

## GET — collection (`ParameterizedTypeReference`)

```java
List<Pet> pets = restClient.get()
    .uri("/pets")
    .retrieve()
    .body(new ParameterizedTypeReference<List<Pet>>() {});
```

## GET — `ResponseEntity` (status + headers + body)

```java
ResponseEntity<Pet> response = restClient.get()
    .uri("/pets/{id}", id)
    .retrieve()
    .toEntity(Pet.class);

HttpStatusCode status = response.getStatusCode();
HttpHeaders headers = response.getHeaders();
Pet pet = response.getBody();
```

## POST — with JSON body

```java
ResponseEntity<Void> response = restClient.post()
    .uri("/pets")
    .contentType(MediaType.APPLICATION_JSON)
    .body(newPet)
    .retrieve()
    .toBodilessEntity();

URI created = response.getHeaders().getLocation();
```

## PUT / PATCH

```java
restClient.put()
    .uri("/pets/{id}", id)
    .contentType(MediaType.APPLICATION_JSON)
    .body(updatedPet)
    .retrieve()
    .toBodilessEntity();
```

## DELETE

```java
restClient.delete()
    .uri("/pets/{id}", id)
    .retrieve()
    .toBodilessEntity();
```

## Dynamic HTTP Method

```java
restClient.method(HttpMethod.POST)
    .uri("/pets")
    .body(pet)
    .retrieve()
    .body(Pet.class);
```

## Multipart Upload

```java
MultiValueMap<String, Object> parts = new LinkedMultiValueMap<>();
parts.add("file", new FileSystemResource(path));
parts.add("metadata", new HttpEntity<>(myDto, jsonHeaders));

restClient.post().uri("/upload").body(parts).retrieve().toBodilessEntity();
```
