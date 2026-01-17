# Implementation Plan: DLS Consensus TLA+ Specification

## Tech Stack

- **Language**: TLA+ (pure, no PlusCal)
- **Tools**: TLC model checker, TLAPS (TLA+ Proof System) for verification
- **File Format**: `.tla` files with standard TLA+ module structure

## Architecture

### Module Structure

```
specs/001-dls-consensus-tla/
├── tla/
│   ├── DLSConsensus.tla          # Main consensus protocol
│   ├── PartialSynchrony.tla      # Partial synchrony model
│   ├── Properties.tla             # Safety & liveness properties
│   ├── FailStop.tla              # Fail-stop failure model
│   └── README.md                 # Documentation for TLA+ specs
└── docs/
    └── algorithm-explanation.md   # Detailed algorithm explanation
```

### Core Modules

#### 1. DLSConsensus.tla
**Purpose**: Main specification of the DLS consensus algorithm

**Key Components**:
- Constants: `N` (number of processes), `f` (max failures), `Values` (possible values)
- Variables: `state` (process states), `round` (current round), `proposal` (proposed values), `decision` (decided values), `msgs` (message buffer)
- Initial state predicate
- Next-state relation (protocol steps)
- Round progression logic
- Message send/receive actions
- Decision logic

**State Machine**:
```
PROPOSE → VOTE → DECIDE
```

#### 2. PartialSynchrony.tla
**Purpose**: Model partial synchrony assumptions

**Key Components**:
- GST (Global Stabilization Time) - unknown time after which synchrony holds
- Message delay bounds (Φ)
- Process speed bounds (φ)
- Timing predicates for "after GST"

#### 3. Properties.tla  
**Purpose**: Specification of correctness properties

**Properties**:
- **Safety**:
  - Agreement: `∀ p, q ∈ Correct: decided[p] = decided[q]`
  - Validity: `∀ p: decided[p] ∈ initial_values`
  - Integrity: Processes decide at most once
  
- **Liveness**:
  - Termination: `◇(∀ p ∈ Correct: decided[p] ≠ ⊥)` (under synchrony)

#### 4. FailStop.tla
**Purpose**: Fail-stop failure model

**Components**:
- Crashed process set
- Failure detection (perfect in fail-stop)
- Process failure actions

## Implementation Strategy

### Phase 1: Core Infrastructure (Setup)
1. Create directory structure
2. Set up TLA+ module templates
3. Create basic README documentation

### Phase 2: Basic Consensus Specification
1. Define constants and variables in DLSConsensus.tla
2. Specify initial state
3. Implement basic round structure
4. Add message passing primitives

### Phase 3: Protocol Logic
1. Implement proposal phase
2. Implement voting/locking phase  
3. Implement decision phase
4. Add coordinator rotation (if applicable)

### Phase 4: Partial Synchrony Model
1. Create PartialSynchrony.tla with timing model
2. Define GST and bounds
3. Link timing to consensus module

### Phase 5: Failure Models
1. Implement FailStop.tla
2. Integrate failure model with main consensus

### Phase 6: Properties & Verification
1. Define safety properties in Properties.tla
2. Define liveness properties
3. Create simple TLC model configs
4. Document assumptions and invariants

### Phase 7: Documentation
1. Write algorithm explanation
2. Document TLA+ modules
3. Provide examples and usage

## File Structure

### TLA+ Files

Each `.tla` file follows standard module structure:
```tla
---- MODULE ModuleName ----
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS ...
VARIABLES ...

Init == ...
Next == ...

Spec == Init ∧ □[Next]_vars

====
```

### Documentation

- `README.md`: Overview, usage instructions, model checking guidance
- `algorithm-explanation.md`: Detailed explanation of DLS algorithm, partial synchrony, and how it's modeled

## Testing & Validation

### Model Checking with TLC
- Create small model instances (N=3, f=1)
- Check safety properties don't fail
- Verify liveness under synchrony assumptions
- Test with different failure scenarios

### Verification Considerations
- TLC can check finite instances
- Properties should be stated clearly
- Document any assumptions or limitations

## Dependencies

- TLA+ Toolbox (includes TLC model checker)
- Or: Command-line TLA+ tools (java-based)

No external libraries needed - pure TLA+ specification

## Key Design Decisions

1. **Pure TLA+ (No PlusCal)**: Specification directly in TLA+ for clarity and control
2. **Modular Structure**: Separate modules for consensus, synchrony, and properties
3. **Fail-Stop First**: Start with simpler failure model, extensible to omission/Byzantine
4. **Round-Based Protocol**: Follow DLS paper's round structure
5. **Explicit GST Modeling**: Model partial synchrony with explicit GST concept

## Success Criteria

- All `.tla` files parse without errors in TLA+ Toolbox
- Basic safety properties can be checked with TLC
- Code is well-documented with comments
- README provides clear usage instructions
- Algorithm explanation matches DLS paper concepts

## Non-Goals (Out of Scope)

- Formal proofs with TLAPS (can be added later)
- Omission and Byzantine models (optional, focus on fail-stop first)
- Optimized TLC performance tuning
- Implementation in programming languages
