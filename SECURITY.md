# Security Policy & Demo Hardening Disclosure — Land Logic (SIH 2026)

This document provides a transparent overview of the security architecture implemented for the Land Logic DRONE-MAPPING-AI prototype demonstration.

---

## 🛡️ What IS Covered

1. **Shared API Key Authentication**:
   - The primary prediction routes (`POST /predict` and `POST /api/v1/predict`) require an `X-API-Key` header matching the server's `API_KEY` environment variable.
   - Constant-time string comparison (`secrets.compare_digest`) prevents timing attacks.
   - Fail-closed behavior: if `API_KEY` is not set on the server, incoming protected requests are immediately rejected with HTTP 401 and a startup warning is logged.
   - `/health` remains intentionally unauthenticated to support platform health probes and uptime checkers (e.g. Render, UptimeRobot).

2. **Layered Safe Image Decoding & Input Sanitization**:
   - File extensions are restricted to `.jpg`, `.jpeg`, `.png`, and `.dng`.
   - File size is strictly capped at 15MB per file before processing.
   - Safe image decode: every uploaded file is decoded and verified (`PIL.Image.open` + `verify()` + partial `load()`) to prevent broken checksums, corrupted byte streams, or renamed non-image files from causing deep pipeline crashes in OpenCV/AI.
   - Corrupted or invalid files are cleanly deleted from disk and rejected with HTTP 422 (`File '<filename>' is not a valid, decodable image`).
   - Decompression bomb protection: `Image.MAX_IMAGE_PIXELS` limits prevent pixel flood denial-of-service.

3. **In-Flight Concurrency Guard (Anti-Exhaustion)**:
   - Heavy drone stitching and AI inference tasks are constrained by an asynchronous semaphore/concurrency guard (default: 3 simultaneous tasks).
   - If judges or users exceed the concurrency threshold, the server immediately returns **HTTP 503** (`Server busy, try again in a moment`) to protect single-worker instances from out-of-memory (OOM) termination.

4. **Sanitized Error Responses**:
   - Internal pipeline errors, file paths, and raw stack traces are not leaked in HTTP response payloads. Structured errors return concise stage-specific failure messages.

5. **Configurable CORS**:
   - Cross-Origin Resource Sharing is controlled via `ALLOWED_ORIGINS` to prevent unauthorized cross-origin browser requests.

---

## ⚠️ What IS NOT Covered (Intentional Prototype Scope)

This system is configured as an educational hackathon demonstration and prototype. It **does not** include:

1. **No Multi-Tenant or Per-User Authentication**:
   - There are no user accounts, passwords, OAuth2/OIDC, or JWT sessions. All authorized access is via the single shared `API_KEY`.
2. **No Dynamic Token Revocation or Scopes**:
   - The shared API key does not have granular permissions or per-client access tiers.
3. **No IP-Based Rate Limiting or DDoS Scrubbing**:
   - There is no Redis-backed token-bucket rate limiter. Request rate throttling beyond the concurrency guard (cap of 3) must be handled upstream at the reverse proxy / CDN tier (e.g., Cloudflare WAF, Render DDoS mitigation).
4. **No Persistent Database Encryption at Rest**:
   - Flight session metadata and job logs are kept in-memory for the duration of the container lifecycle.
5. **No Sandboxing of Native Libraries**:
   - OpenCV and GDAL operate directly in the worker process environment without isolated container virtualization.

---

## 🚨 Reporting Security Issues
To report a vulnerability or inquire about security controls, please contact the development team via the project repository issue tracker.
