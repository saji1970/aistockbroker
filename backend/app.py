#!/usr/bin/env python3
"""
AI Stock Prediction System with Gemini Pro
A comprehensive stock analysis and prediction tool using Google's Gemini Pro AI.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import logging

# Import our custom modules
from gemini_predictor import GeminiStockPredictor
from data_fetcher import StockDataFetcher
from technical_analysis import TechnicalAnalyzer
from config import Config
from portfolio_manager import PortfolioManager, SignalType, AssetType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Stock Prediction System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern chatbot design
st.markdown("""
<style>
/* Main header styling */
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}

/* Metric and prediction cards */
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}

.prediction-card {
    background-color: #e8f4fd;
    padding: 1.5rem;
    border-radius: 0.5rem;
    border: 2px solid #1f77b4;
}

.chart-dropdown {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 0.5rem 0;
}



/* Code block styling */
.code-block {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    overflow-x: auto;
}

.copy-button {
    background: #6c757d;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    cursor: pointer;
    margin-left: 8px;
    transition: background 0.3s ease;
}

.copy-button:hover {
    background: #495057;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource(ttl=3600)  # Cache for 1 hour
def initialize_predictor():
    """Initialize the Gemini predictor with caching."""
    try:
        return GeminiStockPredictor()
    except Exception as e:
        st.error(f"Failed to initialize predictor: {str(e)}")
        return None

def clear_cache():
    """Clear Streamlit cache to force reinitialization."""
    st.cache_resource.clear()
    st.cache_data.clear()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol, period="1y"):
    """Fetch stock data with caching."""
    try:
        fetcher = StockDataFetcher()
        return fetcher.fetch_stock_data(symbol, period)
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_stock_info(symbol):
    """Fetch stock information with caching."""
    try:
        fetcher = StockDataFetcher()
        return fetcher.get_stock_info(symbol)
    except Exception as e:
        st.error(f"Error fetching stock info: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_technical_indicators(symbol, period="1y"):
    """Calculate technical indicators with caching."""
    try:
        stock_data = get_stock_data(symbol, period)
        if stock_data is not None:
            analyzer = TechnicalAnalyzer()
            return analyzer.calculate_all_indicators(stock_data)
        return None
    except Exception as e:
        st.error(f"Error calculating technical indicators: {str(e)}")
        return None

def create_price_chart(data, symbol):
    """Create a price chart with technical indicators."""
    try:
        fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price'
        ))
        
        # Add volume bars
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['Volume'],
            name='Volume',
            yaxis='y2',
            opacity=0.3
        ))
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} Stock Price',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            yaxis2=dict(
                title='Volume',
                overlaying='y',
                side='right'
            ),
            height=500
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None

def display_stock_info(stock_info):
    """Display stock information in a formatted way."""
    if not stock_info:
        return
    
    st.markdown("## 📋 Stock Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Price", f"${stock_info.get('current_price', 0):.2f}")
        st.metric("Market Cap", f"${stock_info.get('market_cap', 0):,.0f}")
    
    with col2:
        st.metric("P/E Ratio", f"{stock_info.get('pe_ratio', 0):.2f}")
        st.metric("Beta", f"{stock_info.get('beta', 0):.2f}")
    
    with col3:
        st.metric("Dividend Yield", f"{stock_info.get('dividend_yield', 0):.2%}")
        st.metric("52 Week High", f"${stock_info.get('fifty_two_week_high', 0):.2f}")

