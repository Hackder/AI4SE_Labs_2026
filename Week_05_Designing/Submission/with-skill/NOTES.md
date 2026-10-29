# OneSport architecture: discussion notes (run with the architecture-design skill)

Requirements: `Tasks/data/OneSport.txt` (system description and 24 user stories).
Working rules: one topic at a time, no move to the ADR until the student asks, notes updated after every settled point.
The student asked that the earlier session's design (`Submission/ADR.md`, `Submission/NOTES.md`, transcript) not be read. Before that request, the assistant had read the skill's `lessons.md` and the first 30 lines of the earlier `NOTES.md`.

## Phase 1: Requirements and drivers

### Most stories are commodity; a few carry the architecture

Commodity (named once, not discussed further):
- Auth and account: 1 signup, 2 login, 3 logout from the navbar, 4 profile settings, 6 change email and password.
- List views: 7 recent news, 11 upcoming tickets, 20 saved news, 21 saved tickets, 22 friend list.
- Story 15 (clear all favourites) is a bulk delete over the collections.

Candidate drivers (not yet agreed):
1. **Ticket purchase.** The description promises "a convenient platform for purchasing tickets". Stories 11–14 only browse and collect. If purchase is in scope, it brings inventory, contention on the last seats, payment through an external provider, and orders that must outlive the user.
2. **Where news and events come from.** "Up-to-date" news on "a wide range of sports" implies either ingestion from outside sources (background work, external systems) or in-house writing (an editorial role no story names), or both.
3. **Collections reference items with their own lifecycle** (9, 10, 13, 14, 15, 20, 21). Saved tickets point at events that end, sell out, or get cancelled. Saved news can be removed or edited.
4. **Social graph** (16–19, 22–24). A friend request state machine (pending, accepted, refused), a symmetric friendship, and lookup by email (19) that can reveal whether an email has an account.
5. **Account deletion cascade** (5). It touches collections, friendships, pending requests and, if purchase is in scope, orders, which must survive the user's deletion.
6. **Country as a data dimension** (8, 12). The filters need every news item and event to carry a country, whatever its source.

Scope questions (for the student to decide):
- Q1. Is ticket purchase in scope, and is it a sale inside OneSport or a redirect to the organiser's vendor?
- Q2. Where does content come from: outside feeds, in-house editors, or both?
- Q3. Which roles exist besides User (editor, admin, event organiser)?

### The student settled scope: both sale modes, both content sources, editors and admins

- Q1: purchase is in scope. Some events sell inside OneSport, others redirect to the organiser's vendor.
- Q2: content comes from automatic feeds and from in-house editors.
- Q3: the roles are User, Editor and Admin. No self-serve event organiser.

Proposed driver list after scope (awaiting agreement):
1. Native ticket sale: per-event inventory, contention on the last seats, payment through an external provider, orders that outlive the user.
2. Two fulfilment modes per event (native, redirect), as a field that only checkout reads.
3. One news model and one event model fed by two sources (feed adapters and editors). A per-source policy field decides whether ingested items publish directly or wait for review. Every item carries a country (8, 12).
4. A back office for Editor and Admin: writing, review queue, source configuration, event and inventory entry.
5. Collections that reference news and events with their own lifecycle.
6. Social graph with a request state machine, and email lookup that must not reveal who has an account.
7. Account deletion cascade that removes social and collection data but keeps orders.

The student agreed to the seven drivers and to A5.

## Phase 2: Four architectures

### The four shapes differ most on seat contention and on account deletion

| | Content (drivers 3, 4) | Purchasing (1, 2) | Social and accounts (5, 6, 7) | Verdict |
|---|---|---|---|---|
| A. Modular monolith, one database, worker mode | Feed adapters run in a worker mode of the same codebase. The back office is part of the same app. | Seat inventory sits in the shared database, and buyers queue on row locks for the hot event. Payment webhooks go through an outbox table. | Collections and friendships use foreign keys. Deletion is one transaction. | Simplest. Its weak spot is the hot event row, which also loads the database that serves news. |
| B. Domain services (content, commerce, identity with social), own databases, message broker | The content service owns ingestion and the back office. | Commerce isolates the sale load from news, but the hot row remains inside commerce. | Deletion becomes a cascade of events across services. Collections reference another service's data. | Isolates load, but pays with a broker, deletion spread across services, and references across services. |
| C. Event log with read models | Ingestion and edits become events. Projections serve the views, including country filters. | Reservations become events, and the last seat still needs one sequencer per event. | An append-only log conflicts with deletion, so it needs encryption keys deleted per user. | Gives full history, but costs a lot for a mostly create-read-update-delete app. |
| D. Managed services (hosted auth, headless CMS, provider checkout, cloud functions) | The CMS supplies the editor UI. Cloud functions push feeds into it. | The provider takes payment, but no commodity service holds seat inventory. | Users live in hosted auth and friendships in a hosted database. Deletion spans several vendors. | Fastest start, but the hardest part (seats) is not a commodity, so it gets built anyway. |

