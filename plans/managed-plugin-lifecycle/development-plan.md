# Managed plugin lifecycle: development plan

Status: native foundation implemented and validated; manager phases remain planned.
Date: 2026-11-04.
Feature contract: [feature-description.md](feature-description.md).
Checkpoint evidence: [checkpoint-validation.md](checkpoint-validation.md).

## Baseline and confirmed direction

The following existing code should be extended and reused:

| Area | Current entry points | Work needed |
| --- | --- | --- |
| Python plugin contract | `src/rpp_py/rpp_py/plugin.py` | Replace the initializer with the new lifecycle callbacks. |
| C++ plugin contract | `src/rpp_cpp/include/rpp_cpp/plugin_def.hpp` | Matching typed callback/result API; rebuild plugins/adapters. |
| Context trees | Python `context.py` / `context_builder.py`; C++ `context.hpp` / context builder | State-aware traversal, guarded calls, and manager-owned root lifetimes. |
| Loading | Python `plugin_loader.py`; C++ `plugin_loader.hpp` / `plugin_loader.cpp` | Track module/library ownership and source generations. |
| Adapted runtime | `plugin_runtime.py`, `plugin_runtime.hpp`, component servers, `rpp_server_host` | Addressed lifecycle control and managed startup without eager activation. |
| Internal RPC | `src/rpp_common/rpp_common/plugin_runtime.capnp` | New lifecycle requests, generations, results, and typed state; regenerate all bindings. |
| Registration/generation | `rpp_plugin_registrator` scaffolds, adapter templates, compiled-artifact metadata | Generate callbacks, record ABI/revision, coordinate source replacement. |
| Typed handover | Cap'n Proto annotations/descriptors and Python/C++ struct generation | Resolve the optional lifecycleState binding and generate typed activation/deactivation bridges. |
| Workspace descriptions | `rpp_orchestrator` component/parameter storage | Resolve component instances and ownership; retain current source of truth. |
| CLI | `src/rpp_cli/rpp_cli/cli.py` / `commands.py` | Optional manager commands using the shared ROS client. |
| Shared fixtures | `src/rpp_testing` | Small lifecycle-aware Python/C++ test plugins. |

Current runtime RPC supports ping, shutdown, listing adapters, and capability
lookup. It has no lifecycle operations. Component server startup currently
initializes components before serving, and external processes cannot accept
new components after startup. Treat those as explicit integration changes.

Confirmed design: two helper layers in each language; the ROS bridge receives
an existing node and delegates to a ROS-free manager. Managed units are workspace
component instances and their subtrees. Native/adapted hosting is retained.
Each plugin type may additionally declare a handover-state struct so alternative
implementations can exchange application state during a managed switch.
Backward compatibility is not required. Update first-party code and generated
artifacts to the new contract directly, with no legacy initializer adapters,
dual startup paths, or old-protocol fallback.

## Phase 1 — Freeze the new contract

Deliverables:

- Agree the state/transition table, callback signatures/result type, idempotent
  behavior, error categories, ownership rules, and reload sequence.
- Put `require_success(operation)` on `CallbackResult` itself in both languages;
  test successful return and failures carrying the operation and error reason.
- Use `on_configure(context)` as the initialization callback and remove the old
  plugin `initialize(context)` API. Specify the corresponding context API changes.
- Define manager-local names, component references, generation IDs, operation
  IDs, and the state snapshot returned by both languages.
- Use the agreed optional `lifecycleState` annotation. Define no-state versus
  cold-activation semantics, `DeactivationResult<State>`, and typed activation
  inputs. Without a state declaration, generate argument-free activation and
  deactivation callbacks. Keep handover state separate from lifecycle state enums.
- Specify logical-role switching, schema/revision compatibility, semantic
  validation, and failure behavior when the old plugin is already inactive.
- Confirm post-reload activation policy, source-update trigger, manager
  configuration format, and names/placement of optional ROS packages.
- Define how outdated C++ plugin/adapter ABI metadata is rejected and rebuilt.

Exit condition: a reviewed language-independent contract with a few complete
callback traces, including activation failure and unsuccessful reload. No ROS
message layout or CLI command is finalized ahead of these decisions.

## Phase 2 — Add lifecycle callbacks and context traversal

Owners: `rpp_common`, `rpp_py`, `rpp_cpp`, `rpp_plugin_registrator`, `rpp_testing`.

- Add core lifecycle states, result types, and the callback surface in Python
  and C++. Keep ROS types out of signatures.
