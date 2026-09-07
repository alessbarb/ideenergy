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
- avoid account identifiers, request URLs and response payloads in normal logs/errors;
- test supported Python versions 3.11 through 3.14.

## Distribution policy for this fork

GitHub releases may contain source and wheel artifacts for reproducibility. This fork does **not** automatically publish the `ideenergy` project to PyPI. Consumers that need these maintained changes should use an immutable Git commit or a release artifact until a separately named/authorized package distribution is established.

## Useful links

- [Maintained Home Assistant integration](https://github.com/alessbarb/ha-ideenergy)
- [Upstream client project](https://github.com/ldotlopez/ideenergy)
- [Documentation about other distributors](https://www.genbeta.com/web/como-saber-consumo-electrico-tiempo-real-casa)
