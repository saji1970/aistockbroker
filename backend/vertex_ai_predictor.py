"""
Enhanced AI Predictor using Google Cloud Vertex AI
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.cloud import aiplatform
from google_cloud_config import google_cloud_config
from data_fetcher import data_fetcher
from technical_analysis import TechnicalAnalyzer

logger = logging.getLogger(__name__)

class VertexAIPredictor:
    """Enhanced AI predictor using Google Cloud Vertex AI."""
    
    def __init__(self):
        """Initialize the Vertex AI predictor."""
        self.initialized = False
        self.model_endpoint = None
        self.technical_analyzer = TechnicalAnalyzer()
        self.data_fetcher = data_fetcher
        
        # Initialize Google Cloud services
        if google_cloud_config.initialized:
            self._initialize_vertex_ai()
        else:
            logger.warning("Google Cloud not initialized. Using fallback mode.")
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI platform."""
        try:
            if google_cloud_config.initialize_ai_platform():
                self.initialized = True
                logger.info("Vertex AI predictor initialized successfully")
            else:
                logger.error("Failed to initialize Vertex AI")
        except Exception as e:
            logger.error(f"Error initializing Vertex AI: {e}")
    
    def predict_stock(self, symbol: str, period: str = "1y") -> Dict:
        """Predict stock performance using Vertex AI."""
        try:
            # Prepare data
            analysis_data = self._prepare_analysis_data(symbol, period)
            
            if not self.initialized:
                return self._fallback_prediction(analysis_data)
            
            # Use Vertex AI for prediction
            prediction = self._vertex_ai_prediction(analysis_data)
            
            return {
                'symbol': symbol,
                'prediction': prediction,
                'confidence': prediction.get('confidence', 0.7),
                'analysis_data': analysis_data,
                'timestamp': datetime.now().isoformat(),
                'model': 'vertex_ai'
            }
            
        except Exception as e:
            logger.error(f"Error predicting stock {symbol}: {e}")
            return self._fallback_prediction({'symbol': symbol})
    
    def _prepare_analysis_data(self, symbol: str, period: str) -> Dict:
        """Prepare comprehensive analysis data."""
        try:
            # Fetch stock data
            stock_data = self.data_fetcher.fetch_stock_data(symbol, period)
            
            # Calculate technical indicators
            analysis_data = self.technical_analyzer.calculate_all_indicators(stock_data)
            
            # Get latest data points
            latest_data = analysis_data.iloc[-1].to_dict()
            
            # Calculate key statistics
            stats = self._calculate_statistics(analysis_data)
            
            # Get technical signals
            signals = self.technical_analyzer.get_signal_summary(analysis_data)
            
            return {
                'symbol': symbol,
                'latest_data': latest_data,
                'statistics': stats,
                'signals': signals,
                'data_points': len(analysis_data),
                'date_range': {
                    'start': analysis_data.index[0].strftime('%Y-%m-%d'),
                    'end': analysis_data.index[-1].strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            logger.error(f"Error preparing analysis data: {e}")
            return {'symbol': symbol, 'error': str(e)}
    
    def _vertex_ai_prediction(self, analysis_data: Dict) -> Dict:
        """Make prediction using Vertex AI."""
        try:
            # Prepare features for ML model
            features = self._extract_features(analysis_data)
            
            # For now, use a simple model endpoint
            # In production, you would deploy a custom model to Vertex AI
            prediction = self._simple_ml_prediction(features)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error in Vertex AI prediction: {e}")
            return self._fallback_prediction(analysis_data)
    
    def _extract_features(self, analysis_data: Dict) -> Dict:
        """Extract features for ML model."""
        latest_data = analysis_data.get('latest_data', {})
        stats = analysis_data.get('statistics', {})
        signals = analysis_data.get('signals', {})
        
        features = {
            'price': latest_data.get('Close', 0),
            'volume': latest_data.get('Volume', 0),
            'rsi': latest_data.get('RSI', 50),
            'macd': latest_data.get('MACD', 0),
            'bollinger_upper': latest_data.get('BB_Upper', 0),
            'bollinger_lower': latest_data.get('BB_Lower', 0),
            'sma_20': latest_data.get('SMA_20', 0),
            'sma_50': latest_data.get('SMA_50', 0),
            'price_change_1d': stats.get('price_change_1d', 0),
            'price_change_1d_pct': stats.get('price_change_1d_pct', 0),
            'volatility': stats.get('volatility', 0),
            'signal_strength': signals.get('overall_signal', 0)
        }
        
        return features
    
    def _simple_ml_prediction(self, features: Dict) -> Dict:
        """Simple ML prediction (placeholder for Vertex AI model)."""
        # This is a simplified prediction algorithm
        # In production, you would use a trained model deployed on Vertex AI
        
        price = features.get('price', 0)
        rsi = features.get('rsi', 50)
        macd = features.get('macd', 0)
        signal_strength = features.get('signal_strength', 0)
        
        # Simple prediction logic
        if rsi < 30 and macd > 0:
            prediction = 'buy'
            confidence = 0.8
        elif rsi > 70 and macd < 0:
            prediction = 'sell'
            confidence = 0.8
        else:
            prediction = 'hold'
            confidence = 0.6
        
        # Calculate predicted price change
        if prediction == 'buy':
            price_change_pct = 2.5 + (signal_strength * 2)
        elif prediction == 'sell':
            price_change_pct = -2.5 - (signal_strength * 2)
        else:
            price_change_pct = 0.5 * signal_strength
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'predicted_price_change_pct': price_change_pct,
            'predicted_price': price * (1 + price_change_pct / 100),
            'reasoning': f"RSI: {rsi:.1f}, MACD: {macd:.3f}, Signal: {signal_strength}"
        }
    
    def _fallback_prediction(self, analysis_data: Dict) -> Dict:
        """Fallback prediction when Vertex AI is not available."""
        return {
            'prediction': 'hold',
            'confidence': 0.5,
            'predicted_price_change_pct': 0,
            'predicted_price': analysis_data.get('latest_data', {}).get('Close', 0),
            'reasoning': 'Fallback prediction - Vertex AI not available'
        }
    
    def _calculate_statistics(self, data: pd.DataFrame) -> Dict:
        """Calculate key statistical measures."""
        try:
            returns = data['Close'].pct_change().dropna()
            
            stats = {
                'current_price': data['Close'].iloc[-1],
                'price_change_1d': data['Close'].iloc[-1] - data['Close'].iloc[-2],
                'price_change_1d_pct': ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100,
                'volatility': returns.std() * np.sqrt(252) * 100,  # Annualized volatility
                'max_drawdown': self._calculate_max_drawdown(data['Close']),
                'sharpe_ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown."""
        try:
            peak = prices.expanding(min_periods=1).max()
            drawdown = (prices - peak) / peak
            return drawdown.min() * 100
        except Exception:
            return 0.0
    
    def batch_predict(self, symbols: List[str], period: str = "1y") -> List[Dict]:
        """Predict multiple stocks."""
        predictions = []
        
        for symbol in symbols:
            try:
                prediction = self.predict_stock(symbol, period)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Error predicting {symbol}: {e}")
                predictions.append({
                    'symbol': symbol,
                    'error': str(e),
                    'prediction': 'error'
                })
        
        return predictions
    
    def get_model_status(self) -> Dict:
        """Get model status and information."""
        return {
            'initialized': self.initialized,
            'model_type': 'vertex_ai',
            'google_cloud_status': google_cloud_config.get_project_info(),
            'endpoint': self.model_endpoint
        }

# Global instance
vertex_ai_predictor = VertexAIPredictor() 