import React from 'react';
import { 
  // Navigation Icons
  HomeIcon,
  ChartBarIcon,
  CogIcon,
  UserIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  ArrowRightOnRectangleIcon,
  
  // Feature Icons
  SparklesIcon,
  CpuChipIcon,
  BriefcaseIcon,
  BoltIcon,
  BeakerIcon,
  LightBulbIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  CalculatorIcon,
  
  // Action Icons
  EyeIcon,
  EyeSlashIcon,
  Bars3Icon,
  XMarkIcon,
  PaperAirplaneIcon,
  ChatBubbleLeftRightIcon,
  MagnifyingGlassIcon,
  ClockIcon,
  CalendarDaysIcon,
  
  // Status Icons
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

const iconMap = {
  // Navigation
  'home': HomeIcon,
  'dashboard': ChartBarIcon,
  'settings': CogIcon,
  'user': UserIcon,
  'users': UserGroupIcon,
  'admin': ShieldCheckIcon,
  'logout': ArrowRightOnRectangleIcon,
  
  // Features
  'sparkles': SparklesIcon,
  'ai': CpuChipIcon,
  'ai-assistant': CpuChipIcon,
  'portfolio': BriefcaseIcon,
  'trading': BoltIcon,
  'trading-bot': BoltIcon,
  'backtest': BeakerIcon,
  'lightbulb': LightBulbIcon,
  'money': CurrencyDollarIcon,
  'trending': ArrowTrendingUpIcon,
  'calculator': CalculatorIcon,
  'agent-dashboard': UserGroupIcon,
  
  // Actions
  'eye': EyeIcon,
  'eye-slash': EyeSlashIcon,
  'menu': Bars3Icon,
  'close': XMarkIcon,
  'send': PaperAirplaneIcon,
  'chat': ChatBubbleLeftRightIcon,
  'search': MagnifyingGlassIcon,
  'clock': ClockIcon,
  'calendar': CalendarDaysIcon,
  
  // Status
  'success': CheckCircleIcon,
  'error': XCircleIcon,
  'warning': ExclamationTriangleIcon,
  'info': InformationCircleIcon
};

const ModernIcon = ({ 
  name, 
  size = 'md', 
  color = 'primary', 
  effect = 'none',
  container = false,
  badge = false,
  badgeCount = null,
  className = '',
  ...props 
}) => {
  const IconComponent = iconMap[name];
  
  if (!IconComponent) {
    console.warn(`Icon "${name}" not found in iconMap`);
    return null;
  }

  // Size classes
  const sizeClasses = {
    'sm': 'icon-sm',
    'md': 'icon-md', 
    'lg': 'icon-lg',
    'xl': 'icon-xl'
  };

  // Color classes
  const colorClasses = {
    'primary': 'icon-primary',
    'secondary': 'icon-secondary',
    'success': 'icon-success',
    'danger': 'icon-danger',
    'warning': 'icon-warning',
    'gray': 'icon-gray'
  };

  // Effect classes
  const effectClasses = {
    'none': '',
    'glow': 'icon-glow',
    'pulse': 'icon-pulse',
    'float': 'icon-float',
    'rotate': 'icon-rotate',
    'bounce': 'icon-bounce'
  };

  // Container classes
  const containerClasses = {
    'sm': 'icon-container-sm',
    'md': 'icon-container-md',
    'lg': 'icon-container-lg'
  };

  // Container color classes
  const containerColorClasses = {
    'primary': 'icon-container-primary',
    'secondary': 'icon-container-secondary',
    'success': 'icon-container-success',
    'danger': 'icon-container-danger',
    'warning': 'icon-container-warning'
  };

  const iconClasses = [
    sizeClasses[size],
    colorClasses[color],
    effectClasses[effect],
    className
  ].filter(Boolean).join(' ');

  const containerClass = container ? [
    'icon-container',
    containerClasses[size],
    containerColorClasses[color]
  ].filter(Boolean).join(' ') : '';

  const badgeClass = badge ? 'icon-badge' : '';
  const notificationClass = badge && badgeCount ? 'icon-badge-notification' : '';

  const iconElement = (
    <IconComponent 
      className={iconClasses}
      {...props}
    />
  );

  if (badge) {
    return (
      <span 
        className={`${badgeClass} ${notificationClass}`}
        data-count={badgeCount}
      >
        {container ? (
          <span className={containerClass}>
            {iconElement}
          </span>
        ) : (
          iconElement
        )}
      </span>
    );
  }

  if (container) {
    return (
      <span className={containerClass}>
        {iconElement}
      </span>
    );
  }

  return iconElement;
};

// Icon Button Component
export const IconButton = ({ 
  icon, 
  onClick, 
  variant = 'primary',
  size = 'md',
  disabled = false,
  className = '',
  ...props 
}) => {
  const variantClasses = {
    'primary': 'icon-button-primary',
    'secondary': 'icon-button-secondary',
    'success': 'icon-button-success',
    'danger': 'icon-button-danger'
  };

  const buttonClasses = [
    'icon-button',
    variantClasses[variant],
    disabled ? 'opacity-50 cursor-not-allowed' : 'icon-hover-scale',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      <ModernIcon name={icon} size={size} />
    </button>
  );
};

// Icon Group Component
export const IconGroup = ({ 
  icons = [], 
  direction = 'horizontal',
  spacing = 'md',
  className = ''
}) => {
  const directionClasses = {
    'horizontal': 'icon-group',
    'vertical': 'icon-group-stacked',
    'connected': 'icon-group-connected'
  };

  const groupClasses = [
    directionClasses[direction],
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={groupClasses}>
      {icons.map((icon, index) => (
        <ModernIcon
          key={index}
          name={icon.name}
          size={icon.size || 'md'}
          color={icon.color || 'primary'}
          effect={icon.effect || 'none'}
          container={icon.container || false}
          className={icon.className || ''}
        />
      ))}
    </div>
  );
};

// Custom Icon Shapes
export const IconShape = ({ 
  children, 
  shape = 'circle',
  size = 'md',
  color = 'primary',
  className = ''
}) => {
  const shapeClasses = {
    'circle': 'icon-circle',
    'square': 'icon-square',
    'rounded': 'icon-rounded'
  };

  const sizeClasses = {
    'sm': 'icon-sm',
    'md': 'icon-md',
    'lg': 'icon-lg',
    'xl': 'icon-xl'
  };

  const classes = [
    shapeClasses[shape],
    sizeClasses[size],
    className
  ].filter(Boolean).join(' ');

  return (
    <span className={classes}>
      {children}
    </span>
  );
};

export default ModernIcon;
