// VeriModel Web UI JavaScript

// Detect if running in Tauri
const isTauri = typeof window.__TAURI__ !== 'undefined';

// API base URL - use localhost for Tauri desktop app
const API_BASE = isTauri ? 'http://localhost:8000/api/v1' : '/api/v1';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeUpload();
    initializeConvert();
    initializeThreatIntel();
    initializeTimeoutSlider();
    initializeTooltips();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Timeout slider
function initializeTimeoutSlider() {
    const slider = document.getElementById('timeout');
    const value = document.getElementById('timeoutValue');
    slider.addEventListener('input', (e) => {
        value.textContent = e.target.value;
    });
}

// Upload area handlers
function initializeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const scanBtn = document.getElementById('scanBtn');
    const clearBtn = document.getElementById('clearBtn');

    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    scanBtn.addEventListener('click', () => scanFile());
    clearBtn.addEventListener('click', () => {
        fileInput.value = '';
        fileInfo.style.display = 'none';
        document.getElementById('scanResults').innerHTML = '';
    });
}

function handleFileSelect(file) {
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    document.getElementById('fileInfo').style.display = 'block';
    window.selectedFile = file;
}

async function scanFile() {
    if (!window.selectedFile) {
        alert('Vui lòng chọn file!');
        return;
    }

    const formData = new FormData();
    formData.append('file', window.selectedFile);
    formData.append('static_only', document.getElementById('staticOnly').checked);
    formData.append('dynamic_only', document.getElementById('dynamicOnly').checked);
    formData.append('include_threat_intel', document.getElementById('includeThreatIntel').checked);
    formData.append('timeout', document.getElementById('timeout').value);

    const resultsDiv = document.getElementById('scanResults');
    resultsDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p>Đang quét...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/scan`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        const data = await response.json();
        displayScanResults(data);
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Lỗi: ${error.message}</div>`;
    }
}

function displayScanResults(results) {
    const div = document.getElementById('scanResults');
    let html = '';

    // Static results
    if (results.static && !results.static.error) {
        html += '<div class="card mt-3"><div class="card-header"><h5>📊 Quét Tĩnh</h5></div><div class="card-body">';
        html += `<p><strong>Tổng Opcodes:</strong> ${results.static.total_opcodes || 0}</p>`;
        html += `<p><strong>Mối đe dọa:</strong> ${results.static.threats?.length || 0}</p>`;
        html += `<p><strong>Cảnh báo:</strong> ${results.static.warnings?.length || 0}</p>`;
        
        if (results.static.threats && results.static.threats.length > 0) {
            html += '<h6 class="text-danger">🚨 Mối đe dọa:</h6>';
            results.static.threats.forEach(threat => {
                html += `<div class="threat-item">${threat.type} (${threat.severity}): ${threat.description}</div>`;
            });
        }
        html += '</div></div>';
    }

    // Dynamic results
    if (results.dynamic && !results.dynamic.error) {
        html += '<div class="card mt-3"><div class="card-header"><h5>🔬 Quét Động</h5></div><div class="card-body">';
        const isSafe = results.dynamic.is_safe !== false;
        html += `<p><strong>Trạng thái:</strong> ${isSafe ? '<span class="text-success">✅ An toàn</span>' : '<span class="text-danger">🚨 Nguy hiểm</span>'}</p>`;
        
        if (results.dynamic.threats && results.dynamic.threats.length > 0) {
            html += '<h6 class="text-danger">🚨 Hành vi độc hại:</h6>';
            results.dynamic.threats.forEach(threat => {
                html += `<div class="threat-item">${threat.type} (${threat.severity}): ${threat.description}</div>`;
            });
        }
        html += '</div></div>';
    }

    // Threat Intelligence
    if (results.threat_intelligence && !results.threat_intelligence.error) {
        html += '<div class="card mt-3"><div class="card-header"><h5>🕵️ Threat Intelligence</h5></div><div class="card-body">';
        const iocs = results.threat_intelligence.iocs || {};
        html += `<p><strong>Hashes:</strong> ${iocs.hashes?.length || 0}</p>`;
        html += `<p><strong>IPs:</strong> ${iocs.ips?.length || 0}</p>`;
        html += `<p><strong>Domains:</strong> ${iocs.domains?.length || 0}</p>`;
        
        if (results.threat_intelligence.threats && results.threat_intelligence.threats.length > 0) {
            html += '<h6 class="text-danger">🚨 Alerts:</h6>';
            results.threat_intelligence.threats.forEach(threat => {
                html += `<div class="threat-item">${threat.type}: ${threat.description}</div>`;
            });
        }
        html += '</div></div>';
    }

    // Final verdict
    const verdict = results.final_verdict;
    if (verdict) {
        const isSafe = verdict.is_safe;
        const cardClass = isSafe ? 'result-safe' : 'result-danger';
        html += `<div class="result-card ${cardClass} mt-3">`;
        html += `<h4>${isSafe ? '✅ KẾT LUẬN: FILE AN TOÀN' : '🚨 KẾT LUẬN: FILE NGUY HIỂM'}</h4>`;
        if (verdict.reasons && verdict.reasons.length > 0) {
            html += '<ul>';
            verdict.reasons.forEach(reason => {
                html += `<li>${reason}</li>`;
            });
            html += '</ul>';
        }
        html += '</div>';
    }

    div.innerHTML = html;
}

