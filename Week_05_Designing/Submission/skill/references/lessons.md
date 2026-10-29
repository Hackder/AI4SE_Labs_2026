# Lessons from the OneSport session

Each lesson is a mistake the assistant made, the correction, and the rule that
came out of it. Source: `AI4SE_Labs_2026/Week_05_Designing/Submission/NOTES.md`
and the transcript next to it.

## Scope and requirements

- **Inferred scope out from absent stories.** The assistant read purchase as out
  of scope because no story buys anything, and read content as coming from an
  external aggregator. The description promised a ticket platform, and the user
  wanted everything in house. Rule: when the description and the stories
  disagree, ask. Never shrink scope silently.
- **Missed an implied role.** In-house content implies an editorial role even
  though no story mentions it. Rule: list the roles the stories imply.
- **Treated a hybrid as two systems.** Ingested and editor-written news could
  have become two parallel models. Rule: one model with a source dimension, and
  per-source policy as a configuration field.
- **Feature combinatorics.** Variations (needs approval, native or redirect
  sale) must not multiply code. Rule: each variation is a field read in exactly
  one place; adapters are the only code that grows, and they grow linearly.
- **A data type with a different write pattern is a different type.** Player
  statistics are upserts with a "latest" view; articles are append-only. The
  user dropped stats to keep the pipeline simple. Rule: when a proposed content
  type needs a different write pattern, say so and let the user decide.

## Purchasing and contention

- **Offered horizontal scaling and a queue for one hot row.** Neither helps.
  A queue defers the spike, re-clicks multiply events, and thousands of waiting
  connections need tracking. Rule: one single-threaded writer per contended
  unit, synchronous, answering in milliseconds. Distribute across units
  (events), never within one.
- **Called the single writer a single point of failure.** The user called this
  unfounded: if the main store is down the service is down in any design. The
  difference is recovery time, not kind. Rule: compare failure modes by what is
  lost and how long recovery takes, not by whether a failure exists.
- **Described the hot service as a counter.** It needs categories, named seats
  or pools, a reservation log with history, uniqueness constraints, and a
  money-free API. Rule: write the data model and invariants of the hard part
  before calling it designed.
- **Proposed a periodic expiry sweep.** It would spike p99. Rule: expiry is a
  query condition on status and creation time. Nothing writes on a timer.
- **Design the API batch-shaped from the start.** A single click is a batch of
  one, so batching is a tuning knob, not a second code path.
- **Payment policy is not architecture.** Grace periods and refunds are
  business rules. The architecture supplies the `payment_pending` state and
  idempotent confirm and cancel, plus an outbox for webhooks.
- **The contended service must not terminate TLS or face the internet.** A
  horizontally scaled web tier with its own database calls it.

## Data flow and state

- **Mentioned several caching layers.** The user rejected them for invalidation
  and staleness problems. Rule: no cache that needs invalidation. A snapshot
  with a stated staleness bound that the write path corrects is fine.
- **Gave one value two sources.** Availability pulled on demand and also pushed
  over the bus would disagree and jump on the page. Rule: every number on a page
  has one source. If pushed, never pulled.
- **Let the bus become a store.** With a retained last value, cold-start
  snapshots, and republish-on-reboot, the bus had become a third persistent
  store. The fix was a once-per-second full-state tick from the owner: it is a
  read with no fsync, it doubles as a heartbeat, and it removed the expiry
  timer, the snapshot, the republish, and the retained value. Rule: write the
  state ownership table and count the persistent stores. Prefer a periodic
  full-state publish over incremental messages plus reconciliation.
- **Measure before optimising.** Publishing on commit as well as on tick was
  deferred until a hot sale shows the need.

## Frontend and push

- **Defaulted to SSR with hydration and a JSON API.** The user asked what about
  a purchase button needs a SPA, and rejected a separate SSR service and a
  TypeScript metaframework (locks the language, fast-moving dependency, server
  functions are not a mobile API). Rule: count the stateful places on the site
  and compare server-rendered HTML with a hypermedia library, islands, and a
  metaframework against that count.
- **Made push a per-page feature.** The user wanted pub-sub first class because
  several future features need it and it removes polling. Rule: push is a
  property of the system, built once; features add subjects.
- **"No JSON API" is a decision, not a consequence.** The website has none. A
  mobile API is a later thin layer over the same service functions, designed for
  mobile's needs rather than inherited.
- **Walk back absolutes where one component needs more.** The article editor
  needs an island (a web component) even though the rest of the site does not.
- **LiveView.** A page-level framework whose strength is all-live pages does
  not fit a site with few live pages. The objection is not memory; it is mixing
  two interaction models.

## Infrastructure choices

- **Postgres as the bus.** Works at launch volume and publishes transactionally,
  but every publisher needs a connection to the primary, notifications contend at
  commit, and payloads are small. The deciding reason was that the isolated
  reservation service would need a main-database connection. Rule: name the one
  deciding reason, and accept the cost (losing transactional publish) with a
  rule that covers it (publish only after commit).

## Language and technology

- **Rushed the language.** Missing criteria were static type safety, AI
  friendliness, and one language everywhere. Rule: compare on static
  guarantees, compiler feedback and reviewability for model-written code, idle
  connection cost, and ecosystem for server-rendered HTML. Then defer if the
  builders are unknown, because familiarity weighs most. Check whether the
  assignment requires a concrete pick before pushing for one.

## The ADR

- One record for the whole system when decisions interlock. Rejected
  alternatives inline, with the deciding reason.
- Markdown with Mermaid was accepted even though other reports used Typst,
  because the ADR is an artifact of the conversation.
- The writing pass should restate jargon literally ("sparse software" became
  "do not build code that has one caller").
- Assumptions and decisions were mixed twice. "Pushed live updates are a
  property of the system" was an assumption that was really a design rule. The
  mobile assumption mixed "a mobile app is plausible" (assumption) with "the
  website has no JSON API" (rule). Rule: audit both lists before showing the ADR.
- Do not edit the user's skills, even to improve them. Suggest in chat.
