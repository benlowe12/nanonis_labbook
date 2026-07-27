# =============================================================================
# nanonis_labbook/combined_measurements.py
#
# Multi-file measurement functions: Nc combined measurement and KPFM(z) set.
# =============================================================================

import os
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
import nanonispy2 as nanonispy
from matplotlib_scalebar.scalebar import ScaleBar

from .config import (
    NC_IMAGE_CHANNEL, NC_SPEC_CHANNEL,
    SPEC_BIAS_CALC_CHANNEL, SPEC_FREQ_SHIFT,
    KPFM_FREQ_SHIFT_FWD, KPFM_FREQ_SHIFT_FWD_AVG,
    KPFM_FREQ_SHIFT_BWD, KPFM_FREQ_SHIFT_BWD_AVG,
)
from .image_utils import fit_function


# -----------------------------------------------------------------------------
# Nc combined measurement
# -----------------------------------------------------------------------------

def save_nc_measurement(files_path_list, labbook_folder):
    """
    Generates four panels:
      1. SXM image with spectrum position marker
      2. Z-spectroscopy curve
      3. Stack of Z-dependent d2I/dV2 bias spectra
      4. Colour map of the same spectra vs Z
    """
    fig, (ax_img, ax_Zspec, ax_specs, ax_map) = plt.subplots(
        1, 4, figsize=(20, 5), constrained_layout=True
    )

    dat_files = []
    files_with_z = []
    scan_data = None
    specs_name = ""

    # Pass 1: separate SXM and DAT files
    for file_path in files_path_list:
        file = os.path.basename(file_path)
        if file_path.endswith('.sxm'):
            im_filename = file[:-4]
            scan_data = nanonispy.read.Scan(file_path)
            scan_im = scan_data.signals[NC_IMAGE_CHANNEL]['forward']

            if scan_data.header['scan_dir'] == 'down':
                scan_im = np.flipud(scan_im)

            extent = (
                scan_data.header['scan_offset'][0] - scan_data.header['scan_range'][0] / 2,
                scan_data.header['scan_offset'][0] + scan_data.header['scan_range'][0] / 2,
                scan_data.header['scan_offset'][1] - scan_data.header['scan_range'][1] / 2,
                scan_data.header['scan_offset'][1] + scan_data.header['scan_range'][1] / 2,
            )

            font_properties = {'size': 14}
            dx = 1
            scalebar = ScaleBar(
                dx=dx, length_fraction=0.3,
                font_properties=font_properties,
                frameon=True, box_color='w', box_alpha=0.5,
                location=3, color='k', sep=1, scale_loc='top',
            )

            ax_img.imshow(scan_im, extent=extent, origin='lower', cmap='Purples_r')
            ax_img.add_artist(scalebar)
            ax_img.set_title(im_filename)

        elif file_path.endswith('.dat'):
            dat_files.append(file_path)

    # Pass 2: separate Z-spectroscopy and bias-spectroscopy DAT files
    for file_path in dat_files:
        file = os.path.basename(file_path)
        if "ZS" in file_path:
            Zspec_name = file[:-8]
            Zspec = nanonispy.read.Spec(file_path)

            freq_shift = Zspec.signals[SPEC_FREQ_SHIFT]
            z = Zspec.signals['Z (m)'] * 1e12
            z -= z[0]

            ax_Zspec.plot(z, freq_shift, 'o', color='k')
            ax_Zspec.set_xlim(z[0], z[-1])
            ax_Zspec.set_ylim(np.min(freq_shift) - 0.2, np.max(freq_shift) + 0.2)
            ax_Zspec.set_title(Zspec_name)

            x = float(Zspec.header['X (m)'])
            y = float(Zspec.header['Y (m)'])

            if scan_data is not None:
                angle = float(scan_data.header['scan_angle']) * np.pi / 180
                x -= scan_data.header['scan_offset'][0]
                y -= scan_data.header['scan_offset'][1]
                x, y = (np.cos(angle) * x - np.sin(angle) * y,
                         np.sin(angle) * x + np.cos(angle) * y)
                x += scan_data.header['scan_offset'][0]
                y += scan_data.header['scan_offset'][1]
                ax_img.plot(x, y, 'o', markersize=8,
                            markerfacecolor='r', markeredgecolor='w')

        else:
            specs_name = file[:-8]
            spec = nanonispy.read.Spec(file_path)
            Z = float(spec.header['Z (m)']) * 1e12
            files_with_z.append((Z, spec))

    # Sort bias spectra from smallest Z to largest Z
    files_sorted = sorted(files_with_z, key=lambda x: x[0])
    specs = [f[1] for f in files_sorted]
    Zs = [f[0] for f in files_sorted]

    no_of_files = len(specs)
    color_array = np.arange(0, no_of_files, 1)
    coloring_array = np.ndarray.flatten(color_array)
    colors = plt.cm.viridis(
        [(xx - np.min(coloring_array)) / (np.max(coloring_array) - np.min(coloring_array))
         for xx in coloring_array]
    )

    no_of_datapoints = np.size(specs[0].signals[SPEC_BIAS_CALC_CHANNEL])

    Zs = np.array(Zs)
    Zs -= Zs[0]

    bias = np.empty((no_of_files, no_of_datapoints))
    d2IdV2 = np.empty((no_of_files, no_of_datapoints))
    d2IdV2_norm = np.empty((no_of_files, no_of_datapoints))

    for i in range(len(specs)):
        ax_Zspec.vlines(Zs[i], -200, 200, color=colors[i], ls='--')

        bias[i] = specs[i].signals[SPEC_BIAS_CALC_CHANNEL]
        d2IdV2[i] = specs[i].signals[NC_SPEC_CHANNEL]
        d2IdV2_norm[i] = d2IdV2[i] / np.max(np.abs(d2IdV2[i]))

        if bias[i, 0] > bias[i, -1]:
            bias[i] = np.flip(bias[i])
            d2IdV2[i] = np.flip(d2IdV2[i])
            d2IdV2_norm[i] = np.flip(d2IdV2_norm[i])

        ax_specs.plot(bias[i], d2IdV2_norm[i] + 1.5 * i, 'o', color=colors[i])

    # Colour map panel
    map_extent = (bias[0, 0], bias[0, -1], Zs[0], Zs[-1])
    ax_map.imshow(
        d2IdV2_norm, extent=map_extent, origin='lower',
        aspect=2 * abs(bias[0, -1] / Zs[-1])
    )

    ax_img.axis("off")

    ax_Zspec.set_xlabel('Z (pm)')
    ax_Zspec.set_ylabel('Frequency shift (Hz)')
    ax_Zspec.grid(True)

    ax_specs.set_xlabel('Bias (V)')
    ax_specs.set_ylabel('$d^2I/dV^2$ (a.u.)')
    ax_specs.grid(True)
    ax_specs.set_title(specs_name)

    ax_map.set_ylabel('z (pm)')
    ax_map.set_xlabel('Bias (V)')
    ax_map.yaxis.set_label_position("right")
    ax_map.yaxis.tick_right()

    base = os.path.basename(specs_name)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    img_path = os.path.join(labbook_folder, f"{base}_Nc_meas_{date_str}.png")
    plt.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close()

    return img_path


