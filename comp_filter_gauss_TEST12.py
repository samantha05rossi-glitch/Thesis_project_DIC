"""
Confronto filtro gaussiano (no filtro / window 7 / window 13) su TEST12
=========================================================================
Legge DIRETTAMENTE i file txt di output DICe (pandas, nessuna dipendenza
da ParaView) per le 3 configurazioni, e per ciascuna calcola:

  1. Quanti centri subset in totale, quanti "processati" (GAMMA valido,
     non sentinella) e quanti con match PLAUSIBILE (GAMMA sotto una
     soglia di qualita').
  2. Per ogni COPPIA di configurazioni, la differenza punto-per-punto di
     DISPLACEMENT_X/Y sui soli centri subset plausibili in ENTRAMBE
     (stesso SUBSET_ID) - dice se il filtro cambia la risposta fisica
     sui punti in comune, non solo quanti punti in piu' recupera.
  3. Per ogni coppia, il GAMMA medio dei punti "nuovi" che la seconda
     configurazione recupera rispetto alla prima (plausibili solo li') -
     se sistematicamente vicino alla soglia (match marginale) invece che
     vicino a 0 (match solido), e' un indizio che quella copertura in piu'
     e' "comprata" con affidabilita' bassa, non segnale genuino.

SOGLIA GAMMA "PLAUSIBILE"
---------------------------
GAMMA e' legato allo ZNCC di py2DIC dalla relazione (Pan, Wang & Lu, 2010,
Optics Express 18(2), 1011-1023, DOI: 10.1364/AO.49.005501):
    ZNCC = 1 - GAMMA/2
GAMMA <= 0.5 corrisponde a ZNCC >= 0.75. E' un valore di lavoro scelto da
te, non uno standard universale: calibralo se necessario sul tuo TEST1
(self-correlation, dove GAMMA dovrebbe essere quasi ovunque vicino a 0).
"""

import os
import pandas as pd
import numpy as np

# --- CONFIGURAZIONI DA CONFRONTARE ------------------------------------------
CONFIGURAZIONI = [
    ("No filtro",       r"C:\Users\saman\Documents\DIC_tesi\DICe_results\result_DATASET_1\TEST12\results\DICe_solution_0.txt"),
    ("Gauss window 7",  r"C:\Users\saman\Documents\DIC_tesi\DICe_results\result_DATASET_1\TEST12C\results\DICe_solution_0.txt"),
    ("Gauss window 13", r"C:\Users\saman\Documents\DIC_tesi\DICe_results\result_DATASET_1\TEST12B\results\DICe_solution_0.txt"),
]

SEPARATORE = None  # None = pandas prova a indovinarlo da solo

COLONNA_ID = "SUBSET_ID"
COLONNA_X = "COORDINATE_X"
COLONNA_Y = "COORDINATE_Y"
COLONNA_DISP_X = "DISPLACEMENT_X"
COLONNA_DISP_Y = "DISPLACEMENT_Y"
COLONNA_GAMMA = "GAMMA"

GAMMA_SOGLIA_SENTINELLA = 0.0   # GAMMA < 0 = subset non processato
GAMMA_SOGLIA_PLAUSIBILE = 0.5   # soglia di qualita' del match (vedi sopra)

# Rumore di fondo noto della tecnica, in pixel - calibrato empiricamente dal
# tuo TEST2B (immagini consecutive, spostamento vero nullo, stessa maschera):
# li' i risultati cadono tra circa -1 e +1 px, quindi sotto questo valore
# qualunque differenza tra configurazioni non e' distinguibile dal rumore
# intrinseco della tecnica, indipendentemente da quanto "sistematica" possa
# sembrare statisticamente.
RUMORE_FONDO_PX = 1.2

SAVE_CSV_PATH = r"C:\Users\saman\Documents\DIC_tesi\DICe_results\result_DATASET_1\ANALISI_12\confronto_filtro_gauss_TEST12.csv"

# -----------------------------------------------------------------------------


def trova_colonna(df, nome_richiesto):
    if nome_richiesto in df.columns:
        return nome_richiesto
    for col in df.columns:
        if col.strip().lower() == nome_richiesto.strip().lower():
            return col
    for col in df.columns:
        if nome_richiesto.lower() in col.lower():
            return col
    return None


