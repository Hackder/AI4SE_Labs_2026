# Week 5 discussion notes: OneSport architecture

These notes condense the session in which the student and the assistant designed an architecture for OneSport (task 1) and then produced and revised an ADR (task 2). The full transcript is in `transcript/` and the final record is `ADR.md`. The student set the working rules: one topic at a time, no move to task 2 until asked, and focus on the stories that shape the architecture.

## Task 1: Architecture discussion

### Most stories are noise, and purchase is in scope

The assistant set aside the UI placement and list-view stories (3, 4, 20, 21, 22), treated auth as commodity except the account deletion cascade (story 5), and named three drivers: news and tickets coming from outside OneSport, collections referencing items OneSport does not own, and a small social graph whose lookup by email risks account enumeration. It proposed reading purchase as out of scope, since no story buys anything.

The student disagreed on both points. The system description promises a platform for purchasing tickets, so purchase is in scope. The student also rejected the reading that content comes from an external aggregator: the product should have everything within it, a sports news site where users can also buy tickets. The assistant accepted both, conceded it had inferred too much from the absence of admin stories, and noted that in-house content implies an editorial role. Purchase now meant inventory, orders, last-seat concurrency, and payment.

### Content is a hybrid, and variation lives in data

The student wanted payment included, with the provider choice as part of the design, and refined the content model: editors can write news, but no product like this can rely on that alone, and not every organiser will sell through OneSport. Some events redirect to an external vendor, and much news is pulled automatically from official sources and other sites, with editors able to add and edit.

The assistant argued for one news model and one event model, each with a source dimension, so the hybrid does not become two parallel systems.

The student warned against a combinatorial explosion of features per variation and against sparse software where most code never runs. The assistant answered that the variation goes into data. Every ingested item takes one pipeline, and a field on the source configuration decides whether it lands published or pending review. Each source gets one concrete adapter, so code grows linearly with sources. Native versus redirect is a fulfilment mode field that only checkout reads.

When the assistant asked whether the student's FIFA player stats example meant a third content type, the student dropped stats for now because they need a "latest version" view that complicates the pipeline. The assistant agreed that stats are an upsert pattern, unlike append-only articles and events, and locked seven drivers, now including the editorial role and two fulfilment modes for tickets.

### Four architectures, and D is ruled out

At the student's request the assistant presented four high-level architectures across news, purchasing, and social:

- A, a modular monolith with one database and a separate worker process.
- B, domain services (content, commerce, social with identity) with their own databases and a message broker.
- C, an event log with read models.
- D, a composition of managed services: hosted auth, headless CMS, provider checkout, cloud functions.

The assistant leaned towards A. The student ruled out D as a nightmare and asked to compare the rest on purchasing first, framing it as a textbook high-contention OLTP problem: reserve a ticket, allow about ten minutes to pay, with thousands of buyers on one event at once.

### A queue defers the problem, so a single-writer SQLite service owns seats

The assistant agreed that horizontal scaling does nothing for one hot row. It described A as a row lock risking a convoy that exhausts the shared connection pool, B as the same hot row with a contained blast radius, and C as the natural fit, one consumer per event behind a log, at the cost of an asynchronous click.

The student rejected the queue. A queue only defers the problem: impatient users refresh and click again, each click adds another event, and the system must track thousands of waiting connections polling or listening for their result. The student agreed that one event cannot be distributed, only events across servers, and proposed keeping the reservation system simple: a small API service with SQLite on a local drive, with no network calls and full ACID.

The assistant called this better than its option C, added idempotency (one hold per user per event) against re-clicks, and raised two concerns: the machine is a single point of failure, and it should not terminate TLS.

The student called the first concern unfounded: in any design, if the main store goes down the service goes down, whether SQLite, Redis, or a queue. The assistant accepted that the difference is recovery time, not kind, and dropped it. On the second, the student proposed a horizontally scaled primary web service with its own database that calls the reservation service, with each replica batching requests, so the web layer scales while the contended part stays single-threaded. For payment the student would use Stripe or similar behind an interface, said the grace and refund rules are business policy rather than architecture, and suggested webhooks arrive at the web tier and are forwarded.

