// Reusable UI component rendering functions for Jade Signal Atlas Dashboard

/**
 * Render a judgment state badge
 * @param {string} judgmentState - Judgment state (值得跟, 观察中, 短热噪音, 需要补证据)
 * @returns {string} HTML string for badge
 */
function renderJudgmentBadge(judgmentState) {
  const badgeClassMap = {
    '值得跟': 'badge-zhidegeng',
    '观察中': 'badge-guanchazu',
    '短热噪音': 'badge-duanrezaoyin',
    '需要补证据': 'badge-xuyaobuzhengju'
  };
  
  const badgeClass = badgeClassMap[judgmentState] || 'badge-xuyaobuzhengju';
  return `<span class="badge ${badgeClass}">${judgmentState}</span>`;
}

/**
 * Render a confidence level badge
 * @param {string} confidence - Confidence level (高, 中高, 中, 低)
 * @returns {string} HTML string for badge
 */
function renderConfidenceBadge(confidence) {
  const badgeClassMap = {
    '高': 'badge-success',
    '中高': 'badge-info',
    '中': 'badge-warning',
    '低': 'badge-danger'
  };
  
  const badgeClass = badgeClassMap[confidence] || 'badge-warning';
  return `<span class="badge ${badgeClass}">信心: ${confidence}</span>`;
}

/**
 * Render a heat indicator with positive/negative styling
 * @param {string} heatMagnitude - Heat magnitude (e.g., "+32%", "-15%")
 * @returns {string} HTML string for heat indicator
 */
function renderHeatIndicator(heatMagnitude) {
  const isPositive = heatMagnitude.startsWith('+');
  const isNegative = heatMagnitude.startsWith('-');
  const heatClass = isPositive ? 'heat-positive' : (isNegative ? 'heat-negative' : 'heat-neutral');
  const arrow = isPositive ? '↑' : (isNegative ? '↓' : '');
  
  return `<span class="heat-indicator ${heatClass}">${arrow} ${heatMagnitude}</span>`;
}

/**
 * Render a freshness indicator
 * @param {string} freshness - Freshness text (e.g., "最近7天", "最近30天")
 * @returns {string} HTML string for freshness indicator
 */
function renderFreshnessIndicator(freshness) {
  return `<span class="freshness">🕐 ${freshness}</span>`;
}

/**
 * Render a product line chip
 * @param {string} productLineName - Product line name
 * @param {string} status - Optional status text
 * @returns {string} HTML string for product chip
 */
function renderProductChip(productLineName, status = '') {
  const statusText = status ? ` (${status})` : '';
  return `<span class="product-chip">${productLineName}${statusText}</span>`;
}

/**
 * Render opportunity/risk level indicator
 * @param {string} level - Level (高, 中高, 中, 低中, 低)
 * @param {string} type - Type ('opportunity' or 'risk')
 * @returns {string} HTML string
 */
function renderOpportunityRiskLevel(level, type = 'opportunity') {
  const label = type === 'opportunity' ? '机会' : '风险';
  const levelClassMap = {
    '高': 'badge-success',
    '中高': 'badge-info',
    '中': 'badge-warning',
    '低中': 'badge-warning',
    '低': 'badge-danger'
  };
  
  const badgeClass = levelClassMap[level] || 'badge-warning';
  return `<span class="badge ${badgeClass}">${label}: ${level}</span>`;
}

/**
 * Render a direction card
 * @param {Object} direction - Direction object
 * @param {boolean} compact - Whether to use compact layout
 * @returns {string} HTML string for direction card
 */
function renderDirectionCard(direction, compact = false) {
  if (compact) {
    return `
      <div class="card" data-direction-id="${direction.id}">
        <div class="card-header">
          <h3 class="card-title">${direction.name}</h3>
          <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
            ${renderJudgmentBadge(direction.judgment_state)}
            ${renderHeatIndicator(direction.heat_magnitude)}
          </div>
        </div>
        <div class="card-body">
          <p class="text-sm text-secondary">${direction.description}</p>
        </div>
      </div>
    `;
  }
  
  return `
    <div class="card" data-direction-id="${direction.id}">
      <div class="card-header">
        <h3 class="card-title">${direction.name}</h3>
        <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
          ${renderJudgmentBadge(direction.judgment_state)}
          ${renderConfidenceBadge(direction.confidence_level)}
          ${renderHeatIndicator(direction.heat_magnitude)}
          ${renderFreshnessIndicator(direction.freshness)}
        </div>
      </div>
      <div class="card-body">
        <p class="mb-md">${direction.description}</p>
        <div class="mb-sm">
          <strong class="text-primary">受众适配:</strong>
          <span class="text-secondary">${direction.audience_fit}</span>
        </div>
        <div class="mb-sm">
          <strong class="text-primary">价格带:</strong>
          <span class="text-secondary">${direction.price_band_fit}</span>
        </div>
        <div class="mb-sm">
          <strong class="text-primary">一句话建议:</strong>
          <span class="text-secondary">${direction.one_line_recommendation}</span>
        </div>
      </div>
      <div class="card-footer">
        <a href="direction-detail.html?id=${direction.id}" class="text-sm">查看详情 →</a>
      </div>
    </div>
  `;
}

