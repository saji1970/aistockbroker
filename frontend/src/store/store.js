import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useStore = create(
  persist(
    (set, get) => ({
      // App state
      isLoading: false,
      currentSymbol: 'AAPL',
      currentPeriod: '1y',
      
      // Market selection
      currentMarket: 'US', // Default to US market
      
      // Investment settings
      investmentSettings: {
        riskTolerance: 'moderate', // conservative, moderate, aggressive
        investmentAmount: 10000,
        preferredCurrencies: ['USD', 'EUR', 'GBP'],
        autoRebalance: true,
        stopLossPercentage: 10,
        takeProfitPercentage: 20,
        maxPositionSize: 25, // percentage of portfolio
        diversificationTarget: 8, // number of different assets
      },
      
      // Portfolio state
      portfolio: {
        totalValue: 10000,
        cash: 5000,
        positions: [],
        performance: {
          daily: 0,
          weekly: 0,
          monthly: 0,
          yearly: 0,
        },
        lastUpdated: new Date().toISOString(),
      },
      
      // UI state
      theme: 'light',
      sidebarOpen: false,
      
      // Actions
      setLoading: (loading) => set({ isLoading: loading }),
      setCurrentSymbol: (symbol) => set({ currentSymbol: symbol }),
      setCurrentPeriod: (period) => set({ currentPeriod: period }),
      setCurrentMarket: (market) => set({ currentMarket: market }),
      
      // Investment actions
      updateInvestmentSettings: (settings) => set((state) => ({
        investmentSettings: { ...state.investmentSettings, ...settings }
      })),
      
      // Portfolio actions
      updatePortfolio: (portfolio) => set({ portfolio }),
      addPosition: (position) => set((state) => ({
        portfolio: {
          ...state.portfolio,
          positions: [...state.portfolio.positions, position],
          cash: state.portfolio.cash - (position.quantity * position.avg_price),
          totalValue: state.portfolio.totalValue + (position.quantity * position.avg_price),
        }
      })),
      removePosition: (symbol) => set((state) => ({
        portfolio: {
          ...state.portfolio,
          positions: state.portfolio.positions.filter(p => p.symbol !== symbol),
        }
      })),
      
      // UI actions
      setTheme: (theme) => set({ theme }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
    }),
    {
      name: 'ai-stock-trading-storage',
      partialize: (state) => ({
        currentSymbol: state.currentSymbol,
        currentPeriod: state.currentPeriod,
        currentMarket: state.currentMarket,
        investmentSettings: state.investmentSettings,
        portfolio: state.portfolio,
        theme: state.theme,
      }),
    }
  )
);

export { useStore }; 