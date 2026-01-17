---------------------------- MODULE FailStop ----------------------------
(***************************************************************************
 * Fail-Stop Failure Model for DLS Consensus
 * 
 * Models fail-stop failures where:
 * - Processes can crash (stop executing)
 * - Crashed processes are eventually detected by all correct processes
 * - Crashed processes don't send any more messages
 * - At most f processes crash, where f < N/2
 ***************************************************************************)

EXTENDS Naturals, FiniteSets

-----------------------------------------------------------------------------
(* Constants *)

CONSTANTS
    N,              \* Total number of processes
    f,              \* Maximum number of failures
    Processes       \* Set of all processes

(* Assumption: f < N/2 to ensure quorum intersection *)
ASSUME f \in Nat /\ N \in Nat /\ f < N \div 2

ASSUME Processes = 1..N

-----------------------------------------------------------------------------
(* Variables *)

VARIABLES
    crashed         \* Set of crashed processes

-----------------------------------------------------------------------------
(* Type Invariant *)

TypeOK ==
    /\ crashed \subseteq Processes
    /\ Cardinality(crashed) <= f

-----------------------------------------------------------------------------
(* Initial State *)

Init ==
    crashed = {}    \* Initially, no processes have crashed

-----------------------------------------------------------------------------
(* Failure Actions *)

(* A process can crash *)
Crash(p) ==
    /\ p \in Processes
    /\ p \notin crashed
    /\ Cardinality(crashed) < f
    /\ crashed' = crashed \cup {p}

-----------------------------------------------------------------------------
(* Helper Predicates *)

(* Set of correct (non-crashed) processes *)
Correct == Processes \ crashed

(* Check if a process is correct *)
IsCorrect(p) == p \in Correct

(* Check if enough processes are correct for quorum *)
QuorumExists == Cardinality(Correct) >= (N \div 2) + 1

(* Failure detection: In fail-stop model, crashes are eventually detected *)
(* This is modeled implicitly - crashed processes simply don't take actions *)

-----------------------------------------------------------------------------
(* Invariants *)

(* At most f failures *)
BoundedFailures ==
    Cardinality(crashed) <= f

(* A quorum of correct processes always exists *)
QuorumInvariant ==
    Cardinality(Correct) >= (N \div 2) + 1

-----------------------------------------------------------------------------
(* Notes on Fail-Stop Model *)

(*
 * Properties of Fail-Stop Failures:
 *
 * 1. Clean Crashes: When a process crashes, it stops executing immediately
 *    and permanently. No partial execution or Byzantine behavior.
 *
 * 2. Perfect Failure Detection: All correct processes eventually detect
 *    the crash. In our model, this is implicit - crashed processes simply
 *    don't send messages or take actions.
 *
 * 3. No Recovery: Once crashed, a process never recovers.
 *
 * 4. Bounded Failures: At most f processes crash, where f < N/2.
 *    This ensures that a quorum (majority) of correct processes always exists.
 *
 * 5. Quorum Intersection: Any two quorums must have at least one correct
 *    process in common, which is crucial for consensus safety.
 *
 * Integration with Consensus:
 * - All consensus actions are guarded by "p \notin crashed"
 * - Correct processes form quorums for voting and decisions
 * - Safety holds even with up to f crashes
 * - Liveness (termination) requires synchrony and at most f < N/2 crashes
 *)

=============================================================================
