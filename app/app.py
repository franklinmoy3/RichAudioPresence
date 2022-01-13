import asyncio
from queue import Queue
import time
import webbrowser

from secrets import app_id, small_image_key, large_image_key
import discordsdk as dsdk
import winrt_audio as wrt

import tkinter as tk
from tkinter import ttk
from threading import Thread


class DiscordThread(Thread):
    def __init__(self, root: tk.Tk, queue: Queue):
        super().__init__(daemon=True)
        self.queue = queue
        self.instance = dsdk.Discord(app_id, dsdk.CreateFlags.default)
        self.activity_manager = self.instance.get_activity_manager()
        self.root = root

    def run(self):
        """Entry point for this thread after __init__"""
        while True:
            time.sleep(5 / 10)
            self.update_activity()
            self.instance.run_callbacks()

    def update_activity(self):
        """Sets the users Discord activity based on media session"""
        media_info = asyncio.run(wrt.get_media_info())
        if media_info == str("No active media"):
            self.activity_manager.clear_activity(self.callback)
            self.root.event_generate("<<UpdateEvent>>")
            return
        activity = dsdk.Activity()
        activity.state = str(media_info["artist"])
        activity.details = f"Listening to {media_info['title']}"
        activity.assets = dsdk.model.ActivityAssets()
        activity.assets.large_image = str(large_image_key)
        activity.assets.large_text = "Rich Audio Presence"
        activity.assets.small_image = str(small_image_key)
        activity.assets.small_text = "Windows OS"
        self.activity_manager.update_activity(activity, self.callback)
        self.queue.put(media_info)
        self.root.event_generate("<<UpdateEvent>>")

    def callback(self, result):
        if result == dsdk.Result.ok:
            pass
            # print("Activity Set!")
        else:
            raise Exception(result)


class SettingsWindow(tk.Toplevel):
    """Class definition for the Settings window"""

    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent

        self.title("Settings")
        self.resizable(width=False, height=False)

        self.border = ttk.Frame(self, borderwidth=5, relief="ridge", width=250, height=250)
        self.border.pack()

        self.header_label = ttk.Label(self.border, text="Settings", font="TkDefaultFont 16 bold", justify=tk.LEFT)
        self.header_label.grid(row=0, column=0, columnspan=3)


class AboutWindow(tk.Toplevel):
    """Class definition for the About window"""

    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent

        self.title("About")
        self.resizable(width=False, height=False)

        self.border = ttk.Frame(
            self, borderwidth=5, relief="ridge", width=250, height=250
        )
        self.border.pack()

        self.header_label = ttk.Label(
            self.border, text="Rich Audio Presence", font="TkDefaultFont 16 bold", justify=tk.LEFT
        )
        self.header_label.grid(row=0, column=0, columnspan=4)
        self.version_label = ttk.Label(
            self.border, text="v0.7.0", font="TkDefaultFont 14", justify=tk.LEFT
        )
        self.version_label.grid(row=1, column=0)


class Root(tk.Tk):
    """Class definition the root tkinter window"""

    def __init__(self):
        super().__init__()

        self.title("RAP")
        self.resizable(width=False, height=False)

        # Menu bar
        menu_bar = tk.Menu(self)
        self["menu"] = menu_bar

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.open_settings_window)
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(menu=file_menu, label="File")

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(
            label="Manual",
            command=lambda: webbrowser.open(
                "https://github.com/franklinmoy3/RichAudioPresence"
            ),
        )
        help_menu.add_command(label="About", command=self.open_about_window)
        menu_bar.add_cascade(menu=help_menu, label="Help")

        # Frame layout
        root_frame = ttk.Frame(
            self, borderwidth=5, relief="ridge", width=400, height=400
        )
        root_frame.grid(row=0, column=0)

        # Frame content
        status_header = ttk.Label(
            root_frame, text="Playback Status", font="TkDefaultFont 16 bold"
        )
        self.status_string = tk.StringVar(value="Starting...")
        self.status_box = ttk.Entry(
            root_frame,
            textvariable=self.status_string,
            state=tk.DISABLED,
            justify=tk.CENTER,
        )
        status_header.grid(row=0, column=0, padx=15, pady=10)
        self.status_box.grid(row=1, column=0, columnspan=6, padx=15, pady=5)

        song_header = ttk.Label(root_frame, text="Song", font="TkDefaultFont 16 bold")
        self.song_string = tk.StringVar()
        self.song_box = ttk.Entry(
            root_frame,
            textvariable=self.song_string,
            state=tk.DISABLED,
            justify=tk.CENTER,
        )
        song_header.grid(row=2, column=0, padx=15, pady=10)
        self.song_box.grid(row=3, column=0, columnspan=6, padx=15, pady=5)

        artist_header = ttk.Label(
            root_frame, text="Artist", font="TkDefaultFont 16 bold"
        )
        self.artist_string = tk.StringVar()
        self.artist_box = ttk.Entry(
            root_frame,
            textvariable=self.artist_string,
            state=tk.DISABLED,
            justify=tk.CENTER,
        )
        artist_header.grid(row=4, column=0, padx=15, pady=10)
        self.artist_box.grid(row=5, column=0, columnspan=6, padx=15, pady=5)

        # Set up bindings
        self.bind("<<UpdateEvent>>", self.update_strings)

        # Create shared queue and separate thread for discord updater
        self.queue = Queue()
        discord_thread = DiscordThread(self, self.queue)
        discord_thread.start()

    def update_strings(self, event):
        """Routine to update the strings shown on the GUI"""
        if self.queue.empty():
            self.status_string.set("No active media")
            self.song_string.set("")
            self.artist_string.set("")
        else:
            media_info = self.queue.get()
            self.status_string.set("Now Playing")
            self.song_string.set(media_info["title"])
            self.artist_string.set(media_info["artist"])
            self.queue.task_done()

    def open_about_window(self):
        """Routine that opens an About window"""
        AboutWindow(self)

    def open_settings_window(self):
        """Routine that opens a Settings window"""
        SettingsWindow(self)


def main():
    root = Root()
    root.mainloop()


if __name__ == "__main__":
    main()