Assistant's lean: A, because most of the system is reads and writes that profit from one database and one transaction (deletion, collections). The one part that does not fit is contention on seats, which probably gets carved out of A rather than splitting everything as B does.

The student ruled out D and chose purchasing as the first subsystem.

## Phase 3: Purchasing

### Every surviving shape needs one writer per event; they differ in where it lives

The hard problem is one event's seats under A5: many buyers, one small set of rows. Options compared:

1. **Row lock in the shared database (plain A).** A conditional update per purchase. Buyers serialise on one row, each holds a database connection while waiting, the pool runs dry, and news pages slow down with the sale. Rejected for hot events.
2. **Queue in front of the writer (A or B).** It defers the spike rather than removing it. Users wait without an answer, re-clicks add more messages, and the app tracks thousands of open connections. Rejected.
3. **One single-threaded writer per event, answering synchronously.** It holds the event's seat state in memory, takes requests in batches (one click is a batch of one), and answers in milliseconds. Events spread across threads or nodes; one event never spans two. B's commerce service and C's per-event sequencer both end up here, so B and C add no purchasing advantage over a carved-out A.

Open question inside option 3, where the writer persists:
- 3a. Writer inside the monolith, committing each batch to the main database. No new store, but a hot sale still writes to the database that serves news.
- 3b. Separate seat service with its own reservation log, not facing the internet, called by the web tier. Isolates the sale, at the cost of a second persistent store.

### A separate seat service keeps a sell-out away from the news database (D1)

The student chose 3b. The seat service is a separate process with one single-threaded writer per event and its own append-only reservation log. Only the web tier calls it, and it does not face the internet. If it fails, sales stop and the rest of the site keeps running. Recovery replays the log.

### The seat service holds seats, not money (proposed, awaiting agreement)

Data:
- Category: event, name, kind (`named` or `pool`), capacity for pools.
- Seat: category, label. Only named categories have seats.
- Reservation: id, event, idempotency key, opaque order reference from the web tier, lines (category plus seat, or category plus quantity), status, `created_at`, `status_changed_at`.

Statuses (revised under D3): `held` → `confirmed`, and `held` → `cancelled`. Expiry is not a status anyone writes. A reservation is live when it is `confirmed`, or `held` within 10 minutes of `created_at`.

Rules:
- R1. A named seat belongs to at most one live reservation.
- R2. For a pool, the sum of live quantities never exceeds capacity.
- R3. Every call carries an idempotency key. Repeating a call returns the first result.
- R4. Only the listed transitions are allowed. Refunding a confirmed reservation is a business rule outside the service.
- R5. Nothing writes on a timer. Expiry is a condition on status and timestamp.
- R6. Every change is appended to the log before the answer goes out. The in-memory state is a replay of the log.
- R7. No prices, payments or user data. Those live in the main database.

API, batch-shaped: `hold(event, requests[])`, `confirm(ids[])`, `cancel(ids[])`, `availability(event)`.

The student confirmed both seat kinds: named seats and pools. The model above stands (D2).

### Orders and money live in the main database; the payment webhook confirms the seat directly (D3)

Ownership split:
- The seat service owns event structure (categories, seats, capacities) and reservations. The back office defines an event's structure by calling the seat service.
- The main database owns prices per category id, orders, tickets, and payment records.

The assistant first proposed an inbox, an outbox and a worker that relays confirmations to the seat service, plus a separate `payment_pending` status. The student rejected the relay worker and gave a simpler flow, which the assistant accepted:
1. The request comes in and the web tier forwards it to the seat service, which holds the seats for 10 minutes.
2. On success, the web tier creates a pending order and sends the user to the provider's hosted checkout (A4).
3. If the user does not pay within 10 minutes, the hold lapses. If they pay, the provider's webhook reaches the web tier, which marks the order paid and calls `confirm` in the same request.

