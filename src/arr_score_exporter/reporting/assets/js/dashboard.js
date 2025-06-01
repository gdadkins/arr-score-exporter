/**
 * Dashboard functionality for Arr Score Exporter HTML reports
 */

// Global variables for charts and data
let scoreDistributionChart = null;
let formatEffectivenessChart = null;
let dashboardData = null;

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Upgrade Candidates DataTable specifically
    $('#upgradeTable').DataTable({
        pageLength: 25,
        dom: 'Bfrtip',
        buttons: [
            'csv', 'excel', 'pdf'
        ],
        order: [[1, 'asc']], // Sort by Current Score column ascending (worst scores first)
        responsive: true
    });
    
    // Initialize other data tables with different settings if needed
    $('.data-table:not(#upgradeTable)').DataTable({
        pageLength: 25,
        dom: 'Bfrtip',
        buttons: [
            'csv', 'excel', 'pdf'
        ],
        order: [[1, 'asc']], // Sort by title by default for other tables
        responsive: true
    });
    
    // Initialize Bootstrap 5 tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize charts if function is available
    if (typeof initializeCharts === 'function') {
        initializeCharts();
    }
    
    // Initialize upgrade table with default limit (10)
    setTimeout(() => {
        updateUpgradeTable();
    }, 100);
});

/**
 * Set up dashboard event listeners
 */
