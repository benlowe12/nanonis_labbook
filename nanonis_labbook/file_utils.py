# =============================================================================
# nanonis_labbook/file_utils.py
#
# Helpers for locating the most recent Nanonis data files in a folder.
# =============================================================================

import os
import glob


def get_most_recent_file(folder, extension):
    """Return the most recently modified file with the given extension in folder,
    or None if no matching files exist."""
    files = glob.glob(os.path.join(folder, f"*{extension}"))
    return max(files, key=os.path.getmtime) if files else None


def get_file_path_sxm(folder):
    """Return the most recent .sxm file in folder."""
    return get_most_recent_file(folder, ".sxm")


def get_file_path_dat(folder):
    """Return the most recent .dat file in folder."""
    return get_most_recent_file(folder, ".dat")
