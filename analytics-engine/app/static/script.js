document.addEventListener('DOMContentLoaded', () => {
    bindEvents();
    refreshDatasets().then(hasDatasets => {
        if (hasDatasets) {
            showDashboard();
        }
    });
});

const API_BASE = ""; // Relative path based on hosting

function bindEvents() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');

    // Drag and Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    // File Input
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    if (!file.name.endsWith('.csv')) {
        showStatus('Please upload a CSV file', 'error');
        return;
    }

    showStatus('Uploading...', 'info');

    const formData = new FormData();
    formData.append('File', file);

    try {
        const response = await fetch(`${API_BASE}/dataset/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        const data = await response.json();
        showStatus(`Uploaded: ${data.filename}`, 'success');
        
        // Switch to dashboard and reload list
        setTimeout(() => {
            showDashboard();
            refreshDatasets();
        }, 1000);

    } catch (error) {
        showStatus('Error uploading file', 'error');
        console.error(error);
    }
}

function showStatus(msg, type) {
    const statusDiv = document.getElementById('upload-status');
    statusDiv.textContent = msg;
    statusDiv.className = `status-message ${type}`; // Add styling for success/error in CSS if needed
    
    // Quick inline style for feedback
    if(type === 'error') statusDiv.style.color = '#ef4444';
    else if(type === 'success') statusDiv.style.color = '#10b981';
    else statusDiv.style.color = '#94a3b8';
}

function showUpload() {
    document.getElementById('upload-section').style.display = 'flex';
    document.getElementById('dashboard-section').classList.add('hidden');
    // Reset any status messages
    document.getElementById('upload-status').textContent = '';
}

function showDashboard() {
    // Hide upload section if desired, or just show dashboard section
    const upSection = document.getElementById('upload-section');
    const dashSection = document.getElementById('dashboard-section');
    
    // Instead of completely hiding upload, we can perhaps make it smaller or just scroll down
    // For now, let's swap views
    upSection.style.display = 'none';
    dashSection.classList.remove('hidden');
}

async function refreshDatasets() {
    const listContainer = document.getElementById('dataset-list');
    listContainer.innerHTML = '<li class="loading-item">Loading...</li>';

    try {
        const response = await fetch(`${API_BASE}/dataset/Load`);
        const data = await response.json();
        
        listContainer.innerHTML = '';
        
        if (data.file && data.file.length > 0) {
            data.file.forEach(serverFilename => {
                // Parse UUID and Display Name
                // Format: "{uuid}_{filename}" or old "{uuid}.csv"
                let display, id;
                
                if (serverFilename.includes('_')) {
                    const parts = serverFilename.split('_');
                    id = parts[0];
                    display = parts.slice(1).join('_'); // Rejoin in case filename had underscores
                } else {
                    // Fallback for old files
                     id = serverFilename.replace('.csv', '');
                     display = serverFilename;
                }

                const li = document.createElement('li');
                li.innerHTML = `<i class="fa-solid fa-file-csv"></i> ${display}`;
                li.onclick = () => loadDatasetStats(id, display, li);
                listContainer.appendChild(li);
            });
            return true;
        } else {
            listContainer.innerHTML = '<li>No datasets found.</li>';
            return false;
        }

    } catch (error) {
        console.error('Error loading datasets:', error);
        listContainer.innerHTML = '<li>Error loading list</li>';
        return false;
    }
}

async function loadDatasetStats(datasetId, displayName, listItem) {
    console.log("Loading stats for:", { datasetId, displayName });
    // UI Active State
    document.querySelectorAll('.dataset-list li').forEach(l => l.classList.remove('active'));
    listItem.classList.add('active');

    // Show stats view
    document.getElementById('select-prompt').classList.add('hidden');
    document.getElementById('stats-view').classList.remove('hidden');
    document.getElementById('current-filename').textContent = displayName;
    document.getElementById('dataset-id-badge').textContent = `ID: ${datasetId.substring(0,8)}...`;

    // Fetch Summary
    try {
        const sumResp = await fetch(`${API_BASE}/dataset/${datasetId}/Summary`);
        const sumData = await sumResp.json();
        
        // Populate Summary
        document.getElementById('rows-count').textContent = sumData.rows.toLocaleString();
        document.getElementById('cols-count').textContent = sumData.coloums.toLocaleString();
        
        renderColumnTypes(sumData.coloums_type);

    } catch (err) {
        console.error("Error fetching summary", err);
    }

    // Fetch Missing Values
    try {
        const missResp = await fetch(`${API_BASE}/dataset/${datasetId}/missing_values`);
        const missData = await missResp.json();
        
        renderMissingValues(missData.missing_values);

    } catch (err) {
        console.error("Error fetching missing values", err);
    }

    // Fetch Correlation Matrix
    const matrixContainer = document.getElementById('correlation-matrix-container');
    matrixContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: #94a3b8;">Loading matrix...</div>';

    try {
        const url = `${API_BASE}/dataset/${datasetId}/corelation_matrix`;
        console.log("Fetching matrix from:", url);
        const corrResp = await fetch(url);
        if (!corrResp.ok) {
            throw new Error(`HTTP error! status: ${corrResp.status}`);
        }
        const corrData = await corrResp.json();
        renderCorrelationMatrix(corrData.corelation);
    } catch (err) {
         console.error("Error fetching correlation matrix", err);
         matrixContainer.innerHTML = 
            `<div style="text-align:center; padding: 20px; color: #ef4444">Error loading matrix: ${err.message}</div>`;
    }
}

function renderCorrelationMatrix(matrix) {
    const container = document.getElementById('correlation-matrix-container');
    if (!matrix || Object.keys(matrix).length === 0) {
        container.innerHTML = '<div style="padding:20px; text-align:center">No numerical data for correlation</div>';
        return;
    }

    const columns = Object.keys(matrix);
    let html = '<table class="correlation-table"><thead><tr><th></th>';
    
    // Header Row
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';

    // Body Rows
    columns.forEach(rowCol => {
        html += `<tr><th>${rowCol}</th>`; // Row Header
        
        columns.forEach(colCol => {
            const value = matrix[rowCol][colCol];
            // Color scale: -1 (red) to 0 (transparent) to 1 (blue) or similar
            // Simple approach: Opacity of a color
            // Let's use Blue for positive, Red for negative
            let bgColor;
            if (value > 0) {
                // Blue: rgba(59, 130, 246, alpha)
                bgColor = `rgba(59, 130, 246, ${Math.abs(value).toFixed(2)})`;
            } else {
                // Red: rgba(239, 68, 68, alpha)
                bgColor = `rgba(239, 68, 68, ${Math.abs(value).toFixed(2)})`;
            }
            // For text contrast, if opacity is high (>0.5), use white, else use muted/white
            
            html += `<td style="background-color: ${bgColor}" title="${rowCol} vs ${colCol}: ${value.toFixed(4)}">
                        ${value.toFixed(2)}
                     </td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function renderColumnTypes(typesMap) {
    const container = document.getElementById('column-types-container');
    container.innerHTML = '';
    
    for (const [col, type] of Object.entries(typesMap)) {
        const div = document.createElement('div');
        div.className = 'col-type-item';
        div.innerHTML = `
            <span>${col}</span>
            <span class="type-tag">${type}</span>
        `;
        container.appendChild(div);
    }
}

function renderMissingValues(missingMap) {
    const container = document.getElementById('missing-values-container');
    container.innerHTML = '';

    const hasMissing = Object.values(missingMap).some(val => val > 0);

    if (!hasMissing) {
        container.innerHTML = '<div style="padding:10px; color:#10b981;">No missing values found! <i class="fa-solid fa-check"></i></div>';
        return;
    }

    // Calculate max for bar width
    const maxVal = Math.max(...Object.values(missingMap));

    for (const [col, count] of Object.entries(missingMap)) {
        if (count > 0) {
            const percentage = (count / maxVal) * 100;
            const div = document.createElement('div');
            div.className = 'mv-item';
            div.innerHTML = `
                <div class="mv-label">
                    <span>${col}</span>
                    <span>${count}</span>
                </div>
                <div class="mv-bar-bg">
                    <div class="mv-bar-fill" style="width: ${percentage}%"></div>
                </div>
            `;
            container.appendChild(div);
        }
    }
}
