# Project Planning Proposal

## Basic Information

| Item | Information |
|---|---|
| A Graph-Assisted Framework for Conflict-Aware Intent Fulfillment and Assurance in O-RAN |
| Student ID / Name | M11502205/ Henry |
| Git Repository / Project Link | TBD |
| Planning Approval Date | TBD |
| Proposal Version | v0.1, 2026-09-18 |

---

# Part A. Detailed Project Planning

## A1. Project Summary

### Problem to be solved

O-RAN enables multiple rApps, xApps, and SMO services to alter RAN configuration through controls such as cell activation or deactivation, transmit-power adjustment, traffic steering, and MIMO adjustment. These controls can support an Energy Saving (ES) intent, but an intent does not itself specify a safe execution sequence, a concrete executor, a target resource, or a recovery action. Moreover, an ES intent can remain active when a later, independent Slice QoS/SLA intent is submitted. A plan that is valid for either intent in isolation may be unsafe when their resource scopes or KPI effects interact.

The project will develop an assurance-driven RAN Management Intent Handler (RMIH) prototype. Given validated machine-readable intents, current normalized RAN state, registered control capabilities, and active-intent conditions, the prototype will generate candidate execution plans, validate their predicted intermediate states, admit only non-conflicting plans, and monitor their outcomes after execution.

### Key challenges

1. A high-level ES objective, such as reducing total energy consumption by a specified target, can be fulfilled through more than one operational path. The system must compare those paths after concrete executor, target, and parameter binding.
2. The effect of an ES operation depends on the current RAN state. An action may reduce energy while causing overload, reduced throughput, or another Slice QoS/SLA violation.
3. Intent drift can occur at three stages: a command is accepted but the intended configuration is not realized; the configuration is realized but observed energy or QoS differs from the prediction; or external traffic and radio conditions invalidate an intent that was previously fulfilled.
4. Conflict resolution cannot rely on an arbitrary hard-coded preference between ES and Slice QoS/SLA. A bounded multi-objective plan-admission method is required, while non-negotiable safety and capability constraints remain enforced.

### Proposed method

The proposed RMIH uses an execution-level graph that represents registered jobs, executors, resources, preconditions, alternative paths, affected KPIs, success evidence, and compensation actions. A Graph Planner produces alternative abstract paths for a validated ES intent. Control Logic Synthesis binds each path to concrete O-RAN operations. A state-aware feasibility evaluator predicts the state after each plan step using audited capability semantics and a testbed-calibrated effect model.

For a later active Slice QoS/SLA intent, the Conflict Admission module compares the incoming plan with active intent constraints, resource reservations, and predicted cross-KPI effects. It selects a feasible non-dominated plan, defers or rejects an inadmissible plan, or returns alternatives to the RMIO when the available inputs do not authorize a unique choice. An Assurance Manager compares intended, predicted, and observed state to detect execution, outcome/model, and environment drift and then triggers retry, compensation, rollback, replanning, deferment, or escalation.

### Expected outcomes

The expected outcome is an end-to-end prototype and an experimentally supported method for bounded O-RAN intent fulfillment. The project will deliver: (1) a capability-audited execution graph and Job Catalog; (2) concrete ExecutionPlan, ConflictReport, and AssuranceDecision artifacts; (3) controlled evaluation scenarios for alternative ES paths, ES-Slice conflicts, and three drift classes; and (4) evidence on planning quality, unsafe-plan rejection, intent fulfillment, conflict handling, and recovery latency. The project will not claim general support for arbitrary O-RAN intents, unrestricted natural-language interpretation, or universal power-model accuracy.

---

## A2. System Architecture

### System assumptions

- The upstream intent-ingestion function is reused from Kenny's work. It translates human requests into validated YAML intent instances. Natural-language understanding is not evaluated as a contribution of this project.
- Two independent intent types are in scope:
  - Energy Saving Intent: requests a specified reduction in total energy consumption over an authorized RAN scope and observation window.
  - Slice QoS/SLA Intent: independently specifies measurable QoS/SLA conditions, lifecycle information, and allowable flexibility. Its control operations and observable KPIs are TBD until the capability audit.