# -----------------------------------------------------------------------------
# KPFM(z) set measurement
# -----------------------------------------------------------------------------

def save_kpfm_z_set(files_path_list, labbook_folder):
    """
    Plots parabolic KPFM measurements at multiple tip heights,
    fits each with a parabola, and plots V_CPD as a function of Z.
    """
    fig, (ax_specs, ax_VCPD) = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)

    files_with_z = []
    specs_name = ""

    for file_path in files_path_list:
        file = os.path.basename(file_path)
        if file_path.endswith('.dat'):
            specs_name = file[:-8]
            spec = nanonispy.read.Spec(file_path)
            Z = float(spec.header['Z (m)']) * 1e12
            files_with_z.append((Z, spec))

    files_sorted = sorted(files_with_z, key=lambda x: x[0])
    specs = [f[1] for f in files_sorted]
    Zs = np.array([f[0] for f in files_sorted])
    Zs -= Zs[0]

    V_CPDs = []
    uV_CPDs = []

    color_array = np.arange(0, np.size(specs), 1)
    coloring_array = np.ndarray.flatten(color_array)
    colors = plt.cm.viridis(
        [(xx - np.min(coloring_array)) / (np.max(coloring_array) - np.min(coloring_array))
         for xx in coloring_array]
    )

    # Determine which frequency shift signal name is present in this file
    if KPFM_FREQ_SHIFT_FWD in specs[0].signals.keys():
        delta_f_signal = KPFM_FREQ_SHIFT_FWD
        delta_f_signal_bwd = KPFM_FREQ_SHIFT_BWD
    elif KPFM_FREQ_SHIFT_FWD_AVG in specs[0].signals.keys():
        delta_f_signal = KPFM_FREQ_SHIFT_FWD_AVG
        delta_f_signal_bwd = KPFM_FREQ_SHIFT_BWD_AVG

    for i in range(len(specs)):
        bias = specs[i].signals['Bias calc (V)']
        delta_f = (specs[i].signals[delta_f_signal] + specs[i].signals[delta_f_signal_bwd]) / 2

        ax_specs.plot(bias, delta_f, 'o', markersize=2, color=colors[i])

        fit = fit_function(bias, delta_f)
        ax_specs.plot(bias, fit.best_fit, ls='--', color=colors[i])

        V_CPD = fit.params.valuesdict()['quad_b']
        V_CPDs.append(V_CPD)

        uV_CPD = fit.params['quad_b'].stderr
        uV_CPDs.append(uV_CPD)

        ax_VCPD.errorbar(
            Zs[i], V_CPD, uV_CPD,
            marker='o', markersize=10, color=colors[i], capsize=5, linestyle=''
        )

    ax_specs.set_xlabel('Bias (V)')
    ax_specs.set_ylabel(r'$\Delta f$ (Hz)')
    ax_specs.grid(True)
    ax_specs.set_title(specs_name)

    ax_VCPD.set_xlabel(r'$\Delta z$ ($\mathrm{\AA}$)')
    ax_VCPD.set_ylabel('$V_{CPD}$ (V)')
    ax_VCPD.grid(True)

    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    img_path = os.path.join(labbook_folder, f"KPFM_z_set_{date_str}.png")
    plt.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close()

    return img_path


