# DLS Consensus Algorithm - Detailed Explanation

## Overview

The DLS (Dwork-Lynch-Stockmeyer) Consensus algorithm, presented in the seminal 1988 JACM paper "Consensus in the Presence of Partial Synchrony," is one of the most influential results in distributed computing. It shows how to achieve consensus in realistic distributed systems that are neither fully synchronous nor fully asynchronous.

## The Consensus Problem

### Goal

A set of distributed processes must agree on a single value, despite:
- Some processes may fail
- Communication may be unreliable or delayed
- No process has a global view of the system

### Requirements

A consensus protocol must satisfy three properties:

1. **Agreement**: No two correct processes decide on different values
2. **Validity**: Any decided value was proposed by some process
3. **Termination**: All correct processes eventually decide

## Why Partial Synchrony?

### The FLP Impossibility

In 1985, Fischer, Lynch, and Paterson proved that consensus is **impossible** in a purely asynchronous system if even one process can fail. This is known as the FLP impossibility result.

### The DLS Breakthrough

DLS circumvents FLP by introducing **partial synchrony** - a realistic middle ground between:
- **Fully synchronous**: Known fixed bounds on message delays and process speeds
- **Fully asynchronous**: No bounds whatsoever (where FLP applies)

### Partial Synchrony Model

DLS defines two variants of partial synchrony:

**Variant 1**: Unknown Bounds
- Message delays and process speeds have fixed bounds Φ and φ
- But these bounds are **unknown** to the processes

**Variant 2**: Eventually Synchronous (modeled in our spec)
- There exists a **Global Stabilization Time (GST)**
- After GST, message delays ≤ Φ and process speeds ≤ φ
- Before GST, no bounds (arbitrary delays)
- **GST is unknown** to the processes

This models real systems: networks are sometimes slow, sometimes fast, but eventually stabilize.

## Algorithm Structure

### Round-Based Protocol

The DLS algorithm operates in rounds:

```
Round r:
  1. PROPOSE: Coordinator proposes a value
  2. VOTE: Processes vote on the proposal
  3. DECIDE: If enough votes, decide; else advance to round r+1
```

### Key Mechanisms

#### 1. Coordinator Selection

Each round has a designated coordinator (round-robin):
```
Coordinator(r) = ((r - 1) mod N) + 1
```

This ensures that eventually a correct process becomes coordinator (after at most f rounds where coordinators crash).

#### 2. Value Locking

Processes can **lock** on a value when they see a quorum (majority) of votes:
- Once locked, prefer the locked value in future rounds
- But can change lock to a newer value if seen in a later round
- Ensures safety through quorum intersection

#### 3. Quorum Requirement

A quorum is a majority: Q = ⌈N/2⌉ + 1

**Quorum Intersection Property**: Any two quorums must overlap in at least one process. If f < N/2, they overlap in at least one **correct** process.

This is crucial for Agreement - prevents conflicting decisions.

### Protocol Flow

```
Process p in round r:

IF p is coordinator of round r:
    - Propose locked value if locked, else any value
    - Broadcast PROPOSAL

IF receive PROPOSAL from coordinator:
    - If not locked, or proposal matches lock, or round > lock round:
        * Send VOTE for the proposed value
        * Lock on the value if see quorum of votes

IF locked on value v and see quorum of votes for v:
    - DECIDE v
    - Broadcast DECISION
    - Terminate

IF receive DECISION message:
    - Adopt the decision
    - Terminate

IF timeout (no quorum):
    - Advance to round r+1
```

## Safety Proof Sketch

### Agreement

**Claim**: No two correct processes decide on different values.

**Sketch**:
1. A process only decides if it's locked on a value v with quorum votes
2. If two processes decide in the same round, their quorums intersect → same value
3. If processes decide in different rounds r < r':
   - The lock in round r had a quorum
   - Any quorum in round r' intersects the round r quorum
   - So at least one process in round r' was locked from round r
   - The coordinator in round r' either:
     * Proposes the same value (if locked), OR
     * Doesn't get a quorum (if processes stay locked on different value)
4. Therefore, all decisions agree

### Validity

**Claim**: Any decided value was proposed by some process.

**Sketch**: Values only come from initial proposals or locked values, which trace back to initial proposals.

### Integrity

**Claim**: Each process decides at most once.

