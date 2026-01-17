# DLS Consensus Algorithm - TLA+ Specification

## Overview

This directory contains TLA+ specifications for the DLS (Dwork-Lynch-Stockmeyer) Consensus algorithm from the 1988 JACM paper "Consensus in the Presence of Partial Synchrony."

The specifications are written in pure TLA+ (without PlusCal) and model the consensus protocol under partial synchrony assumptions with fail-stop failures.

## Files

- **DLSConsensus.tla** - Main consensus protocol specification
- **PartialSynchrony.tla** - Partial synchrony model (GST, message/process bounds)
- **Properties.tla** - Safety and liveness properties
- **FailStop.tla** - Fail-stop failure model
- **DLSConsensus.cfg** - TLC model checker configuration

## Algorithm Overview

The DLS consensus algorithm solves the consensus problem in partially synchronous systems where:
- Up to `f` processes may fail (fail-stop)
- The system is eventually synchronous (after unknown GST - Global Stabilization Time)
- Message delays and process speeds have bounds that hold after GST

The protocol ensures:
- **Agreement**: All correct processes decide on the same value
- **Validity**: The decided value was proposed by some process
- **Termination**: All correct processes eventually decide (under synchrony)

## Model Checking with TLC

### Prerequisites

- TLA+ Toolbox (download from: https://lamport.azurewebsites.net/tla/toolbox.html)
- Or command-line TLA+ tools

### Running the Model Checker

1. Open TLA+ Toolbox
2. Create a new spec, add `DLSConsensus.tla`
3. Create a model with the provided `DLSConsensus.cfg` configuration
4. Run TLC

Or from command line:
```bash
java -cp tla2tools.jar tlc2.TLC -config DLSConsensus.cfg DLSConsensus.tla
```

### Model Parameters

The default model configuration uses:
- **N = 3** processes
- **f = 1** maximum failures  
- **Values = {0, 1}** possible consensus values

These small values keep model checking tractable. Larger values will increase state space exponentially.

## Key Concepts

### Partial Synchrony

The DLS paper introduces two variants of partial synchrony:
1. **Unknown bounds**: Message delays and process speeds have fixed bounds, but they are unknown
2. **Eventually synchronous**: Bounds exist only after some unknown Global Stabilization Time (GST)

Our specification models the second variant with explicit GST.

### Fail-Stop Failures

Processes can crash (stop executing) but:
- Crashed processes are eventually detected by all correct processes
- Crashed processes don't send messages
- At most `f` processes crash where `f < N/2`

### Round Structure

The protocol operates in rounds:
1. **PROPOSE**: Coordinator proposes a value
2. **VOTE**: Processes vote on the proposal
3. **DECIDE**: If enough votes received, decide; otherwise advance round

## Properties Checked

### Safety (Always Hold)
- **Agreement**: No two correct processes decide differently
- **Validity**: Decided values are from the initial value set
- **Integrity**: Each process decides at most once

### Liveness (Eventually Hold)
- **Termination**: All correct processes eventually decide
  - Note: Only guaranteed after GST (under synchrony)

## Limitations and Assumptions

- Finite state space for model checking (small N, bounded rounds)
- Simplified message passing (no explicit network model)
- GST is modeled implicitly through fairness assumptions
- Focus on fail-stop; omission and Byzantine models not included

## References

- Original Paper: "Consensus in the Presence of Partial Synchrony"
  - C. Dwork, N. Lynch, L. Stockmeyer
  - Journal of the ACM, Vol. 35, No. 2, April 1988
  - https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf

## Further Reading

- See `../docs/algorithm-explanation.md` for detailed explanation
- TLA+ documentation: https://lamport.azurewebsites.net/tla/tla.html
- Specifying Systems book: https://lamport.azurewebsites.net/tla/book.html
