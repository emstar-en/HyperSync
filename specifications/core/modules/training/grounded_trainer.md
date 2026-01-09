# Grounded Trainer (RA-SFT + Gates)

Purpose: train models that must cite evidence and satisfy grounding gates.

Losses:
- L = ce + w_cov * (1 - citation_coverage) + w_prec * (1 - citation_precision)

Gates (per-domain defaults):
- citation_precision >= 0.95
- citation_recall >= 0.90
- temporal_correctness >= 0.98
- jurisdiction_accuracy >= 0.98
- hallucination_rate <= 0.005
- ECE <= 0.03

Pipeline:
- Build RA-SFT batches from queries + retrieved passages
- Verify citations pre-training
- Train adapters/LoRA; promote only if gates pass
