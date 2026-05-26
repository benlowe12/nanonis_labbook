# =============================================================================
# nanonis_labbook/gui.py
#
# Tkinter GUI for the STM Labbook Tool.
# =============================================================================

import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox

from .config import CMAP_TOPO, CMAP_CURRENT, CMAP_AFM, CMAP_DIDV
from .config import TOPO_CHANNEL, CURRENT_CHANNEL, AFM_CHANNEL, DIDV_REF_CHANNEL
from .file_utils import get_file_path_sxm, get_file_path_dat
from .sxm_measurements import (
    save_sxm_topo, save_sxm_topo_drift_corrected,
    save_sxm_afm, save_sxm_current, save_sxm_didv_map,
)
from .dat_measurements import (
    save_dat_didv_spectrum, save_dat_z_spectrum, save_dat_kpfm,
)
from .combined_measurements import save_nc_measurement, save_kpfm_z_set, save_dat_compare_spectra
from .clipboard import paste_image_into_app


class LabbookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STM Labbook Tool")

        self.folder = tk.StringVar()

        tk.Label(root, text="Selected data folder:").pack(pady=(10, 0))
        tk.Label(root, textvariable=self.folder, wraplength=450).pack(pady=5)

        tk.Button(root, text="Choose Folder", command=self.choose_folder).pack(pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Topo image",            width=32,
                  command=lambda: self.run_measurement("topo")).pack(pady=2)
        tk.Button(button_frame, text="Drift-corrected TOPO",  width=32,
                  command=lambda: self.run_measurement("topo_drift")).pack(pady=2)
        tk.Button(button_frame, text="AFM image",             width=32,
                  command=lambda: self.run_measurement("afm")).pack(pady=2)
        tk.Button(button_frame, text="Current image",         width=32,
                  command=lambda: self.run_measurement("current")).pack(pady=2)
        tk.Button(button_frame, text="dI/dV map",             width=32,
                  command=lambda: self.run_measurement("didv_map")).pack(pady=2)
        tk.Button(button_frame, text="dI/dV spectrum",        width=32,
                  command=lambda: self.run_measurement("didv_spectrum")).pack(pady=2)
        tk.Button(button_frame, text="Z spectrum",            width=32,
                  command=lambda: self.run_measurement("z_spectrum")).pack(pady=2)
        tk.Button(button_frame, text="KPFM measurement",      width=32,
                  command=lambda: self.run_measurement("kpfm")).pack(pady=2)
        tk.Button(button_frame, text="Nc measurement",        width=32,
                  command=lambda: self.run_measurement("nc_measurement")).pack(pady=2)
        tk.Button(button_frame, text="KPFM(z) set",           width=32,
                  command=lambda: self.run_measurement("kpfm_z_set")).pack(pady=2)

        tk.Frame(button_frame, height=6).pack()  # spacer
        tk.Frame(button_frame, bg="gray", height=1, width=220).pack(pady=2)

        tk.Button(button_frame, text="Choose file(s) to paste", width=32,
                  command=self.run_choose_files).pack(pady=2)
        tk.Button(button_frame, text="Compare spectra", width=32,
                  command=self.run_compare_spectra).pack(pady=2)

        self.status = tk.Label(root, text="", fg="green")
        self.status.pack(pady=5)

    # -------------------------------------------------------------------------

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder.set(folder)
            self.status.config(text="Folder selected.", fg="blue")

    def select_multiple_files(self):
        files = filedialog.askopenfilenames(
            title="Select files for measurement",
            filetypes=[("All STM files", "*.sxm *.dat"), ("All files", "*.*")]
        )
        return list(files)

    # -------------------------------------------------------------------------
    # Reference image type prompt (used by DAT-based measurements)
    # -------------------------------------------------------------------------

    def prompt_reference_image_type(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Reference image type")
        dialog.grab_set()

        tk.Label(dialog, text="Type of image file?", font=("Arial", 12)).pack(pady=10)

        choice = tk.StringVar(value="")

        def select(option):
            choice.set(option)
            dialog.destroy()

        options = [
            "Const. curr STM",
            "Const. height STM",
            "AFM",
            "dI/dV",
        ]
        for opt in options:
            tk.Button(dialog, text=opt, width=25, command=lambda o=opt: select(o)).pack(pady=3)

        self.root.wait_window(dialog)
        return choice.get()

    def image_type_to_channel_and_cmap(self, ref_type):
        """Map a reference image type label to the corresponding channel and colourmap."""
        mapping = {
            "Const. curr STM":   (TOPO_CHANNEL,     CMAP_TOPO),
            "Const. height STM": (CURRENT_CHANNEL,   CMAP_CURRENT),
            "AFM":               (AFM_CHANNEL,        CMAP_AFM),
            "dI/dV":             (DIDV_REF_CHANNEL,   CMAP_DIDV),
        }
        return mapping.get(ref_type, (TOPO_CHANNEL, CMAP_TOPO))

    # -------------------------------------------------------------------------
    # Choose file(s) to paste — measurement type selector and file pickers
    # -------------------------------------------------------------------------

    def prompt_measurement_type(self):
        """Dialog for the user to select which measurement type to process."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select measurement type")
        dialog.grab_set()

        tk.Label(dialog, text="Measurement type?", font=("Arial", 12)).pack(pady=10)

        choice = tk.StringVar(value="")

        def select(option):
            choice.set(option)
            dialog.destroy()

        # SXM-based options
        tk.Label(dialog, text="— Image —", fg="gray").pack()
        sxm_options = [
            ("Topo image",           "topo"),
            ("Drift-corrected TOPO", "topo_drift"),
            ("AFM image",            "afm"),
            ("Current image",        "current"),
            ("dI/dV map",            "didv_map"),
        ]
        for label, key in sxm_options:
            tk.Button(dialog, text=label, width=25,
                      command=lambda k=key: select(k)).pack(pady=2)

        # DAT-based options
        tk.Label(dialog, text="— Spectroscopy —", fg="gray").pack(pady=(6, 0))
        dat_options = [
            ("dI/dV spectrum", "didv_spectrum"),
            ("Z spectrum",     "z_spectrum"),
            ("KPFM",           "kpfm"),
        ]
        for label, key in dat_options:
            tk.Button(dialog, text=label, width=25,
                      command=lambda k=key: select(k)).pack(pady=2)

        tk.Frame(dialog, height=4).pack()
        self.root.wait_window(dialog)
        return choice.get()

    def run_choose_files(self):
        """Handler for the 'Choose file(s) to paste' button."""
        try:
            folder = self.folder.get()
            if not folder:
                messagebox.showerror("Error", "Please select a folder first.")
                return

            labbook_folder = os.path.join(folder, "labbook")
            os.makedirs(labbook_folder, exist_ok=True)

            measurement_type = self.prompt_measurement_type()
            if not measurement_type:
                messagebox.showinfo("Cancelled", "No measurement type selected.")
                return

            SXM_TYPES = ["topo", "topo_drift", "afm", "current", "didv_map"]
            DAT_TYPES  = ["didv_spectrum", "z_spectrum", "kpfm"]

            if measurement_type in SXM_TYPES:
                # Single SXM file picker
                file_path_sxm = filedialog.askopenfilename(
                    title="Select SXM file",
                    filetypes=[("SXM files", "*.sxm"), ("All files", "*.*")],
                )
                if not file_path_sxm:
                    messagebox.showinfo("Cancelled", "No file selected.")
                    return

                if measurement_type == "topo":
                    img = save_sxm_topo(file_path_sxm, labbook_folder)
                elif measurement_type == "topo_drift":
                    img = save_sxm_topo_drift_corrected(file_path_sxm, labbook_folder)
                elif measurement_type == "afm":
                    img = save_sxm_afm(file_path_sxm, labbook_folder)
                elif measurement_type == "current":
                    img = save_sxm_current(file_path_sxm, labbook_folder)
                elif measurement_type == "didv_map":
                    img = save_sxm_didv_map(file_path_sxm, labbook_folder)

            elif measurement_type in DAT_TYPES:
                # Reference image type prompt (same as regular DAT flow)
                ref_type = self.prompt_reference_image_type()
                if not ref_type:
                    messagebox.showinfo("Cancelled", "No reference image type selected.")
                    return

                channel, cmap = self.image_type_to_channel_and_cmap(ref_type)

                # File picker — one DAT required, SXM optional
                files = filedialog.askopenfilenames(
                    title="Select one DAT file (and optionally one SXM file)",
                    filetypes=[("STM files", "*.sxm *.dat"), ("All files", "*.*")],
                )
                if not files:
                    messagebox.showinfo("Cancelled", "No files selected.")
                    return

                sxm_files = [f for f in files if f.endswith(".sxm")]
                dat_files  = [f for f in files if f.endswith(".dat")]

                if len(dat_files) != 1:
                    messagebox.showerror(
                        "Error",
                        "Please select exactly one .dat file (SXM is optional)."
                    )
                    return

                if len(sxm_files) > 1:
                    messagebox.showerror(
                        "Error",
                        "Please select at most one .sxm file."
                    )
                    return

                file_path_dat = dat_files[0]
                file_path_sxm = sxm_files[0] if sxm_files else None

                if measurement_type == "didv_spectrum":
                    img = save_dat_didv_spectrum(file_path_dat, file_path_sxm, labbook_folder, channel, cmap)
                elif measurement_type == "z_spectrum":
                    img = save_dat_z_spectrum(file_path_dat, file_path_sxm, labbook_folder, channel, cmap)
                elif measurement_type == "kpfm":
                    img = save_dat_kpfm(file_path_dat, file_path_sxm, labbook_folder, channel, cmap)

            time.sleep(1)
            paste_image_into_app(img)
            os.remove(img)

        except Exception as e:
            import traceback
            messagebox.showerror(
                "Error",
                f"Something went wrong:\n{e}\n\n{traceback.format_exc()}"
            )

    # -------------------------------------------------------------------------
    # Compare spectra
    # -------------------------------------------------------------------------

    def run_compare_spectra(self):
        """Handler for the Compare spectra button."""
        try:
            folder = self.folder.get()
            if not folder:
                messagebox.showerror("Error", "Please select a folder first.")
                return

            labbook_folder = os.path.join(folder, "labbook")
            os.makedirs(labbook_folder, exist_ok=True)

            # Step 1: measurement type
            spec_type = self.prompt_compare_type()
            if not spec_type:
                messagebox.showinfo("Cancelled", "No measurement type selected.")
                return

            # Step 2: select multiple DAT files
            files = filedialog.askopenfilenames(
                title="Select DAT files to compare",
                filetypes=[("DAT files", "*.dat"), ("All files", "*.*")],
            )
            if not files:
                messagebox.showinfo("Cancelled", "No files selected.")
                return

            img = save_dat_compare_spectra(list(files), labbook_folder, spec_type)

            time.sleep(1)
            paste_image_into_app(img)
            os.remove(img)

        except Exception as e:
            import traceback
            messagebox.showerror(
                "Error",
                f"Something went wrong:\n{e}\n\n{traceback.format_exc()}"
            )

    def prompt_compare_type(self):
        """Dialog to select which spectroscopy type to compare."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Compare: select type")
        dialog.grab_set()

        tk.Label(dialog, text="Measurement type to compare?", font=("Arial", 12)).pack(pady=10)

        choice = tk.StringVar(value="")

        def select(option):
            choice.set(option)
            dialog.destroy()

        options = [
            ("dI/dV spectrum", "didv_spectrum"),
            ("Z spectrum",     "z_spectrum"),
            ("KPFM",           "kpfm"),
        ]
        for label, key in options:
            tk.Button(dialog, text=label, width=25,
                      command=lambda k=key: select(k)).pack(pady=3)

        tk.Frame(dialog, height=4).pack()
        self.root.wait_window(dialog)
        return choice.get()

    # -------------------------------------------------------------------------
    # Main dispatcher
    # -------------------------------------------------------------------------

    def run_measurement(self, measurement_type):
        try:
            folder = self.folder.get()
            if not folder:
                messagebox.showerror("Error", "Please select a folder first.")
                return

            labbook_folder = os.path.join(folder, "labbook")
            os.makedirs(labbook_folder, exist_ok=True)

            # --- SXM-based measurements ---
            if measurement_type in ["topo", "topo_drift", "afm", "current", "didv_map"]:
                file_path_sxm = get_file_path_sxm(folder)
                if not file_path_sxm:
                    messagebox.showinfo("Info", "No SXM files found.")
                    return

                if measurement_type == "topo":
                    img = save_sxm_topo(file_path_sxm, labbook_folder)
                elif measurement_type == "topo_drift":
                    img = save_sxm_topo_drift_corrected(file_path_sxm, labbook_folder)
                elif measurement_type == "afm":
                    img = save_sxm_afm(file_path_sxm, labbook_folder)
                elif measurement_type == "current":
                    img = save_sxm_current(file_path_sxm, labbook_folder)
                elif measurement_type == "didv_map":
                    img = save_sxm_didv_map(file_path_sxm, labbook_folder)

            # --- DAT-based measurements ---
            elif measurement_type in ["didv_spectrum", "z_spectrum", "kpfm"]:
                file_path_dat = get_file_path_dat(folder)
                if not file_path_dat:
                    messagebox.showinfo("Info", "No DAT files found.")
                    return

                file_path_sxm = get_file_path_sxm(folder)  # None if not found; image panel left blank

                ref_type = self.prompt_reference_image_type()
                if not ref_type:
                    messagebox.showinfo("Cancelled", "No reference image type selected.")
                    return

                channel, cmap = self.image_type_to_channel_and_cmap(ref_type)

                if measurement_type == "didv_spectrum":
                    img = save_dat_didv_spectrum(file_path_dat, file_path_sxm, labbook_folder, channel, cmap)
                elif measurement_type == "z_spectrum":
                    img = save_dat_z_spectrum(file_path_dat, file_path_sxm, labbook_folder, channel, cmap)
                elif measurement_type == "kpfm":
                    img = save_dat_kpfm(file_path_dat, file_path_sxm, labbook_folder, channel, cmap)

            # --- Multi-file measurements ---
            elif measurement_type == "nc_measurement":
                files_path_list = self.select_multiple_files()
                if not files_path_list:
                    messagebox.showinfo("Cancelled", "No files selected.")
                    return
                img = save_nc_measurement(files_path_list, labbook_folder)

            elif measurement_type == "kpfm_z_set":
                files_path_list = self.select_multiple_files()
                if not files_path_list:
                    messagebox.showinfo("Cancelled", "No files selected.")
                    return
                img = save_kpfm_z_set(files_path_list, labbook_folder)

            else:
                messagebox.showerror("Error", f"Unknown measurement type: {measurement_type}")
                return

            time.sleep(1)
            paste_image_into_app(img)
            os.remove(img)

        except Exception as e:
            import traceback
            messagebox.showerror(
                "Error",
                f"Something went wrong:\n{e}\n\n{traceback.format_exc()}"
            )
