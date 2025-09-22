import axios from 'axios';

class HuggingFaceAIService {
  constructor() {
    // Use a more effective model for financial analysis
    this.model = 'gpt2'; // Fallback to gpt2 which is more commonly available
    this.apiUrl = 'https://api-inference.huggingface.co/models';
    this.apiKey = process.env.REACT_APP_HUGGINGFACE_API_KEY || 'your_huggingface_api_key_here';
    
    // Enhanced prompt templates for better responses
    this.promptTemplates = {
      stockAnalysis: {
        system: `You are an expert AI financial analyst specializing in stock market analysis, predictions, and trading strategies. You provide accurate, well-reasoned analysis based on technical indicators, market sentiment, and fundamental data. Always include confidence levels and risk assessments.`,
        user: `Analyze {symbol} stock in {market} market. Current price: {price}. Provide comprehensive analysis including predictions, technical indicators, and trading recommendations.`,
        assistant: `I'll provide a comprehensive analysis of {symbol} in the {market} market.`
      },
      
      prediction: {
        system: `You are a specialized AI stock prediction model. You analyze historical data, technical indicators, market sentiment, and fundamental factors to provide accurate price predictions with confidence levels. Always include risk factors and alternative scenarios.`,
        user: `Predict the price movement for {symbol} over {timeframe}. Current price: {price}. Include confidence level and key factors.`,
        assistant: `Based on my analysis, here's my prediction for {symbol} over {timeframe}.`
      },
      
      technicalAnalysis: {
        system: `You are an expert technical analyst. You interpret technical indicators like RSI, MACD, Bollinger Bands, moving averages, and volume patterns to provide actionable trading signals. Always include support/resistance levels and risk management advice.`,
        user: `Provide technical analysis for {symbol}. Include RSI, MACD, support/resistance levels, and trading signals.`,
        assistant: `Here's my technical analysis for {symbol} based on current market data.`
      },
      
      marketOverview: {
        system: `You are a market analyst providing comprehensive market overviews. You analyze sector performance, market trends, volatility, and macroeconomic factors affecting stock markets. Provide actionable insights and risk assessments.`,
        user: `Provide a market overview for {market} market. Include sector performance, trends, and investment opportunities.`,
        assistant: `Here's my analysis of the {market} market based on current conditions.`
      },
      
      investmentAdvice: {
        system: `You are a certified financial advisor providing personalized investment recommendations. You consider risk tolerance, investment goals, market conditions, and diversification principles. Always include risk warnings and disclaimer.`,
        user: `Provide investment advice for {riskProfile} investor in {market} market with {amount} investment.`,
        assistant: `Based on your {riskProfile} risk profile, here are my investment recommendations for the {market} market.`
      },
      
      sentimentAnalysis: {
        system: `You are a sentiment analysis expert specializing in financial markets. You analyze news, social media, earnings reports, and market data to assess investor sentiment and market mood. Provide sentiment scores and confidence levels.`,
        user: `Analyze market sentiment for {symbol} or {market} market. Include sentiment score and key factors.`,
        assistant: `Here's my sentiment analysis for {symbol} based on current market data and news.`
      }
    };
    
    // Enhanced context management
    this.conversationContext = {
      userPreferences: {},
      marketContext: {},
      analysisHistory: [],
      riskProfile: 'moderate'
    };
  }

  // Enhanced prompt management with context
  createPrompt(templateType, variables = {}, context = {}) {
    const template = this.promptTemplates[templateType];
    if (!template) {
      throw new Error(`Unknown prompt template: ${templateType}`);
    }

    // Merge context with variables
    const enhancedVariables = {
      ...variables,
      ...this.conversationContext,
      ...context
    };

    // Replace variables in template
    let systemPrompt = template.system;
    let userPrompt = template.user;
    let assistantPrompt = template.assistant;

    Object.keys(enhancedVariables).forEach(key => {
      const placeholder = `{${key}}`;
      const value = enhancedVariables[key];
      
      systemPrompt = systemPrompt.replace(new RegExp(placeholder, 'g'), value);
      userPrompt = userPrompt.replace(new RegExp(placeholder, 'g'), value);
      assistantPrompt = assistantPrompt.replace(new RegExp(placeholder, 'g'), value);
    });

    // Add conversation history for context
    if (this.conversationContext.analysisHistory.length > 0) {
      const recentHistory = this.conversationContext.analysisHistory
        .slice(-3) // Last 3 interactions
        .map(h => `Previous: ${h.query} -> ${h.response.substring(0, 100)}...`)
        .join('\n');
      
      systemPrompt += `\n\nRecent conversation context:\n${recentHistory}`;
    }

    return {
      system: systemPrompt,
      user: userPrompt,
      assistant: assistantPrompt,
      fullPrompt: `${systemPrompt}\n\nUser: ${userPrompt}\nAssistant: ${assistantPrompt}`
    };
  }

