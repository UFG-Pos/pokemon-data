// Dashboard JavaScript
const API_BASE = '';
let loadingModal;
let toast;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    toast = new bootstrap.Toast(document.getElementById('toast'));
    
    // Load initial data
    refreshStatus();
    refreshEvents();
    refreshAlerts();
    
    // Auto-refresh every 30 seconds
    setInterval(refreshStatus, 30000);
    setInterval(refreshEvents, 60000);
});

// Utility functions
function showLoading() {
    loadingModal.show();
}

function hideLoading() {
    if (loadingModal) {
        loadingModal.hide();
        // Garantir que o modal seja fechado mesmo em casos extremos
        setTimeout(() => {
            const modalElement = document.getElementById('loadingModal');
            if (modalElement && modalElement.classList.contains('show')) {
                modalElement.classList.remove('show');
                modalElement.style.display = 'none';
                document.body.classList.remove('modal-open');
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
            }
        }, 100);
    }
}

function setButtonLoading(buttonElement, loading = true) {
    if (loading) {
        buttonElement.disabled = true;
        const originalText = buttonElement.innerHTML;
        buttonElement.setAttribute('data-original-text', originalText);
        buttonElement.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processando...';
    } else {
        buttonElement.disabled = false;
        const originalText = buttonElement.getAttribute('data-original-text');
        if (originalText) {
            buttonElement.innerHTML = originalText;
            buttonElement.removeAttribute('data-original-text');
        }
    }
}

function showToast(message, type = 'info') {
    const toastElement = document.getElementById('toast');
    const toastBody = document.getElementById('toastBody');
    
    // Remove existing classes
    toastElement.classList.remove('text-bg-success', 'text-bg-danger', 'text-bg-warning', 'text-bg-info');
    
    // Add appropriate class
    switch(type) {
        case 'success':
            toastElement.classList.add('text-bg-success');
            break;
        case 'error':
            toastElement.classList.add('text-bg-danger');
            break;
        case 'warning':
            toastElement.classList.add('text-bg-warning');
            break;
        default:
            toastElement.classList.add('text-bg-info');
    }
    
    toastBody.textContent = message;
    toast.show();
}

async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(API_BASE + endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast(`Erro na API: ${error.message}`, 'error');
        throw error;
    }
}

// Status functions
async function refreshStatus() {
    try {
        // Get pipeline status
        const pipelineStatus = await apiCall('/api/v1/pipeline/status');
        updateStatusCards(pipelineStatus.pipeline_status);
        
        // Get pokemon count
        const pokemonData = await apiCall('/api/v1/pokemons?limit=1');
        document.getElementById('totalPokemons').textContent = pokemonData.total || 0;
        
        // Update connection status
        document.getElementById('connectionStatus').innerHTML = 
            '<span class="status-indicator status-active"></span>Conectado';
            
    } catch (error) {
        document.getElementById('connectionStatus').innerHTML = 
            '<span class="status-indicator status-inactive"></span>Desconectado';
    }
}

function updateStatusCards(status) {
    // Stream processor status
    const streamStatus = document.getElementById('streamStatus');
    const isRunning = status.stream_processor.is_running;
    streamStatus.innerHTML = isRunning ?
        '<span class="status-indicator status-active"></span>Ativo' :
        '<span class="status-indicator status-inactive"></span>Inativo';

    // Alerts count
    document.getElementById('totalAlerts').textContent = status.alert_system.total_alerts;

    // Get real data quality from dashboard
    updateDataQuality();
}

async function updateDataQuality() {
    try {
        const result = await apiCall('/api/v1/pipeline/dashboard/data');
        if (result.success && result.dashboard.data_quality.quality_score !== undefined) {
            document.getElementById('dataQuality').textContent = `${result.dashboard.data_quality.quality_score.toFixed(1)}%`;
        } else {
            document.getElementById('dataQuality').textContent = 'N/A';
        }
    } catch (error) {
        document.getElementById('dataQuality').textContent = 'N/A';
    }
}