Why no relay worker is needed: payment providers retry a webhook that fails. If the seat service is down, the webhook handler returns an error and the provider tries again later. The provider's retry does the outbox's job. Confirm is idempotent (R3), so a repeated webhook is harmless.

Status model change: `payment_pending` is dropped. Statuses are `held`, `confirmed`, `cancelled`, and one 10-minute window from `created_at` decides whether a hold still counts.

Redirect sale: `fulfilment_mode = redirect` with a vendor URL. The event page shows a link. There is no order, no seat service call, and no availability. Only the checkout code reads `fulfilment_mode`. Saved tickets (13, 14, 21) reference events, so they work for both modes.

### A late payment still gets its seats if nobody took them (D4)

R8: `confirm` on a lapsed hold succeeds when the seats are still free, and refuses otherwise. A refused confirm leaves the order `paid_unfulfilled` for a refund (policy outside the architecture). The provider's checkout session expires shortly before the hold does, so late payments are rare.

### Live updates are pushed, and push is built once for the whole system (D5)

The event page for a native sale shows seats left per category. Other features that would also want live updates: new friend requests (17), newly published news (7).

- **Poll.** The page asks every few seconds and the web tier calls `availability`. Load grows with viewers times frequency, and lands on the hot event during a sale. Each feature adds its own polling.
- **Push, built once.** The seat service publishes each event's full availability once per second on a message bus. Web tier nodes subscribe and forward to browsers over server-sent events. Load on the seat service does not depend on the number of viewers. A missed message is corrected by the next tick, so there is no reconciliation, and the tick doubles as a heartbeat. Other features add subjects, not mechanisms.

The student chose push, system-wide. Rule: availability reaches the page only by push. The page never pulls it, so there is one source per number.

### The bus carries no state, so NATS core fits (D6)

The bus only carries the once-per-second availability tick and, later, other subjects. Losing a message costs at most a second, so the bus needs no retention.

- **Postgres notifications (main database).** No new component, and publishing can be tied to a commit. But the seat service would need a connection to the main database, which undoes its isolation (D1). Deciding reason against.
- **Redis pub/sub.** Fire-and-forget, adequate. Redis also invites use as a cache or store, which the design avoids.
- **NATS core, without its persistence layer.** Fire-and-forget subjects with wildcards (`seats.<event>`, `user.<id>.friends`). Nothing to back up, a single small binary.
- **Kafka.** A persistent log. It would become a third persistent store for data that is stale after a second. Rejected.

The student chose NATS core. Against Redis the margin is small; the deciding reason is that it does only messaging.
Rule for publishers other than the seat service: publish only after the database transaction commits.

### Purchasing state has two persistent homes

| State | Source of truth | Lifetime |
|---|---|---|
| Event layout: categories, seats, capacities | Seat service log | Until the event ends |
| Reservations | Seat service log | Until the event ends; then the per-event log is closed and archived, so restart replays only open events |
| Seats left per category | Seat service memory, pushed once per second | One second |
| Event details: name, date, country, `fulfilment_mode`, vendor URL | Main database | As long as the event is listed |
| Prices per category | Main database | As long as the event is listed |
| Orders, tickets, payment records | Main database | Legal retention; outlive the user (driver 7) |
| Checkout session | Payment provider | Minutes |
| Bus messages | None | Not stored |

The student moved on to content and the back office, which closes purchasing.

## Phase 3: Content and back office

### Content is one module of the monolith, fed by adapters in its worker mode (D7)

Against B (a content service with its own database): collections, deletion and the country filter join content with users, so a separate database buys nothing. Against C (event log): article edit history is the only gain, and a revisions table gives that.

Model:
- Source: id, adapter name, endpoint, fetch interval, `policy` (`auto_publish` or `review`), default sport and country.
- Article: id, `source_id` (null for editor-written), `external_id` (unique per source), title, body, sport, country, status (`pending_review`, `published`, `withdrawn`), `published_at`, `edited_by`.
- Article revision: article, editor, time, previous body. Gives edit history without an event log.
- Events take the same source dimension, so official fixture feeds and editors both create them.

Ingestion: the worker mode runs each source's adapter at its interval. An adapter fetches, maps the item to an article draft (including country, for 8 and 12), and upserts on (`source_id`, `external_id`). The source's `policy` decides the initial status, and it is read in one place. Code grows by one adapter per source. After commit, a published item goes out on `news.<country>` (D5).

