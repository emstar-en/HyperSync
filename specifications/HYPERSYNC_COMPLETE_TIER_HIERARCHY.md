# HyperSync Complete Tier Hierarchy

**Date:** January 15, 2026  
**Version:** 1.0.0  
**Status:** FINALIZED

---

## Overview

This document provides the definitive reference for HyperSync's complete tier structure, including sub-enterprise tiers and the QuarterMaster (QM) add-on.

---

## Full Tier Hierarchy

```
SUB-ENTERPRISE TIERS (Service Levels by Complexity):
├── Core (O(n) - fastest)
├── Basic (O(n log n))
├── Pro (O(n²)+)
└── Advanced (Specialized: ML, Crypto, Quantum, Category Theory)
    └── QUARTERMASTER ADD-ON (by network size):
        ├── Venture (small distributed networks)
        ├── Campaign (mid-size distributed networks)
        └── Hegemony (large distributed networks)
        
[Imperium - RESERVED for future focused top-tier variant]
```

---

## Sub-Enterprise Tiers (Complexity-Based)

Sub-enterprise tiers are organized by **computational complexity**:

| Tier | Complexity | Description | Key Operations |
|------|-----------|-------------|----------------|
| **Core** | O(n) | Fastest, linear time | Fréchet mean, basic consensus |
| **Basic** | O(n log n) | Linearithmic | Enhanced consensus, standard IO |
| **Pro** | O(n²)+ | Quadratic+ | Advanced ops, team tools |
| **Advanced** | Specialized | ML, Crypto, Quantum, Category Theory | Full integration |

### Tier Progression
```
Core → Basic → Pro → Advanced
 │       │       │       │
 └───────┴───────┴───────┘
    Increasing complexity
    and feature richness
```

---

## QuarterMaster Add-On (Network Size-Based)

QM is an **optional add-on** exclusively for **Advanced tier** subscribers. QM tiers are based on **distributed network size**, NOT complexity.

### QM Tier Summary

| QM Tier | Network Size | Deployment | Partner Focus |
|---------|-------------|------------|---------------|
| **Venture** | 10-100 nodes | Single region | Starter partners |
| **Campaign** | 100-1000 nodes | Multi-region | Growth partners |
| **Hegemony** | 1000+ nodes | Global | Enterprise partners |

### Key Distinction

| Aspect | Sub-Enterprise Tiers | QM Tiers |
|--------|---------------------|----------|
| **Basis** | Computational complexity | Network size |
| **Purpose** | API access & pricing | Deployment scale |
| **Relation** | Standalone service levels | Add-on to Advanced |

---

## Detailed QM Tier Specifications

### Venture (Small Networks)
- **Nodes:** 10-100 typical
- **Deployment:** Single region
- **Storage:** SQLite + FAISS
- **Partner Tier:** Starter
- **Use Case:** Startups, POC, small orgs

### Campaign (Mid-Size Networks)
- **Nodes:** 100-1000 typical
- **Deployment:** Multi-region (2-4 zones)
- **Storage:** PostgreSQL + pgvector
- **Partner Tier:** Growth
- **Use Case:** Scaling orgs, regional expansion

### Hegemony (Large Networks)
- **Nodes:** 1000+ nodes
- **Deployment:** Global (5+ zones)
- **Storage:** Cassandra + Milvus
- **Partner Tier:** Enterprise
- **Use Case:** Global enterprises, MNCs

---

## Reserved Naming

| Name | Status | Notes |
|------|--------|-------|
| **Imperium** | RESERVED | Future focused variant of top-tier QM |

> **Important:** "Imperium" should NOT be used for current tier naming. It is reserved for a future specialized variant of the top-tier QuarterMaster offering.

---

## Deprecated Terminology

The following terms are **no longer used**:

| Deprecated | Replacement | Reason |
|------------|-------------|--------|
| Bronze | Venture | Metal levels deprecated |
| Silver | Campaign | Metal levels deprecated |
| Gold | Hegemony | Metal levels deprecated |
| Imperium (as current tier) | Hegemony | Imperium reserved for future |

---

## Visual Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    SUB-ENTERPRISE TIERS                         │
│              (Service Levels by Complexity)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌────────┐   ┌────────┐   ┌────────┐   ┌──────────┐          │
│   │  CORE  │ → │ BASIC  │ → │  PRO   │ → │ ADVANCED │          │
│   │  O(n)  │   │O(nlogn)│   │ O(n²)+ │   │Specialized│          │
│   └────────┘   └────────┘   └────────┘   └────┬─────┘          │
│                                               │                 │
└───────────────────────────────────────────────┼─────────────────┘
                                                │
                                                ▼
                    ┌───────────────────────────────────────────┐
                    │         QUARTERMASTER ADD-ON              │
                    │         (Network Size Tiers)              │
                    │         (Advanced Tier Only)              │
                    ├───────────────────────────────────────────┤
                    │                                           │
                    │  ┌─────────────┐  ┌─────────────┐        │
                    │  │   VENTURE   │  │  CAMPAIGN   │        │
                    │  │  (10-100)   │  │ (100-1000)  │        │
                    │  │  Single Rgn │  │ Multi-Rgn   │        │
                    │  └─────────────┘  └─────────────┘        │
                    │                                           │
                    │           ┌─────────────┐                │
                    │           │  HEGEMONY   │                │
                    │           │   (1000+)   │                │
                    │           │   Global    │                │
                    │           └─────────────┘                │
                    │                                           │
                    │   ┌─────────────────────────────────┐    │
                    │   │ IMPERIUM - Reserved for Future  │    │
                    │   └─────────────────────────────────┘    │
                    └───────────────────────────────────────────┘
```

---

## Partner Specialization Model

Licensed partners can specialize by QM tier:

```
Partner Certification Path: Venture → Campaign → Hegemony

┌──────────────────┬────────────────────────────────────────┐
│ Partner Level    │ Deployment Focus                       │
├──────────────────┼────────────────────────────────────────┤
│ Venture Partner  │ Small network deployments, POC         │
│ Campaign Partner │ Mid-size scaling, regional expansion   │
│ Hegemony Partner │ Enterprise global deployments          │
└──────────────────┴────────────────────────────────────────┘
```

---

## Quick Reference Card

### Sub-Enterprise Tiers
- **Core** = O(n) complexity, fastest
- **Basic** = O(n log n) complexity
- **Pro** = O(n²)+ complexity
- **Advanced** = Specialized (ML, Crypto, Quantum, Category Theory)

### QM Add-On Tiers (Advanced only)
- **Venture** = Small networks (10-100 nodes)
- **Campaign** = Mid networks (100-1000 nodes)
- **Hegemony** = Large networks (1000+ nodes)

### Reserved
- **Imperium** = Future top-tier variant (DO NOT USE)

---

*Document Version: 1.0.0*  
*Status: FINALIZED*
