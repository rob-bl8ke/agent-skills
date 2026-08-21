# Time Handling

Use this reference when the behavior under test depends on the current time, scheduled execution, retry windows, expiry rules, or time progression between assertions.

## Default Rule: Inject Clock

Production code should depend on `java.time.Clock` instead of calling static time methods directly.

```java
@Service
class ReminderService {

    private final Clock clock;

    ReminderService(final Clock clock) {
        this.clock = clock;
    }

    Instant nextRun() {
        return clock.instant().plus(Duration.ofHours(1));
    }
}
```

## Use Clock.fixed by Default in Tests

Most time-sensitive tests only need deterministic time, not advancing time.

```java
Clock clock = Clock.fixed(Instant.parse("2026-03-24T10:15:30Z"), ZoneOffset.UTC);
ReminderService service = new ReminderService(clock);
```

Start here unless the test truly needs time to move.

## When a MutableClock Is Justified

Use a test-only `MutableClock` when the same test must advance time across several phases.

Good use cases:
- scheduled-event execution
- retry-window progression
- expiry and grace-period rules
- polling loops
- multi-step workflows where the business outcome changes over time

## MutableClock Implementation

```java
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.util.Objects;

public final class MutableClock extends Clock {

    private final Instant originalInstant;
    private final ZoneId zoneId;
    private Instant currentInstant;

    public MutableClock(final Instant initialInstant, final ZoneId zoneId) {
        this.originalInstant = Objects.requireNonNull(initialInstant, "initialInstant must not be null");
        this.currentInstant = initialInstant;
        this.zoneId = Objects.requireNonNull(zoneId, "zoneId must not be null");
    }

    @Override
    public ZoneId getZone() {
        return zoneId;
    }

    @Override
    public Clock withZone(final ZoneId zone) {
        return new MutableClock(currentInstant, zone);
    }

    @Override
    public Instant instant() {
        return currentInstant;
    }

    public void setInstant(final Instant instant) {
        this.currentInstant = Objects.requireNonNull(instant, "instant must not be null");
    }

    public void advanceBy(final Duration duration) {
        this.currentInstant = this.currentInstant.plus(Objects.requireNonNull(duration, "duration must not be null"));
    }

    public void advanceTo(final Instant instant) {
        this.currentInstant = Objects.requireNonNull(instant, "instant must not be null");
    }

    public void reset() {
        this.currentInstant = originalInstant;
    }
}
```

Usage guidance:
- wire it as a test-only Spring bean when a Spring context is involved
- call `reset()` in `@BeforeEach` when tests share the same instance
- prefer it only when time progression is genuinely part of the behavior under test — `Clock.fixed(...)` is always the first choice