# -----------------------------------------------------------------------------
# Compare spectra — multiple DAT files on the same axes
# -----------------------------------------------------------------------------

def save_dat_compare_spectra(file_paths_dat, labbook_folder, spec_type):
    """Plot multiple DAT spectra of the same type on a single axes in viridis colours.

    Parameters
    ----------
    file_paths_dat : list of str
        Paths to the .dat files to compare.
    labbook_folder : str
        Destination folder for the output PNG.
    spec_type : str
        One of 'didv_spectrum', 'z_spectrum', 'kpfm'.
    """
    from .config import (
        SPEC_BIAS_CHANNEL, SPEC_DIDV_CHANNEL,
        SPEC_Z_CHANNEL, SPEC_FREQ_SHIFT,
    )

    # Colour scale
    no_of_files = len(file_paths_dat)
    color_array = np.arange(0, no_of_files, 1)
    coloring_array = np.ndarray.flatten(color_array)
    colors = plt.cm.viridis(
        [(xx - np.min(coloring_array)) / (np.max(coloring_array) - np.min(coloring_array))
         for xx in coloring_array]
    )

    # Axis labels and signal keys per type
    type_config = {
        "didv_spectrum": dict(
            x_key=SPEC_BIAS_CHANNEL, x_scale=1e3,
            y_key=SPEC_DIDV_CHANNEL, y_scale=1,
            xlabel="Bias (mV)", ylabel="dI/dV (arb. units)",
            title_prefix="dIdV COMPARE",
        ),
        "z_spectrum": dict(
            x_key=SPEC_Z_CHANNEL, x_scale=1e10,
            y_key=SPEC_FREQ_SHIFT, y_scale=1,
            xlabel=r"$Z (\mathrm{\AA})$", ylabel=r"$\Delta f$ (Hz)",
            title_prefix="Z COMPARE",
        ),
        "kpfm": dict(
            x_key=SPEC_BIAS_CHANNEL, x_scale=1,
            y_key=SPEC_FREQ_SHIFT, y_scale=1,
            xlabel="Bias (V)", ylabel=r"$\Delta f$ (Hz)",
            title_prefix="KPFM COMPARE",
        ),
    }
    cfg = type_config[spec_type]

    fig, ax = plt.subplots(figsize=(8, 5))

    basenames = []
    for i, file_path in enumerate(file_paths_dat):
        dat_data = nanonispy.read.Spec(file_path)
        sweep_signal = dat_data.signals[cfg["x_key"]] * cfg["x_scale"]
        y_signal     = dat_data.signals[cfg["y_key"]] * cfg["y_scale"]
        label = os.path.basename(file_path)
        basenames.append(label)
        ax.plot(sweep_signal, y_signal, color=colors[i], label=label)

    header_line = f"{cfg['title_prefix']}: {', '.join(basenames)}"
    ax.set_title(header_line, fontsize=7)
    ax.set_xlabel(cfg["xlabel"])
    ax.set_ylabel(cfg["ylabel"])
    ax.grid(True)

    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    img_path = os.path.join(
        labbook_folder,
        f"compare_{spec_type}_{date_str}.png"
    )
    plt.savefig(img_path, dpi=200, bbox_inches="tight")
    plt.close()

    return img_path
