# Pages module for bass practice desktop app
from .dashboard import DashboardPage
from .practice import PracticePage
from .exercises import ExercisesPage
from .ear_training import EarTrainingPage
from .timing import TimingPage
from .quiz import QuizPage
from .songs import SongsPage
from .progress import ProgressPage
from .settings import SettingsPage

__all__ = [
    'DashboardPage', 'PracticePage', 'ExercisesPage', 'EarTrainingPage',
    'TimingPage', 'QuizPage', 'SongsPage', 'ProgressPage', 'SettingsPage'
]
