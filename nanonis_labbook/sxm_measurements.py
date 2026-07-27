# =============================================================================
# nanonis_labbook/sxm_measurements.py
#
# Functions for reading .sxm files and saving labbook images.
# =============================================================================

import os
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
import nanonispy2 as nanonispy
from matplotlib_scalebar.scalebar import ScaleBar

from .config import (
    TOPO_CHANNEL, CURRENT_CHANNEL, AFM_CHANNEL, DIDV_MAP_CHANNEL,
    CMAP_TOPO, CMAP_CURRENT, CMAP_AFM, CMAP_DIDV,
)
from .image_utils import line_poly_detrend, overlay_text


# -----------------------------------------------------------------------------
# Generic SXM save
# -----------------------------------------------------------------------------

def save_sxm_generic(file_path_sxm, labbook_folder, title_prefix="SXM image",
                     channel=None, cmap="gray", overlay_text_str=None,
                     header_line=None, apply_plane_fit=False):

    scan_data = nanonispy.read.Scan(file_path_sxm)
    header = scan_data.header

    # Select channel
    if channel is None:
        channel = list(scan_data.signals.keys())[0]
    image = scan_data.signals[channel]['forward']

    # Optional drift correction
    if apply_plane_fit:
        image = line_poly_detrend(image)

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
    dx = 1  # Calibrated via extent argument
    scalebar = ScaleBar(
        dx=dx, length_fraction=0.3,
        font_properties=font_properties,
        frameon=True, box_color='w', box_alpha=0.5,
        location=3, color='k', sep=1, scale_loc='top',
    )

    base = os.path.basename(file_path_sxm)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.imshow(image, origin='lower', cmap=cmap, extent=extent)
    ax.add_artist(scalebar)

    if header_line:
        ax.set_title(header_line)
    ax.axis("off")

    if overlay_text_str:
        overlay_text(ax, overlay_text_str)

    img_path = os.path.join(
        labbook_folder,
        f"{base}_{title_prefix.replace(' ', '_')}_{date_str}.png"
    )
    plt.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close()

    return img_path


# -----------------------------------------------------------------------------
# Specific SXM measurement types
# -----------------------------------------------------------------------------

def save_sxm_topo(file_path_sxm, labbook_folder):
    scan_data = nanonispy.read.Scan(file_path_sxm)
    bias = float(scan_data.header["bias"]) * 1e3
    curr = float(scan_data.header["z-controller>setpoint"]) * 1e12
    overlay_text_str = r"$V_\mathrm{b}$ = %.1f mV, $I_\mathrm{t}$ = %.1f pA" % (bias, curr)
    header_line = f"TOPO: {os.path.basename(file_path_sxm)}"

    return save_sxm_generic(
        file_path_sxm, labbook_folder,
        title_prefix="Topo image",
        channel=TOPO_CHANNEL,
        cmap=CMAP_TOPO,
        overlay_text_str=overlay_text_str,
        header_line=header_line,
        apply_plane_fit=False,
    )


def save_sxm_topo_drift_corrected(file_path_sxm, labbook_folder):
    scan_data = nanonispy.read.Scan(file_path_sxm)
    bias = float(scan_data.header["bias"]) * 1e3
    curr = float(scan_data.header["z-controller>setpoint"]) * 1e12
    overlay_text_str = r"$V_\mathrm{b}$ = %.1f mV, $I_\mathrm{t}$ = %.1f pA" % (bias, curr)
    header_line = f"Z-DRIFT-CORRECTED TOPO: {os.path.basename(file_path_sxm)}"

    return save_sxm_generic(
        file_path_sxm, labbook_folder,
        title_prefix="Drift-corrected topo",
        channel=TOPO_CHANNEL,
        cmap=CMAP_TOPO,
        overlay_text_str=overlay_text_str,
        header_line=header_line,
        apply_plane_fit=True,
    )


def save_sxm_afm(file_path_sxm, labbook_folder):
    header_line = f"AFM: {os.path.basename(file_path_sxm)}"

    return save_sxm_generic(
        file_path_sxm, labbook_folder,
        title_prefix="AFM image",
        channel=AFM_CHANNEL,
        cmap=CMAP_AFM,
        overlay_text_str=None,
        header_line=header_line,
        apply_plane_fit=False,
    )


def save_sxm_current(file_path_sxm, labbook_folder):
    scan_data = nanonispy.read.Scan(file_path_sxm)
    bias = float(scan_data.header["bias"]) * 1e3
    overlay_text_str = r"$V_\mathrm{b}$ = %.1f mV" % bias
    header_line = f"CURRENT: {os.path.basename(file_path_sxm)}"

    return save_sxm_generic(
        file_path_sxm, labbook_folder,
        title_prefix="Current image",
        channel=CURRENT_CHANNEL,
        cmap=CMAP_CURRENT,
        overlay_text_str=overlay_text_str,
        header_line=header_line,
        apply_plane_fit=False,
    )


def save_sxm_didv_map(file_path_sxm, labbook_folder):
    scan_data = nanonispy.read.Scan(file_path_sxm)
    bias = float(scan_data.header["bias"]) * 1e3
    overlay_text_str = r"$V_\mathrm{b}$ = %.1f mV" % bias
    header_line = f"dIdV: {os.path.basename(file_path_sxm)}"

    return save_sxm_generic(
        file_path_sxm, labbook_folder,
        title_prefix="dIdV map",
        channel=DIDV_MAP_CHANNEL,
        cmap=CMAP_DIDV,
        overlay_text_str=overlay_text_str,
        header_line=header_line,
        apply_plane_fit=False,
    )
