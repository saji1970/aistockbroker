import React, {createContext, useContext, useReducer, ReactNode} from 'react';

// Types
export interface InvestmentSettings {
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
  investmentAmount: number;
  preferredCurrencies: string[];
  autoRebalance: boolean;
  stopLossPercentage: number;
  takeProfitPercentage: number;
  maxPositionSize: number;
  diversificationTarget: number;
}

export interface PortfolioPosition {
  symbol: string;
  shares: number;
  averagePrice: number;
  currentPrice: number;
  marketValue: number;
  gainLoss: number;
  gainLossPercentage: number;
}

export interface Portfolio {
  totalValue: number;
  cash: number;
  positions: PortfolioPosition[];
  performance: {
    totalReturn: number;
    totalReturnPercentage: number;
    dailyReturn: number;
    dailyReturnPercentage: number;
  };
  lastUpdated: string;
}

export interface AppState {
  currentSymbol: string;
  currentPeriod: string;
  currentMarket: string;
  investmentSettings: InvestmentSettings;
  portfolio: Portfolio;
  sidebarOpen: boolean;
}

// Actions
type Action =
  | {type: 'SET_CURRENT_SYMBOL'; payload: string}
  | {type: 'SET_CURRENT_PERIOD'; payload: string}
  | {type: 'SET_CURRENT_MARKET'; payload: string}
  | {type: 'UPDATE_INVESTMENT_SETTINGS'; payload: Partial<InvestmentSettings>}
  | {type: 'UPDATE_PORTFOLIO'; payload: Portfolio}
  | {type: 'ADD_POSITION'; payload: PortfolioPosition}
  | {type: 'REMOVE_POSITION'; payload: string}
  | {type: 'TOGGLE_SIDEBAR'};

// Initial state
const initialState: AppState = {
  currentSymbol: 'AAPL',
  currentPeriod: '1y',
  currentMarket: 'US',
  investmentSettings: {
    riskTolerance: 'moderate',
    investmentAmount: 10000,
    preferredCurrencies: ['USD'],
    autoRebalance: false,
    stopLossPercentage: 10,
    takeProfitPercentage: 20,
    maxPositionSize: 20,
    diversificationTarget: 10,
  },
  portfolio: {
    totalValue: 10000,
    cash: 10000,
    positions: [],
    performance: {
      totalReturn: 0,
      totalReturnPercentage: 0,
      dailyReturn: 0,
      dailyReturnPercentage: 0,
    },
    lastUpdated: new Date().toISOString(),
  },
  sidebarOpen: false,
};

// Reducer
function appReducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_CURRENT_SYMBOL':
      return {...state, currentSymbol: action.payload};
    case 'SET_CURRENT_PERIOD':
      return {...state, currentPeriod: action.payload};
    case 'SET_CURRENT_MARKET':
      return {...state, currentMarket: action.payload};
    case 'UPDATE_INVESTMENT_SETTINGS':
      return {
        ...state,
        investmentSettings: {...state.investmentSettings, ...action.payload},
      };
    case 'UPDATE_PORTFOLIO':
      return {...state, portfolio: action.payload};
    case 'ADD_POSITION':
      const existingPositionIndex = state.portfolio.positions.findIndex(
        p => p.symbol === action.payload.symbol,
      );
      let updatedPositions = [...state.portfolio.positions];
      
      if (existingPositionIndex >= 0) {
        // Update existing position
        const existing = state.portfolio.positions[existingPositionIndex];
        const totalShares = existing.shares + action.payload.shares;
        const totalCost = existing.shares * existing.averagePrice + action.payload.shares * action.payload.averagePrice;
        const newAveragePrice = totalCost / totalShares;
        
        updatedPositions[existingPositionIndex] = {
          ...action.payload,
          shares: totalShares,
          averagePrice: newAveragePrice,
          marketValue: totalShares * action.payload.currentPrice,
          gainLoss: (action.payload.currentPrice - newAveragePrice) * totalShares,
          gainLossPercentage: ((action.payload.currentPrice - newAveragePrice) / newAveragePrice) * 100,
        };
      } else {
        // Add new position
        updatedPositions.push(action.payload);
      }
      
      const newTotalValue = updatedPositions.reduce((sum, pos) => sum + pos.marketValue, 0) + state.portfolio.cash;
      
      return {
        ...state,
        portfolio: {
          ...state.portfolio,
          positions: updatedPositions,
          totalValue: newTotalValue,
          lastUpdated: new Date().toISOString(),
        },
      };
    case 'REMOVE_POSITION':
      const filteredPositions = state.portfolio.positions.filter(
        p => p.symbol !== action.payload,
      );
      const newTotalValueAfterRemoval = filteredPositions.reduce((sum, pos) => sum + pos.marketValue, 0) + state.portfolio.cash;
      
      return {
        ...state,
        portfolio: {
          ...state.portfolio,
          positions: filteredPositions,
          totalValue: newTotalValueAfterRemoval,
          lastUpdated: new Date().toISOString(),
        },
      };
    case 'TOGGLE_SIDEBAR':
      return {...state, sidebarOpen: !state.sidebarOpen};
    default:
      return state;
  }
}

// Context
interface StoreContextType {
  state: AppState;
  dispatch: React.Dispatch<Action>;
}

const StoreContext = createContext<StoreContextType | undefined>(undefined);

// Provider
export function StoreProvider({children}: {children: ReactNode}) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <StoreContext.Provider value={{state, dispatch}}>
      {children}
    </StoreContext.Provider>
  );
}

// Hook
export function useStore() {
  const context = useContext(StoreContext);
  if (context === undefined) {
    throw new Error('useStore must be used within a StoreProvider');
  }
  return context;
} 