"""
services/queries/helpers.py - Utilidades de formateo, fechas y comprobaciones de esquema.
"""
from datetime import date, timedelta, datetime
import re
from pymysql.cursors import Cursor

_currency_columns_checked = False

def formatear_hora(valor) -> str:
    """Formatea valores de hora (timedelta, time, datetime, str) al formato estándar HH:MM."""
    if not valor:
        return ''
    # PyMySQL entrega campos TIME como datetime.timedelta
    if isinstance(valor, timedelta) or hasattr(valor, 'total_seconds'):
        total_segundos = int(valor.total_seconds()) % 86400
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        return f"{horas:02d}:{minutos:02d}"
    if hasattr(valor, 'strftime'):
        return valor.strftime("%H:%M")

    val_str = str(valor).strip()
    if ':' in val_str:
        partes = val_str.split(':')
        if len(partes) >= 2 and partes[0].isdigit() and partes[1].isdigit():
            return f"{int(partes[0]):02d}:{int(partes[1]):02d}"
    return val_str[:5] if len(val_str) >= 5 else val_str


def formatear_horario_cdp(hr_val, fecha_val) -> str:
    """
    Formatea el horario en formato amigable 'Día · h:mm AM/PM'.
    Si no hay datos, retorna el estándar institucional 'Miércoles · 7:00 PM'.
    """
    from datetime import datetime
    dias_semana = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}

    # 1. Determinar día de la semana
    dia_txt = 'Miércoles'
    if fecha_val:
        if isinstance(fecha_val, str):
            try:
                f_obj = datetime.strptime(fecha_val[:10], '%Y-%m-%d')
                dia_txt = dias_semana.get(f_obj.weekday(), 'Miércoles')
            except Exception:
                pass
        elif hasattr(fecha_val, 'weekday'):
            dia_txt = dias_semana.get(fecha_val.weekday(), 'Miércoles')

    # 2. Determinar y convertir hora a formato 12h (AM/PM)
    if not hr_val:
        return f"{dia_txt} · 7:00 PM"

    hora_24 = formatear_hora(hr_val)
    if not hora_24 or ':' not in hora_24:
        return f"{dia_txt} · 7:00 PM"

    try:
        partes = hora_24.split(':')
        h = int(partes[0])
        m = int(partes[1])
        suffix = 'AM' if h < 12 else 'PM'
        h12 = h % 12
        if h12 == 0:
            h12 = 12
        return f"{dia_txt} · {h12}:{m:02d} {suffix}"
    except Exception:
        return f"{dia_txt} · {hora_24}"


def _asistencia_fila(row):
    """Calcula la asistencia total de un registro de reporte."""
    return (
        (row.get('nro_regulares') or 0)
        + (row.get('nro_niños') or 0)
        + (row.get('nro_visitas') or 0)
        + (row.get('nro_comprometidos') or 0)
    )


def _semana_label(fecha):
    """Retorna una etiqueta legible tipo 'Sem 1' a partir de una fecha."""
    dia = fecha.day
    if dia <= 7:
        return 'Sem 1'
    elif dia <= 14:
        return 'Sem 2'
    elif dia <= 21:
        return 'Sem 3'
    else:
        return 'Sem 4'


def formatear_fecha_corta(fecha_val) -> str:
    """Formatea una fecha como fecha corta legible en español (ej. '28 Ago', '04 Sep')."""
    if not fecha_val:
        return ''
    meses_abr = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    if isinstance(fecha_val, str):
        f_str = fecha_val.strip()
        try:
            fecha_val = date.fromisoformat(f_str[:10])
        except Exception:
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
                try:
                    fecha_val = datetime.strptime(f_str[:10], fmt).date()
                    break
                except Exception:
                    continue
            else:
                return f_str
    if hasattr(fecha_val, 'day') and hasattr(fecha_val, 'month'):
        return f"{fecha_val.day:02d} {meses_abr.get(fecha_val.month, '')}"
    return str(fecha_val)