def leggi_file_dice(path):
    with open(path, "r", errors="ignore") as f:
        righe = f.readlines()
    idx = None
    for i, r in enumerate(righe):
        u = r.upper()
        if "DISPLACEMENT_X" in u and "DISPLACEMENT_Y" in u:
            idx = i
            break
    if idx is None:
        raise RuntimeError(f"Non trovo l'intestazione in {path}")
    df = pd.read_csv(path, skiprows=idx, sep=SEPARATORE, engine="python",
                      skipinitialspace=True)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def carica_configurazione(etichetta, file_path):
    if not os.path.isfile(file_path):
        raise RuntimeError(f"File non trovato per '{etichetta}': {file_path}")
    df = leggi_file_dice(file_path)

    col_id = trova_colonna(df, COLONNA_ID)
    col_x = trova_colonna(df, COLONNA_X)
    col_y = trova_colonna(df, COLONNA_Y)
    col_dx = trova_colonna(df, COLONNA_DISP_X)
    col_dy = trova_colonna(df, COLONNA_DISP_Y)
    col_gamma = trova_colonna(df, COLONNA_GAMMA)

    richieste = {COLONNA_ID: col_id, COLONNA_X: col_x, COLONNA_Y: col_y,
                 COLONNA_DISP_X: col_dx, COLONNA_DISP_Y: col_dy,
                 COLONNA_GAMMA: col_gamma}
    mancanti = [n for n, c in richieste.items() if c is None]
    if mancanti:
        raise RuntimeError(
            f"Colonne non trovate in '{etichetta}': {mancanti}. "
            f"Colonne disponibili: {list(df.columns)}"
        )

    out = pd.DataFrame({
        "id": df[col_id].astype(int).to_numpy() if col_id in df else np.arange(len(df)),
        "x": df[col_x].to_numpy(dtype=float),
        "y": df[col_y].to_numpy(dtype=float),
        "dx": df[col_dx].to_numpy(dtype=float),
        "dy": df[col_dy].to_numpy(dtype=float),
        "gamma": df[col_gamma].to_numpy(dtype=float),
    }).set_index("id")
    return out


def statistiche_copertura(etichetta, dati):
    n_totale = len(dati)
    processato = dati["gamma"] >= GAMMA_SOGLIA_SENTINELLA
    n_processato = int(processato.sum())
    plausibile = processato & (dati["gamma"] <= GAMMA_SOGLIA_PLAUSIBILE)
    n_plausibile = int(plausibile.sum())

    print(f"\n--- {etichetta} ---")
    print(f"  Centri subset totali:                 {n_totale}")
    print(f"  Processati (GAMMA non sentinella):     {n_processato} "
          f"({100*n_processato/n_totale:.1f}% del totale)")
    if n_processato:
        print(f"  Con match plausibile (GAMMA <= {GAMMA_SOGLIA_PLAUSIBILE}):    "
              f"{n_plausibile} ({100*n_plausibile/n_totale:.1f}% del totale, "
              f"{100*n_plausibile/n_processato:.1f}% dei processati)")

    return {
        "Configurazione": etichetta,
        "Centri subset totali": n_totale,
        "Processati": n_processato,
        "% processati": round(100 * n_processato / n_totale, 1),
        "Plausibili (GAMMA<=soglia)": n_plausibile,
        "% plausibili sul totale": round(100 * n_plausibile / n_totale, 1),
        "% plausibili sui processati": round(100 * n_plausibile / n_processato, 1) if n_processato else None,
    }


