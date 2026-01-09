"""
Example: Using the Model Catalogue

This example demonstrates common catalogue operations.
"""

from hypersync.nvm import ModelCatalogueManager

def main():
    # Initialize catalogue
    print("Initializing Model Catalogue...")
    manager = ModelCatalogueManager("example_catalogue.db")

    # Example 1: Scan a directory
    print("\n=== Example 1: Scanning Directory ===")
    model_ids = manager.scan_directory("/path/to/models", recursive=True)
    print(f"Found {len(model_ids)} models")

    # Example 2: List models
    print("\n=== Example 2: Listing Models ===")
    models = manager.list_models(limit=10)
    for model in models:
        print(f"  - {model['name']} ({model['format']}, {model['size_bytes']/(1024**3):.2f} GB)")

    # Example 3: Search
    print("\n=== Example 3: Searching ===")
    results = manager.search_models("code")
    print(f"Found {len(results)} models matching 'code'")

    # Example 4: Get model details
    if model_ids:
        print("\n=== Example 4: Model Details ===")
        model = manager.get_model(model_ids[0])
        print(f"Name: {model['name']}")
        print(f"Format: {model['format']}")
        print(f"Family: {model['family_id'][:8]}...")
        print(f"Generation: {model['generation']}")

    # Example 5: Tag management
    if model_ids:
        print("\n=== Example 5: Tagging ===")
        manager.add_tag(model_ids[0], "production")
        manager.add_tag(model_ids[0], "tested")
        print("Tags added")

    # Example 6: nLD profile
    if model_ids:
        print("\n=== Example 6: nLD Profile ===")
        training_domains = [
            {
                "ld_id": "ld-euclidean",
                "ld_schema": "euclidean-standard",
                "sample_count": 2000,
                "domain_characteristics": "Standard reasoning"
            },
            {
                "ld_id": "ld-hyperbolic",
                "ld_schema": "hyperbolic-compressed",
                "sample_count": 1500,
                "domain_characteristics": "Hierarchical data"
            }
        ]

        manager.set_nld_profile(
            model_ids[0],
            nld_level=2,
            training_domains=training_domains,
            instability_score=0.25,
            threat_level="low"
        )
        print("nLD profile set")

    # Example 7: Family tree
    if model_ids:
        print("\n=== Example 7: Family Tree ===")
        tree = manager.get_family_tree(model_ids[0])
        print(f"Family: {tree['family']['family_name']}")
        print(f"Members: {len(tree['members'])}")
        print(f"Generations: {len(tree['generations'])}")

    # Example 8: Statistics
    print("\n=== Example 8: Statistics ===")
    stats = manager.get_stats()
    print(f"Total models: {stats['total_models']}")
    print(f"Total families: {stats['total_families']}")
    print(f"nLD models: {stats['nld_models']}")
    print("By format:")
    for fmt, count in stats['by_format'].items():
        print(f"  {fmt}: {count}")

    # Example 9: Export
    print("\n=== Example 9: Export ===")
    # manager.export_catalogue("my_catalogue_backup.json")
    print("(Export commented out for example)")

    # Cleanup
    manager.close()
    print("\n✓ Examples complete")


if __name__ == "__main__":
    main()
