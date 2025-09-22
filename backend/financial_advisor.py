#!/usr/bin/env python3
"""
Financial Advisor Module
Provides comprehensive financial advisory services with risk management and compliance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
import json
import re

logger = logging.getLogger(__name__)

class RiskTolerance(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class InvestmentGoal(Enum):
    RETIREMENT = "retirement"
    EDUCATION = "education"
    HOME_PURCHASE = "home_purchase"
    WEALTH_BUILDING = "wealth_building"
    INCOME_GENERATION = "income_generation"
    TAX_EFFICIENCY = "tax_efficiency"

class TimeHorizon(Enum):
    SHORT_TERM = "short_term"  # 1-3 years
    MEDIUM_TERM = "medium_term"  # 3-10 years
    LONG_TERM = "long_term"  # 10+ years

@dataclass
class ClientProfile:
    """Client financial profile and preferences"""
    age: int
    income: float
    net_worth: float
    risk_tolerance: RiskTolerance
    investment_goals: List[InvestmentGoal]
    time_horizon: TimeHorizon
    liquidity_needs: float
    tax_bracket: str
    existing_investments: Dict[str, float]
    debt_obligations: Dict[str, float]
    emergency_fund: float
    insurance_coverage: Dict[str, float]

@dataclass
class FinancialPlan:
    """Comprehensive financial plan"""
    client_profile: ClientProfile
    asset_allocation: Dict[str, float]
    investment_recommendations: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    retirement_planning: Dict[str, Any]
    tax_strategies: List[str]
    insurance_recommendations: List[str]
    debt_management: Dict[str, Any]
    emergency_fund_strategy: Dict[str, Any]
    monitoring_plan: Dict[str, Any]

@dataclass
class PortfolioRecommendation:
    """Individual portfolio recommendation"""
    symbol: str
    name: str
    allocation_percentage: float
    investment_amount: float
    risk_level: str
    expected_return: float
    rationale: str
    alternatives: List[str]

class FinancialAdvisor:
    """Professional financial advisor with comprehensive planning capabilities"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate
        self.market_return = 0.08   # 8% expected market return
        self.inflation_rate = 0.025 # 2.5% inflation rate
        
        # Asset allocation templates by risk tolerance
        self.asset_allocation_templates = {
            RiskTolerance.CONSERVATIVE: {
                'bonds': 0.60,
                'large_cap_stocks': 0.25,
                'international_stocks': 0.10,
                'cash': 0.05
            },
            RiskTolerance.MODERATE: {
                'bonds': 0.40,
                'large_cap_stocks': 0.35,
                'mid_cap_stocks': 0.15,
                'international_stocks': 0.10
            },
            RiskTolerance.AGGRESSIVE: {
                'bonds': 0.20,
                'large_cap_stocks': 0.40,
                'mid_cap_stocks': 0.20,
                'small_cap_stocks': 0.10,
                'international_stocks': 0.10
            }
        }
        
        # Investment recommendations by category
        self.investment_recommendations = {
            'bonds': {
                'conservative': ['BND', 'AGG', 'TLT'],
                'moderate': ['BND', 'AGG', 'LQD'],
                'aggressive': ['BND', 'HYG', 'EMB']
            },
            'large_cap_stocks': {
                'conservative': ['VOO', 'SPY', 'VTI'],
                'moderate': ['VOO', 'SPY', 'VTI', 'QQQ'],
                'aggressive': ['VOO', 'SPY', 'QQQ', 'VTI']
            },
            'mid_cap_stocks': {
                'moderate': ['VO', 'IJH', 'VXF'],
                'aggressive': ['VO', 'IJH', 'VXF', 'IWM']
            },
            'small_cap_stocks': {
                'aggressive': ['VB', 'IJR', 'VTWO']
            },
            'international_stocks': {
                'conservative': ['VXUS', 'EFA'],
                'moderate': ['VXUS', 'EFA', 'EEM'],
                'aggressive': ['VXUS', 'EFA', 'EEM', 'FXI']
            },
            'real_estate': {
                'moderate': ['VNQ', 'IYR'],
                'aggressive': ['VNQ', 'IYR', 'SCHH']
            },
            'commodities': {
                'aggressive': ['GLD', 'SLV', 'DJP']
            }
        }

    def create_client_profile(self, 
                            age: int,
                            income: float,
                            net_worth: float,
                            risk_tolerance: str,
                            goals: List[str],
                            time_horizon: str,
                            liquidity_needs: float = 0,
                            existing_investments: Dict[str, float] = None,
                            debt_obligations: Dict[str, float] = None) -> ClientProfile:
        """Create a comprehensive client profile"""
        
        # Convert string inputs to enums
        risk_tol = RiskTolerance(risk_tolerance.lower())
        investment_goals = [InvestmentGoal(goal.lower().replace(' ', '_')) for goal in goals]
        time_hor = TimeHorizon(time_horizon.lower().replace(' ', '_'))
        
        # Calculate emergency fund (3-6 months of expenses)
        monthly_expenses = income * 0.6  # Assume 60% of income goes to expenses
        emergency_fund = monthly_expenses * 4.5  # 4.5 months average
        
        # Estimate tax bracket
        tax_bracket = self._estimate_tax_bracket(income)
        
        return ClientProfile(
            age=age,
            income=income,
            net_worth=net_worth,
            risk_tolerance=risk_tol,
            investment_goals=investment_goals,
            time_horizon=time_hor,
            liquidity_needs=liquidity_needs,
            tax_bracket=tax_bracket,
            existing_investments=existing_investments or {},
            debt_obligations=debt_obligations or {},
            emergency_fund=emergency_fund,
            insurance_coverage={}
        )

    def generate_financial_plan(self, client_profile: ClientProfile) -> FinancialPlan:
        """Generate a comprehensive financial plan"""
        
        # Asset allocation
        asset_allocation = self._calculate_asset_allocation(client_profile)
        
        # Investment recommendations
        investment_recommendations = self._generate_investment_recommendations(
            client_profile, asset_allocation
        )
        
        # Risk assessment
        risk_assessment = self._assess_portfolio_risk(client_profile, asset_allocation)
        
        # Retirement planning
        retirement_planning = self._create_retirement_plan(client_profile)
        
        # Tax strategies
        tax_strategies = self._recommend_tax_strategies(client_profile)
        
        # Insurance recommendations
        insurance_recommendations = self._recommend_insurance(client_profile)
        
        # Debt management
        debt_management = self._create_debt_management_plan(client_profile)
        
        # Emergency fund strategy
        emergency_fund_strategy = self._create_emergency_fund_strategy(client_profile)
        
        # Monitoring plan
        monitoring_plan = self._create_monitoring_plan(client_profile)
        
        return FinancialPlan(
            client_profile=client_profile,
            asset_allocation=asset_allocation,
            investment_recommendations=investment_recommendations,
            risk_assessment=risk_assessment,
            retirement_planning=retirement_planning,
            tax_strategies=tax_strategies,
            insurance_recommendations=insurance_recommendations,
            debt_management=debt_management,
            emergency_fund_strategy=emergency_fund_strategy,
            monitoring_plan=monitoring_plan
        )

    def _calculate_asset_allocation(self, client_profile: ClientProfile) -> Dict[str, float]:
        """Calculate optimal asset allocation based on client profile"""
        
        base_allocation = self.asset_allocation_templates[client_profile.risk_tolerance].copy()
        
        # Adjust for time horizon
        if client_profile.time_horizon == TimeHorizon.SHORT_TERM:
            base_allocation['bonds'] += 0.10
            base_allocation['cash'] = base_allocation.get('cash', 0) + 0.10
        elif client_profile.time_horizon == TimeHorizon.LONG_TERM:
            base_allocation['bonds'] -= 0.10
            base_allocation['large_cap_stocks'] += 0.10
        
        # Adjust for age
        if client_profile.age < 30:
            base_allocation['bonds'] -= 0.05
            base_allocation['large_cap_stocks'] += 0.05
        elif client_profile.age > 60:
            base_allocation['bonds'] += 0.10
            base_allocation['large_cap_stocks'] -= 0.10
        
        # Normalize to 100%
        total = sum(base_allocation.values())
        return {k: v/total for k, v in base_allocation.items()}

    def _generate_investment_recommendations(self, 
                                           client_profile: ClientProfile,
                                           asset_allocation: Dict[str, float]) -> List[PortfolioRecommendation]:
        """Generate specific investment recommendations"""
        
        recommendations = []
        investable_amount = client_profile.net_worth * 0.8  # Assume 80% is investable
        
        for asset_class, allocation in asset_allocation.items():
            if allocation > 0.05:  # Only recommend if allocation > 5%
                investment_amount = investable_amount * allocation
                
                # Get recommendations for this asset class
                risk_level = client_profile.risk_tolerance.value
                if asset_class in self.investment_recommendations:
                    symbols = self.investment_recommendations[asset_class].get(risk_level, [])
                    
                    for symbol in symbols[:2]:  # Top 2 recommendations per class
                        recommendation = PortfolioRecommendation(
                            symbol=symbol,
                            name=self._get_investment_name(symbol),
                            allocation_percentage=allocation * 100,
                            investment_amount=investment_amount / len(symbols),
                            risk_level=risk_level,
                            expected_return=self._estimate_expected_return(asset_class, risk_level),
                            rationale=self._generate_rationale(asset_class, symbol, client_profile),
                            alternatives=self._get_alternatives(symbol, asset_class)
                        )
                        recommendations.append(recommendation)
        
        return recommendations

    def _assess_portfolio_risk(self, client_profile: ClientProfile, 
                              asset_allocation: Dict[str, float]) -> Dict[str, Any]:
        """Assess portfolio risk and provide risk metrics"""
        
        # Calculate portfolio volatility
        portfolio_volatility = self._calculate_portfolio_volatility(asset_allocation)
        
        # Calculate maximum drawdown potential
        max_drawdown = self._estimate_max_drawdown(asset_allocation)
        
        # Calculate Sharpe ratio
        expected_return = self._calculate_expected_return(asset_allocation)
        sharpe_ratio = (expected_return - self.risk_free_rate) / portfolio_volatility
        
        # Risk tolerance alignment
        risk_alignment = self._assess_risk_alignment(client_profile, portfolio_volatility)
        
        return {
            'portfolio_volatility': portfolio_volatility,
            'max_drawdown_potential': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'expected_return': expected_return,
            'risk_alignment': risk_alignment,
            'var_95': self._calculate_value_at_risk(asset_allocation, 0.95),
            'stress_test_results': self._run_stress_tests(asset_allocation)
        }

    def _create_retirement_plan(self, client_profile: ClientProfile) -> Dict[str, Any]:
        """Create comprehensive retirement planning strategy"""
        
        # Calculate retirement needs
        retirement_age = 65
        years_to_retirement = max(0, retirement_age - client_profile.age)
        life_expectancy = 85
        
        # Estimate retirement expenses
        current_monthly_expenses = client_profile.income * 0.6 / 12
        retirement_monthly_expenses = current_monthly_expenses * 0.8  # 80% of current expenses
        annual_retirement_expenses = retirement_monthly_expenses * 12
        
        # Calculate required retirement savings
        retirement_years = life_expectancy - retirement_age
        total_retirement_needs = annual_retirement_expenses * retirement_years
        
        # Social Security estimate
        social_security_benefit = self._estimate_social_security(client_profile.income)
        social_security_total = social_security_benefit * retirement_years
        
        # Required personal savings
        required_savings = total_retirement_needs - social_security_total
        
        # Monthly savings needed
        if years_to_retirement > 0:
            monthly_savings_needed = self._calculate_monthly_savings(
                required_savings, years_to_retirement, 0.06  # 6% return
            )
        else:
            monthly_savings_needed = 0
        
        return {
            'retirement_age': retirement_age,
            'years_to_retirement': years_to_retirement,
            'annual_retirement_expenses': annual_retirement_expenses,
            'total_retirement_needs': total_retirement_needs,
            'social_security_benefit': social_security_benefit,
            'required_personal_savings': required_savings,
            'monthly_savings_needed': monthly_savings_needed,
            'current_savings_rate': self._calculate_current_savings_rate(client_profile),
            'savings_gap': max(0, monthly_savings_needed - (client_profile.income * 0.1 / 12)),
            'recommendations': self._generate_retirement_recommendations(client_profile, monthly_savings_needed)
        }

    def _recommend_tax_strategies(self, client_profile: ClientProfile) -> List[str]:
        """Recommend tax-efficient investment strategies"""
        
        strategies = []
        
        # Tax bracket considerations
        if client_profile.tax_bracket in ['22%', '24%', '32%']:
            strategies.append("Consider Roth IRA contributions for tax-free growth")
            strategies.append("Maximize 401(k) contributions to reduce taxable income")
        
        if client_profile.tax_bracket in ['35%', '37%']:
            strategies.append("Prioritize traditional IRA/401(k) for immediate tax savings")
            strategies.append("Consider municipal bonds for tax-free income")
        
        # Tax-loss harvesting opportunities
        if client_profile.existing_investments:
            strategies.append("Implement tax-loss harvesting to offset gains")
        
        # Asset location strategy
        strategies.append("Place tax-inefficient investments in tax-advantaged accounts")
        strategies.append("Keep tax-efficient investments in taxable accounts")
        
        return strategies

    def _recommend_insurance(self, client_profile: ClientProfile) -> List[str]:
        """Recommend appropriate insurance coverage"""
        
        recommendations = []
        
        # Life insurance
        life_insurance_needed = client_profile.income * 10  # 10x income rule
        if client_profile.age < 50:
            recommendations.append(f"Consider term life insurance: ${life_insurance_needed:,.0f} coverage")
        
        # Disability insurance
        if client_profile.age < 60:
            recommendations.append("Consider disability insurance to protect income")
        
        # Health insurance
        recommendations.append("Ensure adequate health insurance coverage")
        
        # Umbrella insurance
        if client_profile.net_worth > 500000:
            recommendations.append("Consider umbrella liability insurance")
        
        # Long-term care
        if client_profile.age > 50:
            recommendations.append("Consider long-term care insurance")
        
        return recommendations

    def _create_debt_management_plan(self, client_profile: ClientProfile) -> Dict[str, Any]:
        """Create debt management and payoff strategy"""
        
        if not client_profile.debt_obligations:
            return {'status': 'no_debt', 'recommendations': ['Maintain debt-free status']}
        
        # Prioritize debt payoff
        debt_priorities = []
        for debt_type, amount in client_profile.debt_obligations.items():
            if 'credit' in debt_type.lower():
                priority = 'high'
                rate = 0.18  # 18% credit card rate
            elif 'student' in debt_type.lower():
                priority = 'medium'
                rate = 0.06  # 6% student loan rate
            elif 'mortgage' in debt_type.lower():
                priority = 'low'
                rate = 0.04  # 4% mortgage rate
            else:
                priority = 'medium'
                rate = 0.08  # 8% default rate
            
            debt_priorities.append({
                'type': debt_type,
                'amount': amount,
                'priority': priority,
                'rate': rate,
                'monthly_payment': amount * rate / 12
            })
        
        # Sort by priority and rate
        debt_priorities.sort(key=lambda x: (x['priority'] == 'high', x['rate']), reverse=True)
        
        return {
            'total_debt': sum(client_profile.debt_obligations.values()),
            'debt_priorities': debt_priorities,
            'payoff_strategy': 'avalanche_method',  # Pay highest rate first
            'recommendations': self._generate_debt_recommendations(debt_priorities)
        }

    def _create_emergency_fund_strategy(self, client_profile: ClientProfile) -> Dict[str, Any]:
        """Create emergency fund strategy"""
        
        target_emergency_fund = client_profile.income * 0.6 * 6  # 6 months expenses
        current_emergency_fund = client_profile.emergency_fund
        gap = max(0, target_emergency_fund - current_emergency_fund)
        
        if gap > 0:
            monthly_contribution = gap / 12  # Build over 12 months
            recommendations = [
                f"Build emergency fund to ${target_emergency_fund:,.0f}",
                f"Contribute ${monthly_contribution:,.0f} monthly",
                "Keep emergency fund in high-yield savings account"
            ]
        else:
            recommendations = [
                "Emergency fund is adequate",
                "Consider investing excess emergency funds"
            ]
        
        return {
            'target_amount': target_emergency_fund,
            'current_amount': current_emergency_fund,
            'gap': gap,
            'monthly_contribution_needed': gap / 12 if gap > 0 else 0,
            'recommendations': recommendations
        }

    def _create_monitoring_plan(self, client_profile: ClientProfile) -> Dict[str, Any]:
        """Create portfolio monitoring and rebalancing plan"""
        
        return {
            'review_frequency': 'quarterly',
            'rebalancing_threshold': 0.05,  # 5% deviation
            'performance_benchmarks': self._get_benchmarks(client_profile.risk_tolerance),
            'key_metrics_to_track': [
                'Portfolio return vs benchmark',
                'Asset allocation drift',
                'Risk metrics (Sharpe ratio, volatility)',
                'Tax efficiency',
                'Expense ratios'
            ],
            'rebalancing_strategy': 'threshold_based',
            'tax_considerations': 'Consider tax implications of rebalancing'
        }

    # Helper methods
    def _estimate_tax_bracket(self, income: float) -> str:
        """Estimate federal tax bracket"""
        if income <= 11000:
            return "10%"
        elif income <= 44725:
            return "12%"
        elif income <= 95375:
            return "22%"
        elif income <= 182100:
            return "24%"
        elif income <= 231250:
            return "32%"
        elif income <= 578125:
            return "35%"
        else:
            return "37%"

    def _get_investment_name(self, symbol: str) -> str:
        """Get investment name from symbol"""
        names = {
            'VOO': 'Vanguard S&P 500 ETF',
            'SPY': 'SPDR S&P 500 ETF',
            'VTI': 'Vanguard Total Stock Market ETF',
            'QQQ': 'Invesco QQQ Trust',
            'BND': 'Vanguard Total Bond Market ETF',
            'AGG': 'iShares Core U.S. Aggregate Bond ETF',
            'VXUS': 'Vanguard Total International Stock ETF',
            'EFA': 'iShares MSCI EAFE ETF',
            'EEM': 'iShares MSCI Emerging Markets ETF'
        }
        return names.get(symbol, f'{symbol} ETF')

    def _estimate_expected_return(self, asset_class: str, risk_level: str) -> float:
        """Estimate expected return for asset class"""
        base_returns = {
            'bonds': 0.04,
            'large_cap_stocks': 0.08,
            'mid_cap_stocks': 0.10,
            'small_cap_stocks': 0.12,
            'international_stocks': 0.07,
            'real_estate': 0.06,
            'commodities': 0.05
        }
        
        base_return = base_returns.get(asset_class, 0.06)
        
        # Adjust for risk level
        if risk_level == 'conservative':
            return base_return * 0.8
        elif risk_level == 'aggressive':
            return base_return * 1.2
        else:
            return base_return

    def _generate_rationale(self, asset_class: str, symbol: str, 
                           client_profile: ClientProfile) -> str:
        """Generate investment rationale"""
        rationales = {
            'bonds': f"{symbol} provides stable income and capital preservation, suitable for {client_profile.risk_tolerance.value} investors",
            'large_cap_stocks': f"{symbol} offers broad market exposure with lower volatility, ideal for {client_profile.risk_tolerance.value} portfolios",
            'international_stocks': f"{symbol} provides geographic diversification and growth opportunities in developed markets",
            'real_estate': f"{symbol} offers inflation protection and income generation through real estate exposure"
        }
        return rationales.get(asset_class, f"{symbol} provides exposure to {asset_class} assets")

    def _get_alternatives(self, symbol: str, asset_class: str) -> List[str]:
        """Get alternative investments for the same asset class"""
        alternatives = {
            'VOO': ['SPY', 'VTI'],
            'SPY': ['VOO', 'VTI'],
            'BND': ['AGG', 'TLT'],
            'VXUS': ['EFA', 'EEM']
        }
        return alternatives.get(symbol, [])

    def _calculate_portfolio_volatility(self, asset_allocation: Dict[str, float]) -> float:
        """Calculate portfolio volatility"""
        volatilities = {
            'bonds': 0.05,
            'large_cap_stocks': 0.15,
            'mid_cap_stocks': 0.18,
            'small_cap_stocks': 0.25,
            'international_stocks': 0.17,
            'real_estate': 0.20,
            'commodities': 0.25,
            'cash': 0.02
        }
        
        portfolio_volatility = 0
        for asset_class, allocation in asset_allocation.items():
            vol = volatilities.get(asset_class, 0.15)
            portfolio_volatility += (allocation * vol) ** 2
        
        return portfolio_volatility ** 0.5

    def _estimate_max_drawdown(self, asset_allocation: Dict[str, float]) -> float:
        """Estimate maximum drawdown potential"""
        max_drawdowns = {
            'bonds': 0.10,
            'large_cap_stocks': 0.50,
            'mid_cap_stocks': 0.60,
            'small_cap_stocks': 0.70,
            'international_stocks': 0.55,
            'real_estate': 0.65,
            'commodities': 0.75,
            'cash': 0.02
        }
        
        weighted_drawdown = 0
        for asset_class, allocation in asset_allocation.items():
            drawdown = max_drawdowns.get(asset_class, 0.50)
            weighted_drawdown += allocation * drawdown
        
        return weighted_drawdown

    def _calculate_expected_return(self, asset_allocation: Dict[str, float]) -> float:
        """Calculate expected portfolio return"""
        returns = {
            'bonds': 0.04,
            'large_cap_stocks': 0.08,
            'mid_cap_stocks': 0.10,
            'small_cap_stocks': 0.12,
            'international_stocks': 0.07,
            'real_estate': 0.06,
            'commodities': 0.05,
            'cash': 0.02
        }
        
        expected_return = 0
        for asset_class, allocation in asset_allocation.items():
            ret = returns.get(asset_class, 0.06)
            expected_return += allocation * ret
        
        return expected_return

    def _assess_risk_alignment(self, client_profile: ClientProfile, 
                              portfolio_volatility: float) -> str:
        """Assess if portfolio risk aligns with client risk tolerance"""
        if client_profile.risk_tolerance == RiskTolerance.CONSERVATIVE and portfolio_volatility > 0.10:
            return "Portfolio risk exceeds conservative tolerance"
        elif client_profile.risk_tolerance == RiskTolerance.AGGRESSIVE and portfolio_volatility < 0.15:
            return "Portfolio risk below aggressive tolerance"
        else:
            return "Portfolio risk aligns with risk tolerance"

    def _calculate_value_at_risk(self, asset_allocation: Dict[str, float], 
                                confidence_level: float) -> float:
        """Calculate Value at Risk"""
        portfolio_volatility = self._calculate_portfolio_volatility(asset_allocation)
        expected_return = self._calculate_expected_return(asset_allocation)
        
        # Assuming normal distribution
        z_score = 1.645 if confidence_level == 0.95 else 2.326
        var = expected_return - (z_score * portfolio_volatility)
        
        return var

    def _run_stress_tests(self, asset_allocation: Dict[str, float]) -> Dict[str, float]:
        """Run stress tests on portfolio"""
        base_return = self._calculate_expected_return(asset_allocation)
        
        return {
            'market_crash_2008': base_return - 0.40,  # 40% decline
            'dot_com_bubble': base_return - 0.30,     # 30% decline
            'covid_crash': base_return - 0.35,        # 35% decline
            'inflation_shock': base_return - 0.15,    # 15% decline
            'interest_rate_spike': base_return - 0.10  # 10% decline
        }

    def _estimate_social_security(self, income: float) -> float:
        """Estimate Social Security benefits"""
        # Simplified calculation
        if income <= 160200:  # 2023 limit
            return income * 0.40  # 40% replacement rate
        else:
            return 160200 * 0.40

    def _calculate_monthly_savings(self, target_amount: float, years: int, 
                                  annual_return: float) -> float:
        """Calculate monthly savings needed to reach target"""
        if years == 0:
            return 0
        
        monthly_rate = annual_return / 12
        months = years * 12
        
        if monthly_rate == 0:
            return target_amount / months
        else:
            return target_amount * (monthly_rate / ((1 + monthly_rate) ** months - 1))

    def _calculate_current_savings_rate(self, client_profile: ClientProfile) -> float:
        """Calculate current savings rate"""
        total_savings = sum(client_profile.existing_investments.values())
        return total_savings / client_profile.income if client_profile.income > 0 else 0

    def _generate_retirement_recommendations(self, client_profile: ClientProfile, 
                                           monthly_savings_needed: float) -> List[str]:
        """Generate retirement planning recommendations"""
        recommendations = []
        
        if monthly_savings_needed > 0:
            recommendations.append(f"Increase monthly savings by ${monthly_savings_needed:,.0f}")
        
        recommendations.append("Maximize 401(k) contributions")
        recommendations.append("Consider Roth IRA for tax diversification")
        recommendations.append("Review Social Security claiming strategy")
        recommendations.append("Consider working longer if needed")
        
        return recommendations

    def _generate_debt_recommendations(self, debt_priorities: List[Dict]) -> List[str]:
        """Generate debt management recommendations"""
        recommendations = []
        
        for debt in debt_priorities:
            if debt['priority'] == 'high':
                recommendations.append(f"Prioritize paying off {debt['type']} (${debt['amount']:,.0f})")
        
        recommendations.append("Consider debt consolidation for lower rates")
        recommendations.append("Avoid taking on new high-interest debt")
        
        return recommendations

    def _get_benchmarks(self, risk_tolerance: RiskTolerance) -> List[str]:
        """Get appropriate benchmarks for risk tolerance"""
        benchmarks = {
            RiskTolerance.CONSERVATIVE: ['BND', 'VTI'],
            RiskTolerance.MODERATE: ['VTI', 'VXUS'],
            RiskTolerance.AGGRESSIVE: ['VTI', 'VXUS', 'QQQ']
        }
        return benchmarks.get(risk_tolerance, ['VTI'])

    def generate_advice_summary(self, financial_plan: FinancialPlan) -> str:
        """Generate a comprehensive advice summary"""
        
        summary = f"""
# Financial Advisory Summary

## Client Profile
- Age: {financial_plan.client_profile.age}
- Income: ${financial_plan.client_profile.income:,.0f}
- Net Worth: ${financial_plan.client_profile.net_worth:,.0f}
- Risk Tolerance: {financial_plan.client_profile.risk_tolerance.value.title()}
- Time Horizon: {financial_plan.client_profile.time_horizon.value.replace('_', ' ').title()}

## Key Recommendations

### Asset Allocation
"""
        
        for asset_class, allocation in financial_plan.asset_allocation.items():
            summary += f"- {asset_class.replace('_', ' ').title()}: {allocation:.1%}\n"
        
        summary += f"""
### Investment Recommendations
"""
        
        for rec in financial_plan.investment_recommendations[:5]:  # Top 5
            summary += f"- {rec.symbol} ({rec.name}): {rec.allocation_percentage:.1f}% - {rec.rationale}\n"
        
        summary += f"""
### Risk Assessment
- Portfolio Volatility: {financial_plan.risk_assessment['portfolio_volatility']:.1%}
- Expected Return: {financial_plan.risk_assessment['expected_return']:.1%}
- Sharpe Ratio: {financial_plan.risk_assessment['sharpe_ratio']:.2f}
- Risk Alignment: {financial_plan.risk_assessment['risk_alignment']}

### Retirement Planning
- Monthly Savings Needed: ${financial_plan.retirement_planning['monthly_savings_needed']:,.0f}
- Years to Retirement: {financial_plan.retirement_planning['years_to_retirement']}

### Key Strategies
"""
        
        for strategy in financial_plan.tax_strategies[:3]:
            summary += f"- {strategy}\n"
        
        summary += """
### Next Steps
1. Review and approve the financial plan
2. Implement recommended asset allocation
3. Set up automatic contributions
4. Schedule quarterly reviews
5. Monitor progress and adjust as needed

*This advice is for educational purposes only. Please consult with a qualified financial advisor for personalized recommendations.*
"""
        
        return summary 