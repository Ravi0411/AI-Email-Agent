import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os


monitor_process = None


def update_agent_status():
    global monitor_process

    if monitor_process is not None:

        if monitor_process.poll() is None:

            status_label.config(
                text="Agent Status: RUNNING"
            )

        else:

            monitor_process = None

            status_label.config(
                text="Agent Status: STOPPED"
            )

            start_button.config(
                state=tk.NORMAL
            )

            stop_button.config(
                state=tk.DISABLED
            )

    root.after(
        1000,
        update_agent_status
    )


def start_agent():

    global monitor_process

    if (
        monitor_process is not None
        and monitor_process.poll() is None
    ):

        messagebox.showinfo(
            "AI Email Agent",
            "AI Email Agent is already running."
        )

        return

    try:

        if getattr(
            sys,
            "frozen",
            False
        ):

            application_folder = os.path.dirname(
                sys.executable
            )

            dist_folder = os.path.dirname(
                application_folder
            )

        else:

            project_folder = os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )

            dist_folder = os.path.join(
                project_folder,
                "dist"
            )

        monitor_file = os.path.join(
            dist_folder,
            "AI Email Agent Monitor",
            "AI Email Agent Monitor.exe"
        )

        if not os.path.exists(
            monitor_file
        ):

            messagebox.showerror(
                "Error",
                "AI Email Agent Monitor.exe was not found.\n\n"
                f"Expected location:\n{monitor_file}"
            )

            return

        monitor_process = subprocess.Popen(
            [
                monitor_file
            ],
            cwd=os.path.dirname(
                monitor_file
            )
        )

        status_label.config(
            text="Agent Status: RUNNING"
        )

        start_button.config(
            state=tk.DISABLED
        )

        stop_button.config(
            state=tk.NORMAL
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not start AI Email Agent.\n\n{error}"
        )


def stop_agent():

    global monitor_process

    if monitor_process is None:

        status_label.config(
            text="Agent Status: STOPPED"
        )

        start_button.config(
            state=tk.NORMAL
        )

        stop_button.config(
            state=tk.DISABLED
        )

        return

    if monitor_process.poll() is None:

        try:

            monitor_process.terminate()

            monitor_process.wait(
                timeout=5
            )

        except subprocess.TimeoutExpired:

            monitor_process.kill()

    monitor_process = None

    status_label.config(
        text="Agent Status: STOPPED"
    )

    start_button.config(
        state=tk.NORMAL
    )

    stop_button.config(
        state=tk.DISABLED
    )


def close_application():

    global monitor_process

    if (
        monitor_process is not None
        and monitor_process.poll() is None
    ):

        try:

            monitor_process.terminate()

            monitor_process.wait(
                timeout=5
            )

        except subprocess.TimeoutExpired:

            monitor_process.kill()

    monitor_process = None

    root.destroy()


# --------------------------------------------------
# Main Window
# --------------------------------------------------

root = tk.Tk()

root.title(
    "AI Email Agent"
)

root.geometry(
    "700x450"
)

root.resizable(
    False,
    False
)


# --------------------------------------------------
# Title
# --------------------------------------------------

title_label = tk.Label(
    root,
    text="AI Email Agent",
    font=("Arial", 24, "bold")
)

title_label.pack(
    pady=30
)


# --------------------------------------------------
# Agent Status
# --------------------------------------------------

status_label = tk.Label(
    root,
    text="Agent Status: STOPPED",
    font=("Arial", 14)
)

status_label.pack(
    pady=10
)


# --------------------------------------------------
# Gmail Status
# --------------------------------------------------

gmail_label = tk.Label(
    root,
    text="Gmail: Connected ✓",
    font=("Arial", 12)
)

gmail_label.pack(
    pady=5
)


# --------------------------------------------------
# Gemini Status
# --------------------------------------------------

gemini_label = tk.Label(
    root,
    text="Gemini AI: Connected ✓",
    font=("Arial", 12)
)

gemini_label.pack(
    pady=5
)


# --------------------------------------------------
# Start Button
# --------------------------------------------------

start_button = tk.Button(
    root,
    text="Start Agent",
    font=("Arial", 12, "bold"),
    width=20,
    command=start_agent
)

start_button.pack(
    pady=20
)


# --------------------------------------------------
# Stop Button
# --------------------------------------------------

stop_button = tk.Button(
    root,
    text="Stop Agent",
    font=("Arial", 12, "bold"),
    width=20,
    command=stop_agent,
    state=tk.DISABLED
)

stop_button.pack(
    pady=5
)


# --------------------------------------------------
# Handle Window Close
# --------------------------------------------------

root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# --------------------------------------------------
# Monitor Agent Process
# --------------------------------------------------

root.after(
    1000,
    update_agent_status
)


# --------------------------------------------------
# Start Application
# --------------------------------------------------

root.mainloop()