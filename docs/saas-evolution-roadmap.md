# SaaS Evolution Roadmap

## Product Goal

Turn the current project into a secure, scalable, multi-church SaaS product while preserving:

- financial reports
- statement upload
- AI-assisted transaction creation and categorization
- cells module
- bible school module
- current admin capabilities

## Non-Negotiables

- multi-church support
- web and mobile readiness
- better permission levels
- public event registrations without login
- PIX and card payments
- secure and scalable architecture
- maintain existing reporting and finance features

## Phase 0. Stabilize the Base

Goal: stop architectural drift before adding major SaaS features.

Deliverables:

- remove default production-like credentials from all flows
- standardize auth and permission checks
- audit current endpoints for role leakage
- add test coverage for auth, permissions, upload, payables, receivables, and reports
- centralize settings for storage, payments, and tenant resolution

Success criteria:

- critical flows covered by automated tests
- permission logic is consistent across modules
- deployment can be repeated safely

## Phase 1. Multi-Church Foundation

Goal: make the entire system tenant-aware.

Deliverables:

- add `tenants` and `tenant_memberships`
- add `tenant_id` to tenant-owned tables
- introduce active-tenant resolution in auth
- refactor queries to be tenant-scoped
- migrate existing single-church data into a default tenant
- update audit logs to include tenant context

Success criteria:

- one user can belong to multiple churches
- data isolation works across tenants
- reports and dashboards only show active tenant data

## Phase 2. Authorization 2.0

Goal: make permissions product-grade.

Deliverables:

- move from global user role semantics to membership-scoped permissions
- define permission matrix by module and action
- create support for role templates per tenant
- add optional direct grants or overrides for edge cases
- add UI for managing tenant roles safely

Target permission layers:

- platform super admin
- tenant admin
- finance manager
- finance operator
- cells leader
- school coordinator
- events manager
- read-only auditor

Success criteria:

- permissions are resolved per tenant membership
- admin users can manage roles without bypassing tenant boundaries
- public event registrants remain outside admin auth flows

## Phase 3. Product UX for Web and Mobile

Goal: support a modern sellable product experience.

Deliverables:

- keep web as the full backoffice
- improve responsive layout for mobile web immediately
- define mobile-facing endpoints for attendance, events, payments, and notifications
- prepare a dedicated mobile app backlog

Recommended strategy:

- short term: responsive admin and public web
- medium term: Expo/React Native mobile app

Success criteria:

- public flows work well on mobile browsers
- admin backoffice is usable on tablet and mobile for light operations
- API contracts are stable for future mobile clients

## Phase 4. Events and Registrations

Goal: create a revenue and engagement feature set.

Deliverables:

- event CRUD
- public event pages by slug
- registration forms without login
- free and paid registrations
- confirmation emails and receipts
- registration dashboard for organizers
- attendee status lifecycle

Recommended registration statuses:

- pending
- awaiting_payment
- paid
- cancelled
- refunded
- checked_in

Success criteria:

- anyone can register without creating an account
- churches can track registrations and attendees
- event data remains tenant-scoped

## Phase 5. PIX and Card Payments

Goal: monetize registrations safely.

Deliverables:

- provider abstraction layer
- PIX checkout
- card checkout
- webhook processing
- reconciliation of payment state to registration state
- financial record generation where applicable

Recommendation:

- implement one provider first, not many
- choose based on Brazilian market, webhook quality, split capability, and operational cost

Success criteria:

- public checkout works without login
- webhook retries are idempotent
- finance records can be generated from confirmed payments

## Phase 6. Storage and Processing Hardening

Goal: make uploads and background jobs production-ready.

Deliverables:

- move uploads to object storage
- signed download URLs
- explicit import job lifecycle
- richer retry handling
- observability on AI classification and parsing failures
- model version tracking

Success criteria:

- statement upload remains reliable at scale
- AI suggestions are explainable and auditable
- support can inspect failed imports quickly

## Phase 7. Reporting and Commercial Readiness

Goal: turn the platform into a real product.

Deliverables:

- tenant billing and plan control
- usage metrics
- exportable reports
- support dashboards
- security logs
- onboarding flow for new churches
- terms, privacy, and consent features where needed

Success criteria:

- new tenant onboarding is repeatable
- plan restrictions and limits are enforceable
- support team can operate the product efficiently

## Recommended Delivery Order

If we want the safest path with the highest business value:

1. stabilize auth, permissions, and tests
2. make the core truly multi-tenant
3. improve web/mobile API readiness
4. add events and public registrations
5. integrate payments
6. harden uploads, AI, storage, and observability
7. close the SaaS billing and onboarding loop

## Suggested MVP for a Sellable Version

A credible first sellable version should include:

- multi-church access
- tenant-scoped roles and permissions
- finance with reports and upload+AI
- public event registration
- PIX and card payments
- responsive web
- audit logging
- production deployment baseline

That is enough to present as a real church management product instead of an internal prototype.
