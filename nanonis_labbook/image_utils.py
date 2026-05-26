# =============================================================================
# nanonis_labbook/image_utils.py
#
# Image processing utilities and curve-fitting helpers.
# =============================================================================

import numpy as np
from lmfit import Model, Parameters


def line_poly_detrend(image, order=1):
    """Remove a polynomial trend line-by-line from a 2D image array.

    Parameters
    ----------
    image : np.ndarray
        2D array of scan data.
    order : int
        Polynomial order for the trend fit (default 1 = linear).

    Returns
    -------
    np.ndarray
        Corrected image with the per-line trend subtracted.
    """
    ny, nx = image.shape
    x = np.arange(nx)
    corrected = image.copy()
    for i in range(ny):
        coeffs = np.polyfit(x, image[i, :], order)
        trend = np.polyval(coeffs, x)
        corrected[i, :] -= trend
    return corrected


def overlay_text(ax, text):
    """Add a semi-transparent text box to the top-left corner of an axes."""
    ax.text(
        0.02, 0.98, text,
        transform=ax.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.7)
    )


# --- KPFM fitting -----------------------------------------------------------

def parabola(x, a, b, c):
    """Parabola model: a*(x - b)**2 + c.  Used for KPFM V_CPD extraction."""
    return a * (x - b) ** 2 + c


def fit_function(xx, yy):
    """Fit a parabola to (xx, yy) using lmfit and return the result object."""
    pars = Parameters()
    quadratic_model = Model(parabola, prefix='quad_')
    pars.add('quad_a', value=-1)
    pars.add('quad_b', value=-0.4)
    pars.add('quad_c', value=1)

    model = quadratic_model
    model.eval(pars, x=xx)
    out = model.fit(yy, pars, x=xx)
    return out
