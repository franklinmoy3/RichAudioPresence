import asyncio
from queue import Queue
import time

from secrets import app_id
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
        while True:
            time.sleep(5/10)
            self.update_activity()
            self.instance.run_callbacks()

    def update_activity(self):
        media_info = asyncio.run(wrt.get_media_info())
        if media_info == str("No active media"):
            self.activity_manager.clear_activity(self.callback)
            self.root.event_generate("<<UpdateEvent>>")
            return
        activity = dsdk.Activity()
        activity.state = str(media_info['artist'])
        activity.details = f"Listening to {media_info['title']}"
        self.activity_manager.update_activity(activity, self.callback)
        self.queue.put(media_info)
        self.root.event_generate("<<UpdateEvent>>")

    def callback(self, result):
        if result == dsdk.Result.ok:
            pass
            # print("Activity Set!")
        else:
            raise Exception(result)


class GUI(tk.Frame):
    def __init__(self, root: tk.Tk):
        # Tkinter window setup
        tk.Frame.__init__(self, root)
        self.root = root
        self.root.title("Rich Audio Presence")

        self.menu_bar = tk.Menu(self.root)
        self.file = tk.Menu(self.menu_bar, tearoff=1)
        self.file.add_command(label="Settings")
        self.file.add_command(label="Quit", command=self.root.quit)
        self.help = tk.Menu(self.menu_bar, tearoff=1)
        self.help.add_command(label="Manual")
        self.help.add_command(label="About")

        self.status_string = tk.StringVar(value="Initializing...")
        self.song_string = tk.StringVar(value="None")
        self.artist_string = tk.StringVar(value="None")

        self.status_header = ttk.Label(self.root, text="Playback Status")
        self.status_label = ttk.Label(self.root,
                                      textvariable=self.status_string)
        self.song_header = ttk.Label(self.root, text="Song")
        self.song_label = ttk.Label(self.root, textvariable=self.song_string)
        self.artist_header = ttk.Label(self.root, text="Artist")
        self.artist_label = ttk.Label(self.root,
                                      textvariable=self.artist_string)

        self.root.bind("<<UpdateEvent>>", self.update_strings)

        # Create shared queue and separate thread for discord updater
        self.queue = Queue()
        discord_thread = DiscordThread(self.root, self.queue)
        discord_thread.start()

    def update_strings(self, event):
        if self.queue.empty():
            self.status_string = "No active media"
            self.song_string = ""
            self.artist_string = ""
        else:
            media_info = self.queue.get()
            self.status_string = "Now Playing"
            self.song_string = media_info['title']
            self.artist_string = media_info['artist']
            self.queue.task_done()


if __name__ == "__main__":
    root = tk.Tk()
    GUI(root)
    root.mainloop()
