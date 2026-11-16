# Seo

Strumenti SEO di Magic / Clickstore. Oggi c'è `gsc.py`, client di sola lettura
per l'API di Search Console: come si usa è nel docstring in testa al file.

## Prima di iniziare
- Dipendenze: `pip install -r requirements.txt`.
- Credenziali: `GSC_KEY_B64` o `GSC_KEY_FILE` (formati spiegati in `gsc.py`).
  Nelle sessioni cloud non sono impostate: se mancano fermati e chiedi a Elly
  come vuole fornirle. Non cercarle in altre cartelle.
- Mai committare `.json`, `.csv` o `.env`: sono chiavi ed export. Sono già in
  `.gitignore`; non forzarli con `git add -f`.

## Quale skill usare
- Export Search Console di uno store (zip o righe del foglio): `analisi-search-console-store`
- "Come va il sito X", per una proprietà di cui abbiamo gli accessi: `andamento-sito`
- Una pagina di magicnet.it da posizionare su una query: `posizionamento-magicnet`
- Prospect o sito di cui non abbiamo gli accessi: `checkup-digitale`
- Qualunque report con cifre, prima di consegnarlo: `controllore-numeri`

## Come si verifica il risultato
- Ogni cifra di un report viene da un comando `gsc.py` eseguito nella sessione
  o da un CSV salvato: accanto al dato scrivi proprietà, periodo e dimensioni.
- Confronta solo periodi chiusi e di pari lunghezza: gli ultimi 2-3 giorni di
  Search Console sono incompleti.
- Il nome della proprietà si prende da `python3 gsc.py sites` (`sc-domain:` o
  URL), non si indovina.

## Limiti
- Sola lettura. Nessuna modifica ai siti WordPress, anche se l'ambiente cloud
  ha le credenziali di qualche sito: proponi le modifiche e aspetta l'OK di Elly.

## Correzioni ricorrenti
Una riga per ogni correzione che Elly si trova a ripetere.
