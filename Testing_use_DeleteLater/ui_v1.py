# Just for testing
# Last edited by: Julia
# Last updated date: Fri Apr 4 2026
import tkinter as tk # UI framework
from tkinter import messagebox # To make popup message box
import threading # So UI doesn't freeze whie admin.py runs in background
import os # To read the log txt files
import platform # Detects what system its on for fullscreen
import admin # connect to admin.py

# The log names for the termial and video activity to be used in UI
LOG_FILE = "admin_log.txt"
VIDEO_LIST_FILE = "video_list.txt"

# Get UI started
class AdminUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aegis")

        self.make_fullscreen()

        self.user_email = tk.StringVar()
        self.text_box = None
        self.video_text = None

        self.update_terminal_job = None
        self.update_video_job = None

        self.create_title_screen()
        self.root.mainloop()

    # Fullscreen
    def make_fullscreen(self):
        system = platform.system()
        if system == "Windows":
            self.root.state('zoomed')
        else:
            self.root.attributes('-fullscreen', True)

        self.root.bind("<Escape>", lambda e: self.root.attributes('-fullscreen', False))

    # Title screen
    def create_title_screen(self):
        self.clear_screen()

        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        tk.Label(frame, text="Aegis",
                 font=("Arial", 40)).pack(pady=40)

        tk.Label(frame, text="Your private Ai fall detector",
                 font=("Arial", 30)).pack(pady=40)

        tk.Label(frame, text="Press ENTER to continue",
                 font=("Arial", 20)).pack(pady=20)

        tk.Button(frame, text="ENTER", font=("Arial", 25), bg="green", fg="white", width=15, height=2,
                command=self.create_warning_screen).pack(pady=30)
        self.root.bind("<Return>", lambda e: self.create_warning_screen())

    # Warning screen
    def create_warning_screen(self):
        self.clear_screen()
        self.root.unbind("<Return>")

        # Main vertical frame
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=50, pady=50)

        # Top 80%: Scrollable warning text
        top_frame = tk.Frame(frame)
        top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.8)

        scroll = tk.Scrollbar(top_frame)
        scroll.pack(side="right", fill="y")

        warning_text_widget = tk.Text(top_frame, font=("Arial", 18), wrap="word",
                                    yscrollcommand=scroll.set)
        warning_text_widget.pack(fill="both", expand=True)

        scroll.config(command=warning_text_widget.yview)

        # Load warning content from a text file
        warning_file = "warning_text.txt"
        if os.path.exists(warning_file):
            with open(warning_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "WARNING!\n\nThis system monitors for falls. Press EXIT to close the program."

        warning_text_widget.insert(tk.END, content)
        warning_text_widget.config(state="disabled")  # read-only

        # Bottom 20%: Buttons
        bottom_frame = tk.Frame(frame)
        bottom_frame.place(relx=0, rely=0.8, relwidth=1, relheight=0.2)

        tk.Button(bottom_frame, text="Agree", font=("Arial", 24), bg="green", fg="white", width=15,
                command=self.create_instructions_screen).pack(side="left", expand=True, padx=50, pady=20)
        #self.root.bind("<Return>", lambda e: self.create_instructions_screen())

        tk.Button(bottom_frame, text="Exit", font=("Arial", 24), bg="red", fg="white", width=15,
                command=self.root.destroy).pack(side="right", expand=True, padx=50, pady=20)

    # Instructions screen
    def create_instructions_screen(self):
        self.clear_screen()
        self.root.unbind("<Return>")

        # Main vertical frame
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=50, pady=50)

        # Top 80%: Scrollable instructions text
        top_frame = tk.Frame(frame)
        top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.8)

        scroll = tk.Scrollbar(top_frame)
        scroll.pack(side="right", fill="y")

        instructions_text_widget = tk.Text(top_frame, font=("Arial", 18), wrap="word",
                                        yscrollcommand=scroll.set)
        instructions_text_widget.pack(fill="both", expand=True)

        scroll.config(command=instructions_text_widget.yview)

        # Load instructions content from a text file
        instructions_file = "instructions_text.txt"
        if os.path.exists(instructions_file):
            with open(instructions_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = (
                "Instructions:\n\n"
                "- System records video\n"
                "- AI checks for falls\n"
                "- Alerts are sent if a fall is detected\n"
                "- Videos are managed automatically\n\n"
                "Press NEXT to continue."
            )

        instructions_text_widget.insert(tk.END, content)
        instructions_text_widget.config(state="disabled")  # read-only

        # Bottom 20%: NEXT button
        bottom_frame = tk.Frame(frame)
        bottom_frame.place(relx=0, rely=0.8, relwidth=1, relheight=0.2)

        tk.Button(bottom_frame, text="ENTER", font=("Arial", 24), bg="green", fg="white", width=15,
                command=self.create_input_screen).pack(expand=True,  padx=50, pady=20)

        self.root.bind("<Return>", lambda e: self.create_input_screen())

    # Ask user for email input
    def create_input_screen(self):
        self.clear_screen()
        self.root.unbind("<Return>")

        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        tk.Label(frame, text="Enter email for notifications:",
                 font=("Arial", 24)).pack(pady=10)

        entry = tk.Entry(frame, textvariable=self.user_email,
                         font=("Arial", 24), width=30)
        entry.pack(pady=10)

        self.root.after(100, entry.focus_set)

        tk.Button(frame, text="Submit", font=("Arial", 24),
                  command=self.confirm_input).pack(pady=10)

        self.root.bind("<Return>", lambda e: self.confirm_input())

    # Confirm the email
    def confirm_input(self):
        email = self.user_email.get().strip()

        if not email:
            messagebox.showwarning("Warning", "Enter an email!")
            return

        if messagebox.askyesno("Confirm", f"You entered:\n\n{email}\nIs this correct?"):
            self.root.unbind("<Return>")

            self.create_main_screen()

            threading.Thread(target=admin.run_admin,
                             args=(email,), daemon=True).start()

            self.update_terminal()
            self.update_video_list_display()

    # Show terminal, video logs, show email and be able to change it
    def create_main_screen(self):
        self.clear_screen()

        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill="both", expand=True)

        # LEFT: Terminal
        left_frame = tk.Frame(self.paned, bg="black")
        self.paned.add(left_frame, minsize=300)

        self.text_box = tk.Text(left_frame, bg="black",
                                fg="lime", font=("Courier", 16))
        self.text_box.pack(fill="both", expand=True)

        # RIGHT: Video + controls
        right_frame = tk.Frame(self.paned)
        self.paned.add(right_frame, minsize=200)

        tk.Label(right_frame, text="Videos in Folder:",
                 font=("Arial", 18)).pack(pady=5)

        self.video_text = tk.Text(right_frame, font=("Courier", 14), height=10)
        self.video_text.pack(fill="both", expand=True, pady=5)

        # Email display
        tk.Label(right_frame, text="Current Email:",
                 font=("Arial", 16)).pack(pady=5)

        self.email_label = tk.Label(right_frame,
                                   text=self.user_email.get(),
                                   font=("Arial", 14))
        self.email_label.pack(pady=5)

        tk.Button(right_frame, text="Change Email",
                  font=("Arial", 14), bg="blue", fg="white",
                  command=self.create_input_screen).pack(pady=5)

        # End button
        tk.Button(right_frame, text="End Program",
                  font=("Arial", 16),
                  bg="red", fg="white",
                  command=self.end_program).pack(pady=10)

        # 70/30 split
        self.root.update_idletasks()
        total_width = self.root.winfo_width()
        self.paned.sash_place(0, int(total_width * 0.7), 0)

    # Update terminal log
    def update_terminal(self):
        if self.text_box and os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                content = f.read()

            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, content)
            self.text_box.see(tk.END)

        self.update_terminal_job = self.root.after(1000, self.update_terminal)

    # Update video list log
    def update_video_list_display(self):
        if self.video_text and os.path.exists(VIDEO_LIST_FILE):
            with open(VIDEO_LIST_FILE, "r", encoding="utf-8") as f:
                content = f.read()

            self.video_text.delete(1.0, tk.END)
            self.video_text.insert(tk.END, content)

        self.update_video_job = self.root.after(1000, self.update_video_list_display)

    # End program
    def end_program(self):
        if self.update_terminal_job:
            self.root.after_cancel(self.update_terminal_job)
        if self.update_video_job:
            self.root.after_cancel(self.update_video_job)

        if os.path.exists(LOG_FILE):
            open(LOG_FILE, "w").close()

        if os.path.exists(VIDEO_LIST_FILE):
            open(VIDEO_LIST_FILE, "w").close()

        messagebox.showinfo("Ended", "Logs cleared.")

        if messagebox.askyesno("Exit", "Close UI?"):
            self.root.destroy()

    # Clear screen
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    AdminUI()
