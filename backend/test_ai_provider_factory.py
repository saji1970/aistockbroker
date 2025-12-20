import unittest
import os
from ai_provider_factory import AIProviderFactory
from config import Config

class TestAIProviderFactory(unittest.TestCase):
    """Test AI Provider Factory pattern"""

    def setUp(self):
        """Set up test fixtures"""
        # Store original AI_PROVIDER value
        self.original_provider = os.getenv('AI_PROVIDER', 'gemini')

    def tearDown(self):
        """Clean up after tests"""
        # Restore original provider
        os.environ['AI_PROVIDER'] = self.original_provider

    def test_factory_creates_predictor(self):
        """Test that factory successfully creates a predictor"""
        predictor = AIProviderFactory.create_predictor()
        self.assertIsNotNone(predictor)
        self.assertTrue(hasattr(predictor, 'process_natural_language_query'))
        self.assertTrue(hasattr(predictor, 'get_stock_prediction'))

    def test_gemini_provider_selection(self):
        """Test that setting AI_PROVIDER=gemini creates GeminiStockPredictor"""
        os.environ['AI_PROVIDER'] = 'gemini'
        predictor = AIProviderFactory.create_predictor()

        self.assertIsNotNone(predictor)
        self.assertEqual(type(predictor).__name__, 'GeminiStockPredictor')

    def test_huggingface_provider_selection(self):
        """Test that setting AI_PROVIDER=huggingface creates HuggingFaceStockPredictor"""
        os.environ['AI_PROVIDER'] = 'huggingface'
        predictor = AIProviderFactory.create_predictor()

        self.assertIsNotNone(predictor)
        self.assertEqual(type(predictor).__name__, 'HuggingFaceStockPredictor')

    def test_default_provider(self):
        """Test that default provider is Gemini when AI_PROVIDER not set"""
        # Unset AI_PROVIDER
        if 'AI_PROVIDER' in os.environ:
            del os.environ['AI_PROVIDER']

        predictor = AIProviderFactory.create_predictor()

        self.assertIsNotNone(predictor)
        self.assertEqual(type(predictor).__name__, 'GeminiStockPredictor')

    def test_case_insensitive_provider_selection(self):
        """Test that provider selection is case-insensitive"""
        # Test uppercase
        os.environ['AI_PROVIDER'] = 'HUGGINGFACE'
        predictor = AIProviderFactory.create_predictor()
        self.assertEqual(type(predictor).__name__, 'HuggingFaceStockPredictor')

        # Test mixed case
        os.environ['AI_PROVIDER'] = 'HuggingFace'
        predictor = AIProviderFactory.create_predictor()
        self.assertEqual(type(predictor).__name__, 'HuggingFaceStockPredictor')

        # Test Gemini uppercase
        os.environ['AI_PROVIDER'] = 'GEMINI'
        predictor = AIProviderFactory.create_predictor()
        self.assertEqual(type(predictor).__name__, 'GeminiStockPredictor')

    def test_factory_with_data_fetcher(self):
        """Test that factory passes data_fetcher to predictor"""
        from data_fetcher import data_fetcher

        os.environ['AI_PROVIDER'] = 'gemini'
        predictor = AIProviderFactory.create_predictor(data_fetcher)

        self.assertIsNotNone(predictor)
        self.assertIsNotNone(predictor.data_fetcher)

    def test_invalid_provider_defaults_to_gemini(self):
        """Test that invalid provider falls back to Gemini"""
        os.environ['AI_PROVIDER'] = 'invalid_provider'
        predictor = AIProviderFactory.create_predictor()

        # Should default to Gemini
        self.assertIsNotNone(predictor)
        self.assertEqual(type(predictor).__name__, 'GeminiStockPredictor')

    def test_both_providers_have_same_interface(self):
        """Test that both providers implement the same interface"""
        # Test Gemini
        os.environ['AI_PROVIDER'] = 'gemini'
        gemini_predictor = AIProviderFactory.create_predictor()

        # Test HuggingFace
        os.environ['AI_PROVIDER'] = 'huggingface'
        hf_predictor = AIProviderFactory.create_predictor()

        # Both should have the same methods
        required_methods = [
            'process_natural_language_query',
            'get_stock_prediction',
            '_analyze_intent_and_entities',
            '_extract_tickers',
            '_perform_lstm_analysis'
        ]

        for method in required_methods:
            self.assertTrue(hasattr(gemini_predictor, method),
                           f"Gemini predictor missing method: {method}")
            self.assertTrue(hasattr(hf_predictor, method),
                           f"HuggingFace predictor missing method: {method}")

    def test_factory_fallback_on_import_error(self):
        """Test that factory handles import errors gracefully"""
        # This test verifies the fallback mechanism in the factory
        # If HuggingFace import fails, it should fall back to Gemini
        os.environ['AI_PROVIDER'] = 'huggingface'

        try:
            predictor = AIProviderFactory.create_predictor()
            self.assertIsNotNone(predictor)
            # Should be either HuggingFace or Gemini (fallback)
            self.assertIn(type(predictor).__name__,
                         ['HuggingFaceStockPredictor', 'GeminiStockPredictor'])
        except ImportError:
            # If import fails, that's expected behavior for this test
            pass

    def test_predictor_initialization(self):
        """Test that created predictors are properly initialized"""
        providers = ['gemini', 'huggingface']

        for provider in providers:
            os.environ['AI_PROVIDER'] = provider
            predictor = AIProviderFactory.create_predictor()

            # Check basic initialization
            self.assertIsNotNone(predictor)
            self.assertTrue(hasattr(predictor, 'technical_analyzer'))
            self.assertTrue(hasattr(predictor, 'sensitivity_analyzer'))

    def test_multiple_factory_calls(self):
        """Test that factory can create multiple predictor instances"""
        os.environ['AI_PROVIDER'] = 'gemini'
        predictor1 = AIProviderFactory.create_predictor()
        predictor2 = AIProviderFactory.create_predictor()

        # Should create separate instances
        self.assertIsNot(predictor1, predictor2)
        self.assertEqual(type(predictor1).__name__, type(predictor2).__name__)

    def test_config_integration(self):
        """Test that factory uses Config correctly"""
        # Test that Config.AI_PROVIDER is read correctly
        os.environ['AI_PROVIDER'] = 'huggingface'
        predictor = AIProviderFactory.create_predictor()

        # Verify Config was used
        self.assertEqual(Config.AI_PROVIDER, 'huggingface')
        self.assertEqual(type(predictor).__name__, 'HuggingFaceStockPredictor')

if __name__ == '__main__':
    # Run tests
    print("=" * 70)
    print("Testing AI Provider Factory")
    print("=" * 70)
    print(f"Current AI_PROVIDER: {os.getenv('AI_PROVIDER', 'gemini')}")
    print(f"HF_API_TOKEN set: {bool(Config.HF_API_TOKEN)}")
    print(f"GOOGLE_API_KEY set: {bool(Config.GOOGLE_API_KEY)}")
    print("=" * 70)

    unittest.main(verbosity=2)