def formatear_mes_nombre(fecha_val) -> str:
    """Formatea una fecha retornando el nombre abreviado del mes en español (ej. 'Ene', 'Feb')."""
    if not fecha_val:
        return ''
    meses_abr = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    if isinstance(fecha_val, str):
        f_str = fecha_val.strip()
        try:
            fecha_val = date.fromisoformat(f_str[:10])
        except Exception:
            try:
                fecha_val = datetime.strptime(f_str[:10], '%Y-%m-%d').date()
            except Exception:
                return f_str
    if hasattr(fecha_val, 'month'):
        return meses_abr.get(fecha_val.month, '')
    return str(fecha_val)


def _obtener_rango_periodo(periodo='semana', mes=None, anio=None):
    """Retorna (fecha_inicio, fecha_fin) para el período solicitado según el calendario natural."""
    hoy = date.today()
    try:
        target_year = int(anio) if anio is not None and str(anio).isdigit() else hoy.year
    except Exception:
        target_year = hoy.year

    if periodo == 'mes':
        try:
            target_month = int(mes) if mes is not None and str(mes).isdigit() and 1 <= int(mes) <= 12 else hoy.month
        except Exception:
            target_month = hoy.month
        inicio = date(target_year, target_month, 1)
        if target_month == 12:
            fin = date(target_year, 12, 31)
        else:
            fin = date(target_year, target_month + 1, 1) - timedelta(days=1)
        return inicio, fin
    elif periodo == 'anio':
        return date(target_year, 1, 1), date(target_year, 12, 31)
    return hoy - timedelta(days=7), hoy


def _obtener_metadatos_periodo(periodo='semana', fecha_desde=None, fecha_hasta=None, mes=None, anio=None):
    """Genera etiquetas amigables del período para títulos y subtítulos del dashboard."""
    hoy = date.today()
    target_year = fecha_desde.year if (fecha_desde and hasattr(fecha_desde, 'year')) else hoy.year
    target_month = fecha_desde.month if (fecha_desde and hasattr(fecha_desde, 'month')) else hoy.month
    meses_completos = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    if periodo == 'mes':
        nombre_m = meses_completos[target_month]
        return {
            'periodo_nombre': f"{nombre_m} {target_year}",
            'nombre_mes': nombre_m,
            'mes_numero': target_month,
            'anio': target_year,
        }
    elif periodo == 'anio':
        return {
            'periodo_nombre': f"Año {target_year}",
            'nombre_mes': '',
            'mes_numero': None,
            'anio': target_year,
        }
    return {
        'periodo_nombre': 'Esta Semana',
        'nombre_mes': '',
        'mes_numero': None,
        'anio': target_year,
    }


def _periodo_a_fecha(periodo='semana', mes=None, anio=None):
    """Convierte un período ('semana', 'mes', 'anio') a la fecha límite desde."""
    return _obtener_rango_periodo(periodo, mes=mes, anio=anio)[0]


def _ensure_currency_columns(cursor):
    """Asegura que las columnas ofrendas_bs y ofrendas_usd existan en la tabla reporte una sola vez en el ciclo de la app."""
    import sys
    db_mod = sys.modules.get('db_queries')
    global _currency_columns_checked
    if db_mod and hasattr(db_mod, '_currency_columns_checked'):
        _currency_columns_checked = db_mod._currency_columns_checked
    if _currency_columns_checked:
        return
    try:
        cursor.execute("SHOW COLUMNS FROM reporte LIKE 'ofrendas_bs'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE reporte ADD COLUMN ofrendas_bs DECIMAL(10,2) NOT NULL DEFAULT 0.00")
        cursor.execute("SHOW COLUMNS FROM reporte LIKE 'ofrendas_usd'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE reporte ADD COLUMN ofrendas_usd DECIMAL(10,2) NOT NULL DEFAULT 0.00")
        _currency_columns_checked = True
        if db_mod:
            db_mod._currency_columns_checked = True
    except Exception:
        pass