// Pokemon functions
async function importPokemon() {
    const name = document.getElementById('pokemonName').value.trim();
    if (!name) {
        showToast('Digite o nome do pokémon', 'warning');
        return;
    }

    showLoading();

    try {
        const result = await apiCall(`/api/v1/import-pokemon?name=${encodeURIComponent(name)}`);

        if (result.success) {
            showToast(`Pokémon ${name} importado com sucesso!`, 'success');
            document.getElementById('pokemonName').value = '';
            refreshStatus();
        } else {
            showToast(`Erro ao importar ${name}`, 'error');
        }
    } catch (error) {
        // Error already handled by apiCall
    } finally {
        hideLoading();
    }
}

async function importSamplePokemons() {
    const samples = ['pikachu', 'charizard', 'blastoise', 'venusaur', 'alakazam'];
    showLoading();

    try {
        let imported = 0;
        for (const pokemon of samples) {
            try {
                await apiCall(`/api/v1/import-pokemon?name=${pokemon}`);
                imported++;
            } catch (error) {
                console.warn(`Failed to import ${pokemon}:`, error);
            }
        }

        showToast(`${imported} pokémons de exemplo importados!`, 'success');
        refreshStatus();
    } catch (error) {
        // Error already handled by apiCall
    } finally {
        hideLoading();
    }
}

