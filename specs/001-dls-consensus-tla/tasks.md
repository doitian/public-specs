# Implementation Tasks: DLS Consensus TLA+ Specification

## Phase 1: Setup and Infrastructure

### Task 1.1: Create Directory Structure [P] ✅
**ID**: SETUP-01  
**Files**: Directory structure  
**Description**: Create the directory structure for TLA+ specifications and documentation
**Dependencies**: None

- [X] Create `tla/` directory
- [X] Create `docs/` directory

### Task 1.2: Create README Template [P] ✅
**ID**: SETUP-02  
**Files**: `tla/README.md`  
**Description**: Create initial README with project overview and usage instructions
**Dependencies**: SETUP-01

## Phase 2: Basic Consensus Specification

### Task 2.1: Create DLSConsensus Module Structure ✅
**ID**: CORE-01  
**Files**: `tla/DLSConsensus.tla`  
**Description**: Create the main consensus module with basic structure, constants, and variables

- [X] Define module header with EXTENDS
- [X] Define constants (N, f, Values)
- [X] Define variables (state, round, proposal, decision, msgs)
- [X] Add TypeOK invariant for variable types

**Dependencies**: SETUP-01

### Task 2.2: Implement Initial State ✅
**ID**: CORE-02  
**Files**: `tla/DLSConsensus.tla`  
**Description**: Define the Init predicate for initial system state

- [X] All processes in initial state
- [X] Round 0
- [X] No messages
- [X] No decisions yet

**Dependencies**: CORE-01

### Task 2.3: Implement Message Passing Primitives ✅
**ID**: CORE-03  
**Files**: `tla/DLSConsensus.tla`  
**Description**: Define message sending and receiving actions

- [X] SendMsg action
- [X] ReceiveMsg action
- [X] Message types (PROPOSAL, VOTE, DECISION)

**Dependencies**: CORE-02

## Phase 3: Protocol Logic

### Task 3.1: Implement Proposal Phase ✅
**ID**: PROTO-01  
**Files**: `tla/DLSConsensus.tla`  
**Description**: Implement proposal phase where processes propose values

- [X] Coordinator selection logic
- [X] Proposal broadcast
- [X] State transition to VOTE

**Dependencies**: CORE-03

### Task 3.2: Implement Voting Phase ✅
**ID**: PROTO-02  
**Files**: `tla/DLSConsensus.tla`  
**Description**: Implement voting/locking phase

- [X] Receive proposals
- [X] Vote for proposals
- [X] Collect votes (threshold logic)
- [X] Lock on value if threshold met

**Dependencies**: PROTO-01

### Task 3.3: Implement Decision Phase ✅
**ID**: PROTO-03  
**Files**: `tla/DLSConsensus.tla`  
**Description**: Implement decision logic

- [X] Decision condition (received enough locks)
- [X] Broadcast decision
- [X] Update decision variable
- [X] State transition to DECIDED

**Dependencies**: PROTO-02

### Task 3.4: Implement Round Progression ✅
**ID**: PROTO-04  
**Files**: `tla/DLSConsensus.tla`  
**Description**: Implement round advancement and timeout logic

- [X] Timeout action
- [X] Round increment
- [X] Reset per-round state
- [X] Coordinator rotation

**Dependencies**: PROTO-02

### Task 3.5: Complete Next-State Relation ✅
**ID**: PROTO-05  
**Files**: `tla/DLSConsensus.tla`  
**Description**: Combine all actions into Next predicate and define Spec

- [X] Next == PROPOSE ∨ VOTE ∨ DECIDE ∨ TIMEOUT ∨ RECEIVE
- [X] Spec == Init ∧ □[Next]_vars
- [X] Fairness conditions

**Dependencies**: PROTO-01, PROTO-02, PROTO-03, PROTO-04

## Phase 4: Partial Synchrony Model

### Task 4.1: Create PartialSynchrony Module ✅
**ID**: SYNC-01  
**Files**: `tla/PartialSynchrony.tla`  
**Description**: Create module for partial synchrony assumptions

- [X] Define GST (Global Stabilization Time)
- [X] Define message delay bound Φ
- [X] Define process speed bound φ
- [X] Predicate for "after GST"

**Dependencies**: SETUP-01

### Task 4.2: Integrate Synchrony Model ✅
**ID**: SYNC-02  
**Files**: `tla/DLSConsensus.tla`  
**Description**: Link partial synchrony to consensus module

