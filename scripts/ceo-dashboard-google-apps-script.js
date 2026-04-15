/**
 * RivalEdge CEO Dashboard - Google Apps Script
 * 
 * This script creates a private CEO dashboard accessible only from your Google account.
 * Deploy as a web app with "Execute as: Me" and "Who has access: Only myself"
 */

// Configuration - Update these with your actual values
const CONFIG = {
  API_URL: 'https://rivaledge-production.up.railway.app',
  // You'll need to create an API key for this script
  API_KEY: 'YOUR_API_KEY_HERE'
};

/**
 * Main entry point - creates the HTML dashboard
 */
function doGet(e) {
  return HtmlService.createHtmlOutput(getDashboardHTML())
    .setTitle('RivalEdge CEO Dashboard')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Fetch dashboard data from backend
 */
function getDashboardData() {
  try {
    // Fetch from your backend API
    const response = UrlFetchApp.fetch(`${CONFIG.API_URL}/ceo/dashboard?days=30`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${CONFIG.API_KEY}`,
        'Content-Type': 'application/json'
      },
      muteHttpExceptions: true
    });
    
    if (response.getResponseCode() === 200) {
      return JSON.parse(response.getContentText());
    } else {
      return { error: `API Error: ${response.getResponseCode()}` };
    }
  } catch (error) {
    return { error: error.toString() };
  }
}

/**
 * Fetch sales agent data
 */
function getSalesAgentData() {
  try {
    const response = UrlFetchApp.fetch(`${CONFIG.API_URL}/api/admin/sales-agent/public-status`, {
      method: 'GET',
      muteHttpExceptions: true
    });
    
    if (response.getResponseCode() === 200) {
      return JSON.parse(response.getContentText());
    } else {
      return { error: `API Error: ${response.getResponseCode()}` };
    }
  } catch (error) {
    return { error: error.toString() };
  }
}

/**
 * Trigger sales agent run
 */
function triggerSalesAgent() {
  try {
    const response = UrlFetchApp.fetch(`${CONFIG.API_URL}/api/admin/sales-agent/trigger-cron-public?secret=rivaledge-test-2024&target_count=3`, {
      method: 'POST',
      muteHttpExceptions: true
    });
    
    return {
      success: response.getResponseCode() === 200,
      code: response.getResponseCode(),
      data: response.getContentText()
    };
  } catch (error) {
    return { success: false, error: error.toString() };
  }
}

/**
 * Generate the dashboard HTML
 */
function getDashboardHTML() {
  return `
<!DOCTYPE html>
<html>
<head>
  <base target="_top">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f5f5;
      padding: 20px;
    }
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      border-radius: 12px;
      margin-bottom: 30px;
    }
    .header h1 { font-size: 32px; margin-bottom: 8px; }
    .header p { opacity: 0.9; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    .card {
      background: white;
      padding: 24px;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .card h3 {
      font-size: 14px;
      color: #666;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }
    .card .value {
      font-size: 36px;
      font-weight: bold;
      color: #333;
    }
    .card .subtitle {
      font-size: 14px;
      color: #999;
      margin-top: 4px;
    }
    .section {
      background: white;
      padding: 24px;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      margin-bottom: 20px;
    }
    .section h2 {
      font-size: 20px;
      margin-bottom: 16px;
      color: #333;
    }
    .btn {
      background: #667eea;
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      margin-right: 10px;
    }
    .btn:hover { background: #5568d3; }
    .btn-secondary {
      background: #48bb78;
    }
    .btn-secondary:hover { background: #38a169; }
    .loading {
      text-align: center;
      padding: 40px;
      color: #666;
    }
    .error {
      background: #fed7d7;
      color: #c53030;
      padding: 16px;
      border-radius: 8px;
      margin: 20px 0;
    }
    .status-good { color: #48bb78; }
    .status-bad { color: #e53e3e; }
  </style>
</head>
<body>
  <div class="header">
    <h1>🎯 RivalEdge CEO Dashboard</h1>
    <p>Private access only • Last updated: <span id="lastUpdated">--</span></p>
  </div>

  <div id="loading" class="loading">Loading dashboard data...</div>
  <div id="error" class="error" style="display:none;"></div>
  
  <div id="dashboard" style="display:none;">
    <!-- Stats Grid -->
    <div class="grid">
      <div class="card">
        <h3>Total Users</h3>
        <div class="value" id="totalUsers">--</div>
        <div class="subtitle">Last 30 days</div>
      </div>
      <div class="card">
        <h3>Paying Customers</h3>
        <div class="value" id="payingCustomers">--</div>
        <div class="subtitle" id="conversionRate">--</div>
      </div>
      <div class="card">
        <h3>MRR</h3>
        <div class="value" id="mrr">--</div>
        <div class="subtitle" id="activeSubs">--</div>
      </div>
      <div class="card">
        <h3>Sales Agent</h3>
        <div class="value" id="salesAgentStatus">--</div>
        <div class="subtitle" id="todayCompanies">--</div>
      </div>
    </div>

    <!-- Sales Agent Section -->
    <div class="section">
      <h2>🤖 Sales Agent</h2>
      <p style="margin-bottom: 16px; color: #666;">
        Today's run: <span id="companiesProcessed">--</span> companies, 
        <span id="emailsSent">--</span> emails sent
      </p>
      <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
      <button class="btn btn-secondary" onclick="triggerAgent()">▶️ Run Sales Agent</button>
      <div id="agentResult" style="margin-top: 16px;"></div>
    </div>

    <!-- Quick Actions -->
    <div class="section">
      <h2>⚡ Quick Actions</h2>
      <button class="btn" onclick="window.open('https://rivaledge.ai/admin/buffer', '_blank')">
        📱 Buffer Dashboard
      </button>
      <button class="btn" onclick="window.open('https://app.instantly.ai', '_blank')">
        📧 Instantly Campaign
      </button>
      <button class="btn" onclick="window.open('https://tiriplcqvgsvjpzygsjh.supabase.co', '_blank')">
        🗄️ Supabase Database
      </button>
    </div>
  </div>

  <script>
    // Load data on page load
    google.script.run
      .withSuccessHandler(renderDashboard)
      .withFailureHandler(showError)
      .getDashboardData();
    
    google.script.run
      .withSuccessHandler(renderSalesAgent)
      .withFailureHandler(function() {})
      .getSalesAgentData();

    function renderDashboard(data) {
      document.getElementById('loading').style.display = 'none';
      document.getElementById('dashboard').style.display = 'block';
      document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
      
      if (data.error) {
        showError(data.error);
        return;
      }
      
      // Update stats
      if (data.registrations) {
        document.getElementById('totalUsers').textContent = data.registrations.total_registrations || 0;
        document.getElementById('payingCustomers').textContent = data.registrations.paying_customers || 0;
        document.getElementById('conversionRate').textContent = 
          (data.registrations.conversion_rate || 0) + '% conversion';
      }
      
      if (data.revenue_metrics) {
        document.getElementById('mrr').textContent = data.revenue_metrics.mrr_formatted || '$0';
        document.getElementById('activeSubs').textContent = 
          (data.revenue_metrics.active_subscriptions || 0) + ' active';
      }
      
      if (data.sales_agent) {
        document.getElementById('companiesProcessed').textContent = 
          data.sales_agent.today_stats?.companies || 0;
        document.getElementById('emailsSent').textContent = 
          data.sales_agent.today_stats?.emails_sent || 0;
      }
    }
    
    function renderSalesAgent(data) {
      const statusEl = document.getElementById('salesAgentStatus');
      const todayEl = document.getElementById('todayCompanies');
      
      if (data.status === 'active') {
        statusEl.innerHTML = '<span class="status-good">● Active</span>';
        todayEl.textContent = 'Daily at 9 AM';
      } else {
        statusEl.innerHTML = '<span class="status-bad">● Inactive</span>';
      }
    }
    
    function showError(error) {
      document.getElementById('loading').style.display = 'none';
      document.getElementById('error').style.display = 'block';
      document.getElementById('error').textContent = 'Error: ' + error;
    }
    
    function refreshData() {
      document.getElementById('loading').style.display = 'block';
      document.getElementById('dashboard').style.display = 'none';
      location.reload();
    }
    
    function triggerAgent() {
      const resultEl = document.getElementById('agentResult');
      resultEl.innerHTML = '<p style="color: #666;">Triggering sales agent...</p>';
      
      google.script.run
        .withSuccessHandler(function(result) {
          if (result.success) {
            resultEl.innerHTML = '<p style="color: #48bb78;">✅ Sales agent triggered! Refresh to see results.</p>';
          } else {
            resultEl.innerHTML = '<p style="color: #e53e3e;">❌ Failed: ' + (result.error || 'Unknown error') + '</p>';
          }
        })
        .withFailureHandler(function(error) {
          resultEl.innerHTML = '<p style="color: #e53e3e;">❌ Error: ' + error + '</p>';
        })
        .triggerSalesAgent();
    }
  </script>
</body>
</html>
  `;
}

/**
 * Create a menu item in Google Sheets (optional)
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('RivalEdge')
    .addItem('Open CEO Dashboard', 'showDashboard')
    .addToUi();
}

function showDashboard() {
  const html = HtmlService.createHtmlOutput(getDashboardHTML())
    .setWidth(1200)
    .setHeight(800)
    .setTitle('RivalEdge CEO Dashboard');
  SpreadsheetApp.getUi().showModalDialog(html, 'RivalEdge CEO Dashboard');
}
