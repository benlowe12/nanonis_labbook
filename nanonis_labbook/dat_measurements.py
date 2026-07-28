# =============================================================================
# nanonis_labbook/dat_measurements.py
#
# Functions for reading .dat spectroscopy files and saving labbook images.
# =============================================================================

import os
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
import nanonispy
from matplotlib_scalebar.scalebar import ScaleBar

from .config import (
    SPEC_BIAS_CHANNEL, SPEC_DIDV_CHANNEL,
    SPEC_Z_CHANNEL, SPEC_FREQ_SHIFT,
)
from .image_utils import overlay_text


# -----------------------------------------------------------------------------
# Generic DAT save (spectrum + context SXM image side-by-side)
# -----------------------------------------------------------------------------

def save_dat_generic(file_path_dat, file_path_sxm, labbook_folder,
                     channel, cmap, sweep_signal, y_signal,
                     spec_type="Spectrum",
                     overlay_text_str=None,
                     header_line=None,
                     xlabel="Sweep",
                     ylabel="Signal"):

    base = os.path.basename(file_path_dat)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    fig, (ax_img, ax_spec) = plt.subplots(1, 2, figsize=(11, 5))

    if file_path_sxm is not None:
        scan_data = nanonispy.read.Scan(file_path_sxm)
        header = scan_data.header

        # Select channel for context image
        if channel is None:
            channel = list(scan_data.signals.keys())[0]
        image = scan_data.signals[channel]['forward']

        # Correct scan orientation if scanning top->bottom
        if header['scan_dir'] == 'down':
            image = np.flipud(image)

        # Image extent in physical units
        extent = (
            header['scan_offset'][0] - header['scan_range'][0] / 2,
            header['scan_offset'][0] + header['scan_range'][0] / 2,
            header['scan_offset'][1] - header['scan_range'][1] / 2,
            header['scan_offset'][1] + header['scan_range'][1] / 2,
        )

        # Scalebar
        font_properties = {'size': 14}
        dx = 1
        scalebar = ScaleBar(
            dx=dx, length_fraction=0.3,
            font_properties=font_properties,
            frameon=True, box_color='w', box_alpha=0.5,
            location=3, color='k', sep=1, scale_loc='top',
        )

        # Spectrum position marker
        spec_data = nanonispy.read.Spec(file_path_dat)
        spec_header = spec_data.header
        x = float(spec_header['X (m)'])
        y = float(spec_header['Y (m)'])

        # Adjust for scan angle
        angle = float(scan_data.header['scan_angle']) * np.pi / 180
        x -= scan_data.header['scan_offset'][0]
        y -= scan_data.header['scan_offset'][1]
        x, y = (np.cos(angle) * x - np.sin(angle) * y,
                 np.sin(angle) * x + np.cos(angle) * y)
        x += scan_data.header['scan_offset'][0]
        y += scan_data.header['scan_offset'][1]

        # Left panel: SXM context image with filename as title
        ax_img.imshow(image, origin='lower', cmap=cmap, extent=extent)
        ax_img.add_artist(scalebar)
        ax_img.plot(x, y, 'o', markersize=8, markerfacecolor='r', markeredgecolor='w')
        ax_img.set_title(os.path.basename(file_path_sxm), fontsize=8)

    else:
        ax_img.set_title("Note: no SXM file found", fontsize=8, color="gray")

    ax_img.axis("off")

    # Right panel: spectrum
    ax_spec.plot(sweep_signal, y_signal)
    ax_spec.set_xlabel(xlabel)
    ax_spec.set_ylabel(ylabel)
    if header_line:
        ax_spec.set_title(header_line)
    ax_spec.grid(True)

    if overlay_text_str:
        overlay_text(ax_spec, overlay_text_str)

    img_path = os.path.join(
        labbook_folder,
        f"{base}_{spec_type.replace(' ', '_')}_{date_str}.png"
    )
    plt.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close()

    return img_path


# -----------------------------------------------------------------------------
# Specific DAT measurement types
# -----------------------------------------------------------------------------

def save_dat_didv_spectrum(file_path_dat, file_path_sxm, labbook_folder, channel, cmap):
    dat_data = nanonispy.read.Spec(file_path_dat)
    sweep_signal = dat_data.signals[SPEC_BIAS_CHANNEL] * 1e3
    y_signal = dat_data.signals[SPEC_DIDV_CHANNEL]
    header_line = f"dIdV SPECTRUM: {os.path.basename(file_path_dat)}"

    return save_dat_generic(
        file_path_dat, file_path_sxm, labbook_folder,
        channel=channel, cmap=cmap,
        sweep_signal=sweep_signal, y_signal=y_signal,
        spec_type="dIdV spectrum",
        overlay_text_str=None,
        header_line=header_line,
        xlabel='Bias (mV)',
        ylabel="dI/dV (arb. units)",
    )


def save_dat_z_spectrum(file_path_dat, file_path_sxm, labbook_folder, channel, cmap):
    dat_data = nanonispy.read.Spec(file_path_dat)
    sweep_signal = dat_data.signals[SPEC_Z_CHANNEL] * 1e10
    y_signal = dat_data.signals[SPEC_FREQ_SHIFT]
    header_line = f"Z SPECTRUM: {os.path.basename(file_path_dat)}"

    return save_dat_generic(
        file_path_dat, file_path_sxm, labbook_folder,
        channel=channel, cmap=cmap,
        sweep_signal=sweep_signal, y_signal=y_signal,
        spec_type="Z spectrum",
        overlay_text_str=None,
        header_line=header_line,
        xlabel=r"$Z (\mathrm{\AA})$",
        ylabel=r"$\Delta f$ (Hz)",
    )


def save_dat_kpfm(file_path_dat, file_path_sxm, labbook_folder, channel, cmap):
    dat_data = nanonispy.read.Spec(file_path_dat)
    sweep_signal = dat_data.signals[SPEC_BIAS_CHANNEL]
    y_signal = dat_data.signals[SPEC_FREQ_SHIFT]
    header_line = f"KPFM: {os.path.basename(file_path_dat)}"

    return save_dat_generic(
        file_path_dat, file_path_sxm, labbook_folder,
        channel=channel, cmap=cmap,
        sweep_signal=sweep_signal, y_signal=y_signal,
        spec_type="KPFM measurement",
        overlay_text_str=None,
        header_line=header_line,
        xlabel="Bias (V)",
        ylabel=r"$\Delta f$ (Hz)",
    )
