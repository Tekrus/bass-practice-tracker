// Practice song buttons
document.querySelectorAll('.practice-song-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const songId = this.dataset.songId;
        const quality = this.dataset.quality;

        const formData = new FormData();
        formData.append('quality', quality);

        fetch(`/songs/${songId}/practice`, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
    });
});

// Song suggestion functionality
let currentSuggestion = null;
let isLoadingSuggestion = false;
let providers = [];

// Load providers when page loads
fetch('/songs/providers')
    .then(response => response.json())
    .then(data => {
        providers = data.providers;
        populateProviderDropdown();
    });

function populateProviderDropdown() {
    const providerSelect = document.getElementById('provider-select');
    if (!providerSelect) return;

    providerSelect.innerHTML = '';

    providers.forEach(provider => {
        const option = document.createElement('option');
        option.value = provider.id;
        let label = provider.name;
        if (!provider.configured) {
            if (provider.local) {
                label += provider.status === 'not running' ? ' (not running)' : ' (no models)';
            } else {
                label += ' (no API key)';
            }
        }
        option.textContent = label;
        option.disabled = !provider.configured;
        providerSelect.appendChild(option);
    });

    // Select first configured provider (prefer local Ollama if available)
    const configured = providers.find(p => p.configured);
    if (configured) {
        providerSelect.value = configured.id;
        updateModelDropdown(configured.id);
    } else {
        showApiKeyWarning();
    }
}

function updateModelDropdown(providerId) {
    const modelSelect = document.getElementById('model-select');
    if (!modelSelect) return;

    const provider = providers.find(p => p.id === providerId);

    modelSelect.innerHTML = '';

    if (provider && provider.models) {
        provider.models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = model.name;
            modelSelect.appendChild(option);
        });
    }

    // Show/hide API key warning
    if (provider && !provider.configured) {
        showApiKeyWarning(provider);
    } else {
        const warning = document.getElementById('api-key-warning');
        if (warning) warning.style.display = 'none';
    }
}

function showApiKeyWarning(provider) {
    const warning = document.getElementById('api-key-warning');
    const text = document.getElementById('api-key-warning-text');
    if (!warning || !text) return;

    if (provider) {
        if (provider.local) {
            if (provider.status === 'not running') {
                text.innerHTML = 'Ollama is not running. <a href="https://ollama.ai" target="_blank">Download Ollama</a> and run "ollama serve".';
            } else {
                text.textContent = 'No models found. Run "ollama pull llama3.2" or "ollama pull mistral" to download a model.';
            }
        } else {
            text.textContent = `Set ${provider.env_key} environment variable to use ${provider.name}.`;
        }
    } else {
        text.innerHTML = 'No providers configured. Install <a href="https://ollama.ai" target="_blank">Ollama</a> for local models, or set GROQ_API_KEY for free cloud API.';
    }
    warning.style.display = 'block';
}

const providerSelect = document.getElementById('provider-select');
if (providerSelect) {
    providerSelect.addEventListener('change', function () {
        updateModelDropdown(this.value);
    });
}

// Handle genre "Other" selection
const genreSelect = document.getElementById('genre-select');
if (genreSelect) {
    genreSelect.addEventListener('change', function () {
        const customGenreInput = document.getElementById('custom-genre');
        if (this.value === 'other') {
            customGenreInput.disabled = false;
            customGenreInput.focus();
        } else {
            customGenreInput.disabled = true;
            customGenreInput.value = '';
        }
    });
}

const suggestSongBtn = document.getElementById('suggest-song-btn');
if (suggestSongBtn) {
    suggestSongBtn.addEventListener('click', function () {
        if (isLoadingSuggestion) return;
        document.getElementById('suggestion-container').style.display = 'block';
    });
}

const generateBtn = document.getElementById('generate-btn');
if (generateBtn) generateBtn.addEventListener('click', getSuggestion);

const anotherBtn = document.getElementById('another-btn');
if (anotherBtn) anotherBtn.addEventListener('click', getSuggestion);

function hideSuggestion() {
    const container = document.getElementById('suggestion-container');
    if (container) container.style.display = 'none';
}

