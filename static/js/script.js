/* ============================================
   DuoSentimen - JavaScript Utilities
   By Ahmad Saifulla
   ============================================ */

/**
 * Print a specific section of the page
 * @param {string} elementId - The ID of the element to print
 */
function printSection(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.error('Element not found:', elementId);
        return;
    }

    const clonedContent = element.cloneNode(true);
    const printWindow = window.open('', '_blank', 'width=900,height=700');

    printWindow.document.write(`
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <title>DuoSentimen - Cetak</title>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                * { font-family: 'Poppins', sans-serif; }
                body { padding: 30px; background: #fff; }
                .print-header { text-align: center; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 2px solid #667eea; }
                .print-header h2 { color: #1a1a2e; font-weight: 700; }
                .print-header p { color: #888; font-size: 13px; }
                table { width: 100%; }
                .table thead { background: #667eea; color: #fff; }
                .table thead th { padding: 10px; font-size: 12px; }
                .table tbody td { padding: 8px; font-size: 12px; border-bottom: 1px solid #eee; }
                .btn, .btn-print, .no-print { display: none !important; }
                img { max-width: 100%; }
                @media print { body { padding: 10px; } }
            </style>
        </head>
        <body>
            <div class="print-header">
                <h2>DuoSentimen</h2>
                <p>Analisis Sentimen Ulasan Aplikasi Duolingo - Dicetak pada ${new Date().toLocaleDateString('id-ID', { 
                    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
                    hour: '2-digit', minute: '2-digit'
                })}</p>
            </div>
            ${clonedContent.innerHTML}
        </body>
        </html>
    `);

    printWindow.document.close();

    printWindow.onload = function() {
        setTimeout(function() {
            printWindow.print();
            printWindow.close();
        }, 500);
    };
}

/**
 * Highlight the active navigation item based on current URL
 */
function highlightActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar .nav-item a');

    navLinks.forEach(function(link) {
        link.classList.remove('active');
        const href = link.getAttribute('href');

        if (href && currentPath === href) {
            link.classList.add('active');
        } else if (href && href !== '/dashboard' && currentPath.startsWith(href)) {
            link.classList.add('active');
        }
    });

    // Default to dashboard if no match
    if (!document.querySelector('.sidebar .nav-item a.active')) {
        const dashLink = document.querySelector('.sidebar .nav-item a[href="/dashboard"]');
        if (dashLink && currentPath.startsWith('/dashboard')) {
            dashLink.classList.add('active');
        }
    }
}

/**
 * Show loading overlay spinner
 */
function showLoading() {
    // Remove existing overlay if any
    hideLoading();

    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'spinner-overlay';
    overlay.innerHTML = `
        <div class="spinner-content">
            <div class="spinner-ring"></div>
            <div class="spinner-text">Memproses...</div>
        </div>
    `;
    document.body.appendChild(overlay);
}

/**
 * Hide loading overlay spinner
 */
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        overlay.style.transition = 'opacity 0.3s ease';
        setTimeout(function() {
            overlay.remove();
        }, 300);
    }
}

/**
 * Show a confirm dialog
 * @param {string} message - The confirmation message
 * @returns {boolean}
 */
function confirmAction(message) {
    return confirm(message);
}

/**
 * Auto-dismiss flash messages after a delay
 */
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });
}

/**
 * Add smooth entrance animation to elements
 */
function animateOnScroll() {
    const elements = document.querySelectorAll('.card, .stat-card');
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    elements.forEach(function(el) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });
}

/**
 * Initialize tooltips if Bootstrap is available
 */
function initTooltips() {
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(el) {
            return new bootstrap.Tooltip(el);
        });
    }
}

/* ============================================
   DOM Content Loaded
   ============================================ */
document.addEventListener('DOMContentLoaded', function() {
    highlightActiveNav();
    autoDismissAlerts();
    initTooltips();

    // Small delay to allow page to render first
    setTimeout(animateOnScroll, 100);
});
