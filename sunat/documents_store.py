"""Recepción local de expedientes; no evalúa cumplimiento ni envía documentos a IA."""
import base64, hashlib, io, json, os, re, uuid, zipfile
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(os.environ.get('EXPEDIENTES_DIR','/data/expedientes'))
MAX_FILE=5*1024*1024
MAX_TOTAL=10*1024*1024

def validate_files(files, proposal=False):
    if not isinstance(files,list) or not (1 if proposal else 2)<=len(files)<=(2 if proposal else 11):
        raise ValueError('Adjunta una base y entre uno y diez documentos de empresa.')
    prepared=[]; total=0
    for item in files:
        if not isinstance(item,dict): raise ValueError('Archivo inválido.')
        category=item.get('categoria')
        if category not in (('propuesta','referencia') if proposal else ('bases','empresa')): raise ValueError('Categoría inválida.')
        name=str(item.get('nombre','')).replace('\\','/').split('/')[-1][:180]
        ext=Path(name).suffix.lower()
        if ext not in ('.pdf','.docx','.txt'): raise ValueError('Solo PDF, DOCX o TXT.')
        try: raw=base64.b64decode(item.get('contenido',''),validate=True)
        except Exception: raise ValueError('Contenido de archivo inválido.')
        total+=len(raw)
        if not raw or len(raw)>MAX_FILE or total>MAX_TOTAL: raise ValueError('Máximo 5 MB por archivo y 10 MB por envío.')
        if ext=='.pdf' and not raw.startswith(b'%PDF-'): raise ValueError('El archivo no tiene cabecera PDF.')
        if ext=='.docx':
            try:
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    if 'word/document.xml' not in z.namelist() or '[Content_Types].xml' not in z.namelist(): raise ValueError()
            except Exception: raise ValueError('El archivo no tiene estructura DOCX.')
        if ext=='.txt':
            try: raw.decode('utf-8-sig')
            except UnicodeDecodeError: raise ValueError('Los TXT deben estar en UTF-8.')
        prepared.append((category,name,ext,raw))
    if proposal:
        if sum(x[0]=='propuesta' for x in prepared)!=1 or sum(x[0]=='referencia' for x in prepared)>1:
            raise ValueError('Adjunta una propuesta propia y, opcionalmente, una de referencia.')
    elif sum(x[0]=='bases' for x in prepared)!=1 or not any(x[0]=='empresa' for x in prepared):
        raise ValueError('Adjunta exactamente una base y al menos un documento de empresa.')
    return prepared

