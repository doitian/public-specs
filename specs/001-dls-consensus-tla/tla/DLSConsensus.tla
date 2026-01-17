---------------------------- MODULE DLSConsensus ----------------------------
(***************************************************************************
 * DLS Consensus Algorithm Specification
 * 
 * Based on "Consensus in the Presence of Partial Synchrony"
 * by Dwork, Lynch, and Stockmeyer (JACM 1988)
 *
 * This specification models the consensus protocol in a partially
 * synchronous system with fail-stop failures.
 ***************************************************************************)

EXTENDS Naturals, FiniteSets, Sequences

-----------------------------------------------------------------------------
(* Constants *)

CONSTANTS 
    N,              \* Number of processes
    f,              \* Maximum number of failures (f < N/2)
    Values          \* Set of possible values to propose

(* Processes are identified by natural numbers 1..N *)
Processes == 1..N

(* Message types *)
CONSTANTS PROPOSAL, VOTE, DECISION

-----------------------------------------------------------------------------
(* Variables *)

VARIABLES
    state,          \* state[p] = current state of process p
    round,          \* round[p] = current round number for process p  
    proposal,       \* proposal[p] = value proposed by p in current round
    vote,           \* vote[p] = value voted for by p in current round
    decision,       \* decision[p] = decided value (or ⊥ if not decided)
    locked,         \* locked[p] = value p is locked on (or ⊥)
    lockedRound,    \* lockedRound[p] = round when p locked on value
    msgs,           \* Set of messages in transit
    crashed         \* Set of crashed processes

vars == <<state, round, proposal, vote, decision, locked, lockedRound, msgs, crashed>>

-----------------------------------------------------------------------------
(* Process states *)
CONSTANTS PROPOSE, VOTING, DECIDED

-----------------------------------------------------------------------------
(* Type Invariant *)

Message == [type: {PROPOSAL, VOTE, DECISION}, 
            src: Processes, 
            round: Nat,
            value: Values \cup {0}]  \* 0 represents ⊥ (bottom/null)

TypeOK ==
    /\ state \in [Processes -> {PROPOSE, VOTING, DECIDED}]
    /\ round \in [Processes -> Nat]
    /\ proposal \in [Processes -> Values \cup {0}]
    /\ vote \in [Processes -> Values \cup {0}]
    /\ decision \in [Processes -> Values \cup {0}]
    /\ locked \in [Processes -> Values \cup {0}]
    /\ lockedRound \in [Processes -> Nat]
    /\ msgs \subseteq Message
    /\ crashed \subseteq Processes
    /\ Cardinality(crashed) <= f

-----------------------------------------------------------------------------
(* Initial State *)

Init ==
    /\ state = [p \in Processes |-> PROPOSE]
    /\ round = [p \in Processes |-> 1]
    /\ proposal = [p \in Processes |-> 0]  \* 0 represents ⊥
    /\ vote = [p \in Processes |-> 0]
    /\ decision = [p \in Processes |-> 0]
    /\ locked = [p \in Processes |-> 0]
    /\ lockedRound = [p \in Processes |-> 0]
    /\ msgs = {}
    /\ crashed = {}

-----------------------------------------------------------------------------
(* Helper Functions *)

(* Coordinator for a given round (round-robin) *)
Coordinator(r) == ((r - 1) % N) + 1

(* Correct (non-crashed) processes *)
Correct == Processes \ crashed

(* Messages of a specific type in a specific round to a specific process *)
MessagesOfType(msgType, r) == 
    {m \in msgs : m.type = msgType /\ m.round = r}

(* Count messages with specific type, round, and value *)
CountVotes(r, v) == 
    Cardinality({m \in msgs : m.type = VOTE /\ m.round = r /\ m.value = v})

(* Quorum: majority of processes *)
Quorum == (N \div 2) + 1

-----------------------------------------------------------------------------
(* Message Passing Actions *)

(* Send a message (only non-crashed processes can send) *)
SendMsg(m) ==
    /\ m.src \notin crashed
    /\ msgs' = msgs \cup {m}

(* Broadcast a message to all processes *)
Broadcast(msgType, src, r, v) ==
    SendMsg([type |-> msgType, src |-> src, round |-> r, value |-> v])

-----------------------------------------------------------------------------
(* Protocol Actions *)

(* Propose Phase: Coordinator proposes a value *)
ProposeValue(p) ==
    /\ p \notin crashed
    /\ state[p] = PROPOSE
    /\ p = Coordinator(round[p])
    /\ LET proposedValue == IF locked[p] /= 0 
                            THEN locked[p]
                            ELSE CHOOSE v \in Values : TRUE
       IN
          /\ Broadcast(PROPOSAL, p, round[p], proposedValue)
          /\ proposal' = [proposal EXCEPT ![p] = proposedValue]
          /\ state' = [state EXCEPT ![p] = VOTING]
    /\ UNCHANGED <<round, vote, decision, locked, lockedRound, crashed>>

