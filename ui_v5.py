# UI
# Last edited by: Julia
# Last edit date: Sun Apr 12 2026
import sys
import os
import cv2
import threading
import psutil
import admin_v5 as admin # admin_v5.py
# Using PySide6 for better looking UI and show camera feed
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel,
    QTextEdit, QLineEdit,
    QStackedWidget, QMessageBox
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QTimer

# To change font size
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel

# Get keyboard to work with button
from PySide6.QtGui import QShortcut, QKeySequence

# For video resizing
from PySide6.QtWidgets import QSizePolicy

class AegisApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aegis")
        self.showFullScreen()

        self.email = ""
        self.running = False
        self.alive = True

        # Camera
        self.cap = None

        # Stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Build the screens
        self.build_title()
        self.build_warning()
        self.build_instructions()
        self.build_email()
        self.build_camera()

        self.stack.setCurrentIndex(0)

        # Camera timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)

    # ESC key to EXIT program ==================================================
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.kill_everything()

    # Global exit (KILL ALL)
    def kill_everything(self):
        print("[SYSTEM] Ending all programs...")

        self.alive = False
        self.running = False

        # kill recording_live.py if running
        for proc in psutil.process_iter():
            try:
                cmd = " ".join(proc.cmdline())
                if "recording_live.py" in cmd:
                    proc.kill()
            except:
                pass

        # release camera
        try:
            self.cap.release()
        except:
            pass

        self.close()

    def add_exit(self, layout):
        btn = QPushButton("✖")
        btn.setFixedSize(40, 40)
        btn.setStyleSheet("background:red;color:white;font-size:18px;")
        btn.clicked.connect(self.kill_everything)

        top = QHBoxLayout()
        top.addStretch()
        top.addWidget(btn)

        layout.addLayout(top)

    # Title screen =============================================================
    def build_title(self):
        page = QWidget()
        page.setStyleSheet("background-color: lightblue;")
        main_layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        top_bar.addStretch()

        exit_btn = QPushButton("✖")
        exit_btn.setFixedSize(40, 40)
        exit_btn.setStyleSheet("background:red;color:white;font-size:18px;")
        exit_btn.clicked.connect(self.kill_everything)

        top_bar.addWidget(exit_btn)
        main_layout.addLayout(top_bar)

        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(5)

        title = QLabel("AEGIS")
        title.setFont(QFont("Arial", 50))
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Your Private AI Fall Detector")
        subtitle.setFont(QFont("Arial", 18))
        subtitle.setAlignment(Qt.AlignCenter)

        btn = QPushButton("ENTER")
        btn.setFixedSize(250, 80)
        btn.setStyleSheet("font-size: 22px; background-color: green; color: white;")

        btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addSpacing(20)
        content_layout.addWidget(btn, alignment=Qt.AlignCenter)

        main_layout.addLayout(content_layout)

        page.setLayout(main_layout)
        self.stack.addWidget(page)

    # Warning screen =========================================================
    def build_warning(self):
        page = QWidget()
        page.setStyleSheet("background-color: lightblue;")  # blue background

        layout = QVBoxLayout()

        self.add_exit(layout)

        # Top section: warning text (WHITE BOX) -----------
        text = QTextEdit()
        text.setReadOnly(True)

        text.setStyleSheet("""
            background-color: white;
            color: black;
            font-size: 16px;
            border-radius: 10px;
            padding: 30px;
        """)

        if os.path.exists("warning_text.txt"):
            text.setText(open("warning_text.txt").read())
        else:
            text.setText("WARNING")

        layout.addWidget(text, 7)  # 70% height

        # Bottom side: make buttons side by side -----------
        bottom = QWidget()
        bottom_layout = QHBoxLayout()

        agree = QPushButton("Agree")
        disagree = QPushButton("Disagree")

        # same size as title ENTER button
        agree.setFixedSize(250, 80)
        disagree.setFixedSize(250, 80)

        # styling button for nice UI
        agree.setStyleSheet("""
            background-color: #28a745;
            color: white;
            font-size: 18px;
            border-radius: 10px;
        """)

        disagree.setStyleSheet("""
            background-color: red;
            color: white;
            font-size: 18px;
            border-radius: 10px;
        """)

        agree.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        disagree.clicked.connect(self.kill_everything)

        bottom_layout.addStretch()
        bottom_layout.addWidget(agree)
        bottom_layout.addWidget(disagree)
        bottom_layout.addStretch()

        bottom.setLayout(bottom_layout)

        layout.addWidget(bottom, 3)  # 30% height

        page.setLayout(layout)
        self.stack.addWidget(page)

    # Instructions screen ======================================================
    def build_instructions(self):
        page = QWidget()
        page.setStyleSheet("background-color: lightblue;") 

        layout = QVBoxLayout()

        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.add_exit(layout)

        # Top section: Instruction text (WHITE BOX) -----------------
        text = QTextEdit()
        text.setReadOnly(True)

        text.setStyleSheet("""
            background-color: white;
            color: black;
            font-size: 16px;
            border-radius: 10px;
            padding: 30px;
        """)

        if os.path.exists("instructions_text.txt"):
            text.setText(open("instructions_text.txt").read())
        else:
            text.setText("INSTRUCTIONS")

        layout.addWidget(text, 7)  # 70%

        # Bottom section: 1 button -------------------------------
        bottom = QWidget()
        bottom_layout = QHBoxLayout()

        next_btn = QPushButton("Continue")

        next_btn.setFixedSize(250, 80)

        next_btn.setStyleSheet("""
            background-color: #28a745;
            color: white;
            font-size: 18px;
            border-radius: 10px;
        """)

        next_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        bottom_layout.addStretch()
        bottom_layout.addWidget(next_btn)
        bottom_layout.addStretch()

        bottom.setLayout(bottom_layout)

        layout.addWidget(bottom, 3)  # 30%

        page.setLayout(layout)
        self.stack.addWidget(page)

    # Email screen ==========================================================
    def build_email(self):
        page = QWidget()
        page.setStyleSheet("background-color: lightblue;")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.add_exit(layout)

        # Top section: Display the email ---------------------------
        self.email_label = QLabel("No email set")
        self.email_label.setStyleSheet("""
            background-color: white;
            color: black;
            font-size: 16px;
            padding: 10px;
            border-radius: 10px;
        """)
        self.email_label.setFixedHeight(60)

        layout.addWidget(self.email_label, 1)

        # Center section: Email input -----------------------
        self.email_input = QLineEdit()
        self.email_input.setFocus()
        self.email_input.setPlaceholderText("Enter email")

        QTimer.singleShot(100, self.email_input.setFocus)

        self.email_input.setStyleSheet("""
            background-color: white;
            font-size: 18px;
            padding: 10px;
            border-radius: 10px;
        """)
        self.email_input.setFixedHeight(60)

        layout.addWidget(self.email_input, 2)

        # bottom section: Buttons -----------------------------
        bottom = QWidget()
        bottom_layout = QHBoxLayout()

        confirm = QPushButton("Confirm Email")
        next_btn = QPushButton("Continue")

        confirm.setFixedSize(250, 80)
        next_btn.setFixedSize(250, 80)

        # Dark Blue Confirm
        confirm.setStyleSheet("""
            background-color: #1f4ed8;
            color: white;
            font-size: 18px;
            border-radius: 10px;
        """)

        # Green Continue
        next_btn.setStyleSheet("""
            background-color: #28a745;
            color: white;
            font-size: 18px;
            border-radius: 10px;
        """)

        confirm.clicked.connect(self.save_email)
        next_btn.clicked.connect(self.go_camera)

        bottom_layout.addStretch()
        bottom_layout.addWidget(confirm)
        bottom_layout.addWidget(next_btn)
        bottom_layout.addStretch()

        bottom.setLayout(bottom_layout)

        layout.addWidget(bottom, 2)

        page.setLayout(layout)
        self.stack.addWidget(page)

    # Email input messages ====================================================
    def save_email(self):
        email = self.email_input.text().strip()

        if not email or "@" not in email:
            self.email_label.setText("Invalid email")
            return

        self.email = email
        self.email_label.setText(f"Email: {self.email}")

        # Save email to file (to use in admin)
        with open("email.txt", "w") as f:
            f.write(self.email)

    def clear_email(self):
        self.email = ""
        self.email_input.setText("")
        self.email_label.setText("No email set")

    def go_camera(self):
        if not self.email:
            QMessageBox.warning(self, "Error", "Please enter a valid email and click Confirm Email button, before continuing!")
            return
        self.stack.setCurrentIndex(4)

    # Camera screen ========================================================
    def build_camera(self):
        page = QWidget()
        page.setStyleSheet("background-color: lightblue;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.add_exit(main_layout)

        # Video section: center it -------------------
        video_container = QWidget()
        video_layout = QHBoxLayout()

        self.video = QLabel()
        self.video.setMinimumSize(600, 400)
        self.video.setMaximumSize(900, 600)  # keeps it looking nice
        self.video.setStyleSheet("background-color: #4a90e2; border-radius: 10px;")
        self.video.setAlignment(Qt.AlignCenter)

        self.video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # center horizontally
        video_layout.addStretch()
        video_layout.addWidget(self.video)
        video_layout.addStretch()

        video_container.setLayout(video_layout)

        main_layout.addWidget(video_container, 7)

        # Status box: let user know whats going on --------------
        self.status_box = QLabel("Press Start")
        self.status_box.setAlignment(Qt.AlignCenter)

        self.status_box.setStyleSheet("""
            background-color: white;
            color: black;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
        """)

        self.status_box.setFixedHeight(50)

        main_layout.addWidget(self.status_box, 1)

        # The 3 buttons -----------------------------------
        btn_container = QWidget()
        btn_layout = QHBoxLayout()

        start = QPushButton("Start")
        stop = QPushButton("Stop")
        change = QPushButton("Change Email")

        start.setFixedSize(200, 70)
        stop.setFixedSize(200, 70)
        change.setFixedSize(200, 70)

        start.setStyleSheet("background-color: #28a745; color: white; font-size: 16px; border-radius: 10px;")
        stop.setStyleSheet("background-color: red; color: white; font-size: 16px; border-radius: 10px;")
        change.setStyleSheet("background-color: #1f4ed8; color: white; font-size: 16px; border-radius: 10px;")

        start.clicked.connect(self.start_system)
        stop.clicked.connect(self.stop_system)
        change.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        btn_layout.addStretch()
        btn_layout.addWidget(start)
        btn_layout.addWidget(stop)
        btn_layout.addWidget(change)
        btn_layout.addStretch()

        btn_container.setLayout(btn_layout)

        main_layout.addWidget(btn_container, 2)

        page.setLayout(main_layout)
        self.stack.addWidget(page)

    # Update camera feed =================================================
    def update_camera(self):
        if not self.running or not self.cap:
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape

            img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.video.setPixmap(QPixmap.fromImage(img))

    # Start admin/system ===================================================
    def start_system(self):
        if self.running:
            return

        if not self.email:
            self.status_box.setText("No email set")
            return

        self.running = True

        # Start the camera here
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        self.status_box.setText("Monitoring for Falls")

        threading.Thread(
            target=admin.run_admin,
            args=(self.email,),
            daemon=True
        ).start()

    # Stop admin/system =================================================
    def stop_system(self):
        self.running = False

        # Stop camera
        if self.cap:
            self.cap.release()
            self.cap = None

        # black/blue screen it
        self.video.clear()
        self.video.setStyleSheet("background-color: #4a90e2; border-radius: 10px;")

        self.status_box.setText("Program Stopped")

    # LOG it ===============================================================
    def log_msg(self, msg):
        self.log.append(msg)

    # Clean exit ===========================================================
    def closeEvent(self, event):
        self.kill_everything()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AegisApp()
    window.show()
    sys.exit(app.exec())

