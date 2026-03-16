// Create Website page functionality

let deployModal;
let selectedTemplate = null;

const TEMPLATE_ICONS = {
    'ecommerce': '🛒',
    'school': '🏫',
    'college': '🎓',
    'hotel': '🏨'
};

const TEMPLATE_COLORS = {
    'ecommerce': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'school': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'college': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'hotel': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
};

document.addEventListener('DOMContentLoaded', async () => {
    deployModal = new bootstrap.Modal(document.getElementById('deployModal'));
    
    // Load templates
    await loadTemplates();
    
    // Setup deploy button
    const deployBtn = document.getElementById('deployBtn');
    if (deployBtn) {
        deployBtn.addEventListener('click', handleDeploy);
    }
});

async function loadTemplates() {
    const container = document.getElementById('templatesContainer');
    container.innerHTML = '<div class="text-center"><div class="spinner-border"></div></div>';
    
    const result = await apiRequest('/deploy/templates');
    
    if (result.success && result.data.templates.length > 0) {
        const templates = result.data.templates;
        let html = '<div class="template-grid">';
        
        templates.forEach((template, index) => {
            const icon = TEMPLATE_ICONS[template.id] || '📦';
            
            html += `
                <div class="glass-card stagger-item" 
                     style="animation-delay: ${index * 0.1}s"
                     data-template="${template.id}" 
                     onclick="selectTemplate('${template.id}', '${template.name}')">
                    <div class="d-flex flex-column justify-content-center align-items-center h-100">
                        <div class="card-icon icon-${template.id}">
                            ${icon}
                        </div>
                        <h3 class="fw-bold">${template.name}</h3>
                        <p class="mb-4 text-muted-glass">Click to configure and deploy this platform to your custom domain.</p>
                        <button class="btn btn-outline-custom w-100 mt-auto" onclick="event.stopPropagation(); selectTemplate('${template.id}', '${template.name}')">
                            Configure <i class="bi bi-gear ms-1"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    } else {
        container.innerHTML = `
            <div class="alert alert-warning">
                No templates available. Please check the templates_websites folder.
            </div>
        `;
    }
}

function selectTemplate(templateId, templateName) {
    selectedTemplate = { id: templateId, name: templateName };
    document.getElementById('websiteType').value = templateId;
    document.getElementById('deployModal').querySelector('.modal-title').textContent = `Deploy - ${templateName}`;
    document.getElementById('websiteName').value = '';
    document.getElementById('websiteName').focus();
    deployModal.show();
}

async function handleDeploy() {
    if (!selectedTemplate) {
        showAlert('Please select a template', 'warning');
        return;
    }
    
    const websiteName = document.getElementById('websiteName').value.trim();
    const customDomain = document.getElementById('customDomain').value.trim().toLowerCase();
    
    if (!websiteName) {
        showAlert('Please enter a website name', 'warning', 'modalAlertContainer');
        return;
    }
    
    if (!customDomain) {
        showAlert('Please enter a custom domain', 'warning', 'modalAlertContainer');
        return;
    }
    
    // Validate domain format
    const domainRegex = /^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\.[a-z]{2,}$/;
    if (!domainRegex.test(customDomain)) {
        showAlert('Please enter a valid domain name (e.g., mysite.com)', 'warning', 'modalAlertContainer');
        return;
    }
    
    const deployBtn = document.getElementById('deployBtn');
    deployBtn.disabled = true;
    deployBtn.classList.add('deploying');
    deployBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Provisioning...';
    
    const result = await apiRequest('/deploy/create', {
        method: 'POST',
        body: JSON.stringify({
            website_type: selectedTemplate.id,
            website_name: websiteName,
            custom_domain: customDomain
        })
    });
    
    deployBtn.disabled = false;
    deployBtn.classList.remove('deploying');
    deployBtn.innerHTML = 'Launch Deployment <i class="bi bi-rocket-takeoff ms-1"></i>';
    
    if (result.success) {
        const domain = result.data.deployment?.domain;
        
        // Show success message with setup instructions
        let message = 'Website deployed successfully! ✓<br><br>';
        message += '<strong>🌐 Domain Setup Instructions:</strong><br>';
        message += `Add <code>${domain}</code> to /etc/hosts using one of these methods:<br><br>`;
        message += '<strong>Method 1:</strong><br>';
        message += `<code>sudo python3 add_domain_to_hosts.py ${domain}</code><br><br>`;
        message += `Then access: <code>http://${domain}</code>`;
        
        showAlert(message, 'success', 'modalAlertContainer');
        
        // Redirect after 4 seconds
        setTimeout(() => {
            window.location.href = '/deployments';
        }, 4000);
    } else {
        let errorMsg = result.error || 'Deployment failed';
        
        if (result.data && result.data.suggestions) {
            errorMsg += '<br><br><strong>Suggested Domains:</strong><br><div class="suggestion-grid mt-2">';
            result.data.suggestions.forEach(suggestion => {
                errorMsg += `<span class="suggestion-tag" onclick="document.getElementById('customDomain').value = '${suggestion}'">${suggestion}</span> `;
            });
            errorMsg += '</div>';
        }
        
        showAlert(errorMsg, 'danger', 'modalAlertContainer');
    }
}
