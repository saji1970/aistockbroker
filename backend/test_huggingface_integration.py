import unittest
import os
from huggingface_predictor import HuggingFaceStockPredictor
from config import Config

class TestHuggingFaceIntegration(unittest.TestCase):
    """Test HuggingFace predictor integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.predictor = HuggingFaceStockPredictor()

    def test_initialization(self):
        """Test that predictor initializes correctly"""
        self.assertIsNotNone(self.predictor)
        self.assertIsNotNone(self.predictor.technical_analyzer)
        self.assertIsNotNone(self.predictor.sensitivity_analyzer)

    def test_model_initialization_with_token(self):
        """Test model initialization when HF_API_TOKEN is set"""
        if Config.HF_API_TOKEN:
            self.assertIsNotNone(self.predictor.client)
            self.assertIsNotNone(self.predictor.model)
            self.assertEqual(self.predictor.model, Config.HF_MODEL)
        else:
            self.assertIsNone(self.predictor.client)
            self.assertIsNone(self.predictor.model)

    def test_process_natural_language_query(self):
        """Test natural language query processing"""
        if Config.HF_API_TOKEN:
            query = "What is the current price of AAPL?"
            result = self.predictor.process_natural_language_query(query)

            self.assertIsInstance(result, dict)
            self.assertIn('response', result)
            self.assertIn('query_type', result)
            self.assertIn('confidence', result)

            # Check response is not empty
            self.assertTrue(len(result['response']) > 0)
            # Check confidence is reasonable
            self.assertGreaterEqual(result['confidence'], 0.0)
            self.assertLessEqual(result['confidence'], 1.0)

    def test_intent_classification(self):
        """Test intent classification for different queries"""
        test_queries = [
            ("What is AAPL price?", "get_price_quote"),
            ("Compare AAPL and MSFT", "compare_metrics"),
            ("Explain P/E ratio", "financial_education"),
        ]

        for query, expected_intent in test_queries:
            result = self.predictor._analyze_intent_and_entities(query)
            self.assertEqual(result['intent'], expected_intent)

    def test_ticker_extraction(self):
        """Test stock ticker extraction"""
        query = "What is the price of AAPL and TSLA?"
        tickers = self.predictor._extract_tickers(query)

        self.assertIn('AAPL', tickers)
        self.assertIn('TSLA', tickers)

    def test_get_stock_prediction(self):
        """Test stock prediction generation"""
        if Config.HF_API_TOKEN:
            symbol = 'AAPL'
            timeframe = '1d'
            result = self.predictor.get_stock_prediction(symbol, timeframe)

            if 'error' not in result:
                self.assertIn('symbol', result)
                self.assertIn('prediction', result)
                self.assertIn('current_price', result)
                self.assertIn('lstm_analysis', result)
                self.assertIn('technical_indicators', result)

                # Verify prediction structure
                prediction = result['prediction']
                self.assertIn('direction', prediction)
                self.assertIn('confidence', prediction)
                self.assertIn('target_price', prediction)

    def test_generate_content_wrapper(self):
        """Test the HuggingFace content generation wrapper"""
        if Config.HF_API_TOKEN:
            prompt = "What is the stock market?"
            response = self.predictor._generate_content(prompt)

            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
            self.assertNotIn("Error:", response)  # Should not have errors

    def test_lstm_analysis(self):
        """Test LSTM-inspired analysis"""
        import pandas as pd
        import numpy as np

        # Create sample stock data
        dates = pd.date_range('2024-01-01', periods=30)
        prices = 100 + np.cumsum(np.random.randn(30))  # Random walk
        stock_data = pd.DataFrame({
            'Close': prices,
            'Volume': [1000000] * 30
        }, index=dates)

        result = self.predictor._perform_lstm_analysis(stock_data)

        self.assertIn('trend_direction', result)
        self.assertIn('momentum_5d', result)
        self.assertIn('momentum_10d', result)
        self.assertIn('prediction_factor', result)
        self.assertIn('pattern_type', result)
        self.assertIn('confidence', result)

        # Check confidence is in valid range
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 100)

    def test_fallback_without_token(self):
        """Test that predictor handles missing token gracefully"""
        # Temporarily unset token
        original_token = Config.HF_API_TOKEN
        Config.HF_API_TOKEN = ''

        predictor = HuggingFaceStockPredictor()
        self.assertIsNone(predictor.model)
        self.assertIsNone(predictor.client)

        # Restore token
        Config.HF_API_TOKEN = original_token

    def test_pattern_identification(self):
        """Test price pattern identification"""
        import numpy as np

        # Test uptrend
        uptrend_prices = np.array([100, 101, 102, 103, 104, 105, 106, 107, 108, 109])
        pattern = self.predictor._identify_price_pattern(uptrend_prices)
        self.assertEqual(pattern, "Uptrend")

        # Test downtrend
        downtrend_prices = np.array([109, 108, 107, 106, 105, 104, 103, 102, 101, 100])
        pattern = self.predictor._identify_price_pattern(downtrend_prices)
        self.assertEqual(pattern, "Downtrend")

        # Test consolidation
        consolidation_prices = np.array([100, 100.5, 100.2, 100.3, 100.1, 100.4, 100.2, 100.3, 100.1, 100.2])
        pattern = self.predictor._identify_price_pattern(consolidation_prices)
        self.assertIn(pattern, ["Consolidation", "Mixed"])

if __name__ == '__main__':
    # Run tests
    print("=" * 70)
    print("Testing HuggingFace Integration")
    print("=" * 70)
    print(f"HF_API_TOKEN set: {bool(Config.HF_API_TOKEN)}")
    print(f"HF_MODEL: {Config.HF_MODEL}")
    print("=" * 70)

    unittest.main(verbosity=2)
