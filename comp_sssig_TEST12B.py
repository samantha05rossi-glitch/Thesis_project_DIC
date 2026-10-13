"""
Confronto sssig threshold (50 / 100 / 400) su TEST12B, filtro gauss=13
=========================================================================
Stessa logica gia' validata per il confronto tra finestre di filtro
gaussiano, applicata qui a sssig invece che al filtro. Legge DIRETTAMENTE
i file txt di output DICe (pandas, no ParaView).

A differenza del filtro gaussiano, sssig NON modifica i pixel
dell'immagine: decide solo se un subset viene TENTATO o scartato a priori
per scarso gradiente di intensita'. Sui subset tentati in tutte le
configurazioni, il risultato e' percio' necessariamente identico (stessi
pixel, stesso algoritmo) - il confronto punto-per-punto serve qui solo
come controllo di coerenza, non e' il cuore della domanda.

IL CONTROLLO CHE CONTA DAVVERO: il GAMMA medio dei subset che una soglia
piu' bassa (es. 50) RECUPERA rispetto a una piu' alta (es. 100) - se
quei punti hanno GAMMA vicino a 0 (match solido) la soglia alta stava
scartando dati buoni; se hanno GAMMA vicino alla soglia di plausibilita'
(match marginale), la soglia piu' alta stava facendo il suo lavoro
correttamente.
"""

import os
import pandas as pd
import numpy as np

# --- CONFIGURAZIONI DA CONFRONTARE ------------------------------------------
CONFIGURAZIONI = [
    ("sssig 0",  r"C:\Users\saman\Documents\DIC_tesi\DICe_results\result_DATASET_1\TEST12B3\results\DICe_solution_0.txt"),
    ("sssig 50",  r"C:\Users\saman\Documents\DIC_tesi\DICe_results\result_DATASET_1\TEST12B1\results\DICe_solution_0.txt"),
    ("sssig 100", r"C:\Users\saman\Documents\DIC_tesi\DICe_results\result_DATASET_1\TEST12B\results\DICe_solution_0.txt"),
    ("sssig 400", r"C:\Users\saman\Documents\DIC_tesi\DICe_results\result_DATASET_1\TEST12B2\results\DICe_solution_0.txt"),
]

SEPARATORE = None

COLONNA_ID = "SUBSET_ID"
COLONNA_X = "COORDINATE_X"
COLONNA_Y = "COORDINATE_Y"
COLONNA_DISP_X = "DISPLACEMENT_X"
COLONNA_DISP_Y = "DISPLACEMENT_Y"
COLONNA_GAMMA = "GAMMA"

GAMMA_SOGLIA_SENTINELLA = 0.0
GAMMA_SOGLIA_PLAUSIBILE = 0.5   # ZNCC >= 0.75, vedi Pan, Wang & Lu 2010
RUMORE_FONDO_PX = 0.9           # calibrato su TEST2B

