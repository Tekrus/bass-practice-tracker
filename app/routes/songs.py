from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ..models import db, Song
from ..song_manager import generate_daily_song_playlist, update_song_mastery
from ..song_suggestion import generate_song_suggestion, get_available_providers

bp = Blueprint('songs', __name__)

@bp.route('/songs')
def songs():
    """Browse and manage songs."""
    genre = request.args.get('genre', '')
    mastery = request.args.get('mastery', type=int)
    search = request.args.get('search', '')
    
    query = Song.query
    
    if genre:
        query = query.filter_by(genre=genre)
    if mastery is not None:
        query = query.filter_by(mastery_level=mastery)
    if search:
        query = query.filter(
            db.or_(
                Song.title.ilike(f'%{search}%'),
                Song.artist.ilike(f'%{search}%')
            )
        )
    
    songs = query.order_by(Song.mastery_level, Song.title).all()
    
    # Get daily playlist
    playlist = generate_daily_song_playlist()
    
    # Get unique genres
    genres = db.session.query(Song.genre).distinct().all()
    genres = [g[0] for g in genres if g[0]]
    
    return render_template('songs.html',
        songs=songs,
        playlist=playlist,
        genres=genres,
        current_genre=genre,
        current_mastery=mastery,
        search=search
    )


@bp.route('/songs/add', methods=['GET', 'POST'])
def add_song():
    """Add a new song to practice."""
    if request.method == 'POST':
        song = Song(
            title=request.form['title'],
            artist=request.form.get('artist', ''),
            genre=request.form.get('genre', ''),
            difficulty_level=request.form.get('difficulty_level', type=int) or 5,
            key_signature=request.form.get('key_signature', ''),
            tempo_bpm=request.form.get('tempo_bpm', type=int),
            youtube_url=request.form.get('youtube_url', ''),
            practice_notes=request.form.get('practice_notes', '')
        )
        db.session.add(song)
        db.session.commit()
        
        flash(f'Added "{song.title}" to your song library!', 'success')
        return redirect(url_for('songs.songs'))
    
    return render_template('song_form.html', song=None)


@bp.route('/songs/<int:song_id>/edit', methods=['GET', 'POST'])
def edit_song(song_id):
    """Edit an existing song."""
    song = Song.query.get_or_404(song_id)
    
    if request.method == 'POST':
        song.title = request.form['title']
        song.artist = request.form.get('artist', '')
        song.genre = request.form.get('genre', '')
        song.difficulty_level = request.form.get('difficulty_level', type=int) or 5
        song.key_signature = request.form.get('key_signature', '')
        song.tempo_bpm = request.form.get('tempo_bpm', type=int)
        song.youtube_url = request.form.get('youtube_url', '')
        song.practice_notes = request.form.get('practice_notes', '')
        
        db.session.commit()
        flash('Song updated!', 'success')
        return redirect(url_for('songs.songs'))
    
    return render_template('song_form.html', song=song)


@bp.route('/songs/<int:song_id>/practice', methods=['POST'])
def practice_song(song_id):
    """Record a song practice session."""
    song = Song.query.get_or_404(song_id)
    quality = request.form.get('quality', type=int) or 3
    
    update_song_mastery(song, quality)
    
    return jsonify({
        'success': True,
        'mastery_level': song.mastery_level,
        'practice_count': song.practice_count
    })


@bp.route('/songs/<int:song_id>/delete', methods=['POST'])
def delete_song(song_id):
    """Delete a song."""
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    
    flash(f'Deleted "{song.title}" from your library.', 'info')
    return redirect(url_for('songs.songs'))


@bp.route('/songs/suggest')
def suggest_song():
    """Get an AI-powered song suggestion based on library and skills."""
    provider = request.args.get('provider', 'groq')
    model = request.args.get('model', None)
    level = request.args.get('level', type=int)
    genre = request.args.get('genre', None)
    custom_instructions = request.args.get('custom_instructions', None)
    
    result = generate_song_suggestion(
        provider_id=provider, 
        model_id=model,
        level=level,
        genre=genre,
        custom_instructions=custom_instructions
    )
    return jsonify(result)


@bp.route('/songs/providers')
def get_llm_providers():
    """Get available LLM providers and their models."""
    providers = get_available_providers()
    return jsonify({'providers': providers})


@bp.route('/songs/add-suggestion', methods=['POST'])
def add_suggested_song():
    """Add a suggested song to the library."""
    data = request.get_json()
    
    song = Song(
        title=data.get('title', ''),
        artist=data.get('artist', ''),
        genre=data.get('genre', ''),
        difficulty_level=data.get('difficulty_level', 5),
        key_signature=data.get('key_signature', ''),
        tempo_bpm=data.get('tempo_bpm'),
        practice_notes=data.get('reason', '')  # Store reason as practice notes
    )
    db.session.add(song)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'song_id': song.id,
        'message': f'Added "{song.title}" to your library!'
    })
