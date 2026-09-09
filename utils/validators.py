"""
utils/validators.py - Validadores defensivos centralizados para formularios y entradas de usuario.
Alineado con prácticas de seguridad OWASP para prevenir inyecciones, XSS, desbordamientos y datos corruptos.
"""

import re
import math
import uuid
from datetime import date, datetime, timedelta
from markupsafe import escape


def validate_username(username: str) -> tuple[bool, str]:
    """
    Valida formato y longitud del nombre de usuario.
    Permite letras, números, puntos, guiones bajos y guiones (-).
    """
    if not username or not isinstance(username, str):
        return False, "El nombre de usuario es obligatorio."
    
    cleaned = username.strip()
    if len(cleaned) < 3:
        return False, "El nombre de usuario debe tener al menos 3 caracteres."
    if len(cleaned) > 30:
        return False, "El nombre de usuario no puede exceder 30 caracteres."
    
    if not re.match(r'^[a-zA-Z0-9._-]+$', cleaned):
        return False, "El nombre de usuario solo puede contener letras, números, puntos, guiones y guiones bajos."
    
    # Debe contener al menos un carácter alfanumérico
    if not re.search(r'[a-zA-Z0-9]', cleaned):
        return False, "El nombre de usuario debe contener al menos una letra o número."
        
    return True, cleaned


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valida los requisitos de robustez de contraseña:
    Mínimo 8 caracteres, al menos una mayúscula, una minúscula y un número.
    """
    if not password or not isinstance(password, str):
        return False, "La contraseña es obligatoria."
    
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if len(password) > 128:
        return False, "La contraseña no puede exceder 128 caracteres."
        
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    
    if not (has_lower and has_upper and has_digit):
        return False, "La contraseña debe incluir al menos una letra minúscula, una mayúscula y un número."
        
    return True, ""


def validate_person_name(name: str, field_name: str = "Nombre") -> tuple[bool, str]:
    """
    Valida nombres y apellidos de personas.
    Permite letras (incluyendo acentos/ñ), espacios, apóstrofes y guiones.
    """
    if not name or not isinstance(name, str):
        return False, f"El campo {field_name} es obligatorio."
    
    cleaned = name.strip()
    if len(cleaned) < 2:
        return False, f"{field_name} debe tener al menos 2 caracteres."
    if len(cleaned) > 30:
        return False, f"{field_name} no puede exceder 30 caracteres."
        
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]+$", cleaned):
        return False, f"{field_name} solo puede contener letras y espacios."
        
    return True, cleaned


def validate_phone(phone: str) -> tuple[bool, str, str]:
    """
    Normaliza y valida formato de número telefónico.
    Retorna (es_valido, telefono_formateado, mensaje_error).
    """
    if not phone or not isinstance(phone, str):
        return True, "", ""  # Opcional
        
    cleaned = phone.strip()
    # Permitir '+' al inicio y luego dígitos, espacios, guiones o paréntesis
    if not re.match(r'^\+?[0-9\s\-()]{7,20}$', cleaned):
        return False, "", "Formato de teléfono inválido (ejemplo: +58 412-1234567 o 04141234567)."
        
    digits_only = re.sub(r'\D', '', cleaned)
    if len(digits_only) < 7 or len(digits_only) > 15:
        return False, "", "El teléfono debe contener entre 7 y 15 dígitos numéricos."
        
    return True, cleaned, ""


def validate_uuid(val: str) -> bool:
    """Verifica si un string representa un UUID canónico válido."""
    if not val or not isinstance(val, str):
        return False
    try:
        uuid_obj = uuid.UUID(val.strip())
        return str(uuid_obj) == val.strip().lower()
    except (ValueError, TypeError, AttributeError):
        return False


def validate_positive_int(val: any, default: int = 0, min_val: int = 0, max_val: int = 10000) -> tuple[bool, int, str]:
    """
    Convierte y valida que un valor sea un entero dentro de un rango positivo seguro.
    """
    if val is None or val == '':
        return True, default, ""
    try:
        num = int(str(val).strip())
        if num < min_val:
            return False, default, f"El valor no puede ser inferior a {min_val}."
        if num > max_val:
            return False, default, f"El valor no puede exceder {max_val}."
        return True, num, ""
    except (ValueError, TypeError):
        return False, default, "Debe ser un número entero válido."


def validate_currency(val: any, default: float = 0.0, min_val: float = 0.0, max_val: float = 100000.0) -> tuple[bool, float, str]:
    """
    Convierte y valida montos monetarios (ofrendas).
    Protege contra NaN, Infinito y valores desproporcionados.
    """
    if val is None or val == '':
        return True, default, ""
    try:
        num = float(str(val).strip().replace(',', '.'))
        if math.isnan(num) or math.isinf(num):
            return False, default, "Monto numérico no válido."
        if num < min_val:
            return False, default, f"El monto no puede ser negativo ({min_val})."
        if num > max_val:
            return False, default, f"El monto no puede exceder {max_val:,.2f}."
        return True, round(num, 2), ""
    except (ValueError, TypeError):
        return False, default, "Debe ser un monto numérico válido."


def validate_date(date_str: str, allow_future: bool = False, max_past_days: int = 365) -> tuple[bool, str, str]:
    """
    Valida fechas en formato YYYY-MM-DD.
    """
    if not date_str or not isinstance(date_str, str):
        return False, "", "La fecha es obligatoria."
    
    cleaned = date_str.strip()
    try:
        parsed_date = datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError:
        return False, "", "Formato de fecha inválido. Utilice AAAA-MM-DD."
        
    hoy = date.today()
    if not allow_future and parsed_date > hoy:
        return False, "", "La fecha no puede ser futura."
        
    limite_pasado = hoy - timedelta(days=max_past_days)
    if parsed_date < limite_pasado:
        return False, "", f"La fecha no puede ser anterior a {limite_pasado.strftime('%Y-%m-%d')}."
        
    return True, cleaned, ""


def validate_time_range(hr_inicio: str, hr_fin: str) -> tuple[bool, str]:
    """
    Valida que las horas de inicio y fin tengan formato HH:MM y que hr_fin > hr_inicio.
    """
    if not hr_inicio or not hr_fin:
        return False, "Las horas de inicio y finalización son obligatorias."
        
    hr_inicio = hr_inicio.strip()[:5]
    hr_fin = hr_fin.strip()[:5]
    
    try:
        t_inicio = datetime.strptime(hr_inicio, "%H:%M").time()
        t_fin = datetime.strptime(hr_fin, "%H:%M").time()
    except ValueError:
        return False, "Formato de hora inválido. Utilice HH:MM."
        
    if t_fin <= t_inicio:
        return False, "La hora de finalización debe ser posterior a la hora de inicio."
        
    return True, ""


def sanitize_text(text: any, max_length: int = 255) -> str:
    """
    Limpia espacios en blanco, limita la longitud y neutraliza caracteres HTML (previene XSS).
    """
    if not text:
        return ""
    cleaned = str(text).strip()[:max_length]
    return str(escape(cleaned))


def validate_report_form(form_data: dict, cdp_id: int) -> tuple[bool, str, dict]:
    """
    Valida y sanitiza integralmente el formulario de un reporte de Casa de Paz.
    Retorna (es_valido, mensaje_error, datos_procesados).
    """
    # 1. Validar Fecha
    fecha_ok, fecha_val, msg = validate_date(form_data.get('fecha', ''), allow_future=False)
    if not fecha_ok:
        return False, f"Fecha inválida: {msg}", {}

    # 2. Validar Horas
    hr_inicio = form_data.get('hr_inicio', '').strip()
    hr_fin = form_data.get('hr_fin', '').strip()
    horas_ok, msg_horas = validate_time_range(hr_inicio, hr_fin)
    if not horas_ok:
        return False, msg_horas, {}

    # 3. Validar Tema
    tema = sanitize_text(form_data.get('tema', ''), max_length=100)
    if not tema or len(tema) < 2:
        return False, "El tema desarrollado es obligatorio y debe tener al menos 2 caracteres.", {}

    # 4. Validar Cifras de Asistencia
    asistencia_fields = [
        ('nro_regulares', 'Número de regulares'),
        ('nro_ninos', 'Número de niños'),
        ('nro_visitas', 'Número de visitas'),
        ('nro_comprometidos', 'Número de comprometidos'),
        ('reconciliaciones', 'Reconciliaciones'),
        ('confesiones', 'Conversiones / Confesiones')
    ]
    procesados = {}
    for campo, etiqueta in asistencia_fields:
        ok, val, err = validate_positive_int(form_data.get(campo, 0), default=0, min_val=0, max_val=2000)
        if not ok:
            return False, f"{etiqueta}: {err}", {}
        procesados[campo] = val

    # 5. Validar Ofrendas
    ok_usd, ofr_usd, err_usd = validate_currency(form_data.get('ofrendas_usd', 0.0), default=0.0, max_val=50000.0)
    if not ok_usd:
        return False, f"Ofrendas USD: {err_usd}", {}
    procesados['ofrendas_usd'] = ofr_usd

    ok_bs, ofr_bs, err_bs = validate_currency(form_data.get('ofrendas_bs', 0.0), default=0.0, max_val=5000000.0)
    if not ok_bs:
        return False, f"Ofrendas Bs: {err_bs}", {}
    procesados['ofrendas_bs'] = ofr_bs

    # 6. Cesta de Amor (Booleano)
    cesta_raw = form_data.get('cesta_amor', 0)
    cesta_val = 1 if str(cesta_raw).lower() in ('1', 'true', 'on', 'si', 'sí') else 0
    procesados['cesta_amor'] = cesta_val

    # 7. Observaciones (Sanitizadas)
    observaciones = sanitize_text(form_data.get('observaciones', ''), max_length=1000)
    procesados['observaciones'] = observaciones

    # 8. Encapsular datos finales
    lider_id_raw = form_data.get('lider_id')
    lider_id = None
    if lider_id_raw and str(lider_id_raw).isdigit():
        lider_id = int(lider_id_raw)

    datos_finales = {
        'cdp_id': cdp_id,
        'lider_id': lider_id,
        'fecha': fecha_val,
        'hr_inicio': hr_inicio[:5],
        'hr_fin': hr_fin[:5],
        'tema': tema,
        **procesados
    }

    return True, "", datos_finales
