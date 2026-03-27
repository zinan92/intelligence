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

/**
 * Render a grouped horizontal bar chart comparing product lines by opportunity and risk
 * @param {Array<Object>} productLines - Array of product line objects with opportunity_level and risk_level
 * @param {Object} options - Configuration options
 * @param {number} options.width - Width of SVG in pixels (default: 1000)
 * @param {number} options.height - Height of SVG in pixels (default: 400)
 * @returns {string} SVG element as HTML string
 */
function renderProductLineComparisonChart(productLines, options = {}) {
  // Validate input
  if (!productLines || !Array.isArray(productLines) || productLines.length === 0) {
    return '<div class="text-center text-muted" style="padding: 2rem;">暂无产品线数据</div>';
  }
  
  // Default options
  const { width = 1000, height = 400 } = options;
  
  // Map level strings to numeric values
  const levelMap = {
    '高': 90,
    '中高': 70,
    '中': 50,
    '低中': 30,
    '低': 30
  };
  
  // Process data
  const data = productLines.map(line => ({
    name: line.name,
    opportunity: levelMap[line.opportunity_level] || 50,
    risk: levelMap[line.risk_level] || 50
  }));
  
  // Chart dimensions
  const paddingTop = 60;
  const paddingBottom = 40;
  const paddingLeft = 120;
  const paddingRight = 100;
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;
  
  // Calculate bar dimensions
  const barGroupHeight = chartHeight / data.length;
  const barHeight = (barGroupHeight * 0.7) / 2; // Two bars per group, with 30% spacing
  const barSpacing = barGroupHeight * 0.05;
  
  // Colors
  const opportunityColor = '#10b981'; // Green/teal
  const riskColor = '#ef4444'; // Red/orange
  
  // Scale for X axis (0-100)
  const maxValue = 100;
  const scale = chartWidth / maxValue;
  
  // Generate bars
  const barsHtml = data.map((item, index) => {
    const groupY = paddingTop + index * barGroupHeight;
    const opportunityBarY = groupY + (barGroupHeight - barHeight * 2 - barSpacing) / 2;
    const riskBarY = opportunityBarY + barHeight + barSpacing;
    
    const opportunityWidth = item.opportunity * scale;
    const riskWidth = item.risk * scale;
    
    return `
      <!-- Product line: ${item.name} -->
      <!-- Opportunity bar -->
      <rect
        x="${paddingLeft}"
        y="${opportunityBarY}"
        width="${opportunityWidth}"
        height="${barHeight}"
        fill="${opportunityColor}"
        opacity="0.8"
      />
      <text
        x="${paddingLeft + opportunityWidth + 5}"
        y="${opportunityBarY + barHeight / 2}"
        font-size="14"
        fill="#1a1d21"
        alignment-baseline="middle"
      >${item.opportunity}</text>
      
      <!-- Risk bar -->
      <rect
        x="${paddingLeft}"
        y="${riskBarY}"
        width="${riskWidth}"
        height="${barHeight}"
        fill="${riskColor}"
        opacity="0.8"
      />
      <text
        x="${paddingLeft + riskWidth + 5}"
        y="${riskBarY + barHeight / 2}"
        font-size="14"
        fill="#1a1d21"
        alignment-baseline="middle"
      >${item.risk}</text>
      
      <!-- Product line label (Y-axis) -->
      <text
        x="${paddingLeft - 10}"
        y="${groupY + barGroupHeight / 2}"
        font-size="16"
        font-weight="600"
        fill="#1a1d21"
        text-anchor="end"
        alignment-baseline="middle"
      >${item.name}</text>
    `;
  }).join('\n');
  
  // Generate X-axis
  const xAxisTicks = [0, 25, 50, 75, 100];
  const xAxisHtml = xAxisTicks.map(tick => {
    const x = paddingLeft + tick * scale;
    return `
      <line
        x1="${x}"
        y1="${paddingTop}"
        x2="${x}"
        y2="${paddingTop + chartHeight}"
        stroke="#e5e7eb"
        stroke-width="1"
      />
      <text
        x="${x}"
        y="${paddingTop + chartHeight + 20}"
        font-size="12"
        fill="#6a7178"
        text-anchor="middle"
      >${tick}</text>
    `;
  }).join('\n');
  
  return `
    <div style="width: 100%; overflow-x: auto;">
      <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" style="display: block; max-width: 100%;">
        <!-- Title -->
        <text
          x="${width / 2}"
          y="30"
          font-size="20"
          font-weight="600"
          fill="#1a1d21"
          text-anchor="middle"
        >产品线机会与风险对比</text>
        
        <!-- X-axis -->
        ${xAxisHtml}
        
        <!-- Bars -->
        ${barsHtml}
        
        <!-- Legend -->
        <g transform="translate(${width - paddingRight + 10}, ${paddingTop})">
          <!-- Opportunity legend -->
          <rect x="0" y="0" width="20" height="12" fill="${opportunityColor}" opacity="0.8" />
          <text x="25" y="10" font-size="14" fill="#1a1d21">机会</text>
          
          <!-- Risk legend -->
          <rect x="0" y="25" width="20" height="12" fill="${riskColor}" opacity="0.8" />
          <text x="25" y="35" font-size="14" fill="#1a1d21">风险</text>
        </g>
      </svg>
    </div>
  `;
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
    getJudgmentColors,
    renderProductLineComparisonChart
  };
}
