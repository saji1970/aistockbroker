import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TradeType(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Trade:
    date: datetime
    type: TradeType
    price: float
    quantity: int
    pnl: Optional[float] = None

@dataclass
class BacktestResult:
    total_return: float
    final_value: float
    max_drawdown: float
    sharpe_ratio: float
    total_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    trades: List[Trade]
    equity_curve: pd.DataFrame

class BacktestEngine:
    def __init__(self, data: pd.DataFrame, initial_capital: float = 10000):
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []
        
    def calculate_technical_indicators(self, strategy: str, parameters: Dict) -> pd.DataFrame:
        """Calculate technical indicators based on strategy"""
        df = self.data.copy()
        
        if strategy == 'sma_crossover':
            short_period = parameters.get('short_period', 20)
            long_period = parameters.get('long_period', 50)
            
            df['SMA_Short'] = df['Close'].rolling(window=short_period).mean()
            df['SMA_Long'] = df['Close'].rolling(window=long_period).mean()
            df['SMA_Signal'] = np.where(df['SMA_Short'] > df['SMA_Long'], 1, -1)
            df['SMA_Signal_Change'] = df['SMA_Signal'].diff()
            
        elif strategy == 'rsi_strategy':
            rsi_period = parameters.get('rsi_period', 14)
            oversold = parameters.get('oversold', 30)
            overbought = parameters.get('overbought', 70)
            
            # Calculate RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            df['RSI_Signal'] = 0
            df.loc[df['RSI'] < oversold, 'RSI_Signal'] = 1  # Buy signal
            df.loc[df['RSI'] > overbought, 'RSI_Signal'] = -1  # Sell signal
            
        elif strategy == 'macd_strategy':
            fast_period = parameters.get('fast_period', 12)
            slow_period = parameters.get('slow_period', 26)
            signal_period = parameters.get('signal_period', 9)
            
            df['EMA_Fast'] = df['Close'].ewm(span=fast_period).mean()
            df['EMA_Slow'] = df['Close'].ewm(span=slow_period).mean()
            df['MACD'] = df['EMA_Fast'] - df['EMA_Slow']
            df['MACD_Signal'] = df['MACD'].ewm(span=signal_period).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            df['MACD_Signal_Line'] = np.where(df['MACD'] > df['MACD_Signal'], 1, -1)
            df['MACD_Signal_Change'] = df['MACD_Signal_Line'].diff()
            
        elif strategy == 'bollinger_bands':
            bb_period = parameters.get('bb_period', 20)
            bb_std = parameters.get('bb_std', 2)
            
            df['BB_Middle'] = df['Close'].rolling(window=bb_period).mean()
            bb_std_dev = df['Close'].rolling(window=bb_period).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std_dev * bb_std)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std_dev * bb_std)
            
            df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
            df['BB_Signal'] = 0
            df.loc[df['BB_Position'] < 0.1, 'BB_Signal'] = 1  # Buy when near lower band
            df.loc[df['BB_Position'] > 0.9, 'BB_Signal'] = -1  # Sell when near upper band
            
        elif strategy == 'mean_reversion':
            ma_period = parameters.get('ma_period', 50)
            deviation = parameters.get('deviation', 0.05)
            
            df['MA'] = df['Close'].rolling(window=ma_period).mean()
            df['Deviation'] = (df['Close'] - df['MA']) / df['MA']
            
            df['Mean_Reversion_Signal'] = 0
            df.loc[df['Deviation'] < -deviation, 'Mean_Reversion_Signal'] = 1  # Buy when below MA
            df.loc[df['Deviation'] > deviation, 'Mean_Reversion_Signal'] = -1  # Sell when above MA
            
        elif strategy == 'momentum':
            momentum_period = parameters.get('momentum_period', 10)
            threshold = parameters.get('threshold', 0.02)
            
            df['Momentum'] = df['Close'].pct_change(periods=momentum_period)
            
            df['Momentum_Signal'] = 0
            df.loc[df['Momentum'] > threshold, 'Momentum_Signal'] = 1  # Buy on positive momentum
            df.loc[df['Momentum'] < -threshold, 'Momentum_Signal'] = -1  # Sell on negative momentum
            
        return df
    
    def generate_signals(self, strategy: str, parameters: Dict) -> pd.DataFrame:
        """Generate buy/sell signals based on strategy"""
        df = self.calculate_technical_indicators(strategy, parameters)
        
        # Initialize signal column
        df['Signal'] = 0
        
        if strategy == 'sma_crossover':
            # Buy when short SMA crosses above long SMA
            df.loc[df['SMA_Signal_Change'] == 2, 'Signal'] = 1
            # Sell when short SMA crosses below long SMA
            df.loc[df['SMA_Signal_Change'] == -2, 'Signal'] = -1
            
        elif strategy == 'rsi_strategy':
            df['Signal'] = df['RSI_Signal']
            
        elif strategy == 'macd_strategy':
            # Buy when MACD crosses above signal line
            df.loc[df['MACD_Signal_Change'] == 2, 'Signal'] = 1
            # Sell when MACD crosses below signal line
            df.loc[df['MACD_Signal_Change'] == -2, 'Signal'] = -1
            
        elif strategy == 'bollinger_bands':
            df['Signal'] = df['BB_Signal']
            
        elif strategy == 'mean_reversion':
            df['Signal'] = df['Mean_Reversion_Signal']
            
        elif strategy == 'momentum':
            df['Signal'] = df['Momentum_Signal']
        
        return df
    
    def execute_trade(self, date: datetime, signal: int, price: float) -> Optional[Trade]:
        """Execute a trade based on signal"""
        if signal == 1 and self.position == 0:  # Buy signal and no position
            # Calculate quantity based on available capital
            quantity = int(self.current_capital / price)
            if quantity > 0:
                cost = quantity * price
                self.current_capital -= cost
                self.position = quantity
                
                trade = Trade(
                    date=date,
                    type=TradeType.BUY,
                    price=price,
                    quantity=quantity
                )
                self.trades.append(trade)
                return trade
                
        elif signal == -1 and self.position > 0:  # Sell signal and have position
            # Calculate P&L
            avg_buy_price = sum(t.price * t.quantity for t in self.trades if t.type == TradeType.BUY) / sum(t.quantity for t in self.trades if t.type == TradeType.BUY)
            pnl = (price - avg_buy_price) * self.position
            
            # Execute sell
            proceeds = self.position * price
            self.current_capital += proceeds
            self.position = 0
            
            trade = Trade(
                date=date,
                type=TradeType.SELL,
                price=price,
                quantity=self.position,
                pnl=pnl
            )
            self.trades.append(trade)
            return trade
            
        return None
    
    def run_backtest(self, strategy: str, parameters: Dict) -> BacktestResult:
        """Run the backtest simulation"""
        logger.info(f"Running backtest for strategy: {strategy}")
        
        # Generate signals
        df = self.generate_signals(strategy, parameters)
        
        # Reset state
        self.current_capital = self.initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []
        
        # Simulate trading
        for index, row in df.iterrows():
            if pd.isna(row['Signal']) or row['Signal'] == 0:
                continue
                
            trade = self.execute_trade(
                date=index,
                signal=row['Signal'],
                price=row['Close']
            )
            
            # Calculate current portfolio value
            current_value = self.current_capital + (self.position * row['Close'])
            self.equity_curve.append({
                'date': index,
                'value': current_value,
                'capital': self.current_capital,
                'position': self.position,
                'price': row['Close']
            })
        
        # Calculate final portfolio value
        final_value = self.current_capital + (self.position * df['Close'].iloc[-1])
        
        # Calculate performance metrics
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Calculate max drawdown
        equity_df = pd.DataFrame(self.equity_curve)
        if not equity_df.empty:
            equity_df['peak'] = equity_df['value'].expanding().max()
            equity_df['drawdown'] = (equity_df['value'] - equity_df['peak']) / equity_df['peak']
            max_drawdown = equity_df['drawdown'].min()
        else:
            max_drawdown = 0
        
        # Calculate Sharpe ratio
        if len(self.equity_curve) > 1:
            returns = pd.Series([e['value'] for e in self.equity_curve]).pct_change().dropna()
            if returns.std() > 0:
                sharpe_ratio = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        # Calculate trade statistics
        sell_trades = [t for t in self.trades if t.type == TradeType.SELL and t.pnl is not None]
        total_trades = len(sell_trades)
        
        if total_trades > 0:
            winning_trades = [t for t in sell_trades if t.pnl > 0]
            win_rate = len(winning_trades) / total_trades
            
            if winning_trades:
                avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades)
            else:
                avg_win = 0
                
            losing_trades = [t for t in sell_trades if t.pnl < 0]
            if losing_trades:
                avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades)
            else:
                avg_loss = 0
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
        
        return BacktestResult(
            total_return=total_return,
            final_value=final_value,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            total_trades=total_trades,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            trades=self.trades,
            equity_curve=pd.DataFrame(self.equity_curve)
        ) 