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
        self.root.title("Admin Dashboard")

        self.make_fullscreen()

        self.user_email = tk.StringVar()
        self.text_box = None
        self.video_text = None
        self.update_terminal_job = None
        self.update_video_job = None

        self.create_input_screen()
        self.root.mainloop()

    # Fullscreen
    def make_fullscreen(self):
        system = platform.system()
        if system == "Windows":
            self.root.state('zoomed')
        else:
            self.root.attributes('-fullscreen', True)

        self.root.bind("<Escape>", lambda e: self.root.attributes('-fullscreen', False))

    # Input screen for user to enter email
    def create_input_screen(self):
        self.clear_screen()
        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        tk.Label(frame, text="Enter email for notifications:", font=("Arial", 24)).pack(pady=10)
        entry = tk.Entry(frame, textvariable=self.user_email, font=("Arial", 24), width=30)
        entry.pack(pady=10)
        entry.focus_set()  # Puts cursor on input so user can just type in right away
        tk.Button(frame, text="Submit", font=("Arial", 24), command=self.confirm_input).pack(pady=10)

        self.root.bind("<Return>", lambda e: self.confirm_input())

    # For email confrim
    def confirm_input(self):
        email = self.user_email.get().strip()
        if not email:
            messagebox.showwarning("Warning", "Enter an email!")
            return

        if messagebox.askyesno("Confirm", f"You entered:\n\n{email}\nIs this correct?"):
            self.root.unbind("<Return>") # unbind enter key from email confim button
            self.create_main_screen()
            self.root.bind("<Return>", lambda e: self.end_program()) # To binf it to exit button

            # Start admin process
            threading.Thread(target=admin.run_admin, args=(email,), daemon=True).start()

            # Start UI updates
            self.update_terminal()
            self.update_video_list_display()

    # Show terminal and video logs
    def create_main_screen(self):
        self.clear_screen()

        # Draggable split
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill="both", expand=True)

        # LEFT: Terminal
        left_frame = tk.Frame(self.paned, bg="black")
        self.paned.add(left_frame, minsize=300)

        self.text_box = tk.Text(left_frame, bg="black", fg="lime", font=("Courier", 16))
        self.text_box.pack(fill="both", expand=True)

        # RIGHT: Video list
        right_frame = tk.Frame(self.paned)
        self.paned.add(right_frame, minsize=200)

        tk.Label(right_frame, text="Videos in Folder:", font=("Arial", 20)).pack(pady=5)

        self.video_text = tk.Text(right_frame, font=("Courier", 14))
        self.video_text.pack(fill="both", expand=True, pady=5)

        # End Program button
        tk.Button(right_frame, text="End Program", font=("Arial", 16),
                  bg="red", fg="white", command=self.end_program).pack(pady=10)

        # Set initial 70/30 split
        self.root.update_idletasks()
        total_width = self.root.winfo_width()
        self.paned.sash_place(0, int(total_width * 0.7), 0)

    # Update terminal
    def update_terminal(self):
        if self.text_box and os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                content = f.read()

            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, content)
            self.text_box.see(tk.END)

        self.update_terminal_job = self.root.after(1000, self.update_terminal)

    # Update video list
    def update_video_list_display(self):
        if self.video_text and os.path.exists(VIDEO_LIST_FILE):
            with open(VIDEO_LIST_FILE, "r", encoding="utf-8") as f:
                content = f.read()

            self.video_text.delete(1.0, tk.END)
            self.video_text.insert(tk.END, content)

        self.update_video_job = self.root.after(1000, self.update_video_list_display)

    # End the program
    def end_program(self):
        # Stop updates
        if self.update_terminal_job:
            self.root.after_cancel(self.update_terminal_job)
        if self.update_video_job:
            self.root.after_cancel(self.update_video_job)

        # Clear logs
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("")

        if os.path.exists(VIDEO_LIST_FILE):
            with open(VIDEO_LIST_FILE, "w", encoding="utf-8") as f:
                f.write("")

        messagebox.showinfo("Program Ended", "Logs cleared.")

        if messagebox.askyesno("Exit", "Close UI?"):
            self.root.destroy()

    # Clear screen
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    AdminUI()
