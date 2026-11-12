#!/usr/bin/env python3
"""Client minimale per l'API di Google Search Console (sola lettura).

Credenziali: service account Google, letto dalla variabile d'ambiente
GSC_SA_KEY_B64 (il file JSON della chiave codificato in base64) oppure,
in alternativa, GSC_SA_KEY_FILE (percorso del file JSON).

Uso:
  python3 gsc.py sites
  python3 gsc.py query sc-domain:esempio.it --days 28 --dim query --limit 50
  python3 gsc.py query https://www.esempio.it/ --start 2026-08-01 --end 2026-10-31 \
      --dim date --csv out.csv
  python3 gsc.py inspect sc-domain:esempio.it https://www.esempio.it/pagina/
"""
import argparse
import base64
import csv
import datetime as dt
import json
import os
import sys
from urllib.parse import quote

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
API = "https://searchconsole.googleapis.com"
PAGE = 25000  # massimo di righe per chiamata


def session():
    b64 = os.environ.get("GSC_SA_KEY_B64")
    path = os.environ.get("GSC_SA_KEY_FILE")
    if b64:
        info = json.loads(base64.b64decode(b64))
    elif path:
        with open(path, encoding="utf-8") as f:
            info = json.load(f)
    else:
        sys.exit("Credenziali mancanti: imposta GSC_SA_KEY_B64 o GSC_SA_KEY_FILE.")
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return AuthorizedSession(creds)


def call(s, method, url, **kw):
    r = s.request(method, url, timeout=60, **kw)
    if r.status_code >= 400:
        sys.exit(f"Errore API {r.status_code}: {r.text[:500]}")
    return r.json()


def cmd_sites(s, a):
    for e in sorted(call(s, "GET", f"{API}/webmasters/v3/sites").get("siteEntry", []),
                    key=lambda e: e["siteUrl"]):
        print(f"{e['permissionLevel']:22} {e['siteUrl']}")


def cmd_query(s, a):
    if a.start and a.end:
        start, end = a.start, a.end
    else:
        # i dati GSC arrivano con circa 2-3 giorni di ritardo
        end_d = dt.date.today() - dt.timedelta(days=3)
        start, end = str(end_d - dt.timedelta(days=a.days - 1)), str(end_d)
    dims = [d for d in a.dim.split(",") if d]
    body = {"startDate": start, "endDate": end, "dimensions": dims,
            "type": a.type, "dataState": "final"}
    filters = []
    for name, val in (("page", a.page), ("query", a.query_contains)):
        if val:
            filters.append({"dimension": name, "operator": "contains", "expression": val})
    if filters:
        body["dimensionFilterGroups"] = [{"filters": filters}]

    url = f"{API}/webmasters/v3/sites/{quote(a.site, safe='')}/searchAnalytics/query"
    rows, offset = [], 0
    while len(rows) < a.limit:
        body.update(rowLimit=min(PAGE, a.limit - len(rows)), startRow=offset)
        chunk = call(s, "POST", url, json=body).get("rows", [])
        rows += chunk
        offset += len(chunk)
        if len(chunk) < body["rowLimit"]:
            break

    header = dims + ["clicks", "impressions", "ctr", "position"]
    table = [r.get("keys", []) + [r["clicks"], r["impressions"],
                                  round(r["ctr"] * 100, 2), round(r["position"], 1)]
             for r in rows]
    out = open(a.csv, "w", newline="", encoding="utf-8") if a.csv else sys.stdout
    w = csv.writer(out, delimiter="," if a.csv else "\t")
    w.writerow(header)
    w.writerows(table)
    if a.csv:
        out.close()
        print(f"{len(table)} righe ({start} → {end}) scritte in {a.csv}", file=sys.stderr)


def cmd_inspect(s, a):
    res = call(s, "POST", f"{API}/v1/urlInspection/index:inspect",
               json={"inspectionUrl": a.url, "siteUrl": a.site, "languageCode": "it-IT"})
    print(json.dumps(res.get("inspectionResult", res), indent=2, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("sites", help="elenca le proprietà visibili al service account")

    q = sub.add_parser("query", help="dati di rendimento (Search Analytics)")
    q.add_argument("site", help="es. sc-domain:esempio.it oppure https://www.esempio.it/")
    q.add_argument("--days", type=int, default=28)
    q.add_argument("--start")
    q.add_argument("--end")
    q.add_argument("--dim", default="query",
                   help="dimensioni separate da virgola: query,page,date,country,device")
    q.add_argument("--type", default="web",
                   choices=["web", "image", "video", "news", "discover", "googleNews"])
    q.add_argument("--page", help="filtra le pagine che contengono questa stringa")
    q.add_argument("--query-contains", help="filtra le query che contengono questa stringa")
    q.add_argument("--limit", type=int, default=1000)
    q.add_argument("--csv", help="scrive il risultato in questo file CSV")

    i = sub.add_parser("inspect", help="stato di indicizzazione di un URL")
    i.add_argument("site")
    i.add_argument("url")

    a = p.parse_args()
    s = session()
    {"sites": cmd_sites, "query": cmd_query, "inspect": cmd_inspect}[a.cmd](s, a)


if __name__ == "__main__":
    main()
