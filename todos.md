# Wayfarer — TODO

Improvement roadmap for the multi-agent pipeline (`main.py`) and supporting modules.
Do not touch `app.py` UI/CSS while working through these — backend only.

Work top to bottom. Each phase should leave the pipeline runnable end-to-end before moving to the next.

---

## Phase 1 — Fix silent failure in `planner_agent`

- [ ] Replace raw `json.loads` + try/except-default-to-"unknown" with Pydantic schema validation for planner output
- [ ] On parse/validation failure, retry the LLM call once with an explicit "return valid JSON matching this schema" correction prompt
- [ ] If retry also fails, surface a clear error to the user instead of silently proceeding with `"unknown"` fields
- [ ] Confirm `flight_agent`/`hotel_agent` no longer silently skip search due to swallowed parse errors

## Phase 2 — Add clarification interrupt

- [ ] Use LangGraph interrupt / human-in-the-loop pattern (Postgres checkpointing already supports this)
- [ ] If `planner_agent` can't extract destination or dates, interrupt the graph and prompt the user for the missing field
- [ ] Resume cleanly from checkpoint once user responds
- [ ] Remove the old silent default-to-"unknown" fallback path once this is in place

## Phase 3 — RAG layer: Destination Guide Agent

- [ ] Set up Pinecone index for destination guide content (visa requirements, safety info, local tips)
- [ ] Seed starter dataset for 10-15 popular destinations, chunked appropriately
- [ ] Build new agent node that retrieves via hybrid search (metadata filter by destination + vector similarity)
- [ ] Run this agent in parallel with `flight_agent`/`hotel_agent`
- [ ] Feed retrieved guide content into `itinerary_agent`; itinerary should cite it in the final output

## Phase 4 — Structured `hotel_tool.py`

- [ ] Build `hotel_tool.py` mirroring `flight_tool.py`'s structured output pattern
- [ ] Return structured hotel objects: name, price, rating, location, booking link
- [ ] Replace raw Tavily search text currently passed into the itinerary prompt

## Phase 5 — Budget-aware planning

- [ ] Add `budget` field to `TravelState`
- [ ] Parse budget out of queries in `planner_agent` (e.g. "under ₹2 lakhs")
- [ ] Have `flight_agent`/`hotel_agent` filter/rank results against budget
- [ ] Have `itinerary_agent` explicitly reference budget tradeoffs in final output

## Phase 6 — Observability

- [ ] Extend existing `llm_calls` counter into per-node tracing: latency + estimated token cost per agent
- [ ] Log traces to Postgres
- [ ] Surface a summary (total cost, total time, calls per agent) in the final output returned to the frontend

## Phase 7 — Eval harness

- [ ] Create `tests/eval_harness.py`
- [ ] 20-25 golden test queries covering:
  - [ ] Router intent classification accuracy
  - [ ] Planner field-extraction accuracy (correct IATA codes/dates)
  - [ ] Itinerary faithfulness (LLM-as-judge check against retrieved flight/hotel/guide data)
- [ ] Output pass/fail report with per-category scores, runnable via a single command

---

## Nice-to-have (after Phases 1-7)

- [ ] Multi-city trip support (currently single dep/arr IATA pair only)
- [ ] Router/supervisor override — "just flights, skip hotels" conditional routing
- [ ] Booking/save/compare flow for multiple itinerary variants

---

## Priority if time-constrained

If applying to jobs soon, do **Phase 1, 2, and 6 first** — smallest changes, highest "found and fixed a real reliability bug" interview value. Phase 3 (RAG) is the biggest lift but closes the specific gap of Wayfarer having no retrieval component.

# BREAKDOWN OF PHASES

`````
I'm working on Wayfarer, a multi-agent travel planning system at
github.com/lalitdotdev/wayfarer-multiagent. It uses LangGraph with
Postgres checkpointing, orchestrating: Router → Planner → (Flight ∥ Hotel,
parallel) → Itinerary → Final, built on Groq/LLaMA 3.3 70B, Tavily Search,
and AviationStack. Frontend is a custom-styled Streamlit app (app.py) —
do not touch app.py's UI/CSS, only backend logic in main.py and new files.

Work through these phases in order. After each phase, run the existing
tests, confirm the pipeline still runs end-to-end on a sample query, and
summarize what changed before moving to the next phase.

PHASE 1 — Fix the silent failure in planner_agent
Currently, if the LLM's JSON response fails to parse in planner_agent,
fields silently default to "unknown," and flight_agent/hotel_agent then
skip search entirely with no user-visible error. Fix this:
- Replace raw json.loads + try/except-default with Pydantic schema
  validation for the planner's structured output.
- On parse/validation failure, retry the LLM call once with an explicit
  "return valid JSON matching this schema" correction prompt before
  falling back.
- If it still fails after retry, surface a clear error to the user
  instead of silently proceeding with "unknown" fields.

PHASE 2 — Add a clarification interrupt
The graph already has Postgres checkpointing, so use LangGraph's
interrupt/human-in-the-loop pattern: if planner_agent can't extract a
required field (destination, dates), interrupt the graph and ask the
user for the missing info instead of defaulting to "unknown" and
silently skipping downstream agents. Resume cleanly from the checkpoint
once the user responds.

PHASE 3 — Add a RAG layer: Destination Guide Agent
Add a new agent node that retrieves from a Pinecone vector index of
destination guide content (visa requirements, safety info, local tips —
you can seed this with a small starter dataset for 10-15 popular
destinations, chunked appropriately). This agent runs in parallel with
flight_agent/hotel_agent and its output feeds into itinerary_agent,
which should cite the retrieved guide content in the final itinerary.
Use hybrid search (metadata filter by destination + vector similarity)
rather than naive top-k.

PHASE 4 — Structured hotel_tool.py
Currently hotel data flows into the itinerary prompt as raw Tavily
search text while flight data goes through flight_tool.py with
structured output. Build hotel_tool.py mirroring flight_tool.py's
pattern — structured hotel objects (name, price, rating, location,
booking link) instead of raw search text.

PHASE 5 — Budget field
Add a budget field to TravelState. Parse it out in planner_agent from
queries like "under ₹2 lakhs." Have flight_agent and hotel_agent filter/
rank results against it, and have itinerary_agent explicitly reference
budget tradeoffs in the final output.

PHASE 6 — Observability
Extend the existing llm_calls counter into real per-node tracing:
latency and estimated token cost per agent node, logged to Postgres.
Surface a summary (total cost, total time, calls per agent) in the
final output returned to the frontend.

PHASE 7 — Eval harness
Create a standalone eval script (tests/eval_harness.py) with 20-25
golden test queries covering: router intent classification accuracy,
planner field-extraction accuracy (correct IATA codes/dates), and
itinerary faithfulness (does the final itinerary actually reflect the
retrieved flight/hotel/guide data, checked via a separate LLM-as-judge
call). Output a simple pass/fail report with per-category scores,
runnable via a single command.

For each phase, tell me which files you're changing before you change
them. Keep phases 1-2 minimal and surgical — don't refactor working code
beyond what's needed to fix the described issue.````
`````
