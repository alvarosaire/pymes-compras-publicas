import json, os, re, sqlite3
from contextlib import closing
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import opportunities
import documents_store
import gemini_analysis

DB = Path(os.environ.get('PADRON_DB', '/data/padron.sqlite'))
SOURCE = 'https://www.sunat.gob.pe/descargaPRR/mrc137_padron_reducido.html'

def lookup(ruc):
    base = {'ruc': ruc, 'fuente': SOURCE, 'fechaConsulta': datetime.now(timezone.utc).isoformat(), 'tiempoReal': False}
    if not re.fullmatch(r'[0-9]{11}', ruc):
        return {**base, 'resultado': 'FORMATO_INVALIDO'}
    if not DB.is_file():
        return {**base, 'resultado': 'FUENTE_NO_DISPONIBLE'}
    try:
        with closing(sqlite3.connect(DB.as_uri() + '?mode=ro', uri=True, timeout=5)) as con:
            meta = dict(con.execute('SELECT clave, valor FROM metadata'))
            row = con.execute('SELECT razon_social, estado, condicion, ubigeo FROM empresas WHERE ruc=?', (ruc,)).fetchone()
        base.update(fechaPadron=meta['fechaPadron'], fechaCarga=meta['fechaCarga'])
        if row is None:
            return {**base, 'resultado': 'NO_ENCONTRADO'}
        return {**base, 'resultado': 'ENCONTRADO', **dict(zip(('razonSocial', 'estado', 'condicion', 'ubigeo'), row))}
    except (sqlite3.Error, KeyError, OSError):
        return {**base, 'resultado': 'FUENTE_NO_DISPONIBLE'}


PROFILES_DB = Path(os.environ.get('PROFILES_DB', '/data/perfiles.sqlite'))

def save_profile(data):
    fields = {'ruc': 11, 'productos': 2000, 'regiones': 500, 'experiencia': 2000}
    cleaned = {}
    for key, limit in fields.items():
        value = data.get(key, '')
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
            return {'resultado': 'DATOS_INVALIDOS', 'campo': key}
        cleaned[key] = value.strip()
    official = lookup(cleaned['ruc'])
    if official['resultado'] != 'ENCONTRADO':
        return official
    stamp = datetime.now(timezone.utc).isoformat()
    document = {**cleaned, 'sunat': official, 'rnp': 'PENDIENTE_DE_VERIFICACION',
                'datosComerciales': 'DECLARADOS_POR_USUARIO', 'actualizadoEn': stamp}
    try:
        PROFILES_DB.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(PROFILES_DB, timeout=10)) as con:
            con.execute('CREATE TABLE IF NOT EXISTS perfiles (ruc TEXT PRIMARY KEY, documento TEXT NOT NULL, creado TEXT NOT NULL, actualizado TEXT NOT NULL)')
            con.execute('INSERT INTO perfiles VALUES (?,?,?,?) ON CONFLICT(ruc) DO UPDATE SET documento=excluded.documento, actualizado=excluded.actualizado',
                        (cleaned['ruc'], json.dumps(document, ensure_ascii=False), stamp, stamp))
            con.commit()
    except (sqlite3.Error, OSError):
        return {'resultado': 'ERROR_GUARDADO'}
    return {'resultado': 'PERFIL_GUARDADO', 'perfil': document}



def read_profile(ruc):
    if not re.fullmatch(r'[0-9]{11}', ruc):
        return {'resultado': 'FORMATO_INVALIDO'}
    if not PROFILES_DB.is_file():
        return {'resultado': 'PERFIL_NO_ENCONTRADO'}
    try:
        with closing(sqlite3.connect(PROFILES_DB.as_uri()+'?mode=ro', uri=True)) as con:
            row=con.execute('SELECT documento FROM perfiles WHERE ruc=?',(ruc,)).fetchone()
        return {'resultado':'PERFIL_ENCONTRADO','perfil':json.loads(row[0])} if row else {'resultado':'PERFIL_NO_ENCONTRADO'}
    except (sqlite3.Error, ValueError):
        return {'resultado':'ERROR_PERFIL'}

def search_opportunities(data):
    profile=read_profile(str(data.get('ruc','')).strip())
    if profile['resultado']!='PERFIL_ENCONTRADO':
        return profile
    result=opportunities.search(profile['perfil'])
    result['ruc']=profile['perfil']['ruc']
    result['razonSocial']=profile['perfil']['sunat']['razonSocial']
    if result['resultado'] in ('BUSQUEDA_COMPLETA','BUSQUEDA_PARCIAL'):
        try:
            with closing(sqlite3.connect(PROFILES_DB,timeout=10)) as con:
                con.execute('CREATE TABLE IF NOT EXISTS busquedas (ruc TEXT PRIMARY KEY, documento TEXT NOT NULL)')
                con.execute('INSERT INTO busquedas VALUES (?,?) ON CONFLICT(ruc) DO UPDATE SET documento=excluded.documento',
                            (result['ruc'],json.dumps(result,ensure_ascii=False)))
                con.commit()
        except sqlite3.Error:
            result.setdefault('advertencias',[]).append('La búsqueda respondió, pero no se pudo guardar el resumen.')
    return result

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        path=urlparse(self.path).path
        if path not in ('/perfiles','/oportunidades','/expedientes','/propuestas','/revisiones','/analisis/preparar','/analisis/guardar'):
            self.send_error(404)
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size <= 0 or size > (15*1024*1024 if path in ('/expedientes','/propuestas') else (256*1024 if path=='/analisis/guardar' else 16384)):
                self.send_error(413)
                return
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError()
            if path=='/analisis/preparar':
                result=gemini_analysis.prepare(data)
            elif path=='/analisis/guardar':
                result=gemini_analysis.finish(data)
            elif path=='/revisiones':
                result=documents_store.request_review(data)
            elif path=='/propuestas':
                result=documents_store.save_proposal(data)
            elif path=='/expedientes':
                profile=read_profile(str(data.get('ruc','')).strip())
                result=documents_store.save(data,profile['perfil']) if profile['resultado']=='PERFIL_ENCONTRADO' else profile
            else:
                result = save_profile(data) if path=='/perfiles' else search_opportunities(data)
        except (ValueError, UnicodeDecodeError):
            result = {'resultado': 'DATOS_INVALIDOS'}
        payload = json.dumps(result, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/health':
            body, code = {'servicio': 'ok', 'padronCargado': DB.is_file()}, 200
        elif path.startswith('/perfiles/'):
            body, code = read_profile(path[len('/perfiles/'):]), 200
        elif path.startswith('/ruc/'):
            body, code = lookup(path[len('/ruc/'):]), 200
        else:
            body, code = {'error': 'Ruta no encontrada'}, 404
        payload = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        pass  # No registrar los RUC ingresados.

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()