async function listPokemons() {
    showLoading();
    try {
        const result = await apiCall('/api/v1/pokemons?limit=20');

        const container = document.getElementById('pokemonList');
        if (result.success && result.data && result.data.length > 0) {
            container.innerHTML = result.data.map(pokemon => `
                <div class="pokemon-card">
                    <img src="${pokemon.sprites?.front_default || '/static/placeholder.svg'}"
                         alt="${pokemon.name}" class="pokemon-sprite">
                    <h6>${pokemon.name}</h6>
                    <small class="text-muted">ID: ${pokemon.id}</small>
                    <div class="mt-1">
                        ${pokemon.types.map(type =>
                            `<span class="badge bg-secondary">${type.name}</span>`
                        ).join(' ')}
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="text-muted">Nenhum pokémon encontrado</div>';
        }
    } catch (error) {
        document.getElementById('pokemonList').innerHTML =
            '<div class="text-danger">Erro ao carregar pokémons</div>';
    } finally {
        hideLoading();
    }
}

// Pipeline functions
async function startStream() {
    showLoading();
    try {
        const result = await apiCall('/api/v1/pipeline/stream/start', { method: 'POST' });

        if (result.success) {
            showToast('Stream processor iniciado!', 'success');
            refreshStatus();
        } else {
            showToast(result.message || 'Erro ao iniciar stream', 'warning');
        }
    } catch (error) {
        // Error already handled by apiCall
    } finally {
        hideLoading();
    }
}

async function stopStream() {
    showLoading();
    try {
        const result = await apiCall('/api/v1/pipeline/stream/stop', { method: 'POST' });

        if (result.success) {
            showToast('Stream processor parado!', 'success');
            refreshStatus();
        } else {
            showToast('Erro ao parar stream', 'error');
        }
    } catch (error) {
        // Error already handled by apiCall
    } finally {
        hideLoading();
    }
}

async function simulateAnomaly() {
    showLoading();
    try {
        const result = await apiCall('/api/v1/pipeline/stream/simulate-anomaly?pokemon_name=pikachu&anomaly_type=negative_stats',
            { method: 'POST' });

        if (result.success) {
            showToast('Anomalia simulada com sucesso!', 'success');
            refreshEvents();
            refreshAlerts();
        } else {
            showToast('Erro ao simular anomalia', 'error');
        }
    } catch (error) {
        // Error already handled by apiCall
    } finally {
        hideLoading();
    }
}

async function exportCSV() {
    showLoading();
    try {
        const result = await apiCall('/api/v1/pipeline/file/export-csv', { method: 'POST' });

        if (result.success) {
            showToast(`CSV exportado: ${result.filepath}`, 'success');
        } else {
            showToast('Erro ao exportar CSV', 'error');
        }
    } catch (error) {
        // Error already handled by apiCall
    } finally {
        hideLoading();
    }
}

async function exportJSON() {
    showLoading();
    try {
        const result = await apiCall('/api/v1/pipeline/file/export-json', { method: 'POST' });

        if (result.success) {
            showToast(`JSON exportado: ${result.filepath}`, 'success');
        } else {
            showToast('Erro ao exportar JSON', 'error');
        }
    } catch (error) {
        // Error already handled by apiCall
    } finally {
        hideLoading();
    }
}

async function cleanData() {
    showLoading();
    try {
        const result = await apiCall('/api/v1/pipeline/file/clean-data', { method: 'POST' });

        if (result.success) {
            const processed = result.result.processed;
            showToast(`Dados limpos: ${processed} pokémons processados`, 'success');
        } else {
            showToast('Erro na limpeza de dados', 'error');
        }
    } catch (error) {
        // Error already handled by apiCall
    } finally {
        hideLoading();
    }
}

async function generateReport(type) {
    showLoading();
    try {
        const result = await apiCall(`/api/v1/pipeline/dashboard/report?report_type=${type}`, { method: 'POST' });

        if (result.success) {
            showToast(`Relatório ${type} gerado: ${result.filepath}`, 'success');
        } else {
            showToast(`Erro ao gerar relatório ${type}`, 'error');
        }
    } catch (error) {
        // Error already handled by apiCall
    } finally {
        hideLoading();
    }
}

function viewDashboard() {
    window.open('/api/v1/pipeline/dashboard/html', '_blank');
}

// Events and alerts
async function refreshEvents() {
    try {
        const result = await apiCall('/api/v1/pipeline/stream/events?limit=10');
        const container = document.getElementById('eventsLog');
        
        if (result.events && result.events.length > 0) {
            container.innerHTML = result.events.map(event => {
                const time = new Date(event.timestamp).toLocaleTimeString();
                const anomalies = event.anomalies_count > 0 ? 
                    `<span class="badge bg-warning">${event.anomalies_count} anomalias</span>` : '';
                return `<div class="mb-1">
                    <small class="text-muted">${time}</small> 
                    <strong>${event.pokemon_name}</strong> ${anomalies}
                </div>`;
            }).join('');
        } else {
            container.innerHTML = '<div class="text-muted">Nenhum evento recente</div>';
        }
    } catch (error) {
        document.getElementById('eventsLog').innerHTML = 
            '<div class="text-danger">Erro ao carregar eventos</div>';
    }
}

async function refreshAlerts() {
    try {
        const result = await apiCall('/api/v1/pipeline/alerts/history?limit=10');
        const container = document.getElementById('alertsLog');
        
        if (result.alerts && result.alerts.length > 0) {
            container.innerHTML = result.alerts.map(alert => {
                const time = new Date(alert.timestamp).toLocaleTimeString();
                const levelClass = {
                    'info': 'text-info',
                    'warning': 'text-warning', 
                    'critical': 'text-danger'
                }[alert.level] || 'text-secondary';
                
                return `<div class="mb-1">
                    <small class="text-muted">${time}</small>
                    <span class="badge bg-secondary">${alert.level}</span>
                    <div class="${levelClass}">${alert.title}</div>
                </div>`;
            }).join('');
        } else {
            container.innerHTML = '<div class="text-muted">Nenhum alerta recente</div>';
        }
    } catch (error) {
        document.getElementById('alertsLog').innerHTML = 
            '<div class="text-danger">Erro ao carregar alertas</div>';
    }
}

async function testAlert() {
    try {
        const result = await apiCall('/api/v1/pipeline/alerts/test?level=info', { method: 'POST' });
        if (result.success) {
            showToast('Alerta de teste enviado!', 'success');
            refreshAlerts();
        } else {
            showToast('Erro no teste de alerta', 'error');
        }
    } catch (error) {
        // Error already handled by apiCall
    }
}

async function clearAlerts() {
    if (!confirm('Tem certeza que deseja limpar o histórico de alertas?')) {
        return;
    }
    
    try {
        const result = await apiCall('/api/v1/pipeline/alerts/clear-history', { method: 'POST' });
        if (result.success) {
            showToast('Histórico de alertas limpo!', 'success');
            refreshAlerts();
            refreshStatus();
        } else {
            showToast('Erro ao limpar alertas', 'error');
        }
    } catch (error) {
        // Error already handled by apiCall
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case 'r':
                e.preventDefault();
                refreshStatus();
                break;
            case 'i':
                e.preventDefault();
                document.getElementById('pokemonName').focus();
                break;
        }
    }
});
