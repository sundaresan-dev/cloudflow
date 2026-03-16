// My Deployments page functionality

document.addEventListener('DOMContentLoaded', async () => {
    await loadDeployments();
});

async function loadDeployments() {
    const result = await apiRequest('/deploy/list');
    
    if (result.success) {
        const deployments = result.data.deployments;
        const tbody = document.getElementById('deploymentsBody');
        const noDeployments = document.getElementById('noDeployments');
        const table = document.getElementById('deploymentsTable');
        
        if (deployments.length === 0) {
            table.style.display = 'none';
            noDeployments.style.display = 'block';
            return;
        }
        
        table.style.display = 'table';
        noDeployments.style.display = 'none';
        
        let html = '';
        deployments.forEach(deployment => {
            const createdDate = new Date(deployment.created_at).toLocaleDateString();
            const statusBadge = deployment.status === 'active' 
                ? '<span class="badge badge-success">Active</span>'
                : '<span class="badge badge-danger">Inactive</span>';
            
            // Extract domain from URL (remove http:// and port if present)
            let displayUrl = deployment.url;
            let visitLink = deployment.url;
            
            // Clean up URL for display
            if (displayUrl.includes('http://')) {
                displayUrl = displayUrl.replace('http://', '');
                displayUrl = displayUrl.replace('https://', '');
            }
            if (displayUrl.includes(':')) {
                displayUrl = displayUrl.split(':')[0];
            }
            
            // Ensure visitLink has protocol
            if (!visitLink.includes('http')) {
                visitLink = 'http://' + deployUrl;
            }
            
            html += `
                <tr>
                    <td><strong>${formatWebsiteType(deployment.website_type)}</strong></td>
                    <td><code>${deployment.site_folder}</code></td>
                    <td>${statusBadge}</td>
                    <td>${createdDate}</td>
                    <td>
                        <a href="${visitLink}" target="_blank" class="btn btn-sm btn-primary" title="Visit" style="text-decoration: none;">
                            🔗 Visit
                        </a>
                        <span class="text-muted small ms-2">${displayUrl}</span>
                        <button class="btn btn-sm btn-danger" onclick="deleteDeployment(${deployment.id})">
                            🗑️ Delete
                        </button>
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
    } else {
        showAlert(result.error || 'Failed to load deployments', 'danger');
    }
}

function formatWebsiteType(type) {
    const types = {
        'ecommerce': 'E-commerce',
        'school': 'School Management',
        'college': 'College Management',
        'hotel': 'Hotel Management'
    };
    return types[type] || type;
}

async function deleteDeployment(deploymentId) {
    if (!confirm('Are you sure you want to delete this deployment?')) {
        return;
    }
    
    const result = await apiRequest(`/deploy/delete/${deploymentId}`, {
        method: 'DELETE'
    });
    
    if (result.success) {
        showAlert('Deployment deleted successfully', 'success');
        await loadDeployments();
    } else {
        showAlert(result.error || 'Failed to delete deployment', 'danger');
    }
}
