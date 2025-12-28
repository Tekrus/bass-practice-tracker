"""
Song suggestion service using free LLM APIs.
Suggests new songs to learn based on library and skills that need training.
"""
import os
import json
import urllib.request
import urllib.error
from .models import Song, Progress


# Available LLM providers and their models
LLM_PROVIDERS = {
    'ollama': {
        'name': 'Ollama (Local)',
        'models': [],  # Populated dynamically
        'env_key': None,  # No API key needed
        'url': 'http://localhost:11434/api/generate',
        'local': True,
    },
    'groq': {
        'name': 'Groq',
        'models': [
            {'id': 'llama-3.3-70b-versatile', 'name': 'Llama 3.3 70B'},
            {'id': 'llama-3.1-8b-instant', 'name': 'Llama 3.1 8B'},
            {'id': 'gemma2-9b-it', 'name': 'Gemma 2 9B'},
            {'id': 'mixtral-8x7b-32768', 'name': 'Mixtral 8x7B'},
        ],
        'env_key': 'GROQ_API_KEY',
        'url': 'https://api.groq.com/openai/v1/chat/completions',
    },
    'gemini': {
        'name': 'Google Gemini',
        'models': [
            {'id': 'gemini-2.0-flash-lite', 'name': 'Gemini 2.0 Flash Lite'},
            {'id': 'gemini-1.5-flash', 'name': 'Gemini 1.5 Flash'},
            {'id': 'gemini-1.5-flash-8b', 'name': 'Gemini 1.5 Flash 8B'},
        ],
        'env_key': 'GEMINI_API_KEY',
    },
    'openrouter': {
        'name': 'OpenRouter',
        'models': [
            {'id': 'meta-llama/llama-3.2-3b-instruct:free', 'name': 'Llama 3.2 3B (Free)'},
            {'id': 'qwen/qwen-2.5-72b-instruct:free', 'name': 'Qwen 2.5 72B (Free)'},
            {'id': 'google/gemma-2-9b-it:free', 'name': 'Gemma 2 9B (Free)'},
            {'id': 'mistralai/mistral-7b-instruct:free', 'name': 'Mistral 7B (Free)'},
        ],
        'env_key': 'OPENROUTER_API_KEY',
        'url': 'https://openrouter.ai/api/v1/chat/completions',
    },
}


def get_ollama_models():
    """Get list of models available in local Ollama instance."""
    try:
        req = urllib.request.Request(
            'http://localhost:11434/api/tags',
            method='GET'
        )
        with urllib.request.urlopen(req, timeout=2) as response:
            result = json.loads(response.read().decode('utf-8'))
            models = []
            for model in result.get('models', []):
                name = model.get('name', '')
                # Clean up model name for display
                display_name = name.split(':')[0].replace('-', ' ').title()
                models.append({'id': name, 'name': display_name})
            return models
    except Exception:
        return []


def is_ollama_running():
    """Check if Ollama is running locally."""
    try:
        req = urllib.request.Request(
            'http://localhost:11434/api/tags',
            method='GET'
        )
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def get_available_providers():
    """Get list of providers with their API keys configured."""
    available = []
    for provider_id, provider in LLM_PROVIDERS.items():
        # Handle local Ollama provider
        if provider.get('local'):
            ollama_running = is_ollama_running()
            ollama_models = get_ollama_models() if ollama_running else []
            available.append({
                'id': provider_id,
                'name': provider['name'],
                'models': ollama_models,
                'configured': ollama_running and len(ollama_models) > 0,
                'env_key': None,
                'local': True,
                'status': 'running' if ollama_running else 'not running',
            })
            continue
        
        env_key = provider['env_key']
        # Also check alternate key names
        has_key = bool(os.environ.get(env_key))
        if provider_id == 'gemini' and not has_key:
            has_key = bool(os.environ.get('GOOGLE_API_KEY'))
        
        available.append({
            'id': provider_id,
            'name': provider['name'],
            'models': provider['models'],
            'configured': has_key,
            'env_key': env_key,
        })
    return available