**Sketch**: Once decided, a process terminates (or we track decisions immutably).

## Liveness Under Synchrony

### Termination Guarantee

**After GST** (in synchronous period):

1. **Message delivery**: All messages delivered within Φ time
2. **Process steps**: All processes take steps within φ time
3. **Round duration**: Bounded - processes synchronize rounds
4. **Correct coordinator**: Within f+1 rounds, a correct process is coordinator
5. **Quorum collection**: Correct coordinator collects quorum in its round
6. **Decision**: All correct processes decide

### Why Not Before GST?

Before GST (asynchronous period):
- Messages can be arbitrarily delayed
- Processes may time out prematurely
- Coordinators may appear to have failed when they haven't
- No guarantee of progress

But **safety is always maintained** - no disagreement can occur.

## Failure Model: Fail-Stop

### Characteristics

- **Crash failures**: Process stops executing
- **Permanent**: No recovery
- **Detectable**: Eventually detected by all (perfect failure detection)
- **Bounded**: At most f < N/2 failures

### Why f < N/2?

Need quorum intersection:
- Quorum size: Q = ⌊N/2⌋ + 1
- If f < N/2, then: N - f > N/2
- So correct processes always form a quorum
- And any two quorums share a correct process

## TLA+ Modeling Choices

### Variables

- `state[p]`: Current phase (PROPOSE, VOTING, DECIDED)
- `round[p]`: Current round number
- `locked[p]`: Value locked on (or ⊥)
- `lockedRound[p]`: Round of lock
- `decision[p]`: Final decision (or ⊥)
- `msgs`: Set of messages in transit
- `crashed`: Set of crashed processes

### Key Design Decisions

1. **Message passing**: Explicit message set (not channels)
   - Simpler for TLC to model check
   - Messages persist until relevant

2. **Asynchronous steps**: Each process acts independently
   - No synchronized rounds in execution
   - Round numbers are logical, not global clock

3. **Fairness**: 
   - Weak fairness: Enabled actions eventually happen
   - Strong fairness: AdvanceRound (models timeouts)
   - Represents eventual synchrony without explicit time

4. **GST modeling**: Implicit through fairness
   - Not explicitly modeled as a time variable
   - Fairness ensures eventual progress (as if after GST)

5. **Simplified features**:
   - No explicit timers or clocks
   - No message loss (fail-stop assumes reliable delivery)
   - Abstract value selection (CHOOSE)

### Verification with TLC

**Model parameters**:
- N = 3 processes
- f = 1 maximum failure
- Values = {0, 1}
- Round limit = 5 (state constraint)

**What TLC checks**:
- Safety: Agreement, Validity (as invariants)
- Liveness: Termination (as temporal property)
- TypeOK: Variable types remain consistent

**Limitations**:
- Small state space (N=3)
- Bounded rounds
- Finite execution traces
- Doesn't prove general case (would need TLAPS)

## Comparison to Other Protocols

### Paxos
- DLS provides the theoretical foundation
- Paxos is optimized for practical use
- Both use rounds, quorums, and value locking

### Raft
- Raft builds on DLS/Paxos ideas
- Adds leader election and log replication
- More implementation-focused

### PBFT (Practical Byzantine Fault Tolerance)
- Extends to Byzantine failures
- DLS also has Byzantine variant (not in our spec)
- Uses digital signatures for authentication

## Key Insights

1. **Partial synchrony is realistic**: Most systems are eventually synchronous
2. **Safety always, liveness eventually**: Strong separation of concerns
3. **Quorum intersection**: Fundamental technique for distributed agreement
4. **Round-based structure**: Simplifies reasoning and implementation
5. **Value locking**: Prevents conflicting decisions across rounds

## References

- **Original Paper**: "Consensus in the Presence of Partial Synchrony"
  - C. Dwork, N. Lynch, L. Stockmeyer
  - Journal of the ACM, Vol. 35, No. 2, April 1988
  - https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf

- **Related Work**:
  - FLP impossibility: Fischer, Lynch, Paterson (1985)
  - Paxos: Lamport (1998)
  - Chandra-Toueg failure detectors (1996)

## Further Reading

- Leslie Lamport, "Paxos Made Simple"
- Nancy Lynch, "Distributed Algorithms" (textbook)
- Rachid Guerraoui & Luís Rodrigues, "Introduction to Reliable Distributed Programming"
