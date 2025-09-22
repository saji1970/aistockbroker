#!/usr/bin/env python3
"""
Test Configuration for AI Stock Trading Bot
Contains test settings and mock data
"""

# Test Configuration
TEST_CONFIG = {
    "api_base_url": "https://ai-stock-trading-simple-720013332324.us-central1.run.app",
    "test_symbol": "AAPL",
    "test_initial_capital": 10000,
    "test_timeout": 30,  # seconds
    "api_timeout": 60,   # seconds
    "mock_data_size": 20,
    "training_samples": 60,
    "performance_test_samples": 100
}

# Mock Stock Data for Testing
MOCK_STOCK_DATA = [
    {
        "symbol": "AAPL",
        "price": 175.50,
        "open": 174.00,
        "high": 176.00,
        "low": 173.50,
        "close": 175.50,
        "volume": 50000000,
        "change_percent": 0.86,
        "timestamp": "2025-09-16T10:00:00Z"
    },
    {
        "symbol": "MSFT",
        "price": 380.25,
        "open": 378.00,
        "high": 382.00,
        "low": 377.50,
        "close": 380.25,
        "volume": 30000000,
        "change_percent": 0.59,
        "timestamp": "2025-09-16T10:00:00Z"
    },
    {
        "symbol": "GOOGL",
        "price": 142.80,
        "open": 141.50,
        "high": 143.50,
        "low": 141.00,
        "close": 142.80,
        "volume": 20000000,
        "change_percent": 0.92,
        "timestamp": "2025-09-16T10:00:00Z"
    }
]

# Test Market Events
TEST_MARKET_EVENTS = [
    {
        "timestamp": "2025-09-16T08:00:00Z",
        "event_type": "earnings",
        "description": "Apple reports strong Q4 earnings, beats expectations",
        "impact_score": 0.8,
        "sentiment": "positive",
        "affected_symbols": ["AAPL"]
    },
    {
        "timestamp": "2025-09-16T09:00:00Z",
        "event_type": "news",
        "description": "Tesla announces new factory expansion plans",
        "impact_score": 0.6,
        "sentiment": "positive",
        "affected_symbols": ["TSLA"]
    },
    {
        "timestamp": "2025-09-16T10:00:00Z",
        "event_type": "economic",
        "description": "Federal Reserve hints at potential rate cuts",
        "impact_score": 0.7,
        "sentiment": "positive",
        "affected_symbols": ["AAPL", "MSFT", "GOOGL"]
    }
]

# Test Trading Configurations
TEST_TRADING_CONFIGS = {
    "momentum": {
        "symbol": "AAPL",
        "initial_capital": 10000,
        "strategy": "momentum",
        "max_position_size": 0.1,
        "max_daily_loss": 0.05,
        "risk_tolerance": "medium"
    },
    "rsi": {
        "symbol": "AAPL",
        "initial_capital": 10000,
        "strategy": "rsi",
        "max_position_size": 0.1,
        "max_daily_loss": 0.05,
        "risk_tolerance": "medium"
    },
    "aggressive": {
        "symbol": "AAPL",
        "initial_capital": 10000,
        "strategy": "momentum",
        "max_position_size": 0.2,
        "max_daily_loss": 0.1,
        "risk_tolerance": "high"
    },
    "conservative": {
        "symbol": "AAPL",
        "initial_capital": 10000,
        "strategy": "rsi",
        "max_position_size": 0.05,
        "max_daily_loss": 0.02,
        "risk_tolerance": "low"
    }
}

# Expected API Response Schemas
API_SCHEMAS = {
    "health": {
        "required_fields": ["status", "timestamp"],
        "optional_fields": ["service"]
    },
    "start": {
        "required_fields": ["status", "bot_id", "config", "started_at"],
        "optional_fields": ["message"]
    },
    "status": {
        "required_fields": ["status", "mode", "last_update"],
        "optional_fields": ["bot_id", "config", "started_at", "uptime", "trades_today", "success_rate"]
    },
    "portfolio": {
        "required_fields": ["cash_balance", "positions", "total_value", "timestamp"],
        "optional_fields": ["total_invested", "total_gain_loss", "total_gain_loss_percent"]
    },
    "orders": {
        "required_fields": ["orders", "timestamp"],
        "optional_fields": []
    },
    "learning_insights": {
        "required_fields": ["current_session", "model_status", "recommendations", "timestamp"],
        "optional_fields": []
    },
    "learning_sessions": {
        "required_fields": ["sessions", "total_sessions", "timestamp"],
        "optional_fields": []
    },
    "learning_report": {
        "required_fields": ["date", "performance", "market_analysis", "learning_insights", "recommendations"],
        "optional_fields": []
    }
}

