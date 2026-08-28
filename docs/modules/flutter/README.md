# Flutter Module

Flutter is an optional first-class client target. It is deliberately decoupled from the backend package.

## Target architecture

```text
FastAPI
  ↓
OpenAPI contract
  ↓
Dart client/model generation
  ↓
Flutter application
```

The generated client will not manually duplicate backend request/response models. OpenAPI is the contract source of truth.

## Planned capabilities

- environment-aware API configuration;
- generated API client and models;
- authentication/session abstraction;
- secure token-storage abstraction;
- login/logout/refresh example;
- unit/widget tests; and
- static analysis in CI.

Flutter assets are currently a roadmap milestone. No backend functionality depends on Flutter being installed.
