# Target Architecture for a Sellable Multi-Church Product

## Product Direction

The platform should evolve from a single-church operational system into a multi-tenant church management product with:

- multi-church isolation
- web administration
- mobile access for leaders, members, and event participants
- granular permissions
- public event registrations
- integrated online payments
- financial import with AI-assisted transaction creation and categorization

The current backend already gives us a good foundation:

- FastAPI API
- PostgreSQL
- Celery + Redis
- role and permission entities
- upload and statement processing pipeline
- modular backend domains

The next stage should preserve those strengths instead of replacing them.

## Core Architectural Decisions

### 1. Adopt True Multi-Tenancy

Add a first-class `Tenant` or `Church` entity and make it the root boundary for all domain data.

Recommended core entities:

- `tenants`
- `tenant_memberships`
- `tenant_settings`
- `tenant_domains`
- `tenant_billing_accounts`

Recommended relationship model:

- one user can belong to many churches
- one church can have many users
- each membership has its own role and permission grants

This is more scalable than keeping a global role directly on `users`.

### 2. Scope Access by Tenant Membership

The current model mixes:

- `user.role`
- `user.role_id`
- role object permissions

That works for a single organization, but it becomes fragile in SaaS.

Target model:

- `users`: identity only
- `tenant_memberships`: church-scoped access
- `roles`: reusable permission bundles
- `membership_roles`: role assignment inside one tenant
- optional `permission_overrides`: exceptions for special cases

Every protected query should resolve:

1. who is the authenticated user
2. which tenant is active
3. what permissions the user has in that tenant

### 3. Make the API Mobile-First

Keep the backend API as the product center. That allows:

- responsive web admin
- future mobile apps
- public registration pages
- third-party integrations later

Recommendation:

- keep FastAPI
- standardize DTOs and pagination
- return tenant-aware resources consistently
- introduce stable service boundaries by domain

### 4. Keep Statement Upload + AI as a Dedicated Pipeline

The current upload pipeline is a competitive feature and should remain.

Target ingestion flow:

1. tenant uploads statement
2. file stored in object storage
3. processing task parses file
4. AI suggests transaction type and category
5. system creates draft or pending transactions
6. user confirms or adjusts when confidence is low
7. feedback retrains tenant-aware or global models

Recommended improvements:

- store files in S3-compatible storage instead of local disk
- add processing job table with richer lifecycle states
- add confidence thresholds by tenant
- persist model version used in each classification
- support manual correction feedback loop explicitly

### 5. Add Public Commerce Capabilities

Events and registrations should be treated as a separate domain.

Recommended entities:

- `events`
- `event_sessions`
- `event_ticket_types`
- `event_registrations`
- `registration_attendees`
- `payment_orders`
- `payment_transactions`
- `payment_webhook_events`

Important requirement:

- public registration must work without login

That means:

- public event page with slug
- registration checkout token
- guest registration flow
- payment confirmation through webhook

### 6. Payments Must Be Event-Driven

For PIX and card, the architecture should not rely on synchronous confirmation alone.

Recommended provider strategy:

- Brazil-first: Mercado Pago, Pagar.me, Asaas, or Stripe if available for the business model

Recommended flow:

1. create `payment_order`
2. request PIX or card payment from provider
3. redirect or display QR code
4. receive webhook
5. confirm registration
6. generate financial records if applicable

This keeps finance and commerce aligned without coupling the UI to payment success timing.

### 7. Keep Web and Mobile as Different Clients Over the Same API

Recommended product split:

- web admin for finance, reports, configuration, events, and backoffice
- mobile app for leaders, attendance, registrations, member interactions, and lightweight dashboards

Suggested implementation path:

- short term: responsive web for all modules
- medium term: Expo/React Native client for mobile scenarios

## Proposed Domain Map

Recommended bounded contexts:

- `identity`: users, auth, sessions
- `tenancy`: churches, memberships, plans, billing
- `authorization`: roles, permissions, policies
- `finance`: transactions, payables, receivables, budgets, reports, attachments
- `ingestion`: statements, parsing, AI classification, feedback
- `cells`: cells, members, meetings, attendance, lost sheep
- `school`: courses, classes, lessons, students, attendance
- `events`: events, registrations, tickets, check-in
- `payments`: orders, provider integration, webhooks, refunds
- `notifications`: email, WhatsApp, push, reminders
- `audit`: logs, traceability, security events

This can remain a modular monolith at first. It does not need microservices now.

## Recommended Deployment Model

For a secure and scalable sellable product:

- FastAPI app containers
- Celery worker containers
- PostgreSQL managed service
- Redis managed service
- object storage for uploads and attachments
- CDN for static assets
- reverse proxy or managed ingress
- centralized logs and metrics

Recommendation for scale stage:

- start with a modular monolith
- isolate domains in code
- introduce queues for heavy jobs
- split services only when operational load justifies it

## Security Requirements

Minimum product-grade security baseline:

- rotate all default credentials out of non-local environments
- per-tenant authorization checks everywhere
- webhook signature validation
- rate limiting for login and public registration
- audit logs for privileged actions
- secure file validation for uploads
- object storage with signed URLs
- background malware scanning for attachments if needed
- backup and restore strategy
- encrypted secrets management

Recommended future additions:

- SSO for larger churches
- MFA for administrators
- API audit trail by tenant

## Data Isolation Strategy

Recommended first approach:

- every tenant-owned table gets `tenant_id`
- every service query is tenant-scoped
- central dependency resolves active tenant

Possible later hardening:

- PostgreSQL row-level security for critical tables

Start at the application layer now, because it is easier to move quickly while keeping the code readable.

## What Should Change First in the Current Codebase

Highest priority technical changes:

1. introduce `Tenant` and `TenantMembership`
2. move permissions from user-global to tenant-scoped access
3. refactor auth to issue active-tenant context
4. add tenant scoping to finance, cells, school, and reports
5. extract upload and AI pipeline into a more explicit ingestion module
6. add event and payment domains
7. prepare object storage and webhook infrastructure

## Recommended Product Positioning

This should be built as:

- a church operations platform
- with strong finance
- plus ministry management
- plus event commerce

That is a much more sellable story than a generic internal tool.
