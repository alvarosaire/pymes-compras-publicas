"""Importacion atomica: conserva el padron anterior si el nuevo tiene errores."""
import argparse, io, json, os, re, sqlite3, zipfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

def build(archive, target, date):
    datetime.strptime(date, '%Y-%m-%d')
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix('.loading.sqlite')
    if temp.exists():
        temp.unlink()
    try:
        with zipfile.ZipFile(archive) as z, closing(sqlite3.connect(temp)) as con:
            names = [n for n in z.namelist() if n.lower().endswith('.txt')]
            if len(names) != 1:
                raise ValueError('Se esperaba un unico TXT')
            con.execute('PRAGMA journal_mode=OFF')
            con.execute('CREATE TABLE empresas (ruc TEXT PRIMARY KEY, razon_social TEXT, estado TEXT, condicion TEXT, ubigeo TEXT) WITHOUT ROWID')
            con.execute('CREATE TABLE metadata (clave TEXT PRIMARY KEY, valor TEXT)')
            count = 0
            excluded = 0
            with io.TextIOWrapper(z.open(names[0]), encoding='latin-1') as rows:
                header = next(rows).strip().upper().split('|')
                if not (header[0].strip() == 'RUC' and 'RAZ' in header[1] and 'ESTADO' in header[2] and 'CONDIC' in header[3] and 'UBIGEO' in header[4]):
                    raise ValueError('Columnas no reconocidas: ' + repr(header[:5]))
                batch = []
                for line in rows:
                    if not line.strip():
                        continue
                    cells = line.rstrip('\r\n').split('|')
                    if len(cells) < 5 or not re.fullmatch(r'[0-9]{11}', cells[0].strip()):
                        excluded += 1
                        if excluded > 100:
                            raise ValueError('Demasiadas filas invalidas; se conserva el padron anterior')
                        continue
                    batch.append(tuple(c.strip() for c in cells[:5]))
                    if len(batch) >= 20000:
                        con.executemany('INSERT INTO empresas VALUES (?,?,?,?,?)', batch)
                        count += len(batch)
                        batch.clear()
                        if count % 1000000 == 0:
                            print(f'Importadas {count:,} empresas', flush=True)
                con.executemany('INSERT INTO empresas VALUES (?,?,?,?,?)', batch)
                count += len(batch)
            if count == 0:
                raise ValueError('Padron vacio')
            meta = {'fechaPadron': date, 'fechaCarga': datetime.now(timezone.utc).isoformat(), 'filas': str(count), 'filasExcluidas': str(excluded), 'archivoFuente': 'https://www2.sunat.gob.pe/padron_reducido_ruc.zip'}
            con.executemany('INSERT INTO metadata VALUES (?,?)', meta.items())
            con.commit()
            if con.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise ValueError('Integridad incorrecta')
        os.replace(temp, target)
        print(json.dumps(meta), flush=True)
    except Exception:
        if temp.exists():
            temp.unlink()
        raise

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('zip')
    p.add_argument('database')
    p.add_argument('--fecha', required=True, help='Fecha publicada por SUNAT, AAAA-MM-DD')
    a = p.parse_args()
    build(a.zip, a.database, a.fecha)



