### Why don’t we parse inside the API request?

> **Because parsing is slow and unreliable, and HTTP requests should be fast and predictable.**
> Background tasks allow us to return immediately while work continues safely in the background.

That highlights **reliability** and **timeouts**, which matter a lot in SaaS.

---

### What role does the database play between request & background work?

> **The database is the shared state and source of truth between the request lifecycle and the background task lifecycle.**

The DB isn’t just storage - it’s the **handoff mechanism**.

---

## The mental model

Here’s the clean mental picture you should keep:

```
POST /documents
│
├─ Save document (status = pending)
│
├─ Schedule background task
│
└─ Return response immediately
```

Later (separately):

```
Background task starts
│
├─ Load document from DB
├─ Update status → processing
├─ Parse text
├─ Create reaction
└─ Update status → parsed
```

**No direct connection.**
**No shared memory.**
**Only the database connects them.**

That’s *exactly* how distributed systems work.

---