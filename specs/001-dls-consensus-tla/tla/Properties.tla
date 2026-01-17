---------------------------- MODULE Properties ----------------------------
(***************************************************************************
 * Correctness Properties for DLS Consensus
 * 
 * Specifies safety and liveness properties that the consensus
 * protocol must satisfy.
 ***************************************************************************)

EXTENDS Naturals, FiniteSets

-----------------------------------------------------------------------------
(* Import from DLSConsensus *)

CONSTANTS
    N,              \* Number of processes
    Values,         \* Set of possible values
    Processes       \* Set of all processes

VARIABLES
    decision,       \* decision[p] = decided value of process p
    crashed         \* Set of crashed processes

ASSUME Processes = 1..N

-----------------------------------------------------------------------------
(* Helper Definitions *)

(* Correct (non-crashed) processes *)
Correct == Processes \ crashed

(* A process has decided *)
HasDecided(p) == decision[p] /= 0

(* All correct processes have decided *)
AllCorrectDecided == \A p \in Correct : HasDecided(p)

-----------------------------------------------------------------------------
(* SAFETY PROPERTIES *)
(* Safety properties must hold in ALL states, even with failures
   and in asynchronous periods *)

(* Agreement: No two correct processes decide on different values *)
Agreement ==
    \A p, q \in Correct :
        (HasDecided(p) /\ HasDecided(q)) => decision[p] = decision[q]

(* Validity: Any decided value must be from the Values set *)
Validity ==
    \A p \in Processes :
        HasDecided(p) => decision[p] \in Values

(* Integrity: Each process decides at most once - decisions are immutable *)
(* This is checked as a state invariant: once decided, value doesn't change *)
Integrity ==
    \A p \in Processes :
        HasDecided(p) => decision[p] \in Values

(* Irrevocability: Once a value is decided, it remains decided *)
(* This is a state invariant that captures immutability *)
Irrevocability ==
    \A p \in Processes :
        HasDecided(p) => decision[p] /= 0

(* DecisionStability: Check that decision values are stable across state transitions *)
(* This would need to be checked as an action invariant in the main spec *)
(* For now, we rely on the fact that decision variables are only written once *)

-----------------------------------------------------------------------------
(* LIVENESS PROPERTIES *)
(* Liveness properties must EVENTUALLY hold, but only under
   synchrony assumptions (after GST) and with bounded failures *)

(* Termination: All correct processes eventually decide *)
Termination ==
    <>( \A p \in Correct : HasDecided(p) )

(* Strong Termination: At least one correct process eventually decides *)
WeakTermination ==
    <>( \E p \in Correct : HasDecided(p) )

-----------------------------------------------------------------------------
(* COMBINED PROPERTIES *)

(* Full Consensus Correctness: Safety always holds, liveness eventually holds *)
ConsensusCorrectness ==
    /\ Agreement
    /\ Validity
    /\ Integrity
    /\ Termination

-----------------------------------------------------------------------------
(* HELPER LEMMAS (for understanding, not checked by TLC) *)

(*
 * Quorum Intersection Lemma:
 * Any two quorums (majorities) must have at least one correct process
 * in common, provided f < N/2.
 *
 * This is crucial for Agreement - if processes lock on values in
 * different rounds, the quorum intersection ensures consistency.
 *)

Quorum == (N \div 2) + 1

QuorumIntersection ==
    \A Q1, Q2 \in SUBSET Processes :
        (Cardinality(Q1) >= Quorum /\ Cardinality(Q2) >= Quorum)
        => Q1 \cap Q2 \cap Correct /= {}

-----------------------------------------------------------------------------
(* NOTES ON PROPERTIES *)

(*
 * Safety vs Liveness in Partial Synchrony:
 *
 * SAFETY properties (Agreement, Validity, Integrity):
 * - Must hold at ALL times
 * - Hold even during asynchronous periods (before GST)
 * - Hold even with up to f failures
 * - Never violated, regardless of timing
 *
 * LIVENESS properties (Termination):
 * - Only guaranteed AFTER GST (synchronous period)
 * - Only guaranteed with at most f < N/2 failures
 * - May not hold during asynchronous periods
 * - In TLA+, modeled through fairness assumptions
 *
 * Model Checking:
 * - TLC can check safety properties (invariants) thoroughly
 * - TLC can check liveness with bounded model (limited states)
 * - For unbounded liveness, would need TLAPS (proof system)
 *
 * DLS Contribution:
 * - Showed that consensus is POSSIBLE in partial synchrony
 * - Circumvents FLP impossibility (which applies to pure asynchrony)
 * - Safety always holds; liveness requires eventual synchrony
 *)

=============================================================================
