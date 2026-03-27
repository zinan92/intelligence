// Data loading and access utilities for Jade Signal Atlas Dashboard

// Configurable data source path
// Default: frontend_dashboard.json (pipeline-generated with real streetwear data)
// Alternative: jade_dashboard.json (hand-crafted jade data for backward compatibility)
// Can also be overridden via URL parameter: ?data=jade_dashboard.json
const DEFAULT_DATA_PATH = '/data/frontend_dashboard.json';

/**
 * Get the data file path from URL parameter or default
 * @returns {string} Data file path
 */
function getDataPath() {
  const urlParams = new URLSearchParams(window.location.search);
  const dataParam = urlParams.get('data');
  
  if (dataParam) {
    // If data parameter is provided, use it (with /data/ prefix if not absolute)
    return dataParam.startsWith('/') ? dataParam : `/data/${dataParam}`;
  }
  
  return DEFAULT_DATA_PATH;
}

/**
 * Load the dashboard data from JSON file
 * @returns {Promise<Object>} Dashboard data object
 */
async function loadDashboardData() {
  try {
    const dataPath = getDataPath();
    const response = await fetch(dataPath);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to load dashboard data:', error);
    throw error;
  }
}

/**
 * Get all trend directions
 * @param {Object} data - Dashboard data
 * @returns {Array} Array of trend direction objects
 */
function getTrendDirections(data) {
  return data.trend_directions || [];
}

/**
 * Get a specific trend direction by ID
 * @param {Object} data - Dashboard data
 * @param {string} directionId - Direction ID
 * @returns {Object|null} Direction object or null if not found
 */
function getDirectionById(data, directionId) {
  const directions = getTrendDirections(data);
  return directions.find(d => d.id === directionId) || null;
}

/**
 * Get trend directions by judgment state
 * @param {Object} data - Dashboard data
 * @param {string} judgmentState - Judgment state (值得跟, 观察中, 短热噪音, 需要补证据)
 * @returns {Array} Filtered array of trend directions
 */
function getDirectionsByJudgment(data, judgmentState) {
  const directions = getTrendDirections(data);
  return directions.filter(d => d.judgment_state === judgmentState);
}

/**
 * Get all product lines
 * @param {Object} data - Dashboard data
 * @returns {Array} Array of product line objects
 */
function getProductLines(data) {
  return data.product_lines || [];
}

/**
 * Get a specific product line by ID
 * @param {Object} data - Dashboard data
 * @param {string} lineId - Product line ID
 * @returns {Object|null} Product line object or null if not found
 */
function getProductLineById(data, lineId) {
  const lines = getProductLines(data);
  return lines.find(l => l.id === lineId) || null;
}

/**
 * Get all evidence entries
 * @param {Object} data - Dashboard data
 * @returns {Array} Array of evidence entry objects
 */
function getEvidenceEntries(data) {
  return data.evidence_entries || [];
}

/**
 * Get evidence entries by direction
 * @param {Object} data - Dashboard data
 * @param {string} directionName - Direction name
 * @returns {Array} Filtered array of evidence entries
 */
function getEvidenceByDirection(data, directionName) {
  const entries = getEvidenceEntries(data);
  return entries.filter(e => e.related_direction === directionName);
}

/**
 * Get evidence entries by type
 * @param {Object} data - Dashboard data
 * @param {string} type - Evidence type (笔记, 图片, 评论)
 * @returns {Array} Filtered array of evidence entries
 */
function getEvidenceByType(data, type) {
  const entries = getEvidenceEntries(data);
  return entries.filter(e => e.type === type);
}

/**
 * Get today's judgment summary
 * @param {Object} data - Dashboard data
 * @returns {Object} Judgment counts object
 */
function getTodayJudgments(data) {
  return data.today_judgments || {};
}

/**
 * Get 14-day change data
 * @param {Object} data - Dashboard data
 * @returns {Object} 14-day change object with rising, cooling, newly_emerging arrays
 */
function getFourteenDayChanges(data) {
  return data.fourteen_day_changes || { rising: [], cooling: [], newly_emerging: [] };
}

/**
 * Get executive summary
 * @param {Object} data - Dashboard data
 * @returns {Object} Executive summary object
 */
function getExecutiveSummary(data) {
  return data.executive_summary || {};
}

/**
 * Sort directions by heat magnitude (descending)
 * @param {Array} directions - Array of direction objects
 * @returns {Array} Sorted array
 */
function sortByHeat(directions) {
  return [...directions].sort((a, b) => {
    const heatA = parseFloat(a.heat_magnitude.replace('%', ''));
    const heatB = parseFloat(b.heat_magnitude.replace('%', ''));
    return heatB - heatA;
  });
}

/**
 * Sort directions by confidence level (descending: 高 > 中高 > 中 > 低)
 * @param {Array} directions - Array of direction objects
 * @returns {Array} Sorted array
 */
function sortByConfidence(directions) {
  const confidenceOrder = { '高': 4, '中高': 3, '中': 2, '低': 1 };
  return [...directions].sort((a, b) => {
    return (confidenceOrder[b.confidence_level] || 0) - (confidenceOrder[a.confidence_level] || 0);
  });
}

/**
 * Filter directions by classification
 * @param {Array} directions - Array of direction objects
 * @param {string} classification - Classification type
 * @returns {Array} Filtered array
 */
function filterByClassification(directions, classification) {
  return directions.filter(d => d.classification === classification);
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    loadDashboardData,
    getTrendDirections,
    getDirectionById,
    getDirectionsByJudgment,
    getProductLines,
    getProductLineById,
    getEvidenceEntries,
    getEvidenceByDirection,
    getEvidenceByType,
    getTodayJudgments,
    getFourteenDayChanges,
    getExecutiveSummary,
    sortByHeat,
    sortByConfidence,
    filterByClassification
  };
}
