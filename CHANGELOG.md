# Changelog

## 2.0.1.dev4

Maintained-fork development release.

### Reliability

- Authenticate on demand instead of relying on periodic keepalive calls.
- Retry an authenticated operation at most once after HTTP 401/403.
- Add a fail-fast circuit breaker after repeated 401/403/429/5xx failures.
- Reset the circuit after a successful authenticated operation or after the cooldown expires.
- Deliberately avoid artificial keepalive traffic as a workaround for i-DE SMS 2FA because the private API has no documented OTP challenge contract and excessive automated access can lead to account blocking.

### Data correctness

- Normalize reversed historical date ranges without collapsing the requested interval.
- Preserve real elapsed hourly periods across Europe/Madrid DST transitions, including the 23-hour spring day and both repeated 02:00 hours on the 25-hour autumn day.
- Preserve decimal precision returned by i-DE for accumulated meter readings instead of truncating them to integer kWh.

### Privacy

- Redact username, contract identifiers, request URLs and response payloads from normal client string/error output.

### Engineering

- Add CI across Python 3.11, 3.12, 3.13 and 3.14.
- Build and validate source/wheel distributions in pull requests.
- Keep GitHub Release artifacts for reproducibility.
- Disable automatic PyPI publication in this maintained fork.

## Upstream history

This repository is derived from [`ldotlopez/ideenergy`](https://github.com/ldotlopez/ideenergy). Earlier release history belongs to the upstream project.
