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
    renderRiskCard
  };
}