function getSuggestion() {
    const provider = document.getElementById('provider-select').value;
    const model = document.getElementById('model-select').value;
    const level = document.getElementById('level-select').value;
    let genre = document.getElementById('genre-select').value;
    const customGenre = document.getElementById('custom-genre').value.trim();
    const customInstructions = document.getElementById('custom-instructions').value.trim();

    // Use custom genre if "other" is selected
    if (genre === 'other' && customGenre) {
        genre = customGenre;
    } else if (genre === 'other') {
        genre = '';  // Clear if no custom genre provided
    }

    if (!provider) {
        document.getElementById('suggestion-error-text').textContent = 'Please select a provider.';
        document.getElementById('suggestion-error').style.display = 'block';
        return;
    }

    // Prevent multiple simultaneous requests
    if (isLoadingSuggestion) return;
    isLoadingSuggestion = true;

    // Disable buttons while loading
    const suggestBtn = document.getElementById('suggest-song-btn');
    const genBtn = document.getElementById('generate-btn');
    if (suggestBtn) suggestBtn.disabled = true;
    if (genBtn) genBtn.disabled = true;

    // Show loading, hide content and error
    document.getElementById('suggestion-loading').style.display = 'block';
    document.getElementById('suggestion-content').style.display = 'none';
    document.getElementById('suggestion-error').style.display = 'none';

    // Build URL with all parameters
    let url = `/songs/suggest?provider=${encodeURIComponent(provider)}&model=${encodeURIComponent(model)}`;
    if (level) {
        url += `&level=${encodeURIComponent(level)}`;
    }
    if (genre) {
        url += `&genre=${encodeURIComponent(genre)}`;
    }
    if (customInstructions) {
        url += `&custom_instructions=${encodeURIComponent(customInstructions)}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            isLoadingSuggestion = false;
            if (suggestBtn) suggestBtn.disabled = false;
            if (genBtn) genBtn.disabled = false;
            document.getElementById('suggestion-loading').style.display = 'none';

            if (data.success && data.suggestion) {
                currentSuggestion = data.suggestion;
                displaySuggestion(data.suggestion);
                document.getElementById('suggestion-content').style.display = 'block';
            } else {
                document.getElementById('suggestion-error-text').textContent =
                    data.error || 'Failed to get suggestion. Please try again.';
                document.getElementById('suggestion-error').style.display = 'block';
            }
        })
        .catch(error => {
            isLoadingSuggestion = false;
            if (suggestBtn) suggestBtn.disabled = false;
            if (genBtn) genBtn.disabled = false;
            document.getElementById('suggestion-loading').style.display = 'none';
            document.getElementById('suggestion-error-text').textContent =
                'Network error. Please check your connection and try again.';
            document.getElementById('suggestion-error').style.display = 'block';
        });
}

function displaySuggestion(suggestion) {
    document.getElementById('suggestion-title').textContent = suggestion.title;
    document.getElementById('suggestion-artist').textContent = suggestion.artist ? `by ${suggestion.artist}` : '';
    document.getElementById('suggestion-reason').textContent = suggestion.reason;

    // Genre badge
    const genreBadge = document.getElementById('suggestion-genre');
    if (suggestion.genre) {
        genreBadge.textContent = suggestion.genre;
        genreBadge.style.display = 'inline-block';
    } else {
        genreBadge.style.display = 'none';
    }

    // Difficulty badge
    const diffBadge = document.getElementById('suggestion-difficulty');
    if (suggestion.difficulty_level) {
        diffBadge.innerHTML = `<i class="bi bi-bar-chart"></i> Level ${suggestion.difficulty_level}`;
        diffBadge.style.display = 'inline-block';
    } else {
        diffBadge.style.display = 'none';
    }

    // Key badge
    const keyBadge = document.getElementById('suggestion-key');
    if (suggestion.key_signature) {
        keyBadge.innerHTML = `<i class="bi bi-music-note"></i> ${suggestion.key_signature}`;
        keyBadge.style.display = 'inline-block';
    } else {
        keyBadge.style.display = 'none';
    }

    // Tempo badge
    const tempoBadge = document.getElementById('suggestion-tempo');
    if (suggestion.tempo_bpm) {
        tempoBadge.innerHTML = `<i class="bi bi-speedometer2"></i> ${suggestion.tempo_bpm} BPM`;
        tempoBadge.style.display = 'inline-block';
    } else {
        tempoBadge.style.display = 'none';
    }
}

const addSuggestionBtn = document.getElementById('add-suggestion-btn');
if (addSuggestionBtn) {
    addSuggestionBtn.addEventListener('click', function () {
        if (!currentSuggestion) return;

        this.disabled = true;
        this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Adding...';

        fetch('/songs/add-suggestion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentSuggestion)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Failed to add song. Please try again.');
                    this.disabled = false;
                    this.innerHTML = '<i class="bi bi-plus-lg"></i> Add to Library';
                }
            })
            .catch(error => {
                alert('Network error. Please try again.');
                this.disabled = false;
                this.innerHTML = '<i class="bi bi-plus-lg"></i> Add to Library';
            });
    });
}
