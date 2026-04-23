# UI
# Last edited by: Julia
# Last edit date: Mon Apr 20 2026
import sys
import os
import cv2
import platform
import multiprocessing # To stop admin from running
import psutil
import admin_v8 as admin # admin_v8.py
# Using PySide6 for better looking UI and show camera feed
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel,QLineEdit, QStackedWidget,
    QSizePolicy, QTextEdit, QMessageBox,
    QScrollArea, QFrame
)
from PySide6.QtGui import (
    QImage, QPixmap, QFont, QColor
) 
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, 
    QEasingCurve, Property, QUrl
) 
# To play the videos
from PySide6.QtMultimedia import (
    QMediaPlayer, QAudioOutput
)
from PySide6.QtMultimediaWidgets import QVideoWidget

# UI Button animation
class AnimatedButton(QPushButton):
    def __init__(self, text, base, hover, pressed):
        super().__init__(text)

        self.base_color = QColor(base)
        self.hover_color = QColor(hover)
        self.pressed_color = QColor(pressed)

        self._color = self.base_color

        self.anim = QPropertyAnimation(self, b"color")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.update_style()

    # Property that animation changes
    def getColor(self):
        return self._color

    def setColor(self, color):
        self._color = color
        self.update_style()

    color = Property(QColor, getColor, setColor)

    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color.name()};
                color: white;
                font-size: 18px;
                border-radius: 10px;
            }}
        """)

    # Hover enter
    def enterEvent(self, event):
        self.animate_to(self.hover_color)
        super().enterEvent(event)

    # Hover leave
    def leaveEvent(self, event):
        self.animate_to(self.base_color)
        super().leaveEvent(event)

    # Mouse press
    def mousePressEvent(self, event):
        self.animate_to(self.pressed_color)
        super().mousePressEvent(event)

    # Mouse release
    def mouseReleaseEvent(self, event):
        self.animate_to(self.hover_color)
        super().mouseReleaseEvent(event)

    def animate_to(self, target):
        self.anim.stop()
        self.anim.setStartValue(self._color)
        self.anim.setEndValue(target)
        self.anim.start()

# Main UI
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
        self.build_title() # index 0
        self.build_warning() # index 1
        self.build_instructions() # index 2
        self.build_email() # index 3
        self.build_choose_screen() # index 4
        self.build_camera() # index 5
        self.build_mainscreen() # index 6
        self.build_video_screen() # index 7

        self.stack.setCurrentIndex(0)

        # Camera timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)

        # Alert box updater
        self.alert_timer = QTimer()
        self.alert_timer.timeout.connect(self.update_alert_box)
        self.alert_timer.start(1000)  # updates every 1 second

    # ESC key to EXIT program ==================================================
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.kill_everything()

    # Global exit (KILL ALL)
    def kill_everything(self):
        print("[SYSTEM UI] Ending all programs...")

        self.running = False

        # stop admin
        if hasattr(self, "admin_stop_flag"):
            self.admin_stop_flag.value = True

        # kill admin process
        if hasattr(self, "admin_process") and self.admin_process:
            self.admin_process.terminate()
            self.admin_process = None

        # kill recording_live.py
        for proc in psutil.process_iter():
            try:
                cmd = " ".join(proc.cmdline())
                if "recording_live.py" in cmd:
                    proc.kill()
            except:
                pass

        # release camera
        try:
            if self.cap:
                self.cap.release()
                self.cap = None
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

    # Title screen index 0 =============================================================
    def build_title(self):
        page = QWidget()
        page.setStyleSheet("background-color: lightblue;")
        main_layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        top_bar.addStretch()

        # exit red button top right
        exit_btn = QPushButton("✖")
        exit_btn.setFixedSize(40, 40)
        exit_btn.setStyleSheet("background:red;color:white;font-size:18px;")
        exit_btn.clicked.connect(self.kill_everything)

        top_bar.addWidget(exit_btn)
        main_layout.addLayout(top_bar)

        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(5)

        # Title text
        title = QLabel("AEGIS")
        title.setFont(QFont("Arial", 50))
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Your Private AI Fall Detector")
        subtitle.setFont(QFont("Arial", 18))
        subtitle.setAlignment(Qt.AlignCenter)

        # Buttons
        # 1st is button color, 2nd hover, 3rd select/click
        btn = AnimatedButton("ENTER", "#28a745", "#46f66f", "#15381D")
        btn.setFixedSize(250, 80)

        # Click button to go to next screen
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addSpacing(20)
        content_layout.addWidget(btn, alignment=Qt.AlignCenter)

        main_layout.addLayout(content_layout)

        page.setLayout(main_layout)
        self.stack.addWidget(page)

    # Warning screen index 1 =========================================================
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

        agree = AnimatedButton("Agree", "#28a745", "#46f66f", "#15381D")
        agree.setFixedSize(250, 80)

        disagree = AnimatedButton("Disagree", "#b41714", "#f8030b", "#4b0a0a")
        disagree.setFixedSize(250, 80)

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

    # Instructions screen index 2 ======================================================
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

        next_btn = AnimatedButton("Continue", "#28a745", "#46f66f", "#15381D")
        next_btn.setFixedSize(250, 80)

        next_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        bottom_layout.addStretch()
        bottom_layout.addWidget(next_btn)
        bottom_layout.addStretch()

        bottom.setLayout(bottom_layout)

        layout.addWidget(bottom, 3)  # 30%

        page.setLayout(layout)
        self.stack.addWidget(page)

    # Email screen index 3 ==========================================================
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
        self.email_input.setPlaceholderText("EnterYourEmailHere@gmail.com")

        QTimer.singleShot(100, self.email_input.setFocus)

        # Keep text to stay black not turn white
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                font-size: 18px;
                padding: 10px;
                border-radius: 10px;
                border: 1px solid #ccc;
            }

            QLineEdit:focus {
                color: black;
            }

            QLineEdit::placeholder {
                color: gray;
            }

            QLineEdit {
                selection-color: white;
                selection-background-color: #1f4ed8;
            }
        """)
        self.email_input.setTextMargins(5, 0, 5, 0)

        self.email_input.setFixedHeight(60)

        layout.addWidget(self.email_input, 2)

        # bottom section: Buttons -----------------------------
        bottom = QWidget()
        bottom_layout = QHBoxLayout()

        confirm  = AnimatedButton("Confirm Email", "#304da5", "#00c8ff", "#0b1a44")
        next_btn = AnimatedButton("Continue", "#28a745", "#46f66f", "#15381D")
        
        confirm.setFixedSize(250, 80)
        next_btn.setFixedSize(250, 80)

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

    # Email input messages -------------------------------------------------
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

    # Choosing screen index 4 ============================================================
    def build_choose_screen(self):
        page = QWidget()
        page.setStyleSheet("background-color: lightblue;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.add_exit(main_layout)

        # Status box: let user know whats going on -------------- 
        # Title
        title = QLabel("Would you like to test the camera first or start monitoring?")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: black;
        """)

        main_layout.addWidget(title, 1)

        # The 2 buttons -----------------------------------
        btn_container = QWidget()
        btn_layout = QHBoxLayout()

        test  = AnimatedButton("TEST CAMERA", "#304da5", "#00c8ff", "#0b1a44")
        f_btn = AnimatedButton("VIDEO RECORDINGS", "#632874", "#c300ff", "#4A0F5B")
        start = AnimatedButton("START MONITORING", "#28a745", "#46f66f", "#15381D")

        test.setFixedSize(200, 70)
        f_btn.setFixedSize(200, 70)
        start.setFixedSize(200, 70)

        test.clicked.connect(self.go_to_camera_screen)
        f_btn.clicked.connect(self.open_video_screen)
        start.clicked.connect(self.go_to_main_screen)

        btn_layout.addStretch()
        btn_layout.addWidget(test)
        btn_layout.addWidget(f_btn)
        btn_layout.addWidget(start)
        btn_layout.addStretch()

        btn_container.setLayout(btn_layout)

        main_layout.addWidget(btn_container, 2)

        page.setLayout(main_layout)
        self.stack.addWidget(page)

    # Button to switch to Camera test screen ------------------------------------------------------
    def go_to_camera_screen(self):
        # reuse STOP logic
        # admin's camera use shut down so no conflict with new camera use
        self.stop_system()

        # Reset MAIN SCREEN text to original state
        if hasattr(self, "status_box_main"):
            self.status_box_main.setText("Press START to start detecting for falls")

        # Switch to camera screen (index 5)
        self.stack.setCurrentIndex(5)

    # Camera test screen index 5 ========================================================
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
        self.status_box = QLabel("Press TEST to turn on camera, Press STOP TEST to turn off camera")
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

        start  = AnimatedButton("TEST", "#304da5", "#00c8ff", "#0b1a44")
        stop = AnimatedButton("STOP", "#b41714", "#f8030b", "#4b0a0a")
        change = AnimatedButton("NEXT", "#28a745", "#46f66f", "#15381D")

        start.setFixedSize(200, 70)
        stop.setFixedSize(200, 70)
        change.setFixedSize(200, 70)

        start.clicked.connect(self.start_camera)
        stop.clicked.connect(self.stop_camera)
        change.clicked.connect(self.go_to_main_screen)

        btn_layout.addStretch()
        btn_layout.addWidget(start)
        btn_layout.addWidget(stop)
        btn_layout.addWidget(change)
        btn_layout.addStretch()

        btn_container.setLayout(btn_layout)

        main_layout.addWidget(btn_container, 2)

        page.setLayout(main_layout)
        self.stack.addWidget(page)

    # Update camera feed --------------------------------------------------
    def update_camera(self):
        if not getattr(self, "running", False):
            return

        if not self.cap:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.video.setPixmap(QPixmap.fromImage(img))

    # Start camera logic ---------------------------------------------
    def start_camera(self):
        # FULL reset
        self.running = False

        if hasattr(self, "cap") and self.cap:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None

        self.video.clear()

        # delay so admin releases camera
        QTimer.singleShot(500, self._init_camera)

    def _init_camera(self):
        if platform.system() == "Windows":
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            self.status_box.setText("Camera is busy, try again after 5 seconds")
            return

        self.cam_timer = QTimer()
        self.cam_timer.timeout.connect(self.update_camera)
        self.cam_timer.start(30)

        self.running = True
        self.status_box.setText("Camera Test ON")

    # Stop camera logic -----------------------------------------------
    def stop_camera(self):
        self.running = False

        if hasattr(self, "cam_timer") and self.cam_timer:
            self.cam_timer.stop()

        # Stop camera
        if self.cap:
            self.cap.release()
            self.cap = None

        # black/blue screen it
        self.video.clear()
        self.video.setStyleSheet("background-color: #4a90e2; border-radius: 10px;")

        self.status_box.setText("Camera Test OFF")

    # Button to switch to Main screen  -----------------------------------------------------------
    def go_to_main_screen(self):
        # ALWAYS stop camera before switching so admin and UI don't lock camera
        self.running = False

        if hasattr(self, "cam_timer") and self.cam_timer:
            self.cam_timer.stop()

        if self.cap:
            self.cap.release()
            self.cap = None

        # reset camera screen UI
        self.video.clear()
        self.video.setStyleSheet("background-color: #4a90e2; border-radius: 10px;")

        # Reset main screen text
        if hasattr(self, "main_status_box"):
            self.status_box_main.setText("Press START to start detecting for falls")

        # go to main screen
        self.stack.setCurrentIndex(6)

    # Main screen index 6 ====================================================================
    def build_mainscreen(self):
        # Make/clear alert.txt
        alert_path = os.path.join(os.path.dirname(__file__), "alert.txt")
        try:
            # create OR clear file
            with open(alert_path, "w") as f:
                f.write("")  # empty file

            print("[UI] alert.txt initialized")
        except Exception as e:
            print("[UI ERROR] alert.txt:", e)

        page = QWidget()
        page.setStyleSheet("background-color: lightblue;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.add_exit(main_layout)

        # Status box
        self.status_box_main = QLabel("Press START to start detecting for falls")
        self.status_box_main.setAlignment(Qt.AlignCenter)
        self.status_box_main.setStyleSheet("""
            background-color: white;
            color: black;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
        """)
        self.status_box_main.setFixedHeight(50)
        main_layout.addWidget(self.status_box_main, 1)

        # Alert display box ------------------------
        self.alert_box = QLabel("...")
        self.alert_box.setAlignment(Qt.AlignCenter)
        self.alert_box.setStyleSheet("""
            background-color: #fff3cd;
            color: black;
            font-size: 16px;
            border-radius: 10px;
            padding: 10px;
        """)
        self.alert_box.setFixedHeight(70)
        main_layout.addWidget(self.alert_box, 1)

        # Buttons --------------------------------
        btn_container = QWidget()
        btn_layout = QHBoxLayout()

        start = AnimatedButton("START", "#28a745", "#46f66f", "#15381D")
        stop = AnimatedButton("STOP", "#b41714", "#f8030b", "#4b0a0a")
        change = AnimatedButton("Change Email", "#304da5", "#00c8ff", "#0b1a44")
        b_btn = AnimatedButton("← BACK", "#4D3F87", "#ad7bff", "#290D48")

        start.setFixedSize(200, 70)
        stop.setFixedSize(200, 70)
        change.setFixedSize(200, 70)
        b_btn.setFixedSize(200, 70)

        start.clicked.connect(self.start_with_loading)
        stop.clicked.connect(self.stop_system)
        change.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        b_btn.clicked.connect(lambda: self.stack.setCurrentIndex(4))

        btn_layout.addStretch()
        btn_layout.addWidget(b_btn)
        btn_layout.addWidget(change)
        btn_layout.addWidget(stop)
        btn_layout.addWidget(start)
        btn_layout.addStretch()

        btn_container.setLayout(btn_layout)
        main_layout.addWidget(btn_container, 2)

        page.setLayout(main_layout)
        self.stack.addWidget(page)

    # Update alert display box -------------------------------------------
    def update_alert_box(self):
        try:
            if os.path.exists("alert.txt"):
                with open("alert.txt", "r") as f:
                    content = f.read().strip()

                if content:
                    self.alert_box.setText(content)
                else:
                    self.alert_box.setText("...")
            else:
                self.alert_box.setText("...")

        except Exception as e:
            self.alert_box.setText("Error reading alerts")

    # Loading bar for admin logic -----------------------------------------------------------
    def start_with_loading(self):
        if hasattr(self, "admin_process") and self.admin_process:
            return

        if not self.email:
            self.status_box_main.setText("No email set")
            return

        self._progress_value = 0

        self.status_box_main.setText("[░░░░░░░░░░░░░░░░] 0% Setting everything up...")

        self.start_system()

        # smooth timer for bar
        self.timer = QTimer()
        self.timer.timeout.connect(self._loading_step)
        # FAST = smooth animation
        # 30, 50, 80, 100 are options to change if load bar to fast
        # Do higher number
        self.timer.start(50)   

    def _loading_step(self):
        # smooth increment, small steps = animation like
        self._progress_value += 0.8

        if self._progress_value >= 100:
            self._progress_value = 100
            self.timer.stop()

        # build bar
        total_blocks = 16
        filled = int((self._progress_value / 100) * total_blocks)
        empty = total_blocks - filled

        bar = "█" * filled + "░" * empty

        if self._progress_value < 100:
            self.status_box_main.setText(f"[{bar}] {int(self._progress_value)}% Setting everything up...")
        else:
            self.status_box_main.setText(f"[{bar}] 100% All Done!")

            self.status_box_main.setText("Aegis is now running and monitoring for falls!")

    # Start admin ------------------------------------------------------------------------------
    def start_system(self):
        if hasattr(self, "admin_process") and self.admin_process:
            return

        self.admin_stop_flag = multiprocessing.Value("b", False)

        self.admin_process = multiprocessing.Process(
            target=admin.run_admin,
            args=(self.email, self.admin_stop_flag)
        )

        self.admin_process.start()

    # Stop admin ------------------------------------------------------------------------------------------
    def stop_system(self):
        self.status_box_main.setText("You have put Aegis to sleep, it is no longer monitoring for falls.")

        if hasattr(self, "admin_stop_flag"):
            self.admin_stop_flag.value = True

        if hasattr(self, "admin_process") and self.admin_process:
            self.admin_process.join(timeout=2)

            if self.admin_process.is_alive():
                print("[SYSTEM UI] Force terminating admin...")
                self.admin_process.terminate()

            self.admin_process = None

    # Clean up for exit -------------------------------------------------
    def closeEvent(self, event):
        self.kill_everything()
        event.accept()

    # open screen index 7 -------------------------------------------------------------------------
    def open_video_screen(self):
        self.update_video_list()
        self.stack.setCurrentIndex(7)

    # Video folder screen index 7 ===========================================
    def build_video_screen(self):
        page = QWidget()
        page.setStyleSheet("background-color: lightblue;")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left side (video + back button)---------------------------------
        left_side = QVBoxLayout()

        # Back button --------------------
        back_btn = AnimatedButton("← BACK", "#28a745", "#46f66f", "#15381D")
        back_btn.setFixedSize(180, 60)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(4))

        left_side.addWidget(back_btn, alignment=Qt.AlignLeft)

        # Video player -----------------------------
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(500, 400)
        self.video_widget.setStyleSheet("background-color: black; border-radius: 10px;")

        self.player = QMediaPlayer()
        self.audio = QAudioOutput()

        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_widget)

        left_side.addWidget(self.video_widget, stretch=1)

        # Status box
        self.status_box = QLabel("Select a video")
        self.status_box.setAlignment(Qt.AlignCenter)
        self.status_box.setFixedHeight(50)
        self.status_box.setStyleSheet("""
            background-color: white;
            color: black;
            font-size: 16px;
            border-radius: 10px;
        """)

        left_side.addWidget(self.status_box)

        # Right side (scrollable video list)--------------
        right_side = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(8)

        scroll_content.setLayout(self.scroll_layout)
        scroll.setWidget(scroll_content)

        right_side.addWidget(scroll)

        # 50/50 split screen
        main_layout.addLayout(left_side, 5)
        main_layout.addLayout(right_side, 5)

        page.setLayout(main_layout)

        self.stack.addWidget(page)
        self.video_page_index = self.stack.count() - 1

        self.update_video_list()

    # video screen play func -------------------------------------------------
    def play_video(self, path):
        self.status_box.setText(f"Playing: {os.path.basename(path)}")
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()

    # Video playlist update ------------------------------------------------------
    def update_video_list(self):
        folder = "archived_falls"
        os.makedirs(folder, exist_ok=True)

        # clear layout
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        videos = [
            f for f in sorted(os.listdir(folder))
            if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
        ]

        # Empty state -----------------------------------------
        if len(videos) == 0:
            no_videos = QLabel("No videos saved in folder")
            no_videos.setAlignment(Qt.AlignCenter)
            no_videos.setStyleSheet("""
                background-color: white;
                color: black;
                font-size: 18px;
                border-radius: 10px;
                padding: 20px;
            """)
            self.scroll_layout.addWidget(no_videos)
            return

        # Video buttons ---------------------------------------
        for file in videos:
            path = os.path.join(folder, file)

            btn = QPushButton(file)
            btn.setFixedHeight(60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2C4C6C;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 10px;
                }
                QPushButton:hover {
                    background-color: #0b7ae8;
                }
                QPushButton:pressed {
                    background-color: #1abc9c;
                }
            """)

            btn.clicked.connect(lambda checked, p=path: self.play_video(p))

            self.scroll_layout.addWidget(btn)

        self.scroll_layout.addStretch()

# Main entry =================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AegisApp()

    window.show()
    sys.exit(app.exec())
