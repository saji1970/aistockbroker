#!/usr/bin/env python3
"""
Flask API Server for AI Stock Trading Platform
Provides REST API endpoints for the React frontend
"""

import os
# Set environment variables first
os.environ['GOOGLE_API_KEY'] = 'AIzaSyBGgBC9HhFBImN16B1W3tCIsK8W7GMNOMQ'

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from datetime import datetime
import logging
import numpy as np
import pandas as pd
from enum import Enum
import yfinance as yf

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemini_predictor import GeminiStockPredictor
from portfolio_manager import PortfolioManager, SignalType, AssetType
from enhanced_portfolio_manager import EnhancedPortfolioManager, PortfolioConfig
from enhanced_auto_trader import EnhancedAutoTrader, TradingGoal, TradingStrategy
from dataclasses import asdict
from backtest_engine import BacktestEngine
from financial_advisor import FinancialAdvisor
from config import Config
from sensitivity_analysis import SensitivityAnalyzer
from technical_analysis import TechnicalAnalyzer
from data_fetcher import data_fetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

def convert_numpy_types(obj):
    """Convert numpy types and custom objects to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, Enum):
        return obj.value if hasattr(obj, 'value') else str(obj)
    elif hasattr(obj, '__dict__') and not isinstance(obj, (dict, list, str, int, float, bool)):
        # Handle dataclasses and custom objects
        return {key: convert_numpy_types(value) for key, value in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

# Initialize AI predictor
predictor = None
try:
    predictor = GeminiStockPredictor(data_fetcher)
    logger.info("AI Predictor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AI Predictor: {e}")
    predictor = None

# Initialize portfolio manager
try:
    portfolio_manager = PortfolioManager(initial_capital=100000.0)  # Default $100k
    logger.info("Portfolio manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize portfolio manager: {e}")
    portfolio_manager = None

# Initialize enhanced portfolio manager
try:
    enhanced_portfolio_manager = EnhancedPortfolioManager(
        investment_amount=100000.0,  # Default $100k
        portfolio_name="Main Portfolio",
        ai_predictor=predictor,
        data_fetcher=predictor.data_fetcher if predictor else None
    )
    logger.info("Enhanced portfolio manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize enhanced portfolio manager: {e}")
    enhanced_portfolio_manager = None

# Initialize enhanced auto trader
try:
    enhanced_auto_trader = EnhancedAutoTrader(
        portfolio_manager=enhanced_portfolio_manager,
        ai_predictor=predictor,
        data_fetcher=predictor.data_fetcher if predictor else None
    )
    logger.info("Enhanced auto trader initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize enhanced auto trader: {e}")
    enhanced_auto_trader = None

# Initialize financial advisor
financial_advisor = None
try:
    financial_advisor = FinancialAdvisor()
    logger.info("Financial Advisor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Financial Advisor: {e}")
    financial_advisor = None

# Financial Advisor endpoints
@app.route('/api/financial-advisor/create-profile', methods=['POST'])
def create_client_profile():
    """Create a client financial profile"""
    try:
        data = request.get_json()
        
        if not financial_advisor:
            return jsonify({'error': 'Financial advisor not available'}), 500
        
        required_fields = ['age', 'income', 'net_worth', 'risk_tolerance', 'goals', 'time_horizon']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        client_profile = financial_advisor.create_client_profile(
            age=data['age'],
            income=data['income'],
            net_worth=data['net_worth'],
            risk_tolerance=data['risk_tolerance'],
            goals=data['goals'],
            time_horizon=data['time_horizon'],
            liquidity_needs=data.get('liquidity_needs', 0),
            existing_investments=data.get('existing_investments', {}),
            debt_obligations=data.get('debt_obligations', {})
        )
        
        return jsonify({
            'message': 'Client profile created successfully',
            'client_profile': {
                'age': client_profile.age,
                'income': client_profile.income,
                'net_worth': client_profile.net_worth,
                'risk_tolerance': client_profile.risk_tolerance.value,
                'investment_goals': [goal.value for goal in client_profile.investment_goals],
                'time_horizon': client_profile.time_horizon.value,
                'tax_bracket': client_profile.tax_bracket
            }
        })
    
    except Exception as e:
        logger.error(f"Error creating client profile: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-advisor/generate-plan', methods=['POST'])
def generate_financial_plan():
    """Generate a comprehensive financial plan"""
    try:
        data = request.get_json()
        
        if not financial_advisor:
            return jsonify({'error': 'Financial advisor not available'}), 500
        
        # Create client profile first
        client_profile = financial_advisor.create_client_profile(
            age=data['age'],
            income=data['income'],
            net_worth=data['net_worth'],
            risk_tolerance=data['risk_tolerance'],
            goals=data['goals'],
            time_horizon=data['time_horizon'],
            liquidity_needs=data.get('liquidity_needs', 0),
            existing_investments=data.get('existing_investments', {}),
            debt_obligations=data.get('debt_obligations', {})
        )
        
        # Generate financial plan
        financial_plan = financial_advisor.generate_financial_plan(client_profile)
        
        # Generate advice summary
        advice_summary = financial_advisor.generate_advice_summary(financial_plan)
        
        return jsonify({
            'message': 'Financial plan generated successfully',
            'advice_summary': advice_summary,
            'financial_plan': {
                'asset_allocation': financial_plan.asset_allocation,
                'investment_recommendations': [
                    {
                        'symbol': rec.symbol,
                        'name': rec.name,
                        'allocation_percentage': rec.allocation_percentage,
                        'investment_amount': rec.investment_amount,
                        'risk_level': rec.risk_level,
                        'expected_return': rec.expected_return,
                        'rationale': rec.rationale,
                        'alternatives': rec.alternatives
                    }
                    for rec in financial_plan.investment_recommendations
                ],
                'risk_assessment': financial_plan.risk_assessment,
                'retirement_planning': financial_plan.retirement_planning,
                'tax_strategies': financial_plan.tax_strategies,
                'insurance_recommendations': financial_plan.insurance_recommendations,
                'debt_management': financial_plan.debt_management,
                'emergency_fund_strategy': financial_plan.emergency_fund_strategy,
                'monitoring_plan': financial_plan.monitoring_plan
            }
        })
    
    except Exception as e:
        logger.error(f"Error generating financial plan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-advisor/retirement-planning', methods=['POST'])
def get_retirement_planning():
    """Get retirement planning analysis"""
    try:
        data = request.get_json()
        
        if not financial_advisor:
            return jsonify({'error': 'Financial advisor not available'}), 500
        
        client_profile = financial_advisor.create_client_profile(
            age=data['age'],
            income=data['income'],
            net_worth=data['net_worth'],
            risk_tolerance=data['risk_tolerance'],
            goals=['retirement'],
            time_horizon=data['time_horizon'],
            existing_investments=data.get('existing_investments', {})
        )
        
        retirement_plan = financial_advisor._create_retirement_plan(client_profile)
        
        return jsonify({
            'message': 'Retirement planning analysis completed',
            'retirement_plan': retirement_plan
        })
    
    except Exception as e:
        logger.error(f"Error generating retirement plan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-advisor/risk-assessment', methods=['POST'])
def get_risk_assessment():
    """Get portfolio risk assessment"""
    try:
        data = request.get_json()
        
        if not financial_advisor:
            return jsonify({'error': 'Financial advisor not available'}), 500
        
        client_profile = financial_advisor.create_client_profile(
            age=data['age'],
            income=data['income'],
            net_worth=data['net_worth'],
            risk_tolerance=data['risk_tolerance'],
            goals=data.get('goals', ['wealth_building']),
            time_horizon=data['time_horizon']
        )
        
        asset_allocation = financial_advisor._calculate_asset_allocation(client_profile)
        risk_assessment = financial_advisor._assess_portfolio_risk(client_profile, asset_allocation)
        
        return jsonify({
            'message': 'Risk assessment completed',
            'asset_allocation': asset_allocation,
            'risk_assessment': risk_assessment
        })
    
    except Exception as e:
        logger.error(f"Error generating risk assessment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-advisor/tax-strategies', methods=['POST'])
def get_tax_strategies():
    """Get tax-efficient investment strategies"""
    try:
        data = request.get_json()
        
        if not financial_advisor:
            return jsonify({'error': 'Financial advisor not available'}), 500
        
        client_profile = financial_advisor.create_client_profile(
            age=data['age'],
            income=data['income'],
            net_worth=data['net_worth'],
            risk_tolerance=data['risk_tolerance'],
            goals=data.get('goals', ['tax_efficiency']),
            time_horizon=data['time_horizon'],
            existing_investments=data.get('existing_investments', {})
        )
        
        tax_strategies = financial_advisor._recommend_tax_strategies(client_profile)
        
        return jsonify({
            'message': 'Tax strategies generated',
            'tax_strategies': tax_strategies
        })
    
    except Exception as e:
        logger.error(f"Error generating tax strategies: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_predictor_available': predictor is not None
    })

# Stock data endpoints (legacy - keeping for compatibility)
@app.route('/api/stock/data', methods=['GET'])
def get_stock_data_legacy():
    """Get stock data (legacy endpoint)"""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        period = request.args.get('period', '1y')
        interval = request.args.get('interval', '1d')
        
        if not predictor:
            return jsonify({'error': 'AI predictor not available'}), 500
        
        data = predictor.data_fetcher.fetch_stock_data(symbol, period, interval)
        if data is None or data.empty:
            return jsonify({'error': 'No data available'}), 404
        
        # Convert to JSON-serializable format
        recent_data = data.tail(100)
        data_records = []
        for idx, row in recent_data.iterrows():
            record = row.to_dict()
            record['Date'] = idx.isoformat() if hasattr(idx, 'isoformat') else str(idx)
            data_records.append(convert_numpy_types(record))
        
        latest_data = convert_numpy_types(data.iloc[-1].to_dict()) if not data.empty else {}
        
        result = {
            'symbol': symbol,
            'period': period,
            'interval': interval,
            'data': data_records,
            'latest_data': latest_data,
            'statistics': convert_numpy_types({
                'current_price': data['Close'].iloc[-1] if not data.empty else 0,
                'price_change_1d': (data['Close'].iloc[-1] - data['Close'].iloc[-2]) if len(data) > 1 else 0,
                'price_change_1d_pct': ((data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100) if len(data) > 1 else 0,
                'volume': data['Volume'].iloc[-1] if not data.empty else 0,
                'market_cap': 0,  # Would need to fetch from stock info
            })
        }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/info', methods=['GET'])
def get_stock_info_legacy():
    """Get stock information (legacy endpoint)"""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        
        if not predictor:
            return jsonify({'error': 'AI predictor not available'}), 500
        
        info = predictor.data_fetcher.get_stock_info(symbol)
        return jsonify(convert_numpy_types(info))
    
    except Exception as e:
        logger.error(f"Error fetching stock info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/technical', methods=['GET'])
def get_technical_indicators():
    """Get technical indicators"""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        period = request.args.get('period', '1y')
        
        if not predictor:
            return jsonify({'error': 'AI predictor not available'}), 500
        
        analysis_data = predictor.prepare_analysis_data(symbol, period)
        return jsonify(convert_numpy_types(analysis_data))
    
    except Exception as e:
        logger.error(f"Error fetching technical indicators: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/comprehensive', methods=['GET'])
def get_comprehensive_analysis():
    """Get comprehensive technical analysis for any instrument"""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        period = request.args.get('period', '1y')
        interval = request.args.get('interval', '1d')
        
        if not predictor:
            return jsonify({'error': 'AI predictor not available'}), 500
        
        # Get stock data
        stock_data = predictor.data_fetcher.fetch_stock_data(symbol, period, interval)
        if stock_data is None or stock_data.empty:
            return jsonify({'error': 'No data available for symbol'}), 404
        
        # Get technical indicators
        analysis_data = predictor.prepare_analysis_data(symbol, period)
        
        # Get stock info
        stock_info = predictor.data_fetcher.get_stock_info(symbol)
        
        # Determine instrument type
        instrument_type = 'stock'
        if symbol.endswith('-USD'):
            instrument_type = 'crypto'
        elif symbol.startswith('^'):
            instrument_type = 'index'
        elif any(etf in symbol.upper() for etf in ['SPY', 'QQQ', 'VTI', 'VOO', 'ARKK', 'GLD', 'BND', 'IWM']):
            instrument_type = 'etf'
        
        # Calculate additional metrics
        latest_data = stock_data.iloc[-1] if not stock_data.empty else {}
        prev_data = stock_data.iloc[-2] if len(stock_data) > 1 else latest_data
        
        # Price analysis
        current_price = latest_data.get('Close', 0)
        prev_price = prev_data.get('Close', current_price)
        price_change = current_price - prev_price
        price_change_pct = ((current_price / prev_price - 1) * 100) if prev_price > 0 else 0
        
        # Volume analysis
        current_volume = latest_data.get('Volume', 0)
        avg_volume = stock_data['Volume'].mean() if 'Volume' in stock_data.columns else 0
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Volatility analysis
        returns = stock_data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility
        
        # Trend analysis
        sma_20 = analysis_data.get('latest_data', {}).get('SMA_20', current_price)
        sma_50 = analysis_data.get('latest_data', {}).get('SMA_50', current_price)
        trend_strength = 'bullish' if sma_20 > sma_50 else 'bearish'
        
        # RSI analysis
        rsi = analysis_data.get('latest_data', {}).get('RSI', 50)
        rsi_signal = 'overbought' if rsi > 70 else 'oversold' if rsi < 30 else 'neutral'
        
        # MACD analysis
        macd = analysis_data.get('latest_data', {}).get('MACD', 0)
        macd_signal = analysis_data.get('latest_data', {}).get('MACD_Signal', 0)
        macd_trend = 'bullish' if macd > macd_signal else 'bearish'
        
        # Bollinger Bands analysis
        bb_position = analysis_data.get('latest_data', {}).get('BB_Position', 0.5)
        bb_signal = 'upper_band' if bb_position > 0.8 else 'lower_band' if bb_position < 0.2 else 'middle_range'
        
        # Support and Resistance
        support_level = analysis_data.get('latest_data', {}).get('Support_Level', current_price * 0.95)
        resistance_level = analysis_data.get('latest_data', {}).get('Resistance_Level', current_price * 1.05)
        
        # Overall signal strength
        signal_strength = 0
        if trend_strength == 'bullish': signal_strength += 1
        if rsi_signal == 'oversold': signal_strength += 1
        if macd_trend == 'bullish': signal_strength += 1
        if bb_signal == 'lower_band': signal_strength += 1
        
        overall_signal = 'strong_buy' if signal_strength >= 3 else 'buy' if signal_strength >= 2 else 'hold' if signal_strength >= 1 else 'sell'
        
        comprehensive_analysis = {
            'symbol': symbol,
            'instrument_type': instrument_type,
            'period': period,
            'interval': interval,
            'current_price': current_price,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'volume': current_volume,
            'volume_ratio': volume_ratio,
            'volatility': volatility,
            'trend_analysis': {
                'trend_strength': trend_strength,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'trend_direction': 'up' if sma_20 > sma_50 else 'down'
            },
            'momentum_analysis': {
                'rsi': rsi,
                'rsi_signal': rsi_signal,
                'macd': macd,
                'macd_signal': macd_signal,
                'macd_trend': macd_trend,
                'stochastic_k': analysis_data.get('latest_data', {}).get('Stoch_K', 50),
                'stochastic_d': analysis_data.get('latest_data', {}).get('Stoch_D', 50),
                'williams_r': analysis_data.get('latest_data', {}).get('Williams_R', -50)
            },
            'volatility_analysis': {
                'bollinger_position': bb_position,
                'bollinger_signal': bb_signal,
                'atr': analysis_data.get('latest_data', {}).get('ATR', 0),
                'keltner_upper': analysis_data.get('latest_data', {}).get('Keltner_Upper', current_price * 1.02),
                'keltner_lower': analysis_data.get('latest_data', {}).get('Keltner_Lower', current_price * 0.98)
            },
            'support_resistance': {
                'support_level': support_level,
                'resistance_level': resistance_level,
                'distance_to_support': ((current_price - support_level) / current_price) * 100,
                'distance_to_resistance': ((resistance_level - current_price) / current_price) * 100
            },
            'volume_analysis': {
                'obv': analysis_data.get('latest_data', {}).get('OBV', 0),
                'adl': analysis_data.get('latest_data', {}).get('ADL', 0),
                'cmf': analysis_data.get('latest_data', {}).get('CMF', 0),
                'volume_trend': 'increasing' if volume_ratio > 1.2 else 'decreasing' if volume_ratio < 0.8 else 'normal'
            },
            'overall_signal': overall_signal,
            'signal_strength': signal_strength,
            'risk_level': 'high' if volatility > 50 else 'medium' if volatility > 25 else 'low',
            'stock_info': stock_info,
            'technical_data': analysis_data
        }
        
        return jsonify(convert_numpy_types(comprehensive_analysis))
    
    except Exception as e:
        logger.error(f"Error getting comprehensive analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/instruments/search', methods=['GET'])
def search_instruments():
    """Search for instruments by symbol or name"""
    try:
        query = request.args.get('q', '').upper()
        
        # Predefined popular instruments
        popular_instruments = {
            'stocks': [
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'stock'},
                {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'type': 'stock'},
                {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'type': 'stock'},
                {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'type': 'stock'},
                {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'type': 'stock'},
                {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'type': 'stock'},
                {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'type': 'stock'},
                {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'type': 'stock'},
                {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.', 'type': 'stock'},
                {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'type': 'stock'},
            ],
            'etfs': [
                {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF', 'type': 'etf'},
                {'symbol': 'QQQ', 'name': 'Invesco QQQ Trust', 'type': 'etf'},
                {'symbol': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'type': 'etf'},
                {'symbol': 'VOO', 'name': 'Vanguard S&P 500 ETF', 'type': 'etf'},
                {'symbol': 'ARKK', 'name': 'ARK Innovation ETF', 'type': 'etf'},
                {'symbol': 'GLD', 'name': 'SPDR Gold Trust', 'type': 'etf'},
                {'symbol': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'type': 'etf'},
                {'symbol': 'IWM', 'name': 'iShares Russell 2000 ETF', 'type': 'etf'},
                {'symbol': 'TQQQ', 'name': 'ProShares UltraPro QQQ', 'type': 'etf'},
                {'symbol': 'SQQQ', 'name': 'ProShares UltraPro Short QQQ', 'type': 'etf'},
            ],
            'crypto': [
                {'symbol': 'BTC-USD', 'name': 'Bitcoin', 'type': 'crypto'},
                {'symbol': 'ETH-USD', 'name': 'Ethereum', 'type': 'crypto'},
                {'symbol': 'ADA-USD', 'name': 'Cardano', 'type': 'crypto'},
                {'symbol': 'DOT-USD', 'name': 'Polkadot', 'type': 'crypto'},
                {'symbol': 'LINK-USD', 'name': 'Chainlink', 'type': 'crypto'},
                {'symbol': 'UNI-USD', 'name': 'Uniswap', 'type': 'crypto'},
                {'symbol': 'SOL-USD', 'name': 'Solana', 'type': 'crypto'},
                {'symbol': 'MATIC-USD', 'name': 'Polygon', 'type': 'crypto'},
            ],
            'indices': [
                {'symbol': '^GSPC', 'name': 'S&P 500', 'type': 'index'},
                {'symbol': '^DJI', 'name': 'Dow Jones Industrial Average', 'type': 'index'},
                {'symbol': '^IXIC', 'name': 'NASDAQ Composite', 'type': 'index'},
                {'symbol': '^VIX', 'name': 'CBOE Volatility Index', 'type': 'index'},
                {'symbol': '^RUT', 'name': 'Russell 2000', 'type': 'index'},
                {'symbol': '^FTSE', 'name': 'FTSE 100', 'type': 'index'},
            ]
        }
        
        results = []
        if query:
            for category, instruments in popular_instruments.items():
                for instrument in instruments:
                    if (query in instrument['symbol'] or 
                        query in instrument['name'].upper()):
                        results.append(instrument)
        
        return jsonify({
            'query': query,
            'results': results[:20],  # Limit to 20 results
            'total': len(results)
        })
    
    except Exception as e:
        logger.error(f"Error searching instruments: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/instruments/popular', methods=['GET'])
def get_popular_instruments():
    """Get popular instruments by category"""
    try:
        popular_instruments = {
            'stocks': [
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'stock'},
                {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'type': 'stock'},
                {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'type': 'stock'},
                {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'type': 'stock'},
                {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'type': 'stock'},
                {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'type': 'stock'},
                {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'type': 'stock'},
                {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'type': 'stock'},
            ],
            'etfs': [
                {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF', 'type': 'etf'},
                {'symbol': 'QQQ', 'name': 'Invesco QQQ Trust', 'type': 'etf'},
                {'symbol': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'type': 'etf'},
                {'symbol': 'VOO', 'name': 'Vanguard S&P 500 ETF', 'type': 'etf'},
                {'symbol': 'ARKK', 'name': 'ARK Innovation ETF', 'type': 'etf'},
                {'symbol': 'GLD', 'name': 'SPDR Gold Trust', 'type': 'etf'},
                {'symbol': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'type': 'etf'},
                {'symbol': 'IWM', 'name': 'iShares Russell 2000 ETF', 'type': 'etf'},
            ],
            'crypto': [
                {'symbol': 'BTC-USD', 'name': 'Bitcoin', 'type': 'crypto'},
                {'symbol': 'ETH-USD', 'name': 'Ethereum', 'type': 'crypto'},
                {'symbol': 'ADA-USD', 'name': 'Cardano', 'type': 'crypto'},
                {'symbol': 'DOT-USD', 'name': 'Polkadot', 'type': 'crypto'},
                {'symbol': 'LINK-USD', 'name': 'Chainlink', 'type': 'crypto'},
                {'symbol': 'UNI-USD', 'name': 'Uniswap', 'type': 'crypto'},
            ],
            'indices': [
                {'symbol': '^GSPC', 'name': 'S&P 500', 'type': 'index'},
                {'symbol': '^DJI', 'name': 'Dow Jones Industrial Average', 'type': 'index'},
                {'symbol': '^IXIC', 'name': 'NASDAQ Composite', 'type': 'index'},
                {'symbol': '^VIX', 'name': 'CBOE Volatility Index', 'type': 'index'},
            ]
        }
        
        return jsonify(popular_instruments)
    
    except Exception as e:
        logger.error(f"Error getting popular instruments: {e}")
        return jsonify({'error': str(e)}), 500

# AI prediction endpoints (commented out - using enhanced version below)
# @app.route('/api/prediction', methods=['GET'])
# def get_prediction():
#     """Get AI prediction"""
#     try:
#         symbol = request.args.get('symbol', 'AAPL')
#         period = request.args.get('period', '1y')
#         
#         if not predictor:
#             return jsonify({'error': 'AI predictor not available'}), 500
#         
#         prediction = predictor.predict_stock(symbol, period)
#         return jsonify(convert_numpy_types(prediction))
#     
#     except Exception as e:
#         logger.error(f"Error getting prediction: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/sensitivity', methods=['GET'])
# def get_sensitivity_analysis():
#     """Get sensitivity analysis"""
#     try:
#         symbol = request.args.get('symbol', 'AAPL')
#         period = request.args.get('period', '1y')
#         
#         if not predictor:
#             return jsonify({'error': 'AI predictor not available'}), 500
#         
#         sensitivity = predictor.perform_sensitivity_analysis(symbol, period)
#         return jsonify(convert_numpy_types(sensitivity))
#     
#     except Exception as e:
#         logger.error(f"Error getting sensitivity analysis: {e}")
#         return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations', methods=['POST'])
def get_smart_recommendations():
    """Get smart recommendations"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'AAPL')
        user_preferences = data.get('userPreferences', {})
        
        if not predictor:
            return jsonify({'error': 'AI predictor not available'}), 500
        
        recommendations = predictor.generate_smart_recommendations(symbol, user_preferences)
        return jsonify(recommendations)
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/growth', methods=['POST'])
def get_portfolio_growth():
    """Get portfolio growth analysis"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', ['AAPL', 'MSFT', 'GOOGL'])
        initial_investment = data.get('initialInvestment', 10000)
        time_horizon = data.get('timeHorizon', '1y')
        
        if not predictor:
            return jsonify({'error': 'AI predictor not available'}), 500
        
        growth = predictor.predict_portfolio_growth(symbols, initial_investment, time_horizon)
        return jsonify(growth)
    
    except Exception as e:
        logger.error(f"Error getting portfolio growth: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/etf/analysis', methods=['GET'])
def get_etf_analysis():
    """Get ETF analysis"""
    try:
        symbol = request.args.get('symbol', 'SPY')
        period = request.args.get('period', '1y')
        
        if not predictor:
            return jsonify({'error': 'AI predictor not available'}), 500
        
        analysis = predictor.analyze_etf_performance(symbol, period)
        return jsonify(analysis)
    
    except Exception as e:
        logger.error(f"Error getting ETF analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies/money-growth', methods=['POST'])
def get_money_growth_strategies():
    """Get money growth strategies"""
    try:
        data = request.get_json()
        initial_investment = data.get('initialInvestment', 10000)
        risk_tolerance = data.get('riskTolerance', 'moderate')
        time_horizon = data.get('timeHorizon', '1y')
        
        if not predictor:
            return jsonify({'error': 'AI predictor not available'}), 500
        
        strategies = predictor.predict_money_growth_strategies(
            initial_investment, risk_tolerance, time_horizon
        )
        return jsonify(strategies)
    
    except Exception as e:
        logger.error(f"Error getting money growth strategies: {e}")
        return jsonify({'error': str(e)}), 500

# Portfolio management endpoints
@app.route('/api/portfolio/initialize', methods=['POST'])
def initialize_portfolio():
    """Initialize a new portfolio with initial capital."""
    try:
        data = request.get_json()
        initial_capital = data.get('initial_capital', 10000)
        
        # Initialize portfolio manager
        portfolio_manager.initialize_portfolio(initial_capital)
        
        # Get current portfolio state
        portfolio_data = portfolio_manager.get_portfolio_summary()
        
        return jsonify({
            'success': True,
            'message': f'Portfolio initialized with ${initial_capital:,.2f}',
            'total_capital': portfolio_data['total_capital'],
            'available_cash': portfolio_data['available_cash'],
            'total_value': portfolio_data['total_value'],
            'assets': portfolio_data['assets'],
            'performance_history': portfolio_data['performance_history'],
            'signals_history': portfolio_data['signals_history']
        })
    except Exception as e:
        logger.error(f"Error initializing portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio state."""
    try:
        portfolio_data = portfolio_manager.get_portfolio_summary()
        return jsonify(portfolio_data)
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/add-capital', methods=['POST'])
def add_capital():
    """Add capital to the portfolio."""
    try:
        data = request.get_json()
        amount = data.get('amount', 0)
        
        portfolio_manager.add_capital(amount)
        portfolio_data = portfolio_manager.get_portfolio_summary()
        
        return jsonify({
            'success': True,
            'message': f'Added ${amount:,.2f} to portfolio',
            'total_capital': portfolio_data['total_capital'],
            'available_cash': portfolio_data['available_cash'],
            'total_value': portfolio_data['total_value'],
            'assets': portfolio_data['assets'],
            'performance_history': portfolio_data['performance_history'],
            'signals_history': portfolio_data['signals_history']
        })
    except Exception as e:
        logger.error(f"Error adding capital: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/buy', methods=['POST'])
def buy_stock():
    """Buy shares of a stock."""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        shares = data.get('shares', 0)
        price = data.get('price', 0)
        
        if not symbol or shares <= 0 or price <= 0:
            return jsonify({'error': 'Invalid parameters'}), 400
        
        # Execute buy order
        success = portfolio_manager.buy_stock(symbol, shares, price)
        
        if success:
            portfolio_data = portfolio_manager.get_portfolio_summary()
            return jsonify({
                'success': True,
                'message': f'Bought {shares} shares of {symbol} at ${price:.2f}',
                'portfolio': portfolio_data
            })
        else:
            return jsonify({'error': 'Insufficient funds or invalid order'}), 400
    except Exception as e:
        logger.error(f"Error buying stock: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/sell', methods=['POST'])
def sell_stock():
    """Sell shares of a stock."""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        shares = data.get('shares', 0)
        price = data.get('price', 0)
        
        if not symbol or shares <= 0 or price <= 0:
            return jsonify({'error': 'Invalid parameters'}), 400
        
        # Execute sell order
        success = portfolio_manager.sell_stock(symbol, shares, price)
        
        if success:
            portfolio_data = portfolio_manager.get_portfolio_summary()
            return jsonify({
                'success': True,
                'message': f'Sold {shares} shares of {symbol} at ${price:.2f}',
                'portfolio': portfolio_data
            })
        else:
            return jsonify({'error': 'Insufficient shares or invalid order'}), 400
    except Exception as e:
        logger.error(f"Error selling stock: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/performance', methods=['GET'])
def get_portfolio_performance():
    """Get portfolio performance metrics."""
    try:
        period = request.args.get('period', '1y')
        performance_data = portfolio_manager.get_performance_metrics(period)
        return jsonify(performance_data)
    except Exception as e:
        logger.error(f"Error getting portfolio performance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/generate-signals', methods=['POST'])
def generate_signals():
    """Generate trading signals for specified symbols."""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': 'No symbols provided'}), 400
        
        # Generate signals using the portfolio manager
        signals = portfolio_manager.generate_trading_signals(symbols)
        
        return jsonify({
            'success': True,
            'signals': signals,
            'count': len(signals)
        })
    except Exception as e:
        logger.error(f"Error generating signals: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/reset', methods=['POST'])
def reset_portfolio():
    """Reset the portfolio to initial state."""
    try:
        portfolio_manager.reset_portfolio()
        return jsonify({
            'success': True,
            'message': 'Portfolio reset successfully'
        })
    except Exception as e:
        logger.error(f"Error resetting portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/analytics', methods=['GET'])
def get_portfolio_analytics():
    """Get comprehensive portfolio analytics."""
    try:
        analytics = portfolio_manager.get_analytics()
        return jsonify(analytics)
    except Exception as e:
        logger.error(f"Error getting portfolio analytics: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced Stock Data Endpoints
@app.route('/api/stock/data/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    """Get stock data for a specific symbol."""
    try:
        period = request.args.get('period', '1y')
        interval = request.args.get('interval', '1d')
        
        # Get stock data
        stock_data = predictor.data_fetcher.fetch_stock_data(symbol, period=period, interval=interval)
        
        if stock_data is None or stock_data.empty:
            return jsonify({'error': f'No data available for {symbol}'}), 404
        
        # Convert to JSON-serializable format
        current_price = float(stock_data['Close'].iloc[-1])
        
        # Calculate price change safely
        if len(stock_data) > 1:
            prev_price = float(stock_data['Close'].iloc[-2])
            price_change = current_price - prev_price
            price_change_pct = (price_change / prev_price) * 100
        else:
            price_change = 0.0
            price_change_pct = 0.0
        
        data_dict = {
            'symbol': symbol,
            'period': period,
            'interval': interval,
            'data': stock_data.to_dict('records'),
            'summary': {
                'current_price': current_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'volume': int(stock_data['Volume'].iloc[-1]) if 'Volume' in stock_data.columns else 0,
                'high': float(stock_data['High'].max()),
                'low': float(stock_data['Low'].min()),
                'open': float(stock_data['Open'].iloc[0])
            }
        }
        
        return jsonify(data_dict)
    except Exception as e:
        logger.error(f"Error getting stock data for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/info/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """Get stock information for a specific symbol."""
    try:
        # Try to get stock info using yfinance
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Check if we got valid data
        if not info or len(info) < 5:
            # Try to get basic info from data fetcher
            logger.info(f"Yahoo Finance info failed for {symbol}, trying data fetcher...")
            if predictor and hasattr(predictor, 'data_fetcher'):
                try:
                    # Try to fetch actual data first
                    data = predictor.data_fetcher.fetch_stock_data(symbol, period='5d')
                    if data is not None and not data.empty:
                        # Generate info from real data
                        current_price = float(data['Close'].iloc[-1])
                        prev_close = float(data['Close'].iloc[-2]) if len(data) > 1 else current_price
                        change = current_price - prev_close
                        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
                        
                        sample_info = {
                            'symbol': symbol.upper(),
                            'shortName': f'{symbol.upper()} Corp',
                            'longName': f'{symbol.upper()} Corporation',
                            'currentPrice': current_price,
                            'previousClose': prev_close,
                            'regularMarketPrice': current_price,
                            'regularMarketPreviousClose': prev_close,
                            'regularMarketChange': change,
                            'regularMarketChangePercent': change_pct,
                            'marketCap': current_price * 1000000000,  # Estimate
                            'volume': int(data['Volume'].iloc[-1]) if 'Volume' in data.columns else 1000000,
                            'averageVolume': int(data['Volume'].mean()) if 'Volume' in data.columns else 1000000,
                            'currency': 'USD',
                            'exchange': 'NASDAQ',
                            'quoteType': 'EQUITY',
                            'source': 'real_data'
                        }
                        return jsonify(sample_info)
                except Exception as e:
                    logger.warning(f"Data fetcher failed for {symbol}: {str(e)}")
            
            # Final fallback to sample data
            logger.info(f"Using fallback sample data for {symbol}")
            if predictor and hasattr(predictor, 'data_fetcher'):
                sample_info = predictor.data_fetcher._generate_sample_stock_info(symbol)
                return jsonify(sample_info)
            else:
                return jsonify({'error': f'No data available for {symbol}'}), 404
        
        # Extract relevant information
        stock_info = {
            'symbol': symbol,
            'name': info.get('longName', info.get('shortName', symbol)),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 0),
            'volume': info.get('volume', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'beta': info.get('beta', 0),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'current_price': info.get('currentPrice', 0),
            'previous_close': info.get('previousClose', 0),
            'open': info.get('open', 0),
            'day_high': info.get('dayHigh', 0),
            'day_low': info.get('dayLow', 0)
        }
        
        return jsonify(stock_info)
    except Exception as e:
        logger.error(f"Error getting stock info for {symbol}: {e}")
        # Try fallback sample data
        try:
            if predictor and hasattr(predictor, 'data_fetcher'):
                logger.info(f"Using fallback sample data for {symbol} due to error")
                sample_info = predictor.data_fetcher._generate_sample_stock_info(symbol)
                return jsonify(sample_info)
        except Exception as fallback_error:
            logger.error(f"Fallback also failed for {symbol}: {fallback_error}")
        
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/search', methods=['GET'])
def search_stocks():
    """Search for stocks by symbol or name."""
    try:
        query = request.args.get('q', '').upper()
        
        if not query or len(query) < 1:
            return jsonify({'stocks': []})
        
        # Common stock symbols for search
        common_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
            {'symbol': 'NFLX', 'name': 'Netflix Inc.'},
            {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF'},
            {'symbol': 'QQQ', 'name': 'Invesco QQQ Trust'},
            {'symbol': 'VOO', 'name': 'Vanguard S&P 500 ETF'},
            {'symbol': 'DAL', 'name': 'Delta Air Lines Inc.'},
            {'symbol': 'UAL', 'name': 'United Airlines Holdings Inc.'},
            {'symbol': 'AAL', 'name': 'American Airlines Group Inc.'},
            {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.'},
            {'symbol': 'BAC', 'name': 'Bank of America Corp.'},
            {'symbol': 'WMT', 'name': 'Walmart Inc.'},
            {'symbol': 'JNJ', 'name': 'Johnson & Johnson'},
            {'symbol': 'PG', 'name': 'Procter & Gamble Co.'},
            {'symbol': 'KO', 'name': 'The Coca-Cola Company'}
        ]
        
        # Filter stocks based on query
        filtered_stocks = [
            stock for stock in common_stocks
            if query in stock['symbol'] or query in stock['name'].upper()
        ]
        
        return jsonify({'stocks': filtered_stocks[:10]})  # Limit to 10 results
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced Portfolio Management Endpoints
@app.route('/api/portfolio/enhanced/initialize', methods=['POST'])
def initialize_enhanced_portfolio():
    """Initialize enhanced portfolio with investment amount."""
    try:
        data = request.get_json()
        investment_amount = data.get('investment_amount', 100000.0)
        portfolio_name = data.get('portfolio_name', 'Main Portfolio')
        
        if investment_amount <= 0:
            return jsonify({'error': 'Investment amount must be positive'}), 400
        
        global enhanced_portfolio_manager
        enhanced_portfolio_manager = EnhancedPortfolioManager(
            investment_amount=investment_amount,
            portfolio_name=portfolio_name,
            ai_predictor=predictor,
            data_fetcher=predictor.data_fetcher if predictor else None
        )
        
        return jsonify({
            'success': True,
            'message': f'Enhanced portfolio initialized with ${investment_amount:,.2f}',
            'portfolio_id': enhanced_portfolio_manager.portfolio_id,
            'portfolio_name': portfolio_name,
            'investment_amount': investment_amount
        })
        
    except Exception as e:
        logger.error(f"Error initializing enhanced portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/enhanced/update-investment', methods=['POST'])
def update_investment_amount():
    """Update the investment amount."""
    try:
        if not enhanced_portfolio_manager:
            return jsonify({'error': 'Enhanced portfolio not initialized'}), 400
        
        data = request.get_json()
        new_amount = data.get('investment_amount')
        
        if new_amount is None or new_amount <= 0:
            return jsonify({'error': 'Investment amount must be positive'}), 400
        
        success = enhanced_portfolio_manager.update_investment_amount(new_amount)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Investment amount updated to ${new_amount:,.2f}',
                'new_amount': new_amount,
                'available_cash': enhanced_portfolio_manager.portfolio.available_cash
            })
        else:
            return jsonify({'error': 'Failed to update investment amount'}), 400
            
    except Exception as e:
        logger.error(f"Error updating investment amount: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/enhanced/buy', methods=['POST'])
def buy_shares():
    """Buy shares at market price."""
    try:
        if not enhanced_portfolio_manager:
            return jsonify({'error': 'Enhanced portfolio not initialized'}), 400
        
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        quantity = float(data.get('quantity', 0))  # Convert to float
        price = data.get('price')  # Optional, will use market price if not provided
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        if not quantity or quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
        
        result = enhanced_portfolio_manager.buy_shares(symbol, quantity, price)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'Successfully bought {quantity} shares of {symbol}',
                'transaction_id': result['transaction_id'],
                'details': result
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error buying shares: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/enhanced/sell', methods=['POST'])
def sell_shares():
    """Sell shares at market price."""
    try:
        if not enhanced_portfolio_manager:
            return jsonify({'error': 'Enhanced portfolio not initialized'}), 400
        
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        quantity = float(data.get('quantity', 0))  # Convert to float
        price = data.get('price')  # Optional, will use market price if not provided
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        if not quantity or quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
        
        result = enhanced_portfolio_manager.sell_shares(symbol, quantity, price)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'Successfully sold {quantity} shares of {symbol}',
                'transaction_id': result['transaction_id'],
                'details': result
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error selling shares: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/enhanced/summary', methods=['GET'])
def get_enhanced_portfolio_summary():
    """Get comprehensive portfolio summary."""
    try:
        if not enhanced_portfolio_manager:
            return jsonify({'error': 'Enhanced portfolio not initialized'}), 400
        
        summary = enhanced_portfolio_manager.get_portfolio_summary()
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/enhanced/transactions', methods=['GET'])
def get_transaction_history():
    """Get transaction history."""
    try:
        if not enhanced_portfolio_manager:
            return jsonify({'error': 'Enhanced portfolio not initialized'}), 400
        
        limit = request.args.get('limit', 50, type=int)
        transactions = enhanced_portfolio_manager.get_transaction_history(limit)
        
        return jsonify({
            'transactions': transactions,
            'total_count': len(enhanced_portfolio_manager.portfolio.transactions)
        })
        
    except Exception as e:
        logger.error(f"Error getting transaction history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/enhanced/asset/<symbol>', methods=['GET'])
def get_asset_performance(symbol):
    """Get performance details for a specific asset."""
    try:
        if not enhanced_portfolio_manager:
            return jsonify({'error': 'Enhanced portfolio not initialized'}), 400
        
        symbol = symbol.upper()
        performance = enhanced_portfolio_manager.get_asset_performance(symbol)
        
        if performance:
            return jsonify(performance)
        else:
            return jsonify({'error': f'No position found for {symbol}'}), 404
            
    except Exception as e:
        logger.error(f"Error getting asset performance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/enhanced/current-price/<symbol>', methods=['GET'])
def get_current_price(symbol):
    """Get current market price for a symbol."""
    try:
        if not enhanced_portfolio_manager:
            return jsonify({'error': 'Enhanced portfolio not initialized'}), 400
        
        symbol = symbol.upper()
        price = enhanced_portfolio_manager.get_current_price(symbol)
        
        if price:
            return jsonify({
                'symbol': symbol,
                'current_price': price,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': f'Could not fetch price for {symbol}'}), 404
            
    except Exception as e:
        logger.error(f"Error getting current price: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced Auto Trader Endpoints
@app.route('/api/trader/configure', methods=['POST'])
def configure_auto_trader():
    """Configure the auto trader with goals and parameters."""
    try:
        if not enhanced_auto_trader:
            return jsonify({'error': 'Enhanced auto trader not initialized'}), 400
        
        data = request.get_json()
        
        # Configure trading goal
        goal_config = data.get('goal', {})
        if goal_config:
            success = enhanced_auto_trader.configure_trading_goal(goal_config)
            if not success:
                return jsonify({'error': 'Failed to configure trading goal'}), 400
        
        # Set watchlist
        watchlist = data.get('watchlist', [])
        if watchlist:
            success = enhanced_auto_trader.set_watchlist(watchlist)
            if not success:
                return jsonify({'error': 'Failed to set watchlist'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Auto trader configured successfully',
            'goal': asdict(enhanced_auto_trader.goal),
            'watchlist': enhanced_auto_trader.watchlist
        })
        
    except Exception as e:
        logger.error(f"Error configuring auto trader: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trader/start', methods=['POST'])
def start_auto_trader():
    """Start the automated trading system."""
    try:
        if not enhanced_auto_trader:
            return jsonify({'error': 'Enhanced auto trader not initialized'}), 400
        
        success = enhanced_auto_trader.start_trading()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Automated trading started successfully',
                'status': enhanced_auto_trader.status.value
            })
        else:
            return jsonify({'error': 'Failed to start automated trading'}), 400
            
    except Exception as e:
        logger.error(f"Error starting auto trader: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trader/stop', methods=['POST'])
def stop_auto_trader():
    """Stop the automated trading system."""
    try:
        if not enhanced_auto_trader:
            return jsonify({'error': 'Enhanced auto trader not initialized'}), 400
        
        success = enhanced_auto_trader.stop_trading()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Automated trading stopped successfully',
                'status': enhanced_auto_trader.status.value
            })
        else:
            return jsonify({'error': 'Failed to stop automated trading'}), 400
            
    except Exception as e:
        logger.error(f"Error stopping auto trader: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trader/pause', methods=['POST'])
def pause_auto_trader():
    """Pause the automated trading system."""
    try:
        if not enhanced_auto_trader:
            return jsonify({'error': 'Enhanced auto trader not initialized'}), 400
        
        success = enhanced_auto_trader.pause_trading()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Automated trading paused successfully',
                'status': enhanced_auto_trader.status.value
            })
        else:
            return jsonify({'error': 'Failed to pause automated trading'}), 400
            
    except Exception as e:
        logger.error(f"Error pausing auto trader: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trader/resume', methods=['POST'])
def resume_auto_trader():
    """Resume the automated trading system."""
    try:
        if not enhanced_auto_trader:
            return jsonify({'error': 'Enhanced auto trader not initialized'}), 400
        
        success = enhanced_auto_trader.resume_trading()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Automated trading resumed successfully',
                'status': enhanced_auto_trader.status.value
            })
        else:
            return jsonify({'error': 'Failed to resume automated trading'}), 400
            
    except Exception as e:
        logger.error(f"Error resuming auto trader: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trader/status', methods=['GET'])
def get_auto_trader_status():
    """Get current auto trader status and statistics."""
    try:
        if not enhanced_auto_trader:
            return jsonify({'error': 'Enhanced auto trader not initialized'}), 400
        
        status = enhanced_auto_trader.get_trading_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting auto trader status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trader/history', methods=['GET'])
def get_auto_trader_history():
    """Get auto trader trading history."""
    try:
        if not enhanced_auto_trader:
            return jsonify({'error': 'Enhanced auto trader not initialized'}), 400
        
        history = enhanced_auto_trader.get_trading_history()
        return jsonify({
            'trading_history': history,
            'total_trades': len(history)
        })
        
    except Exception as e:
        logger.error(f"Error getting auto trader history: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced Prediction Endpoints with Sensitivity Analysis
@app.route('/api/prediction/<symbol>', methods=['GET'])
def get_prediction(symbol):
    """Get stock prediction with sensitivity analysis."""
    try:
        if predictor and Config.GOOGLE_API_KEY and hasattr(predictor, 'model') and predictor.model:
            prediction_data = predictor.get_stock_prediction(symbol)
            
            # Check if the prediction contains an error
            if 'error' in prediction_data:
                # Provide helpful error message with suggestions
                error_message = {
                    'error': prediction_data['error'],
                    'message': f'The stock symbol "{symbol}" could not be found or has no available data.',
                    'suggestions': {
                        'check_spelling': f'Please check the spelling of "{symbol}"',
                        'try_popular_stocks': 'Try popular stock symbols like: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA',
                        'verify_market': 'Make sure the stock symbol is valid for the intended market',
                        'check_trading_hours': 'Ensure the request is made during trading hours'
                    },
                    'available_markets': {
                        'US': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'SPY', 'QQQ'],
                        'UK': ['VOD.L', 'HSBA.L', 'BP.L', 'GSK.L', 'ULVR.L', 'RIO.L', 'BHP.L', 'AZN.L'],
                        'India': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS'],
                        'Canada': ['RY.TO', 'TD.TO', 'SHOP.TO', 'ENB.TO', 'TRP.TO', 'BCE.TO'],
                        'Australia': ['CBA.AX', 'CSL.AX', 'BHP.AX', 'RIO.AX', 'WES.AX', 'WOW.AX']
                    },
                    'example_queries': [
                        f'What\'s the prediction for AAPL tomorrow?',
                        f'Give me a comprehensive analysis of MSFT with technical indicators',
                        f'What\'s the market sentiment for GOOGL?',
                        f'Show me top 10 tech stocks in US market',
                        f'Give me investment advice for a conservative investor'
                    ]
                }
                return jsonify(error_message), 404
            
            return jsonify(prediction_data)
        else:
            # Provide helpful message when AI predictor is not available
            if not Config.GOOGLE_API_KEY:
                return jsonify({
                    'error': 'AI prediction service not configured',
                    'message': 'Google API key is required for AI predictions',
                    'status': 'service_unavailable',
                    'fallback_available': True,
                    'suggestions': {
                        'use_technical_analysis': 'Use the technical analysis features which are available',
                        'view_stock_data': 'View current stock data and charts',
                        'check_trading_bot': 'Use the trading bot for automated trading strategies'
                    }
                }), 503
            else:
                return jsonify({
                    'error': 'AI predictor not available',
                    'message': 'The AI prediction service is temporarily unavailable',
                    'status': 'service_unavailable',
                    'fallback_available': True
                }), 503
    except Exception as e:
        logger.error(f"Error getting prediction for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction/<symbol>/sensitivity', methods=['GET'])
def get_prediction_with_sensitivity(symbol):
    """Get stock prediction with detailed sensitivity analysis."""
    try:
        if predictor and Config.GOOGLE_API_KEY and hasattr(predictor, 'model') and predictor.model:
            # Get stock data
            stock_data = predictor.data_fetcher.fetch_stock_data(symbol, period='1y')
            if stock_data is None or stock_data.empty:
                return jsonify({'error': f'No data available for {symbol}'}), 404
            
            # Perform sensitivity analysis
            sensitivity_result = predictor._perform_sensitivity_analysis(symbol, stock_data)
            
            # Get prediction
            prediction_data = predictor.get_stock_prediction(symbol)
            
            # Combine results
            result = {
                'symbol': symbol,
                'prediction': prediction_data,
                'sensitivity_analysis': sensitivity_result,
                'confidence_level': 'High',  # This would be calculated based on analysis
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(result)
        else:
            # Provide helpful message when AI predictor is not available
            if not Config.GOOGLE_API_KEY:
                return jsonify({
                    'error': 'AI prediction service not configured',
                    'message': 'Google API key is required for AI predictions and sensitivity analysis',
                    'status': 'service_unavailable',
                    'fallback_available': True,
                    'suggestions': {
                        'use_technical_analysis': 'Use the technical analysis features which are available',
                        'view_stock_data': 'View current stock data and charts',
                        'check_trading_bot': 'Use the trading bot for automated trading strategies',
                        'use_basic_sensitivity': 'Basic sensitivity analysis is available without AI'
                    }
                }), 503
            else:
                return jsonify({
                    'error': 'AI predictor not available',
                    'message': 'The AI prediction service is temporarily unavailable',
                    'status': 'service_unavailable',
                    'fallback_available': True
                }), 503
    except Exception as e:
        logger.error(f"Error getting prediction with sensitivity for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced Sensitivity Analysis Endpoints
@app.route('/api/sensitivity/analysis/<symbol>', methods=['GET'])
def get_sensitivity_analysis(symbol):
    """Get comprehensive sensitivity analysis for a stock."""
    try:
        # Get stock data - try predictor first, then fallback to direct yfinance
        stock_data = None
        if predictor and hasattr(predictor, 'data_fetcher'):
            stock_data = predictor.data_fetcher.fetch_stock_data(symbol, period='1y')
        
        # Fallback to direct yfinance if predictor is not available
        if stock_data is None or stock_data.empty:
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                stock_data = ticker.history(period='1y')
            except Exception as e:
                logger.error(f"Failed to fetch stock data for {symbol}: {e}")
                stock_data = None
        
        if stock_data is None or stock_data.empty:
            # Provide helpful error message with suggestions
            error_message = {
                'error': f'No data available for {symbol}',
                'message': f'The stock symbol "{symbol}" could not be found or has no available data.',
                'suggestions': {
                    'check_spelling': f'Please check the spelling of "{symbol}"',
                    'try_popular_stocks': 'Try popular stock symbols like: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA',
                    'verify_market': 'Make sure the stock symbol is valid for the intended market',
                    'check_trading_hours': 'Ensure the request is made during trading hours'
                },
                'available_markets': {
                    'US': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'SPY', 'QQQ'],
                    'UK': ['VOD.L', 'HSBA.L', 'BP.L', 'GSK.L', 'ULVR.L', 'RIO.L', 'BHP.L', 'AZN.L'],
                    'India': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS'],
                    'Canada': ['RY.TO', 'TD.TO', 'SHOP.TO', 'ENB.TO', 'TRP.TO', 'BCE.TO'],
                    'Australia': ['CBA.AX', 'CSL.AX', 'BHP.AX', 'RIO.AX', 'WES.AX', 'WOW.AX']
                },
                'example_queries': [
                    f'What\'s the prediction for AAPL tomorrow?',
                    f'Give me a comprehensive analysis of MSFT with technical indicators',
                    f'What\'s the market sentiment for GOOGL?',
                    f'Show me top 10 tech stocks in US market',
                    f'Give me investment advice for a conservative investor'
                ]
            }
            return jsonify(error_message), 404
        
        # Perform sensitivity analysis
        sensitivity_analyzer = SensitivityAnalyzer()
        scenarios = sensitivity_analyzer.create_scenarios({
            'symbol': symbol,
            'current_price': stock_data['Close'].iloc[-1],
            'volatility': stock_data['Close'].pct_change().std() * np.sqrt(252),
            'volume': stock_data['Volume'].iloc[-1] if 'Volume' in stock_data.columns else 1000000,
            'price_change_1d': stock_data['Close'].pct_change().iloc[-1],
            'price_change_5d': stock_data['Close'].pct_change(5).iloc[-1],
            'price_change_20d': stock_data['Close'].pct_change(20).iloc[-1]
        })
        
        # Calculate sensitivity metrics
        sensitivity_metrics = sensitivity_analyzer.calculate_sensitivity_metrics({
            'symbol': symbol,
            'current_price': stock_data['Close'].iloc[-1],
            'volatility': stock_data['Close'].pct_change().std() * np.sqrt(252),
        }, scenarios)
        
        # Generate comprehensive report
        sensitivity_report = sensitivity_analyzer.generate_sensitivity_report({
            'symbol': symbol,
            'current_price': stock_data['Close'].iloc[-1],
            'volatility': stock_data['Close'].pct_change().std() * np.sqrt(252),
        }, scenarios)
        
        return jsonify({
            'symbol': symbol,
            'current_price': float(stock_data['Close'].iloc[-1]),
            'scenarios': {
                name: {
                    'name': scenario.name,
                    'description': scenario.description,
                    'factors': scenario.factors,
                    'expected_impact': scenario.expected_impact,
                    'confidence_level': scenario.confidence_level,
                    'risk_level': scenario.risk_level
                } for name, scenario in scenarios.items()
            },
            'metrics': sensitivity_metrics,
            'report': sensitivity_report,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting sensitivity analysis for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/day-trading/prediction/<symbol>', methods=['POST'])
def get_day_trading_prediction(symbol):
    """Get day trading prediction for a specific date."""
    try:
        data = request.get_json()
        target_date = data.get('target_date')
        
        if not target_date:
            return jsonify({'error': 'Target date is required'}), 400
        
        # Get stock data
        stock_data = predictor.data_fetcher.fetch_stock_data(symbol, period='1mo')
        if stock_data is None or stock_data.empty:
            return jsonify({'error': f'No data available for {symbol}'}), 404
        
        # Perform technical analysis
        technical_analyzer = TechnicalAnalyzer()
        current_price = stock_data['Close'].iloc[-1]
        
        # Calculate technical indicators
        sma_20 = stock_data['Close'].rolling(window=20).mean().iloc[-1]
        ema_12 = stock_data['Close'].ewm(span=12).mean().iloc[-1]
        rsi = technical_analyzer.calculate_rsi(stock_data['Close'], 14)
        
        # Generate day trading prediction
        prediction = generate_day_trading_prediction(symbol, target_date, stock_data, {
            'current_price': current_price,
            'sma_20': sma_20,
            'ema_12': ema_12,
            'rsi': rsi,
            'volatility': stock_data['Close'].pct_change().std() * np.sqrt(252)
        })
        
        return jsonify(prediction)
    except Exception as e:
        logger.error(f"Error getting day trading prediction for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

def generate_day_trading_prediction(symbol, target_date, stock_data, indicators):
    """Generate comprehensive day trading prediction."""
    
    # Calculate support and resistance levels
    high_20 = stock_data['High'].rolling(window=20).max().iloc[-1]
    low_20 = stock_data['Low'].rolling(window=20).min().iloc[-1]
    pivot = (high_20 + low_20 + indicators['current_price']) / 3
    
    # Generate intraday predictions
    volatility_factor = indicators['volatility'] * 100
    base_price = indicators['current_price']
    
    intraday_predictions = {
        'open': {
            'min': base_price * (1 - volatility_factor * 0.01),
            'max': base_price * (1 + volatility_factor * 0.01),
            'expected': base_price * (1 + (np.random.random() - 0.5) * volatility_factor * 0.005)
        },
        'mid_morning': {
            'min': base_price * (1 - volatility_factor * 0.008),
            'max': base_price * (1 + volatility_factor * 0.012),
            'expected': base_price * (1 + (np.random.random() - 0.5) * volatility_factor * 0.01)
        },
        'lunch': {
            'min': base_price * (1 - volatility_factor * 0.006),
            'max': base_price * (1 + volatility_factor * 0.010),
            'expected': base_price * (1 + (np.random.random() - 0.5) * volatility_factor * 0.008)
        },
        'afternoon': {
            'min': base_price * (1 - volatility_factor * 0.008),
            'max': base_price * (1 + volatility_factor * 0.012),
            'expected': base_price * (1 + (np.random.random() - 0.5) * volatility_factor * 0.01)
        },
        'close': {
            'min': base_price * (1 - volatility_factor * 0.010),
            'max': base_price * (1 + volatility_factor * 0.008),
            'expected': base_price * (1 + (np.random.random() - 0.5) * volatility_factor * 0.006)
        }
    }
    
    # Generate trading signals
    signals = []
    if indicators['rsi'] < 30:
        signals.append({
            'time': '09:30-10:30',
            'signal': 'BUY',
            'confidence': 75,
            'reasoning': 'Oversold conditions (RSI < 30) suggest buying opportunity',
            'target_price': base_price * 1.02,
            'stop_loss': base_price * 0.98
        })
    elif indicators['rsi'] > 70:
        signals.append({
            'time': '09:30-10:30',
            'signal': 'SELL',
            'confidence': 70,
            'reasoning': 'Overbought conditions (RSI > 70) suggest selling opportunity',
            'target_price': base_price * 0.98,
            'stop_loss': base_price * 1.02
        })
    else:
        signals.append({
            'time': '09:30-10:30',
            'signal': 'HOLD',
            'confidence': 60,
            'reasoning': 'Neutral RSI conditions, wait for clearer signals',
            'target_price': base_price,
            'stop_loss': base_price * 0.99
        })
    
    # Add more signals based on technical analysis
    if indicators['current_price'] > indicators['sma_20']:
        signals.append({
            'time': '11:00-12:00',
            'signal': 'BUY',
            'confidence': 65,
            'reasoning': 'Price above 20-day SMA indicates bullish trend',
            'target_price': base_price * 1.015,
            'stop_loss': base_price * 0.985
        })
    
    # Risk assessment
    risk_factors = []
    if indicators['volatility'] > 0.3:
        risk_factors.append({
            'factor': 'High Volatility',
            'impact': 'High',
            'description': f'Volatility of {indicators["volatility"]:.2%} indicates high risk',
            'mitigation': 'Use tight stop losses and smaller position sizes'
        })
    
    if abs(indicators['current_price'] - indicators['sma_20']) / indicators['sma_20'] > 0.05:
        risk_factors.append({
            'factor': 'Price Deviation',
            'impact': 'Medium',
            'description': 'Price significantly deviated from moving average',
            'mitigation': 'Wait for price to converge or confirm trend'
        })
    
    # Market sentiment
    sentiment = 'Neutral'
    confidence = 60
    if indicators['current_price'] > indicators['ema_12'] and indicators['rsi'] < 70:
        sentiment = 'Bullish'
        confidence = 70
    elif indicators['current_price'] < indicators['ema_12'] and indicators['rsi'] > 30:
        sentiment = 'Bearish'
        confidence = 65
    
    return {
        'symbol': symbol,
        'target_date': target_date,
        'timestamp': datetime.now().isoformat(),
        'current_price': indicators['current_price'],
        'intraday_predictions': intraday_predictions,
        'signals': signals,
        'risk_factors': risk_factors,
        'technical_levels': {
            'support': [low_20, low_20 * 0.98, low_20 * 0.96],
            'resistance': [high_20, high_20 * 1.02, high_20 * 1.04],
            'pivot': pivot
        },
        'sentiment': {
            'overall': sentiment,
            'confidence': confidence,
            'factors': [
                f'RSI: {indicators["rsi"]:.1f}',
                f'Price vs SMA20: {"Above" if indicators["current_price"] > indicators["sma_20"] else "Below"}',
                f'Volatility: {indicators["volatility"]:.2%}'
            ]
        },
        'indicators': {
            'rsi': indicators['rsi'],
            'sma_20': indicators['sma_20'],
            'ema_12': indicators['ema_12'],
            'volatility': indicators['volatility']
        }
    }

# Chat/NLP endpoints
@app.route('/api/chat/query', methods=['POST'])
def process_query():
    """Process natural language query using AI."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # First, try to use the AI predictor for all queries
        if predictor:
            try:
                result = predictor.process_natural_language_query(query)
                return jsonify(result)
            except Exception as e:
                logger.error(f"AI predictor failed: {e}")
                # Fall through to financial advisor if AI fails
        
        # Only use financial advisor for specific financial planning queries
        # Check for explicit financial planning requests
        financial_planning_keywords = [
            'financial plan', 'financial planning', 'retirement plan', 'retirement planning',
            'investment plan', 'portfolio plan', 'financial advisor', 'financial advice',
            'create financial plan', 'build portfolio', 'investment strategy'
        ]
        
        if any(keyword in query.lower() for keyword in financial_planning_keywords):
            if financial_advisor:
                try:
                    # Provide different responses based on query type
                    if any(word in query.lower() for word in ['etf', 'etfs', 'exchange traded fund']):
                        return jsonify({
                            'response': "Here are some of the best ETFs to consider for different investment strategies:\n\n**📈 Broad Market ETFs (Core Holdings):**\n• **SPY** - SPDR S&P 500 ETF (Large-cap US stocks)\n• **VOO** - Vanguard S&P 500 ETF (Lower expense ratio)\n• **VTI** - Vanguard Total Stock Market ETF (Complete US market)\n• **QQQ** - Invesco QQQ Trust (Technology-heavy)\n\n**🌍 International ETFs (Diversification):**\n• **VXUS** - Vanguard Total International Stock ETF\n• **EFA** - iShares MSCI EAFE ETF (Developed markets)\n• **EEM** - iShares MSCI Emerging Markets ETF\n\n**💰 Bond ETFs (Income & Stability):**\n• **BND** - Vanguard Total Bond Market ETF\n• **AGG** - iShares Core U.S. Aggregate Bond ETF\n• **TLT** - iShares 20+ Year Treasury Bond ETF\n\n**💡 Recommended Strategy:**\n• **Conservative:** 60% BND + 25% VOO + 15% VXUS\n• **Moderate:** 40% VOO + 20% VXUS + 25% BND + 15% QQQ\n• **Aggressive:** 50% VOO + 20% QQQ + 15% VXUS + 15% sector ETFs\n\nWould you like me to create a personalized ETF portfolio based on your financial profile?",
                            'query_type': 'etf_recommendations',
                            'confidence': 0.9
                        })
                    
                    elif any(word in query.lower() for word in ['retirement', 'retire']):
                        return jsonify({
                            'response': "**🏖️ Retirement Planning Services:**\n\nI can help you plan for a secure retirement with:\n\n**1. Retirement Needs Analysis**\n• Calculate required retirement savings\n• Estimate retirement expenses\n• Social Security benefit analysis\n• Retirement income gap identification\n\n**2. Savings Strategy**\n• Monthly savings requirements\n• 401(k) and IRA optimization\n• Catch-up contribution strategies\n• Investment allocation for retirement\n\n**3. Retirement Account Management**\n• Traditional vs Roth IRA decisions\n• 401(k) rollover strategies\n• Required Minimum Distribution (RMD) planning\n• Tax-efficient withdrawal strategies\n\n**4. Retirement Timeline Planning**\n• Years to retirement calculation\n• Retirement readiness assessment\n• Working longer considerations\n• Early retirement planning\n\nTo get your personalized retirement plan, please provide:\n• Your current age and retirement age goal\n• Current income and savings\n• Expected retirement lifestyle\n• Current retirement account balances\n\nWould you like to start your retirement planning analysis?",
                            'query_type': 'retirement_planning',
                            'confidence': 0.9
                        })
                    
                    elif any(word in query.lower() for word in ['risk', 'volatility', 'safe']):
                        return jsonify({
                            'response': "**⚠️ Risk Assessment & Tolerance Analysis:**\n\nI can help you understand and manage investment risk:\n\n**1. Risk Tolerance Evaluation**\n• Conservative: 20-40% stocks, 60-80% bonds\n• Moderate: 40-70% stocks, 30-60% bonds\n• Aggressive: 70-90% stocks, 10-30% bonds\n\n**2. Portfolio Risk Analysis**\n• Volatility assessment\n• Maximum drawdown potential\n• Sharpe ratio calculation\n• Value at Risk (VaR) analysis\n\n**3. Risk Management Strategies**\n• Asset allocation optimization\n• Diversification recommendations\n• Stop-loss strategies\n• Position sizing guidelines\n\n**4. Stress Testing**\n• Market crash scenarios\n• Inflation impact analysis\n• Interest rate sensitivity\n• Economic downturn preparation\n\nTo assess your risk profile, please provide:\n• Your age and investment experience\n• Financial goals and time horizon\n• Comfort level with market volatility\n• Current investment portfolio\n\nWould you like to take a risk assessment quiz?",
                            'query_type': 'risk_assessment',
                            'confidence': 0.9
                        })
                    
                    elif any(word in query.lower() for word in ['start', 'beginner', 'first time', 'how to start']):
                        return jsonify({
                            'response': "**🚀 Getting Started with Investing:**\n\n**Step 1: Build Emergency Fund**\n• Save 3-6 months of expenses\n• Keep in high-yield savings account\n• Don't invest until this is complete\n\n**Step 2: Pay Off High-Interest Debt**\n• Credit cards (15-25% interest)\n• Personal loans\n• Student loans (if >6%)\n\n**Step 3: Choose Investment Account**\n• **401(k):** Employer-sponsored (tax-advantaged)\n• **IRA:** Individual retirement account\n• **Roth IRA:** Tax-free growth (if eligible)\n• **Taxable account:** For additional investments\n\n**Step 4: Start with Index Funds**\n• **VTI** - Total US Stock Market\n• **VOO** - S&P 500 Index\n• **BND** - Total Bond Market\n\n**Step 5: Dollar-Cost Averaging**\n• Invest regularly (monthly)\n• Start with $100-500/month\n• Increase as you earn more\n\n**Step 6: Set Investment Goals**\n• Retirement (long-term)\n• House down payment (medium-term)\n• Emergency fund (short-term)\n\n**💡 Beginner Portfolio:**\n• 70% VTI (US stocks)\n• 20% VXUS (International stocks)\n• 10% BND (Bonds)\n\nWould you like me to help you create a personalized investment plan?",
                            'query_type': 'getting_started',
                            'confidence': 0.9
                        })
                    
                    elif any(word in query.lower() for word in ['diversify', 'diversification', 'portfolio']):
                        return jsonify({
                            'response': "**🌍 Portfolio Diversification Strategy:**\n\n**1. Asset Class Diversification:**\n• **Stocks:** 60-80% (Growth potential)\n• **Bonds:** 20-40% (Stability & income)\n• **Real Estate:** 5-15% (Inflation hedge)\n• **Commodities:** 0-10% (Diversification)\n\n**2. Geographic Diversification:**\n• **US Stocks:** 50-70% (Home bias)\n• **International Developed:** 20-30% (Europe, Japan)\n• **Emerging Markets:** 5-15% (Growth potential)\n\n**3. Sector Diversification:**\n• **Technology:** 15-25%\n• **Healthcare:** 10-15%\n• **Financial:** 10-15%\n• **Consumer:** 10-15%\n• **Other sectors:** 35-55%\n\n**4. Company Size Diversification:**\n• **Large-cap:** 40-60% (Stability)\n• **Mid-cap:** 20-30% (Growth)\n• **Small-cap:** 10-20% (High growth potential)\n\n**5. Investment Vehicles:**\n• **ETFs:** Easy diversification\n• **Index funds:** Low-cost broad exposure\n• **Individual stocks:** Targeted positions\n• **Bonds:** Government and corporate\n\nWould you like me to analyze your current portfolio and suggest diversification improvements?",
                            'query_type': 'diversification',
                            'confidence': 0.9
                        })
                    
                    else:
                        # Extract basic profile information from query for personalized response
                        profile_data = {
                            'age': 35,  # Default age
                            'income': 75000,  # Default income
                            'net_worth': 100000,  # Default net worth
                            'risk_tolerance': 'moderate',  # Default risk tolerance
                            'goals': ['retirement'],  # Default goal
                            'time_horizon': 'long_term'  # Default time horizon
                        }
                        
                        # Try to extract actual values from query
                        import re
                        age_match = re.search(r'(\d+)\s*(?:years?\s+old|age|yo)', query.lower())
                        if age_match:
                            profile_data['age'] = int(age_match.group(1))
                        
                        income_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d{2})?[kKmM]?)\s*(?:per\s+year|salary|income)', query.lower())
                        if income_match:
                            income_str = income_match.group(1).replace(',', '').upper()
                            if 'K' in income_str:
                                profile_data['income'] = float(income_str.replace('K', '')) * 1000
                            elif 'M' in income_str:
                                profile_data['income'] = float(income_str.replace('M', '')) * 1000000
                            else:
                                profile_data['income'] = float(income_str)
                        
                        net_worth_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d{2})?[kKmM]?)\s*(?:net\s+worth|savings|assets)', query.lower())
                        if net_worth_match:
                            net_worth_str = net_worth_match.group(1).replace(',', '').upper()
                            if 'K' in net_worth_str:
                                profile_data['net_worth'] = float(net_worth_str.replace('K', '')) * 1000
                            elif 'M' in net_worth_str:
                                profile_data['net_worth'] = float(net_worth_str.replace('M', '')) * 1000000
                            else:
                                profile_data['net_worth'] = float(net_worth_str)
                        
                        risk_match = re.search(r'(conservative|moderate|aggressive)', query.lower())
                        if risk_match:
                            profile_data['risk_tolerance'] = risk_match.group(1)
                        
                        # Generate financial plan only if we have specific user data
                        if any([age_match, income_match, net_worth_match, risk_match]):
                            client_profile = financial_advisor.create_client_profile(
                                age=profile_data['age'],
                                income=profile_data['income'],
                                net_worth=profile_data['net_worth'],
                                risk_tolerance=profile_data['risk_tolerance'],
                                goals=profile_data['goals'],
                                time_horizon=profile_data['time_horizon']
                            )
                            
                            financial_plan = financial_advisor.generate_financial_plan(client_profile)
                            advice_summary = financial_advisor.generate_advice_summary(financial_plan)
                            
                            return jsonify({
                                'response': f"I'll help you with financial planning! Here's a personalized financial plan based on your profile:\n\n{advice_summary}\n\n*Note: This is financial advice generated by our AI system. For personalized recommendations, please consult with a qualified financial advisor.*",
                                'query_type': 'financial_planning',
                                'confidence': 0.9
                            })
                        else:
                            return jsonify({
                                'response': "I'm your comprehensive financial advisor! I can help you with:\n\n**📊 Investment Planning**\n• Portfolio analysis and recommendations\n• Asset allocation strategies\n• Risk assessment and management\n\n**💰 Financial Planning**\n• Retirement planning and savings\n• Tax-efficient strategies\n• Debt management\n• Emergency fund planning\n\n**🎯 Personalized Advice**\n• Financial profile creation\n• Goal-based planning\n• Investment recommendations\n\nTo get personalized advice, please tell me:\n• Your age and income\n• Current net worth and savings\n• Risk tolerance (conservative/moderate/aggressive)\n• Investment goals and time horizon\n\nWhat specific financial planning area would you like to focus on?",
                                'query_type': 'financial_planning',
                                'confidence': 0.8
                            })
                except Exception as e:
                    logger.error(f"Error generating financial plan: {e}")
                    return jsonify({
                        'response': "I can help you with financial planning! Please visit the Financial Advisor page to create a comprehensive financial plan. You can access it at /financial-advisor or tell me about your financial situation (age, income, net worth, risk tolerance) and I'll provide personalized recommendations.",
                        'query_type': 'financial_planning',
                        'confidence': 0.8
                    })
            else:
                return jsonify({
                    'response': "I can help you with financial planning! Please visit the Financial Advisor page to create a comprehensive financial plan. You can access it at /financial-advisor.",
                    'query_type': 'financial_planning',
                    'confidence': 0.8
                })
        else:
            # For non-financial planning queries, provide a helpful response
            return jsonify({
                'response': "I'm your AI Stock Trading Assistant! I can help you with:\n\n**📈 Stock Analysis & Predictions**\n• Stock price predictions and analysis\n• Technical indicator analysis\n• Market trend analysis\n• Investment recommendations\n\n**🔍 Stock Research**\n• Company financial analysis\n• Industry comparisons\n• Risk assessment\n• Growth potential analysis\n\n**💡 Trading Strategies**\n• Backtesting trading strategies\n• Portfolio optimization\n• Risk management\n• Market timing insights\n\n**🎯 Quick Actions**\n• Ask me about specific stocks (e.g., 'What's the prediction for AAPL?')\n• Get market analysis (e.g., 'How is the tech sector performing?')\n• Request trading advice (e.g., 'Should I buy TSLA now?')\n\nWhat would you like to know about stocks or trading?",
                'query_type': 'ai_assistant',
                'confidence': 0.8
            })
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze text sentiment"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not predictor:
            return jsonify({'error': 'AI predictor not available'}), 500
        
        sentiment = predictor.analyze_text_sentiment(text)
        return jsonify(convert_numpy_types(sentiment))
    
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/insights', methods=['GET'])
def get_conversation_insights():
    """Get conversation insights"""
    try:
        if not predictor:
            return jsonify({'error': 'AI predictor not available'}), 500
        
        insights = predictor.get_conversation_insights()
        return jsonify(convert_numpy_types(insights))
    
    except Exception as e:
        logger.error(f"Error getting conversation insights: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    """Run a backtest for a given strategy and symbol"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        strategy = data.get('strategy')
        parameters = data.get('parameters', {})
        initial_capital = data.get('initial_capital', 10000)
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not symbol or not strategy:
            return jsonify({'error': 'Symbol and strategy are required'}), 400
        
        if not predictor:
            return jsonify({'error': 'AI predictor not available'}), 500
        
        # Fetch historical data
        # Calculate period based on start and end dates
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            days_diff = (end_dt - start_dt).days
            
            if days_diff <= 30:
                period = '1mo'
            elif days_diff <= 90:
                period = '3mo'
            elif days_diff <= 180:
                period = '6mo'
            elif days_diff <= 365:
                period = '1y'
            else:
                period = '2y'
        else:
            period = '1y'
        
        historical_data = predictor.data_fetcher.fetch_stock_data(symbol, period, '1d')
        if historical_data is None or historical_data.empty:
            return jsonify({'error': f'No historical data available for {symbol}'}), 404
        
        # Filter data by date range if provided
        if start_date and end_date:
            historical_data = historical_data[
                (historical_data.index >= start_date) & 
                (historical_data.index <= end_date)
            ]
        
        if historical_data.empty:
            return jsonify({'error': 'No data available for the specified date range'}), 404
        
        # Initialize and run backtest engine
        backtest_engine = BacktestEngine(historical_data, initial_capital)
        result = backtest_engine.run_backtest(strategy, parameters)
        
        # Convert result to JSON-serializable format
        result_dict = {
            'total_return': result.total_return,
            'final_value': result.final_value,
            'max_drawdown': result.max_drawdown,
            'sharpe_ratio': result.sharpe_ratio,
            'total_trades': result.total_trades,
            'win_rate': result.win_rate,
            'avg_win': result.avg_win,
            'avg_loss': result.avg_loss,
            'trades': [
                {
                    'date': trade.date.isoformat() if hasattr(trade.date, 'isoformat') else str(trade.date),
                    'type': trade.type.value,
                    'price': trade.price,
                    'quantity': trade.quantity,
                    'pnl': trade.pnl
                }
                for trade in result.trades
            ],
            'equity_curve': result.equity_curve.to_dict('records') if not result.equity_curve.empty else []
        }
        
        return jsonify(convert_numpy_types(result_dict)), 200
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    
    # Get port from environment variable (for Cloud Run) or default to 8080
    port = int(os.environ.get('PORT', 8080))
    
    print("🚀 Starting AI Stock Trading API Server...")
    print(f"📊 API endpoints available at http://localhost:{port}")
    print(f"🔗 React frontend should connect to http://localhost:{port}")
    print("📖 API documentation:")
    print("   - GET  /api/health - Health check")
    print("   - GET  /api/stock/data - Get stock data")
    print("   - GET  /api/stock/info - Get stock info")
    print("   - GET  /api/stock/technical - Get technical indicators")
    print("   - GET  /api/prediction - Get AI prediction")
    print("   - GET  /api/sensitivity - Get sensitivity analysis")
    print("   - POST /api/recommendations - Get smart recommendations")
    print("   - POST /api/portfolio/growth - Get portfolio growth")
    print("   - GET  /api/etf/analysis - Get ETF analysis")
    print("   - POST /api/strategies/money-growth - Get money growth strategies")
    print("   - POST /api/portfolio/initialize - Initialize portfolio")
    print("   - POST /api/portfolio/add-capital - Add capital")
    print("   - POST /api/portfolio/signals - Generate signals")
    print("   - POST /api/portfolio/execute - Execute signal")
    print("   - GET  /api/portfolio/summary - Get portfolio summary")
    print("   - GET  /api/portfolio/performance - Track performance")
    print("   - POST /api/portfolio/rebalance - Rebalance portfolio")
    print("   - POST /api/portfolio/save - Save portfolio state")
    print("   - POST /api/portfolio/load - Load portfolio state")
    print("   🚀 ENHANCED PORTFOLIO ENDPOINTS:")
    print("   - POST /api/portfolio/enhanced/initialize - Initialize enhanced portfolio")
    print("   - POST /api/portfolio/enhanced/update-investment - Update investment amount")
    print("   - POST /api/portfolio/enhanced/buy - Buy shares at market price")
    print("   - POST /api/portfolio/enhanced/sell - Sell shares at market price")
    print("   - GET  /api/portfolio/enhanced/summary - Get comprehensive portfolio summary")
    print("   - GET  /api/portfolio/enhanced/transactions - Get transaction history")
    print("   - GET  /api/portfolio/enhanced/asset/<symbol> - Get asset performance")
    print("   - GET  /api/portfolio/enhanced/current-price/<symbol> - Get current market price")
    print("   🤖 ENHANCED AUTO TRADER ENDPOINTS:")
    print("   - POST /api/trader/configure - Configure auto trader goals and parameters")
    print("   - POST /api/trader/start - Start automated trading system")
    print("   - POST /api/trader/stop - Stop automated trading system")
    print("   - POST /api/trader/pause - Pause automated trading system")
    print("   - POST /api/trader/resume - Resume automated trading system")
    print("   - GET  /api/trader/status - Get auto trader status and statistics")
    print("   - GET  /api/trader/history - Get auto trader trading history")
    print("   - POST /api/chat/query - Process natural language query")
    print("   - POST /api/chat/sentiment - Analyze sentiment")
    print("   - GET  /api/chat/insights - Get conversation insights")
    print("   - POST /api/backtest/run - Run backtest")
    
    # Use debug mode only in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port) 