/**
 * Render a product line card
 * @param {Object} productLine - Product line object
 * @returns {string} HTML string for product line card
 */
function renderProductLineCard(productLine) {
  return `
    <div class="card" data-line-id="${productLine.id}">
      <div class="card-header">
        <h3 class="card-title">${productLine.name}</h3>
        <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
          ${renderOpportunityRiskLevel(productLine.opportunity_level, 'opportunity')}
          ${renderOpportunityRiskLevel(productLine.risk_level, 'risk')}
        </div>
      </div>
      <div class="card-body">
        <div class="mb-md">
          <strong class="text-primary">状态:</strong>
          <span class="text-secondary">${productLine.movement_status}</span>
        </div>
        <p class="text-sm text-secondary">${productLine.reasoning}</p>
      </div>
      <div class="card-footer">
        <a href="product-line.html?id=${productLine.id}" class="text-sm">查看详情 →</a>
      </div>
    </div>
  `;
}

/**
 * Render an evidence card
 * @param {Object} evidence - Evidence entry object
 * @param {boolean} compact - Whether to use compact layout
 * @returns {string} HTML string for evidence card
 */
function renderEvidenceCard(evidence, compact = false) {
  const typeIconMap = {
    '笔记': '📝',
    '图片': '🖼️',
    '评论': '💬'
  };
  
  const typeIcon = typeIconMap[evidence.type] || '📄';
  
  if (compact) {
    return `
      <div class="card" data-evidence-id="${evidence.id}">
        <div class="card-header">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>${typeIcon}</span>
            <h4 class="card-title text-base">${evidence.title}</h4>
          </div>
          <div style="margin-top: 0.25rem;">
            ${renderFreshnessIndicator(evidence.freshness)}
          </div>
        </div>
        <div class="card-body">
          <p class="text-sm text-secondary">相关方向: ${evidence.related_direction}</p>
        </div>
      </div>
    `;
  }
  
  return `
    <div class="card" data-evidence-id="${evidence.id}">
      <div class="card-header">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span>${typeIcon}</span>
          <h4 class="card-title text-base">${evidence.title}</h4>
        </div>
        <div class="card-subtitle">${evidence.source}</div>
        <div style="margin-top: 0.5rem;">
          ${renderFreshnessIndicator(evidence.freshness)}
        </div>
      </div>
      <div class="card-body">
        <div class="mb-sm">
          <strong class="text-primary">相关方向:</strong>
          <span class="text-secondary">${evidence.related_direction}</span>
        </div>
        <div class="mb-sm">
          <strong class="text-primary">产品线:</strong>
          <span class="text-secondary">${evidence.product_line}</span>
        </div>
        <p class="text-sm text-secondary">${evidence.relevance_explanation}</p>
      </div>
    </div>
  `;
}

/**
 * Render a risk warning card
 * @param {Object} risk - Risk object
 * @returns {string} HTML string for risk card
 */
function renderRiskCard(risk) {
  const severityBadgeMap = {
    'high': 'badge-danger',
    'medium': 'badge-warning',
    'low': 'badge-info'
  };
  
  const severityLabelMap = {
    'high': '高',
    'medium': '中',
    'low': '低'
  };
  
  const badgeClass = severityBadgeMap[risk.severity] || 'badge-warning';
  const severityLabel = severityLabelMap[risk.severity] || '中';
  
  return `
    <div class="card">
      <div class="card-header">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span>⚠️</span>
          <h4 class="card-title text-base">${risk.description}</h4>
        </div>
        <div style="margin-top: 0.5rem;">
          <span class="badge ${badgeClass}">严重度: ${severityLabel}</span>
        </div>
      </div>
      ${risk.mitigation ? `
        <div class="card-body">
          <strong class="text-primary">缓解措施:</strong>
          <span class="text-secondary">${risk.mitigation}</span>
        </div>
      ` : ''}
    </div>
  `;
}

/**
 * Render an area chart from movement history data
 * @param {Array<number>} data - Array of numeric values (typically 14 data points for movement_history)
 * @param {Object} options - Configuration options
 * @param {number} options.width - Width of SVG in pixels (default: 400)
 * @param {number} options.height - Height of SVG in pixels (default: 180)
 * @param {string} options.fillColor - Fill color for area (default: '#10b981')
 * @param {string} options.strokeColor - Stroke color for line (default: '#059669')
 * @param {boolean} options.showDots - Whether to show data point dots (default: false)
 * @param {boolean} options.showLabels - Whether to show axis labels (default: false)
 * @param {boolean} options.showGradient - Whether to use gradient fill (default: true)
 * @param {string} options.className - CSS class for container (default: '')
 * @returns {string} SVG element as HTML string
 */
