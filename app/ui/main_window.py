# app/ui/main_window.py
import sys
import time
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton,
    QDialog, QDialogButtonBox, QHeaderView, QMessageBox,
    QLineEdit, QComboBox, QStatusBar, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor
from app.data.database import initialize_database
from app.data.parsers.chance_csv import load_chance_csv
from app.data.fetchers.poe2scout import fetch_unique_prices, fetch_currency_prices
from app.data.fetchers.ggg_trade import fetch_base_prices
from app.data.calculator import calculate_cost
from PyQt6.QtWidgets import QStyledItemDelegate

class AccentBorderDelegate(QStyledItemDelegate):
    def __init__(self, profit_color, loss_color, parent=None):
        super().__init__(parent)
        self.profit_color = profit_color
        self.loss_color = loss_color

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        profit_col = index.siblingAtColumn(8)
        try:
            profit = float(profit_col.data() or 0)
        except ValueError:
            profit = 0
        color = self.profit_color if profit > 0 else self.loss_color
        painter.fillRect(option.rect.x(), option.rect.y(), 3, option.rect.height(), QColor(color))
class TierPillDelegate(QStyledItemDelegate):
    STYLES = {
        "T1": ("#E8C27A", "#1F1A12", "#E8C27A"),
        "T2": ("#6E92C8", "#121821", "#2C405C"),
        "T3": ("#A0A8B3", "#1D232D", "#2E3744"),
    }

    def paint(self, painter, option, index):
        from PyQt6.QtWidgets import QStyle
        tier = index.data() or "T3"
        fg, pill_bg, border = self.STYLES.get(tier, self.STYLES["T3"])

        painter.save()
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)
        cell_bg = QColor("#2C384A") if is_selected else option.palette.base()
        painter.fillRect(option.rect, cell_bg)

        pw, ph = 36, 22
        cx = option.rect.center().x()
        cy = option.rect.center().y()
        pill = option.rect.__class__(cx - pw // 2, cy - ph // 2, pw, ph)

        from PyQt6.QtGui import QBrush, QPen
        painter.setBrush(QBrush(QColor(pill_bg)))
        painter.setPen(QPen(QColor(border), 1))
        painter.drawRoundedRect(pill, 3, 3)

        painter.setPen(QColor(fg))
        painter.setFont(option.font)
        painter.drawText(pill, Qt.AlignmentFlag.AlignCenter, tier)
        painter.restore()

class RowHoverDelegate(QStyledItemDelegate):
    def __init__(self, table, parent=None):
        super().__init__(parent)
        self.table = table

    def paint(self, painter, option, index):
        if index.row() == self.table.hovered_row:
            option.palette.setColor(option.palette.ColorRole.Base, QColor("#232B38"))
            option.palette.setColor(option.palette.ColorRole.AlternateBase, QColor("#232B38"))
        super().paint(painter, option, index)

DARK_STYLE = """
QWidget {
    background-color: #0F1216;
    color: #E4E6EB;
    font-family: "Inter", "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 13px;
}
QMainWindow, QDialog {
    background-color: #0F1216;
}
QWidget#topbar {
    background-color: #161A21;
    border-bottom: 1px solid #2E3744;
    min-height: 64px;
    max-height: 64px;
}
QLabel#brand, QLabel#brandSub, QLabel#status {
    background-color: transparent;
}
QLabel#brand {
    color: #E4E6EB;
    font-size: 18px;
    font-weight: 700;
    padding-left: 10px;
}
QLabel#brandSub {
    color: #6B7585;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    padding-left: 10px;
    border-left: 1px solid #2E3744;
}
QFrame#brandMark {
    background-color: #E8C27A;
    border-radius: 3px;
    min-width: 22px; max-width: 22px;
    min-height: 22px; max-height: 22px;
}
QLabel#status {
    color: #A0A8B3;
    background-color: #1D232D;
    border: 1px solid #2E3744;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
}
QLabel#rowCount {
    color: #6B7585;
    font-family: "JetBrains Mono", "Consolas", monospace;
    font-size: 12px;
}
QPushButton {
    background-color: #1D232D;
    color: #E4E6EB;
    border: 1px solid #3B4658;
    border-radius: 4px;
    padding: 7px 16px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #232B38;
    border-color: #E8C27A;
    color: #E8C27A;
}
QPushButton:pressed {
    background-color: #161A21;
    border-color: #C8A050;
    color: #C8A050;
}
QPushButton:disabled {
    color: #6B7585;
    border-color: #2E3744;
    background-color: #161A21;
}
QPushButton#chip {
    background-color: transparent;
    border: 1px solid #2E3744;
    border-radius: 13px;
    padding: 4px 14px;
    color: #A0A8B3;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#chip:hover {
    border-color: #3B4658;
    color: #E4E6EB;
}
QPushButton#chip:checked {
    background-color: #1F1A12;
    color: #E8C27A;
    border-color: #E8C27A;
}
QWidget#filterbar {
    background-color: #0F1216;
    border-bottom: 1px solid #242A34;
    min-height: 52px;
    max-height: 52px;
}
QLineEdit {
    background-color: #161A21;
    color: #E4E6EB;
    border: 1px solid #2E3744;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 12px;
    min-height: 18px;
}
QLineEdit:focus { border-color: #E8C27A; }
QLineEdit::placeholder { color: #6B7585; }
QComboBox {
    background-color: #161A21;
    color: #E4E6EB;
    border: 1px solid #2E3744;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 12px;
    min-height: 18px;
    min-width: 90px;
}
QComboBox:focus { border-color: #E8C27A; }
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #2E3744;
}
QComboBox QAbstractItemView {
    background-color: #1D232D;
    color: #E4E6EB;
    border: 1px solid #2E3744;
    selection-background-color: #2C384A;
    selection-color: #E8C27A;
    padding: 4px;
    outline: 0;
}
QTableView, QTableWidget {
    background-color: #161A21;
    alternate-background-color: #181C24;
    color: #E4E6EB;
    gridline-color: #242A34;
    border: 0;
    selection-background-color: #2C384A;
    selection-color: #E4E6EB;
    font-family: "JetBrains Mono", "Consolas", monospace;
    font-size: 13px;
}
QTableView::item, QTableWidget::item {
    padding: 10px 14px;
    border: 0;
    border-bottom: 1px solid #242A34;
}
QTableView::item:selected, QTableWidget::item:selected {
    background-color: #2C384A;
    color: #E4E6EB;
}
QHeaderView { background-color: #1D232D; border: 0; }
QHeaderView::section {
    background-color: #1D232D;
    color: #A0A8B3;
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 11px;
    font-weight: 600;
    padding: 12px 14px;
    border: 0;
    border-right: 1px solid #242A34;
    border-bottom: 1px solid #2E3744;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QHeaderView::section:hover { color: #E4E6EB; background-color: #232B38; }
QHeaderView::section:last { border-right: 0; }
QScrollBar:vertical {
    background: #0F1216;
    width: 12px;
    margin: 0;
    border-left: 1px solid #242A34;
}
QScrollBar::handle:vertical {
    background: #2E3744;
    border-radius: 3px;
    margin: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #3B4658; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #0F1216;
    height: 12px;
    border-top: 1px solid #242A34;
}
QScrollBar::handle:horizontal {
    background: #2E3744;
    border-radius: 3px;
    margin: 3px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #3B4658; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QStatusBar {
    background-color: #0A0D11;
    color: #6B7585;
    border-top: 1px solid #242A34;
    font-family: "JetBrains Mono", "Consolas", monospace;
    font-size: 11px;
    min-height: 28px;
}
QStatusBar::item { border: 0; }
QDialog { background-color: #161A21; border: 1px solid #2E3744; }
QGroupBox {
    background-color: #161A21;
    border: 1px solid #2E3744;
    border-radius: 6px;
    margin-top: 14px;
    padding: 14px;
    color: #A0A8B3;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #E8C27A;
    font-size: 11px;
}
QMenu {
    background-color: #1D232D;
    color: #E4E6EB;
    border: 1px solid #2E3744;
    padding: 4px;
}
QMenu::item { padding: 6px 14px; border-radius: 3px; }
QMenu::item:selected { background-color: #2C384A; color: #E8C27A; }
"""

COLUMNS = [
    "Base Item", "Unique Item", "Tier", "Avg Orbs",
    "Base Cost", "Orb Cost", "Total Cost", "EV", "Profit", "ROI %",
]

PROFIT_BG  = QColor("#1B2A22")
LOSS_BG    = QColor("#2A1B1B")
PROFIT_FG  = QColor("#6BB07A")
LOSS_FG    = QColor("#C26B6B")
ACCENT_FG  = QColor("#E8C27A")


class RefreshWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, league, poesessid):
        super().__init__()
        self.league = league
        self.poesessid = poesessid

    def run(self):
        try:
            db = initialize_database()
            league_url = self.league.replace(" ", "%20")
            league_scout = self.league.replace(" ", "_")
            self.progress.emit("Loading item data...")
            load_chance_csv(db, "assets/outcomes.csv")
            self.progress.emit("Fetching unique prices...")
            fetch_unique_prices(db, league_scout)
            self.progress.emit("Fetching currency rates...")
            fetch_currency_prices(db, league_scout)
            self.progress.emit("Fetching base prices — this may take a while...")
            fetch_base_prices(db, league_url, self.poesessid)
            self.progress.emit("Calculating profits...")
            calculate_cost(db)
            db.close()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(340)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        warning = QLabel(
            "⚠  This will re-fetch all data from the API.\n"
            "The process may take up to 2 hours.\n"
            "Do not close the application while refreshing."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #C26B6B; padding: 8px; font-size: 12px;")
        layout.addWidget(warning)

        self.refresh_btn = QPushButton("Refresh All Data")
        self.refresh_btn.clicked.connect(self.accept)
        layout.addWidget(self.refresh_btn)

        cancel = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        cancel.rejected.connect(self.reject)
        layout.addWidget(cancel)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self, db, league, poesessid):
        super().__init__()
        self.db = db
        self.league = league
        self.poesessid = poesessid
        self.worker = None
        self.all_rows = []
        self.last_sync_time = None

        self.setWindowTitle("Poe2Profit")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(DARK_STYLE)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("QStatusBar { font-family: 'JetBrains Mono', 'Consolas', monospace; font-size: 11px; }")

        self.sb_connected = QLabel("● Connected")
        self.sb_connected.setStyleSheet("color: #6BB07A; padding: 0 8px;")
        self.sb_sync = QLabel("Last sync: —")
        self.sb_sync.setStyleSheet("color: #6B7585; padding: 0 8px; border-left: 1px solid #2E3744;")
        self.sb_rate = QLabel("Rate: —")
        self.sb_rate.setStyleSheet("color: #6B7585; padding: 0 8px; border-left: 1px solid #2E3744;")
        self.sb_version = QLabel("v1.0.0")
        self.sb_version.setStyleSheet("color: #3B4658; padding: 0 8px;")

        self.status_bar.addWidget(self.sb_connected)
        self.status_bar.addWidget(self.sb_sync)
        self.status_bar.addWidget(self.sb_rate)
        self.status_bar.addPermanentWidget(self.sb_version)

        # Root
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Top bar ──────────────────────────────────────────────
        topbar = QWidget()
        topbar.setObjectName("topbar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 0, 20, 0)
        topbar_layout.setSpacing(8)

        mark = QFrame()
        mark.setObjectName("brandMark")
        mark.setFixedSize(22, 22)
        topbar_layout.addWidget(mark)

        brand = QLabel("Poe2Profit")
        brand.setObjectName("brand")
        topbar_layout.addWidget(brand)

        brand_sub = QLabel("PROFIT CALCULATOR")
        brand_sub.setObjectName("brandSub")
        topbar_layout.addWidget(brand_sub)

        topbar_layout.addStretch()

        self.status_label = QLabel("● Ready")
        self.status_label.setObjectName("status")
        topbar_layout.addWidget(self.status_label)

        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.clicked.connect(self.start_refresh)
        topbar_layout.addWidget(refresh_btn)

        settings_btn = QPushButton("⚙  Settings")
        settings_btn.clicked.connect(self.open_settings)
        topbar_layout.addWidget(settings_btn)

        root_layout.addWidget(topbar)

        # ── Filter bar ───────────────────────────────────────────
        filterbar = QWidget()
        filterbar.setObjectName("filterbar")
        filterbar_layout = QHBoxLayout(filterbar)
        filterbar_layout.setContentsMargins(20, 0, 20, 0)
        filterbar_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("Search items…")
        self.search_input.setFixedWidth(160)
        self.search_input.textChanged.connect(self.apply_filters)
        filterbar_layout.addWidget(self.search_input)

        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["All Tiers", "T1", "T2", "T3"])
        self.tier_combo.currentIndexChanged.connect(self.apply_filters)
        filterbar_layout.addWidget(self.tier_combo)

        self.roi_combo = QComboBox()
        self.roi_combo.addItems(["Min ROI: Any", "0%+", "10%+", "50%+", "100%+"])
        self.roi_combo.currentIndexChanged.connect(self.apply_filters)
        filterbar_layout.addWidget(self.roi_combo)

        self.chip_profit = QPushButton("● Profitable")
        self.chip_profit.setObjectName("chip")
        self.chip_profit.setCheckable(True)
        self.chip_profit.toggled.connect(self.apply_filters)
        filterbar_layout.addWidget(self.chip_profit)

        self.chip_loss = QPushButton("Loss")
        self.chip_loss.setObjectName("chip")
        self.chip_loss.setCheckable(True)
        self.chip_loss.toggled.connect(self.apply_filters)
        filterbar_layout.addWidget(self.chip_loss)

        filterbar_layout.addStretch()

        self.row_count_label = QLabel("")
        self.row_count_label.setObjectName("rowCount")
        filterbar_layout.addWidget(self.row_count_label)

        root_layout.addWidget(filterbar)

        # ── Table ────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setObjectName("itemTable")
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setItemDelegateForColumn(0, AccentBorderDelegate("#6BB07A", "#C26B6B", self.table))
        self.table.setItemDelegateForColumn(2, TierPillDelegate(self.table))
        self.hover_delegate = RowHoverDelegate(self, self.table)
        self.table.setItemDelegate(self.hover_delegate)
        root_layout.addWidget(self.table)
        self.table.setMouseTracking(True)
        self.table.viewport().setMouseTracking(True)
        self.table.cellEntered.connect(self.on_cell_hover)
        self.hovered_row = -1
        # Timer for "Updated X ago"
        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self.update_elapsed)
        self.elapsed_timer.start(10000)

        self.load_results()
        self.update_rate_label()

    def load_results(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT base_item, unique_item, tier, avg_orbs,
                   base_cost_div, orb_cost_div, total_cost_div,
                   ev_div, profit_div, roi_pct
            FROM results
            ORDER BY profit_div DESC
        """)
        self.all_rows = cur.fetchall()
        cur.execute("SELECT MAX(last_calculated) FROM results")
        row = cur.fetchone()
        if row and row[0]:
            from datetime import datetime
            dt = datetime.fromisoformat(row[0])
            self.last_sync_time = dt.timestamp()
            self.update_elapsed()
        self.apply_filters()

    def apply_filters(self):
        search = self.search_input.text().lower().strip()

        tier_text = self.tier_combo.currentText()
        tier_filter = None if tier_text == "All Tiers" else int(tier_text[1])

        roi_map = {"Min ROI: Any": None, "0%+": 0, "10%+": 10, "50%+": 50, "100%+": 100}
        min_roi = roi_map[self.roi_combo.currentText()]

        only_profit = self.chip_profit.isChecked()
        only_loss   = self.chip_loss.isChecked()

        filtered = []
        for row in self.all_rows:
            base_item, unique_item, tier, avg_orbs, base_cost, orb_cost, total_cost, ev, profit, roi = row

            if search and search not in (base_item or "").lower() and search not in (unique_item or "").lower():
                continue
            if tier_filter is not None and tier != tier_filter:
                continue
            if min_roi is not None and roi < min_roi:
                continue
            if only_profit and not only_loss and profit <= 0:
                continue
            if only_loss and not only_profit and profit > 0:
                continue

            filtered.append(row)

        profitable_count = sum(1 for r in filtered if r[8] > 0)
        self.row_count_label.setText(f"{len(filtered)} rows · {profitable_count} profitable")
        self.populate_table(filtered)

    def populate_table(self, rows):
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            base_item, unique_item, tier, avg_orbs, base_cost, orb_cost, total_cost, ev, profit, roi = row
            is_profit = profit > 0
            bg = PROFIT_BG if is_profit else LOSS_BG

            values = [base_item, unique_item, tier, avg_orbs, base_cost, orb_cost, total_cost, ev, profit, roi]
            for col_idx, value in enumerate(values):
                # Tier column: styled label text
                if col_idx == 2:
                    tier_int = int(value) if value else 3
                    label = f"T{tier_int}"
                    item = QTableWidgetItem(label)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)
                    continue

                text = f"{value:.2f}" if isinstance(value, float) else (str(value) if value is not None else "")

                # Add + prefix for positive profit/roi
                if col_idx in (8, 9) and isinstance(value, float) and value > 0:
                    text = f"+{text}"

                item = QTableWidgetItem(text)

                # Alignment: left for text cols, right for numbers
                if col_idx in (0, 1):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

                item.setBackground(bg)

                # Unique item name in gold
                if col_idx == 1:
                    item.setForeground(ACCENT_FG)
                # Profit and ROI colored by sign
                elif col_idx in (8, 9):
                    item.setForeground(PROFIT_FG if is_profit else LOSS_FG)
    
                self.table.setItem(row_idx, col_idx, item)

    def update_rate_label(self):
        cur = self.db.cursor()
        cur.execute("SELECT divine_equivalent FROM currency_rates WHERE currency_name = 'Orb of Chance'")
        row = cur.fetchone()
        if row:
            rate = row[0]
            orbs_per_div = round(1 / rate) if rate > 0 else "?"
            self.sb_rate.setText(f"Rate 1 div = {orbs_per_div} chaos")

    def update_elapsed(self):
        if self.last_sync_time is None:
            return
        elapsed = int(time.time() - self.last_sync_time)
        if elapsed < 60:
            text = f"Updated {elapsed}s ago · League: {self.league}"
        elif elapsed < 3600:
            text = f"Updated {elapsed // 60}m ago · League: {self.league}"
        else:
            text = f"Updated {elapsed // 3600}h ago · League: {self.league}"
        self.status_label.setText(f"● {text}")

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.start_refresh()

    def start_refresh(self):
        if self.worker and self.worker.isRunning():
            return
        self.status_label.setText("● Fetching...")
        self.worker = RefreshWorker(self.league, self.poesessid)
        self.worker.progress.connect(lambda msg: self.status_label.setText(f"● {msg}"))
        self.worker.finished.connect(self.on_refresh_done)
        self.worker.error.connect(self.on_refresh_error)
        self.worker.start()

    def on_refresh_done(self):
        self.last_sync_time = time.time()
        self.sb_sync.setText(f"Last sync {datetime.now().strftime('%H:%M:%S')}")
        self.load_results()
        self.update_rate_label()
        self.update_elapsed()

    def on_refresh_error(self, msg):
        self.status_label.setText("● Error")
        QMessageBox.critical(self, "Refresh Error", msg)
    def on_cell_hover(self, row, col):
        if row == self.hovered_row:
            return
        self.hovered_row = row
        self.table.viewport().update()

def launch_ui(db, league, poesessid):
    app = QApplication(sys.argv)
    window = MainWindow(db, league, poesessid)
    window.show()
    sys.exit(app.exec())