def display_prediction_results(prediction_result):
    """Display prediction results in a formatted way."""
    if not prediction_result:
        return
    
    st.markdown("## 🤖 AI Prediction Results")
    
    # Display prediction text
    with st.expander("📊 Detailed AI Analysis", expanded=True):
        st.markdown(prediction_result['prediction_text'])
    
    # Display confidence metrics
    confidence_metrics = prediction_result.get('confidence_metrics', {})
    if confidence_metrics:
        st.markdown("### 📈 Confidence Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if confidence_metrics.get('short_term_confidence'):
                st.metric("Short-term Confidence", f"{confidence_metrics['short_term_confidence']}%")
        
        with col2:
            if confidence_metrics.get('medium_term_confidence'):
                st.metric("Medium-term Confidence", f"{confidence_metrics['medium_term_confidence']}%")
        
        with col3:
            if confidence_metrics.get('overall_confidence'):
                st.metric("Overall Confidence", f"{confidence_metrics['overall_confidence']}%")
    
    # Display recommendations
    recommendations = prediction_result.get('recommendations', {})
    if recommendations:
        st.markdown("### 💡 Trading Recommendations")
        
        action = recommendations.get('action', 'Hold')
        action_color = {
            'Buy': 'success',
            'Sell': 'danger',
            'Hold': 'warning'
        }.get(action, 'info')
        
        st.info(f"**Recommended Action: {action}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if recommendations.get('entry_price'):
                st.metric("Entry Price", f"${recommendations['entry_price']:.2f}")
            if recommendations.get('target_price'):
                st.metric("Target Price", f"${recommendations['target_price']:.2f}")
        
        with col2:
            if recommendations.get('stop_loss'):
                st.metric("Stop Loss", f"${recommendations['stop_loss']:.2f}")
            if recommendations.get('exit_price'):
                st.metric("Exit Price", f"${recommendations['exit_price']:.2f}")

def display_sensitivity_analysis(sensitivity_result):
    """Display sensitivity analysis results."""
    if not sensitivity_result or 'error' in sensitivity_result:
        st.error("Failed to generate sensitivity analysis. Please try again.")
        return
    
    st.subheader("📊 Sensitivity Analysis")
    
    # Display summary
    if 'summary' in sensitivity_result:
        summary = sensitivity_result['summary']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Scenarios", summary['total_scenarios'])
        with col2:
            st.metric("Best Scenario", summary['best_scenario'].replace('_', ' ').title())
        with col3:
            st.metric("Average Impact", f"{summary['avg_impact']:+.2f}%")
    
    # Display scenario results
    if 'sensitivity_results' in sensitivity_result:
        st.markdown("### 📈 Scenario Analysis")
        
        results = sensitivity_result['sensitivity_results']
        
        # Create a summary table
        scenario_data = []
        for scenario_name, result in results.items():
            scenario = result['scenario']
            price_impact = result['price_impact']
            recommendations = result['recommendations']
            
            scenario_data.append([
                scenario.name,
                f"{price_impact['price_change_pct']:+.2f}%",
                f"${price_impact['new_price']:.2f}",
                recommendations['action'],
                f"{recommendations['confidence']:.1%}"
            ])
        
        if scenario_data:
            df_scenarios = pd.DataFrame(
                scenario_data,
                columns=['Scenario', 'Price Impact', 'New Price', 'Action', 'Confidence']
            )
            st.dataframe(df_scenarios, use_container_width=True)
    
    # Display detailed report
    if 'report' in sensitivity_result:
        with st.expander("📋 Detailed Sensitivity Report", expanded=False):
            st.markdown(sensitivity_result['report'])

def display_portfolio_growth(portfolio_result):
    """Display portfolio growth analysis results."""
    try:
        if not portfolio_result or 'error' in portfolio_result:
            st.error("❌ Error generating portfolio growth analysis")
            return
        
        st.subheader("📈 Portfolio Growth Analysis")
        
        # Display portfolio summary
        if 'portfolio_summary' in portfolio_result:
            summary = portfolio_result['portfolio_summary']
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Predicted Return", f"{summary.get('total_predicted_return', 0)*100:.2f}%")
            with col2:
                st.metric("Confidence", f"{summary.get('weighted_confidence', 0)*100:.1f}%")
            with col3:
                st.metric("Volatility", f"{summary.get('portfolio_volatility', 0)*100:.2f}%")
            with col4:
                st.metric("Diversification", f"{summary.get('diversification_score', 0)*100:.0f}%")
        
        # Display individual asset predictions
        if 'portfolio_predictions' in portfolio_result:
            st.write("**Asset Predictions:**")
            for symbol, data in portfolio_result['portfolio_predictions'].items():
                with st.expander(f"📊 {symbol} ({data['allocation']}%)"):
                    prediction = data['prediction']
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Investment:** ${data['investment_amount']:,.0f}")
                        st.write(f"**Predicted Return:** {prediction.get('predicted_return', 0)*100:.2f}%")
                    
                    with col2:
                        st.write(f"**Confidence:** {prediction.get('confidence', 0)*100:.1f}%")
                        st.write(f"**Risk Level:** {prediction.get('risk_level', 'Medium')}")
        
        # Display growth scenarios
        if 'growth_scenarios' in portfolio_result:
            st.write("**Growth Scenarios:**")
            scenarios = portfolio_result['growth_scenarios']
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Conservative", f"{scenarios.get('conservative', {}).get('final_amount', 0):,.0f}")
            with col2:
                st.metric("Base Case", f"{scenarios.get('base_case', {}).get('final_amount', 0):,.0f}")
            with col3:
                st.metric("Optimistic", f"{scenarios.get('optimistic', {}).get('final_amount', 0):,.0f}")
                
    except Exception as e:
        st.error(f"❌ Error displaying portfolio growth: {str(e)}")

def display_etf_analysis(etf_result):
    """Display ETF analysis results."""
    try:
        if not etf_result or 'error' in etf_result:
            st.error("❌ Error generating ETF analysis")
            return
        
        st.subheader("🏦 ETF Analysis")
        
        # Display basic ETF info
        st.write(f"**Symbol:** {etf_result.get('symbol', 'N/A')}")
        st.write(f"**Type:** {etf_result.get('type', 'N/A')}")
        
        # Display ETF metrics
        if 'etf_metrics' in etf_result:
            metrics = etf_result['etf_metrics']
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Tracking Error", f"{metrics.get('tracking_error', 0)*100:.2f}%")
            with col2:
                st.metric("Bid-Ask Spread", f"{metrics.get('bid_ask_spread', 0)*100:.3f}%")
            with col3:
                st.metric("Premium/Discount", f"{metrics.get('premium_discount', 0)*100:.2f}%")
            with col4:
                st.metric("Volume", f"{metrics.get('volume_liquidity', 0):,.0f}")
        
        # Display sector exposure
        if 'sector_exposure' in etf_result:
            st.write("**Sector Exposure:**")
            sectors = etf_result['sector_exposure']
            for sector, percentage in sectors.items():
                st.write(f"• {sector}: {percentage}%")
        
        # Display liquidity analysis
        if 'liquidity_analysis' in etf_result:
            liquidity = etf_result['liquidity_analysis']
            st.write("**Liquidity Analysis:**")
            st.write(f"• **Score:** {liquidity.get('liquidity_score', 'N/A')}")
            st.write(f"• **Average Volume:** {liquidity.get('average_volume', 0):,.0f}")
            st.write(f"• **Recommendation:** {liquidity.get('trading_recommendation', 'N/A')}")
        
        # Display prediction results
        if 'prediction' in etf_result:
            st.write("**AI Prediction:**")
            prediction = etf_result['prediction']
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Predicted Return", f"{prediction.get('predicted_return', 0)*100:.2f}%")
                st.metric("Confidence", f"{prediction.get('confidence', 0)*100:.1f}%")
            
            with col2:
                st.metric("Risk Level", prediction.get('risk_level', 'Medium'))
                st.metric("Volatility", f"{prediction.get('volatility', 0)*100:.2f}%")
                
    except Exception as e:
        st.error(f"❌ Error displaying ETF analysis: {str(e)}")

def display_money_growth_strategies(strategies_result):
    """Display money growth strategies results."""
    try:
        if not strategies_result or 'error' in strategies_result:
            st.error("❌ Error generating money growth strategies")
            return
        
        st.subheader("💰 Money Growth Strategies")
        
        # Display selected strategy
        if 'selected_strategy' in strategies_result:
            strategy = strategies_result['selected_strategy']
            st.write(f"**Selected Strategy:** {strategy.get('risk_tolerance', 'N/A').title()}")
            
            # Display allocation
            st.write("**Asset Allocation:**")
            allocation = strategy.get('allocation', {})
            for symbol, percentage in allocation.items():
                st.write(f"• {symbol}: {percentage}%")
        
        # Display alternative strategies
        if 'alternative_strategies' in strategies_result:
            st.write("**Alternative Strategies:**")
            alternatives = strategies_result['alternative_strategies']
            for name, alt_strategy in alternatives.items():
                with st.expander(f"📊 {name.replace('_', ' ').title()}"):
                    st.write(f"**Description:** {alt_strategy.get('description', 'N/A')}")
                    st.write(f"**Expected Return:** {alt_strategy.get('expected_return', 0)*100:.2f}%")
                    st.write(f"**Risk Level:** {alt_strategy.get('risk_level', 'N/A')}")
                    
                    # Display allocation
                    st.write("**Allocation:**")
                    for symbol, percentage in alt_strategy.get('allocation', {}).items():
                        st.write(f"• {symbol}: {percentage}%")
        
        # Display compound growth scenarios
        if 'compound_growth_scenarios' in strategies_result:
            st.write("**Compound Growth Over Time:**")
            scenarios = strategies_result['compound_growth_scenarios']
            
            # Create a simple chart
            periods = list(scenarios.keys())
            amounts = [scenarios[period]['amount'] for period in periods]
            
            # Format period labels for display
            period_labels = []
            for period in periods:
                if period.startswith('days_'):
                    day_num = period.replace('days_', '')
                    period_labels.append(f"Day {day_num}")
                elif period.startswith('months_'):
                    month_num = period.replace('months_', '')
                    period_labels.append(f"Month {month_num}")
                elif period.startswith('years_'):
                    year_num = period.replace('years_', '')
                    period_labels.append(f"Year {year_num}")
                else:
                    period_labels.append(period.replace('_', ' ').title())
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=period_labels,
                y=amounts,
                mode='lines+markers',
                name='Portfolio Value',
                line=dict(color='#1f77b4', width=3)
            ))
            
            # Determine appropriate axis title based on time horizon
            if periods and periods[0].startswith('days_'):
                xaxis_title = "Days"
            elif periods and periods[0].startswith('months_'):
                xaxis_title = "Months"
            else:
                xaxis_title = "Years"
            
            fig.update_layout(
                title="Portfolio Growth Over Time",
                xaxis_title=xaxis_title,
                yaxis_title="Portfolio Value ($)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True, key="portfolio_growth_chart")
        
        # Display risk-adjusted returns
        if 'risk_adjusted_returns' in strategies_result:
            st.write("**Risk-Adjusted Returns:**")
            returns = strategies_result['risk_adjusted_returns']
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Sharpe Ratio", f"{returns.get('sharpe_ratio', 0):.2f}")
            with col2:
                st.metric("Sortino Ratio", f"{returns.get('sortino_ratio', 0):.2f}")
            with col3:
                st.metric("Calmar Ratio", f"{returns.get('calmar_ratio', 0):.2f}")
            with col4:
                st.metric("Information Ratio", f"{returns.get('information_ratio', 0):.2f}")
        
        # Display recommendations
        if 'recommendations' in strategies_result:
            recommendations = strategies_result['recommendations']
            
            if 'strategy_recommendations' in recommendations:
                st.write("**Strategy Recommendations:**")
                for rec in recommendations['strategy_recommendations']:
                    st.write(f"• {rec}")
            
            if 'timing_recommendations' in recommendations:
                st.write("**Timing Recommendations:**")
                for rec in recommendations['timing_recommendations']:
                    st.write(f"• {rec}")
            
            if 'risk_management' in recommendations:
                st.write("**Risk Management:**")
                for rec in recommendations['risk_management']:
                    st.write(f"• {rec}")
                    
    except Exception as e:
        st.error(f"❌ Error displaying money growth strategies: {str(e)}")

def display_portfolio_summary(portfolio_summary):
    """Display portfolio summary."""
    if not portfolio_summary:
        st.warning("No portfolio data available.")
        return
    
    try:
        # Portfolio overview
        st.markdown("### 📊 Portfolio Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Value", f"${portfolio_summary['total_value']:,.2f}")
        with col2:
            st.metric("Total Return", f"{portfolio_summary['total_return']:.2f}%")
        with col3:
            st.metric("Available Cash", f"${portfolio_summary['available_cash']:,.2f}")
        with col4:
            st.metric("Number of Assets", portfolio_summary['num_assets'])
        
        # Performance metrics
        if 'performance_metrics' in portfolio_summary:
            st.markdown("### 📈 Performance Metrics")
            metrics = portfolio_summary['performance_metrics']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Daily Return", f"{metrics.get('daily_return', 0):.2f}%")
            with col2:
                st.metric("Volatility", f"{metrics.get('volatility', 0):.2f}%")
            with col3:
                st.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.3f}")
            with col4:
                st.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0):.2f}%")
        
        # Assets breakdown
        if 'assets' in portfolio_summary and portfolio_summary['assets']:
            st.markdown("### 💼 Assets Breakdown")
            
            # Create DataFrame for better display
            assets_df = pd.DataFrame(portfolio_summary['assets'])
            
            # Display assets table
            st.dataframe(
                assets_df[['symbol', 'asset_type', 'quantity', 'current_price', 'current_value', 'allocation', 'unrealized_pnl_pct']].round(2),
                use_container_width=True
            )
            
            # Asset allocation chart
            if len(assets_df) > 0:
                fig = px.pie(
                    assets_df, 
                    values='current_value', 
                    names='symbol',
                    title='Asset Allocation'
                )
                st.plotly_chart(fig, use_container_width=True, key="asset_allocation_chart")
        
    except Exception as e:
        st.error(f"Error displaying portfolio summary: {str(e)}")