Back office: editors write, review the `pending_review` queue, and withdraw. Admins manage sources and roles. It is part of the same web app, behind the Editor and Admin roles.

### An editor's edit freezes the item against later feed updates (D8)

The first editor edit sets `editor_locked` on the article. The adapter's upsert skips locked rows, as a condition in the same statement, so no extra code path exists. Corrections from the source to a locked item are lost; the student accepted that.

### Saved items point at content and show its current state (D9)

- `saved_article(user, article, saved_at)` and `saved_event(user, event, saved_at)`, with foreign keys and a uniqueness constraint per pair. Stories 9, 10, 13, 14, 20, 21.
- Story 15 (clear all) deletes both sets in one transaction.
- Content is never hard-deleted. Withdrawn articles and past, cancelled or sold-out events keep their rows, so references stay valid.
- The saved list reads status from the article or event row when it renders. It holds no copy, so there is one source.
- Saving an event does not hold seats. Only `hold` (D3) holds seats, for 10 minutes.
- Sold-out state comes from the seat service's push (D5), like on the event page.

The student agreed to D9.

### Content state lives in the main database only

| State | Source of truth | Lifetime |
|---|---|---|
| Sources and their policy | Main database | Until an admin removes the source |
| Articles and revisions | Main database | Permanent; withdrawn, never deleted |
| Event details | Main database | Permanent; past events kept for saved lists and orders |
| Saved articles and events | Main database | Until the user removes them or deletes the account |
| New-article notices | NATS `news.<country>` | Not stored |

## Phase 3: Social and accounts

### A request table plus a canonical friendship row (D10)

- `friend_request(id, from_user, to_user, created_at)`, at most one per unordered pair. Story 16 creates it, 17 lists incoming ones.
- `friendship(user_low, user_high, since)`, one row per pair with the smaller id first, so the relation is symmetric by construction.
- Accept (23): one transaction deletes the request and inserts the friendship. Refuse (24): delete the request. Remove a friend (18): delete the friendship.
- If B sends a request while A's request to B is pending, the system treats it as acceptance. One rule, no duplicate pair.
- After commit, the web tier publishes on `user.<id>.friends` (D5), so the recipient's badge updates without polling.

### Email lookup is limited four ways (D11)

Story 19 finds a user by email. A found result necessarily confirms the email has an account. Options to limit what this leaks:
- Exact match only, no partial search. Logged-in users only.
- A per-user lookup limit per day, counted in the main database.
- A profile setting `discoverable_by_email`, default on. When off, the lookup answers "not found".
- Non-friends see only display name and avatar.

The student agreed to D10 and chose all four lookup limits (D11).

### Deleting an account is one transaction in the main database (D12)

Story 5. One transaction:
- deletes saved articles and events, friend requests in both directions, friendships, and lookup counters;
- sets `order.user_id` and `article.edited_by` to null through `ON DELETE SET NULL`;
- deletes the user row.

Orders stay readable because each order already stores a buyer snapshot (name, billing email) taken at purchase, the same way it stores a price snapshot. That is the order's own data, not a copy of the profile.
Open holds need no action; they lapse within 10 minutes (D3). The seat service holds no user data (R7), so it is not involved.
After commit, the web tier publishes on `user.<friend>.friends` for each removed friend.

The student chose: the confirmation screen lists upcoming tickets as a warning, and the tickets stay valid after deletion.

## Phase 3: Frontend

### Six places on the site hold client state (proposed)

Counted stateful places:
1. Seat picker on a native event page (a stadium map for named seats, quantities for pools).
2. Live seats-left numbers (pushed, D5).
3. Checkout countdown for the 10-minute hold.
4. Friend-request badge (pushed).
5. New-article notice on news lists (pushed).
6. Article editor in the back office (rich text).

Everything else is pages and forms.

| Approach | Fit |
|---|---|
| Server-rendered HTML with a hypermedia library (htmx) and its server-sent-events extension | Pages and forms need nothing more. Places 2, 4 and 5 become fragments the server pushes. Place 3 is a few lines of script. Places 1 and 6 need a richer widget. |
| Islands (web components) over a JSON API | Fits places 1 and 6. For the rest it adds an API layer the server pages do not need. |
| SPA or SSR metaframework (Next.js, SvelteKit) | Built for many stateful places; OneSport has six. Ties the server language to TypeScript and brings a fast-moving dependency. Its server functions are not a mobile API. |

