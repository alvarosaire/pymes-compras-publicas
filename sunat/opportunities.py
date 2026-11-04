"""Radar de convocatorias públicas. Coincidencia léxica, no dictamen de aptitud."""
import json, re, time, unicodedata, threading
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

BASE = 'https://prod4.seace.gob.pe:8086/api/oportunidades'
PORTAL = 'https://prod4.seace.gob.pe/openegocio/'
LIST_URL = BASE + '/codObjeto/codDepartamento/sintesisProceso/codTipoProceso/0/0/0/0'
LIMA = timezone(timedelta(hours=-5))
_CACHE = {}
_LOCK = threading.Lock()
STOP = set('de del la las el los y en para con por un una unos unas empresa venta ventas comercializacion fabricacion fabricamos vendemos servicios servicio productos producto suministro suministros distribucion ofrecemos ofrecemos'.split())
REGIONS = ['Amazonas','Ancash','Apurimac','Arequipa','Ayacucho','Cajamarca','Callao','Cusco','Huancavelica','Huanuco','Ica','Junin','La Libertad','Lambayeque','Lima','Loreto','Madre de Dios','Moquegua','Pasco','Piura','Puno','San Martin','Tacna','Tumbes','Ucayali']

def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(value).lower()) if not unicodedata.combining(c))

def stem(word):
    if len(word)>5 and word.endswith(('iones','ones','ores','ales','iles')): return word[:-2]
    if len(word)>4 and word.endswith('ces'): return word[:-3]+'z'
    if len(word)>4 and word.endswith('s'): return word[:-1]
    return word

def keywords(text):
    return list(dict.fromkeys(stem(w) for w in re.findall(r'[a-z0-9]+',normalize(text)) if len(w)>2 and w not in STOP))[:16]

def product_terms(text):
    terms=keywords(text)
    # En descanso, base/box/tarima/protector/dormitorio no identifican por sí solos el producto.
    if any(t in terms for t in ('colchon','cama','almohada')):
        terms=[t for t in terms if t not in ('base','box','tarima','protector','dormitorio')]
        if 'dormitorio' in normalize(text) and 'mueble' in terms:
            terms.remove('mueble')
            terms.append('mueble dormitorio')
    return terms

def item_matches(row, terms):
    # El catálogo describe el objeto contratado, evitando nombres de sedes o beneficiarios.
    catalog=row.get('detCubso') or row.get('descripcionCubso')
    text=catalog or row.get('detItem') or row.get('descripcion') or row.get('sintesisProceso') or ''
    tokens={stem(w) for w in re.findall(r'[a-z0-9]+',normalize(text))}
    ordered=' '.join(stem(w) for w in re.findall(r'[a-z0-9]+',normalize(text)) if w not in STOP)
    return [t for t in terms if (t in tokens if ' ' not in t else (' '+t+' ') in (' '+ordered+' '))]

def json_get(url, ttl=180):
    with _LOCK:
        hit=_CACHE.get(url)
        if hit and time.monotonic()-hit[0]<ttl: return hit[1],hit[2]
    req=Request(url,headers={'Accept':'application/json','User-Agent':'PYMES-prototipo-local/1.0'})
    with urlopen(req,timeout=12) as response:
        raw=response.read(12_000_001)
        if len(raw)>12_000_000: raise ValueError('Respuesta demasiado grande')
        result=json.loads(raw)
    consulted=datetime.now(LIMA).isoformat()
    with _LOCK: _CACHE[url]=(time.monotonic(),result,consulted)
    return result,consulted

def parse_date(value):
    try: return datetime.strptime(value,'%d/%m/%Y %H:%M:%S').replace(tzinfo=LIMA)
    except (TypeError,ValueError): return None

def classify_candidates(rows, terms, now):
    found={}
    for row in rows:
        if not isinstance(row,dict): raise ValueError('Fila inválida')
        ident=row.get('idProcedimiento')
        if not isinstance(ident,int): continue
        matches=item_matches(row,terms)
        if not matches: continue
        end=parse_date(row.get('fecFinParticipantes') or row.get('fechaFin'))
        if end is not None and end<now: continue
        current=found.get(ident)
        if current is None or len(matches)>len(current[1]):
            found[ident]=(row,matches,end)
    return sorted(found.values(),key=lambda x:(-len(x[1]),x[2] or datetime.max.replace(tzinfo=LIMA)))

