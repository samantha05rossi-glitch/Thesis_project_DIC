# import numpy as np

# u = np.loadtxt("umSPCS03.dat")  # nome file corretto nella cartella Output
# v = np.loadtxt("vmSPCS03.dat")
# w = np.loadtxt("wmSPCS03.dat")

# for nome, arr in [("u", u), ("v", v), ("w", w)]:
#     print(f"{nome}: media={np.nanmean(arr):.4f} mm, std={np.nanstd(arr):.4f} mm, "
#           f"min={np.nanmin(arr):.4f}, max={np.nanmax(arr):.4f}")

#     import numpy as np

# u = np.loadtxt("umSPCS03.dat")  # nome file corretto nella cartella Output
# v = np.loadtxt("vmSPCS03.dat")
# w = np.loadtxt("wmSPCS03.dat")

# for nome, arr in [("u", u), ("v", v), ("w", w)]:
#     media = np.nanmean(arr)
#     mediana = np.nanmedian(arr)
#     std = np.nanstd(arr)
#     rmse = np.sqrt(np.nanmean(arr**2))
#     nmad = 1.4826 * np.nanmedian(np.abs(arr - mediana))
#     print(f"{nome}: media={media:.4f} mm, mediana={mediana:.4f} mm, std={std:.4f} mm, "
#           f"rmse={rmse:.4f} mm, nmad={nmad:.4f} mm, "
#           f"min={np.nanmin(arr):.4f}, max={np.nanmax(arr):.4f}")

import numpy as np

u = np.loadtxt("umSPCS03.dat")  # nome file corretto nella cartella Output
v = np.loadtxt("vmSPCS03.dat")
w = np.loadtxt("wmSPCS03.dat")

for nome, arr in [("u", u), ("v", v), ("w", w)]:
    media = np.nanmean(arr)
    mediana = np.nanmedian(arr)
    std = np.nanstd(arr)
    rmse = np.sqrt(np.nanmean(arr**2))
    nmad = 1.4826 * np.nanmedian(np.abs(arr - mediana))
    le68 = np.nanpercentile(np.abs(arr), 68)
    le95 = np.nanpercentile(np.abs(arr), 95)
    print(f"{nome}: media={media:.4f} mm, mediana={mediana:.4f} mm, std={std:.4f} mm, "
          f"rmse={rmse:.4f} mm, nmad={nmad:.4f} mm, "
          f"LE68={le68:.4f} mm, LE95={le95:.4f} mm, "
          f"min={np.nanmin(arr):.4f}, max={np.nanmax(arr):.4f}")