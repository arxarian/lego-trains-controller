# Route Planning — GitHub Task Prompts

Copy each **Prompt** block into a GitHub issue (or paste it to the coding agent).  
Implement issues in order within each slice; do not start a slice before its dependencies are done.

**Related project rules:** `.cursor/rules/project-spec.mdc`, `.cursor/rules/coding-spec.mdc`

**Master plan issue (order, priorities, architecture):** see GitHub milestone [Route Planning MVP](https://github.com/arxarian/lego-trains-controller/milestone/1) — issue titled `[EPIC] Route Planning MVP — master plan`.

---

## Recommended implementation order

**Complexity:** **S** small (~≤½ day) · **M** medium (1–2 days) · **L** large · **XL** multi-day integration.  
**Canonical table + easy-starters list:** GitHub [#155](https://github.com/arxarian/lego-trains-controller/issues/155).

### Easy starters (few/no prereqs)
| ID | Issue | Cx | Prereq |
|---|---|---|---|
| F0 | #114 unique marker colors | S | — |
| A1.1 | #130 logical switch position | S–M | — |
| A2.1 | #132 shortest-path leg | S–M | — |
| A2.3 | #134 multi-waypoint list | S | A2.1 |
| B1.1 | #137 order list model | S–M | — |
| C2.1 | #142 click switch toggle | S–M | A1.1 |
| E4 | #148 deadlock design note | S | — |

### Phase 0 — Foundations
1. **F0** #114 (**S**, —)  
2. **F1** #154 (**M**, —)  
3. **F2** #68 marker clustering (**M–L**, needs F0) — P2 / after first Auto demo (capacity upgrade; not critical path)

### Phase 1 — Backend critical path
3. A1.1 (**S–M**) → A1.2 (**M**, needs A1.1)  
4. A2.1 (**S–M**) → A2.2 (**S–M**, A2.1+A1.1) → A3.1 (**M**) → A3.2 (**M**, A3.1+A2.1)  
5. A2.3 (**S**, A2.1) anytime after A2.1

### Phase 2 — One Auto train (sim)
6. S1 (**M–L**, A1) → B1.1 (**S–M**) → B1.2 (**L**, A2+A3+B1.1) → S2 (**L**, S1+B1.2)  
7. B2 (**M**, B1.2) later

### Phase 3 — Switches + plan UI
8. SW1 (**L**, A1.1) → C2.1 (**S–M**, A1.1) → C2.2 (**M–L**)  
9. C1.1 (**M**, B1.1) → C1.2 (**M**, C1.1)  
10. SW2 (**L**, SW1) when hardware ready

### Phase 4 — Multi-train + polish
11. S3 (**L–XL**) → E3 (**M**) → E1/E2 (**M**); E4 (**S**) design only  
12. **F2** #68 (**M–L**, F0) when layouts outgrow ~5 unique single-color markers

### Architecture constraints (do not violate)
- **Auto owns motion** when Automatic; sim only emits colors along the reserved leg; Manual = today’s slider, pause executor later (B2).  
- **One interlocking API** (segment ownership + atomic leg reserve); migrate off dual reserve paths.  
- **`generate()` invalidates run state** (clear locks, pause executors) — implement with E3, design for it from A3.  
- **Pathfind on full graph**, then set/lock required switches — do not Dijkstra on “currently set branches only”.  
- **Device layering:** shared BLE transport base; train hub vs switch actuator as separate roles; Fake* for sim.  
- **Stable owner/binding ids** when implementing A3/SW1.  
- Bindings and planning target live in **Python**, not only QML.

---

## Shared product decisions (include in every issue or link this doc)

These decisions are final for MVP:

| Topic | Decision |
|---|---|
| Plan model | Transport Tycoon / OpenTTD style: per-train **looping order list** |
| Order | Target marker (graph node) + optional **wait N seconds** at that marker |
| Conflict policy | **Hold** (train stops / stays at last safe marker until leg can be reserved) |
| Reservation | **Reserve entire leg** (all segments to next waypoint) atomically before departure |
| Deadlock (v1) | Full-leg reservation only; no passing-loop logic, no deadlock detector |
| Marker selection UI | **Click marker on canvas** (Run mode) |
| Train modes | Per-train **Manual** \| **Automatic**; mixed fleet allowed |
| Switch modes | Per-switch **Manual** \| **Automatic** (logical first) |
| Physical switches | Later; same style BLE hub as trains — not in early slices |
| Auto speed | Reuse last non-zero speed; fallback constant (e.g. 40) |
| Manual during plan | **Pause** executor; keep orders; release current leg reservation |
| Persist orders | Session-only in MVP |
| First verification | Simulator first, then real hub |
| Localization | Markers are the only position source; react only at markers |

### Important current code facts

- Graph: `Controller/src/python/network_generator.py` → NetworkX undirected graph; marker nodes `"rail_id + path_id + distance"`; segments `"sorted_a:sorted_b"`.
- Network API: `Controller/src/python/network_manager.py` — `reserve` / `unreserve` apply to **one segment**; `find_segment_by_entry_node` still picks first neighbor when branching (TODO).
- Train: `Controller/src/python/items/train.py` — on color → find node → reserve **current** segment only.
- Planner stub: `Controller/src/python/planner.py` — debug `plan(paths)` toggles `path_id_active` on path indicators.
- Switch rails: `RailType.SwitchLeft` / `SwitchRight`; paths `"A"` (straight) and `"B"` (curved) in JSON under `Controller/src/resources/`.
- Path highlight: `PathIndicators.path_id_active` + `MultiPathView.qml`.
- Wiring: `Controller/src/python/app_context.py` exposes `planner`, `network`, `trains`, `simulator` to QML.
- Run UI: `RunPanel.qml` + `TrainControlPanel.qml`; canvas in `TrackCanvas.qml`; markers in `MarkerItem.qml`.
- Simulator: `Controller/src/python/simulator.py` + `FakeDevice` — walks a color circuit; good for testing Auto later.
- Conventions: domain objects are `QObject` with `Property`/`Signal`/`Slot`; models use `ObjectBasedModel[T]`; update `Controller/TrainsController.pyproject` when adding files.
- Do not rewrite entire files for small changes; match existing style; add pytest coverage for backend logic.

---

# Slice F — Foundations (do early / before the epic bites)

## Issue F0 — Marker sanity / unique colors (#114)

Existing GitHub issue: https://github.com/arxarian/lego-trains-controller/issues/114  
(`implement sanity check for markers`)

**Prompt (expanded for planning epic):**

```
Implement marker sanity checks so localization and route planning are not corrupted by duplicate or adjacent identical colors.

## Why before / early in the epic
Trains resolve position via color_map (hex → one node). Duplicate colors last-write-wins today and break Auto plans and simulation. This is issue #114, pulled into Route Planning MVP foundations.

## Depends on
None. Can ship before A1.

## Requirements
1. On network generate() and/or when markers change in Edit mode:
   - Detect duplicate marker colors among taken/visible colored markers used as graph nodes
   - Detect identical colors on immediately adjacent marker positions (as #114 suggested)
2. Surface result clearly: warning list in UI and/or block Run/generate with a visible message (prefer warn in Edit, fail or hard-warn before Run/Auto)
3. color_map construction should not silently overwrite without logging which nodes collided
4. Tests for duplicate detection
5. Follow project-spec.mdc / coding-spec.mdc

## Acceptance
- Two markers with the same color → user-visible warning (and documented Run behavior)
- Adjacent identical markers → warning
- Unique layout → no warnings; color_map size matches colored marker count

## Out of scope
Auto-fixing colors, planner executor, switch actuators, marker clustering (see F2 / #68)
```

## Issue F2 — Marker color clustering (#68)

Existing GitHub issue: https://github.com/arxarian/lego-trains-controller/issues/68  
(`implement markers clustering`)

**Complexity:** **M–L** · **Prerequisites:** F0 (#114) · **Priority:** P2 (after first Auto demo; not on critical path)

**Prompt:**

```
Expand localization capacity beyond 5 single colors by treating two adjacent different-colored bricks as one compound beacon (e.g. blue+red → signatures blue→red / red→blue).

## Why later (not instead of F0)
F0 keeps single-color layouts reliable. Clustering is a capacity upgrade for large layouts. Hub still emits one discrete color at a time; the host reconstructs pairs.

## Depends on
F0 (#114) — uniqueness / warnings must exist so signature collisions are detectable.

## Design (agreed)
1. Host-side sequence matching (no hub firmware change in v1). Adjacent bricks produce a sequence of clr events (possibly with BLACK/NONE between).
2. Geometry clusters at generate/edit: consecutive taken markers on the same path with abs(d1-d2)==1 and different colors → one virtual marker node (midpoint or first distance); remove the two singles from the localization map.
3. Signatures: ordered pairs; both blue→red and red→blue resolve to the same node (bidirectional travel).
4. Replace or extend color_map with signature_map:
   - Single marker: key = color hex (as today)
   - Cluster: keys "#0000ff|#ff0000" and "#ff0000|#0000ff" → same node
5. Train localization: buffer last accepted color; on new color try pair signature first, else single. Clear buffer after match, timeout, or non-adjacent second color.
6. Uniqueness (generalized F0): colors used in any cluster cannot also be used as singles; warn on duplicate unordered cluster pairs.
7. Simulator: emit both colors in order when crossing a cluster node.
8. UI dual-color chip in editor is optional follow-up.

## Requirements
1. Detect geometry clusters on generate
2. signature_map + sequence matcher in Train (or NetworkManager helper)
3. F0-style warnings for signature / single-vs-cluster collisions
4. Tests: cluster detection, signature map, sequence matcher, simulator pair emission
5. Follow project-spec.mdc / coding-spec.mdc

## Acceptance
- Blue+red adjacent → one beacon; red/blue reusable only under the uniqueness rules above
- Train crossing a cluster localizes once to the cluster node
- Signature collisions produce warnings
- Pair-only clusters (no 3+ brick clusters in v1)

## Out of scope
New physical brick colors / hub HSV changes; clusters of 3+; auto-placement of bricks; replacing F0
```

## Issue F1 — Device layering (`BleDevice` + train hub; switches separate)

GitHub: https://github.com/arxarian/lego-trains-controller/issues/154

**Prompt:**

```
Introduce clean device layering so real/sim train hubs share a contract, and BLE transport is reusable for switch hubs later — without a god-Device that is both train and switch.

## Agreed architecture
1. BleDevice (or equivalent): connect/disconnect, GATT, send/receive — shared by real train hub and real switch hub.
2. Train hub role: Device + FakeDevice — speed, color, voltage, disconnect API used by Train / Simulator / QML.
3. Switch actuator role (SW1, not this issue): set_position(A|B); FakeSwitch + real switch. Separate from train hub.

Fake devices implement the role interface; they need not inherit BleDevice.

## Why now
FakeDevice duplicates Device’s Property surface by convention only. Multi-sim and Auto need Train to be device-agnostic. Supersedes #128.

## Depends on
None. Prefer before S1/S2/S3. SW1 uses the switch role separately.

## Current state
- items/device.py — real BLE train hub
- items/fake_device.py — parallel QObject, no BLE
- Train holds a device and uses color/speed/name/initialized

## Requirements
1. Extract train-facing contract used by Train / TrainControlPanel / Simulator:
   name, initialized, color (+ signal), speed (+ setter: local for fake, BLE for real), voltage, minimalSpeed, disconnect(), shutDown(), disconnected Signal
2. Factor BLE transport into a base/helper used by real Device (ready for SW2 to reuse).
3. FakeDevice stays BLE-free.
4. Train type-hints/accepts the train hub contract.
5. Keep QML working (@QmlElement on concrete types as needed).
6. Update TrainsController.pyproject if new files.
7. Small smoke test: FakeDevice works with Train; property surface aligned.
8. Follow project-spec.mdc / coding-spec.mdc.

## Acceptance
- Clear separation: BLE transport vs train hub vs (later) switch actuator.
- Sim start/stop and real connect path still work.
- Docstrings state switch actuators are out of scope for this base.

## Out of scope
SW1/SW2 implementation, plan executor, BLE protocol changes for switches.
```

---

# Slice A — Backend path (no UI required)

## Issue A1 — Logical switch state + correct branch selection

### Subtask A1.1 — Switch position on Rail

**Prompt:**

```
Implement logical switch position on switch rails (no BLE, no planning UI).

## Context
LEGO Trains Controller (Python 3.13, PySide6, QML). Track graph is NetworkX via NetworkGenerator/NetworkManager. SwitchLeft/SwitchRight rails have two path_ids: "A" (straight) and "B" (curved) per resources JSON (e.g. switch left.json).

PathIndicators already has path_id_active used by MultiPathView.qml for visual route. Planner.plan() currently sets this for debug.

Follow .cursor/rules/project-spec.mdc and coding-spec.mdc.

## Goal
Each switch rail has a logical position that selects which path is set, and the UI path indicators reflect it.

## Requirements
1. On Rail (or a small helper used by Rail): for SwitchLeft/SwitchRight only, add:
   - property for active path_id (default "A")
   - optional enum/mode stub can wait for Issue C2; for now position is enough
   - Signal/Property so QML can bind
   - Slot or method to set position (toggle or set path_id "A"|"B")
2. When switch position changes, update that rail's path_indicators.path_id_active to match.
3. Non-switch rails unchanged.
4. Persist in project save/load only if Rail is already serialized in a way that makes this trivial; otherwise session-only is OK and note a TODO. Do not redesign ProjectStorage.

## Files likely involved
- Controller/src/python/items/rail.py
- Controller/src/python/models/path_indicators.py (only if needed)
- Possibly project serialization if Rail fields are saved today

## Acceptance
- Creating/loading a layout with a switch: default position "A", path indicators show A.
- Setting position to "B" updates path_id_active and indicators show B.
- No changes to reservation or planner algorithms yet.

## Out of scope
BLE switch hub, Auto/Manual switch modes, route reservation, train executor, QML click handling (can be a tiny debug Slot callable from Debug panel if useful for testing).
```

### Subtask A1.2 — Branch selection uses switch state

**Prompt:**

```
Fix NetworkManager.find_segment_by_entry_node so switch branches use logical switch state instead of picking the first neighbor.

## Depends on
A1.1 (switch position on Rail exists).

## Context
network_manager.py find_segment_by_entry_node currently:
- lists graph neighbors excluding exclude_node
- if multiple candidates, logs a TODO and picks candidates[0]

Graph edges carry segment_data: list of {rail_id, path_id, from, to}. Switch-adjacent nodes are marked at_switch during generation.

Trains call this when a color marker is seen (train.py on_color_changed) to choose the next segment.

Follow project-spec.mdc / coding-spec.mdc.

## Goal
When leaving a node with multiple forward neighbors, choose the neighbor consistent with current switch positions on the rails involved in those candidate edges. If only one candidate, keep current behavior.

## Requirements
1. Implement deterministic selection using:
   - edge segment_data path_ids
   - Rail.type SwitchLeft/SwitchRight and that rail's active path_id
2. If a candidate edge requires a switch path that is NOT currently set, do not pick it (unless no valid candidate remains — then document fallback: None or best-effort; prefer returning None and logging clearly).
3. Keep segment id format "sorted_a:sorted_b".
4. Add pytest covering a small hand-built or generated graph with a switch and two exits; assert correct segment for path A vs B.

## Files likely involved
- Controller/src/python/network_manager.py
- Controller/src/python/items/rail.py (read switch position)
- Controller/tests/ (new or extend test_network_manager.py)

## Acceptance
- With switch on A, train/network selects the A branch segment.
- Flip to B → selects B branch segment.
- Unit test fails if first-neighbor logic returns.

## Out of scope
Reserving whole routes, planner Dijkstra, QML, physical switches.
```

---

## Issue A2 — Route computation (NetworkX)

### Subtask A2.1 — Shortest path between marker nodes

**Prompt:**

```
Implement pure route computation: shortest path between two marker graph nodes using NetworkX. No motors, no UI, no reservation yet.

## Depends on
A1 recommended (switch-aware edges help later) but A2.1 can compute on the undirected graph first. If switch constraints are not applied yet, document that paths may include either branch; A2.2 will add switch requirements.

## Context
- NetworkManager holds _graph and _segments after generate().
- Marker nodes are in the graph; color_map maps color hex → node_id.
- Planner (planner.py) is currently a stub; put routing API on Planner or a small RoutePlanner helper owned by Planner — keep Planner as the QML-facing facade if methods need @Slot later.
- Weights: edges already have weight (distance).

Follow project-spec.mdc / coding-spec.mdc. Prefer networkx.shortest_path / shortest_path_length with weight="weight".

## Goal
Given from_node_id and to_node_id, return a structured route leg:
- ordered node ids
- ordered segment ids ("a:b" sorted form matching NetworkManager._segments keys)
- total length
- clear error if no path / unknown nodes

## Requirements
1. API roughly:
   - compute_leg(from_node: str, to_node: str) -> LegResult | None
   - LegResult should be a simple dataclass or QObject-free structure (backend first)
2. Segment id for each consecutive node pair must match NetworkManager segment keys.
3. from_node == to_node → empty leg or explicit trivial result (pick one; document).
4. Pytest with an existing project layout or generated rails used by current network tests; assert path exists and segments are in _segments.

## Files likely involved
- Controller/src/python/planner.py (and/or new python/routing.py)
- Controller/tests/test_planner.py (new)

## Acceptance
- Unit test: two known marker nodes → non-empty segment list, each segment in network.segments().
- No QML changes required.

## Out of scope
Multi-waypoint lists, reservation, executor, switch locking, UI.
```

### Subtask A2.2 — Extract required switch positions for a leg

**Prompt:**

```
Extend route computation so each leg reports which switches must be set (rail_id → path_id) for the train to traverse that path.

## Depends on
A2.1, A1.1.

## Context
Edges include segment_data with rail_id and path_id. Switch rails use path_id "A" or "B". When a leg traverses a switch rail on path B, that switch must be set to B before the train is allowed to depart (reservation slice will apply this).

## Goal
LegResult includes required_switches: list/dict of {rail_id, path_id} for SwitchLeft/SwitchRight rails appearing in the leg's segment_data (dedupe; last/consistent path_id wins; conflict on same rail with two path_ids = invalid leg / error).

## Requirements
1. Derive required switches from the chosen path's segment_data (not from current switch state).
2. Unit test: path through curved branch requires path_id "B" on that switch rail.
3. Keep API pure (no mutating rails yet).

## Files
- Same as A2.1 + tests

## Acceptance
- Test asserts required_switches for a known branched path.
- Non-switch rails never appear in required_switches.

## Out of scope
Actually setting/locking switches (Issue A3 / C2).
```

### Subtask A2.3 — Multi-waypoint path (concatenate legs)

**Prompt:**

```
Add helper to compute a list of legs for an ordered list of marker node waypoints (Tycoon orders without looping execution).

## Depends on
A2.1 (A2.2 nice-to-have in same PR).

## Requirements
1. compute_route(waypoints: list[str]) -> list[LegResult] for consecutive pairs (w0→w1, w1→w2, ...).
2. If any leg fails, fail the whole route with a clear reason (which pair failed).
3. Do not loop back to start here (looping is executor responsibility).
4. Pytest with 3 waypoints.

## Out of scope
Executor, reservation, UI.
```

---

## Issue A3 — Leg reservation / interlocking

### Subtask A3.1 — Segment ownership table

**Prompt:**

```
Introduce segment ownership so a segment can be reserved by at most one train (or free). Keep visual rail reservation indicators working.

## Context
Today NetworkManager.reserve(segment_id) / unreserve(segment_id) paint reservation on rails via rail.reserve_segment but do not track which train owns the segment or prevent double-reserve.

Train.on_color_changed unreserves previous segment and reserves the new one (occupancy style).

MVP interlocking decision: before an Auto train departs toward the next waypoint, it must atomically reserve ALL segments of that leg. Conflict policy = Hold.

Follow project-spec.mdc / coding-spec.mdc.

## Goal
NetworkManager (or Interlocking helper used by it) tracks owner per segment_id.

## Requirements
1. Data: segment_id → owner_id (train identity string or object id); missing key = free.
2. try_reserve_segment(segment_id, owner) -> bool
   - false if owned by someone else
   - true if free or already owned by same owner (idempotent)
   - on success, call existing visual reserve if newly taken
3. release_segment(segment_id, owner) -> bool
   - only owner can release; clears ownership + visual unreserve
4. release_all_for(owner) for pause/manual cleanup
5. Do not break manual/sim occupancy flow yet: adapt Train to use ownership API OR keep old reserve as wrapper that uses a stable owner id for that train.
6. Pytest: two owners cannot hold same segment; same owner re-reserve OK.

## Files
- network_manager.py (preferred place) or new interlocking.py wired from AppContext
- train.py may need small adapt
- tests

## Acceptance
- Unit tests for ownership conflicts.
- Existing sim still runs (update calls if needed).

## Out of scope
Whole-leg API (A3.2), executor, UI, switch locking.
```

### Subtask A3.2 — Atomic leg reserve / release

**Prompt:**

```
Add atomic reserve/release for an entire route leg (list of segment ids). This is the deadlock-prevention MVP for single-track: only one train gets the full path between waypoints.

## Depends on
A3.1, A2.1 (leg has segment list).

## Requirements
1. try_reserve_leg(owner, segment_ids: list[str]) -> bool
   - If ALL segments free or already owned by owner → reserve all, return True
   - Else reserve nothing new (rollback any partial), return False
2. release_leg(owner, segment_ids) or release_all_for(owner)
3. Optional helper apply_required_switches(required_switches) can be a stub/TODO pointing to C2; or set logical switch positions when reserving if A1 exists — prefer setting positions here only if tests stay simple; locking belongs with switch modes (C2).
4. Pytest:
   - Train A reserves full leg → Train B try_reserve_leg same segments fails
   - A releases → B succeeds
   - Partial overlap fails atomically

## Acceptance
- Documented API ready for executor (Issue B1).
- No QML required.

## Out of scope
Hold state machine, waits, Tycoon loop, UI.
```

---

# Slice B — Automatic train (simulator)

## Issue B1 — Order list model + executor

### Subtask B1.1 — Order / plan data model on Train

**Prompt:**

```
Add Tycoon-style order list data model to Train (session-only, no persistence).

## Context
OpenTTD-like orders: ordered list of stops; each stop is a marker graph node id + optional wait_seconds; list loops at runtime (executor in B1.2).

Marker node ids look like f"{rail.id}{path_id}{marker.distance}" and are keys in network color_map / graph.

Train is QObject in items/train.py, exposed via Trains model to QML.

Follow project-spec.mdc / coding-spec.mdc.

## Requirements
1. Order item: target_node_id: str, wait_seconds: float (default 0).
2. Train holds:
   - list of orders (QObject list model preferred for QML — ObjectBasedModel pattern or QVariantList with notify; prefer model if you will bind ListView soon)
   - current_order_index
   - control_mode: Manual | Automatic (enum) — can be stubbed default Manual if B2 not started
3. Python/QML API:
   - add_order(node_id, wait_seconds=0)
   - remove_order(index)
   - move_order(from, to) or clear_orders()
   - set_wait(index, seconds)
4. Signals for UI updates.
5. No motor control in this subtask; model + unit-testable methods only.
6. Update TrainsController.pyproject if new files.

## Acceptance
- pytest or simple unit test: add three orders, remove middle, clear.
- Train still localizes via color as today.

## Out of scope
Executor loop, reservation, canvas clicking, persistence.
```

### Subtask B1.2 — Plan executor (leg reserve → move → wait → loop)

**Prompt:**

```
Implement the automatic plan executor that follows a train's looping order list using whole-leg reservation and Hold on conflict.

## Depends on
A2 (compute_leg), A3 (try_reserve_leg), B1.1 (orders on Train). A1 for correct branching at switches.

## Product rules
- Loop orders forever when Automatic.
- Before leaving toward next order: compute_leg(current_node → next_order.node), try_reserve_leg; if false → Hold (speed 0), retry later.
- On arriving at marker matching next order: stop, wait wait_seconds, advance index (wrap), release previous leg as appropriate, then try next leg.
- Between markers position unknown — only advance on color events.
- Must have known current_node_id before starting Auto; else wait until first localization.
- Manual mid-run (if mode exists): Pause — release leg, keep orders, speed manual. If mode API not ready, provide pause()/resume() on executor.

## Architecture guidance
- Prefer a PlanExecutor class (QObject) owned by Train or Planner/AppContext, not a giant ball of logic in Device.
- Use asyncio/qasync consistent with Simulator (asyncio tasks / sleep for wait and hold retry). Do not block Qt GUI thread with time.sleep.
- Speed: set device speed to last non-zero or fallback 40 when Moving; 0 when Hold/Waiting.
- Integrate with Train.on_color_changed: either executor handles progress, or Train emits and executor listens — avoid double-reserving conflicting with old single-segment logic. Migrate occupancy to leg ownership cleanly.

## Simulator
Extend or cooperate with Simulator so an Auto train can be tested: FakeDevice color sequence should be able to follow a planned A→B→A (or document how to drive colors for the test). Minimum: pytest-level test of executor state machine with mocked network/device if full sim is heavy; plus manual sim path if feasible.

## Acceptance
- With two waypoints and free track: Auto train reserves leg, "moves" (speed > 0), on fake color at destination waits, loops.
- Second owner holding overlapping leg → executor stays Hold (speed 0) until free.
- No QML required beyond existing speed display.

## Out of scope
Canvas order editing UI (C1), switch click UI (C2), physical hubs, order persistence.
```

---

## Issue B2 — Train Manual / Automatic mode

**Prompt:**

```
Expose per-train Manual vs Automatic control mode and wire it to the plan executor and TrainControlPanel.

## Depends on
B1.2 (executor exists). B1.1 mode field may already exist — finish wiring.

## Requirements
1. Train.control_mode: Manual | Automatic with Property/Signal; QML-accessible.
2. Manual (default):
   - Existing TrainControlPanel speed slider remains authoritative
   - Executor paused; release_all_for this train / release current leg
   - Orders list retained
3. Automatic:
   - Slider disabled or ignored; executor owns speed
   - Requires non-empty orders and network.has_graph; else reject / stay Manual with message/log
4. QML: toggle or ComboBox on TrainControlPanel.qml (Run mode).
5. Mixed fleet: trains independent.
6. Switching Auto→Manual mid-leg: pause behavior from product decisions.

## Files
- items/train.py
- plan executor module
- qml/TrainControlPanel.qml
- optionally app_context if executor needs wiring

## Acceptance
- One train Manual (slider works), another Automatic (follows orders) can coexist conceptually.
- Mode toggle updates Property and pauses/starts executor.

## Out of scope
Order editing UI, switch modes, BLE switches.
```

---

# Slice C — UI

## Issue C1 — Plan UI (canvas click + order list)

### Subtask C1.1 — Select planning target train + order list panel

**Prompt:**

```
Add Run-mode UI to view/edit the selected train's Tycoon order list (without canvas click yet).

## Depends on
B1.1 (orders model). B2 helpful for Start Auto.

## Requirements
1. In Run mode, extend TrainControlPanel or a side panel:
   - List current orders (show human-readable label: marker color if resolvable + short node id)
   - Edit wait seconds per order
   - Remove order / clear all / reorder (up/down buttons OK for MVP)
   - Show current_order_index and simple status text if executor exposes it ("Moving", "Holding for path", "Waiting 5s", "Manual")
2. Selected train = the train whose panel is focused/expanded OR explicit "planning target" on trains model — pick the simplest approach consistent with horizontal ListView of trains.
3. Follow existing QML style (QtQuick.Controls, TrainView 1.0); no new design system.
4. Register any new QML in TrainsController.pyproject / qmldir if required by project convention.

## Acceptance
- Can add orders from a temporary debug Slot (node id string) and see them in the list; remove/edit wait works.
- Ready for C1.2 to call add_order from marker clicks.

## Out of scope
Canvas hit-testing, route polyline drawing, persistence.
```

### Subtask C1.2 — Click marker on canvas to append order

**Prompt:**

```
In Run mode, clicking a placed (taken) marker on the track canvas appends it as an order for the planning-target train.

## Depends on
C1.1, B1.1. Network must be generated so marker → graph node id is known.

## Context
MarkerItem.qml currently uses SelectableItem mainly for Edit mode (enabled: Globals.editMode && marker.taken). Run mode needs a different interaction: click → add order, not delete/select for edit.

Node id format must match NetworkManager.build_color_map / generator: f"{rail.id}{path_id}{marker.distance}".

## Requirements
1. When tab is Run Mode (!Globals.editMode) and marker.taken and has color:
   - Clickable
   - Resolve graph node id (Python Slot on Planner/Network/Train preferred over duplicating formula in QML)
   - Append order to planning-target train (wait_seconds default 0)
2. If no graph / node not in graph: ignore + log/status message.
3. If no planning-target train: ignore + message.
4. Do not break Edit mode marker placement/selection.
5. Optional: brief visual feedback (flash/border) — keep minimal.

## Files likely
- qml/MarkerItem.qml
- qml/Globals.qml / Main.qml if needed for run-mode click routing
- planner.py or trains.py Slot: addOrderForMarker(railId, pathId, distance) or addOrderForNode(nodeId)
- items/marker.py if exposing rail id / helpers

## Acceptance
- Run mode: click red marker → order appears on selected train's list with correct node.
- Edit mode behavior unchanged.
- Auto executor (if present) can use these orders without manual node id typing.

## Out of scope
Drag-reorder on canvas, drawing the reserved leg polyline, multi-select.
```

---

## Issue C2 — Switch Manual/Auto + click to toggle

### Subtask C2.1 — Click switch on canvas to toggle logical position

**Prompt:**

```
In Run mode, clicking a switch rail toggles its logical position (A↔B) when the switch is Manual and not locked.

## Depends on
A1.1 (logical position). A3/C2.2 for lock — if lock not ready, toggling always allowed but log a TODO.

## Requirements
1. Detect switch rails in Run mode click path (RailItem.qml or similar).
2. Toggle path_id A↔B; path indicators update (already via A1.1).
3. Visible which route is set (existing MultiPathView / path_id_active).
4. Do not toggle in Edit mode (edit keeps current rail selection behavior).

## Acceptance
- Click switch in Run mode flips indicators between A and B.
- Straight/curved rails ignore this click behavior.

## Out of scope
BLE actuation, Auto mode setting switches from routes (C2.2).
```

### Subtask C2.2 — Switch Manual/Auto + lock while leg reserved

**Prompt:**

```
Add per-switch Manual|Automatic mode and lock switches when a reserved leg requires them.

## Depends on
A1, A2.2 (required_switches), A3.2 (leg reserve), C2.1 (click toggle).

## Requirements
1. Switch rail properties: control_mode Manual|Automatic; locked: bool (or locked_by owner).
2. On successful try_reserve_leg: for each required switch, set path_id and lock (Auto trains / interlocking).
3. On release_leg: unlock switches that are no longer required by any remaining reservation (simple v1: unlock all that were locked by this owner).
4. Manual click toggle: allowed only if !locked && (Manual mode or always Manual click only when Manual mode).
5. Automatic switches: user click rejected when Auto; interlocking sets position.
6. QML: optional small badge/mode later; minimum = click respects rules + indicators show position.

## Acceptance
- Reserve leg needing B → switch shows B and click cannot flip until release.
- After release, Manual click works again.

## Out of scope
Physical BLE switch hub (Issue D1).
```

---

# Slice SW — Switch actuators (simulated + real)

Logical switch position on the rail (A1) is the source of truth for routing/UI.  
**Actuators** are optional devices bound 1:1 to a switch rail: either a **simulated** switch or a **real BLE** switch hub.  
When a project/track is loaded (and graph generated), the user assigns unbound switch rails to a device: “Add simulated switch” or “Assign discovered real switch”.

## Issue SW1 — Switch device model + assign to graph switches

**Prompt:**

```
Implement switch actuators that can be simulated or real, and a Run-mode way to bind them to switch rails in the loaded track.

## Depends on
A1.1 (logical path_id / position on SwitchLeft/SwitchRight rails). C2.1 helpful for click-to-toggle logical state.

## Product model
- Each switch rail in the project may have zero or one bound actuator device.
- Actuator types:
  1. FakeSwitchDevice — no BLE; applying position only updates logical rail state (and can expose the same Property/Slot surface as real).
  2. Real SwitchDevice — BLE hub (protocol in SW2); applying position sends a command and updates logical state.
- Binding is 1 hub ↔ 1 switch rail for MVP.
- After loading a project / generating the network, user must be able to assign devices to switch rails that appear in the layout.

## Requirements
1. Shared interface (duck-typed or base QObject) usable by interlocking later: set_position(path_id "A"|"B"), position property, connected/initialized, name/id for UI.
2. FakeSwitchDevice implementing that interface; “Add simulated switch” creates one and binds it to a chosen unbound switch rail (or creates unbound then assign — pick one UX and document).
3. SwitchDevices model (similar spirit to Devices/Trains) exposed on AppContext; list unbound vs bound.
4. Assignment UI in Run mode (panel is fine for MVP):
   - List switch rails (id, type, current path_id, bound device name or “unassigned”)
   - Action: Add simulated switch → bind to selected rail
   - Action: Assign existing/discovered real device to selected rail (real connect can stub until SW2)
   - Action: Unbind
5. When logical position changes on a rail (UI toggle or code), if an actuator is bound, call set_position so sim/real stay in sync.
6. Persist bindings in project JSON if straightforward (e.g. rail id → device kind + name/key); otherwise session-only with a clear TODO. Prefer persist simulated bindings; real hubs may re-assign after rediscovery.
7. Update TrainsController.pyproject for new files.
8. Follow project-spec.mdc / coding-spec.mdc.

## Acceptance
- Load a layout with ≥1 switch: can add a simulated switch and bind it; toggling logical position goes through the fake device API.
- Unbind works; second simulated switch can bind to another rail.
- Non-switch rails never appear in the assignment list.
- Unit or smoke test for FakeSwitchDevice set_position updating rail path_id_active / switch position.

## Out of scope
BLE protocol/firmware (SW2), multi-train sim, path planning executor, locking from interlocking (C2.2 can call the same set_position later).
```

## Issue SW2 — Real BLE switch hub

**Prompt:**

```
Implement the real BLE switch hub device and wire it into the SW1 assignment flow (replaces older D1 scope).

## Depends on
SW1 (actuator interface + assignment UI). A1 logical state.

## Context
Train BLE: bleak + GATT c5f50002-8280-46da-89f4-6d8051e4aeef; see items/device.py, TrainHub/main.py. Switch hub is a similar CityHub/Pybricks device but commands set turnout A/B instead of motor speed.

## Requirements
1. Minimal host↔hub protocol: set_position(A|B), optional ack/state; document next to firmware.
2. SwitchDevice (real) implementing the same interface as FakeSwitchDevice.
3. Discover/connect flow analogous to trains (reuse Devices patterns where sensible, or a SwitchDevices discover path).
4. Assignment UI from SW1: “Assign detected switch” lists connected real hubs not yet bound.
5. Logical rail change → BLE command when bound and connected; failures log clearly without crashing UI.
6. Firmware sketch under TrainHub/ or SwitchHub/ (MicroPython) — keep intelligence in the Controller.

## Acceptance
- Mockable send path in tests; manual QA checklist with a real hub optional.
- Simulated and real actuators interchangeable at the binding layer.

## Out of scope
One hub driving multiple turnouts, planning, sim trains.
```

---

# Slice S — Simulator (trains)

Evolve existing `simulator.py` + `FakeDevice`; do not build a second engine.

## Issue S1 — Path-aware single simulated train (+ respect switches)

**Prompt:**

```
Upgrade the existing Simulator so one FakeDevice train drives along the graph using switch state, so you can see how the train moves in simulation.

## Depends on
F1 recommended (TrainDevice base). A1.1 + A1.2 (logical switch + branch selection). SW1 optional but nice (sim switches assigned); minimum is logical switch position.

## Current state
Simulator builds a fixed color circuit from color_map and walks it with delays. It does not follow switch position or reserved legs. RunPanel has Start/Stop Simulation.

## Goal
One simulated train: given current node + switch positions, advance to the next marker by traversing the graph (same rules as find_segment_by_entry_node / neighbors). Changing a switch should change where the sim train goes on the next branch. Manual speed still controls step delay (existing behavior).

## Requirements
1. Replace or gate the fixed circuit walker with graph-following marker sequence.
2. At switches, honor active path_id when choosing the next marker.
3. Keep a single sim train for this issue (add/remove via existing start/stop or “Add sim train” that creates one FakeDevice + Train).
4. Train still localizes via color_changed like a real hub (FakeDevice.set_color).
5. Visible in Run UI with TrainControlPanel (already works once Train is added).
6. Tests: small graph with a switch — position A vs B yields different next marker from the junction approach.

## Acceptance
- With a branched layout, flip switch A↔B and the sim train’s subsequent marker colors follow the selected branch.
- Start/stop sim remains usable without planner/Auto.

## Out of scope
Tycoon orders, Auto executor, multiple sim trains, BLE switches (logical/fake enough).
```

## Issue S2 — Plan route for one simulated train

**Prompt:**

```
Enable Tycoon-style route planning / Auto execution for a single simulated train (debug planner without physical hubs).

## Depends on
S1 (path-aware sim colors). B1.1 + B1.2 + B2 (orders, executor, Manual/Auto). A2 + A3 (legs + reservation). C1 helpful for clicking markers to build orders.

## Goal
User assigns orders to the one sim train (canvas click or panel), sets Automatic, and the sim train follows: reserve whole leg, move (FakeDevice colors along the reserved path), wait at markers, loop. Hold if leg cannot be reserved (only one train here — mainly for API readiness / blocked-by-manual-reserve tests).

## Requirements
1. Simulator advancement must cooperate with executor: prefer emitting the next marker on the reserved/planned leg rather than a free-roam circuit that ignores the plan.
2. When Manual: existing S1 free-roam or paused behavior; when Automatic: executor owns speed and progress.
3. Wait_seconds at orders must be observable (train speed 0 for N seconds in sim time).
4. Document how to run a manual QA: generate graph → start sim train → add orders → Auto → observe.

## Acceptance
- One sim train loops A → wait → B → A under Auto with whole-leg reservation.
- No second train required.

## Out of scope
Multi-train conflicts (S3), real BLE trains (should still work if executor is device-agnostic).
```

## Issue S3 — Multiple simulated trains + planning

**Prompt:**

```
Support multiple FakeDevice trains in the simulator, each with its own plan, to debug Hold and multi-train interlocking.

## Depends on
S2, A3 (atomic leg reserve / Hold), B2 (per-train Manual/Auto).

## Requirements
1. UI: add/remove additional simulated trains (names Simulator-1, Simulator-2, …).
2. Each has independent orders and control mode.
3. Path-aware color emission per train without cross-talk (each FakeDevice own color stream).
4. Demo/QA: two stations (or two waypoints) on a single-track corridor — opposing Autos; second Holds until first releases whole leg.
5. Mixing one Manual sim train + one Auto sim train must work.

## Acceptance
- Two Autosim trains cannot both hold the same leg; Hold then proceed when free.
- Start/stop or remove sim trains cleans reservations for that owner.

## Out of scope
Physics-perfect timing, canvas animation interpolation (#120), real hubs.
```

---

# Slice E — Polish (later)

## Issue E1 — Persist order lists in project JSON

**Prompt:**

```
Persist per-train (or per-device-name) Tycoon order lists in project save/load.

## Depends on
B1.1, C1.

## Notes
Trains are often created from connected devices and may not exist at project load. Define a clear key strategy (e.g. device name / hub id) and document behavior when device missing. Keep schema backward compatible.
```

## Issue E2 — Draw planned / reserved leg on canvas

**Prompt:**

```
Visually highlight the reserved or planned leg (segments or path indicators) for the selected Auto train so the user can see the locked route.

## Depends on
A3, C1.

## Prefer reusing reservation_indicators / path_indicators rather than a new graphics stack. Keep Run-mode performance acceptable.
```

## Issue E3 — Stronger hold UX + graph invalidation

**Prompt:**

```
Improve Hold feedback ("blocked by train X on segment Y") and cancel/invalidate plans when NetworkManager.generate() rebuilds the graph (clear reservations, pause executors, mark orders needing revalidation).
```

## Issue E4 — Passing loops / advanced deadlock (future)

**Prompt:**

```
Design-only or later implementation: allow meets at sidings; reserve only to next safe wait point when multiple wait-capable markers exist on a corridor. Out of scope for MVP full-leg between Tycoon orders. Do not implement unless MVP is stable.
```

---

# Suggested GitHub issue titles

| ID | Title |
|---|---|
| F0 | feat(markers): sanity check / unique colors (GitHub #114) |
| F1 | refactor(device): abstract device bases (BLE + train; switches separate subclass) |
| F2 | feat(markers): color clustering / compound beacons (GitHub #68) |
| A1.1 | feat(planner): logical switch position on switch rails |
| A1.2 | fix(network): select next segment using switch state |
| A2.1 | feat(planner): shortest-path leg between marker nodes |
| A2.2 | feat(planner): required switch positions for a leg |
| A2.3 | feat(planner): multi-waypoint route as list of legs |
| A3.1 | feat(network): segment ownership for interlocking |
| A3.2 | feat(network): atomic leg reserve/release |
| B1.1 | feat(train): Tycoon-style order list model |
| B1.2 | feat(train): plan executor with hold + looping orders |
| B2 | feat(train): Manual vs Automatic control mode |
| C1.1 | feat(ui): order list panel in Run mode |
| C1.2 | feat(ui): click canvas marker to add order |
| C2.1 | feat(ui): click switch to toggle logical position |
| C2.2 | feat(switch): Manual/Auto mode + lock on reserved leg |
| SW1 | feat(switch): sim/real actuators + assign to graph switches |
| SW2 | feat(device): BLE switch hub (real actuator) |
| S1 | feat(sim): path-aware single simulated train |
| S2 | feat(sim): plan route for one simulated train |
| S3 | feat(sim): multiple simulated trains + planning |
| E1–E4 | polish / future (as titled above) |
| ~~D1~~ | superseded by SW1 + SW2 |

---

# Agent bootstrap blurb (paste above any single prompt)

```
You are implementing a slice of LEGO Trains Controller route planning.
Read .cursor/rules/project-spec.mdc and coding-spec.mdc first.
Stack: Python 3.13, PySide6, QML, NetworkX, asyncio/qasync, pytest.
Match existing patterns (QObject Property/Signal/Slot, ObjectBasedModel, AppContext wiring).
Update Controller/TrainsController.pyproject when adding source files.
Do not expand scope beyond this issue's Acceptance / Out of scope.
Shared MVP decisions: Tycoon looping orders; whole-leg atomic reservation; Hold on conflict; canvas marker click for orders; Manual/Auto per train; logical switches before BLE.
Prefer F1 (abstract TrainDevice) before multi-sim work so Train stays device-agnostic.
```