- The prototype operates in one controlled O-RAN administrative domain using maintained OSC and VIAVI AI RSG components.
- Candidate ES operations may include cell on/off, transmit-power adjustment, traffic steering, and MIMO adjustment. Only audited, registered, and measurable operations are admitted to the final prototype.
- Safety limits, API capability bounds, and explicit non-negotiable intent constraints are enforced as feasibility conditions. The project does not use a fixed hard-coded rule such as “ES always loses to SLA” for all conflict-resolution decisions.
- Energy is evaluated through directly observable energy or power telemetry where available. If direct measurement is unavailable, the project will use a documented and validated testbed-specific energy-estimation model and will state that limitation explicitly.
- The effect model is limited to selected audited operations and testbed conditions. It is not assumed to generalize across vendors, radio hardware, or arbitrary traffic environments.

### Environment

| Component | Role in the project |
|---|---|
| RMIO and Intent Specification Registry | Receives validated YAML intent instances from the upstream IBN flow. |
| Active Intent Registry | Stores active intents, scopes, constraints, lifecycle state, selected plans, and fulfillment status. |
| OSC / SMO / Non-RT RIC | Hosts the proposed RMIH logical modules and invokes registered control services. |
| VIAVI AI RSG and maintained testbed components | Provide the controlled RAN environment, available control actions, and telemetry. |
| Telemetry and RAN State Store | Normalizes timestamps, freshness, identifiers, units, missing values, and observation windows before planning or assurance. |
| Registered executor rApps, xApps, or SMO services | Execute only audited and schema-validated operations. |

### Input parameters

| Symbol / Input | Description |
|---|---|
| I_ES | Validated Energy Saving intent: authorized scope, energy target, lifecycle, constraints, and permitted flexibility. |
| I_Slice | Validated independent Slice QoS/SLA intent: scope, measurable SLA targets, lifecycle, and permitted flexibility. |
| S_t | Normalized current RAN state at time t. Candidate fields include cell state, PRB utilization, UE count, throughput, delay, traffic distribution, radio-quality indicators, and power or energy measurements. The final field set is TBD after audit. |
| C_cap | Audited capability and Job Catalog: supported target types, parameters, executors, preconditions, completion evidence, and recovery behavior. |
| A_t | Active-intent state: intent constraints, plan reservations, execution history, and current fulfillment reports. |
| M_j | Versioned effect model for job j, including calibrated predicted effects and uncertainty where measurements permit. |

### Output parameters

| Output | Description |
|---|---|
| ExecutionPlan | Ordered, concrete plan containing executor bindings, targets, parameters, guards, success conditions, timeouts, and recovery actions. |
| FeasibilityReport | Predicted intermediate states, constraint checks, rejected paths, uncertainty information, and selection rationale. |
| ConflictReport | Involved intents and plans, conflict class, affected resources or KPIs, evidence, severity, and candidate responses. |
| AssuranceDecision | Continue, retry, compensate, rollback, replan, defer, reject, escalate, or report fulfillment. |
| IntentFulfillmentReport | Separate observed fulfillment results for ES and Slice QoS/SLA intents. |

### Proposed control modules

1. Intent Intake and Active Intent Registry
2. Capability and Execution-Level Graph
3. Graph Planner and Control Logic Synthesis
4. Step-Wise Feasibility and Effect Prediction
5. Conflict Admission and Multi-Objective Resolution
6. Job Controller and Executor Adapters
7. Intent Assurance and Drift Manager

### System block diagram

