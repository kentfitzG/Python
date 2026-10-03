import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox

def download_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return

    folder = folder_entry.get().strip()
    if not folder:
        messagebox.showerror("Error", "Please choose a download folder")
        return

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": folder + "/%(title)s.%(ext)s"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", "Download complete!")
    except Exception as e:
        messagebox.showerror("Error", f"Download failed:\n{e}")

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)

# GUI Setup
root = tk.Tk()
root.title("YouTube Downloader (yt-dlp)")
root.geometry("500x200")

tk.Label(root, text="YouTube URL:").pack()
url_entry = tk.Entry(root, width=60)
url_entry.pack()

tk.Label(root, text="Download Folder:").pack()
folder_entry = tk.Entry(root, width=60)
folder_entry.pack()

tk.Button(root, text="Browse", command=choose_folder).pack(pady=5)
tk.Button(root, text="Download", command=download_video).pack(pady=10)

root.mainloop()