  // Enhanced query classification with better accuracy
  classifyQuery(query) {
    const queryLower = query.toLowerCase();
    
    // Enhanced patterns for better classification
    const patterns = {
      stockAnalysis: [
        /analyze|analysis|overview|summary/i,
        /(price|value|worth|cost)\s+(of|for)/i,
        /(current|latest|present)\s+(price|value)/i
      ],
      
      prediction: [
        /predict|forecast|outlook|future|tomorrow|next\s+(week|month|year)/i,
        /(will|going\s+to|expect|anticipate)\s+(price|value|movement)/i,
        /(ai|artificial\s+intelligence|machine\s+learning)\s+(prediction|analysis)/i,
        /(end\s+of\s+day|eod|close|closing)\s+(price|value|prediction)/i
      ],
      
      technicalAnalysis: [
        /(rsi|macd|bollinger|moving\s+average|sma|ema|volume|stochastic|atr)/i,
        /(technical|indicator|chart|pattern)/i,
        /(support|resistance|trend|momentum|breakout|breakdown)/i
      ],
      
      marketOverview: [
        /market\s+(outlook|analysis|trends|sentiment|insights)/i,
        /(sector|industry)\s+(performance|analysis|outlook)/i,
        /(how\s+is|how\s+are)\s+(market|sector|industry)/i
      ],
      
      investmentAdvice: [
        /(investment|portfolio|recommend|suggest|advise|buy|sell)/i,
        /(best|top|worst)\s+(stock|investment|opportunity)/i,
        /(what\s+should|where\s+should)\s+(i\s+)?(invest|buy|sell)/i
      ],
      
      sentimentAnalysis: [
        /(sentiment|mood|feeling|opinion|view)/i,
        /(bullish|bearish|positive|negative|optimistic|pessimistic)/i,
        /(market\s+sentiment|investor\s+confidence)/i
      ],
      
      comparison: [
        /(compare|versus|vs|against|better|worse|similar)/i,
        /(performance|return|growth)\s+(comparison|vs)/i,
        /(difference\s+between|which\s+is\s+better)/i
      ],
      
      ranking: [
        /(top|best|worst|leading)\s+\d+\s+(loser|gainer|stock|performer)/i,
        /(list|show|give)\s+\d+\s+(stock|company|performer)/i
      ]
    };

    // Calculate confidence scores for each category
    const scores = {};
    Object.keys(patterns).forEach(category => {
      scores[category] = 0;
      patterns[category].forEach(pattern => {
        if (pattern.test(query)) {
          scores[category] += 1;
        }
      });
    });

    // Return the highest scoring category with confidence
    const maxScore = Math.max(...Object.values(scores));
    const primaryCategory = Object.keys(scores).find(key => scores[key] === maxScore);
    
    return {
      category: primaryCategory || 'general',
      confidence: maxScore / Math.max(...Object.values(patterns).map(p => p.length)),
      scores
    };
  }

  // Enhanced response generation with better context
  async generateResponse(query, context = {}) {
    try {
      // Classify the query
      const classification = this.classifyQuery(query);
      
      // Update conversation context
      this.conversationContext.analysisHistory.push({
        query,
        category: classification.category,
        timestamp: new Date().toISOString()
      });

      // Create appropriate prompt based on classification
      const promptData = this.createPrompt(classification.category, {
        query,
        ...context
      }, this.conversationContext);

      // Generate response using Hugging Face API
      const response = await this.callHuggingFaceAPI(promptData.fullPrompt, classification.category);
      
      // Update context with response
      this.conversationContext.analysisHistory[this.conversationContext.analysisHistory.length - 1].response = response;

      return {
        response,
        category: classification.category,
        confidence: classification.confidence,
        promptUsed: promptData.fullPrompt
      };

    } catch (error) {
      console.error('Error generating AI response:', error);
      throw new Error(`AI response generation failed: ${error.message}`);
    }
  }