- Replace legacy initialization calls with the new configure transition. Update
  Python and C++ callers, generated plugin bases, fixtures, and applications in
  the same delivery. Keep `reset()` separate.
- Update generated bases, adapters, scaffolds, metadata, and examples together;
  do not add lifecycle methods independently to every user-defined Cap'n Proto
  plugin type.
- Implement the optional annotation binding and validate the resolved handover struct.
  Reuse generated Python dataclasses and C++ owning values. Generate typed
  callbacks over internal schema-aware dispatch, rather than incompatible C++
  virtual overloads or generic Python dictionaries.
- Implement subtree ordering and rollback of partial activation, using the
  existing best-effort cleanup/error-reporting conventions.
- Add `rpp_testing` fixtures whose callbacks record order and can fail at
  selected phases. Store reusable fixture data there.

Validation: matching Python/C++ traces for normal lifecycle, invalid states,
a failing child, and a failing parent. Update runtime tests to the new callback
contract and require them to pass. Reject invalid state-schema declarations
and distinguish an absent initial snapshot from a default-valued snapshot.

## Phase 3 — Implement the ROS-free managers

Owners: `rpp_py`, `rpp_cpp`, with shared contracts in `rpp_common`.

- Implement Python and C++ `PluginManager` around existing context builders and
  loaders. Support a named list of component specifications, empty startup,
  and dynamic additions/removals.
- Add a coordinated switch operation: prepare target inactive, quiesce and
  deactivate source, validate/copy its returned state, activate target with it,
  then commit active-role routing. Preserve truthful state on failed handover.
- Add list/get state, load, configure, activate, deactivate, cleanup, unload,
  and coordinated reload operations. Separate desired specification from
  actual loaded state so failed operations remain diagnosable/retryable.
- Implement call gates, scoped active-access handles, in-flight call draining,
  operation serialization, and generation validation. Preserve plugin-specific
  typed interfaces inside guarded calls.
- Restore only entries changed by a failed operation; never dismantle unrelated
  components. Preserve the first error and report additional teardown failures.
- Keep state queries responsive during long operations. Specify the lock and
  executor ownership model before adding asynchronous control requests.

Validation: independent managers in each language, two instances of one plugin,
concurrent call/deactivation, stale handles, partial batch failure, and graceful
shutdown. An inactive plugin cannot be called through a managed handle.

## Phase 4 — Extend native/adapted lifecycle control

Owners: `rpp_common`, `rpp_py`, `rpp_cpp`, `rpp_plugin_registrator`.

- Define runtime control methods for addressed lifecycle operations, state
  transfer, and exact protocol-version validation. Old method ordinals and old
  wire layouts need not be retained; do not negotiate an older protocol.
- Regenerate C++ runtime bindings with the pinned Cap'n Proto toolchain. Update
  server/client implementations and adapter generation in the same change.
- Make component servers serve an unconfigured tree until explicitly configured
  through the new lifecycle. Update all callers; do not keep an eager legacy path.
- Carry schema-tagged handover snapshots through lifecycle RPC results/requests.
  Copy values before releasing message/process storage; preserve existing domain
  adapter behavior and avoid Python-only object serialization.
- Execute lifecycle callbacks beside the real plugin, propagate real remote
  results, and prevent calls to remote inactive/obsolete generations.
- Give each managed root an independent process ownership scope. Reuse existing
  RPC executors/process launchers without stopping another root's server.
- Define timeout outcomes and duplicate-operation handling; a lost response
  must not cause a second load/reload when the client retries.

Validation: Python host/C++ plugin, C++ host/Python plugin, mixed-language
subtrees, remote callback failure/disconnection, and unloading one root while
another remains active. Verify state transfer in both language directions,
including values remaining valid after the source is unloaded. Check both
callbacks and actual domain-method execution.

## Phase 5 — Make replacement reliable

Owners: managers/loaders and registration/build tooling.

- Implement one replacement path used by reconfiguration and source updates:
  quiesce, deactivate, cleanup, destroy/unload, rebuild/refresh when requested,
  load, configure, and restore the requested active/inactive state.
- Read fresh parameters and component specifications for the new instance.
- Add explicit state-preserving reload: retain the deactivation snapshot across
  replacement and supply it after configuration. Validate compatibility with
  changed parameters/schema; state transfer is not automatic for reconfiguration.
- Track source/artifact revisions and affected instances, including helper
  modules and shared adapter libraries. Prevent eviction of live dependencies.
- Stage immutable artifact generations. Publish a new generation only after
  successful construction/configuration; retain failed-operation diagnostics.
