from app.services.knowledge_pipeline import build_embedding_encoder


def main() -> None:
    encoder = build_embedding_encoder()
    dimensions = encoder.dimensions
    print(f"Preloaded embedding model: {encoder.model_name} ({dimensions} dimensions)")


if __name__ == "__main__":
    main()