  // Enhanced API call with better error handling and retry logic
  async callHuggingFaceAPI(prompt, category) {
    const maxRetries = 3;
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const response = await axios.post(
          `${this.apiUrl}/${this.model}`,
          {
            inputs: prompt,
            parameters: {
              max_length: 500,
              temperature: 0.7,
              top_p: 0.9,
              do_sample: true,
              return_full_text: false
            }
          },
          {
            headers: {
              'Authorization': `Bearer ${this.apiKey}`,
              'Content-Type': 'application/json'
            },
            timeout: 30000 // 30 second timeout
          }
        );

        if (response.data && response.data[0] && response.data[0].generated_text) {
          return this.postProcessResponse(response.data[0].generated_text, category);
        } else {
          throw new Error('Invalid response format from Hugging Face API');
        }

      } catch (error) {
        lastError = error;
        console.warn(`Attempt ${attempt} failed:`, error.message);
        
        if (attempt < maxRetries) {
          // Wait before retrying (exponential backoff)
          await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
      }
    }

    throw new Error(`Failed to generate response after ${maxRetries} attempts: ${lastError.message}`);
  }

  // Enhanced response post-processing
  postProcessResponse(response, category) {
    // Clean up the response
    let cleanedResponse = response.trim();
    
    // Remove any incomplete sentences at the end
    cleanedResponse = cleanedResponse.replace(/[^.!?]*$/, '');
    
    // Add category-specific formatting
    switch (category) {
      case 'prediction':
        cleanedResponse = this.formatPredictionResponse(cleanedResponse);
        break;
      case 'technicalAnalysis':
        cleanedResponse = this.formatTechnicalResponse(cleanedResponse);
        break;
      case 'marketOverview':
        cleanedResponse = this.formatMarketResponse(cleanedResponse);
        break;
      case 'investmentAdvice':
        cleanedResponse = this.formatInvestmentResponse(cleanedResponse);
        break;
      default:
        cleanedResponse = this.formatGeneralResponse(cleanedResponse);
    }

    return cleanedResponse;
  }

  // Category-specific response formatting
  formatPredictionResponse(response) {
    return `# 📊 **Stock Prediction Analysis**

${response}

## ⚠️ **Risk Disclaimer**
This prediction is based on AI analysis and should not be considered as financial advice. Always do your own research and consult with a financial advisor before making investment decisions.`;
  }

  formatTechnicalResponse(response) {
    return `# 📈 **Technical Analysis**

${response}

## 📊 **Key Technical Levels**
- **Support**: [Calculated support levels]
- **Resistance**: [Calculated resistance levels]
- **Trend**: [Current trend direction]`;
  }

  formatMarketResponse(response) {
    return `# 🌍 **Market Overview**

${response}

## 📈 **Market Summary**
- **Overall Trend**: [Market trend]
- **Volatility**: [Volatility level]
- **Volume**: [Volume analysis]`;
  }

  formatInvestmentResponse(response) {
    return `# 💼 **Investment Recommendations**

${response}

## ⚠️ **Important Disclaimer**
This is not financial advice. Investment decisions should be based on your own research, risk tolerance, and financial goals. Consider consulting with a qualified financial advisor.`;
  }

  formatGeneralResponse(response) {
    return `# 🤖 **AI Analysis**

${response}

---
*This analysis was generated using advanced AI technology. Please verify information independently.*`;
  }

  // Update user preferences and context
  updateContext(newContext) {
    this.conversationContext = {
      ...this.conversationContext,
      ...newContext
    };
  }

  // Get conversation history
  getConversationHistory() {
    return this.conversationContext.analysisHistory;
  }

  // Clear conversation history
  clearHistory() {
    this.conversationContext.analysisHistory = [];
  }
}

// Create singleton instance
const huggingfaceAI = new HuggingFaceAIService();

export default huggingfaceAI;