# Test Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    "api_response_time": 5.0,  # seconds
    "strategy_analysis_time": 1.0,  # seconds
    "sentiment_analysis_time": 0.5,  # seconds
    "learning_training_time": 10.0,  # seconds
    "memory_usage_mb": 100,  # MB
    "cpu_usage_percent": 50  # percent
}

# Test Data Generators
def generate_mock_stock_data(symbol="AAPL", count=20, base_price=100.0):
    """Generate mock stock data for testing"""
    from datetime import datetime, timedelta
    import random
    
    data = []
    current_price = base_price
    
    for i in range(count):
        # Simulate price movement
        change = random.uniform(-0.02, 0.02)  # ±2% change
        current_price *= (1 + change)
        
        data.append({
            "symbol": symbol,
            "price": round(current_price, 2),
            "open": round(current_price * random.uniform(0.99, 1.01), 2),
            "high": round(current_price * random.uniform(1.00, 1.02), 2),
            "low": round(current_price * random.uniform(0.98, 1.00), 2),
            "close": round(current_price, 2),
            "volume": random.randint(1000000, 10000000),
            "change_percent": round(change * 100, 2),
            "timestamp": (datetime.now() - timedelta(minutes=i)).isoformat()
        })
    
    return data

def generate_mock_features(count=100):
    """Generate mock features for learning system testing"""
    import random
    
    features = []
    for i in range(count):
        features.append({
            'momentum': random.uniform(-0.05, 0.05),
            'rsi': random.uniform(20, 80),
            'volume_ratio': random.uniform(0.5, 2.0),
            'price_change_1d': random.uniform(-0.03, 0.03),
            'price_change_5d': random.uniform(-0.1, 0.1),
            'volatility': random.uniform(0.05, 0.3),
            'sentiment_score': random.uniform(-1.0, 1.0),
            'market_hour': random.randint(9, 16),
            'day_of_week': random.randint(0, 6)
        })
    
    return features

def generate_mock_outcomes(count=100):
    """Generate mock outcomes for learning system testing"""
    import random
    
    outcomes = []
    for i in range(count):
        outcome = random.choice(['profitable', 'loss', 'neutral'])
        pnl = random.uniform(-1000, 1000)
        outcomes.append((outcome, pnl))
    
    return outcomes

# Test Utilities
class TestUtils:
    """Utility functions for testing"""
    
    @staticmethod
    def validate_api_response(response_data, schema_name):
        """Validate API response against schema"""
        if schema_name not in API_SCHEMAS:
            return False, f"Unknown schema: {schema_name}"
        
        schema = API_SCHEMAS[schema_name]
        required_fields = schema["required_fields"]
        
        for field in required_fields:
            if field not in response_data:
                return False, f"Missing required field: {field}"
        
        return True, "Valid"
    
    @staticmethod
    def measure_performance(func, *args, **kwargs):
        """Measure function performance"""
        import time
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = process.cpu_percent()
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = process.cpu_percent()
        
        return {
            "result": result,
            "execution_time": end_time - start_time,
            "memory_usage": end_memory - start_memory,
            "cpu_usage": end_cpu - start_cpu
        }
    
    @staticmethod
    def create_test_portfolio():
        """Create a test portfolio"""
        from simple_api import Portfolio, Position
        
        positions = {
            "AAPL": Position(
                symbol="AAPL",
                quantity=100,
                avg_price=170.0,
                current_price=175.5,
                unrealized_pnl=550.0,
                realized_pnl=0.0,
                market_value=17550.0
            ),
            "MSFT": Position(
                symbol="MSFT",
                quantity=50,
                avg_price=375.0,
                current_price=380.25,
                unrealized_pnl=262.5,
                realized_pnl=0.0,
                market_value=19012.5
            )
        }
        
        return Portfolio(
            cash=59153.5,
            total_value=100000.0,
            positions=positions,
            orders=[],
            performance_metrics={}
        )

if __name__ == "__main__":
    print("Test Configuration Loaded")
    print(f"API Base URL: {TEST_CONFIG['api_base_url']}")
    print(f"Test Symbol: {TEST_CONFIG['test_symbol']}")
    print(f"Mock Data Size: {TEST_CONFIG['mock_data_size']}")
