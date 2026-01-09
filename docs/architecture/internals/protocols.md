# HyperSync Protocols

## Communication Protocols

### 1. REST API Protocol

**Transport**: HTTP/1.1 or HTTP/2 over TLS
**Format**: JSON
**Authentication**: Bearer token or API key

**Request Format**:
```http
POST /api/v1/operators/execute HTTP/1.1
Host: hypersync.example.com
Authorization: Bearer <token>
Content-Type: application/json

{
  "operator_id": "op_123",
  "inputs": {...},
  "options": {...}
}
```

**Response Format**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "outputs": {...},
  "receipt_id": "receipt_456",
  "execution_time_ms": 45
}
```

### 2. gRPC Protocol

**Transport**: HTTP/2 over TLS
**Format**: Protocol Buffers
**Authentication**: Mutual TLS or token

**Service Definition**:
```protobuf
service HyperSync {
  rpc ExecuteOperator(OperatorRequest) returns (OperatorResponse);
  rpc StreamResults(StreamRequest) returns (stream Result);
}
```

### 3. ICO Network Protocol

**Purpose**: Inter-component orchestration

**Message Types**:
- `HELLO`: Peer introduction
- `STATE_SYNC`: State synchronization
- `CONSENSUS`: Consensus messages
- `HEARTBEAT`: Liveness check

**Message Format**:
```json
{
  "type": "STATE_SYNC",
  "sender": "node_123",
  "timestamp": "2024-12-05T03:15:03Z",
  "payload": {...},
  "signature": "..."
}
```

**Connection Lifecycle**:
```
1. TCP connection established
2. TLS handshake
3. HELLO message exchange
4. Authentication
5. State synchronization
6. Normal operation
7. Graceful disconnect
```

## Consensus Protocols

### 1. PBFT (Practical Byzantine Fault Tolerance)

**Phases**: Pre-prepare, Prepare, Commit

**Message Flow**:
```
Client → Primary: REQUEST
Primary → Replicas: PRE-PREPARE
Replicas → All: PREPARE
All → All: COMMIT
Replicas → Client: REPLY
```

**Guarantees**:
- Safety: All honest nodes agree
- Liveness: Progress guaranteed
- Byzantine tolerance: Up to f faulty nodes (3f+1 total)

### 2. Raft

**Roles**: Leader, Follower, Candidate

**Operations**:
- Leader election
- Log replication
- Safety

**Message Types**:
- `RequestVote`: Candidate requests votes
- `AppendEntries`: Leader replicates log
- `InstallSnapshot`: Leader sends snapshot

## Receipt Protocol

**Purpose**: Cryptographic proof of operations

**Receipt Format**:
```json
{
  "receipt_id": "receipt_123",
  "timestamp": "2024-12-05T03:15:03Z",
  "operation": {
    "type": "operator_execution",
    "operator_id": "op_456",
    "inputs_hash": "sha256:...",
    "outputs_hash": "sha256:..."
  },
  "prev_receipt_hash": "sha256:...",
  "signature": "..."
}
```

**Verification**:
```
1. Verify signature
2. Verify prev_receipt_hash links to previous receipt
3. Verify inputs_hash matches actual inputs
4. Verify outputs_hash matches actual outputs
5. Verify timestamp is reasonable
```

## Synchronization Protocol

**Purpose**: Distributed state synchronization

**Phases**:
1. **Discovery**: Find peers
2. **Handshake**: Establish connection
3. **State Exchange**: Exchange state checksums
4. **Diff Computation**: Identify differences
5. **Sync**: Transfer missing data
6. **Verification**: Verify synchronized state

**Conflict Resolution**:
- Last-write-wins (timestamp-based)
- Policy-based resolution
- Manual resolution (escalation)