def search(profile):
    now=datetime.now(LIMA)
    terms=product_terms(profile.get('productos',''))
    region_text=normalize(profile.get('regiones',''))
    nationwide=any(x in region_text for x in ['nacional','todo el peru','todas las regiones','todo peru'])
    regions=[r for r in REGIONS if re.search(r'\b'+re.escape(normalize(r))+r'\b',region_text)]
    alerts=[]
    if not nationwide and not regions:
        alerts.append('No se reconoció una región del perfil: no se excluyeron oportunidades por región.')
    common={'fuente':PORTAL,'fechaBusqueda':now.isoformat(),'terminos':terms,'regiones':regions,'metodo':'Coincidencia en el catálogo del producto o descripción del ítem; no evalúa requisitos ni probabilidad de ganar.'}
    if not terms: return {**common,'resultado':'PERFIL_SIN_TERMINOS','oportunidades':[]}
    try:
        rows,consulted=json_get(LIST_URL)
        if not isinstance(rows,list): raise ValueError('Respuesta no válida')
        candidates=classify_candidates(rows,terms,now)
    except Exception:
        return {**common,'resultado':'FUENTE_NO_DISPONIBLE','oportunidades':[]}
    selected=candidates[:20]
    if len(candidates)>20: alerts.append('Se revisaron las fichas de los primeros 20 procedimientos por coincidencia. La búsqueda es parcial.')
    def detail(candidate):
        row,matches,end=candidate
        try:
            ficha,_=json_get(BASE+'/fichaProceso/idProceso/'+str(row['idProcedimiento']))
            if not isinstance(ficha,dict) or 'listaItems' not in ficha: raise ValueError()
            return candidate,ficha
        except Exception: return candidate,None
    with ThreadPoolExecutor(max_workers=4) as pool: details=list(pool.map(detail,selected))
    results=[]
    incomplete=0
    for (row,matches,end),ficha in details:
        if ficha is None:
            incomplete+=1
        # Región de los ítems, no ubicación de la entidad.
        items=(ficha or {}).get('listaItems',[])
        described=[i for i in items if i.get('descripcionCubso') or i.get('descripcion')]
        relevant=[i for i in described if item_matches(i,terms)]
        if described and not relevant:
            continue
        item_regions=list(dict.fromkeys(str(i.get('departamento')).strip() for i in (relevant if described else items) if i.get('departamento')))
        region_match=any(normalize(r)==normalize(v) for r in regions for v in item_regions)
        if regions and not nationwide and item_regions and not region_match: continue
        region_status='Nacional' if nationwide else ('Coincide' if region_match else 'Por verificar')
        beginning=parse_date(row.get('fecInicioParticipantes') or row.get('fechaInicio'))
        status='Por verificar' if end is None else ('Próxima apertura' if beginning and beginning>now else 'Registro abierto según fechas')
        ident=row['idProcedimiento']
        documents=[]
        for d in (ficha or {}).get('listaDocumentos',[]):
            code=d.get('codigoAlfresco')
            if isinstance(code,str) and re.fullmatch('[a-fA-F0-9-]{36}',code) and 'base' in normalize(d.get('tipoDocumento','')):
                documents.append({'nombre':d.get('nombreArchivo') or 'Bases','url':'https://prod1.seace.gob.pe/SeaceWeb-PRO/SdescargarArchivoAlfresco?fileCode='+quote(code)})
        results.append({'id':ident,'nomenclatura':row.get('nomenclatura'),'entidad':row.get('detEntidad'),
          'descripcion':row.get('sintesisProceso') or row.get('detItem'),'objeto':row.get('detObjeto'),
          'regionItems':item_regions,'coincidenciaRegion':region_status,'coincidencias':matches,
          'motivo':'Posible coincidencia en el ítem: '+', '.join(matches)+'. '+('Ítem relacionado: '+ '; '.join(str(i.get('descripcion') or i.get('descripcionCubso')) for i in relevant[:3])+'. ' if relevant else '')+'Región: '+region_status+'. Verificar especificaciones; compatibilidad no confirmada.',
          'inscripcionHasta':row.get('fecFinParticipantes') or row.get('fechaFin'),
          'presentacionOferta':row.get('fechaPresentacionPropuestas'),'estadoPlazo':status,
          'monto':row.get('valorReferencial'),'moneda':row.get('monedaProceso'),
          'url':PORTAL+'#/ficha/idProceso/'+str(ident),'bases':documents,
          'detalleConsultado':ficha is not None})
    if incomplete: alerts.append(str(incomplete)+' fichas no pudieron consultarse; sus regiones y documentos quedan por verificar.')
    results.sort(key=lambda r:(r['coincidenciaRegion']=='Por verificar',-len(r['coincidencias'])))
    partial=len(candidates)>20 or incomplete>0
    return {**common,'resultado':'BUSQUEDA_PARCIAL' if partial else 'BUSQUEDA_COMPLETA',
      'fechaConsultaFuente':consulted,'registrosConsultados':len(rows),'candidatosPorPalabras':len(candidates),
      'fichasRevisadas':len(selected),'coincidenciasTrasFiltros':len(results),'oportunidades':results[:10],
      'limiteMostrado':10,'advertencias':alerts}

