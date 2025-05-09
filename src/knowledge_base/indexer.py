class PackageIndexer:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def create_index(self, travel_packages):
        embeddings = self._generate_embeddings(travel_packages)
        self.vector_store.save_embeddings(embeddings)

    def update_index(self, travel_package):
        embedding = self._generate_embedding(travel_package)
        self.vector_store.save_embeddings([embedding])

    def _generate_embeddings(self, travel_packages):
        # Placeholder for actual embedding generation logic
        return [self._generate_embedding(pkg) for pkg in travel_packages]

    def _generate_embedding(self, travel_package):
        # Placeholder for actual embedding generation logic
        return {"package_id": travel_package["id"], "embedding": [0.0] * 128}  # Example embedding