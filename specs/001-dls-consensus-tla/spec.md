# DLS Consensus Algorithm TLA+ Specification

## Overview

Create TLA+ specifications for the DLS (Dwork-Lynch-Stockmeyer) Consensus algorithm from the 1988 JACM paper "Consensus in the Presence of Partial Synchrony" without using PlusCal.

## Background

The DLS paper introduces the concept of "partial synchrony" - a model that lies between fully synchronous and fully asynchronous distributed systems. The paper provides several consensus algorithms for different failure models:

- Fail-stop faults
- Omission faults  
- Byzantine faults (authenticated and unauthenticated)

## Objectives

1. Create TLA+ specifications for the DLS consensus protocols using pure TLA+ (no PlusCal)
2. Model the partial synchrony assumptions
3. Specify safety and liveness properties
4. Include specifications for different failure models

## Requirements

### Core Specifications

1. **DLSConsensus.tla** - Main consensus protocol specification
   - Process states and message passing
   - Round-based protocol structure
   - Value proposal and decision logic

2. **PartialSynchrony.tla** - Partial synchrony model
   - Time bounds (unknown but fixed OR exist after GST)
   - Message delay assumptions
   - Process speed assumptions

3. **Properties.tla** - Safety and liveness properties
   - Agreement: All non-faulty processes decide on the same value
   - Validity: If all processes start with same value v, then v is the decided value
   - Termination: All non-faulty processes eventually decide (under synchrony)

### Failure Models

1. **FailStop.tla** - Fail-stop fault specification
2. **Omission.tla** - Omission fault specification (optional)
3. **Byzantine.tla** - Byzantine fault specification (optional, authenticated case)

## Success Criteria

- TLA+ specifications are syntactically valid
- Can be checked with TLC model checker
- Clearly document partial synchrony assumptions
- Safety properties are always maintained
- Liveness properties hold under synchrony assumptions

## References

- Paper: https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf
- "Consensus in the Presence of Partial Synchrony" by Dwork, Lynch, and Stockmeyer (JACM 1988)