The assistant agreed. It suggested a batch-shaped API from the start, so a single click is a batch of one and batching is a tuning knob, not a second code path. For webhooks it added idempotency and an outbox in the main database with retries. Purchasing now looked the same under all three architectures.

### News and social stay in one application with one database

The assistant argued that news is the opposite workload: few scheduled writes, many identical public reads. B would make collections and the event listing cross a network boundary for isolation nobody needs, and C's read models would be the table A already has. Social and collections gain nothing from either. It concluded: A with purchasing carved out.

The student said the proposal was unclear, raised future live match stats, and objected that the assistant had mentioned several layers of caching, which brings invalidation and staleness problems. The assistant restated the design as five components, dropped the CDN, and kept only a one-second-stale availability snapshot that the reserve call corrects. For live stats it offered polling or a publish-subscribe channel.

### The reservation service is more than a counter

The student asked the assistant to name "the box" and the main web service, and called the reservation service too bare: it needs specific seats, ticket categories, a reservation log, and a guarantee that no seat sells twice. It should return a valid reservation and leave payment entirely to the main service, which confirms or cancels. The student also objected that a second data path per live feature adds complexity, asked whether the stories call for chat, and asked for a list of what the main web service handles.

The assistant named the two components Core Service and Reservation Service. It gave the Reservation Service ticket categories (pools or named seats), a reservation log with history, a uniqueness constraint on seats, and a money-free API. It retracted the subscription channel, said the stories contain no chat, listed the Core Service's responsibilities, and asked whether friends could see each other's saved events.

The student rejected the periodic expiry sweep the assistant had described, because it would spike p99 latency. Pending reservations are simply those with a given status and a creation time inside the expiry window. The student declined to assume anything about friends beyond the stories, mentioning a GitHub-style feed as a possible future, and said polling should not be a blind choice. The student asked to move to the frontend and client-server model.

### The frontend is server-rendered and push-first, not an SSR metaframework

The assistant recommended SSR with hydration, a frontend server next to the Core Service, a JSON API, and server-sent events fed by each replica's availability pull.

The student said the options had not been considered properly. A purchase button or article approval does not need a SPA, and a separate SSR service is unwanted complexity. An SSR metaframework would absorb the backend, forcing TypeScript, a large fast-moving dependency, and slower rendering, and its server functions are not an API a future mobile app, with its own needs, could use. The student asked for a real comparison between a metaframework and server-rendered HTML with JavaScript interactivity. On pub-sub, the student argued it should be first class, because several future features need push and it removes polling.

The assistant admitted it had defaulted. It compared a TypeScript metaframework, hypermedia-style server HTML, and server HTML with islands backed by a JSON API, found only three stateful places (seat picker, article editor, live availability), and recommended islands. It accepted first-class pub-sub and recommended a dedicated bus such as NATS.

The student accepted NATS and suggested htmx or datastar, removing the need for a JSON API for the website. The assistant agreed that the islands dissolve, with a later mobile API as a thin layer over the same service functions. It recommended datastar because its model is server-sent events, matching the bus, named its youth as the risk, and noted that thousands of open streams favour a runtime with cheap idle connections, such as Go.

The student walked back "no islands" for the article editor, which needs good behaviour and so a web component or similar island, though without collaborative editing and so without an API. The student added that live stats should store every event so a match timeline can be shown, while displaying the latest. The assistant agreed and consolidated the full architecture.

### A dedicated bus beats Postgres notifications for this design

The student asked whether Postgres could serve as the bus and what NATS adds. The assistant said Postgres would work at launch volume and offers transactional publish, but only processes connected to the primary can publish, payloads are small, and notifications contend at commit. The deciding point was that the Reservation Service, the main producer of availability changes, would need a main database connection, undoing its isolation.

### Availability must have one path, so the Reservation Service ticks once per second

