// Configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let queryHistory = [];
let totalExecutionTime = 0;
let connectionParams = null;

// DOM Elements
const dbTypeSelect = document.getElementById('dbType');
const testConnectionBtn = document.getElementById('testConnection');
const connectionStatus = document.getElementById('connectionStatus');
const queryInput = document.getElementById('queryInput');
const executeQueryBtn = document.getElementById('executeQuery');
const generateOnlyBtn = document.getElementById('generateOnly');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const loadingIndicator = document.getElementById('loadingIndicator');
const exampleQueriesContainer = document.getElementById('exampleQueries');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadExampleQueries();
    setupEventListeners();
    updateConnectionFields();
});

// Event Listeners
function setupEventListeners() {
    dbTypeSelect.addEventListener('change', updateConnectionFields);
    testConnectionBtn.addEventListener('click', testConnection);
    executeQueryBtn.addEventListener('click', () => executeQuery(true));
    generateOnlyBtn.addEventListener('click', () => executeQuery(false));
    document.getElementById('copySQL')?.addEventListener('click', copySQL);
    document.getElementById('exportCSV')?.addEventListener('click', exportCSV);
}

// Update connection fields based on database type
function updateConnectionFields() {
    const dbType = dbTypeSelect.value;
    const fieldsContainer = document.getElementById('connectionFields');

    if (dbType === 'postgresql' || dbType === 'mysql') {
        const defaultPort = dbType === 'postgresql' ? '5432' : '3306';
        document.getElementById('port').placeholder = defaultPort;
        fieldsContainer.innerHTML = `
            <div class="form-row">
                <div class="form-group">
                    <label for="host">Host</label>
                    <input type="text" id="host" class="form-control" placeholder="localhost" value="localhost">
                </div>
                <div class="form-group">
                    <label for="port">Port</label>
                    <input type="text" id="port" class="form-control" placeholder="${defaultPort}" value="${defaultPort}">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="database">Database</label>
                    <input type="text" id="database" class="form-control" placeholder="analytics" value="">
                </div>
                <div class="form-group">
                    <label for="user">User</label>
                    <input type="text" id="user" class="form-control" placeholder="analyst" value="">
                </div>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" class="form-control" placeholder="••••••••" value="">
            </div>
        `;
    } else if (dbType === 'snowflake') {
        fieldsContainer.innerHTML = `
            <div class="form-row">
                <div class="form-group">
                    <label for="account">Account</label>
                    <input type="text" id="account" class="form-control" placeholder="your-account">
                </div>
                <div class="form-group">
                    <label for="warehouse">Warehouse</label>
                    <input type="text" id="warehouse" class="form-control" placeholder="COMPUTE_WH">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="database">Database</label>
                    <input type="text" id="database" class="form-control" placeholder="ANALYTICS_DB">
                </div>
                <div class="form-group">
                    <label for="schema">Schema</label>
                    <input type="text" id="schema" class="form-control" placeholder="PUBLIC" value="PUBLIC">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="user">User</label>
                    <input type="text" id="user" class="form-control" placeholder="analyst">
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" class="form-control" placeholder="••••••••">
                </div>
            </div>
        `;
    } else if (dbType === 'databricks') {
        fieldsContainer.innerHTML = `
            <div class="form-group">
                <label for="server_hostname">Server Hostname</label>
                <input type="text" id="server_hostname" class="form-control" placeholder="your-workspace.cloud.databricks.com">
            </div>
            <div class="form-group">
                <label for="http_path">HTTP Path</label>
                <input type="text" id="http_path" class="form-control" placeholder="/sql/1.0/warehouses/...">
            </div>
            <div class="form-group">
                <label for="access_token">Access Token</label>
                <input type="password" id="access_token" class="form-control" placeholder="dapi...">
            </div>
        `;
    }
}

// Get connection parameters from form
function getConnectionParams() {
    const dbType = dbTypeSelect.value;
    let params = {};

    if (dbType === 'postgresql' || dbType === 'mysql') {
        params = {
            host: document.getElementById('host').value,
            port: document.getElementById('port').value,
            database: document.getElementById('database').value,
            user: document.getElementById('user').value,
            password: document.getElementById('password').value
        };
    } else if (dbType === 'snowflake') {
        params = {
            account: document.getElementById('account').value,
            warehouse: document.getElementById('warehouse').value,
            database: document.getElementById('database').value,
            schema: document.getElementById('schema').value,
            user: document.getElementById('user').value,
            password: document.getElementById('password').value
        };
    } else if (dbType === 'databricks') {
        params = {
            server_hostname: document.getElementById('server_hostname').value,
            http_path: document.getElementById('http_path').value,
            access_token: document.getElementById('access_token').value
        };
    }

    return params;
}

