# Episode Recorder Mechanics

## Overview
The Episode Recorder is the "Black Box" flight recorder for Pathfinder agents. It captures every input, output, and side effect to allow for perfect replay.

## Data Structure: `PathfinderEpisode`

```json
{
  "episode_id": "uuid",
  "agent_id": "uuid",
  "start_time": "iso8601",
  "end_time": "iso8601",
  "seed": 12345,
  "trace": [
    {
      "step_id": 1,
      "op": "geometry.move",
      "inputs": {"x": 0.1, "y": 0.2},
      "outputs": {"new_pos": {"x": 0.15, "y": 0.25}},
      "duration_ms": 12
    },
    {
      "step_id": 2,
      "op": "network.fetch",
      "inputs": {"url": "https://api.example.com"},
      "outputs": {"status": 200, "body_hash": "sha256:..."},
      "duration_ms": 150
    }
  ],
  "outcome": "SUCCESS"
}
```

## Recording Logic

1.  **Stream Capture**: The recorder hooks into the AGUA Interceptor.
2.  **Sanitization**: Sensitive data (API keys, PII) is redacted *before* writing to disk.
3.  **Hashing**: Large payloads (images, binaries) are hashed and stored in a content-addressable store (CAS), with only the hash in the trace.
4.  **Async Write**: Traces are written to a ring buffer and flushed to disk asynchronously to minimize performance impact.

## Replay Mechanism
To verify a trace:
1.  Reset agent to `start_state`.
2.  Inject `inputs` from the trace.
3.  Mock `network` calls using the recorded outputs.
4.  Assert that the agent produces the exact same `outputs`.
