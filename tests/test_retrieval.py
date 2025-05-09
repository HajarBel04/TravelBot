#tests/test_retrieval.py
import unittest
from src.retrieval.query_builder import QueryBuilder
from src.retrieval.retriever import PackageRetriever
from src.knowledge_base.db import TravelPackageDB

class TestPackageRetriever(unittest.TestCase):

    def setUp(self):
        self.db = TravelPackageDB()
        self.retriever = PackageRetriever(self.db)
        self.query_builder = QueryBuilder()

    def test_retrieve_packages(self):
        # Assuming we have some packages added to the database for testing
        self.db.add_package({"destination": "Paris", "dates": ["2023-06-01", "2023-06-10"], "budget": 2000})
        self.db.add_package({"destination": "London", "dates": ["2023-07-01", "2023-07-10"], "budget": 1500})

        # Create a query based on some hypothetical extracted email information
        query = self.query_builder.build_query(destination="Paris", dates=["2023-06-01", "2023-06-10"], budget=2000)
        
        # Retrieve packages based on the query
        retrieved_packages = self.retriever.retrieve_packages(query)

        # Check if the retrieved packages match the expected result
        self.assertEqual(len(retrieved_packages), 1)
        self.assertEqual(retrieved_packages[0]['destination'], "Paris")

if __name__ == '__main__':
    unittest.main()