def display_signals(signals):
    """Display trading signals."""
    if not signals:
        st.info("No trading signals available.")
        return
    
    try:
        st.markdown("### 📊 Trading Signals")
        
        for signal in signals:
            # Determine color based on signal type
            if signal.signal_type in [SignalType.STRONG_BUY, SignalType.BUY]:
                color = "green"
                icon = "🟢"
            elif signal.signal_type in [SignalType.STRONG_SELL, SignalType.SELL]:
                color = "red"
                icon = "🔴"
            else:
                color = "orange"
                icon = "🟡"
            
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 2, 2, 3])
                with col1:
                    st.markdown(f"**{icon} {signal.symbol}**")
                with col2:
                    st.markdown(f"**{signal.signal_type.value}**")
                with col3:
                    st.markdown(f"**${signal.price:.2f}**")
                with col4:
                    st.markdown(f"**Confidence: {signal.confidence:.1%}**")
                
                st.markdown(f"*{signal.reasoning}*")
                
                if signal.target_price:
                    st.markdown(f"**Target Price:** ${signal.target_price:.2f}")
                if signal.stop_loss:
                    st.markdown(f"**Stop Loss:** ${signal.stop_loss:.2f}")
                
                st.markdown("---")
        
    except Exception as e:
        st.error(f"Error displaying signals: {str(e)}")

