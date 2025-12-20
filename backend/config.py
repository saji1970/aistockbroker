import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the stock prediction system."""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your_google_api_key_here')
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'your_alpha_vantage_api_key_here')
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', 'your_finnhub_api_key_here')
    MARKETSTACK_API_KEY = os.getenv('MARKETSTACK_API_KEY', 'your_marketstack_api_key_here')

    # HuggingFace Configuration (for free AI alternative)
    HF_API_TOKEN = os.getenv('HF_API_TOKEN', '')
    HF_MODEL = os.getenv('HF_MODEL', 'meta-llama/Meta-Llama-3-8B-Instruct')
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini')  # 'gemini' or 'huggingface'

    # Model Configuration
    GEMINI_MODEL = "gemini-1.5-pro"
    MAX_TOKENS = 4096
    TEMPERATURE = 0.3  # Lower temperature for more focused stock analysis
    TOP_P = 0.9
    TOP_K = 40
    
    # Stock Data Configuration
    DEFAULT_PERIOD = "1y"
    DEFAULT_INTERVAL = "1d"
    
    # Technical Indicators
    SMA_PERIODS = [20, 50, 200]
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    # Prediction Settings
    PREDICTION_DAYS = 30
    CONFIDENCE_THRESHOLD = 0.6
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your environment variables.")
        return True 