- [X] Import PartialSynchrony module
- [X] Use timing predicates in liveness properties
- [X] Document synchrony assumptions in comments

**Dependencies**: SYNC-01, PROTO-05

## Phase 5: Failure Models

### Task 5.1: Create FailStop Module ✅
**ID**: FAIL-01  
**Files**: `tla/FailStop.tla`  
**Description**: Implement fail-stop failure model

- [X] Define Crashed variable (set of crashed processes)
- [X] Crash action
- [X] Constraints: |Crashed| ≤ f
- [X] Perfect failure detection (crashed processes don't send)

**Dependencies**: SETUP-01

### Task 5.2: Integrate FailStop with Consensus ✅
**ID**: FAIL-02  
**Files**: `tla/DLSConsensus.tla`  
**Description**: Integrate failure model into main consensus

- [X] Import FailStop module
- [X] Guard actions with "not crashed" condition
- [X] Update Next to include Crash action
- [X] Define Correct == Processes \ Crashed

**Dependencies**: FAIL-01, PROTO-05

## Phase 6: Properties and Verification

### Task 6.1: Create Properties Module ✅
**ID**: PROP-01  
**Files**: `tla/Properties.tla`  
**Description**: Define correctness properties

- [X] Agreement property
- [X] Validity property
- [X] Integrity property
- [X] Termination property (liveness)

**Dependencies**: FAIL-02, SYNC-02

### Task 6.2: Create TLC Model Config ✅
**ID**: PROP-02  
**Files**: `tla/DLSConsensus.cfg`, `tla/MC.tla` (optional)  
**Description**: Create TLC model checker configuration

- [X] Define constant values (N=3, f=1, Values={0,1})
- [X] Specify properties to check
- [X] Set state constraints if needed
- [X] Add invariants

**Dependencies**: PROP-01

### Task 6.3: Document Invariants and Assumptions ✅
**ID**: PROP-03  
**Files**: `tla/DLSConsensus.tla`  
**Description**: Add comprehensive comments documenting invariants and assumptions

- [X] Safety invariants
- [X] Timing assumptions
- [X] Failure assumptions
- [X] Protocol invariants

**Dependencies**: PROP-01

## Phase 7: Documentation

### Task 7.1: Complete README [P] ✅
**ID**: DOC-01  
**Files**: `tla/README.md`  
**Description**: Complete README with full documentation

- [X] Overview of DLS algorithm
- [X] File structure explanation
- [X] How to run TLC model checker
- [X] Explanation of constants and properties
- [X] Known limitations

**Dependencies**: PROP-02

### Task 7.2: Create Algorithm Explanation [P] ✅
**ID**: DOC-02  
**Files**: `docs/algorithm-explanation.md`  
**Description**: Write detailed explanation of DLS algorithm and modeling choices

- [X] DLS algorithm overview
- [X] Partial synchrony explained
- [X] Round structure
- [X] How failure model works
- [X] Safety and liveness guarantees
- [X] Mapping from paper to TLA+ spec

**Dependencies**: PROP-01

## Execution Order

### Sequential Dependencies
1. SETUP-01 → SETUP-02, CORE-01
2. CORE-01 → CORE-02
3. CORE-02 → CORE-03
4. CORE-03 → PROTO-01
5. PROTO-01 → PROTO-02
6. PROTO-02 → PROTO-03, PROTO-04
7. PROTO-01, PROTO-02, PROTO-03, PROTO-04 → PROTO-05
8. PROTO-05 → SYNC-02, FAIL-02
9. SYNC-01 → SYNC-02
10. FAIL-01 → FAIL-02
11. FAIL-02, SYNC-02 → PROP-01
12. PROP-01 → PROP-02, PROP-03, DOC-02
13. PROP-02 → DOC-01

### Parallel Tasks [P]
- SETUP-01 and SETUP-02 can run in parallel (different files)
- SYNC-01 and FAIL-01 can run in parallel (different files)
- DOC-01 and DOC-02 can run in parallel (different files)

## Notes

- TLA+ syntax must be precise - test each module as it's created
- Focus on fail-stop model first; omission and Byzantine can be added later
- Keep specifications readable with good comments
- Small model instances for TLC (N=3, f=1) to keep checking fast
- Document any deviations from the original paper