// Convert functionality
function initializeConvert() {
    const uploadArea = document.getElementById('convertUploadArea');
    const fileInput = document.getElementById('convertFileInput');
    const convertBtn = document.getElementById('convertBtn');

    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            document.getElementById('convertFileName').textContent = file.name;
            document.getElementById('convertFileInfo').style.display = 'block';
            window.convertFile = file;
        }
    });

    convertBtn.addEventListener('click', () => convertFile());
}

async function convertFile() {
    if (!window.convertFile) {
        alert('Vui lòng chọn file!');
        return;
    }

    const formData = new FormData();
    formData.append('file', window.convertFile);
    formData.append('safe_mode', 'true');

    const resultsDiv = document.getElementById('convertResults');
    resultsDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-success" role="status"></div><p>Đang chuyển đổi...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/convert`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        // Lấy tên file từ Content-Disposition header hoặc tạo từ tên file gốc
        const contentDisposition = response.headers.get('Content-Disposition');
        let outputFileName = window.convertFile.name.replace(/\.(pkl|pickle|pth)$/i, '.safetensors');
        
        if (contentDisposition) {
            const fileNameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
            if (fileNameMatch) {
                outputFileName = fileNameMatch[1];
            }
        }

        const blob = await response.blob();
        
        if (blob.size === 0) {
            throw new Error('File output rỗng - có thể chuyển đổi thất bại');
        }

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = outputFileName;
        
        // Trigger download
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Cleanup URL sau 1 giây
        setTimeout(() => window.URL.revokeObjectURL(url), 1000);

        // Hiển thị thông báo với tên file rõ ràng
        const fileSize = formatFileSize(blob.size);
        resultsDiv.innerHTML = `
            <div class="alert alert-success">
                <h5>✅ Chuyển đổi thành công!</h5>
                <p><strong>Tên file gốc:</strong> ${window.convertFile.name}</p>
                <p><strong>Tên file đã chuyển đổi:</strong> <code>${outputFileName}</code></p>
                <p><strong>Kích thước:</strong> ${fileSize}</p>
                <p class="mb-0">📥 File đã được tải xuống tự động.</p>
            </div>
        `;
    } catch (error) {
        resultsDiv.innerHTML = `
            <div class="alert alert-danger">
                <h5>❌ Lỗi khi chuyển đổi</h5>
                <p><strong>Chi tiết:</strong> ${error.message}</p>
                <p class="mb-0"><small>Vui lòng kiểm tra:</small><br>
                • File có phải là PyTorch model không?<br>
                • Đã cài đặt torch và safetensors chưa?<br>
                • File có bị hỏng không?</p>
            </div>
        `;
    }
}

// Threat Intelligence
function initializeThreatIntel() {
    document.getElementById('queryBtn').addEventListener('click', () => queryThreatIntel());
}