- Audit all owners of C++ handles before `dlclose`, and Python references and
  module namespaces before source replacement. Keep external server lifetimes
  within the affected root's ownership.
- Connect a coordinated source-update command to registration refresh/building;
  existing registry-only commands must not silently claim to update live code.
- On failure, leave a truthful unloaded/inactive/error state. Do not fall back
  to old active code automatically. Refuse unloading if calls cannot quiesce.

Validation: fresh object identity and parameters after reconfigure; v1-to-v2
behavior after source update; unchanged sibling instances; failed build,
configuration, activation, and teardown; retained handles and drain timeout.
Successful reload alone is insufficient evidence—call the new implementation.

## Phase 6 — Add the ROS node bridges

Proposed owners: optional `rpp_ros2` and `rpp_ros2_interfaces` packages.

- Provide both `RosPluginManagerBridge(node, manager)` and its C++ equivalent.
  Use the supplied node; do not require users to replace their node class.
- Define ROS services/results, state snapshots, and lifecycle-event messages
  from the already reviewed core contract.
- Expose core switching with source/target/role and transfer-state options.
  Keep domain handover values inside the core/internal RPC path unless a
  separately typed ROS API is explicitly designed; do not publish opaque Python objects.
- Create namespaced services and state/event publishers. Configure snapshot
  durability and bounded event history; include operation/generation IDs.
- Convert requests to core manager operations; publish authoritative manager
  results, including failures. Keep all transition decisions in the core.
- Integrate callback groups and manager/RPC executors without deadlocks or
  running build/reload work in a time-sensitive subscription/update callback.
- Expose a guarded binding hook for application-specific ROS behavior. Document
  node/bridge/manager ownership, explicit closure, and node shutdown order.
- Keep core installation and imports functional without ROS.

Validation: existing Python and C++ nodes construct the bridge; a ROS service
drives a real plugin callback; event/state topics agree with manager state;
namespace isolation, concurrent node callbacks, and node shutdown work.

## Phase 7 — Add spawner, unspawner, and CLI commands

Owners: optional ROS package/client and `rpp_cli`.

- Implement one reusable service client for the ROS executables and CLI.
- Implement spawn-to-active, inactive/load-only modes, list, activate,
  deactivate, unload, reload/source-update, and switch commands. Include explicit
  state-transfer and preserve-state options with failure diagnostics.
- Parse instance/component specifications from the existing workspace and the
  selected manager configuration. Reject duplicate names and invalid references
  before changing live state.
- Add manager discovery/operation deadlines and explicit request IDs. Report
  timeouts as uncertain outcomes to query, not as proof of cancellation.
- Add per-instance batch results, meaningful stderr, nonzero failure exit codes,
  and opt-in attached spawner ownership/cleanup behavior.
- Import ROS dependencies lazily in `rpp_cli`. Add shell completion and update
  the CLI reference alongside the parser.

Validation: spawn/unspawn after node startup from a separate process; load-only
and inactive states; full replacement on reconfigure/source update; unavailable
manager, duplicate request, callback error, and CLI timeout. Verify the ROS
executables and `rpp manager` delegate to the same client behavior.
Add a localization example with two implementations sharing one Cap'n Proto
state contract. Verify the destination's first estimate starts from the source's
final estimate, and reject a mismatched frame/schema or a missing required state.

## Phase 8 — Documentation, CI, and delivery

- Add one Python-node and one C++-node example with a short-lived spawner, a
  declared component list, activation/deactivation, and a source replacement.
- Document each callback's resource obligations, tree ordering, borrowed-handle
  lifetime, failure recovery, and the required plugin/adapter rebuild.
- Coordinate package changes and dependency pins so CI uses matching contracts
  and regenerated artifacts; do not ship a mixture of old and new runtimes.
- Put system-level lifecycle/ROS guides in `rpp_docs`; keep API and installation
  details in package READMEs. Link the feature proposal to the delivered docs.
- Extend existing component CI with a small set of behavior-focused tests;
  place actual ROS bridge/spawner integration tests in the optional ROS package.
- If adding repositories/submodules, establish their own successful `ci.yml`
  before pinning them in `rpp_dev`, whose CI aggregates pinned workflow results.

Delivery is complete when both node examples can dynamically load, activate,
deactivate, reload, and unload workspace components in both languages, failures
remain visible and contained, and updated non-ROS applications use the same
new core lifecycle without requiring ROS.

## Sequencing and review boundaries

### First PR checkpoint: native lifecycle foundation

