import os
import logging

logger = logging.getLogger(__name__)

class AIProviderFactory:
    """Factory for creating AI predictor instances based on configuration.

    This factory enables runtime switching between different AI providers
    (Gemini, HuggingFace, etc.) based on the AI_PROVIDER environment variable.
    """

    @staticmethod
    def create_predictor(data_fetcher=None):
        """Create and return appropriate predictor based on AI_PROVIDER env var.

        Args:
            data_fetcher: Optional data fetcher instance for market data

        Returns:
            Instance of GeminiStockPredictor or HuggingFaceStockPredictor

        Example:
            >>> predictor = AIProviderFactory.create_predictor()
            >>> result = predictor.process_natural_language_query("What is AAPL price?")
        """
        from config import Config

        provider = os.getenv('AI_PROVIDER', 'gemini').lower()

        if provider == 'huggingface':
            try:
                from huggingface_predictor import HuggingFaceStockPredictor
                logger.info("Using HuggingFace AI provider")
                return HuggingFaceStockPredictor(data_fetcher)
            except ImportError as e:
                logger.error(f"Failed to import HuggingFaceStockPredictor: {e}")
                logger.info("Falling back to Gemini provider")
                from gemini_predictor import GeminiStockPredictor
                return GeminiStockPredictor(data_fetcher)
        else:  # default to gemini
            from gemini_predictor import GeminiStockPredictor
            logger.info("Using Gemini AI provider")
            return GeminiStockPredictor(data_fetcher)
