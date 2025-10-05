# Modern Icon System

A comprehensive, customizable icon system for the AI Stock Trading application with modern effects, animations, and styling options.

## Features

- **Modern Design**: Clean, consistent icons with contemporary styling
- **Multiple Sizes**: Small, medium, large, and extra-large variants
- **Color Themes**: Primary, secondary, success, danger, warning, and gray variants
- **Visual Effects**: Glow, pulse, float, rotate, and bounce animations
- **Container Support**: Background containers with gradient effects
- **Badge Support**: Notification badges and count indicators
- **Responsive**: Mobile-optimized sizing and effects
- **Accessible**: Screen reader support and focus states
- **Dark Mode**: Automatic dark mode color adjustments

## Usage

### Basic Icon

```jsx
import ModernIcon from '../components/UI/ModernIcon';

// Simple icon
<ModernIcon name="sparkles" size="lg" color="primary" />
```

### Icon with Container

```jsx
// Icon with background container
<ModernIcon name="ai" size="md" color="secondary" container />
```

### Icon with Effects

```jsx
// Pulsing icon
<ModernIcon name="portfolio" size="lg" color="success" effect="pulse" />

// Rotating icon on hover
<ModernIcon name="trading" size="md" color="warning" effect="rotate" />

// Floating icon
<ModernIcon name="sparkles" size="lg" color="primary" effect="float" />
```

### Icon Buttons

```jsx
import { IconButton } from '../components/UI/ModernIcon';

// Clickable icon button
<IconButton 
  icon="home" 
  variant="primary" 
  onClick={handleClick}
  size="lg"
/>
```

### Icon Groups

```jsx
import { IconGroup } from '../components/UI/ModernIcon';

// Horizontal group
<IconGroup 
  icons={[
    { name: 'home', color: 'primary' },
    { name: 'sparkles', color: 'secondary' },
    { name: 'success', color: 'success' }
  ]} 
  direction="horizontal" 
/>

// Vertical group
<IconGroup 
  icons={[
    { name: 'sparkles', color: 'primary' },
    { name: 'portfolio', color: 'secondary' }
  ]} 
  direction="vertical" 
/>
```

### Icon Shapes

```jsx
import { IconShape } from '../components/UI/ModernIcon';

// Circular container
<IconShape shape="circle" size="lg" color="primary">
  <ModernIcon name="sparkles" size="md" color="white" />
</IconShape>

// Square container
<IconShape shape="square" size="lg" color="secondary">
  <ModernIcon name="ai" size="md" color="white" />
</IconShape>

// Rounded container
<IconShape shape="rounded" size="lg" color="success">
  <ModernIcon name="portfolio" size="md" color="white" />
</IconShape>
```

### Badge Icons

```jsx
// Simple badge
<ModernIcon 
  name="chat" 
  size="lg" 
  color="primary" 
  badge 
  container 
/>

// Notification with count
<ModernIcon 
  name="chat" 
  size="lg" 
  color="secondary" 
  badge 
  badgeCount="5"
  container 
/>

// High count badge
<ModernIcon 
  name="chat" 
  size="lg" 
  color="danger" 
  badge 
  badgeCount="99+"
  container 
/>
```

## Available Icons

### Navigation Icons
- `home` - Home/Dashboard
- `dashboard` - Analytics Dashboard
- `settings` - Configuration
- `user` - User Profile
- `users` - User Management
- `admin` - Admin Panel
- `logout` - Sign Out

### Feature Icons
- `sparkles` - AI Features
- `ai` - AI Assistant
- `portfolio` - Portfolio Management
- `trading` - Trading Bot
- `backtest` - Strategy Testing
- `lightbulb` - Smart Features
- `money` - Financial Tools
- `trending` - Market Trends
- `calculator` - Calculations

### Action Icons
- `eye` - View/Show
- `eye-slash` - Hide
- `menu` - Menu/Hamburger
- `close` - Close/Cancel
- `send` - Send/Submit
- `chat` - Chat/Message
- `search` - Search
- `clock` - Time/Schedule

### Status Icons
- `success` - Success/Check
- `error` - Error/Failure
- `warning` - Warning/Alert
- `info` - Information

## Sizes

- `sm` - Small (1rem)
- `md` - Medium (1.5rem) - Default
- `lg` - Large (2rem)
- `xl` - Extra Large (2.5rem)

## Colors

