# =============================================================================
# nanonis_labbook/config.py
#
# USER CONFIGURATION — edit this file to match your Nanonis channel names
# and system setup before running the labbook tool.
# =============================================================================


# -----------------------------------------------------------------------------
# SXM image channel names
# These must match the channel names exactly as they appear in your .sxm files.
# -----------------------------------------------------------------------------

TOPO_CHANNEL      = "Z"               # Topography (constant-current STM)
CURRENT_CHANNEL   = "Current"         # Current (constant-height STM)
AFM_CHANNEL       = "Frequency_Shift" # Frequency shift (nc-AFM)
DIDV_MAP_CHANNEL  = "Input_3"         # Lock-in output channel for dI/dV maps

# Channel used for the reference SXM image shown alongside .dat spectra.
# This is also the fallback channel in image_type_to_channel_and_cmap().
DIDV_REF_CHANNEL  = "Input_3"

# Channel used for the SXM image displayed in the Nc measurement panel
NC_IMAGE_CHANNEL  = "Current"


# -----------------------------------------------------------------------------
# .dat spectroscopy channel names
# These must match the signal names exactly as they appear in your .dat files.
# -----------------------------------------------------------------------------

SPEC_BIAS_CHANNEL      = "Bias (V)"            # Bias sweep axis
SPEC_BIAS_CALC_CHANNEL = "Bias calc (V)"        # Calculated bias (used in Nc/KPFM(z))
SPEC_DIDV_CHANNEL      = "Input 3 (V)"          # Lock-in dI/dV signal
SPEC_Z_CHANNEL         = "Z (m)"                # Z sweep axis
SPEC_FREQ_SHIFT        = "Frequency Shift (Hz)" # Frequency shift signal

# Nc measurement: second-derivative / d2I/dV2 signal
NC_SPEC_CHANNEL        = "Input 3 (V)"

# KPFM: frequency shift signal names (the tool checks both and uses whichever
# is present in the file)
KPFM_FREQ_SHIFT_FWD    = "Frequency Shift (Hz)"
KPFM_FREQ_SHIFT_FWD_AVG= "Frequency Shift [AVG] (Hz)"
KPFM_FREQ_SHIFT_BWD    = "Frequency Shift [bwd] (Hz)"
KPFM_FREQ_SHIFT_BWD_AVG= "Frequency Shift [AVG] [bwd] (Hz)"


# -----------------------------------------------------------------------------
# Colourmaps
# Any valid matplotlib colormap name.
# -----------------------------------------------------------------------------

CMAP_TOPO    = "Blues_r"
CMAP_CURRENT = "Purples_r"
CMAP_AFM     = "gray"
CMAP_DIDV    = "magma"


# -----------------------------------------------------------------------------
# Target application for pasting images into the logbook
# Set this to the window title of the application you use as your logbook.
# The tool searches for a window whose title contains this string
# (case-insensitive match).
# Examples: "Firefox", "Chrome", "Notion", "OneNote"
# -----------------------------------------------------------------------------

LABBOOK_APP_TITLE = "Firefox"
