# nanonis-labbook

A GUI tool for transferring data collected with a Nanonis STM controller into a logbook for day-to-day experiment tracking.

Supported measurement types:
- Topography (constant-current STM)
- Drift-corrected topography
- nc-AFM (frequency shift)
- Constant-height current image
- dI/dV map
- dI/dV spectrum (with context SXM image)
- Z-spectroscopy
- KPFM
- Nc combined measurement (Z-spec + Z-dependent d²I/dV² stack)
- KPFM(z) set

---

## Installation

Clone the repository and install with pip:
Note: run the pip command from the top level "nanonis-labook" folder not the lower level folder.
```bash
git clone https://github.com/benlowe12/nanonis-labbook.git
cd nanonis-labbook
pip install .
```

---

## Configuration

Before running for the first time, open `nanonis_labbook/config.py` and set the channel names to match your Nanonis configuration:

```python
# Channel names — must match your Nanonis channel names exactly
TOPO_CHANNEL     = "Z"
CURRENT_CHANNEL  = "Current"
AFM_CHANNEL      = "OC_M1_Freq._Shift"
DIDV_MAP_CHANNEL = "LI_Demod_1_Y"
SPEC_DIDV_CHANNEL = "LI Demod 1 Y (A)"
# ... etc.

# Application to paste images into
LABBOOK_APP_TITLE = "Firefox"   # change to e.g. "Chrome", "Notion", "OneNote"
```

All channel names and the target application are defined in one place — you should not need to edit any other file.

---

## Usage

After installation you can launch the GUI in two ways:

**Option 1 — command line (recommended):**
```bash
nanonis-labbook
```

**Option 2 — as a Python module:**
```bash
python -m nanonis_labbook
```

### Workflow

1. Launch the tool.
2. Click **Choose Folder** and select the folder containing your Nanonis data files.
3. Click the button for the measurement type you want to log.  
   - For spectroscopy types a dialog will ask which SXM channel to use as the context image.  
   - For Nc and KPFM(z) measurements a file picker will open for you to select multiple files.
4. The image is generated, pasted automatically into the logbook application, and the temporary PNG is deleted.

---

## Project structure

```
nanonis_labbook/
├── config.py                 ← user configuration (channel names, app title)
├── file_utils.py             ← file discovery helpers
├── image_utils.py            ← image processing and curve fitting
├── sxm_measurements.py       ← SXM image functions
├── dat_measurements.py       ← DAT spectroscopy functions
├── combined_measurements.py  ← Nc and KPFM(z) multi-file functions
├── clipboard.py              ← clipboard and app-paste utilities
├── gui.py                    ← tkinter GUI
├── main.py                   ← entry point (run())
└── __main__.py               ← enables python -m nanonis_labbook
pyproject.toml
requirements.txt
README.md
```

---

## Requirements

- Windows (required for clipboard paste via `pywin32`)
- Python 3.8+
- See `requirements.txt` for Python dependencies