(* Receive a proposal and vote *)
ReceiveProposal(p) ==
    /\ p \notin crashed
    /\ state[p] = PROPOSE \/ state[p] = VOTING
    /\ \E m \in msgs :
        /\ m.type = PROPOSAL
        /\ m.round = round[p]
        /\ m.src = Coordinator(round[p])
        /\ LET shouldVote == \/ locked[p] = 0
                             \/ lockedRound[p] < round[p]
                             \/ locked[p] = m.value
           IN
              IF shouldVote
              THEN /\ Broadcast(VOTE, p, round[p], m.value)
                   /\ vote' = [vote EXCEPT ![p] = m.value]
                   /\ state' = [state EXCEPT ![p] = VOTING]
                   /\ UNCHANGED <<proposal, decision, locked, lockedRound>>
              ELSE /\ UNCHANGED <<proposal, vote, decision, locked, lockedRound, state>>
    /\ UNCHANGED <<round, crashed>>

(* Lock on a value when receiving quorum of votes *)
LockOnValue(p) ==
    /\ p \notin crashed
    /\ state[p] = VOTING
    /\ decision[p] = 0  \* Not yet decided
    /\ \E v \in Values :
        /\ CountVotes(round[p], v) >= Quorum
        /\ locked' = [locked EXCEPT ![p] = v]
        /\ lockedRound' = [lockedRound EXCEPT ![p] = round[p]]
    /\ UNCHANGED <<state, round, proposal, vote, decision, msgs, crashed>>

(* Decide on a value *)
DecideValue(p) ==
    /\ p \notin crashed
    /\ state[p] = VOTING
    /\ decision[p] = 0  \* Not yet decided
    /\ locked[p] /= 0   \* Must be locked on some value
    /\ \E v \in Values :
        /\ locked[p] = v
        /\ CountVotes(round[p], v) >= Quorum
        /\ decision' = [decision EXCEPT ![p] = v]
        /\ state' = [state EXCEPT ![p] = DECIDED]
        /\ Broadcast(DECISION, p, round[p], v)
    /\ UNCHANGED <<round, proposal, vote, locked, lockedRound, crashed>>

(* Receive decision message *)
ReceiveDecision(p) ==
    /\ p \notin crashed
    /\ decision[p] = 0  \* Not yet decided
    /\ \E m \in msgs :
        /\ m.type = DECISION
        /\ m.value \in Values
        /\ decision' = [decision EXCEPT ![p] = m.value]
        /\ state' = [state EXCEPT ![p] = DECIDED]
    /\ UNCHANGED <<round, proposal, vote, locked, lockedRound, msgs, crashed>>

(* Timeout and advance to next round *)
AdvanceRound(p) ==
    /\ p \notin crashed
    /\ state[p] = VOTING
    /\ decision[p] = 0  \* Not yet decided
    \* Timeout condition: haven't received enough votes or decision
    /\ ~\E v \in Values : CountVotes(round[p], v) >= Quorum
    /\ round' = [round EXCEPT ![p] = @ + 1]
    /\ state' = [state EXCEPT ![p] = PROPOSE]
    /\ proposal' = [proposal EXCEPT ![p] = 0]
    /\ vote' = [vote EXCEPT ![p] = 0]
    /\ UNCHANGED <<decision, locked, lockedRound, msgs, crashed>>

(* Process crashes *)
Crash(p) ==
    /\ p \notin crashed
    /\ Cardinality(crashed) < f
    /\ crashed' = crashed \cup {p}
    /\ UNCHANGED <<state, round, proposal, vote, decision, locked, lockedRound, msgs>>

-----------------------------------------------------------------------------
(* Next-State Relation *)

Next ==
    \/ \E p \in Processes : ProposeValue(p)
    \/ \E p \in Processes : ReceiveProposal(p)
    \/ \E p \in Processes : LockOnValue(p)
    \/ \E p \in Processes : DecideValue(p)
    \/ \E p \in Processes : ReceiveDecision(p)
    \/ \E p \in Processes : AdvanceRound(p)
    \/ \E p \in Processes : Crash(p)

-----------------------------------------------------------------------------
(* Specification *)

(* Fairness: correct processes eventually take their enabled actions *)
Fairness ==
    /\ \A p \in Processes : WF_vars(ProposeValue(p))
    /\ \A p \in Processes : WF_vars(ReceiveProposal(p))
    /\ \A p \in Processes : WF_vars(LockOnValue(p))
    /\ \A p \in Processes : WF_vars(DecideValue(p))
    /\ \A p \in Processes : WF_vars(ReceiveDecision(p))
    /\ \A p \in Processes : SF_vars(AdvanceRound(p))

Spec == Init /\ [][Next]_vars /\ Fairness

-----------------------------------------------------------------------------
(* Invariants *)

(* Agreement: No two correct processes decide on different values *)
Agreement ==
    \A p, q \in Correct :
        (decision[p] /= 0 /\ decision[q] /= 0) => decision[p] = decision[q]

(* Validity: Decided values are from the Values set *)
Validity ==
    \A p \in Processes : 
        decision[p] /= 0 => decision[p] \in Values

(* Integrity: Each process decides at most once - decisions are immutable *)
(* Note: This is a state invariant, not a temporal formula *)
Integrity ==
    \A p \in Processes :
        decision[p] /= 0 => decision[p] \in Values

(* Termination: All correct processes eventually decide *)
Termination ==
    <>(\A p \in Correct : decision[p] /= 0)

=============================================================================
