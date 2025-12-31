"""
Dark theme stylesheet for the Bass Practice desktop app.
"""

DARK_STYLE = """
/* Main window and backgrounds */
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #eaeaea;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

/* Menu bar */
QMenuBar {
    background-color: #16213e;
    color: #eaeaea;
    padding: 5px;
}

QMenuBar::item:selected {
    background-color: #0f3460;
}

QMenu {
    background-color: #16213e;
    color: #eaeaea;
    border: 1px solid #0f3460;
}

QMenu::item:selected {
    background-color: #0f3460;
}

/* Sidebar / Navigation */
QListWidget {
    background-color: #16213e;
    color: #eaeaea;
    border: none;
    padding: 5px;
}

QListWidget::item {
    padding: 12px 20px;
    border-radius: 5px;
    margin: 2px 5px;
}

QListWidget::item:hover {
    background-color: #0f3460;
}

QListWidget::item:selected {
    background-color: #e94560;
    color: white;
}

/* Buttons */
QPushButton {
    background-color: #0f3460;
    color: #eaeaea;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #e94560;
}

QPushButton:pressed {
    background-color: #c73e54;
}

QPushButton:disabled {
    background-color: #333;
    color: #666;
}

/* Primary button */
QPushButton[primary="true"] {
    background-color: #e94560;
}

QPushButton[primary="true"]:hover {
    background-color: #ff6b6b;
}

/* Success button */
QPushButton[success="true"] {
    background-color: #22c55e;
}

QPushButton[success="true"]:hover {
    background-color: #16a34a;
}

/* Labels */
QLabel {
    color: #eaeaea;
}

QLabel[heading="true"] {
    font-size: 24px;
    font-weight: bold;
    color: #ffffff;
}

QLabel[subheading="true"] {
    font-size: 18px;
    font-weight: bold;
    color: #e94560;
}

QLabel[muted="true"] {
    color: #888;
}

/* Input fields */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #0f3460;
    color: #eaeaea;
    border: 1px solid #333;
    border-radius: 5px;
    padding: 8px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #e94560;
}

/* Combo boxes */
QComboBox {
    background-color: #0f3460;
    color: #eaeaea;
    border: 1px solid #333;
    border-radius: 5px;
    padding: 8px;
    min-width: 100px;
}

QComboBox:hover {
    border-color: #e94560;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #eaeaea;
    selection-background-color: #e94560;
}

/* Spin boxes */
QSpinBox, QDoubleSpinBox {
    background-color: #0f3460;
    color: #eaeaea;
    border: 1px solid #333;
    border-radius: 5px;
    padding: 8px;
}

/* Sliders */
QSlider::groove:horizontal {
    background: #333;
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #e94560;
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background: #ff6b6b;
}

QSlider::sub-page:horizontal {
    background: #0f3460;
    border-radius: 4px;
}

/* Progress bars */
QProgressBar {
    background-color: #333;
    border-radius: 5px;
    text-align: center;
    color: white;
}

QProgressBar::chunk {
    background-color: #e94560;
    border-radius: 5px;
}

/* Scroll bars */
QScrollBar:vertical {
    background: #16213e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #0f3460;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #e94560;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #16213e;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #0f3460;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #e94560;
}

/* Tab widget */
QTabWidget::pane {
    border: 1px solid #333;
    border-radius: 5px;
    background-color: #1a1a2e;
}

QTabBar::tab {
    background-color: #16213e;
    color: #eaeaea;
    padding: 10px 20px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #e94560;
}

QTabBar::tab:hover:!selected {
    background-color: #0f3460;
}

/* Group boxes */
QGroupBox {
    border: 1px solid #333;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 15px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    color: #e94560;
}

/* Tables */
QTableWidget, QTableView {
    background-color: #16213e;
    color: #eaeaea;
    gridline-color: #333;
    border: none;
}

QTableWidget::item, QTableView::item {
    padding: 8px;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #0f3460;
}

QHeaderView::section {
    background-color: #0f3460;
    color: #eaeaea;
    padding: 10px;
    border: none;
    font-weight: bold;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 2px solid #333;
}

QCheckBox::indicator:checked {
    background-color: #e94560;
    border-color: #e94560;
}

/* Radio buttons */
QRadioButton {
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #333;
}

QRadioButton::indicator:checked {
    background-color: #e94560;
    border-color: #e94560;
}

/* Tool tips */
QToolTip {
    background-color: #16213e;
    color: #eaeaea;
    border: 1px solid #e94560;
    padding: 5px;
    border-radius: 3px;
}

/* Splitter */
QSplitter::handle {
    background-color: #333;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* Frame */
QFrame[card="true"] {
    background-color: #16213e;
    border-radius: 10px;
    padding: 15px;
}

/* Status bar */
QStatusBar {
    background-color: #16213e;
    color: #888;
}
"""

# Color constants for use in code
COLORS = {
    'background': '#1a1a2e',
    'surface': '#16213e',
    'primary': '#e94560',
    'primary_hover': '#ff6b6b',
    'secondary': '#0f3460',
    'text': '#eaeaea',
    'text_muted': '#888',
    'success': '#22c55e',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'border': '#333',
}