@st.cache_resource(ttl=3600)
def initialize_portfolio_manager(initial_capital: float, ai_predictor):
    """Initialize portfolio manager with caching."""
    return PortfolioManager(initial_capital, ai_predictor)

def main():
    """Main Streamlit application."""
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Stock Prediction System</h1>', unsafe_allow_html=True)
    st.markdown("### Powered by Google Gemini Pro & Advanced Analytics")
    
    # Sidebar configuration
    st.sidebar.markdown("## ⚙️ Configuration")
    
    # Stock symbol input
    symbol = st.sidebar.text_input(
        "Stock Symbol",
        value="AAPL",
        placeholder="e.g., AAPL, GOOGL, MSFT"
    ).upper()
    
    # Time period selection
    period = st.sidebar.selectbox(
        "Analysis Period",
        options=["1d", "7d", "14d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3
    )
    
    # Cache management
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 System")
    
    if st.sidebar.button("🔄 Clear Cache & Restart"):
        clear_cache()
        st.success("Cache cleared! Please refresh the page.")
        st.rerun()
    
    # Initialize predictor
    predictor = initialize_predictor()
    
    if not predictor:
        st.error("❌ Failed to initialize the AI predictor. Please check your API key and try again.")
        return
    
    # Main content area
    if symbol:
        try:
            # Fetch stock data
            stock_data = get_stock_data(symbol, period)
            
            if stock_data is None or stock_data.empty:
                st.error(f"❌ Unable to fetch data for {symbol}. Please check the symbol and try again.")
                return
            
            # Display stock information
            stock_info = get_stock_info(symbol)
            if stock_info:
                display_stock_info(stock_info)
            
            # Create main tabs
            analysis_tab, ai_tab, portfolio_tab = st.tabs(["📊 Analysis", "🤖 AI Features", "💼 Portfolio Manager"])
            
            with analysis_tab:
                # Technical Analysis Charts with dropdowns
                st.markdown("## 📈 Technical Analysis Charts")
                
                # Price chart (always visible)
                st.markdown("### 💹 Price Chart")
                price_chart = create_price_chart(stock_data, symbol)
                st.plotly_chart(price_chart, use_container_width=True, key="main_price_chart")
                
                # Short-term analysis for 1d, 7d, 14d periods
                if period in ["1d", "7d", "14d"]:
                    st.markdown("### ⚡ Short-Term Analysis")
                    
                    # Calculate short-term metrics
                    if len(stock_data) > 1:
                        current_price = stock_data['Close'].iloc[-1]
                        previous_price = stock_data['Close'].iloc[-2]
                        price_change = current_price - previous_price
                        price_change_pct = (price_change / previous_price) * 100
                        
                        # Display key metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Current Price", f"${current_price:.2f}")
                        with col2:
                            st.metric("Price Change", f"${price_change:.2f}", f"{price_change_pct:+.2f}%")
                        with col3:
                            st.metric("High", f"${stock_data['High'].max():.2f}")
                        with col4:
                            st.metric("Low", f"${stock_data['Low'].min():.2f}")
                        
                        # Volume analysis
                        if 'Volume' in stock_data.columns:
                            avg_volume = stock_data['Volume'].mean()
                            current_volume = stock_data['Volume'].iloc[-1]
                            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                            
                            st.markdown("#### 📊 Volume Analysis")
                            vol_col1, vol_col2, vol_col3 = st.columns(3)
                            with vol_col1:
                                st.metric("Current Volume", f"{current_volume:,.0f}")
                            with vol_col2:
                                st.metric("Avg Volume", f"{avg_volume:,.0f}")
                            with vol_col3:
                                st.metric("Volume Ratio", f"{volume_ratio:.2f}x")
                        
                        # Intraday volatility
                        if len(stock_data) > 1:
                            volatility = stock_data['Close'].pct_change().std() * 100
                            st.markdown("#### 📈 Volatility Analysis")
                            vol_col1, vol_col2, vol_col3 = st.columns(3)
                            with vol_col1:
                                st.metric("Period Volatility", f"{volatility:.2f}%")
                            with vol_col2:
                                st.metric("Price Range", f"${stock_data['High'].max() - stock_data['Low'].min():.2f}")
                            with vol_col3:
                                st.metric("Data Points", len(stock_data))
                
                # Technical indicators in dropdowns
                st.markdown("### 📊 Technical Indicators")
                
                # Moving Averages
                with st.expander("📈 Moving Averages", expanded=False):
                    if st.button("Calculate Moving Averages", key="ma_btn"):
                        with st.spinner("Calculating moving averages..."):
                            try:
                                technical_data = get_technical_indicators(symbol, period)
                                if technical_data is not None and 'SMA_20' in technical_data.columns:
                                    ma_data = technical_data[['Close', 'SMA_20', 'SMA_50', 'SMA_200']].dropna()
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(x=ma_data.index, y=ma_data['Close'], name='Price', line=dict(color='blue')))
                                    fig.add_trace(go.Scatter(x=ma_data.index, y=ma_data['SMA_20'], name='SMA 20', line=dict(color='orange')))
                                    fig.add_trace(go.Scatter(x=ma_data.index, y=ma_data['SMA_50'], name='SMA 50', line=dict(color='red')))
                                    fig.add_trace(go.Scatter(x=ma_data.index, y=ma_data['SMA_200'], name='SMA 200', line=dict(color='green')))
                                    fig.update_layout(title=f'{symbol} Moving Averages', xaxis_title='Date', yaxis_title='Price')
                                    st.plotly_chart(fig, use_container_width=True, key="moving_averages_chart")
                            except Exception as e:
                                st.error(f"Error calculating moving averages: {str(e)}")
                
                # RSI
                with st.expander("📊 RSI (Relative Strength Index)", expanded=False):
                    if st.button("Calculate RSI", key="rsi_btn"):
                        with st.spinner("Calculating RSI..."):
                            try:
                                technical_data = get_technical_indicators(symbol, period)
                                if technical_data is not None and 'RSI' in technical_data.columns:
                                    rsi_data = technical_data[['RSI']].dropna()
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(x=rsi_data.index, y=rsi_data['RSI'], name='RSI', line=dict(color='purple')))
                                    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
                                    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
                                    fig.update_layout(title=f'{symbol} RSI', xaxis_title='Date', yaxis_title='RSI', yaxis_range=[0, 100])
                                    st.plotly_chart(fig, use_container_width=True, key="rsi_chart")
                            except Exception as e:
                                st.error(f"Error calculating RSI: {str(e)}")
                
                # MACD
                with st.expander("📈 MACD (Moving Average Convergence Divergence)", expanded=False):
                    if st.button("Calculate MACD", key="macd_btn"):
                        with st.spinner("Calculating MACD..."):
                            try:
                                technical_data = get_technical_indicators(symbol, period)
                                if technical_data is not None and 'MACD' in technical_data.columns:
                                    macd_data = technical_data[['MACD', 'MACD_Signal', 'MACD_Histogram']].dropna()
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(x=macd_data.index, y=macd_data['MACD'], name='MACD', line=dict(color='blue')))
                                    fig.add_trace(go.Scatter(x=macd_data.index, y=macd_data['MACD_Signal'], name='Signal', line=dict(color='red')))
                                    fig.add_trace(go.Bar(x=macd_data.index, y=macd_data['MACD_Histogram'], name='Histogram', marker_color='gray'))
                                    fig.update_layout(title=f'{symbol} MACD', xaxis_title='Date', yaxis_title='MACD')
                                    st.plotly_chart(fig, use_container_width=True, key="macd_chart")
                            except Exception as e:
                                st.error(f"Error calculating MACD: {str(e)}")
                
                # Bollinger Bands
                with st.expander("📊 Bollinger Bands", expanded=False):
                    if st.button("Calculate Bollinger Bands", key="bb_btn"):
                        with st.spinner("Calculating Bollinger Bands..."):
                            try:
                                technical_data = get_technical_indicators(symbol, period)
                                if technical_data is not None and 'BB_Upper' in technical_data.columns:
                                    bb_data = technical_data[['Close', 'BB_Upper', 'BB_Middle', 'BB_Lower']].dropna()
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(x=bb_data.index, y=bb_data['Close'], name='Price', line=dict(color='blue')))
                                    fig.add_trace(go.Scatter(x=bb_data.index, y=bb_data['BB_Upper'], name='Upper Band', line=dict(color='red', dash='dash')))
                                    fig.add_trace(go.Scatter(x=bb_data.index, y=bb_data['BB_Middle'], name='Middle Band', line=dict(color='orange')))
                                    fig.add_trace(go.Scatter(x=bb_data.index, y=bb_data['BB_Lower'], name='Lower Band', line=dict(color='green', dash='dash')))
                                    fig.update_layout(title=f'{symbol} Bollinger Bands', xaxis_title='Date', yaxis_title='Price')
                                    st.plotly_chart(fig, use_container_width=True, key="bollinger_bands_chart")
                            except Exception as e:
                                st.error(f"Error calculating Bollinger Bands: {str(e)}")
                
                # Volume
                with st.expander("📊 Volume Analysis", expanded=False):
                    if st.button("Calculate Volume", key="volume_btn"):
                        with st.spinner("Calculating volume analysis..."):
                            try:
                                volume_data = stock_data[['Volume']].dropna()
                                fig = go.Figure()
                                fig.add_trace(go.Bar(x=volume_data.index, y=volume_data['Volume'], name='Volume', marker_color='lightblue'))
                                fig.update_layout(title=f'{symbol} Volume', xaxis_title='Date', yaxis_title='Volume')
                                st.plotly_chart(fig, use_container_width=True, key="volume_chart")
                            except Exception as e:
                                st.error(f"Error calculating volume: {str(e)}")
            
            with ai_tab:
                # AI Prediction
                st.markdown("## 🤖 AI Prediction")
                if st.button("🎯 Generate AI Prediction", type="primary"):
                    with st.spinner("🧠 Generating AI prediction... This may take a few moments."):
                        try:
                            prediction_result = predictor.predict_stock(symbol, period)
                            st.session_state['last_prediction'] = prediction_result
                            display_prediction_results(prediction_result)
                        except Exception as e:
                            st.error(f"❌ Error generating prediction: {str(e)}")
                
                # Display last prediction if available
                if 'last_prediction' in st.session_state:
                    display_prediction_results(st.session_state['last_prediction'])
                
                # Short-term AI Prediction for 1d, 7d, 14d periods
                if period in ["1d", "7d", "14d"]:
                    st.markdown("## ⚡ Short-Term AI Prediction")
                    st.markdown(f"### 📊 {period.upper()} Analysis & Forecast")
                    
                    if st.button("🚀 Generate Short-Term Prediction", type="primary", key="short_term_pred_btn"):
                        with st.spinner(f"🧠 Generating {period} prediction... This may take a few moments."):
                            try:
                                # Generate short-term prediction
                                short_term_prediction = predictor.predict_stock(symbol, period)
                                
                                # Display short-term specific analysis
                                st.markdown("#### 📈 Short-Term Price Movement")
                                
                                if 'prediction' in short_term_prediction:
                                    pred = short_term_prediction['prediction']
                                    
                                    # Calculate short-term metrics
                                    current_price = stock_data['Close'].iloc[-1]
                                    predicted_price = pred.get('predicted_price', current_price)
                                    price_change = predicted_price - current_price
                                    price_change_pct = (price_change / current_price) * 100
                                    
                                    # Display prediction metrics
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Current Price", f"${current_price:.2f}")
                                    with col2:
                                        st.metric("Predicted Price", f"${predicted_price:.2f}")
                                    with col3:
                                        st.metric("Expected Change", f"${price_change:.2f}", f"{price_change_pct:+.2f}%")
                                    
                                    # Short-term sentiment
                                    sentiment = pred.get('sentiment', 'neutral')
                                    confidence = pred.get('confidence', 0.5)
                                    
                                    st.markdown("#### 🎯 Short-Term Sentiment")
                                    sent_col1, sent_col2 = st.columns(2)
                                    with sent_col1:
                                        st.metric("Sentiment", sentiment.title())
                                    with sent_col2:
                                        st.metric("Confidence", f"{confidence:.1%}")
                                    
                                    # Short-term recommendations
                                    if 'short_term_recommendations' in pred:
                                        st.markdown("#### 💡 Short-Term Recommendations")
                                        for rec in pred['short_term_recommendations']:
                                            st.markdown(f"- {rec}")
                                
                                # Save to session state
                                st.session_state['last_short_term_prediction'] = short_term_prediction
                                
                            except Exception as e:
                                st.error(f"❌ Error generating short-term prediction: {str(e)}")
                    
                    # Display last short-term prediction if available
                    if 'last_short_term_prediction' in st.session_state:
                        short_pred = st.session_state['last_short_term_prediction']
                        if 'prediction' in short_pred:
                            pred = short_pred['prediction']
                            st.markdown("#### 📊 Previous Short-Term Analysis")
                            
                            current_price = stock_data['Close'].iloc[-1]
                            predicted_price = pred.get('predicted_price', current_price)
                            price_change = predicted_price - current_price
                            price_change_pct = (price_change / current_price) * 100
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Current Price", f"${current_price:.2f}")
                            with col2:
                                st.metric("Predicted Price", f"${predicted_price:.2f}")
                            with col3:
                                st.metric("Expected Change", f"${price_change:.2f}", f"{price_change_pct:+.2f}%")
                
                # Sensitivity Analysis
                st.markdown("## 📊 Sensitivity Analysis")
                if st.button("📊 Generate Sensitivity Analysis", type="secondary"):
                    with st.spinner("📊 Generating sensitivity analysis... This may take a few moments."):
                        try:
                            # Verify predictor has the method
                            if not hasattr(predictor, 'perform_sensitivity_analysis'):
                                st.error("❌ Sensitivity analysis feature not available. Please clear cache and restart.")
                                st.info("💡 Click 'Clear Cache & Restart' in the sidebar to fix this.")
                                return
                            
                            sensitivity_result = predictor.perform_sensitivity_analysis(symbol, period)
                            display_sensitivity_analysis(sensitivity_result)
                            
                            # Save sensitivity analysis to session state
                            st.session_state['last_sensitivity'] = sensitivity_result
                            
                        except Exception as e:
                            st.error(f"❌ Error generating sensitivity analysis: {str(e)}")
                
                # Display last sensitivity analysis if available
                if 'last_sensitivity' in st.session_state:
                    display_sensitivity_analysis(st.session_state['last_sensitivity'])
                
                # Smart Recommendations
                st.markdown("## 🧠 Smart Recommendations")
                if st.button("🎯 Generate Smart Recommendations", type="primary"):
                    with st.spinner("🧠 Generating personalized recommendations..."):
                        try:
                            # Verify predictor has the method
                            if not hasattr(predictor, 'generate_smart_recommendations'):
                                st.error("❌ Smart recommendations feature not available. Please clear cache and restart.")
                                st.info("💡 Click 'Clear Cache & Restart' in the sidebar to fix this.")
                                return
                            
                            # Get user preferences (simplified)
                            user_preferences = {
                                'risk_tolerance': 'medium',
                                'investment_horizon': 'medium_term',
                                'preferred_sectors': ['technology', 'healthcare']
                            }
                            
                            smart_recs = predictor.generate_smart_recommendations(symbol, user_preferences)
                            
                            # Display recommendations
                            st.markdown("### 🎯 Personalized Analysis")
                            
                            # Main recommendation
                            rec = smart_recs['smart_recommendations']
                            st.markdown(f"**Recommended Action:** {rec['action']}")
                            st.markdown(f"**Confidence:** {rec['confidence']:.1%}")
                            st.markdown(f"**Position Size:** {rec['position_size']}")
                            
                            # Reasoning
                            if rec['reasoning']:
                                st.markdown("**💡 Reasoning:**")
                                for reason in rec['reasoning']:
                                    st.markdown(f"- {reason}")
                            
                            # Risk assessment
                            risk = smart_recs['risk_assessment']
                            st.markdown("**⚠️ Risk Assessment:**")
                            st.markdown(f"- Risk Level: {risk['risk_level']}")
                            st.markdown(f"- Volatility: {risk['volatility']:.1%}")
                            st.markdown(f"- Max Drawdown: {risk['max_drawdown']:.1%}")
                            
                            if risk['risk_factors']:
                                st.markdown("**Risk Factors:**")
                                for factor in risk['risk_factors']:
                                    st.markdown(f"- {factor}")
                            
                            # Timing recommendations
                            timing = smart_recs['timing_recommendations']
                            st.markdown("**⏰ Timing Recommendations:**")
                            st.markdown(f"- Entry Timing: {timing['entry_timing']}")
                            st.markdown(f"- Exit Timing: {timing['exit_timing']}")
                            st.markdown(f"- Holding Period: {timing['holding_period']}")
                            
                            if timing['key_levels']:
                                levels = timing['key_levels']
                                st.markdown("**Key Levels:**")
                                st.markdown(f"- Support: ${levels.get('support', 'N/A')}")
                                st.markdown(f"- Resistance: ${levels.get('resistance', 'N/A')}")
                                st.markdown(f"- Distance to Support: {levels.get('distance_to_support', 'N/A'):.1f}%")
                                st.markdown(f"- Distance to Resistance: {levels.get('distance_to_resistance', 'N/A'):.1f}%")
                            
                        except Exception as e:
                            st.error(f"❌ Error generating smart recommendations: {str(e)}")
                
                # Portfolio Growth Analysis
                st.markdown("## 📈 Portfolio Growth Analysis")
                if st.button("📊 Analyze Portfolio Growth", type="primary"):
                    with st.spinner("📈 Analyzing portfolio growth..."):
                        try:
                            # Verify predictor has the method
                            if not hasattr(predictor, 'predict_portfolio_growth'):
                                st.error("❌ Portfolio growth analysis feature not available. Please clear cache and restart.")
                                st.info("💡 Click 'Clear Cache & Restart' in the sidebar to fix this.")
                                return
                            
                            # Sample portfolio (user can modify this)
                            sample_portfolio = {
                                'SPY': 40,  # S&P 500 ETF
                                'QQQ': 25,  # NASDAQ ETF
                                'VTI': 20,  # Total Market ETF
                                'GLD': 15   # Gold ETF
                            }
                            
                            portfolio_result = predictor.predict_portfolio_growth(
                                portfolio=sample_portfolio,
                                period=period,
                                investment_amount=10000
                            )
                            
                            display_portfolio_growth(portfolio_result)
                            
                            # Save to session state
                            st.session_state['last_portfolio'] = portfolio_result
                            
                        except Exception as e:
                            st.error(f"❌ Error analyzing portfolio growth: {str(e)}")
                
                # Display last portfolio analysis if available
                if 'last_portfolio' in st.session_state:
                    display_portfolio_growth(st.session_state['last_portfolio'])
                
                # ETF Analysis
                st.markdown("## 🏦 ETF Analysis")
                etf_symbol = st.text_input("ETF Symbol", value="SPY", placeholder="e.g., SPY, QQQ, VTI")
                
                if st.button("🏦 Analyze ETF", type="primary"):
                    with st.spinner("🏦 Analyzing ETF performance..."):
                        try:
                            # Verify predictor has the method
                            if not hasattr(predictor, 'analyze_etf_performance'):
                                st.error("❌ ETF analysis feature not available. Please clear cache and restart.")
                                st.info("💡 Click 'Clear Cache & Restart' in the sidebar to fix this.")
                                return
                            
                            etf_result = predictor.analyze_etf_performance(etf_symbol, period)
                            display_etf_analysis(etf_result)
                            
                            # Save to session state
                            st.session_state['last_etf'] = etf_result
                            
                        except Exception as e:
                            st.error(f"❌ Error analyzing ETF: {str(e)}")
                
                # Display last ETF analysis if available
                if 'last_etf' in st.session_state:
                    display_etf_analysis(st.session_state['last_etf'])
                
                # Money Growth Strategies
                st.markdown("## 💰 Money Growth Strategies")
                
                # Strategy parameters
                col1, col2, col3 = st.columns(3)
                with col1:
                    initial_investment = st.number_input("Initial Investment ($)", value=10000, min_value=1000, step=1000)
                with col2:
                    risk_tolerance = st.selectbox("Risk Tolerance", ["conservative", "moderate", "aggressive"])
                with col3:
                    time_horizon = st.selectbox("Time Horizon", [
                        "30d", "60d", "90d", "180d",  # Days
                        "6mo", "1y", "2y", "3y", "5y", "10y"  # Months and Years
                    ])
                
                if st.button("💰 Generate Growth Strategies", type="primary"):
                    with st.spinner("💰 Generating money growth strategies..."):
                        try:
                            # Verify predictor has the method
                            if not hasattr(predictor, 'predict_money_growth_strategies'):
                                st.error("❌ Money growth strategies feature not available. Please clear cache and restart.")
                                st.info("💡 Click 'Clear Cache & Restart' in the sidebar to fix this.")
                                return
                            
                            strategies_result = predictor.predict_money_growth_strategies(
                                initial_investment=initial_investment,
                                risk_tolerance=risk_tolerance,
                                time_horizon=time_horizon
                            )
                            
                            display_money_growth_strategies(strategies_result)
                            
                            # Save to session state
                            st.session_state['last_strategies'] = strategies_result
                            
                        except Exception as e:
                            st.error(f"❌ Error generating money growth strategies: {str(e)}")
                
                # Display last strategies if available
                if 'last_strategies' in st.session_state:
                    display_money_growth_strategies(st.session_state['last_strategies'])
            
            with portfolio_tab:
                st.markdown("## 💼 Portfolio Management System")
                st.markdown("Manage your investment portfolio with AI-powered analysis and automated trading signals.")
                
                # Initialize portfolio manager
                if 'portfolio_manager' not in st.session_state:
                    # Portfolio setup
                    st.markdown("### 🚀 Portfolio Setup")
                    initial_capital = st.number_input(
                        "Initial Capital ($)", 
                        value=10000, 
                        min_value=1000, 
                        step=1000,
                        help="Enter your starting capital"
                    )
                    
                    if st.button("Initialize Portfolio", type="primary"):
                        portfolio_manager = initialize_portfolio_manager(initial_capital, predictor)
                        st.session_state['portfolio_manager'] = portfolio_manager
                        st.success(f"Portfolio initialized with ${initial_capital:,.2f}")
                        st.rerun()
                
                else:
                    portfolio_manager = st.session_state['portfolio_manager']
                    
                    # Portfolio overview
                    st.markdown("### 📊 Portfolio Overview")
                    portfolio_summary = portfolio_manager.get_portfolio_summary()
                    display_portfolio_summary(portfolio_summary)
                    
                    # Portfolio actions
                    st.markdown("### ⚡ Portfolio Actions")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Add capital
                        add_capital = st.number_input("Add Capital ($)", value=1000, min_value=100, step=100)
                        if st.button("Add Capital"):
                            if portfolio_manager.add_capital(add_capital):
                                st.success(f"Added ${add_capital:,.2f} to portfolio")
                                st.rerun()
                    
                    with col2:
                        # Generate signals
                        if st.button("Generate Trading Signals"):
                            with st.spinner("Generating AI trading signals..."):
                                # Sample watchlist
                                watchlist = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "SPY", "QQQ", "BTC", "ETH"]
                                signals = portfolio_manager.generate_signals(watchlist)
                                st.session_state['recent_signals'] = signals
                                st.success(f"Generated {len(signals)} trading signals")
                    
                    with col3:
                        # Check rebalancing
                        if st.button("Check Rebalancing"):
                            if portfolio_manager.check_rebalancing_needed():
                                st.warning("Portfolio rebalancing needed!")
                                st.session_state['rebalancing_needed'] = True
                            else:
                                st.success("Portfolio is well-balanced")
                    
                    # Display recent signals
                    if 'recent_signals' in st.session_state:
                        st.markdown("### 📊 Recent Trading Signals")
                        display_signals(st.session_state['recent_signals'])
                        
                        # Execute signals
                        st.markdown("### 🎯 Execute Signals")
                        for signal in st.session_state['recent_signals']:
                            col1, col2, col3 = st.columns([2, 2, 1])
                            with col1:
                                st.write(f"**{signal.symbol}** - {signal.signal_type.value}")
                            with col2:
                                st.write(f"Confidence: {signal.confidence:.1%}")
                            with col3:
                                if st.button(f"Execute {signal.symbol}", key=f"execute_{signal.symbol}"):
                                    if portfolio_manager.execute_signal(signal):
                                        st.success(f"Executed {signal.signal_type.value} for {signal.symbol}")
                                        st.rerun()
                    
                    # Rebalancing
                    if st.session_state.get('rebalancing_needed', False):
                        st.markdown("### ⚖️ Portfolio Rebalancing")
                        st.warning("Your portfolio needs rebalancing!")
                        
                        if st.button("Rebalance Portfolio"):
                            with st.spinner("Rebalancing portfolio..."):
                                if portfolio_manager.rebalance_portfolio():
                                    st.success("Portfolio rebalanced successfully!")
                                    st.session_state['rebalancing_needed'] = False
                                    st.rerun()
                    
                    # Performance tracking
                    st.markdown("### 📈 Performance Tracking")
                    if st.button("Update Performance"):
                        with st.spinner("Updating performance metrics..."):
                            performance = portfolio_manager.track_performance()
                            st.session_state['performance_data'] = performance
                            st.success("Performance updated!")
                    
                    if 'performance_data' in st.session_state:
                        performance = st.session_state['performance_data']
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Return", f"{performance.get('total_return', 0):.2f}%")
                        with col2:
                            st.metric("Daily Return", f"{performance.get('daily_return', 0):.2f}%")
                        with col3:
                            st.metric("Sharpe Ratio", f"{performance.get('performance_metrics', {}).get('sharpe_ratio', 0):.3f}")
                        with col4:
                            st.metric("Max Drawdown", f"{performance.get('performance_metrics', {}).get('max_drawdown', 0):.2f}%")
                    
                    # Portfolio management
                    st.markdown("### 💾 Portfolio Management")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Save Portfolio State"):
                            portfolio_manager.save_portfolio_state()
                            st.success("Portfolio state saved!")
                    
                    with col2:
                        uploaded_file = st.file_uploader("Load Portfolio State", type=['json'])
                        if uploaded_file is not None:
                            try:
                                portfolio_manager.load_portfolio_state(uploaded_file.name)
                                st.success("Portfolio state loaded!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error loading portfolio: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error processing {symbol}: {str(e)}")
            st.info("💡 Try clearing the cache and restarting the application.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>⚠️ Disclaimer: This tool is for educational purposes only. Always do your own research before making investment decisions.</p>
        <p>Powered by Google Gemini Pro AI | Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 