The student identified a flaw: if the web service sometimes pulls the seat count on demand and also receives it over NATS, the two sources can disagree and the number on the page jumps up and down. Fixing that would need synchronisation code that exists only because the data was split.

The assistant agreed and proposed that the Core Service only listens: full-state messages per event, an in-memory map per replica, NATS retaining the last value for cold starts, and a timer on the earliest expiry.

The student then raised two points. First, state ownership: there were now three persistent stores (main database for purchases, NATS for derived seat counts, SQLite for reservation state). Tickets are sold only within a sale window, and availability should be consulted only inside it. One SQLite file per event, archivable to S3, could come later. A rebooting Reservation Service would simply emit its current state. Second, the student proposed that the Reservation Service emit the full available count once per second. It only reads, using expiry time as the truth, so there is no write, no fsync, and little p99 effect, and the design should measure before optimising.

The assistant agreed that the tick removes the expiry timer, the cold-start snapshot, the reboot republish, and the retained value, and doubles as a heartbeat. The bus became transient again, leaving two persistent stores. Outside the sale window pages render from the main database alone. One file per event was deferred, and the assistant wrote a full summary at the student's request.

### LiveView was considered and set aside

On technologies, the assistant recommended Go and named Elixir with Phoenix as an alternative for the web half. The student doubted it: LiveView keeps client state on the server, which might cost memory, OneSport has few live parts, and the student had never written LiveView. The assistant said memory is not the real issue: LiveView is a page-level choice, so the site would mix two interaction models while barely using LiveView's strength.

### The language choice is deferred because it depends on who builds it

The student kept datastar but said the language decision was being rushed. One language everywhere is a real benefit, and two criteria were missing: static type safety and AI friendliness. The student noted Go is weaker on types than Rust, and that a Go stack should use templ or similar instead of only the standard library. The assistant compared Go, Rust, TypeScript, and Kotlin on static guarantees and on compiler feedback, loop speed, and reviewability for model-written code. It still recommended Go with templ, generated typed SQL, and strict linters, since the critical invariants live in SQLite constraints and the small Reservation Service could be rewritten in Rust later.

The student asked whether the assignment requires a concrete pick. The assistant said it does not. The student agreed to defer, because the language choice depends heavily on who builds the system and their familiarity. The assistant listed the open decisions and closed task 1.

## Task 2: The ADR

### The first draft is a single record for the whole system

The assistant wrote `Submission/ADR.md` as one record covering drivers, architectures considered, the decision, consequences, open decisions, and a glossary, with Mermaid diagrams. It chose one record over one file per decision because the decisions interlock, and kept rejected alternatives inline. The student found it good and accepted Markdown, since the ADR is an artifact of the conversation, unlike the student's other reports written in Typst.

### A technical-writing pass tightens the language

At the student's request the assistant applied the technical-writing skill and its companion unslop skill by hand: active voice, whole sentences, literal phrasing, one name per component, "sparse software" restated as "do not build code that has one caller", and headings that state the point. It also proposed adding "carve-out" to a rule in the unslop skill without editing it. The student replied that the assistant must not edit their skills.

### Two decisions move out of the assumptions list

The student pointed out that "pushed live updates are a property of the system, not a feature of one page" was listed as an assumption but was a decision. The assistant moved it to design rule 7. It then flagged that the mobile assumption mixed an assumption with a decision. The student asked to split it: the mobile app stays an assumption, and "the website has no JSON API" became design rule 8. The student then accepted the ADR as pretty good, and the assistant closed task 2.

## Open decisions in the final ADR

1. Backend language: Go with templ, generated typed SQL, and strict linters is recommended over Rust everywhere or TypeScript on a plain server. The builders' familiarity decides.
2. Payment provider: Stripe or an equivalent behind an interface, chosen when building based on markets and volumes.
3. Publishing availability on commit: the tick is the only trigger until measured hot-sale latency justifies adding it.
4. One SQLite file per event: deferred until a second shard machine or long-term archiving is needed.
5. Future features: statistics, a friend feed, chat, and collaborative editing are out of scope, and the architecture has a place for each.