~~~mermaid
flowchart LR
    U[Human Request] --> K[Kenny's NLP-to-YAML Intent Flow]
    K --> R[RMIO and Intent Registry]
    R --> AIR[Active Intent Registry]

    T[VIAVI AI RSG / OSC Testbed] --> TEL[Telemetry Collection and State Normalization]
    TEL --> S[RAN State Store]

    C[Audited Capability and Job Catalog] --> G[Execution-Level Graph]
    AIR --> G
    S --> G

    G --> P[Graph Planner]
    P --> CLS[Control Logic Synthesis]
    CLS --> F[Step-Wise Feasibility and Effect Prediction]
    S --> F
    AIR --> F

    F --> CA[Conflict Admission and Multi-Objective Resolution]
    CA -->|admitted plan| JC[Job Controller]
    CA -->|infeasible or unresolved| RR[ConflictReport / Alternatives to RMIO]
    JC --> EX[Registered rApp, xApp, or SMO Executor]
    EX --> T

    T --> OBS[Observed State]
    OBS --> AM[Intent Assurance and Drift Manager]
    F --> AM
    AIR --> AM
    AM -->|continue / retry / rollback / replan| JC
    AM --> FR[IntentFulfillmentReport and AssuranceDecision]
~~~

---

## A3. Expected Deliverables and Validation

### Deliverables

1. Capability-audit report covering selected ES and Slice-related controls, telemetry, success evidence, and recovery support.
2. YAML-compatible intent contracts for the scoped ES and Slice QoS/SLA use cases.
3. Execution-level graph, Job Catalog, and planning-time annotation schema.
4. Graph Planner, Control Logic Synthesis, step-wise feasibility evaluator, and testbed-calibrated effect model for audited operations.
5. Conflict Admission and multi-objective resolution module for two concurrently active intent instances.
6. Assurance module that identifies execution/configuration drift, outcome/model drift, and environment drift.
7. Reproducible experimental scenarios, logs, metrics, and a final prototype evaluation.

### Validation environment

- Controlled O-RAN testbed based on available OSC and VIAVI AI RSG components.
- Existing RMIO and Intent Specification Registry reused as the upstream intent-entry path.
- Registered control operations selected only after capability audit.
- RAN state assembled from available telemetry sources. The exact endpoints, fields, sampling periods, and time-alignment procedure are TBD.
- Energy baseline defined before experiments using either comparable pre/post observation windows, a no-action control run, or a documented telemetry-derived model.

### Experiment Scenario 1: Alternative ES Path Planning and Feasibility

**Design:** For the same ES intent and authorized RAN scope, construct at least two genuinely different candidate execution paths after the capability audit. Paths may differ by control sequence, operation type, target selection, or parameterization. Test low-load, boundary-load, and infeasible-load conditions where supported by the testbed.

**Baselines:**

- B0: one fixed predefined ES workflow;
- B1: graph-based candidate generation with only static or initial-state checks;
- B2: proposed graph planning with concrete binding and step-wise feasibility validation.

**Metrics:**

- number of generated and concretely bindable paths;
- planning and binding latency;
- unsafe-plan acceptance rate;
- false-rejection rate, where ground truth is available;
- achieved or estimated energy reduction;
- QoS/SLA constraint satisfaction;
- explanation completeness for accepted and rejected plans.

**Purpose:** Determine whether step-wise concrete validation rejects paths that appear plausible from graph structure or initial state alone but become unsafe at an intermediate step.

### Experiment Scenario 2: ES-Slice Intent Conflict Admission

**Design:** Admit an ES intent, retain it as active, then submit a separate Slice QoS/SLA intent with an overlapping resource domain or coupled KPI condition. Test at least one direct/resource conflict and one indirect-KPI conflict, subject to audited testbed capability.

**Baselines:**

- C0: sequential execution using only the latest observed state, without checking active-intent constraints;
- C1: resource-overlap detection only;
- C2: proposed conflict admission using concrete plans, active constraints, predicted KPI effects, and multi-objective candidate selection.

**Metrics:**

- detection coverage and detection latency for controlled conflict cases;
- first-conflicting-step localization accuracy;
- protected constraint violation rate;
- admitted intent utility or reported Pareto alternatives;
- energy reduction retained after resolution;
- Slice QoS/SLA fulfillment;
- resolution and replanning latency;
- rate of correct infeasible-plan rejection.

**Purpose:** Determine whether the system can avoid admitting a later plan that threatens an active independent intent, while retaining feasible energy-saving opportunities.

### Experiment Scenario 3: Intent Drift Assurance and Recovery

**Design:** Create controlled cases representing:

1. execution/configuration drift: command acknowledgement or request completion does not match observed configuration state;
2. outcome/model drift: observed energy or KPI effect lies outside the predicted effect or uncertainty range;
3. environment drift: external traffic or radio-condition changes make a previously fulfilled intent unsatisfied.

The final method used to induce each case is TBD after capability audit and testbed safety review.

**Baselines:**

- D0: execution monitoring without post-action intent assurance;
- D1: assurance that checks only final intent status;
- D2: proposed step-level assurance with drift classification and recovery decisions.

**Metrics:**

- drift detection coverage;
- detection delay;
- false-alarm rate;
- recovery success rate;
- rollback or replanning completion time;
- time until both active intents are again fulfilled, or correct reporting of infeasibility;
- repeated-action or oscillation rate.

**Purpose:** Determine whether assurance can detect and safely respond to the three scoped drift causes rather than merely reporting an end-of-run failure.

---

## A4. Cross-Validation

| Validation Question | Analysis | Provisional Conclusion |
|---|---|---|
| Can the proposed contributions address the identified challenges? | The execution-level graph and synthesis process address the gap between a high-level intent and an executable control sequence. Step-wise feasibility addresses the fact that a plan may become unsafe between its initial and final states. Active-intent-aware admission addresses ES-Slice conflict before actuation. Intended-predicted-observed comparison addresses the three defined drift classes after actuation. | Yes, provided that the capability audit confirms at least two executable ES paths, observable state evidence, and one independent Slice QoS/SLA use case. |
| Do the planned experiments provide sufficient evidence that the method solves the problem? | The three scenarios test planning, conflict admission, and drift recovery separately, with baselines that remove alternative-path reasoning, active-intent checks, or step-level assurance. The metrics measure both control decisions and network/intent outcomes. However, the experiments validate only the selected operations and controlled testbed conditions. | Partially. The evaluation can support a bounded prototype claim, but cannot establish universal O-RAN conformance, general conflict management across arbitrary intents, or hardware-independent energy savings. |

---

## Scope and Explicit Non-Claims

- The thesis does not evaluate natural-language understanding or train a new foundation model.
- The thesis does not claim support for arbitrary intent types, unrestricted multi-intent negotiation, or operator-scale numbers of simultaneous intents.
- The thesis does not replace a Near-RT RIC xApp Conflict Mitigation Function. It focuses on intent and plan admission at the SMO / Non-RT RIC timescale.
- The thesis does not claim a universal power model. Any prediction model is constrained to audited controls, measured telemetry, and the selected testbed.
- A multi-objective solver may identify non-dominated plans, but it must not fabricate operator preferences. Where no authorized preference is available, the system returns alternatives or escalates the decision.

---

## Initial References

1. A. Clemm et al., Intent-Based Networking - Concepts and Definitions, RFC 9315, 2022.
2. O-RAN ALLIANCE, SMO Intent Management Technical Report and related specifications.
3. Y. Wang et al., Network Intent Decomposition and Optimization for Energy-Aware Radio Access Network, IEEE Transactions on Vehicular Technology, 2026.
4. K. Dzeparoska, A. Tizghadam, and A. Leon-Garcia, Emergence: An Intent Fulfillment System, IEEE Communications Magazine, 2024.
5. F. de Souza Almeida et al., A Survey and an Analysis of Conflict Management in O-RAN, IEEE Open Journal of the Communications Society, 2026.
6. G. Z. Bruno et al., Towards Energy- and QoS-aware Load Balancing for 5G Advanced: Leveraging O-RAN to Achieve Sustainability and Energy Efficiency, arXiv preprint, 2026.
