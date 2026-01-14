"""Consensus Example

Demonstrates Spherical BFT consensus with Byzantine nodes.
"""

import numpy as np
from hypersync_core.consensus import spherical_bft_consensus


def run_spherical_bft_example():
    """Demonstrate Spherical BFT consensus."""
    print("=== Spherical BFT Consensus ===")
    print("Testing with 10 honest nodes + 3 Byzantine nodes")
    print()
    
    # Create honest node proposals (clustered)
    np.random.seed(42)
    honest_proposals = [
        np.array([1.0, 0.1, 0.1]) + 0.1 * np.random.randn(3)
        for _ in range(10)
    ]
    
    # Create Byzantine node proposals (outliers)
    byzantine_proposals = [
        np.array([10.0, 10.0, 10.0]),  # Far outlier
        np.array([-5.0, -5.0, -5.0]),  # Far outlier
        np.array([0.0, 0.0, 100.0]),   # Far outlier
    ]
    
    # Combine all proposals
    all_proposals = honest_proposals + byzantine_proposals
    
    print(f"Total nodes: {len(all_proposals)}")
    print(f"Expected Byzantine nodes: [10, 11, 12]")
    print()
    
    # Run consensus
    try:
        consensus, detected_byzantine = spherical_bft_consensus(all_proposals)
        
        print("✓ Consensus reached!")
        print(f"Consensus value: {consensus}")
        print(f"Detected Byzantine nodes: {detected_byzantine}")
        print()
        
        # Verify consensus is on unit sphere
        norm = np.linalg.norm(consensus)
        print(f"Consensus norm: {norm:.6f} (should be ≈1.0)")
        
        # Check if Byzantine detection was successful
        if set(detected_byzantine) == {10, 11, 12}:
            print("✓ Perfect Byzantine detection!")
        elif len(set(detected_byzantine) & {10, 11, 12}) >= 2:
            print("✓ Good Byzantine detection (2+ detected)")
        else:
            print("⚠ Partial Byzantine detection")
    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


if __name__ == "__main__":
    run_spherical_bft_example()
    print("✓ Consensus example completed!")
