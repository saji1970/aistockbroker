import pandas as pd
import numpy as np
try:
    import ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    print("Warning: ta library not available. Technical indicators will be limited.")
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Class for calculating technical indicators and analysis."""
    
    def __init__(self):
        """Initialize the technical analyzer."""
        self.indicators = {}
        if not TA_AVAILABLE:
            logger.warning("Technical Analysis library (ta) not available. Limited functionality.")
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for the given data.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with all indicators added
        """
        if not TA_AVAILABLE:
            logger.warning("TA library not available, returning data without indicators")
            return data.copy()
            
        try:
            # Make a copy to avoid modifying original data
            df = data.copy()
            
            # Moving averages
            df = self._add_moving_averages(df)
            
            # Momentum indicators
            df = self._add_momentum_indicators(df)
            
            # Volatility indicators
            df = self._add_volatility_indicators(df)
            
            # Volume indicators
            df = self._add_volume_indicators(df)
            
            # Trend indicators
            df = self._add_trend_indicators(df)
            
            # Support and resistance levels
            df = self._add_support_resistance(df)
            
            logger.info(f"Calculated {len(self.indicators)} technical indicators")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            raise
    
    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add various moving averages."""
        if not TA_AVAILABLE:
            logger.warning("TA library not available, skipping moving averages")
            return df
            
        try:
            # Simple Moving Averages
            for period in [5, 10, 20, 50, 100, 200]:
                df[f'SMA_{period}'] = ta.trend.sma_indicator(df['Close'], window=period)
                df[f'EMA_{period}'] = ta.trend.ema_indicator(df['Close'], window=period)
            
            # Weighted Moving Average
            df['WMA_20'] = ta.trend.wma_indicator(df['Close'], window=20)
            
            # Hull Moving Average (skip if not available)
            try:
                df['HMA_20'] = ta.trend.hma_indicator(df['Close'], window=20)
            except AttributeError:
                logger.warning("HMA indicator not available in this version of ta library")
            
            self.indicators['moving_averages'] = [col for col in df.columns if 'SMA_' in col or 'EMA_' in col or 'WMA_' in col or 'HMA_' in col]
            
        except Exception as e:
            logger.error(f"Error calculating moving averages: {str(e)}")
        
        return df
    
    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum indicators."""
        if not TA_AVAILABLE:
            return df
        try:
            # RSI
            df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
            df['RSI_30'] = ta.momentum.rsi(df['Close'], window=30)
            
            # Stochastic Oscillator
            df['Stoch_K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'], window=14)
            df['Stoch_D'] = ta.momentum.stoch_signal(df['High'], df['Low'], df['Close'], window=14)
            
            # Williams %R
            try:
                df['Williams_R'] = ta.momentum.williams_r(df['High'], df['Low'], df['Close'], window=14)
            except TypeError:
                # Try without window parameter for older versions
                df['Williams_R'] = ta.momentum.williams_r(df['High'], df['Low'], df['Close'])
            
            # MACD
            df['MACD'] = ta.trend.macd(df['Close'])
            df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])
            df['MACD_Histogram'] = ta.trend.macd_diff(df['Close'])
            
            # CCI (Commodity Channel Index)
            df['CCI'] = ta.trend.cci(df['High'], df['Low'], df['Close'], window=20)
            
            # ROC (Rate of Change)
            df['ROC'] = ta.momentum.roc(df['Close'], window=10)
            
            self.indicators['momentum'] = ['RSI', 'RSI_30', 'Stoch_K', 'Stoch_D', 'Williams_R', 'MACD', 'MACD_Signal', 'MACD_Histogram', 'CCI', 'ROC']
            
        except Exception as e:
            logger.error(f"Error calculating momentum indicators: {str(e)}")
        
        return df
    
    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility indicators."""
        if not TA_AVAILABLE:
            return df
        try:
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
            df['BB_Upper'] = bb.bollinger_hband()
            df['BB_Middle'] = bb.bollinger_mavg()
            df['BB_Lower'] = bb.bollinger_lband()
            df['BB_Width'] = bb.bollinger_wband()
            df['BB_Position'] = bb.bollinger_pband()
            
            # Average True Range
            df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
            
            # Keltner Channel
            kc = ta.volatility.KeltnerChannel(df['High'], df['Low'], df['Close'], window=20)
            df['KC_Upper'] = kc.keltner_channel_hband()
            df['KC_Middle'] = kc.keltner_channel_mband()
            df['KC_Lower'] = kc.keltner_channel_lband()
            
            # Donchian Channel
            dc = ta.volatility.DonchianChannel(df['High'], df['Low'], df['Close'], window=20)
            df['DC_Upper'] = dc.donchian_channel_hband()
            df['DC_Middle'] = dc.donchian_channel_mband()
            df['DC_Lower'] = dc.donchian_channel_lband()
            
            self.indicators['volatility'] = [col for col in df.columns if 'BB_' in col or 'ATR' in col or 'KC_' in col or 'DC_' in col]
            
        except Exception as e:
            logger.error(f"Error calculating volatility indicators: {str(e)}")
        
        return df
    
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based indicators."""
        if not TA_AVAILABLE:
            return df
        try:
            # Volume Weighted Average Price
            df['VWAP'] = ta.volume.volume_weighted_average_price(df['High'], df['Low'], df['Close'], df['Volume'])
            
            # On Balance Volume
            df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
            
            # Accumulation/Distribution Line
            df['ADL'] = ta.volume.acc_dist_index(df['High'], df['Low'], df['Close'], df['Volume'])
            
            # Chaikin Money Flow
            df['CMF'] = ta.volume.chaikin_money_flow(df['High'], df['Low'], df['Close'], df['Volume'], window=20)
            
            # Volume Rate of Change (skip if not available)
            try:
                df['VROC'] = ta.volume.volume_roc(df['Volume'], window=25)
            except AttributeError:
                logger.warning("VROC indicator not available in this version of ta library")
            
            # Money Flow Index
            df['MFI'] = ta.volume.money_flow_index(df['High'], df['Low'], df['Close'], df['Volume'], window=14)
            
            self.indicators['volume'] = ['VWAP', 'OBV', 'ADL', 'CMF', 'VROC', 'MFI']
            
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {str(e)}")
        
        return df
    
    def _add_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trend indicators."""
        if not TA_AVAILABLE:
            return df
        try:
            # Parabolic SAR
            df['PSAR'] = ta.trend.psar_up(df['High'], df['Low'], df['Close'])
            
            # ADX (Average Directional Index)
            df['ADX'] = ta.trend.adx(df['High'], df['Low'], df['Close'], window=14)
            df['ADX_Pos'] = ta.trend.adx_pos(df['High'], df['Low'], df['Close'], window=14)
            df['ADX_Neg'] = ta.trend.adx_neg(df['High'], df['Low'], df['Close'], window=14)
            
            # Ichimoku Cloud
            ichimoku = ta.trend.IchimokuIndicator(df['High'], df['Low'])
            df['Ichimoku_A'] = ichimoku.ichimoku_a()
            df['Ichimoku_B'] = ichimoku.ichimoku_b()
            df['Ichimoku_Base'] = ichimoku.ichimoku_base_line()
            df['Ichimoku_Conversion'] = ichimoku.ichimoku_conversion_line()
            
            # Aroon Indicator
            try:
                aroon = ta.trend.AroonIndicator(df['Close'], window=25)
            except TypeError:
                # Try with high and low parameters
                aroon = ta.trend.AroonIndicator(df['High'], df['Low'], window=25)
            df['Aroon_Up'] = aroon.aroon_up()
            df['Aroon_Down'] = aroon.aroon_down()
            df['Aroon_Indicator'] = aroon.aroon_indicator()
            
            self.indicators['trend'] = ['PSAR', 'ADX', 'ADX_Pos', 'ADX_Neg', 'Ichimoku_A', 'Ichimoku_B', 'Ichimoku_Base', 'Ichimoku_Conversion', 'Aroon_Up', 'Aroon_Down', 'Aroon_Indicator']
            
        except Exception as e:
            logger.error(f"Error calculating trend indicators: {str(e)}")
        
        return df
    
    def _add_support_resistance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add support and resistance levels."""
        if not TA_AVAILABLE:
            return df
        try:
            # Pivot Points
            pp = ta.trend.PSARIndicator(df['High'], df['Low'], df['Close'])
            df['PSAR_Support'] = pp.psar_down()
            df['PSAR_Resistance'] = pp.psar_up()
            
            # Simple support and resistance (local minima/maxima)
            window = 20
            df['Support'] = df['Low'].rolling(window=window, center=True).min()
            df['Resistance'] = df['High'].rolling(window=window, center=True).max()
            
            self.indicators['support_resistance'] = ['PSAR_Support', 'PSAR_Resistance', 'Support', 'Resistance']
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {str(e)}")
        
        return df
    
    def get_signal_summary(self, df: pd.DataFrame) -> Dict[str, str]:
        """Get a summary of current technical signals."""
        try:
            latest = df.iloc[-1]
            signals = {}
            
            # RSI signals
            if latest['RSI'] > 70:
                signals['RSI'] = 'Overbought'
            elif latest['RSI'] < 30:
                signals['RSI'] = 'Oversold'
            else:
                signals['RSI'] = 'Neutral'
            
            # MACD signals
            if latest['MACD'] > latest['MACD_Signal']:
                signals['MACD'] = 'Bullish'
            else:
                signals['MACD'] = 'Bearish'
            
            # Moving average signals
            if latest['Close'] > latest['SMA_50'] > latest['SMA_200']:
                signals['MA_Trend'] = 'Strong Bullish'
            elif latest['Close'] > latest['SMA_50']:
                signals['MA_Trend'] = 'Bullish'
            elif latest['Close'] < latest['SMA_50'] < latest['SMA_200']:
                signals['MA_Trend'] = 'Strong Bearish'
            else:
                signals['MA_Trend'] = 'Bearish'
            
            # Bollinger Bands signals
            if latest['Close'] > latest['BB_Upper']:
                signals['BB'] = 'Overbought'
            elif latest['Close'] < latest['BB_Lower']:
                signals['BB'] = 'Oversold'
            else:
                signals['BB'] = 'Neutral'
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signal summary: {str(e)}")
            return {}
    
    def get_indicators_list(self) -> Dict[str, List[str]]:
        """Get list of all calculated indicators by category."""
        return self.indicators
    
    def calculate_rsi(self, prices: np.ndarray, window: int = 14) -> float:
        """Calculate RSI for a given price array."""
        if not TA_AVAILABLE:
            logger.warning("TA library not available, returning default RSI value")
            return 50.0
            
        try:
            # Convert to pandas Series if needed
            if isinstance(prices, np.ndarray):
                prices = pd.Series(prices)
            
            # Calculate RSI using ta library
            rsi_values = ta.momentum.rsi(prices, window=window)
            return float(rsi_values.iloc[-1]) if not pd.isna(rsi_values.iloc[-1]) else 50.0
        except Exception as e:
            logger.warning(f"Error calculating RSI: {e}")
            return 50.0  # Return neutral RSI if calculation fails 