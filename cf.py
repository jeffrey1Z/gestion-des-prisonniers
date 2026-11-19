import asyncio
import threading
import time
from bleak import BleakScanner
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BluetoothScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scanner Bluetooth avec RSSI")
        self.root.geometry("600x500")

        self.devices = []
        self.selected_device = None
        self.rssi_values = []

        # Widgets
        self.scan_button = ttk.Button(root, text="🔍 Scanner", command=self.start_scan)
        self.scan_button.pack(pady=10)

        self.device_listbox = tk.Listbox(root, height=10)
        self.device_listbox.pack(fill=tk.BOTH, expand=True, padx=10)
        self.device_listbox.bind("<<ListboxSelect>>", self.on_device_select)

        self.start_track_button = ttk.Button(root, text="📈 Suivre le RSSI", command=self.start_tracking, state=tk.DISABLED)
        self.start_track_button.pack(pady=10)

        # Graph
        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

    def start_scan(self):
        threading.Thread(target=self._scan_devices).start()

    def _scan_devices(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        devices = loop.run_until_complete(BleakScanner.discover())
        self.devices = devices

        self.device_listbox.delete(0, tk.END)
        for d in devices:
            line = f"{d.name or 'Inconnu'} - {d.address} - RSSI: {d.rssi} dBm"
            self.device_listbox.insert(tk.END, line)

    def on_device_select(self, event):
        selection = self.device_listbox.curselection()
        if selection:
            self.selected_device = self.devices[selection[0]]
            self.start_track_button.config(state=tk.NORMAL)

    def start_tracking(self):
        if not self.selected_device:
            messagebox.showwarning("Attention", "Aucun appareil sélectionné.")
            return

        self.rssi_values.clear()
        threading.Thread(target=self._track_rssi).start()

    def _track_rssi(self):
        for _ in range(30):  # suivre pendant 30 secondes
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            devices = loop.run_until_complete(BleakScanner.discover())
            for d in devices:
                if d.address == self.selected_device.address:
                    self.rssi_values.append(d.rssi)
                    break
            time.sleep(1)
            self.update_plot()

    def update_plot(self):
        self.ax.clear()
        self.ax.plot(self.rssi_values, marker='o')
        self.ax.set_title("Évolution RSSI")
        self.ax.set_xlabel("Temps (s)")
        self.ax.set_ylabel("RSSI (dBm)")
        self.canvas.draw()

# Lancement de l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = BluetoothScannerApp(root)
    root.mainloop()