async function queryThreatIntel() {
    const hash = document.getElementById('tiHash').value.trim();
    const ip = document.getElementById('tiIP').value.trim();
    const domain = document.getElementById('tiDomain').value.trim();

    if (!hash && !ip && !domain) {
        alert('Vui lòng nhập ít nhất một giá trị!');
        return;
    }

    const resultsDiv = document.getElementById('threatResults');
    resultsDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p>Đang tra cứu...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/threat-intel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ hash, ip, domain })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        const data = await response.json();
        displayThreatIntelResults(data);
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Lỗi: ${error.message}</div>`;
    }
}

function displayThreatIntelResults(results) {
    const div = document.getElementById('threatResults');
    let html = '<div class="card mt-3"><div class="card-body">';

    if (results.hash) {
        const hashResult = results.hash;
        html += '<h6><i class="bi bi-hash"></i> Hash Results</h6>';
        
        if (hashResult.error) {
            html += `<div class="alert alert-warning">⚠️ ${hashResult.error}</div>`;
        } else if (hashResult.found === false) {
            html += '<div class="alert alert-info">ℹ️ Hash không được tìm thấy trong VirusTotal database</div>';
        } else if (hashResult.found) {
            const positives = hashResult.positives || 0;
            const total = hashResult.total || 0;
            const isThreat = positives > 0;
            
            html += `<div class="alert ${isThreat ? 'alert-danger' : 'alert-success'}">`;
            html += `<strong>${isThreat ? '🚨' : '✅'} Phát hiện:</strong> ${positives}/${total} antivirus engines đánh dấu là độc hại<br>`;
            if (hashResult.permalink) {
                html += `<a href="${hashResult.permalink}" target="_blank" class="btn btn-sm btn-outline-primary mt-2">Xem chi tiết trên VirusTotal</a>`;
            }
            html += '</div>';
            
            if (hashResult.scan_date) {
                html += `<p><small class="text-muted">Ngày quét: ${hashResult.scan_date}</small></p>`;
            }
        }
    }

    if (results.ip) {
        const ipResult = results.ip;
        html += '<h6><i class="bi bi-globe"></i> IP Address Results</h6>';
        
        if (ipResult.error) {
            html += `<div class="alert alert-warning">⚠️ ${ipResult.error}</div>`;
        } else if (ipResult.found === false) {
            html += '<div class="alert alert-info">ℹ️ IP không được tìm thấy trong VirusTotal database</div>';
        } else if (ipResult.found) {
            const detectedUrls = ipResult.detected_urls || [];
            const undetectedUrls = ipResult.undetected_urls || [];
            const isThreat = detectedUrls.length > 0;
            
            html += `<div class="alert ${isThreat ? 'alert-danger' : 'alert-success'}">`;
            html += `<strong>${isThreat ? '🚨' : '✅'} Trạng thái:</strong> `;
            if (isThreat) {
                html += `IP có liên quan đến ${detectedUrls.length} URL độc hại`;
            } else {
                html += 'IP không có lịch sử độc hại';
            }
            html += '</div>';
            
            if (ipResult.country) {
                html += `<p><strong>Quốc gia:</strong> ${ipResult.country}</p>`;
            }
            if (ipResult.asn) {
                html += `<p><strong>ASN:</strong> ${ipResult.asn}</p>`;
            }
            if (detectedUrls.length > 0) {
                html += '<p><strong>URL độc hại phát hiện:</strong></p><ul>';
                detectedUrls.slice(0, 5).forEach(url => {
                    html += `<li><a href="${url.url}" target="_blank">${url.url}</a> (${url.positives}/${url.total})</li>`;
                });
                if (detectedUrls.length > 5) {
                    html += `<li><small>... và ${detectedUrls.length - 5} URL khác</small></li>`;
                }
                html += '</ul>';
            }
        }
    }

    if (results.domain) {
        const domainResult = results.domain;
        html += '<h6><i class="bi bi-link-45deg"></i> Domain Results</h6>';
        
        if (domainResult.error) {
            html += `<div class="alert alert-warning">⚠️ ${domainResult.error}</div>`;
        } else if (domainResult.found === false) {
            html += '<div class="alert alert-info">ℹ️ Domain không được tìm thấy trong VirusTotal database</div>';
        } else if (domainResult.found) {
            const detectedUrls = domainResult.detected_urls || [];
            const isThreat = detectedUrls.length > 0;
            
            html += `<div class="alert ${isThreat ? 'alert-danger' : 'alert-success'}">`;
            html += `<strong>${isThreat ? '🚨' : '✅'} Trạng thái:</strong> `;
            if (isThreat) {
                html += `Domain có liên quan đến ${detectedUrls.length} URL độc hại`;
            } else {
                html += 'Domain không có lịch sử độc hại';
            }
            html += '</div>';
            
            if (domainResult.categories && Object.keys(domainResult.categories).length > 0) {
                html += '<p><strong>Categories:</strong> ';
                html += Object.entries(domainResult.categories).map(([cat, source]) => 
                    `<span class="badge bg-secondary">${cat}</span>`
                ).join(' ');
                html += '</p>';
            }
            
            if (domainResult.subdomains && domainResult.subdomains.length > 0) {
                html += `<p><strong>Subdomains:</strong> ${domainResult.subdomains.length} subdomains được phát hiện</p>`;
            }
            
            if (detectedUrls.length > 0) {
                html += '<p><strong>URL độc hại phát hiện:</strong></p><ul>';
                detectedUrls.slice(0, 5).forEach(url => {
                    html += `<li><a href="${url.url}" target="_blank">${url.url}</a> (${url.positives}/${url.total})</li>`;
                });
                if (detectedUrls.length > 5) {
                    html += `<li><small>... và ${detectedUrls.length - 5} URL khác</small></li>`;
                }
                html += '</ul>';
            }
        }
    }

    html += '</div></div>';
    div.innerHTML = html;
    
    // Re-initialize tooltips sau khi render content mới (nếu có tooltip mới)
    initializeTooltips();
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