def save(data, profile):
    reference=data.get('referencia','')
    if not isinstance(reference,str) or not reference.strip() or len(reference)>250:
        return {'resultado':'DOCUMENTOS_INVALIDOS','mensaje':'Indica la convocatoria (máximo 250 caracteres).'}
    try: files=validate_files(data.get('archivos'))
    except ValueError as e: return {'resultado':'DOCUMENTOS_INVALIDOS','mensaje':str(e)}
    ident=uuid.uuid4().hex
    folder=ROOT/ident
    manifest={'id':ident,'ruc':profile['ruc'],'razonSocial':profile['sunat']['razonSocial'],
      'referenciaDeclarada':reference.strip(),'fechaCarga':datetime.now(timezone.utc).isoformat(),
      'estado':'PENDIENTE_DE_ANALISIS','documentos':[],'perfilAlCargar':profile}
    try:
        folder.mkdir(parents=True,exist_ok=False)
        for i,(category,name,ext,raw) in enumerate(files,1):
            stored=str(i)+ext
            (folder/stored).write_bytes(raw)
            manifest['documentos'].append({'categoria':category,'nombre':name,'archivo':stored,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        (folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    except OSError:
        # Retirar solo los archivos creados en el directorio aleatorio de esta operación.
        if folder.is_dir():
            for p in folder.iterdir():
                if p.is_file(): p.unlink()
            folder.rmdir()
        return {'resultado':'ERROR_GUARDADO'}
    return {'resultado':'EXPEDIENTE_GUARDADO',**{k:v for k,v in manifest.items() if k!='perfilAlCargar'}}



def save_proposal(data):
    ident=data.get('expediente','')
    ruc=data.get('ruc','')
    if not isinstance(ident,str) or not re.fullmatch('[a-f0-9]{32}',ident) or not isinstance(ruc,str) or not re.fullmatch('[0-9]{11}',ruc):
        return {'resultado':'DOCUMENTOS_INVALIDOS','mensaje':'Revisa el RUC y el folio de 32 caracteres de la FASE 2.'}
    try:
        parent=json.loads((ROOT/ident/'manifest.json').read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {'resultado':'EXPEDIENTE_NO_ENCONTRADO'}
    except (OSError,ValueError):
        return {'resultado':'ERROR_LECTURA'}
    if parent.get('ruc')!=ruc:
        return {'resultado':'EXPEDIENTE_NO_ENCONTRADO'}
    source=data.get('fuenteReferencia','')
    if not isinstance(source,str) or len(source)>500:
        return {'resultado':'DOCUMENTOS_INVALIDOS','mensaje':'La fuente de referencia debe tener hasta 500 caracteres.'}
    try:
        files=validate_files(data.get('archivos'),proposal=True)
    except ValueError as e:
        return {'resultado':'DOCUMENTOS_INVALIDOS','mensaje':str(e)}
    has_reference=any(f[0]=='referencia' for f in files)
    if has_reference and not source.strip():
        return {'resultado':'DOCUMENTOS_INVALIDOS','mensaje':'Indica de dónde obtuviste la propuesta de referencia.'}
    revision=uuid.uuid4().hex
    folder=ROOT/ident/'propuestas'/revision
    manifest={'id':revision,'expediente':ident,'ruc':ruc,'razonSocial':parent['razonSocial'],
      'convocatoria':parent['referenciaDeclarada'],'fechaCarga':datetime.now(timezone.utc).isoformat(),
      'estado':'PENDIENTE_DE_REVISION','fuenteReferenciaDeclarada':source.strip() if has_reference else None,
      'conReferencia':has_reference,'documentos':[]}
    try:
        folder.mkdir(parents=True,exist_ok=False)
        for i,(category,name,ext,raw) in enumerate(files,1):
            stored=str(i)+ext
            (folder/stored).write_bytes(raw)
            manifest['documentos'].append({'categoria':category,'nombre':name,'archivo':stored,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        (folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    except OSError:
        if folder.is_dir():
            for p in folder.iterdir():
                if p.is_file(): p.unlink()
            folder.rmdir()
        return {'resultado':'ERROR_GUARDADO'}
    return {'resultado':'PROPUESTA_GUARDADA',**manifest}

def request_review(data):
    ident=data.get('expediente','');ruc=data.get('ruc','')
    if not isinstance(ident,str) or not re.fullmatch('[a-f0-9]{32}',ident) or not isinstance(ruc,str) or not re.fullmatch('[0-9]{11}',ruc):
        return {'resultado':'DATOS_INVALIDOS','mensaje':'Revisa el RUC y el folio de 32 caracteres de la FASE 2.'}
    inputs={}
    for field,limit in [('inquietud',2000),('ubicacion',500),('fuente',500)]:
        value=data.get(field,'')
        if not isinstance(value,str) or len(value)>limit:
            return {'resultado':'DATOS_INVALIDOS','mensaje':f'El campo {field} admite hasta {limit} caracteres.'}
        inputs[field]=value.strip()
    folder=ROOT/ident
    try:
        parent=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {'resultado':'EXPEDIENTE_NO_ENCONTRADO'}
    except (OSError,ValueError):
        return {'resultado':'ERROR_LECTURA'}
    if parent.get('ruc')!=ruc:return {'resultado':'EXPEDIENTE_NO_ENCONTRADO'}
    bases=[f for f in parent.get('documentos',[]) if f.get('categoria')=='bases']
    if not bases:return {'resultado':'BASES_NO_DISPONIBLES'}
    try:
        for f in bases:
            path=(folder/f['archivo']).resolve()
            if path.parent!=folder.resolve() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=f['sha256']:
                return {'resultado':'BASES_NO_DISPONIBLES'}
    except (OSError,KeyError):return {'resultado':'BASES_NO_DISPONIBLES'}
    review_id=uuid.uuid4().hex
    review={'id':review_id,'expediente':ident,'ruc':ruc,'razonSocial':parent['razonSocial'],
        'convocatoria':parent['referenciaDeclarada'],'fechaSolicitud':datetime.now(timezone.utc).isoformat(),
        'estado':'PENDIENTE_DE_ANALISIS','alcance':'Revisión general de bases' if not inputs['inquietud'] else 'Revisión de la inquietud declarada y de las bases',
        'datosDeclarados':inputs,'basesDisponibles':bases,
        'comprobacionesPendientes':['Leer requisitos y su justificación en las bases',
            'Contrastar el requisito con normativa aplicable y fuentes verificables',
            'Identificar evidencia a favor y en contra de una posible restricción',
            'Preparar hallazgos y, cuando corresponda, un borrador para revisión humana'],
        'hallazgos':None,'conclusionLegal':None,'borradorObservacion':None}
    target=folder/'revisiones'/review_id
    try:
        target.mkdir(parents=True,exist_ok=False)
        tmp=target/'solicitud.tmp'
        tmp.write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
        tmp.replace(target/'solicitud.json')
    except OSError:
        if target.is_dir():
            for p in target.iterdir():
                if p.is_file():p.unlink()
            target.rmdir()
        return {'resultado':'ERROR_GUARDADO'}
    return {'resultado':'REVISION_REGISTRADA',**review}
