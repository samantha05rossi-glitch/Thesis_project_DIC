import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

files = {
    "TEST154-164": "TEST12_results_corrcoeff_0_1.txt",
    "TEST134-144": "TSEQ3_results_corrcoeff_0_1.txt",
}

# ============================================================
# Caricamento dati e maschera AOI
# ============================================================
data = {}
for label, fpath in files.items():
    corr = np.genfromtxt(fpath)

    dx_fpath = fpath.replace("results_corrcoeff", "results_mm_dx")
    dx_reference = np.genfromtxt(dx_fpath)

    aoi_mask = ~np.isnan(dx_reference)

    corr_aoi = corr.copy()
    corr_aoi[~aoi_mask] = np.nan

    data[label] = corr_aoi

# ============================================================
# Figure: una colonna per dataset, aspect reale rispettato
# ============================================================
n = len(data)
fig_height = 6
width_ratios = [arr.shape[1] / arr.shape[0] for arr in data.values()]
fig_width = fig_height * sum(width_ratios) * 1.15

fig, axs = plt.subplots(
    1, n,
    figsize=(fig_width, fig_height),
    gridspec_kw={"width_ratios": width_ratios, "wspace": 0.55}
)

if n == 1:
    axs = [axs]

for ax, (label, corr_aoi) in zip(axs, data.items()):

    im = ax.imshow(
        corr_aoi,
        cmap="viridis",
        vmin=0,
        vmax=1,
        aspect="equal"
    )

    ax.set_title(f"Correlation coefficient surface - {label}")
    ax.set_xlabel("X [px]")
    ax.set_ylabel("Y [px]")

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="4%", pad=0.15)
    fig.colorbar(im, cax=cax, label="ZNCC / TM_CCOEFF_NORMED")

    # ============================================================
    # Statistiche calcolate SOLO dentro l'AOI
    # ============================================================
    n_valid = np.sum(~np.isnan(corr_aoi))
    mean_corr = np.nanmean(corr_aoi)
    low_corr_pct = 100 * np.sum(corr_aoi < 0.5) / n_valid

    print(
        f"{label}: "
        f"mean corr (AOI) = {mean_corr:.3f}, "
        f"% punti con corr < 0.5 (AOI) = {low_corr_pct:.2f}%"
    )

# NIENTE plt.tight_layout(): è incompatibile con gli axes creati da
# make_axes_locatable e genera il warning. Lo spacing è già gestito
# esplicitamente da wspace + bbox_inches="tight" in savefig, quindi
# rimuoverlo non cambia il risultato ma elimina il warning.
plt.savefig(
    "correlation_coefficient_comparison154_134.png",
    dpi=150,
    bbox_inches="tight"
)
plt.show()
#--------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------

# import numpy as np
# import matplotlib.pyplot as plt

# files = {
#     "TEST154-164": "TEST12_results_corrcoeff_0_1.txt",   
#     "TEST134-144": "TSEQ3_results_corrcoeff_0_1.txt",
# }

# fig, axs = plt.subplots(1, len(files), figsize=(7*len(files), 6))
# if len(files) == 1:
#     axs = [axs]

# for ax, (label, fpath) in zip(axs, files.items()):
#     corr = np.genfromtxt(fpath)
#     im = ax.imshow(corr, cmap="viridis", vmin=0, vmax=1, aspect="auto")
#     ax.set_title(f"Correlation coefficient surface - {label}")
#     plt.colorbar(im, ax=ax, label="ZNCC / TM_CCOEFF_NORMED")

#     n_valid = np.sum(~np.isnan(corr))
#     mean_corr = np.nanmean(corr)
#     low_corr_pct = 100 * np.sum(corr < 0.5) / n_valid
#     print(f"{label}: mean corr = {mean_corr:.3f}, % punti con corr < 0.5 = {low_corr_pct:.2f}%")

# plt.tight_layout()
# plt.savefig("correlation_coefficient_comparison154_174.png", dpi=150)
# plt.show()
#-------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------
# import numpy as np
# import matplotlib.pyplot as plt

# files = {
#     "TEST154-164": "TEST12_results_corrcoeff_0_1.txt",
#     "TSE174-184": "TSEQ4_results_corrcoeff_0_1.txt",
# }

# fig, axs = plt.subplots(
#     1, len(files),
#     figsize=(7 * len(files), 6)
# )

# # Se c'è un solo file, axs non è un array
# if len(files) == 1:
#     axs = [axs]

# for ax, (label, fpath) in zip(axs, files.items()):

#     # ============================================================
#     # Caricamento correlation coefficient
#     # ============================================================
#     corr = np.genfromtxt(fpath)

#     # ============================================================
#     # Maschera AOI usando il corrispondente file dx
#     # ============================================================
#     dx_fpath = fpath.replace(
#         "results_corrcoeff",
#         "results_mm_dx"
#     )

#     dx_reference = np.genfromtxt(dx_fpath)

#     # True solo dentro l'AOI
#     aoi_mask = ~np.isnan(dx_reference)

#     # Manteniamo i valori di corr solo dentro l'AOI
#     corr_aoi = corr.copy()
#     corr_aoi[~aoi_mask] = np.nan

#     # ============================================================
#     # Plot
#     # ============================================================
#     im = ax.imshow(
#         corr_aoi,
#         cmap="viridis",
#         vmin=0,
#         vmax=1,
#         aspect="auto"
#     )

#     ax.set_title(f"Correlation coefficient surface - {label}")
#     ax.set_xlabel("X")
#     ax.set_ylabel("Y")

#     # Colorbar per ciascun subplot
#     plt.colorbar(
#         im,
#         ax=ax,
#         label="ZNCC / TM_CCOEFF_NORMED"
#     )

#     # ============================================================
#     # Statistiche calcolate SOLO dentro l'AOI
#     # ============================================================
#     n_valid = np.sum(~np.isnan(corr_aoi))

#     mean_corr = np.nanmean(corr_aoi)

#     low_corr_pct = (
#         100 * np.sum(corr_aoi < 0.5) / n_valid
#     )

#     print(
#         f"{label}: "
#         f"mean corr (AOI) = {mean_corr:.3f}, "
#         f"% punti con corr < 0.5 (AOI) = {low_corr_pct:.2f}%"
#     )

# plt.tight_layout()

# plt.savefig(
#     "correlation_coefficient_comparison154_174.png",
#     dpi=150,
#     bbox_inches="tight"
# )

# plt.show()