# Poker Night Orchestration Logic

## 1. The "Game Master" Protocol

This capsule does not just run a game; it orchestrates a **Social Event**.
When a user issues a `CreateLobby` intent, the Game Master performs the following sequence:

### Phase A: The Setup (Natural Language Parsing)
1.  **Analyze Request**: "Redhead dealer, looks like Character A, sounds like Character B."
2.  **Resolve Participants**:
    *   "The Regulars" -> Resolves to a User Group ID (e.g., `@dev_team_alpha`).
    *   "Mail Bot" -> Resolves to Agent ID (`agent.utility.mailbot`).
3.  **Configure Dealer**:
    *   **Visuals**: Generates a Stable Diffusion/Flux prompt for the avatar.
    *   **Voice**: Selects the nearest TTS embedding match for "Character B".
    *   **Personality**: Synthesizes a System Prompt: *"You are a dealer who looks like [A] and sounds like [B]. You are [Cute/Sassy/Strict]."*

### Phase B: The Invitation (Geodesic Routing)
1.  **Spatial Quorum**: A new hyperbolic coordinate is allocated for the table.
2.  **Alerts**:
    *   **Humans**: Sends a TUI Notification: *"♠️ Poker Night Alert: [User] started a game. Table is open."*
    *   **Agents**: Sends a `PROTOCOL_ADAPTER_REQUEST` to the target agents (e.g., Mail Bot).
        *   *Note:* The Mail Bot must load the `poker_rules` skill module to participate.

### Phase C: The Game Loop (Tier 2 Consensus)
1.  **State**: The "Deck" is a shared cryptographic object.
2.  **Speed**: Actions are optimistic (D2).
3.  **Rendering**:
    *   **Table**: 8-bit/ASCII representation of cards and chips.
    *   **Dealer**: Live-generated avatar (Sixel/Image) that reacts to game state.
    *   **Mail Bot**: Represented by its standard icon, chatting via its LLM output.

## 2. Agent Bridging (The "Mail Bot" Problem)

How does a Mail Bot play poker?
The Game Master wraps the utility agent in a **Player Proxy**:

```python
class PokerProxy(AgentWrapper):
    def on_game_state(self, state):
        # Translate Poker State -> Natural Language
        context = f"You have {state.hand}. The pot is {state.pot}. The odds are {state.odds}."

        # Ask the Agent
        decision = self.agent.ask(context, task="play_poker")

        # Translate Response -> Game Action
        return parse_action(decision)
```

This allows *any* agent in the HyperSync ecosystem to be invited to the table.