Freeze feature scope at callbacks, result values, typed native handover, schema
binding/generation, and native context traversal. Include the corresponding
server/fixture migration and focused tests. A single public manager/helper
should own contexts and hide async runtime details from synchronous clients;
do not introduce a separate session object. Do not start manager implementation
until this checkpoint has been reviewed.

Prepare linked PRs for `rpp_common`, `rpp_py`, `rpp_cpp`,
`rpp_plugin_registrator`, and `rpp_testing`. The `rpp_dev` PR carries the plans
and, after component commits exist, their tested submodule pins. No changes to
`rpp_cli`, `rpp_orchestrator`, or `rpp_docs` are required for this checkpoint.

Checkpoint validation is complete for the coordinated working tree:

- Generated stateful/stateless Python and C++ adapter clients implement concrete
  callbacks and explicitly reject unsupported remote lifecycle control. Real
  generated C++ clients compile, link, and execute in the pinned environment.
- All 218 Python runtime and registrator tests pass, including native/adapted
  integration and the generated-adapter regression cases.
- The full C++ build passes with Cap'n Proto 1.1.0. All 38 C++ behavioral cases
  and formatting, CMake lint, and XML lint checks pass through CTest. The image's
  cppcheck 2.19.0 integration skips 43 checks due to its documented performance
  issue; these are tool skips, not skipped behavioral tests.

Remaining work is preparing the linked commits/PRs and their dependency pins,
then checking CI on those exact revisions. Current per-repository CI uses
dependency revisions from its base branch, so isolated PR checks may test
incompatible old dependencies until the linked changes are coordinated. Record
the validation commands, tool skips, and dependency requirements in each PR.

Managers, state machines, call gates, loading/replacement, lifecycle RPC, ROS
bridges, and spawner commands belong to subsequent PR checkpoints.

Implement phases in order, with language parity at each contract boundary.
Review core callback/ABI changes before the manager API, then review ownership
and replacement before ROS services/CLI. Do not ship a public reload command
that can still call cached old code or unload a library with active references.

Proceed in small test-first increments:

1. Make only the `CallbackResult.require_success()` tests pass in Python and
   C++; leave plugins, contexts, schemas, and generators unchanged.
2. Implement callback dispatch and owned handover values against the focused
   tests. Add stateless callback cases before changing their implementation.
3. Add annotation/generator tests for absent, valid, and invalid state bindings;
   then implement the optional annotation and typed generation together.
4. Add context transition/ordering tests, then migrate configuration calls and
   affected fixtures in a separate increment.
5. Proceed to manager, runtime, ROS bridge, and CLI phases after this foundation.

These are implementation milestones, not calendar estimates. Feature branches
exist. Increments 1 and 2 are complete: result checking, activation/deactivation
dispatch, and owned handover values pass their focused tests in both languages.
Increment 3 supports local, non-generic lifecycle state
bindings and generates native callback bases in both languages. Its tests parse
real schemas, exercise generated Python dispatch, and compile generated C++
callback overrides. Increment 4 adds configuration and cleanup callbacks,
child-first configuration and parent-first cleanup, with failure propagation
and continued cleanup after errors. The old initializer API is removed from
contexts, generators, component servers, and fixtures. Python unit verification
passes 134 tests, including configuration, native activation/deactivation, and
builder/runtime ownership;
the standalone C++ lifecycle suite passes 19 tests. Generated callback/adapter
tests pass 14 cases in the pinned environment. Native context activation now traverses children first,
rolls back only completed children on failure, and preserves the first error if
rollback also fails. Deactivation visits the parent first and exports root
state only if the whole tree stops. State payloads apply only to the root;
adapted activation/deactivation explicitly fail until lifecycle RPC is added.
Context traversal is now ready for manager transition and call-gate work.
The `more_simulation` migration and its lifecycle tests have been reverted;
the simulator remains on the legacy initializer until its public RPP usage is
agreed. Do not treat it as validated against this lifecycle branch.
Python now follows C++ ownership: builders prepare external hosts before
returning and transfer ownership to the returned tree. Context infrastructure
start/stop methods are removed. Explicit Python `close()` reports release
failures; destruction supplies best-effort fallback release. Purely native
trees create no async machinery. Partial builds release their reservations and
hosts, and reusing a builder does not shut down earlier trees.

The C++ runtime and test targets build with Cap'n Proto 1.1.0 in an isolated ROS
container workspace. All nine Python native/adapted integration cases pass
there as part of the 218 passing Python runtime/registrator tests. All 38 C++
behavioral tests pass; configured lint outcomes and tool skips are recorded
above. Manager transitions, adapted lifecycle RPC, and state serialization
remain pending.
