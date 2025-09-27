import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

const ScrollToTop = () => {
  const { pathname } = useLocation();
  const scrollPosition = useRef(0);

  useEffect(() => {
    // Store current scroll position before route change
    scrollPosition.current = window.scrollY;

    // Prevent automatic scrolling on route changes
    const preventScroll = () => {
      if (window.location.hash) {
        // If there's a hash in the URL, scroll to that element
        const element = document.querySelector(window.location.hash);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      } else {
        // For regular navigation, maintain current scroll position
        // Force scroll position to remain where it was
        window.scrollTo(0, scrollPosition.current);
      }
    };

    // Immediate scroll prevention
    preventScroll();

    // Additional scroll prevention after a short delay
    const timeoutId = setTimeout(() => {
      window.scrollTo(0, scrollPosition.current);
    }, 50);

    // Prevent scroll on popstate events
    const handlePopState = () => {
      window.scrollTo(0, scrollPosition.current);
    };

    window.addEventListener('popstate', handlePopState);

    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('popstate', handlePopState);
    };
  }, [pathname]);

  return null;
};

export default ScrollToTop;
