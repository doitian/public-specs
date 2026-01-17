------------------------ MODULE PartialSynchrony ------------------------
(***************************************************************************
 * Partial Synchrony Model for DLS Consensus
 * 
 * Models the timing assumptions from "Consensus in the Presence of
 * Partial Synchrony" (DLS 1988).
 *
 * Partial synchrony means:
 * - Message delays and process speeds have bounds Φ and φ
 * - These bounds hold only after some Global Stabilization Time (GST)
 * - GST is unknown to the processes
 ***************************************************************************)

EXTENDS Naturals

-----------------------------------------------------------------------------
(* Constants *)

CONSTANTS
    GST,    \* Global Stabilization Time (unknown to processes)
    Phi,    \* Message delay bound (after GST)
    Psi     \* Process speed bound (after GST)

ASSUME GST \in Nat
ASSUME Phi \in Nat /\ Phi > 0
ASSUME Psi \in Nat /\ Psi > 0

-----------------------------------------------------------------------------
(* Variables *)

VARIABLES
    time    \* Global time (for modeling purposes, not accessible to processes)

-----------------------------------------------------------------------------
(* Timing Predicates *)

(* System is synchronous (after GST) *)
IsSynchronous == time >= GST

(* System is asynchronous (before GST) *)
IsAsynchronous == time < GST

(* Message delay is bounded after GST *)
MessageDelayBounded(delay) ==
    IsSynchronous => delay <= Phi

(* Process speed is bounded after GST *)  
ProcessSpeedBounded(steps) ==
    IsSynchronous => steps <= Psi

-----------------------------------------------------------------------------
(* Time Advance *)

(* Time can always advance *)
TimeAdvance ==
    time' = time + 1

-----------------------------------------------------------------------------
(* Initial State *)

Init ==
    time = 0

-----------------------------------------------------------------------------
(* Specification Notes *)

(*
 * In the main consensus specification:
 * 
 * 1. Before GST (asynchronous period):
 *    - Messages can be arbitrarily delayed
 *    - Processes may take arbitrarily long between steps
 *    - No liveness guarantees
 *
 * 2. After GST (synchronous period):
 *    - Messages delivered within Phi time units
 *    - Processes take steps within Psi time units
 *    - Liveness (termination) is guaranteed
 *
 * The consensus protocol must maintain SAFETY at all times,
 * but LIVENESS is only guaranteed after GST.
 *
 * In practice, this is modeled through fairness assumptions:
 * - Weak fairness ensures messages are eventually delivered
 * - Strong fairness ensures rounds eventually make progress
 *)

=============================================================================
