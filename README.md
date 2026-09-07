# ideenergy

Programmatic access to consumer energy consumption from https://www.i-de.es/ (Spanish energy distributor).

<!-- Code and releases -->

![GitHub Release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/alessbarb/ideenergy?include_prereleases)
[![CI](https://github.com/alessbarb/ideenergy/actions/workflows/ci.yml/badge.svg)](https://github.com/alessbarb/ideenergy/actions/workflows/ci.yml)
[![Create release](https://github.com/alessbarb/ideenergy/actions/workflows/release.yml/badge.svg)](https://github.com/alessbarb/ideenergy/actions/workflows/release.yml)

This repository is a maintained fork of [`ldotlopez/ideenergy`](https://github.com/ldotlopez/ideenergy). Original authorship and GPL licensing are preserved. The maintained Home Assistant integration is [`alessbarb/ha-ideenergy`](https://github.com/alessbarb/ha-ideenergy).

The fork focuses on conservative, bounded access to i-DE's private web endpoints:

- authenticate on demand rather than keeping sessions alive continuously;
- perform at most one re-authentication retry after an authentication rejection;
- stop repeated requests temporarily after consecutive 401/403/429/5xx failures;
- preserve zero and reversed-range historical queries correctly;
- preserve real elapsed hours across Europe/Madrid daylight-saving transitions;
- preserve decimal precision in accumulated meter readings;
- avoid account identifiers, request URLs and response payloads in normal logs/errors;
- test supported Python versions 3.11 through 3.14.

## Two-factor authentication

i-DE can require an SMS second factor before allowing a session. The private web API currently used by this project does not have a documented, stable OTP challenge contract that this client can safely implement, so this fork does **not** claim native SMS/OTP support.

Experiments reported by the upstream maintainer indicate that a session established after completing 2FA in an i-DE first-party client may stay usable while it is kept alive with regular requests. This fork deliberately does not use that as a workaround: i-DE also warns that automated or excessive access can lead to temporary account blocking, and keeping a session alive solely to avoid 2FA would conflict with the conservative request policy above.

If i-DE requires 2FA and rejects the automated login, complete the required authentication through i-DE's own website/app. The maintained Home Assistant integration handles ordinary expired/rejected sessions and transient API failures, but it cannot complete an SMS challenge on your behalf until a reliable protocol is known.

## Distribution policy for this fork

GitHub releases may contain source and wheel artifacts for reproducibility. This fork does **not** automatically publish the `ideenergy` project to PyPI. Consumers that need these maintained changes should use an immutable Git commit or a release artifact until a separately named/authorized package distribution is established.

## Useful links

- [Maintained Home Assistant integration](https://github.com/alessbarb/ha-ideenergy)
- [Upstream client project](https://github.com/ldotlopez/ideenergy)
- [Documentation about other distributors](https://www.genbeta.com/web/como-saber-consumo-electrico-tiempo-real-casa)