- `primary` - Blue theme (#0ea5e9)
- `secondary` - Purple theme (#c026d3)
- `success` - Green theme (#22c55e)
- `danger` - Red theme (#ef4444)
- `warning` - Yellow theme (#f59e0b)
- `gray` - Gray theme (#6b7280)

## Effects

- `none` - No effect (default)
- `glow` - Glowing shadow effect
- `pulse` - Pulsing animation
- `float` - Floating animation
- `rotate` - Rotation on hover
- `bounce` - Bouncing animation

## CSS Classes

The system provides extensive CSS classes for custom styling:

### Icon Base Classes
- `.icon-custom` - Base icon styling
- `.icon-sm`, `.icon-md`, `.icon-lg`, `.icon-xl` - Size variants

### Color Classes
- `.icon-primary`, `.icon-secondary`, `.icon-success`, `.icon-danger`, `.icon-warning`, `.icon-gray`

### Effect Classes
- `.icon-glow`, `.icon-pulse`, `.icon-float`, `.icon-rotate`, `.icon-bounce`

### Container Classes
- `.icon-container`, `.icon-container-sm`, `.icon-container-md`, `.icon-container-lg`
- `.icon-container-primary`, `.icon-container-secondary`, etc.

### Button Classes
- `.icon-button`, `.icon-button-primary`, `.icon-button-secondary`, etc.

### Badge Classes
- `.icon-badge`, `.icon-badge-notification`

### Utility Classes
- `.icon-hover-scale`, `.icon-hover-rotate`, `.icon-hover-bounce`, `.icon-hover-glow`

## Responsive Design

Icons automatically adjust size on mobile devices:
- Small screens: Reduced icon sizes
- Touch-friendly: Larger touch targets
- Performance: Optimized animations

## Dark Mode Support

Automatic dark mode color adjustments:
- Primary colors become lighter in dark mode
- Container backgrounds adjust for contrast
- Maintains accessibility standards

## Accessibility

- Screen reader support with semantic markup
- Focus states for keyboard navigation
- High contrast color combinations
- Reduced motion support for animations

## Performance

- Optimized CSS animations
- Minimal JavaScript overhead
- Efficient rendering
- Lazy loading support

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Progressive enhancement for older browsers

## Examples

See `IconShowcase.js` component for comprehensive examples of all features and usage patterns.

## Migration Guide

To migrate from existing Heroicons usage:

1. Replace direct icon imports with `ModernIcon` component
2. Update icon names to use the new naming convention
3. Add size and color props for consistent styling
4. Use container prop for background effects
5. Add effects for enhanced visual appeal

### Before
```jsx
import { SparklesIcon } from '@heroicons/react/24/outline';

<SparklesIcon className="h-6 w-6 text-blue-500" />
```

### After
```jsx
import ModernIcon from '../components/UI/ModernIcon';

<ModernIcon name="sparkles" size="lg" color="primary" />
```

## Customization

### Adding New Icons

1. Add the icon to the `iconMap` in `ModernIcon.js`
2. Import the icon from `@heroicons/react/24/outline`
3. Add a descriptive name for the icon

### Custom Effects

Create new CSS animations and add them to the effect classes:

```css
@keyframes customEffect {
  /* Animation keyframes */
}

.icon-custom-effect {
  animation: customEffect 2s ease-in-out infinite;
}
```

### Custom Colors

Add new color variants to the CSS:

```css
.icon-custom-color {
  color: #your-color;
  fill: currentColor;
}
```

## Best Practices

1. **Consistency**: Use the same size and color for similar actions
2. **Accessibility**: Always provide text alternatives for icon-only buttons
3. **Performance**: Use appropriate sizes for the context
4. **Semantics**: Choose icons that clearly represent their function
5. **Feedback**: Use effects sparingly to avoid overwhelming users

## Troubleshooting

### Icon Not Displaying
- Check if the icon name exists in `iconMap`
- Verify the import from `@heroicons/react/24/outline`
- Check console for warnings about missing icons

### Styling Issues
- Ensure CSS classes are properly loaded
- Check for conflicting styles
- Verify responsive breakpoints

### Performance Issues
- Reduce the number of animated icons
- Use appropriate sizes for mobile devices
- Consider lazy loading for large icon sets

## Contributing

When adding new features to the icon system:

1. Update the documentation
2. Add examples to `IconShowcase.js`
3. Test across different browsers and devices
4. Ensure accessibility compliance
5. Update the migration guide if needed
