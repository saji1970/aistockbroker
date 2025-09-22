/**
 * Safe logging utility to prevent circular reference errors
 */

/**
 * Safely stringify an object, handling circular references
 * @param {any} obj - Object to stringify
 * @param {number} maxDepth - Maximum depth to traverse
 * @returns {string} - Safe string representation
 */
export const safeStringify = (obj, maxDepth = 3) => {
  const seen = new WeakSet();
  
  const replacer = (key, value) => {
    // Skip functions
    if (typeof value === 'function') {
      return '[Function]';
    }
    
    // Skip DOM elements and React components
    if (value && typeof value === 'object') {
      if (value.constructor === HTMLElement || 
          value.constructor === HTMLSpanElement ||
          value.constructor === HTMLDivElement ||
          value.constructor === HTMLCanvasElement ||
          value.__reactFiber$ ||
          value.__reactInternalInstance$ ||
          value.__reactInternalFiber) {
        return '[DOM Element or React Component]';
      }
      
      // Handle circular references
      if (seen.has(value)) {
        return '[Circular Reference]';
      }
      seen.add(value);
    }
    
    return value;
  };
  
  try {
    return JSON.stringify(obj, replacer, 2);
  } catch (error) {
    return `[Error stringifying object: ${error.message}]`;
  }
};

/**
 * Safely log an object without causing circular reference errors
 * @param {string} message - Log message
 * @param {any} data - Data to log
 */
export const safeLog = (message, data = null) => {
  if (data === null || data === undefined) {
    console.log(message);
    return;
  }
  
  try {
    const safeData = safeStringify(data);
    console.log(message, safeData);
  } catch (error) {
    console.log(message, '[Error logging data]');
  }
};

/**
 * Safely log an error with context
 * @param {string} message - Error message
 * @param {Error} error - Error object
 * @param {any} context - Additional context data
 */
export const safeLogError = (message, error, context = null) => {
  console.error(message);
  console.error('Error:', error.message);
  
  if (context) {
    try {
      const safeContext = safeStringify(context);
      console.error('Context:', safeContext);
    } catch (e) {
      console.error('Context: [Error logging context]');
    }
  }
  
  if (error.stack) {
    console.error('Stack:', error.stack);
  }
};

/**
 * Check if an object contains circular references
 * @param {any} obj - Object to check
 * @returns {boolean} - True if circular references found
 */
export const hasCircularReference = (obj) => {
  const seen = new WeakSet();
  
  const check = (value) => {
    if (value && typeof value === 'object') {
      if (seen.has(value)) {
        return true;
      }
      seen.add(value);
      
      for (const key in value) {
        if (check(value[key])) {
          return true;
        }
      }
    }
    return false;
  };
  
  return check(obj);
};

export default {
  safeStringify,
  safeLog,
  safeLogError,
  hasCircularReference
};
