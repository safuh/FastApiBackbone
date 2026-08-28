# Authentication Module

The auth module owns security primitives, not an application's complete identity domain.

## Current capability

`TokenService` creates and validates signed JWTs with:

- `sub` subject claims;
- `iat` issued-at timestamps;
- `exp` expiration validation;
- explicit token type claims; and
- a minimum signing-secret length guard.

## Planned identity layer

The production identity module will add password hashing, OAuth2 flows, refresh-token rotation/revocation, user persistence, RBAC/scopes, rate limiting, audit events, and security regression tests.

Refresh tokens must not be treated as interchangeable with access tokens. Revocation state belongs to server-side persistence or an explicitly designed stateful mechanism; a self-contained JWT alone cannot provide reliable revocation.

## Security boundary

Applications must supply secrets through deployment configuration or a secret manager. Never commit signing keys to source control or examples.

See [`SECURITY.md`](../../../SECURITY.md) and the identity milestones in [`../../MILESTONES.md`](../../MILESTONES.md).
