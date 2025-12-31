"""
Main application window for Bass Practice desktop app.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QListWidget, QListWidgetItem, QLabel, QFrame, QSplitter, QStatusBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

from .styles import DARK_STYLE
from .pages.dashboard import DashboardPage
from .pages.practice import PracticePage
from .pages.exercises import ExercisesPage
from .pages.ear_training import EarTrainingPage
from .pages.timing import TimingPage
from .pages.quiz import QuizPage
from .pages.songs import SongsPage
from .pages.progress import ProgressPage
from .pages.settings import SettingsPage


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""
    
    def __init__(self, audio_engine=None, db=None):
        super().__init__()
        
        self.audio_engine = audio_engine
        self.db = db
        
        self.setWindowTitle("Bass Practice")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(DARK_STYLE)
        
        self._setup_ui()
        self._setup_status_bar()
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self._create_sidebar()
        layout.addWidget(sidebar)
        
        # Create page stack
        self.page_stack = QStackedWidget()
        self._create_pages()
        layout.addWidget(self.page_stack, 1)
    
    def _create_sidebar(self) -> QWidget:
        """Create the navigation sidebar."""
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #16213e;")
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # App title
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #0f3460; padding: 20px;")
        title_layout = QVBoxLayout(title_frame)
        
        title = QLabel("Bass Practice")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #e94560;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Desktop")
        subtitle.setStyleSheet("color: #888;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_frame)
        
        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setSpacing(2)
        
        # Navigation items
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Practice", "practice"),
            ("Exercises", "exercises"),
            ("Ear Training", "ear_training"),
            ("Timing", "timing"),
            ("Quiz", "quiz"),
            ("Songs", "songs"),
            ("Progress", "progress"),
            ("Settings", "settings"),
        ]
        
        for name, page_id in nav_items:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, page_id)
            item.setSizeHint(QSize(200, 45))
            self.nav_list.addItem(item)
        
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        self.nav_list.setCurrentRow(0)
        
        layout.addWidget(self.nav_list, 1)
        
        # Audio status indicator
        self.audio_status = QLabel("Audio: Initializing...")
        self.audio_status.setStyleSheet("color: #888; padding: 15px;")
        layout.addWidget(self.audio_status)
        
        return sidebar
    
    def _create_pages(self):
        """Create all page widgets."""
        self.pages = {
            'dashboard': DashboardPage(self.db),
            'practice': PracticePage(self.audio_engine, self.db),
            'exercises': ExercisesPage(self.db),
            'ear_training': EarTrainingPage(self.audio_engine, self.db),
            'timing': TimingPage(self.audio_engine, self.db),
            'quiz': QuizPage(self.db),
            'songs': SongsPage(self.db),
            'progress': ProgressPage(self.db),
            'settings': SettingsPage(self.audio_engine, self.db),
        }
        
        for page in self.pages.values():
            self.page_stack.addWidget(page)
    
    def _on_nav_changed(self, index: int):
        """Handle navigation item selection."""
        self.page_stack.setCurrentIndex(index)
        
        # Refresh the page when navigating to it
        page_ids = list(self.pages.keys())
        if 0 <= index < len(page_ids):
            page = self.pages[page_ids[index]]
            if hasattr(page, 'refresh'):
                page.refresh()
    
    def _setup_status_bar(self):
        """Set up the status bar."""
        status = QStatusBar()
        self.setStatusBar(status)
        
        # Audio latency indicator
        self.latency_label = QLabel("Latency: --")
        status.addPermanentWidget(self.latency_label)
    
    def update_audio_status(self, status: str, is_ok: bool = True):
        """Update the audio status indicator."""
        color = "#22c55e" if is_ok else "#ef4444"
        self.audio_status.setText(f"Audio: {status}")
        self.audio_status.setStyleSheet(f"color: {color}; padding: 15px;")
    
    def update_latency(self, latency_ms: float):
        """Update the latency display."""
        self.latency_label.setText(f"Latency: {latency_ms:.1f}ms")
    
    def closeEvent(self, event):
        """Handle window close."""
        # Stop any audio
        if self.audio_engine:
            self.audio_engine.cleanup()
        
        # Close database
        if self.db:
            self.db.close_session()
        
        event.accept()
