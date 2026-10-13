import numpy as np
import matplotlib.pyplot as plt
import os
from astropy.convolution import Gaussian2DKernel, convolve
from scipy.ndimage import gaussian_filter
from scipy import signal as sg


def gaussian_smooting_with_Nan(img, sigma=7, k_size=15):
    # copia identica della funzione in Main.py, per evitare di importare
    # tutto Main.py (che richiede cv2, non necessario per questo script)
    kernel = Gaussian2DKernel(sigma)
    img_smoothed = gaussian_filter(img, sigma=sigma, mode='nearest')
    img_smoothed_2 = convolve(sg.medfilt2d(img, k_size), kernel)

    idx_NaN = np.isnan(img)
    indx_NaN_filtered = np.isnan(img_smoothed)
    mask = idx_NaN != indx_NaN_filtered

    img_smoothed[mask] = img_smoothed_2[mask]
    img_smoothed[idx_NaN] = np.nan
    img_smoothed = sg.medfilt2d(img_smoothed, 5)

    return img_smoothed


test_name = "TSEQ2"
n_steps = 10   # 10 coppie consecutive per 10 immagini

# ---- Parametri usati nel Run (stessi per tutti gli step, dalla GUI) ----
temp_dim = 21     # Template width
b = 5            # Edge y
d = 25            # Edge x
rectx1 = None     # None se non hai usato un'AOI rettangolare custom
recty1 = None

os.makedirs(f"OutputPlots/step_plots_{test_name}", exist_ok=True)

for step in range(1, n_steps + 1):
    dx = np.genfromtxt(f"OutputPlots/{test_name}_results_mm_dx_0_{step}.txt")
    dy = np.genfromtxt(f"OutputPlots/{test_name}_results_mm_dy_0_{step}.txt")

    # stesso smoothing usato dalla GUI prima di calcolare le sezioni centrali
    dispx_smoothed = gaussian_smooting_with_Nan(dx, 9, 21)
    dispy_smoothed = gaussian_smooting_with_Nan(dy, 9, 21)

    # ---- stesse formule di offset usate in GUI.py ----
    mask_x0 = rectx1 if rectx1 is not None else 0
    mask_y0 = recty1 if recty1 is not None else 0
    offset_col = mask_x0 + int((temp_dim - 1) / 2 + d)
    offset_row = mask_y0 + int((temp_dim - 1) / 2 + b)

    center_row = dispx_smoothed.shape[0] // 2
    center_col = dispy_smoothed.shape[1] // 2

    x_positions = offset_col + np.arange(dispx_smoothed.shape[1])
    section_x = dispx_smoothed[center_row, :]

    y_positions = offset_row + np.arange(dispy_smoothed.shape[0])
    section_y = dispy_smoothed[:, center_col]

    # ---- figura con 4 pannelli, come nella GUI ----
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

    im0 = axs[0, 0].imshow(dx, cmap="jet", aspect="auto")
    axs[0, 0].set_title(f"Horizontal displacement (dx) - step {step}")
    plt.colorbar(im0, ax=axs[0, 0], label="dx")

    im1 = axs[0, 1].imshow(dy, cmap="jet", aspect="auto")
    axs[0, 1].set_title(f"Vertical displacement (dy) - step {step}")
    plt.colorbar(im1, ax=axs[0, 1], label="dy")

    axs[1, 0].plot(x_positions, section_x, color="darkorange", linewidth=2)
    axs[1, 0].set_title("Horizontal central section")
    axs[1, 0].set_xlabel("X position [px]")
    axs[1, 0].set_ylabel("X displacement")
    axs[1, 0].grid(True)

    axs[1, 1].plot(y_positions, section_y, color="blue", linewidth=2)
    axs[1, 1].set_title("Vertical central section")
    axs[1, 1].set_xlabel("Y position [px]")
    axs[1, 1].set_ylabel("Y displacement")
    axs[1, 1].grid(True)

    plt.suptitle(f"{test_name} — step {step} (coppia immagini {step-1}-{step})")
    plt.tight_layout()
    plt.savefig(f"OutputPlots/step_plots_{test_name}/{test_name}_step{step:02d}.png", dpi=150)
    plt.close(fig)

    print(f"Step {step}: salvato plot -> OutputPlots/step_plots/{test_name}_step{step:02d}.png")
