#tests/test_generation.py
import unittest
from src.generation.proposal_generator import ProposalGenerator
from src.generation.llm_wrapper import LLMWrapper

class TestProposalGenerator(unittest.TestCase):
    def setUp(self):
        self.llm_wrapper = LLMWrapper()
        self.proposal_generator = ProposalGenerator(self.llm_wrapper)

    def test_generate_proposal(self):
        # Mock data for testing
        retrieved_info = {
            'destination': 'Paris',
            'dates': '2023-12-01 to 2023-12-10',
            'travelers': ['Alice', 'Bob'],
            'budget': '2000',
            'interests': ['sightseeing', 'cuisine']
        }
        expected_proposal = "Here is your travel proposal for Paris from 2023-12-01 to 2023-12-10 for Alice and Bob, with a budget of 2000 focusing on sightseeing and cuisine."

        # Generate proposal
        proposal = self.proposal_generator.generate_proposal(retrieved_info)

        # Assert the proposal matches expected output
        self.assertEqual(proposal, expected_proposal)

if __name__ == '__main__':
    unittest.main()