// Navigation bar rendering and active page highlighting

/**
 * Navigation items configuration
 */
const NAV_ITEMS = [
  { label: '首页', href: 'index.html', id: 'home' },
  { label: '方向地图', href: 'direction-map.html', id: 'direction-map' },
  { label: '产品线观察', href: 'product-line.html', id: 'product-line' },
  { label: '证据库', href: 'evidence.html', id: 'evidence' }
];

/**
 * Render the navigation bar
 * @param {string} activePage - ID of the active page
 * @returns {string} HTML string for navigation bar
 */
function renderNavigationBar(activePage = 'home') {
  const navLinks = NAV_ITEMS.map(item => {
    const activeClass = item.id === activePage ? ' active' : '';
    return `<li><a href="${item.href}" class="nav-link${activeClass}">${item.label}</a></li>`;
  }).join('');
  
  return `
    <nav class="nav-bar">
      <a href="index.html" class="nav-brand">翡翠信号图谱</a>
      <ul class="nav-links">
        ${navLinks}
      </ul>
    </nav>
  `;
}

/**
 * Initialize navigation bar on page load
 * This function should be called with the current page ID
 * @param {string} activePage - ID of the active page
 */
function initNavigation(activePage = 'home') {
  // Check if we're in a browser environment
  if (typeof document === 'undefined') {
    return;
  }
  
  // Try to find a nav container element
  const navContainer = document.getElementById('nav-container');
  
  if (navContainer) {
    navContainer.innerHTML = renderNavigationBar(activePage);
  } else {
    console.warn('Nav container element with id "nav-container" not found. Navigation bar not rendered.');
  }
}

/**
 * Auto-detect active page from current URL
 * @returns {string} Page ID based on current URL
 */
function detectActivePage() {
  if (typeof window === 'undefined') {
    return 'home';
  }
  
  const pathname = window.location.pathname;
  const filename = pathname.split('/').pop() || 'index.html';
  
  // Map filenames to page IDs
  const pageMap = {
    'index.html': 'home',
    'direction-map.html': 'direction-map',
    'direction-detail.html': 'direction-map', // Detail pages highlight the map
    'product-line.html': 'product-line',
    'evidence.html': 'evidence'
  };
  
  return pageMap[filename] || 'home';
}

/**
 * Initialize navigation with auto-detection
 * Call this in your page's DOMContentLoaded event
 */
function autoInitNavigation() {
  const activePage = detectActivePage();
  initNavigation(activePage);
}

// Auto-initialize if in browser environment and DOM is ready
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInitNavigation);
  } else {
    // DOM already loaded
    autoInitNavigation();
  }
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    NAV_ITEMS,
    renderNavigationBar,
    initNavigation,
    detectActivePage,
    autoInitNavigation
  };
}