Assistant's pick: server-rendered HTML with htmx, plus two web-component islands for the seat picker and the article editor. The islands talk to the same server endpoints, not a separate JSON API.
Consequence to decide with it: the website has no JSON API. A mobile app, if it comes, gets a thin API over the same service functions, designed for mobile.

### Search engines and sell-out traffic narrow the frontend field (discussion)

The student asked to discuss alternatives before deciding. Two facts weigh on every option: news pages must be indexable by search engines (a news site lives on search traffic), and a sell-out means many open pages at once.

| Option | What it gives | Painful parts |
|---|---|---|
| htmx plus two web-component islands | Plain HTML is indexable as is. Pushed fragments are rendered once per tick per event and the same bytes go to every subscriber. | Islands must sit outside regions htmx swaps, or they lose state. Out-of-band swaps for badges get fiddly. Back-button caching needs care. |
| Hotwire (Turbo and Stimulus) | Same model as htmx with more structure: Turbo Streams for pushed updates, Stimulus controllers for small client state. | Larger, and its conventions come from Rails. Little difference from htmx for OneSport. |
| Server-held page state (Phoenix LiveView, Livewire, Blazor Server) | Every page is live with no client code. | The server holds state per open page, so a sell-out multiplies server memory. Mixes two interaction models on a site where most pages are static. Ties the server language. |
| Astro with framework islands | Content-site focus, indexable, islands in React or Svelte. | Its server is Node. Either the whole web tier is TypeScript, or Astro becomes a second server calling a JSON API. |
| SPA (React) over a JSON API | One API for web and later mobile; large ecosystem, ready-made seat-map components. | Not indexable without server rendering, so it turns into a metaframework. Two codebases, validation in two places, client state that must reconcile with pushed data. The API is shaped by the website, not by mobile. |
| Next.js | Server rendering and React in one; indexable. | TypeScript on the server, a fast-moving framework, server functions that are not a mobile API. |

### Datastar fits better than htmx because push is already system-wide (D13)

The student proposed Datastar over htmx. The assistant agreed; htmx had been the default hypermedia choice, not a requirements-driven one.

Why it fits:
- It is built around server-sent events. Any response can be a stream that patches elements and signals, so ordinary requests and pushed updates (D5) use one mechanism instead of htmx plus its SSE extension.
- It has client signals built in. The checkout countdown, the pool quantity picker, and probably the named-seat map (server-rendered SVG, selected seats held in a signal, validated by `hold`) need no separate script or island.
- It morphs patched HTML instead of replacing it, so focus and nearby state survive updates.

What it costs:
- A younger project with a smaller community than htmx, and fewer answers to search for.
- Some extras sit in a paid tier; the core is free.

Result: server-rendered HTML with Datastar. One island remains: the article editor, marked so morphing leaves it alone. The named-seat map is a signal-driven SVG, to be confirmed with a prototype; if it fails, it becomes the second island.

### The website has no JSON API (D14)

Pages and Datastar requests go to the same server handlers. A later mobile app gets a thin API over the same service functions, designed for mobile.

## Phase 3 close: the whole design

### Eight components, two of them persistent stores

1. **Web app.** The modular monolith (accounts, social, content, orders, back office). Server-rendered HTML with Datastar, one article-editor island. Handles payment webhooks. Scales horizontally; holds no state between requests except open SSE streams.
2. **Worker.** The same codebase in worker mode. Runs feed adapters on each source's interval and sends ticket emails.
3. **Seat service.** One single-threaded writer per event, an append-only reservation log, batch API. Internal only; called by the web app.
4. **Main database.** Users, social graph, content, saved items, prices, orders, tickets, payments.
5. **NATS core.** Carries `seats.<event>` ticks, `news.<country>`, `user.<id>.friends`. Stores nothing.
6. **Payment provider** (external). Hosted checkout, webhooks with retry, refunds.
7. **Feed sources** (external). News and fixture feeds.
8. **Email provider** (external). Ticket delivery.

### State ownership

| State | Source of truth | Lifetime |
|---|---|---|
| Users, roles, settings | Main database | Until account deletion |
| Friend requests, friendships, lookup counters | Main database | Until resolved, removed, or account deletion |
| Sources, articles, revisions, event details | Main database | Permanent; withdrawn, never deleted |
| Saved articles and events | Main database | Until removed or account deletion |
| Prices, orders with buyer snapshot, tickets, payments | Main database | Legal retention; outlive the user |
| Event layout and reservations | Seat service log | Until the event ends; then archived |
| Seats left | Seat service memory, pushed each second | One second |
| Checkout session | Payment provider | Minutes |
| Bus messages | NATS core | Not stored |