def build_library_context(songs):
    """Build a summary of the current song library."""
    if not songs:
        return "The user's song library is empty. They are just starting out."
    
    genres = {}
    difficulties = []
    artists = set()
    mastery_levels = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    song_list = []
    for song in songs:
        song_info = f"- {song.title}"
        if song.artist:
            song_info += f" by {song.artist}"
            artists.add(song.artist)
        if song.genre:
            genres[song.genre] = genres.get(song.genre, 0) + 1
            song_info += f" ({song.genre})"
        if song.difficulty_level:
            difficulties.append(song.difficulty_level)
            song_info += f" [difficulty: {song.difficulty_level}/10]"
        song_info += f" [mastery: {song.mastery_level}/5]"
        mastery_levels[song.mastery_level] = mastery_levels.get(song.mastery_level, 0) + 1
        song_list.append(song_info)
    
    avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 5
    
    context = f"""Current Song Library ({len(songs)} songs):
{chr(10).join(song_list)}

Library Statistics:
- Genres: {', '.join(f'{g} ({c})' for g, c in genres.items()) if genres else 'None specified'}
- Average difficulty: {avg_difficulty:.1f}/10
- Artists covered: {', '.join(list(artists)[:10]) if artists else 'None specified'}
- Mastery distribution: New({mastery_levels[0]}), Learning({mastery_levels[1]+mastery_levels[2]}), Intermediate({mastery_levels[3]}), Mastered({mastery_levels[4]+mastery_levels[5]})
"""
    return context


def build_skills_context(progress_data):
    """Build a summary of skills that need training."""
    if not progress_data:
        return "No skill progress data available yet. The user is a beginner."
    
    skills = []
    weakest_skills = []
    
    for p in progress_data:
        skill_pct = p.skill_level * 100
        skills.append(f"- {p.category}: {skill_pct:.0f}% (exercises completed: {p.exercises_completed})")
        if skill_pct < 50:
            weakest_skills.append(p.category)
    
    context = f"""Skill Progress:
{chr(10).join(skills)}

Skills needing most work: {', '.join(weakest_skills) if weakest_skills else 'All skills are progressing well'}
"""
    return context


def build_prompt(songs, progress_data, level=None, genre=None, custom_instructions=None):
    """Build the prompt for song suggestion."""
    library_context = build_library_context(songs)
    skills_context = build_skills_context(progress_data)
    
    # Build user preferences section
    preferences = []
    if level:
        level_descriptions = {
            1: "absolute beginner (simple root notes, slow tempo, easy rhythms)",
            2: "beginner (basic patterns, moderate tempo)",
            3: "intermediate (more complex patterns, varied rhythms)",
            4: "advanced (challenging techniques, faster tempo, complex bass lines)",
            5: "expert (virtuoso level, slapping, complex jazz/fusion lines)"
        }
        level_desc = level_descriptions.get(level, f"difficulty level {level}/5")
        preferences.append(f"- Difficulty level: {level}/5 ({level_desc})")
    
    if genre:
        preferences.append(f"- Genre: {genre}")
    
    preferences_text = ""
    if preferences:
        preferences_text = f"""
User Preferences:
{chr(10).join(preferences)}
"""
    
    custom_text = ""
    if custom_instructions:
        custom_text = f"""
Additional User Instructions:
{custom_instructions}
"""
    
    return f"""You are a bass guitar teacher helping a student find their next song to learn.
Based on their current song library, skill progress, and preferences, suggest ONE specific song they should learn next.

{library_context}

{skills_context}
{preferences_text}{custom_text}
Requirements for your suggestion:
1. The song should be a REAL, well-known song with bass guitar (not a made-up song)
2. It should match the user's requested difficulty level and genre preferences if specified
3. It should help them practice skills they need to improve
4. Consider variety - don't suggest songs too similar to what they already have
5. Pay special attention to any custom instructions the user provided (key, scale, technique, feeling, etc.)

Respond in the following JSON format only (no markdown, no code blocks):
{{
    "title": "Song Title",
    "artist": "Artist Name",
    "genre": "genre",
    "difficulty_level": 5,
    "key_signature": "C",
    "tempo_bpm": 120,
    "reason": "A 2-3 sentence explanation of why this song is a great next choice, mentioning specific skills it will help develop and how it connects to their current learning journey."
}}"""


