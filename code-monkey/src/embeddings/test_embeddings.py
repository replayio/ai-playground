import unittest
from embeddings import VoyageEmbeddings
from unittest.mock import patch, MagicMock

class TestVoyageEmbeddings(unittest.TestCase):

    def setUp(self):
        self.test_folder = 'test_data'
        self.embedder = VoyageEmbeddings(self.test_folder)

    @patch('voyageai.Client')
    def test_embed_function(self, mock_client):
        # Mock the voyageai.Client's embed method
        mock_client.return_value.embed.return_value = [[0.1, 0.2, 0.3]]
        
        # Run the embed function
        self.embedder.embed()

        # Check if embeddings have been added to the embedder
        self.assertTrue(len(self.embedder.embeddings) > 0)

    @patch('voyageai.Client')
    def test_run_prompt_function(self, mock_client):
        # Mock the voyageai.Client's embed method
        mock_client.return_value.embed.return_value = [[0.1, 0.2, 0.3]]
        
        # Assume that the embed function has already been run and embeddings are available
        self.embedder.embeddings = {
            'file1.py': [0.1, 0.2, 0.3],
            'file2.py': [0.4, 0.5, 0.6]
        }

        # Run the run_prompt function with a sample prompt
        result = self.embedder.run_prompt('Sample prompt')

        # Check if the result is the content of the most similar file
        self.assertEqual(result, 'file1.py content')

if __name__ == '__main__':
    unittest.main()