def confronta_coppia(etichetta_a, dati_a, etichetta_b, dati_b):
    """Differenza sui punti plausibili in ENTRAMBE, + GAMMA medio dei punti
    "nuovi" recuperati solo da B rispetto ad A (copertura aggiuntiva)."""
    plaus_a = dati_a[(dati_a["gamma"] >= GAMMA_SOGLIA_SENTINELLA) &
                      (dati_a["gamma"] <= GAMMA_SOGLIA_PLAUSIBILE)]
    plaus_b = dati_b[(dati_b["gamma"] >= GAMMA_SOGLIA_SENTINELLA) &
                      (dati_b["gamma"] <= GAMMA_SOGLIA_PLAUSIBILE)]

    id_comuni = plaus_a.index.intersection(plaus_b.index)
    id_solo_b = plaus_b.index.difference(plaus_a.index)  # copertura in piu' di B

    print(f"\n--- {etichetta_a} vs {etichetta_b} ---")
    print(f"  Plausibili in '{etichetta_a}':  {len(plaus_a)}")
    print(f"  Plausibili in '{etichetta_b}':  {len(plaus_b)}")
    print(f"  Plausibili in ENTRAMBE:         {len(id_comuni)}")
    print(f"  Plausibili SOLO in '{etichetta_b}' (copertura aggiuntiva): {len(id_solo_b)}")

    risultato = {
        "Confronto": f"{etichetta_a} vs {etichetta_b}",
        "Punti comuni plausibili": len(id_comuni),
        "Punti aggiuntivi solo in B": len(id_solo_b),
    }

    if len(id_comuni) > 0:
        diff_dx = plaus_a.loc[id_comuni, "dx"].to_numpy() - plaus_b.loc[id_comuni, "dx"].to_numpy()
        diff_dy = plaus_a.loc[id_comuni, "dy"].to_numpy() - plaus_b.loc[id_comuni, "dy"].to_numpy()
        print(f"  Diff dx sui punti comuni: media={np.mean(diff_dx):.4f}  "
              f"std={np.std(diff_dx):.4f}")
        print(f"  Diff dy sui punti comuni: media={np.mean(diff_dy):.4f}  "
              f"std={np.std(diff_dy):.4f}")
        for comp, media, std in [("dx", np.mean(diff_dx), np.std(diff_dx)),
                                  ("dy", np.mean(diff_dy), np.std(diff_dy))]:
            if std > 1e-9 and abs(media) > 0.3 * std:
                print(f"  ATTENZIONE ({comp}): scostamento sistematico "
                      f"(|media|/std = {abs(media)/std:.2f}) tra le due "
                      f"configurazioni sui punti comuni.")
            if abs(media) > RUMORE_FONDO_PX:
                print(f"  ATTENZIONE ({comp}): |media| = {abs(media):.3f} px "
                      f"SUPERA il rumore di fondo noto ({RUMORE_FONDO_PX} px, "
                      f"da TEST2B) - differenza fisicamente rilevante, non "
                      f"spiegabile col solo rumore intrinseco della tecnica.")
            else:
                print(f"  ({comp}: |media| = {abs(media):.3f} px, sotto il "
                      f"rumore di fondo noto di {RUMORE_FONDO_PX} px - "
                      f"differenza non distinguibile dal rumore della tecnica)")
        risultato.update({
            "Diff dx media": round(float(np.mean(diff_dx)), 4),
            "Diff dx std": round(float(np.std(diff_dx)), 4),
            "Diff dy media": round(float(np.mean(diff_dy)), 4),
            "Diff dy std": round(float(np.std(diff_dy)), 4),
        })

    if len(id_solo_b) > 0:
        gamma_nuovi = plaus_b.loc[id_solo_b, "gamma"].to_numpy()
        gamma_comuni_b = plaus_b.loc[id_comuni, "gamma"].to_numpy() if len(id_comuni) else np.array([])
        print(f"  GAMMA medio punti NUOVI (solo {etichetta_b}): "
              f"{np.mean(gamma_nuovi):.4f} (mediana {np.median(gamma_nuovi):.4f})")
        if len(gamma_comuni_b):
            print(f"  GAMMA medio punti COMUNI (per confronto): "
                  f"{np.mean(gamma_comuni_b):.4f}")
            if np.mean(gamma_nuovi) > np.mean(gamma_comuni_b) * 1.3:
                print(f"  ATTENZIONE: i punti nuovi hanno GAMMA sistematicamente "
                      f"peggiore (piu' vicino alla soglia) dei punti comuni - "
                      f"possibile copertura 'comprata' con match marginali.")
        risultato["GAMMA medio punti nuovi"] = round(float(np.mean(gamma_nuovi)), 4)

    return risultato


def main():
    dati = {}
    righe_copertura = []
    for etichetta, path in CONFIGURAZIONI:
        d = carica_configurazione(etichetta, path)
        dati[etichetta] = d
        righe_copertura.append(statistiche_copertura(etichetta, d))

    print("\n\n=== TABELLA COPERTURA/PLAUSIBILITA' ===")
    df_copertura = pd.DataFrame(righe_copertura)
    print(df_copertura.to_string(index=False))

    print("\n\n=== CONFRONTO A COPPIE (ordine crescente: no filtro -> 7 -> 13) ===")
    righe_confronto = []
    etichette = [e for e, _ in CONFIGURAZIONI]
    for i in range(len(etichette)):
        for j in range(i + 1, len(etichette)):
            a, b = etichette[i], etichette[j]
            righe_confronto.append(confronta_coppia(a, dati[a], b, dati[b]))

    df_confronto = pd.DataFrame(righe_confronto)
    print("\n" + df_confronto.to_string(index=False))

    if SAVE_CSV_PATH:
        cartella = os.path.dirname(SAVE_CSV_PATH)
        if cartella and not os.path.isdir(cartella):
            os.makedirs(cartella)
        base, _ = os.path.splitext(SAVE_CSV_PATH)
        df_copertura.to_csv(base + "_copertura.csv", index=False, sep=";", decimal=",")
        df_confronto.to_csv(base + "_confronto_coppie.csv", index=False, sep=";", decimal=",")
        print(f"\nOK - Salvati: {base}_copertura.csv e {base}_confronto_coppie.csv")
        print("(formato italiano: separatore ';' e decimale ',')")


try:
    main()
except Exception:
    import traceback
    print("=== ERRORE ===")
    traceback.print_exc()

