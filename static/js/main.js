// Main JavaScript file for Digital Portfolio

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(function(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        const counterElement = document.createElement('div');
        counterElement.className = 'text-muted small mt-1';
        counterElement.innerHTML = `<span class="current">0</span>/${maxLength} characters`;
        textarea.parentNode.appendChild(counterElement);

        const currentSpan = counterElement.querySelector('.current');
        
        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            currentSpan.textContent = currentLength;
            
            if (currentLength > maxLength * 0.9) {
                counterElement.classList.add('text-warning');
            } else {
                counterElement.classList.remove('text-warning');
            }
            
            if (currentLength === maxLength) {
                counterElement.classList.add('text-danger');
            } else {
                counterElement.classList.remove('text-danger');
            }
        });
    });

    // Image preview for file uploads
    const fileInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Remove existing preview
                    const existingPreview = input.parentNode.querySelector('.image-preview');
                    if (existingPreview) {
                        existingPreview.remove();
                    }
                    
                    // Create new preview
                    const preview = document.createElement('div');
                    preview.className = 'image-preview mt-2';
                    preview.innerHTML = `
                        <img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px;" alt="Preview">
                        <div class="text-muted small mt-1">Preview of selected image</div>
                    `;
                    input.parentNode.appendChild(preview);
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Search functionality for projects (if search input exists)
    const searchInput = document.querySelector('#project-search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                const searchTerm = searchInput.value.toLowerCase();
                const projectCards = document.querySelectorAll('.project-card');
                
                projectCards.forEach(function(card) {
                    const title = card.querySelector('.card-title').textContent.toLowerCase();
                    const description = card.querySelector('.card-text').textContent.toLowerCase();
                    
                    if (title.includes(searchTerm) || description.includes(searchTerm)) {
                        card.style.display = 'block';
                        card.parentElement.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                        card.parentElement.style.display = 'none';
                    }
                });
            }, 300);
        });
    }

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-delete') || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Copy to clipboard functionality
    window.copyToClipboard = function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                showToast('Copied to clipboard!', 'success');
            }).catch(function() {
                fallbackCopyToClipboard(text);
            });
        } else {
            fallbackCopyToClipboard(text);
        }
    };

    function fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showToast('Copied to clipboard!', 'success');
        } catch (err) {
            showToast('Failed to copy to clipboard', 'error');
        }
        document.body.removeChild(textArea);
    }

    // Toast notification system
    window.showToast = function(message, type = 'info') {
        const toastContainer = getOrCreateToastContainer();
        const toastId = 'toast-' + Date.now();
        const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
        
        const toastHTML = `
            <div id="${toastId}" class="toast ${bgClass} text-white" role="alert">
                <div class="toast-header ${bgClass} text-white border-0">
                    <strong class="me-auto">Notification</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    };

    function getOrCreateToastContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        return container;
    }

    // Back to top button
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopButton.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3 rounded-circle';
    backToTopButton.style.display = 'none';
    backToTopButton.style.zIndex = '1050';
    backToTopButton.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTopButton);

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });

    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Add loading states to forms
    const submitButtons = document.querySelectorAll('form button[type="submit"]');
    submitButtons.forEach(function(button) {
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                button.disabled = true;
                const originalHTML = button.innerHTML;
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                
                // Re-enable button after 10 seconds as fallback
                setTimeout(function() {
                    button.disabled = false;
                    button.innerHTML = originalHTML;
                }, 10000);
            });
        }
    });

    // Enhanced like button functionality
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const projectId = this.getAttribute('data-project-id');
            const icon = this.querySelector('i');
            const countElement = this.parentElement.querySelector('.like-count');
            
            // Add loading state
            icon.className = 'fas fa-spinner fa-spin';
            this.disabled = true;
            
            fetch(`/like_project/${projectId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                icon.className = 'fas fa-heart';
                this.disabled = false;
                
                if (data.liked) {
                    this.classList.remove('btn-outline-danger');
                    this.classList.add('btn-danger');
                    showToast('Project liked!', 'success');
                } else {
                    this.classList.remove('btn-danger');
                    this.classList.add('btn-outline-danger');
                    showToast('Like removed', 'info');
                }
                
                if (countElement) {
                    countElement.textContent = data.like_count;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                icon.className = 'fas fa-heart';
                this.disabled = false;
                showToast('Error updating like', 'error');
            });
        });
    });
});

// Utility functions
window.utils = {
    formatDate: function(dateString) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    },
    
    formatRelativeTime: function(dateString) {
        const now = new Date();
        const date = new Date(dateString);
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
        if (diffDays < 365) return `${Math.ceil(diffDays / 30)} months ago`;
        return `${Math.ceil(diffDays / 365)} years ago`;
    },
    
    truncateText: function(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength) + '...';
    }
};