function setupEventListeners() {
    // Filter change events
    document.getElementById('scoreFilter')?.addEventListener('change', applyFilters);
    document.getElementById('formatFilter')?.addEventListener('input', applyFilters);
    document.getElementById('sizeFilter')?.addEventListener('change', applyFilters);
    
    // Collapsible sections
    const collapsibles = document.querySelectorAll('.collapsible');
    collapsibles.forEach(elem => {
        elem.addEventListener('click', function() {
            this.classList.toggle('active');
            const content = this.nextElementSibling;
            
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                content.style.maxHeight = '0';
            } else {
                content.classList.add('active');
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    });
}

/**
 * Apply dashboard filters
 */
function applyFilters() {
    // Filters are simplified since we no longer have detailed file data
    console.log('Filter functionality available with detailed file data');
}

/**
 * Reset all filters
 */
function resetFilters() {
    document.getElementById('scoreFilter').value = 'all';
    document.getElementById('formatFilter').value = '';
    document.getElementById('sizeFilter').value = 'all';
    applyFilters();
}

/**
 * Update charts with filtered data
 */
function updateCharts(filteredData) {
    // Charts use static data from server-side generation
    console.log('Chart updates available with detailed file data');
}

/**
 * Show category modal with file details
 */
function showCategoryModal(category, filesData) {
    const modal = document.getElementById('categoryModal');
    if (!modal) {
        console.warn('Category modal not found');
        return;
    }
    
    const modalTitle = document.getElementById('modalTitle');
    const modalContent = document.getElementById('modalContent');
    
    // Set title based on category
    const titles = {
        'premium_quality': 'Premium Quality Files',
        'upgrade_worthy': 'Upgrade Worthy Files', 
        'priority_replacements': 'Priority Replacements',
        'large_low_quality': 'Large Low Quality Files',
        'hdr_candidates': 'HDR Candidates',
        'audio_upgrade_candidates': 'Audio Upgrade Candidates',
        'legacy_content': 'Legacy Content'
    };
    
    modalTitle.textContent = titles[category] || 'Category Files';
    
    // Parse filesData if it's a string
    let files = filesData;
    if (typeof filesData === 'string') {
        try {
            files = JSON.parse(filesData);
        } catch (e) {
            console.error('Error parsing files data:', e);
            return;
        }
    }
    
    // Build content table
    let content = `
        <div class="modal-table-container">
            <table class="modal-table" style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="padding: 12px; border-bottom: 1px solid #ddd;">Title</th>
                        <th style="padding: 12px; border-bottom: 1px solid #ddd;">Score</th>
                        <th style="padding: 12px; border-bottom: 1px solid #ddd;">Size (MB)</th>
                        <th style="padding: 12px; border-bottom: 1px solid #ddd;">Formats</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    files.forEach(file => {
        const scoreClass = file.score >= 100 ? 'positive' : file.score >= 0 ? 'neutral' : 'negative';
        const scoreColor = file.score >= 100 ? '#28a745' : file.score >= 0 ? '#333' : '#dc3545';
        const sizeDisplay = file.size ? (file.size / 1024).toFixed(2) + ' GB' : 'N/A';
        
        content += `
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">${file.title}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; color: ${scoreColor}; font-weight: bold;">${file.score}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">${sizeDisplay}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">${file.formats || 'None'}</td>
            </tr>
        `;
    });
    
    content += `
                </tbody>
            </table>
        </div>
    `;
    
    modalContent.innerHTML = content;
    modal.style.display = 'block';
}

/**
 * Close category modal
 */
function closeCategoryModal() {
    const modal = document.getElementById('categoryModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('categoryModal');
    if (modal && event.target == modal) {
        modal.style.display = 'none';
    }
}

/**
 * Export chart as image
 */
function exportChart(chartId) {
    const chart = Chart.getChart(chartId);
    if (chart) {
        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `${chartId}_${new Date().toISOString().split('T')[0]}.png`;
        link.href = url;
        link.click();
    }
}

/**
 * Initialize dashboard data from embedded JSON
 */
function initializeDashboardData(data) {
    dashboardData = data;
}

/**
 * Update upgrade opportunities table based on selected limit
 */
function updateUpgradeTable() {
    const limitSelect = document.getElementById('upgradeLimit');
    const tableBody = document.getElementById('upgradeTableBody');
    
    if (!limitSelect || !tableBody) {
        console.warn('Upgrade table elements not found');
        return;
    }
    
    const limit = limitSelect.value;
    const allRows = tableBody.querySelectorAll('tr');
    const totalCount = allRows.length;
    
    console.log(`Upgrade table: limit=${limit}, totalCount=${totalCount}, allRows=`, allRows);
    
    // Update DataTable page length instead of manually hiding rows
    if ($.fn.DataTable && $.fn.DataTable.isDataTable('#upgradeTable')) {
        const table = $('#upgradeTable').DataTable();
        
        if (limit === 'all') {
            // Show all rows by setting page length to total count
            table.page.len(totalCount).draw();
        } else {
            // Set page length to the selected limit
            table.page.len(parseInt(limit)).draw();
        }
    }
}

/**
 * Handle clicks on score distribution pie chart
 */
function handleScoreDistributionClick(event, activeElements) {
    if (activeElements && activeElements.length > 0) {
        const clickedIndex = activeElements[0].index;
        const clickedLabel = scoreDistributionChart.data.labels[clickedIndex];
        
        // Only handle clicks on "Zero Scores" segment (index 1)
        if (clickedIndex === 1 && clickedLabel === 'Zero Scores') {
            toggleZeroScoresTable();
        }
    }
}

/**
 * Toggle zero scores table visibility
 */
function toggleZeroScoresTable() {
    const tableSection = document.getElementById('zeroScoresTableSection');
    if (!tableSection) {
        console.warn('Zero scores table section not found');
        return;
    }
    
    const isVisible = tableSection.style.display !== 'none';
    
    if (isVisible) {
        // Hide the table
        tableSection.style.display = 'none';
        
        // Update any toggle button text if present
        const toggleBtn = document.getElementById('zeroScoresToggleBtn');
        if (toggleBtn) {
            toggleBtn.textContent = 'Show Zero Scores Details';
        }
    } else {
        // Show the table
        tableSection.style.display = 'block';
        
        // Scroll to the table
        tableSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Update any toggle button text if present
        const toggleBtn = document.getElementById('zeroScoresToggleBtn');
        if (toggleBtn) {
            toggleBtn.textContent = 'Hide Zero Scores Details';
        }
        
        // Initialize DataTable if not already done
        const table = tableSection.querySelector('.zero-scores-table');
        if (table && $.fn.DataTable && !$.fn.DataTable.isDataTable(table)) {
            $(table).DataTable({
                pageLength: 25,
                dom: 'Bfrtip',
                buttons: ['csv', 'excel', 'pdf'],
                order: [[1, 'asc']], // Sort by title by default
                responsive: true
            });
        }
    }
}

/**
 * Smooth scroll to section
 */
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}