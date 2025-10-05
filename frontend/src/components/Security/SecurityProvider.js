/**
 * Security Provider Component
 * Provides security context and monitoring for the entire application
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import { 
  initializeSecurity, 
  logSecurityEvent, 
  validateSecureContext,
  validateCSP,
  cleanupSensitiveData 
} from '../../utils/security';

// Security Context
const SecurityContext = createContext();

// Security Provider Component
export const SecurityProvider = ({ children }) => {
  const [securityStatus, setSecurityStatus] = useState({
    isSecure: false,
    cspValid: false,
    initialized: false,
    threats: [],
    lastScan: null
  });

  const [securityEvents, setSecurityEvents] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(true);

  // Initialize security features
  useEffect(() => {
    const initializeAppSecurity = async () => {
      try {
        // Initialize security utilities
        initializeSecurity();

        // Check secure context
        const isSecure = validateSecureContext();
        
        // Check CSP
        const cspValid = validateCSP();

        // Scan for potential threats
        const threats = await scanForThreats();

        // Set initial security status
        setSecurityStatus({
          isSecure,
          cspValid,
          initialized: true,
          threats,
          lastScan: new Date().toISOString()
        });

        // Start security monitoring
        startSecurityMonitoring();

        // Log security initialization
        logSecurityEvent('SECURITY_INITIALIZED', {
          isSecure,
          cspValid,
          threats: threats.length
        });

      } catch (error) {
        console.error('Security initialization error:', error);
        logSecurityEvent('SECURITY_INIT_ERROR', {
          error: error.message
        });
      }
    };

    initializeAppSecurity();

    // Cleanup on unmount
    return () => {
      cleanupSensitiveData();
    };
  }, []);

  // Start security monitoring
  const startSecurityMonitoring = () => {
    if (!isMonitoring) return;

    // Monitor for suspicious activities
    const monitoringInterval = setInterval(() => {
      monitorSecurity();
    }, 30000); // Check every 30 seconds

    // Monitor for XSS attempts
    const originalInnerHTML = Element.prototype.innerHTML;
    Element.prototype.innerHTML = function(value) {
      if (value && typeof value === 'string') {
        // Check for script tags or javascript: protocols
        if (value.includes('<script') || value.includes('javascript:')) {
          logSecurityEvent('XSS_ATTEMPT', {
            content: value.substring(0, 100),
            element: this.tagName
          });
          
          setSecurityEvents(prev => [...prev, {
            type: 'XSS_ATTEMPT',
            timestamp: new Date().toISOString(),
            details: { content: value.substring(0, 100) }
          }]);
        }
      }
      return originalInnerHTML.call(this, value);
    };

    // Monitor for suspicious network requests
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
      // Check for suspicious URLs
      if (typeof url === 'string' && (
        url.includes('eval') || 
        url.includes('javascript:') ||
        url.includes('data:text/html')
      )) {
        logSecurityEvent('SUSPICIOUS_REQUEST', {
          url: url,
          method: options?.method || 'GET'
        });
        
        setSecurityEvents(prev => [...prev, {
          type: 'SUSPICIOUS_REQUEST',
          timestamp: new Date().toISOString(),
          details: { url, method: options?.method || 'GET' }
        }]);
      }
      
      return originalFetch.call(this, url, options);
    };

    // Monitor for console access attempts
    const originalConsole = { ...console };
    Object.keys(console).forEach(key => {
      if (typeof console[key] === 'function') {
        console[key] = function(...args) {
          // Log console access
          logSecurityEvent('CONSOLE_ACCESS', {
            method: key,
            args: args.map(arg => typeof arg === 'string' ? arg.substring(0, 100) : typeof arg)
          });
          
          return originalConsole[key].apply(console, args);
        };
      }
    });

    // Monitor for localStorage access
    const originalSetItem = localStorage.setItem;
    localStorage.setItem = function(key, value) {
      // Check for sensitive data
      if (key.includes('token') || key.includes('password') || key.includes('secret')) {
        logSecurityEvent('SENSITIVE_DATA_STORAGE', {
          key: key,
          valueLength: value ? value.length : 0
        });
      }
      
      return originalSetItem.call(this, key, value);
    };

    // Monitor for clipboard access
    if (navigator.clipboard) {
      const originalWriteText = navigator.clipboard.writeText;
      navigator.clipboard.writeText = function(text) {
        logSecurityEvent('CLIPBOARD_WRITE', {
          textLength: text ? text.length : 0
        });
        
        return originalWriteText.call(this, text);
      };
    }

    // Monitor for geolocation access
    if (navigator.geolocation) {
      const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
      navigator.geolocation.getCurrentPosition = function(success, error, options) {
        logSecurityEvent('GEOLOCATION_ACCESS', {
          options: options
        });
        
        return originalGetCurrentPosition.call(this, success, error, options);
      };
    }

    // Monitor for camera/microphone access
    if (navigator.mediaDevices) {
      const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
      navigator.mediaDevices.getUserMedia = function(constraints) {
        logSecurityEvent('MEDIA_ACCESS', {
          constraints: constraints
        });
        
        return originalGetUserMedia.call(this, constraints);
      };
    }

    return () => {
      clearInterval(monitoringInterval);
      // Restore original functions
      Element.prototype.innerHTML = originalInnerHTML;
      window.fetch = originalFetch;
      Object.assign(console, originalConsole);
      localStorage.setItem = originalSetItem;
    };
  };

  // Monitor security status
  const monitorSecurity = async () => {
    try {
      // Check for new threats
      const newThreats = await scanForThreats();
      
      // Update security status
      setSecurityStatus(prev => ({
        ...prev,
        threats: newThreats,
        lastScan: new Date().toISOString()
      }));

      // Check for security policy violations
      checkSecurityPolicies();

    } catch (error) {
      console.error('Security monitoring error:', error);
    }
  };

  // Scan for potential threats
  const scanForThreats = async () => {
    const threats = [];

    try {
      // Check for malicious scripts
      const scripts = document.querySelectorAll('script');
      scripts.forEach(script => {
        if (script.src && (
          script.src.includes('eval') ||
          script.src.includes('javascript:') ||
          script.src.includes('data:text/html')
        )) {
          threats.push({
            type: 'MALICIOUS_SCRIPT',
            severity: 'HIGH',
            description: 'Potentially malicious script detected',
            source: script.src
          });
        }
      });

      // Check for suspicious iframes
      const iframes = document.querySelectorAll('iframe');
      iframes.forEach(iframe => {
        if (iframe.src && (
          iframe.src.includes('javascript:') ||
          iframe.src.includes('data:text/html')
        )) {
          threats.push({
            type: 'SUSPICIOUS_IFRAME',
            severity: 'MEDIUM',
            description: 'Suspicious iframe detected',
            source: iframe.src
          });
        }
      });

      // Check for suspicious event handlers
      const elements = document.querySelectorAll('[onclick], [onload], [onerror]');
      elements.forEach(element => {
        const handlers = ['onclick', 'onload', 'onerror'];
        handlers.forEach(handler => {
          const value = element.getAttribute(handler);
          if (value && (
            value.includes('eval') ||
            value.includes('javascript:') ||
            value.includes('document.cookie')
          )) {
            threats.push({
              type: 'SUSPICIOUS_EVENT_HANDLER',
              severity: 'MEDIUM',
              description: 'Suspicious event handler detected',
              element: element.tagName,
              handler: handler
            });
          }
        });
      });

      // Check for suspicious localStorage data
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        const value = localStorage.getItem(key);
        
        if (key && value && (
          key.includes('token') && value.length > 1000 ||
          key.includes('password') ||
          key.includes('secret')
        )) {
          threats.push({
            type: 'SENSITIVE_DATA_EXPOSURE',
            severity: 'HIGH',
            description: 'Sensitive data found in localStorage',
            key: key
          });
        }
      }

      // Check for suspicious cookies
      document.cookie.split(';').forEach(cookie => {
        const [name, value] = cookie.trim().split('=');
        if (name && value && (
          name.includes('token') && value.length > 1000 ||
          name.includes('password') ||
          name.includes('secret')
        )) {
          threats.push({
            type: 'SENSITIVE_COOKIE',
            severity: 'MEDIUM',
            description: 'Sensitive data found in cookie',
            name: name
          });
        }
      });

    } catch (error) {
      console.error('Threat scan error:', error);
    }

    return threats;
  };

  // Check security policies
  const checkSecurityPolicies = () => {
    const violations = [];

    // Check HTTPS usage
    if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
      violations.push({
        type: 'INSECURE_PROTOCOL',
        severity: 'HIGH',
        description: 'Application is not using HTTPS'
      });
    }

    // Check for missing security headers
    const requiredHeaders = [
      'Content-Security-Policy',
      'X-Frame-Options',
      'X-Content-Type-Options'
    ];

    // This would typically be checked by making a request to the backend
    // For now, we'll just log the check
    logSecurityEvent('SECURITY_POLICY_CHECK', {
      requiredHeaders: requiredHeaders,
      violations: violations.length
    });

    if (violations.length > 0) {
      setSecurityEvents(prev => [...prev, ...violations.map(v => ({
        type: v.type,
        timestamp: new Date().toISOString(),
        details: v
      }))]);
    }
  };

  // Security actions
  const securityActions = {
    // Toggle security monitoring
    toggleMonitoring: () => {
      setIsMonitoring(prev => !prev);
      logSecurityEvent('SECURITY_MONITORING_TOGGLED', {
        enabled: !isMonitoring
      });
    },

    // Clear security events
    clearEvents: () => {
      setSecurityEvents([]);
      logSecurityEvent('SECURITY_EVENTS_CLEARED', {});
    },

    // Generate security report
    generateReport: () => {
      const report = {
        timestamp: new Date().toISOString(),
        securityStatus,
        eventCount: securityEvents.length,
        threats: securityStatus.threats,
        recommendations: generateRecommendations()
      };

      logSecurityEvent('SECURITY_REPORT_GENERATED', {
        eventCount: securityEvents.length,
        threatCount: securityStatus.threats.length
      });

      return report;
    },

    // Scan for threats
    scanThreats: async () => {
      const threats = await scanForThreats();
      setSecurityStatus(prev => ({
        ...prev,
        threats,
        lastScan: new Date().toISOString()
      }));

      logSecurityEvent('THREAT_SCAN_COMPLETED', {
        threatCount: threats.length
      });

      return threats;
    },

    // Clean up sensitive data
    cleanup: () => {
      cleanupSensitiveData();
      logSecurityEvent('SENSITIVE_DATA_CLEANUP', {});
    }
  };

  // Generate security recommendations
  const generateRecommendations = () => {
    const recommendations = [];

    if (!securityStatus.isSecure) {
      recommendations.push({
        type: 'SECURE_CONTEXT',
        priority: 'HIGH',
        description: 'Enable HTTPS for secure context'
      });
    }

    if (!securityStatus.cspValid) {
      recommendations.push({
        type: 'CSP',
        priority: 'HIGH',
        description: 'Implement Content Security Policy'
      });
    }

    if (securityStatus.threats.length > 0) {
      recommendations.push({
        type: 'THREATS',
        priority: 'MEDIUM',
        description: `Address ${securityStatus.threats.length} security threats`
      });
    }

    return recommendations;
  };

  // Context value
  const contextValue = {
    securityStatus,
    securityEvents,
    isMonitoring,
    actions: securityActions,
    recommendations: generateRecommendations()
  };

  return (
    <SecurityContext.Provider value={contextValue}>
      {children}
    </SecurityContext.Provider>
  );
};

// Hook to use security context
export const useSecurity = () => {
  const context = useContext(SecurityContext);
  if (!context) {
    throw new Error('useSecurity must be used within a SecurityProvider');
  }
  return context;
};

// Security Status Component
export const SecurityStatus = () => {
  const { securityStatus, isMonitoring } = useSecurity();

  if (!securityStatus.initialized) {
    return (
      <div className="flex items-center space-x-2 text-gray-500">
        <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
        <span className="text-sm">Initializing Security...</span>
      </div>
    );
  }

  const getStatusColor = () => {
    if (!securityStatus.isSecure || !securityStatus.cspValid) {
      return 'bg-red-400';
    }
    if (securityStatus.threats.length > 0) {
      return 'bg-yellow-400';
    }
    return 'bg-green-400';
  };

  const getStatusText = () => {
    if (!securityStatus.isSecure || !securityStatus.cspValid) {
      return 'Security Issues';
    }
    if (securityStatus.threats.length > 0) {
      return 'Threats Detected';
    }
    return 'Secure';
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-2 h-2 rounded-full ${getStatusColor()}`}></div>
      <span className="text-sm text-gray-600">
        {getStatusText()}
        {!isMonitoring && ' (Monitoring Disabled)'}
      </span>
    </div>
  );
};

// Security Dashboard Component
export const SecurityDashboard = () => {
  const { securityStatus, securityEvents, actions } = useSecurity();

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Security Dashboard</h2>
        <div className="flex space-x-2">
          <button
            onClick={actions.scanThreats}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Scan Threats
          </button>
          <button
            onClick={actions.clearEvents}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Clear Events
          </button>
        </div>
      </div>

      {/* Security Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Secure Context</h3>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${securityStatus.isSecure ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span className="text-sm">{securityStatus.isSecure ? 'Secure' : 'Insecure'}</span>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">CSP Status</h3>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${securityStatus.cspValid ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span className="text-sm">{securityStatus.cspValid ? 'Valid' : 'Invalid'}</span>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Threats</h3>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${securityStatus.threats.length === 0 ? 'bg-green-400' : 'bg-yellow-400'}`}></div>
            <span className="text-sm">{securityStatus.threats.length} detected</span>
          </div>
        </div>
      </div>

      {/* Recent Security Events */}
      <div className="mb-6">
        <h3 className="font-semibold text-gray-900 mb-4">Recent Security Events</h3>
        <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
          {securityEvents.length === 0 ? (
            <p className="text-gray-500 text-sm">No security events</p>
          ) : (
            <div className="space-y-2">
              {securityEvents.slice(-10).map((event, index) => (
                <div key={index} className="text-sm">
                  <div className="flex justify-between">
                    <span className="font-medium">{event.type}</span>
                    <span className="text-gray-500">{new Date(event.timestamp).toLocaleTimeString()}</span>
                  </div>
                  {event.details && (
                    <div className="text-gray-600 mt-1">
                      {JSON.stringify(event.details, null, 2)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Security Recommendations */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-4">Recommendations</h3>
        <div className="space-y-2">
          {actions.recommendations.map((rec, index) => (
            <div key={index} className="flex items-center space-x-2 p-3 bg-yellow-50 rounded-lg">
              <div className={`w-2 h-2 rounded-full ${rec.priority === 'HIGH' ? 'bg-red-400' : 'bg-yellow-400'}`}></div>
              <span className="text-sm">{rec.description}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SecurityProvider;