SAVE_CSV_PATH = r"C:\Users\saman\Documents\DIC_tesi\DICe_results\result_DATASET_1\ANALISI_12\confronto_sssig_TEST12B.csv"

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
    """A = soglia PIU' ALTA (piu' restrittiva), B = soglia PIU' BASSA
    (piu' permissiva). Il controllo chiave e' sui punti che B recupera
    rispetto ad A: sono match solidi o marginali?"""
    plaus_a = dati_a[(dati_a["gamma"] >= GAMMA_SOGLIA_SENTINELLA) &
                      (dati_a["gamma"] <= GAMMA_SOGLIA_PLAUSIBILE)]
    plaus_b = dati_b[(dati_b["gamma"] >= GAMMA_SOGLIA_SENTINELLA) &
                      (dati_b["gamma"] <= GAMMA_SOGLIA_PLAUSIBILE)]

    id_comuni = plaus_a.index.intersection(plaus_b.index)
    id_solo_b = plaus_b.index.difference(plaus_a.index)

    print(f"\n--- {etichetta_a} vs {etichetta_b} ---")
    print(f"  Plausibili in '{etichetta_a}':  {len(plaus_a)}")
    print(f"  Plausibili in '{etichetta_b}':  {len(plaus_b)}")
    print(f"  Plausibili in ENTRAMBE:         {len(id_comuni)}")
    print(f"  Plausibili SOLO in '{etichetta_b}' (recuperati in piu'): {len(id_solo_b)}")

    risultato = {
        "Confronto": f"{etichetta_a} vs {etichetta_b}",
        "Punti comuni plausibili": len(id_comuni),
        "Punti recuperati in piu' da B": len(id_solo_b),
    }

    if len(id_comuni) > 0:
        diff_dx = plaus_a.loc[id_comuni, "dx"].to_numpy() - plaus_b.loc[id_comuni, "dx"].to_numpy()
        diff_dy = plaus_a.loc[id_comuni, "dy"].to_numpy() - plaus_b.loc[id_comuni, "dy"].to_numpy()
        print(f"  [controllo di coerenza] Diff dx sui punti comuni: "
              f"media={np.mean(diff_dx):.4f} std={np.std(diff_dx):.4f} "
              f"({'OK, sotto rumore di fondo' if abs(np.mean(diff_dx)) < RUMORE_FONDO_PX else 'ATTENZIONE'})")
        print(f"  [controllo di coerenza] Diff dy sui punti comuni: "
              f"media={np.mean(diff_dy):.4f} std={np.std(diff_dy):.4f} "
              f"({'OK, sotto rumore di fondo' if abs(np.mean(diff_dy)) < RUMORE_FONDO_PX else 'ATTENZIONE'})")
        risultato.update({
            "Diff dx media": round(float(np.mean(diff_dx)), 4),
            "Diff dy media": round(float(np.mean(diff_dy)), 4),
        })

    if len(id_solo_b) > 0:
        gamma_nuovi = plaus_b.loc[id_solo_b, "gamma"].to_numpy()
        gamma_comuni = plaus_b.loc[id_comuni, "gamma"].to_numpy() if len(id_comuni) else np.array([])
        print(f"  *** IL CONTROLLO CHE CONTA ***")
        print(f"  GAMMA medio punti RECUPERATI (soglia piu' bassa, soli nuovi): "
              f"{np.mean(gamma_nuovi):.4f} (mediana {np.median(gamma_nuovi):.4f})")
        if len(gamma_comuni):
            print(f"  GAMMA medio punti COMUNI (gia' validi con soglia alta): "
                  f"{np.mean(gamma_comuni):.4f}")
            if np.mean(gamma_nuovi) <= GAMMA_SOGLIA_PLAUSIBILE * 0.6:
                print(f"  -> I punti recuperati hanno GAMMA solido (ben sotto la "
                      f"soglia {GAMMA_SOGLIA_PLAUSIBILE}): la soglia piu' alta "
                      f"stava scartando dati BUONI.")
            elif np.mean(gamma_nuovi) > GAMMA_SOGLIA_PLAUSIBILE * 0.8:
                print(f"  -> I punti recuperati hanno GAMMA vicino al limite "
                      f"(soglia {GAMMA_SOGLIA_PLAUSIBILE}): sono match MARGINALI, "
                      f"la soglia piu' alta stava facendo il suo lavoro.")
            else:
                print(f"  -> Zona intermedia: ne' chiaramente solidi ne' chiaramente "
                      f"marginali, valuta caso per caso.")
        risultato["GAMMA medio punti recuperati"] = round(float(np.mean(gamma_nuovi)), 4)

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

    # Confronti in ordine dal piu' RESTRITTIVO al piu' PERMISSIVO
    # (400 -> 100 -> 50), cosi' "B" e' sempre quello che recupera punti in piu'
    print("\n\n=== CONFRONTI (dal piu' restrittivo al piu' permissivo) ===")
    ordine = ["sssig 400", "sssig 100", "sssig 50"]
    ordine = [e for e in ordine if e in dati]  # solo quelli presenti
    righe_confronto = []
    for i in range(len(ordine)):
        for j in range(i + 1, len(ordine)):
            a, b = ordine[i], ordine[j]
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


try:
    main()
except Exception:
    import traceback
    print("=== ERRORE ===")
    traceback.print_exc()