// Test database connection
async function testConnection() {
    const params = getConnectionParams();
    const dbType = dbTypeSelect.value;

    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/api/test-connection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                db_type: dbType,
                connection_params: params
            })
        });

        const data = await response.json();

        if (data.success) {
            connectionStatus.textContent = '✓ Connected';
            connectionStatus.className = 'status-indicator success';
            connectionParams = params;
        } else {
            connectionStatus.textContent = '✗ Failed: ' + data.message;
            connectionStatus.className = 'status-indicator error';
        }
    } catch (error) {
        connectionStatus.textContent = '✗ Error: ' + error.message;
        connectionStatus.className = 'status-indicator error';
    } finally {
        hideLoading();
    }
}

// Execute query
async function executeQuery(shouldExecute) {
    const question = queryInput.value.trim();

    if (!question) {
        showError('Please enter a question');
        return;
    }

    const params = getConnectionParams();
    const dbType = dbTypeSelect.value;

    showLoading();
    hideError();
    hideResults();

    try {
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                db_type: dbType,
                connection_params: params,
                execute: shouldExecute
            })
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
            updateStats(data.execution_time);
        } else {
            showError(data.error || 'Query failed');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Display results
function displayResults(data) {
    resultsSection.style.display = 'block';

    // Metadata
    document.getElementById('complexity').textContent = data.complexity || 'Unknown';
    document.getElementById('complexity').className = `badge ${(data.complexity || 'medium').toLowerCase()}`;
    document.getElementById('executionTime').textContent = `${(data.execution_time || 0).toFixed(2)}s`;
    document.getElementById('rowCount').textContent = data.row_count || 0;

    // Explanation
    document.getElementById('explanation').textContent = data.explanation || 'No explanation provided';

    // SQL Query
    document.getElementById('sqlQuery').textContent = data.sql || 'No SQL generated';

    // Assumptions
    if (data.assumptions && data.assumptions.length > 0) {
        const assumptionsSection = document.getElementById('assumptionsSection');
        assumptionsSection.style.display = 'block';
        const assumptionsList = document.getElementById('assumptions');
        assumptionsList.innerHTML = data.assumptions.map(a => `<li>${a}</li>`).join('');
    } else {
        document.getElementById('assumptionsSection').style.display = 'none';
    }

    // Data table
    if (data.results && data.results.length > 0) {
        displayDataTable(data.results);
    } else {
        document.getElementById('dataSection').style.display = 'none';
    }

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Display data table
function displayDataTable(results) {
    const dataSection = document.getElementById('dataSection');
    dataSection.style.display = 'block';

    const table = document.getElementById('resultsTable');
    const columns = Object.keys(results[0]);

    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    // Create body
    const tbody = document.createElement('tbody');
    results.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = row[col] !== null && row[col] !== undefined ? row[col] : 'NULL';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    // Clear and populate table
    table.innerHTML = '';
    table.appendChild(thead);
    table.appendChild(tbody);
}

// Copy SQL to clipboard
function copySQL() {
    const sqlText = document.getElementById('sqlQuery').textContent;
    navigator.clipboard.writeText(sqlText).then(() => {
        const copyBtn = document.getElementById('copySQL');
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    });
}

// Export to CSV
function exportCSV() {
    const table = document.getElementById('resultsTable');
    const rows = table.querySelectorAll('tr');

    let csv = [];
    rows.forEach(row => {
        const cols = row.querySelectorAll('th, td');
        const csvRow = Array.from(cols).map(col => {
            let data = col.textContent;
            // Escape quotes and wrap in quotes if contains comma
            data = data.replace(/"/g, '""');
            if (data.includes(',') || data.includes('"') || data.includes('\n')) {
                data = `"${data}"`;
            }
            return data;
        });
        csv.push(csvRow.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'query_results.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Load example queries
async function loadExampleQueries() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/examples`);
        const data = await response.json();

        const examples = data.examples.flatMap(category =>
            category.queries.slice(0, 2) // Take 2 from each category
        );

        exampleQueriesContainer.innerHTML = examples.map(query => `
            <div class="example-chip" onclick="useExample('${query.replace(/'/g, "\\'")}')">
                ${query}
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load examples:', error);
    }
}

// Use example query
function useExample(query) {
    queryInput.value = query;
    queryInput.focus();
}

// Update stats
function updateStats(executionTime) {
    queryHistory.push(executionTime);
    totalExecutionTime += executionTime;

    document.getElementById('queryCount').textContent = queryHistory.length;
    document.getElementById('avgTime').textContent = `${(totalExecutionTime / queryHistory.length).toFixed(2)}s`;
}

// UI Helper Functions
function showLoading() {
    loadingIndicator.style.display = 'flex';
}

function hideLoading() {
    loadingIndicator.style.display = 'none';
}

function showError(message) {
    errorSection.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

function hideError() {
    errorSection.style.display = 'none';
}

function hideResults() {
    resultsSection.style.display = 'none';
}