### Four flows carry the design

- **Purchase.** Web app → seat service `hold` (10 min) → pending order → provider checkout → webhook → order paid, `confirm`, tickets created → worker emails tickets. Late payment still confirms if seats are free (R8).
- **Ingestion.** Worker runs an adapter → upsert on (source, external id), skipping editor-locked rows → source policy sets status → publish on `news.<country>` after commit.
- **Live updates.** Seat service ticks each second on NATS; other publishers publish after commit. Web app nodes subscribe and patch open pages over SSE.
- **Account deletion.** One transaction removes social and saved data, nulls order and article links, deletes the user, then notifies former friends.

### Open decisions

| # | Decision | Recommendation | Deciding factor |
|---|---|---|---|
| O1 | Server language | Defer to the builders | Familiarity outweighs the rest; compare on static types, review of model-written code, idle connection cost for SSE, server-rendered HTML ecosystem |
| O2 | Main database product | PostgreSQL | Foreign keys, transactional deletes, mature hosting; no requirement points elsewhere |
| O3 | Payment provider | Any with hosted checkout, retried webhooks, refund API, settable session expiry | Session expiry shorter than the hold keeps late payments rare |
| O4 | Seat log format | One append-only file per event, fsync per batch | Replay is reading one file; no second database engine |
| O5 | Seat service distribution | One node at launch; partition by event id later | No sale is known to need more; one event never spans nodes |
| O6 | Named-seat map | Signal-driven SVG | Prototype decides; fallback is a second island |
| O7 | Ticket email delivery | Worker sends for tickets where `emailed_at` is null | A query condition, no outbox; a failed send is retried next run |
| O8 | Publish availability on commit as well as on tick | Not now | Measure a hot sale first |

The student approved the summary and decided that the server language is left to the implementers (O1 closed as deferred).

## Phase 4: ADR

### Revision 1: one record for the whole system

`ADR.md` follows the skill's template. Changes from the notes made during writing:
- Drivers are numbered D1–D7 in the ADR; decisions from these notes appear as design rules 1–12 and Seat service invariants R1–R7. The late-payment rule (R8 here) is R7 there, because `mark_pending` and its rule were dropped.
- Two assumptions were added: A6 (providers retry webhooks), which the payment flow depends on, and A7 (news pages must be indexable), which rejected the single-page app.
- The Main database is described as one primary with a replica. That was not discussed; it is the default for a single relational database.
- A back-office flow was added after the driver check showed D4 had no section of its own.

The student accepted revision 1 without changes.

## Phase 5: Close

Deliverables in `Submission/with-skill/`: `NOTES.md` (this file) and `ADR.md` (revision 1, accepted).

Open decisions carried in the ADR: O1 server language (left to implementers), O2 PostgreSQL, O3 payment provider criteria, O4 one append-only log file per event, O5 one Seat service node at launch, O6 named-seat map as signal-driven SVG pending a prototype, O7 tick-only availability until measured.

## Assumptions

- A1. Some events sell inside OneSport and others link to an outside vendor.
- A2. News and events arrive from outside feeds and from in-house editors.
- A3. The roles are User, Editor and Admin. Organisers do not log in.
- A4. OneSport does not process card data itself. A payment provider does.
- A5. Popular events sell out in minutes, so many buyers compete for the last seats.
- A6. Payment providers retry a webhook until the receiver accepts it.
- A7. News sites depend on search engine traffic, so news pages must be indexable.

## Decisions

- D1. A separate Seat service with one single-threaded writer per event and its own log.
- D2. Both named seats and pools.
- D3. Hold for 10 minutes, pending order, payment webhook confirms directly; no relay worker.
- D4. A late payment confirms if the seats are still free.
- D5. Push is built once for the whole system; the Seat service ticks once per second.
- D6. NATS core as the bus.
- D7. Content is a module of the monolith, fed by adapters in the worker mode.
- D8. An editor's edit locks the item against feed updates.
- D9. Saved items reference content and read its current state.
- D10. Friend requests plus one canonical friendship row per pair.
- D11. Email lookup: exact match, daily limit, opt-out, minimal details.
- D12. Account deletion is one transaction; upcoming tickets stay valid after a warning.
- D13. Server-rendered HTML with Datastar; the article editor is the one island.
- D14. The website has no JSON API.
- D15. The server language is left to the implementers.