def call_openai_compatible_api(url, api_key, model, prompt, extra_headers=None):
    """Call an OpenAI-compatible API (Groq, OpenRouter, etc.)."""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    if extra_headers:
        headers.update(extra_headers)
    
    data = json.dumps({
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.7,
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result['choices'][0]['message']['content']


def call_gemini_api(api_key, model, prompt):
    """Call Google Gemini API."""
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'
    
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        'contents': [{'parts': [{'text': prompt}]}]
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result['candidates'][0]['content']['parts'][0]['text']


def call_ollama_api(model, prompt):
    """Call local Ollama API."""
    url = 'http://localhost:11434/api/generate'
    
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        'model': model,
        'prompt': prompt,
        'stream': False,
        'options': {
            'temperature': 0.7,
        }
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    # Longer timeout for local models which can be slower
    with urllib.request.urlopen(req, timeout=120) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result['response']


def parse_response(response_text):
    """Parse the LLM response into a suggestion dict."""
    response_text = response_text.strip()
    
    # Clean up response - remove markdown code blocks if present
    if response_text.startswith('```'):
        lines = response_text.split('\n')
        lines = [l for l in lines if not l.strip().startswith('```')]
        response_text = '\n'.join(lines)
    
    suggestion = json.loads(response_text)
    
    # Validate required fields
    required = ['title', 'artist', 'reason']
    for field in required:
        if field not in suggestion:
            raise ValueError(f'Missing required field: {field}')
    
    return suggestion


def generate_song_suggestion(provider_id='ollama', model_id=None, level=None, genre=None, custom_instructions=None):
    """
    Generate a song suggestion using the specified LLM provider.
    
    Args:
        provider_id: The LLM provider to use (ollama, groq, gemini, openrouter)
        model_id: The specific model to use
        level: Difficulty level 1-5 (optional)
        genre: Preferred genre (optional)
        custom_instructions: Custom instructions like key, scale, technique, feeling (optional)
    
    Returns dict with song suggestion and reason, or error.
    """
    if provider_id not in LLM_PROVIDERS:
        return {
            'success': False,
            'error': f'Unknown provider: {provider_id}',
            'suggestion': None
        }
    
    provider = LLM_PROVIDERS[provider_id]
    
    api_key = None
    
    # Handle local Ollama provider
    if provider.get('local'):
        if not is_ollama_running():
            return {
                'success': False,
                'error': 'Ollama is not running. Start Ollama with "ollama serve" or download from https://ollama.ai',
                'suggestion': None
            }
        ollama_models = get_ollama_models()
        if not ollama_models:
            return {
                'success': False,
                'error': 'No models found in Ollama. Pull a model with "ollama pull llama3.2" or "ollama pull mistral"',
                'suggestion': None
            }
        if not model_id:
            model_id = ollama_models[0]['id']
    else:
        # Get API key for cloud providers
        api_key = os.environ.get(provider['env_key'])
        if provider_id == 'gemini' and not api_key:
            api_key = os.environ.get('GOOGLE_API_KEY')
        
        if not api_key:
            return {
                'success': False,
                'error': f'{provider["env_key"]} environment variable not set. Please set your API key to use {provider["name"]}.',
                'suggestion': None
            }
        
        # Get model (use first available if not specified)
        if not model_id:
            model_id = provider['models'][0]['id']
    
    # Get current library and progress
    songs = Song.query.all()
    progress_data = Progress.query.all()
    prompt = build_prompt(songs, progress_data, level=level, genre=genre, custom_instructions=custom_instructions)
    
    try:
        if provider_id == 'ollama':
            response_text = call_ollama_api(model_id, prompt)
        elif provider_id == 'gemini':
            response_text = call_gemini_api(api_key, model_id, prompt)
        elif provider_id == 'openrouter':
            extra_headers = {'HTTP-Referer': 'http://localhost:5000', 'X-Title': 'Bass Practice'}
            response_text = call_openai_compatible_api(
                provider['url'], api_key, model_id, prompt, extra_headers
            )
        else:  # groq and other OpenAI-compatible APIs
            response_text = call_openai_compatible_api(
                provider['url'], api_key, model_id, prompt
            )
        
        suggestion = parse_response(response_text)
        
        return {
            'success': True,
            'error': None,
            'suggestion': suggestion
        }
        
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        if e.code == 429 or 'rate' in error_body.lower() or 'quota' in error_body.lower():
            return {
                'success': False,
                'error': 'Rate limit reached. Please wait a moment and try again, or try a different model/provider.',
                'suggestion': None
            }
        if e.code == 401 or e.code == 403:
            return {
                'success': False,
                'error': f'Invalid API key for {provider["name"]}. Please check your {provider["env_key"]}.',
                'suggestion': None
            }
        return {
            'success': False,
            'error': f'API error ({e.code}): {error_body[:200] if error_body else str(e)}',
            'suggestion': None
        }
    except urllib.error.URLError as e:
        if provider_id == 'ollama':
            return {
                'success': False,
                'error': 'Cannot connect to Ollama. Make sure it is running with "ollama serve".',
                'suggestion': None
            }
        return {
            'success': False,
            'error': f'Connection error: {str(e)}',
            'suggestion': None
        }
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Failed to parse AI response. The model may not have returned valid JSON. Try a different model.',
            'suggestion': None
        }
    except Exception as e:
        error_msg = str(e)
        if 'timed out' in error_msg.lower():
            return {
                'success': False,
                'error': 'Request timed out. Local models can be slow - try a smaller model or wait longer.',
                'suggestion': None
            }
        return {
            'success': False,
            'error': f'Error generating suggestion: {error_msg}',
            'suggestion': None
        }
