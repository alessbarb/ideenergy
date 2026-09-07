# Changelog

## 2.0.1.dev4

Maintained-fork development release.

### Reliability

- Authenticate on demand instead of relying on periodic keepalive calls.
- Retry an authenticated operation at most once after HTTP 401/403.
- Add a fail-fast circuit breaker after repeated 401/403/429/5xx failures.
- Reset the circuit after a successful authenticated operation or after the cooldown expires.

### Data correctness

- Normalize reversed historical date ranges without collapsing the requested interval.

### Privacy

- Redact username, contract identifiers, request URLs and response payloads from normal client string/error output.

### Engineering

- Add CI across Python 3.11, 3.12, 3.13 and 3.14.
- Build and validate source/wheel distributions in pull requests.
- Keep GitHub Release artifacts for reproducibility.
- Disable automatic PyPI publication in this maintained fork.

## Upstream history

This repository is derived from [`ldotlopez/ideenergy`](https://github.com/ldotlopez/ideenergy). Earlier release history belongs to the upstream project.
