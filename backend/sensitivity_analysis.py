import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SensitivityScenario:
    """Data class for sensitivity analysis scenarios."""
    name: str
    description: str
    factors: Dict[str, float]
    expected_impact: str
    confidence_level: float
    risk_level: str

class SensitivityAnalyzer:
    """Class for performing sensitivity analysis on stock predictions."""
    
    def __init__(self):
        self.scenarios = {}
        self.risk_factors = {
            'market_volatility': {
                'description': 'Overall market volatility changes',
                'baseline': 0.20,
                'range': (0.10, 0.40),
                'impact': 'high'
            },
            'interest_rates': {
                'description': 'Interest rate changes',
                'baseline': 0.05,
                'range': (0.02, 0.08),
                'impact': 'medium'
            },
            'earnings_growth': {
                'description': 'Company earnings growth rate',
                'baseline': 0.15,
                'range': (0.05, 0.25),
                'impact': 'high'
            },
            'sector_performance': {
                'description': 'Sector-specific performance',
                'baseline': 0.10,
                'range': (-0.10, 0.30),
                'impact': 'medium'
            },
            'volume_trends': {
                'description': 'Trading volume trends',
                'baseline': 1.0,
                'range': (0.5, 2.0),
                'impact': 'low'
            },
            'technical_momentum': {
                'description': 'Technical indicator momentum',
                'baseline': 0.0,
                'range': (-0.5, 0.5),
                'impact': 'medium'
            }
        }
    
    def create_scenarios(self, base_prediction: Dict) -> Dict[str, SensitivityScenario]:
        """Create various sensitivity analysis scenarios."""
        
        scenarios = {}
        
        # Bull Market Scenario
        scenarios['bull_market'] = SensitivityScenario(
            name="Bull Market",
            description="Optimistic market conditions with strong growth",
            factors={
                'market_volatility': 0.15,
                'interest_rates': 0.03,
                'earnings_growth': 0.25,
                'sector_performance': 0.25,
                'volume_trends': 1.5,
                'technical_momentum': 0.3
            },
            expected_impact="Significant upside potential",
            confidence_level=0.75,
            risk_level="low"
        )
        
        # Bear Market Scenario
        scenarios['bear_market'] = SensitivityScenario(
            name="Bear Market",
            description="Pessimistic market conditions with economic downturn",
            factors={
                'market_volatility': 0.35,
                'interest_rates': 0.07,
                'earnings_growth': 0.05,
                'sector_performance': -0.05,
                'volume_trends': 0.7,
                'technical_momentum': -0.3
            },
            expected_impact="Significant downside risk",
            confidence_level=0.70,
            risk_level="high"
        )
        
        # Interest Rate Shock
        scenarios['interest_rate_shock'] = SensitivityScenario(
            name="Interest Rate Shock",
            description="Rapid increase in interest rates",
            factors={
                'market_volatility': 0.30,
                'interest_rates': 0.08,
                'earnings_growth': 0.10,
                'sector_performance': -0.10,
                'volume_trends': 1.2,
                'technical_momentum': -0.2
            },
            expected_impact="Moderate to high downside risk",
            confidence_level=0.65,
            risk_level="medium"
        )
        
        # Earnings Surprise
        scenarios['earnings_surprise'] = SensitivityScenario(
            name="Earnings Surprise",
            description="Better than expected earnings performance",
            factors={
                'market_volatility': 0.18,
                'interest_rates': 0.05,
                'earnings_growth': 0.30,
                'sector_performance': 0.15,
                'volume_trends': 1.8,
                'technical_momentum': 0.4
            },
            expected_impact="Strong upside potential",
            confidence_level=0.80,
            risk_level="low"
        )
        
        # Sector Rotation
        scenarios['sector_rotation'] = SensitivityScenario(
            name="Sector Rotation",
            description="Money flowing out of current sector",
            factors={
                'market_volatility': 0.25,
                'interest_rates': 0.05,
                'earnings_growth': 0.12,
                'sector_performance': -0.15,
                'volume_trends': 0.8,
                'technical_momentum': -0.1
            },
            expected_impact="Moderate downside risk",
            confidence_level=0.60,
            risk_level="medium"
        )
        
        # Volatility Spike
        scenarios['volatility_spike'] = SensitivityScenario(
            name="Volatility Spike",
            description="Sudden increase in market volatility",
            factors={
                'market_volatility': 0.40,
                'interest_rates': 0.06,
                'earnings_growth': 0.08,
                'sector_performance': 0.05,
                'volume_trends': 2.0,
                'technical_momentum': 0.0
            },
            expected_impact="High uncertainty, potential for large moves",
            confidence_level=0.45,
            risk_level="high"
        )
        
        return scenarios
    
    def calculate_sensitivity_metrics(self, base_data: Dict, scenarios: Dict[str, SensitivityScenario]) -> Dict:
        """Calculate sensitivity metrics for different scenarios."""
        
        results = {}
        base_price = base_data.get('current_price', 100.0)
        base_volatility = base_data.get('volatility_20d', 0.20)
        
        for scenario_name, scenario in scenarios.items():
            # Calculate price impact based on scenario factors
            price_impact = self._calculate_price_impact(base_data, scenario.factors)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(base_data, scenario.factors)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                base_price, price_impact, scenario.confidence_level
            )
            
            results[scenario_name] = {
                'scenario': scenario,
                'price_impact': price_impact,
                'risk_metrics': risk_metrics,
                'confidence_intervals': confidence_intervals,
                'recommendations': self._generate_scenario_recommendations(scenario, price_impact)
            }
        
        return results
    
    def _calculate_price_impact(self, base_data: Dict, factors: Dict[str, float]) -> Dict:
        """Calculate price impact based on scenario factors."""
        
        base_price = base_data.get('current_price', 100.0)
        base_volatility = base_data.get('volatility_20d', 0.20)
        
        # Calculate factor impacts
        volatility_impact = (factors['market_volatility'] - base_volatility) * -0.5  # Higher volatility = lower price
        interest_rate_impact = (factors['interest_rates'] - 0.05) * -2.0  # Higher rates = lower price
        earnings_impact = (factors['earnings_growth'] - 0.15) * 1.5  # Higher earnings = higher price
        sector_impact = factors['sector_performance'] * 0.8  # Sector performance impact
        volume_impact = (factors['volume_trends'] - 1.0) * 0.1  # Volume impact
        technical_impact = factors['technical_momentum'] * 0.3  # Technical momentum impact
        
        # Combine impacts
        total_impact_pct = (
            volatility_impact + 
            interest_rate_impact + 
            earnings_impact + 
            sector_impact + 
            volume_impact + 
            technical_impact
        )
        
        new_price = base_price * (1 + total_impact_pct)
        
        return {
            'base_price': base_price,
            'new_price': new_price,
            'price_change': new_price - base_price,
            'price_change_pct': total_impact_pct * 100,
            'factor_impacts': {
                'volatility': volatility_impact * 100,
                'interest_rates': interest_rate_impact * 100,
                'earnings': earnings_impact * 100,
                'sector': sector_impact * 100,
                'volume': volume_impact * 100,
                'technical': technical_impact * 100
            }
        }
    
    def _calculate_risk_metrics(self, base_data: Dict, factors: Dict[str, float]) -> Dict:
        """Calculate risk metrics for the scenario."""
        
        base_volatility = base_data.get('volatility_20d', 0.20)
        new_volatility = factors['market_volatility']
        
        # Calculate Value at Risk (VaR)
        confidence_levels = [0.90, 0.95, 0.99]
        var_metrics = {}
        
        for conf_level in confidence_levels:
            z_score = self._get_z_score(conf_level)
            var_metrics[f'var_{int(conf_level*100)}'] = z_score * new_volatility * np.sqrt(252)
        
        # Calculate Expected Shortfall (Conditional VaR)
        es_95 = self._calculate_expected_shortfall(new_volatility, 0.95)
        
        # Calculate Sharpe ratio adjustment
        base_return = base_data.get('annual_return', 0.10)
        risk_free_rate = factors['interest_rates']
        new_sharpe = (base_return - risk_free_rate) / new_volatility if new_volatility > 0 else 0
        
        return {
            'volatility': new_volatility,
            'var_metrics': var_metrics,
            'expected_shortfall_95': es_95,
            'sharpe_ratio': new_sharpe,
            'max_drawdown_estimate': new_volatility * 2.5,  # Rough estimate
            'beta_adjustment': factors['sector_performance'] * 0.5 + 1.0
        }
    
    def _calculate_confidence_intervals(self, base_price: float, price_impact: Dict, confidence_level: float) -> Dict:
        """Calculate confidence intervals for price predictions."""
        
        new_price = price_impact['new_price']
        volatility = price_impact.get('volatility', 0.20)
        
        # Calculate standard error based on confidence level
        z_score = self._get_z_score(confidence_level)
        standard_error = new_price * volatility * z_score / np.sqrt(252)
        
        lower_bound = new_price - standard_error
        upper_bound = new_price + standard_error
        
        return {
            'confidence_level': confidence_level,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'range': upper_bound - lower_bound,
            'standard_error': standard_error
        }
    
    def _get_z_score(self, confidence_level: float) -> float:
        """Get z-score for given confidence level."""
        z_scores = {
            0.90: 1.645,
            0.95: 1.960,
            0.99: 2.576
        }
        return z_scores.get(confidence_level, 1.960)
    
    def _calculate_expected_shortfall(self, volatility: float, confidence_level: float) -> float:
        """Calculate Expected Shortfall (Conditional VaR)."""
        # Simplified calculation
        var = self._get_z_score(confidence_level) * volatility
        return var * 1.5  # ES is typically 1.5x VaR for normal distributions
    
    def _generate_scenario_recommendations(self, scenario: SensitivityScenario, price_impact: Dict) -> Dict:
        """Generate recommendations based on scenario analysis."""
        
        price_change_pct = price_impact['price_change_pct']
        
        if price_change_pct > 10:
            action = "Strong Buy"
            reasoning = "Significant upside potential in this scenario"
        elif price_change_pct > 5:
            action = "Buy"
            reasoning = "Moderate upside potential"
        elif price_change_pct > -5:
            action = "Hold"
            reasoning = "Limited impact expected"
        elif price_change_pct > -10:
            action = "Sell"
            reasoning = "Moderate downside risk"
        else:
            action = "Strong Sell"
            reasoning = "Significant downside risk"
        
        return {
            'action': action,
            'reasoning': reasoning,
            'position_size': self._recommend_position_size(scenario.risk_level, abs(price_change_pct)),
            'stop_loss': price_impact['base_price'] * (1 - abs(price_change_pct) / 100 * 0.5),
            'target_price': price_impact['new_price']
        }
    
    def _recommend_position_size(self, risk_level: str, price_impact: float) -> str:
        """Recommend position size based on risk level and price impact."""
        
        if risk_level == "high":
            if price_impact > 15:
                return "Small (2-3% of portfolio)"
            else:
                return "Avoid or minimal (1-2% of portfolio)"
        elif risk_level == "medium":
            if price_impact > 10:
                return "Medium (3-5% of portfolio)"
            else:
                return "Small (2-3% of portfolio)"
        else:  # low risk
            if price_impact > 10:
                return "Large (5-8% of portfolio)"
            else:
                return "Medium (3-5% of portfolio)"
    
    def generate_sensitivity_report(self, base_data: Dict, scenarios: Dict[str, SensitivityScenario]) -> str:
        """Generate a comprehensive sensitivity analysis report."""
        
        results = self.calculate_sensitivity_metrics(base_data, scenarios)
        
        report = "# 📊 Sensitivity Analysis Report\n\n"
        report += f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**Base Price:** ${base_data.get('current_price', 0):.2f}\n\n"
        
        # Executive Summary
        report += "## 🎯 Executive Summary\n\n"
        
        # Find best and worst scenarios
        best_scenario = max(results.items(), key=lambda x: x[1]['price_impact']['price_change_pct'])
        worst_scenario = min(results.items(), key=lambda x: x[1]['price_impact']['price_change_pct'])
        
        report += f"**Best Case Scenario:** {best_scenario[1]['scenario'].name}\n"
        report += f"- Expected Price: ${best_scenario[1]['price_impact']['new_price']:.2f}\n"
        report += f"- Price Change: {best_scenario[1]['price_impact']['price_change_pct']:+.2f}%\n"
        report += f"- Risk Level: {best_scenario[1]['scenario'].risk_level.title()}\n\n"
        
        report += f"**Worst Case Scenario:** {worst_scenario[1]['scenario'].name}\n"
        report += f"- Expected Price: ${worst_scenario[1]['price_impact']['new_price']:.2f}\n"
        report += f"- Price Change: {worst_scenario[1]['price_impact']['price_change_pct']:+.2f}%\n"
        report += f"- Risk Level: {worst_scenario[1]['scenario'].risk_level.title()}\n\n"
        
        # Detailed Scenario Analysis
        report += "## 📈 Detailed Scenario Analysis\n\n"
        
        for scenario_name, result in results.items():
            scenario = result['scenario']
            price_impact = result['price_impact']
            recommendations = result['recommendations']
            
            report += f"### {scenario.name}\n\n"
            report += f"**Description:** {scenario.description}\n\n"
            report += f"**Expected Impact:** {scenario.expected_impact}\n\n"
            report += f"**Price Analysis:**\n"
            report += f"- Base Price: ${price_impact['base_price']:.2f}\n"
            report += f"- Expected Price: ${price_impact['new_price']:.2f}\n"
            report += f"- Price Change: {price_impact['price_change_pct']:+.2f}%\n"
            report += f"- Confidence Level: {scenario.confidence_level:.0%}\n\n"
            
            report += f"**Risk Metrics:**\n"
            risk_metrics = result['risk_metrics']
            report += f"- Volatility: {risk_metrics['volatility']:.1%}\n"
            report += f"- VaR (95%): {risk_metrics['var_metrics']['var_95']:.1%}\n"
            report += f"- Sharpe Ratio: {risk_metrics['sharpe_ratio']:.2f}\n"
            report += f"- Max Drawdown Estimate: {risk_metrics['max_drawdown_estimate']:.1%}\n\n"
            
            report += f"**Recommendations:**\n"
            report += f"- Action: {recommendations['action']}\n"
            report += f"- Reasoning: {recommendations['reasoning']}\n"
            report += f"- Position Size: {recommendations['position_size']}\n"
            report += f"- Stop Loss: ${recommendations['stop_loss']:.2f}\n"
            report += f"- Target Price: ${recommendations['target_price']:.2f}\n\n"
            
            report += "---\n\n"
        
        # Risk Factor Analysis
        report += "## ⚠️ Risk Factor Analysis\n\n"
        
        for factor_name, factor_info in self.risk_factors.items():
            report += f"**{factor_name.replace('_', ' ').title()}:**\n"
            report += f"- Description: {factor_info['description']}\n"
            report += f"- Baseline: {factor_info['baseline']:.2f}\n"
            report += f"- Range: {factor_info['range'][0]:.2f} to {factor_info['range'][1]:.2f}\n"
            report += f"- Impact Level: {factor_info['impact'].title()}\n\n"
        
        # Key Insights
        report += "## 💡 Key Insights\n\n"
        
        # Calculate average impact
        avg_impact = np.mean([r['price_impact']['price_change_pct'] for r in results.values()])
        report += f"- **Average Expected Impact:** {avg_impact:+.2f}%\n"
        
        # Count scenarios by risk level
        risk_counts = {}
        for result in results.values():
            risk_level = result['scenario'].risk_level
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        report += f"- **Risk Distribution:** {', '.join([f'{k.title()}: {v}' for k, v in risk_counts.items()])}\n"
        
        # Most sensitive factor
        all_factor_impacts = []
        for result in results.values():
            all_factor_impacts.extend(result['price_impact']['factor_impacts'].values())
        
        if all_factor_impacts:
            avg_factor_impacts = {}
            for result in results.values():
                for factor, impact in result['price_impact']['factor_impacts'].items():
                    if factor not in avg_factor_impacts:
                        avg_factor_impacts[factor] = []
                    avg_factor_impacts[factor].append(abs(impact))
            
            most_sensitive = max(avg_factor_impacts.items(), key=lambda x: np.mean(x[1]))
            report += f"- **Most Sensitive Factor:** {most_sensitive[0].replace('_', ' ').title()} (avg impact: {np.mean(most_sensitive[1]):.1f}%)\n"
        
        report += "\n## ⚠️ Disclaimer\n\n"
        report += "This sensitivity analysis is based on historical data and assumptions. "
        report += "Actual market conditions may differ significantly. "
        report += "Always conduct your own research and consult with financial advisors before making investment decisions.\n"
        
        return report
    
    def create_sensitivity_charts(self, base_data: Dict, scenarios: Dict[str, SensitivityScenario]) -> Dict:
        """Create visualization charts for sensitivity analysis."""
        
        results = self.calculate_sensitivity_metrics(base_data, scenarios)
        
        # Prepare data for charts
        scenario_names = []
        price_changes = []
        confidence_levels = []
        risk_levels = []
        
        for scenario_name, result in results.items():
            scenario_names.append(result['scenario'].name)
            price_changes.append(result['price_impact']['price_change_pct'])
            confidence_levels.append(result['scenario'].confidence_level)
            risk_levels.append(result['scenario'].risk_level)
        
        # Create price impact chart
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        colors = ['green' if x > 0 else 'red' for x in price_changes]
        bars = ax1.bar(scenario_names, price_changes, color=colors, alpha=0.7)
        ax1.set_title('Price Impact by Scenario', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price Change (%)')
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, price_changes):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + (0.1 if height > 0 else -0.5),
                    f'{value:+.1f}%', ha='center', va='bottom' if height > 0 else 'top')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Create risk vs return chart
        fig2, ax2 = plt.subplots(figsize=(10, 8))
        
        risk_level_numeric = {'low': 1, 'medium': 2, 'high': 3}
        risk_values = [risk_level_numeric[rl] for rl in risk_levels]
        
        scatter = ax2.scatter(risk_values, price_changes, s=[cl*100 for cl in confidence_levels], 
                            c=price_changes, cmap='RdYlGn', alpha=0.7)
        
        # Add scenario labels
        for i, name in enumerate(scenario_names):
            ax2.annotate(name, (risk_values[i], price_changes[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax2.set_xlabel('Risk Level (1=Low, 2=Medium, 3=High)')
        ax2.set_ylabel('Expected Price Change (%)')
        ax2.set_title('Risk vs Return Analysis', fontsize=14, fontweight='bold')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.axvline(x=2, color='black', linestyle='--', alpha=0.3)
        
        plt.colorbar(scatter, label='Price Change (%)')
        plt.tight_layout()
        
        return {
            'price_impact_chart': fig1,
            'risk_return_chart': fig2
        } 