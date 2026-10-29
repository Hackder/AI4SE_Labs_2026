# ADR template

One record for the whole system. Replace every bracket. Delete a section only
if it is genuinely empty and say so in one line.

```markdown
# ADR-[number]: [System] architecture

| | |
|---|---|
| Status | Proposed / Accepted / Superseded |
| Date | [YYYY-MM-DD] |
| Scope | [what the record covers] |
| Supersedes | none / ADR-[n] |

## 1. Context

[Two paragraphs: what the system is, what the requirements look like, and how
many of them matter architecturally. Name the commodity stories once.]

| # | Driver | Source | Why it matters |
|---|---|---|---|
| D1 | [requirement that shapes the design] | [story numbers, or "inferred from ..."] | [consequence for the architecture] |

The design rests on these assumptions:

- [fact about the world or product that the design takes as given]

The discussion settled on these design rules:

1. [a choice the design makes, stated as a rule the implementation must keep]

## 2. Architectures considered

| | [Subsystem 1] | [Subsystem 2] | [Subsystem 3] | Verdict |
|---|---|---|---|---|
| A. [name]. [one sentence] | | | | Chosen / Rejected, [why in one clause] |
| B. ... | | | | |

[One paragraph on the subsystem that decided the choice and why.]

## 3. Decision

[One paragraph: the chosen shape in three sentences.]

### 3.1 Components

[Mermaid flowchart of components and the edges between them, labelled with
what crosses each edge.]

| Component | Instances | Owns | Does |
|---|---|---|---|

### 3.2 State ownership

| State | Source of truth | Lifetime |
|---|---|---|

[One paragraph on what can be lost in a failure and what cannot.]

### 3.3 [The hard part's model]

[Data model, invariants as constraints, API as a table of calls and effects.]

### 3.4 [The rule that needed the most discussion, as a numbered mechanism]

### 3.5 Flows

[One bold heading per flow. A Mermaid sequence diagram for the critical one.]

### 3.6 [Frontend / client model]

[The choice, and the rejected alternatives with one reason each.]

### 3.7 [Any infrastructure choice that had a plausible simpler alternative]

## 4. Consequences

### What the design gains
### What the design accepts
### Failure modes

| Failure | Effect | Loss |
|---|---|---|

## 5. Open decisions

| # | Decision | Options | Recommendation | Deciding factor |
|---|---|---|---|---|

## 6. Glossary

- [Component or term]: [one line]
```

## Checks before showing the ADR

- Every component in a diagram appears in the component table and the glossary
  under the same name.
- Every driver in section 1 is addressed somewhere in section 3.
- No assumption is a decision in disguise, and no rule is a fact.
- Each rejected alternative has one deciding reason, not a list.
- Open decisions have a recommendation and the factor that would settle them.
