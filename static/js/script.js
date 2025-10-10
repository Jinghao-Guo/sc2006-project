/* JavaScript for HDB Search Website */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize search functionality
    initializeSearch();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const suggestionsContainer = document.getElementById('search-suggestions');
    
    if (!searchInput || !suggestionsContainer) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Clear previous timeout
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        
        // Debounce search requests
        searchTimeout = setTimeout(() => {
            fetchSearchSuggestions(query);
        }, 300);
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            hideSuggestions();
        }
    });
    
    // Handle keyboard navigation
    searchInput.addEventListener('keydown', function(e) {
        const suggestions = suggestionsContainer.querySelectorAll('.suggestion-item');
        const currentActive = suggestionsContainer.querySelector('.suggestion-item.active');
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                navigateSuggestions(suggestions, currentActive, 'down');
                break;
            case 'ArrowUp':
                e.preventDefault();
                navigateSuggestions(suggestions, currentActive, 'up');
                break;
            case 'Enter':
                if (currentActive) {
                    e.preventDefault();
                    selectSuggestion(currentActive);
                }
                break;
            case 'Escape':
                hideSuggestions();
                break;
        }
    });
}

function fetchSearchSuggestions(query) {
    const suggestionsContainer = document.getElementById('search-suggestions');
    
    // Show loading state
    suggestionsContainer.innerHTML = '<div class="suggestion-item">Searching...</div>';
    showSuggestions();
    
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySuggestions(data);
        })
        .catch(error => {
            console.error('Search error:', error);
            suggestionsContainer.innerHTML = '<div class="suggestion-item text-muted">Search temporarily unavailable</div>';
        });
}

function displaySuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('search-suggestions');
    
    if (suggestions.length === 0) {
        suggestionsContainer.innerHTML = '<div class="suggestion-item text-muted">No suggestions found</div>';
        return;
    }
    
    const suggestionHTML = suggestions.map(flat => `
        <div class="suggestion-item" data-flat-id="${flat.id}" data-suggestion="${flat.block} ${flat.street_name}">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>Block ${flat.block}, ${flat.street_name}</strong><br>
                    <small class="text-muted">${flat.town} • ${flat.flat_type}</small>
                </div>
                <div class="text-end">
                    <strong class="text-success">$${Number(flat.resale_price).toLocaleString()}</strong>
                </div>
            </div>
        </div>
    `).join('');
    
    suggestionsContainer.innerHTML = suggestionHTML;
    
    // Add click handlers to suggestions
    suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
        item.addEventListener('click', function() {
            selectSuggestion(this);
        });
        
        item.addEventListener('mouseenter', function() {
            // Remove active class from others
            suggestionsContainer.querySelectorAll('.suggestion-item').forEach(s => s.classList.remove('active'));
            // Add active class to current
            this.classList.add('active');
        });
    });
}

function navigateSuggestions(suggestions, currentActive, direction) {
    if (suggestions.length === 0) return;
    
    // Remove current active
    if (currentActive) {
        currentActive.classList.remove('active');
    }
    
    let nextActive;
    
    if (!currentActive) {
        // No current selection, select first or last
        nextActive = direction === 'down' ? suggestions[0] : suggestions[suggestions.length - 1];
    } else {
        // Find current index
        const currentIndex = Array.from(suggestions).indexOf(currentActive);
        
        if (direction === 'down') {
            nextActive = suggestions[currentIndex + 1] || suggestions[0];
        } else {
            nextActive = suggestions[currentIndex - 1] || suggestions[suggestions.length - 1];
        }
    }
    
    nextActive.classList.add('active');
    nextActive.scrollIntoView({ block: 'nearest' });
}

function selectSuggestion(suggestionElement) {
    const flatId = suggestionElement.getAttribute('data-flat-id');
    const suggestionText = suggestionElement.getAttribute('data-suggestion');
    
    if (flatId) {
        // Navigate to flat detail page
        window.location.href = `/flat/${flatId}`;
    } else if (suggestionText) {
        // Fill search input and hide suggestions
        document.getElementById('search-input').value = suggestionText;
        hideSuggestions();
        
        // Optionally trigger search
        document.querySelector('.search-form').submit();
    }
}

function showSuggestions() {
    const suggestionsContainer = document.getElementById('search-suggestions');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'block';
    }
}

function hideSuggestions() {
    const suggestionsContainer = document.getElementById('search-suggestions');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
        // Remove all active states
        suggestionsContainer.querySelectorAll('.suggestion-item').forEach(s => s.classList.remove('active'));
    }
}

// Animation initialization
function initializeAnimations() {
    // Add fade-in animation to cards when they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all cards
    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });
}

// Utility functions
function formatPrice(price) {
    return new Intl.NumberFormat('en-SG', {
        style: 'currency',
        currency: 'SGD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(price);
}

function formatPricePerSqm(price, area) {
    const pricePerSqm = price / area;
    return new Intl.NumberFormat('en-SG', {
        style: 'currency',
        currency: 'SGD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(pricePerSqm);
}

// Search form utilities
function clearForm() {
    document.getElementById('search-input').value = '';
    document.getElementById('town-select').value = '';
    document.getElementById('flat-type-select').value = '';
    hideSuggestions();
}

// Loading state management
function showLoading(element) {
    if (element) {
        element.classList.add('loading');
        element.disabled = true;
    }
}

function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

// Error handling
function showError(message, container) {
    const alertHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    if (container) {
        container.innerHTML = alertHTML + container.innerHTML;
    } else {
        // Default to main container
        const main = document.querySelector('main.container');
        if (main) {
            main.innerHTML = alertHTML + main.innerHTML;
        }
    }
}

// Local storage utilities for user preferences
function saveSearchPreferences() {
    const preferences = {
        town: document.getElementById('town-select')?.value || '',
        flatType: document.getElementById('flat-type-select')?.value || ''
    };
    
    localStorage.setItem('hdbSearchPreferences', JSON.stringify(preferences));
}

function loadSearchPreferences() {
    try {
        const preferences = JSON.parse(localStorage.getItem('hdbSearchPreferences') || '{}');
        
        if (preferences.town && document.getElementById('town-select')) {
            document.getElementById('town-select').value = preferences.town;
        }
        
        if (preferences.flatType && document.getElementById('flat-type-select')) {
            document.getElementById('flat-type-select').value = preferences.flatType;
        }
    } catch (error) {
        console.error('Error loading search preferences:', error);
    }
}

// Initialize preferences on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSearchPreferences();
    
    // Save preferences when form is submitted
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', saveSearchPreferences);
    }
});