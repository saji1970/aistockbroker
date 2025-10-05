import React from 'react';
import ModernIcon, { IconButton, IconGroup, IconShape } from './ModernIcon';

const IconShowcase = () => {
  const navigationIcons = [
    'home', 'dashboard', 'settings', 'user', 'users', 'admin', 'logout'
  ];

  const featureIcons = [
    'sparkles', 'ai', 'portfolio', 'trading', 'backtest', 'lightbulb', 'money', 'trending'
  ];

  const actionIcons = [
    'eye', 'eye-slash', 'menu', 'close', 'send', 'chat', 'search', 'clock'
  ];

  const statusIcons = [
    'success', 'error', 'warning', 'info'
  ];

  const iconGroup = [
    { name: 'home', color: 'primary' },
    { name: 'sparkles', color: 'secondary' },
    { name: 'success', color: 'success' },
    { name: 'warning', color: 'warning' }
  ];

  return (
    <div className="container-modern section-padding">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gradient mb-4">Modern Icon System</h1>
        <p className="text-gray-600 text-lg">Beautiful, customizable icons with modern effects</p>
      </div>

      {/* Basic Icons */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-8 text-gray-900">Basic Icons</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-6">
          {navigationIcons.map(icon => (
            <div key={icon} className="text-center">
              <div className="icon-container icon-container-md icon-container-primary mb-2">
                <ModernIcon name={icon} size="lg" color="primary" />
              </div>
              <p className="text-sm text-gray-600 capitalize">{icon}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Icons */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-8 text-gray-900">Feature Icons</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-6">
          {featureIcons.map(icon => (
            <div key={icon} className="text-center">
              <div className="icon-container icon-container-md icon-container-secondary mb-2">
                <ModernIcon name={icon} size="lg" color="secondary" />
              </div>
              <p className="text-sm text-gray-600 capitalize">{icon}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Action Icons */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-8 text-gray-900">Action Icons</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-6">
          {actionIcons.map(icon => (
            <div key={icon} className="text-center">
              <div className="icon-container icon-container-md icon-container-success mb-2">
                <ModernIcon name={icon} size="lg" color="success" />
              </div>
              <p className="text-sm text-gray-600 capitalize">{icon}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Status Icons */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-8 text-gray-900">Status Icons</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {statusIcons.map(icon => (
            <div key={icon} className="text-center">
              <div className="icon-container icon-container-md icon-container-warning mb-2">
                <ModernIcon name={icon} size="lg" color="warning" />
              </div>
              <p className="text-sm text-gray-600 capitalize">{icon}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Icon Sizes */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-8 text-gray-900">Icon Sizes</h2>
        <div className="flex items-center gap-8">
          <div className="text-center">
            <ModernIcon name="sparkles" size="sm" color="primary" container />
            <p className="text-sm text-gray-600 mt-2">Small</p>
          </div>
          <div className="text-center">
            <ModernIcon name="sparkles" size="md" color="primary" container />
            <p className="text-sm text-gray-600 mt-2">Medium</p>
          </div>
          <div className="text-center">
            <ModernIcon name="sparkles" size="lg" color="primary" container />
            <p className="text-sm text-gray-600 mt-2">Large</p>
          </div>
          <div className="text-center">
            <ModernIcon name="sparkles" size="xl" color="primary" container />
            <p className="text-sm text-gray-600 mt-2">Extra Large</p>
          </div>
        </div>
      </section>

      {/* Icon Effects */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-8 text-gray-900">Icon Effects</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
          <div className="text-center">
            <ModernIcon name="sparkles" size="lg" color="primary" effect="glow" />
            <p className="text-sm text-gray-600 mt-2">Glow</p>
          </div>
          <div className="text-center">
            <ModernIcon name="sparkles" size="lg" color="secondary" effect="pulse" />
            <p className="text-sm text-gray-600 mt-2">Pulse</p>
          </div>
          <div className="text-center">
            <ModernIcon name="sparkles" size="lg" color="success" effect="float" />
            <p className="text-sm text-gray-600 mt-2">Float</p>
          </div>
          <div className="text-center">
            <ModernIcon name="sparkles" size="lg" color="warning" effect="rotate" />
            <p className="text-sm text-gray-600 mt-2">Rotate</p>
          </div>
          <div className="text-center">
            <ModernIcon name="sparkles" size="lg" color="danger" effect="bounce" />
            <p className="text-sm text-gray-600 mt-2">Bounce</p>
          </div>
        </div>
      </section>

      {/* Icon Buttons */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-8 text-gray-900">Icon Buttons</h2>
        <div className="flex flex-wrap gap-4">
          <IconButton icon="home" variant="primary" />
          <IconButton icon="sparkles" variant="secondary" />
          <IconButton icon="success" variant="success" />
          <IconButton icon="error" variant="danger" />
        </div>
      </section>

      {/* Icon Groups */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-8 text-gray-900">Icon Groups</h2>
        <div className="space-y-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">Horizontal Group</h3>
            <IconGroup icons={iconGroup} direction="horizontal" />
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Vertical Group</h3>
            <IconGroup icons={iconGroup} direction="vertical" />
          </div>
        </div>
      </section>

      {/* Icon Shapes */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-8 text-gray-900">Icon Shapes</h2>
        <div className="flex items-center gap-8">
          <div className="text-center">
            <IconShape shape="circle" size="lg" color="primary">
              <ModernIcon name="sparkles" size="md" color="white" />
            </IconShape>
            <p className="text-sm text-gray-600 mt-2">Circle</p>
          </div>
          <div className="text-center">
            <IconShape shape="square" size="lg" color="secondary">
              <ModernIcon name="ai" size="md" color="white" />
            </IconShape>
            <p className="text-sm text-gray-600 mt-2">Square</p>
          </div>
          <div className="text-center">
            <IconShape shape="rounded" size="lg" color="success">
              <ModernIcon name="portfolio" size="md" color="white" />
            </IconShape>
            <p className="text-sm text-gray-600 mt-2">Rounded</p>
          </div>
        </div>
      </section>

      {/* Badge Icons */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-8 text-gray-900">Badge Icons</h2>
        <div className="flex items-center gap-8">
          <div className="text-center">
            <ModernIcon 
              name="chat" 
              size="lg" 
              color="primary" 
              badge 
              container 
            />
            <p className="text-sm text-gray-600 mt-2">Badge</p>
          </div>
          <div className="text-center">
            <ModernIcon 
              name="chat" 
              size="lg" 
              color="secondary" 
              badge 
              badgeCount="5"
              container 
            />
            <p className="text-sm text-gray-600 mt-2">Notification (5)</p>
          </div>
          <div className="text-center">
            <ModernIcon 
              name="chat" 
              size="lg" 
              color="danger" 
              badge 
              badgeCount="99+"
              container 
            />
            <p className="text-sm text-gray-600 mt-2">High Count (99+)</p>
          </div>
        </div>
      </section>

      {/* Usage Examples */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-8 text-gray-900">Usage Examples</h2>
        <div className="bg-gray-50 rounded-xl p-6">
          <pre className="text-sm text-gray-700 overflow-x-auto">
{`// Basic Icon
<ModernIcon name="sparkles" size="lg" color="primary" />

// Icon with Container
<ModernIcon name="ai" size="md" color="secondary" container />

// Icon with Effect
<ModernIcon name="portfolio" size="lg" color="success" effect="pulse" />

// Icon Button
<IconButton icon="home" variant="primary" onClick={handleClick} />

// Icon Group
<IconGroup 
  icons={[
    { name: 'home', color: 'primary' },
    { name: 'sparkles', color: 'secondary' }
  ]} 
  direction="horizontal" 
/>

// Icon Shape
<IconShape shape="circle" size="lg" color="primary">
  <ModernIcon name="sparkles" size="md" color="white" />
</IconShape>

// Badge Icon
<ModernIcon 
  name="chat" 
  size="lg" 
  color="primary" 
  badge 
  badgeCount="5" 
  container 
/>`}
          </pre>
        </div>
      </section>
    </div>
  );
};

export default IconShowcase;
