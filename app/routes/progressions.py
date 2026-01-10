from flask import Blueprint, render_template, request
from ..models import db, Song, ChordProgression

bp = Blueprint('progressions', __name__)

@bp.route('/progressions')
def chord_progressions():
    """Browse chord progressions."""
    genre = request.args.get('genre', '')
    
    query = ChordProgression.query
    
    if genre:
        query = query.filter_by(genre=genre)
    
    progressions = query.order_by(ChordProgression.difficulty_level).all()
    
    # Get unique genres
    genres = db.session.query(ChordProgression.genre).distinct().all()
    genres = [g[0] for g in genres if g[0]]
    
    return render_template('chord_progressions.html',
        progressions=progressions,
        genres=genres,
        current_genre=genre
    )


@bp.route('/progressions/<int:progression_id>')
def progression_detail(progression_id):
    """View chord progression details."""
    progression = ChordProgression.query.get_or_404(progression_id)
    
    # Find songs using this progression
    related_songs = Song.query.filter(
        Song.chord_progression.ilike(f'%{progression.numerals}%')
    ).all()
    
    return render_template('progression_detail.html',
        progression=progression,
        related_songs=related_songs
    )