function renderAreaChart(data, options = {}) {
  // Validate input
  if (!data || !Array.isArray(data) || data.length < 2) {
    return '<span class="text-sm text-muted">数据不足</span>';
  }
  
  // Default options
  const {
    width = 400,
    height = 180,
    fillColor = '#10b981',
    strokeColor = '#059669',
    showDots = false,
    showLabels = false,
    showGradient = true,
    className = ''
  } = options;
  
  // Calculate padding for labels
  const paddingTop = showLabels ? 20 : 10;
  const paddingBottom = showLabels ? 30 : 10;
  const paddingLeft = showLabels ? 40 : 10;
  const paddingRight = 10;
  
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;
  
  // Find min and max values
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  
  // Generate points for the area path
  const points = data.map((value, index) => {
    const x = paddingLeft + (index / (data.length - 1)) * chartWidth;
    const y = paddingTop + chartHeight - ((value - min) / range) * chartHeight;
    return { x, y, value };
  });
  
  // Create SVG path for area
  const areaPath = [
    `M ${points[0].x} ${height - paddingBottom}`, // Start at bottom-left
    ...points.map(p => `L ${p.x} ${p.y}`), // Line to each data point
    `L ${points[points.length - 1].x} ${height - paddingBottom}`, // Line down to bottom-right
    'Z' // Close path
  ].join(' ');
  
  // Create SVG path for line
  const linePath = points.map((p, i) => 
    i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`
  ).join(' ');
  
  // Generate unique ID for gradient
  const gradientId = `gradient-${Math.random().toString(36).substr(2, 9)}`;
  
  // Generate dots HTML if enabled
  const dotsHtml = showDots ? points.map(p => 
    `<circle cx="${p.x}" cy="${p.y}" r="3" fill="${strokeColor}" />`
  ).join('\n') : '';
  
  // Generate labels HTML if enabled
  let labelsHtml = '';
  if (showLabels) {
    // X-axis labels (first and last day)
    labelsHtml += `
      <text x="${paddingLeft}" y="${height - 5}" font-size="12" fill="#6a7178" text-anchor="start">第1天</text>
      <text x="${width - paddingRight}" y="${height - 5}" font-size="12" fill="#6a7178" text-anchor="end">第${data.length}天</text>
    `;
    
    // Y-axis labels (min and max)
    labelsHtml += `
      <text x="${paddingLeft - 5}" y="${paddingTop + 5}" font-size="12" fill="#6a7178" text-anchor="end">${max}</text>
      <text x="${paddingLeft - 5}" y="${height - paddingBottom}" font-size="12" fill="#6a7178" text-anchor="end">${min}</text>
    `;
  }
  
  return `
    <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" class="${className}" style="display: block;">
      <defs>
        ${showGradient ? `
          <linearGradient id="${gradientId}" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:${fillColor};stop-opacity:0.6" />
            <stop offset="100%" style="stop-color:${fillColor};stop-opacity:0.05" />
          </linearGradient>
        ` : ''}
      </defs>
      
      <!-- Area fill -->
      <path
        d="${areaPath}"
        fill="${showGradient ? `url(#${gradientId})` : fillColor}"
        opacity="${showGradient ? '1' : '0.2'}"
      />
      
      <!-- Line stroke -->
      <path
        d="${linePath}"
        fill="none"
        stroke="${strokeColor}"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      
      <!-- Data point dots -->
      ${dotsHtml}
      
      <!-- Axis labels -->
      ${labelsHtml}
    </svg>
  `;
}

/**
 * Helper function to get judgment state color for charts
 * @param {string} judgmentState - Judgment state
 * @returns {Object} Object with fillColor and strokeColor
 */
function getJudgmentColors(judgmentState) {
  const colorMap = {
    '值得跟': { fillColor: '#10b981', strokeColor: '#059669' },
    '观察中': { fillColor: '#3b82f6', strokeColor: '#2563eb' },
    '短热噪音': { fillColor: '#f59e0b', strokeColor: '#d97706' },
    '需要补证据': { fillColor: '#6b7280', strokeColor: '#4b5563' }
  };
  
  return colorMap[judgmentState] || colorMap['需要补证据'];
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    renderJudgmentBadge,
    renderConfidenceBadge,
    renderHeatIndicator,
    renderFreshnessIndicator,
    renderProductChip,
    renderOpportunityRiskLevel,
    renderDirectionCard,
    renderProductLineCard,
    renderEvidenceCard,
    renderRiskCard,
    renderAreaChart,
    getJudgmentColors
  };
}
