"""
Servicio de exportación binaria server-side para Vino Nuevo.
Genera reportes consolidados en PDF (fpdf2) y listados en Excel (.xlsx vía openpyxl)
y CSV (UTF-8 con BOM), con saneamiento anti-inyección de fórmulas en hojas de cálculo.
"""
import csv
import io
import re
from datetime import date
from typing import Any, Iterable, Optional

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

MAX_EXPORT_ROWS = 5000
FORMULA_PREFIXES = ('=', '+', '-', '@', '\t', '\r')
_E164_RE = re.compile(r'^\+\d{8,15}$')

MIME_PDF = 'application/pdf'
MIME_XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
MIME_CSV = 'text/csv; charset=utf-8'

_WINE_DARK_HEX = '4A0203'
_WINE_TEXT_HEX = '390002'
_ROSE_LIGHT_HEX = 'F8E4E3'
_ZEBRA_HEX = 'FAF7F7'
_BORDER_HEX = 'DDC0BD'


def sanitize_spreadsheet_cell(value: Any, *, is_phone: bool = False) -> Any:
    """
    Neutraliza prefijos de fórmulas peligrosas (=, +, -, @, tab, CR) en celdas de texto
    para prevenir CSV/Excel Formula Injection, preservando números reales y teléfonos
    E.164 válidos cuando corresponden a columnas de contacto.
    """
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'Sí' if value else 'No'
    if isinstance(value, (int, float)):
        return value

    text = str(value).strip()
    if not text:
        return ''

    if is_phone and _E164_RE.match(text):
        return text

    if text[0] in FORMULA_PREFIXES:
        return "'" + text
    return text


def _pdf_safe_text(value: Any, max_len: Optional[int] = None) -> str:
    """Convierte texto a Latin-1 seguro para fuentes core de fpdf2 sin fallar con emojis."""
    if value is None:
        return ''
    text = str(value).strip()
    replacements = {
        '\u2014': '-',
        '\u2013': '-',
        '\u2022': '-',
        '\u00b7': '|',
        '\u201c': '"',
        '\u201d': '"',
        '\u2018': "'",
        '\u2019': "'",
        '\u2026': '...',
        '\u00a0': ' ',
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = re.sub(r'\s+', ' ', text)
    if max_len and len(text) > max_len:
        text = text[: max_len - 3].rstrip() + '...'
    # Mantener caracteres soportados por latin-1 (incluye tildes y ñ en español)
    return text.encode('latin-1', errors='replace').decode('latin-1')


def _to_int(val: Any) -> int:
    try:
        return int(val or 0)
    except (ValueError, TypeError):
        return 0


def _to_float(val: Any) -> float:
    try:
        return round(float(val or 0.0), 2)
    except (ValueError, TypeError):
        return 0.0


def _format_fecha(val: Any) -> str:
    if val is None:
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    return str(val)[:10]


def _compute_asistencia(rep: dict) -> int:
    if rep.get('asistencia') is not None:
        return _to_int(rep.get('asistencia'))
    ninos = rep.get('nro_niños', rep.get('nro_ninos', 0))
    return (
        _to_int(rep.get('nro_regulares'))
        + _to_int(ninos)
        + _to_int(rep.get('nro_visitas'))
        + _to_int(rep.get('nro_comprometidos'))
    )


def build_csv(
    headers: list[str],
    rows: Iterable[list[Any]],
    *,
    phone_columns: Optional[set[int]] = None,
) -> bytes:
    """Genera un CSV codificado en UTF-8 con BOM y saneamiento anti-fórmulas."""
    phone_cols = phone_columns or set()
    buf = io.StringIO()
    buf.write('\ufeff')
    writer = csv.writer(buf, lineterminator='\r\n')
    writer.writerow(headers)
    for row in rows:
        sanitized = [
            sanitize_spreadsheet_cell(val, is_phone=(idx in phone_cols))
            for idx, val in enumerate(row)
        ]
        writer.writerow(sanitized)
    return buf.getvalue().encode('utf-8')


def build_xlsx(
    sheet_title: str,
    headers: list[str],
    rows: list[list[Any]],
    *,
    summary_row: Optional[list[Any]] = None,
    phone_columns: Optional[set[int]] = None,
    currency_usd_columns: Optional[set[int]] = None,
    currency_bs_columns: Optional[set[int]] = None,
    int_columns: Optional[set[int]] = None,
) -> bytes:
    """Genera un archivo Excel binario (.xlsx) estilizado en memoria con openpyxl."""
    phone_cols = phone_columns or set()
    usd_cols = currency_usd_columns or set()
    bs_cols = currency_bs_columns or set()
    int_cols = int_columns or set()

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_title[:31]
    ws.freeze_panes = 'A2'

    header_fill = PatternFill(start_color=_WINE_DARK_HEX, end_color=_WINE_DARK_HEX, fill_type='solid')
    header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    zebra_fill = PatternFill(start_color=_ZEBRA_HEX, end_color=_ZEBRA_HEX, fill_type='solid')
    total_fill = PatternFill(start_color=_ROSE_LIGHT_HEX, end_color=_ROSE_LIGHT_HEX, fill_type='solid')
    total_font = Font(name='Calibri', size=11, bold=True, color=_WINE_TEXT_HEX)
    body_font = Font(name='Calibri', size=10, color='2B1111')
    thin_side = Side(style='thin', color=_BORDER_HEX)
    cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

    # Encabezados
    for col_idx, title in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=title)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = cell_border
    ws.row_dimensions[1].height = 24

    # Filas de datos
    for r_idx, row in enumerate(rows, start=2):
        is_even = (r_idx % 2 == 0)
        for c_idx, raw_val in enumerate(row):
            val = sanitize_spreadsheet_cell(raw_val, is_phone=(c_idx in phone_cols))
            cell = ws.cell(row=r_idx, column=c_idx + 1, value=val)
            cell.font = body_font
            cell.border = cell_border
            if not is_even:
                cell.fill = zebra_fill

            if c_idx in phone_cols:
                cell.number_format = '@'
                cell.alignment = Alignment(horizontal='left', vertical='center')
            elif c_idx in usd_cols:
                cell.number_format = '$#,##0.00'
                cell.alignment = Alignment(horizontal='right', vertical='center')
            elif c_idx in bs_cols:
                cell.number_format = '#,##0.00'
                cell.alignment = Alignment(horizontal='right', vertical='center')
            elif c_idx in int_cols:
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal='center', vertical='center')
            else:
                cell.alignment = Alignment(horizontal='left', vertical='center')

    # Fila de totales opcional
    if summary_row is not None:
        total_row_idx = len(rows) + 2
        for c_idx, raw_val in enumerate(summary_row):
            val = sanitize_spreadsheet_cell(raw_val, is_phone=(c_idx in phone_cols))
            cell = ws.cell(row=total_row_idx, column=c_idx + 1, value=val)
            cell.fill = total_fill
            cell.font = total_font
            cell.border = cell_border
            if c_idx in usd_cols:
                cell.number_format = '$#,##0.00'
                cell.alignment = Alignment(horizontal='right', vertical='center')
            elif c_idx in bs_cols:
                cell.number_format = '#,##0.00'
                cell.alignment = Alignment(horizontal='right', vertical='center')
            elif c_idx in int_cols:
                cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal='center', vertical='center')
            else:
                cell.alignment = Alignment(horizontal='left', vertical='center')
        ws.row_dimensions[total_row_idx].height = 22

    # Ajuste automático de anchos
    for col_idx, header in enumerate(headers, start=1):
        max_len = len(str(header))
        for r_idx in range(2, ws.max_row + 1):
            val = ws.cell(row=r_idx, column=col_idx).value
            if val is not None:
                max_len = max(max_len, len(str(val)))
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max(max_len + 4, 12), 42)

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


class _ReportesPdf(FPDF):
    """Documento PDF institucional en orientación horizontal para reportes consolidados."""

    def __init__(self, emission_date: str, filters_summary: str = ''):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.emission_date = emission_date
        self.filters_summary = filters_summary
        self.set_auto_page_break(auto=True, margin=16)

    def header(self):
        # Barra superior vino institucional
        self.set_fill_color(74, 2, 3)
        self.rect(10, 10, 277, 16, style='F')
        self.set_xy(14, 12)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(255, 255, 255)
        self.cell(190, 6, _pdf_safe_text('Comunidad Cristiana Vino Nuevo'), new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_font('Helvetica', '', 9)
        self.cell(79, 6, _pdf_safe_text(f'Emisión: {self.emission_date}'), align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_x(14)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(248, 222, 218)
        subtitle = 'Reporte Consolidado de Actividad Ministerial · Casas de Paz'
        if self.filters_summary:
            subtitle = f'{subtitle} | Filtros: {self.filters_summary}'
        self.cell(269, 5, _pdf_safe_text(subtitle, max_len=145), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(43, 17, 17)
        self.ln(5)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 100, 98)
        self.cell(
            0,
            6,
            _pdf_safe_text(f'Sistema de Gestión Vino Nuevo · Página {self.page_no()}/{{nb}}'),
            align='C',
        )


def build_reportes_pdf(
    reportes: list[dict],
    *,
    filters_summary: str = '',
    emission_date: Optional[str] = None,
) -> bytes:
    """Genera un PDF binario consolidado con resumen de KPIs, detalle y totales."""
    em_date = emission_date or date.today().strftime('%Y-%m-%d')
    pdf = _ReportesPdf(emission_date=em_date, filters_summary=filters_summary)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Totales globales
    total_reportes = len(reportes)
    total_reg = sum(_to_int(r.get('nro_regulares')) for r in reportes)
    total_ninos = sum(_to_int(r.get('nro_niños', r.get('nro_ninos', 0))) for r in reportes)
    total_vis = sum(_to_int(r.get('nro_visitas')) for r in reportes)
    total_comp = sum(_to_int(r.get('nro_comprometidos')) for r in reportes)
    total_asis = sum(_compute_asistencia(r) for r in reportes)
    total_usd = round(sum(_to_float(r.get('ofrendas_usd')) for r in reportes), 2)
    total_bs = round(sum(_to_float(r.get('ofrendas_bs')) for r in reportes), 2)

    # Franja de resumen ejecutivo
    kpis = [
        ('REPORTES', str(total_reportes)),
        ('ASISTENCIA TOTAL', f'{total_asis:,}'),
        ('OFRENDAS (USD)', f'${total_usd:,.2f}'),
        ('OFRENDAS (BS)', f'Bs. {total_bs:,.2f}'),
    ]
    box_w = 67
    gap = 3
    start_x = 10
    y_top = pdf.get_y()
    for idx, (label, val) in enumerate(kpis):
        x = start_x + idx * (box_w + gap)
        pdf.set_fill_color(248, 228, 227)
        pdf.set_draw_color(221, 192, 189)
        pdf.rect(x, y_top, box_w, 14, style='DF')
        pdf.set_xy(x + 3, y_top + 2)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_text_color(120, 2, 4)
        pdf.cell(box_w - 6, 4, _pdf_safe_text(label), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(x + 3)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(57, 0, 2)
        pdf.cell(box_w - 6, 6, _pdf_safe_text(val), new_x=XPos.RIGHT, new_y=YPos.TOP)

    pdf.set_xy(10, y_top + 18)

    # Definición de columnas (ancho total = 277 mm)
    cols = [
        ('Fecha', 22, 'C'),
        ('Red', 28, 'L'),
        ('Casa de Paz', 38, 'L'),
        ('Líder', 38, 'L'),
        ('Tema', 51, 'L'),
        ('Reg', 12, 'C'),
        ('Niñ', 12, 'C'),
        ('Vis', 12, 'C'),
        ('Cmp', 12, 'C'),
        ('Total', 14, 'C'),
        ('USD', 18, 'R'),
        ('Bs', 20, 'R'),
    ]

    def _draw_table_header():
        pdf.set_fill_color(74, 2, 3)
        pdf.set_text_color(255, 255, 255)
        pdf.set_draw_color(74, 2, 3)
        pdf.set_font('Helvetica', 'B', 8)
        for title, width, align in cols:
            pdf.cell(width, 7, _pdf_safe_text(title), border=1, align=align, fill=True)
        pdf.ln()

    _draw_table_header()

    pdf.set_font('Helvetica', '', 8)
    pdf.set_draw_color(221, 192, 189)

    if not reportes:
        pdf.set_fill_color(250, 247, 247)
        pdf.set_text_color(86, 66, 64)
        pdf.cell(277, 10, _pdf_safe_text('No se encontraron reportes con los filtros aplicados.'), border=1, align='C', fill=True)
        pdf.ln()
    else:
        for idx, rep in enumerate(reportes):
            if pdf.get_y() > 180:
                pdf.add_page()
                _draw_table_header()
                pdf.set_font('Helvetica', '', 8)
                pdf.set_draw_color(221, 192, 189)

            fill = (idx % 2 == 1)
            pdf.set_fill_color(250, 247, 247) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(43, 17, 17)

            reg = _to_int(rep.get('nro_regulares'))
            ninos = _to_int(rep.get('nro_niños', rep.get('nro_ninos', 0)))
            vis = _to_int(rep.get('nro_visitas'))
            comp = _to_int(rep.get('nro_comprometidos'))
            asis = _compute_asistencia(rep)
            usd = _to_float(rep.get('ofrendas_usd'))
            bs = _to_float(rep.get('ofrendas_bs'))

            cdp_label = rep.get('cdp_codigo') or rep.get('cdp_nombre') or f"CDP #{rep.get('cdp_id', '')}"
            if rep.get('cdp_codigo') and rep.get('cdp_nombre') and rep['cdp_codigo'] not in str(rep['cdp_nombre']):
                cdp_label = f"{rep['cdp_codigo']} - {rep['cdp_nombre']}"

            row_vals = [
                (_format_fecha(rep.get('fecha') or rep.get('fecha_formateada')), 10),
                (rep.get('red_nombre') or '-', 18),
                (cdp_label, 24),
                (rep.get('lider_nombre') or 'Sin asignar', 24),
                (rep.get('tema') or '-', 34),
                (str(reg), 6),
                (str(ninos), 6),
                (str(vis), 6),
                (str(comp), 6),
                (str(asis), 6),
                (f'${usd:,.2f}', 12),
                (f'{bs:,.2f}', 14),
            ]
            for (val, max_c), (_, width, align) in zip(row_vals, cols):
                pdf.cell(width, 6.5, _pdf_safe_text(val, max_len=max_c), border=1, align=align, fill=fill)
            pdf.ln()

        # Fila de totales consolidados
        if pdf.get_y() > 180:
            pdf.add_page()
            _draw_table_header()
        pdf.set_fill_color(248, 228, 227)
        pdf.set_text_color(57, 0, 2)
        pdf.set_draw_color(74, 2, 3)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(22 + 28 + 38 + 38 + 51, 7.5, _pdf_safe_text(f'TOTALES CONSOLIDADOS ({total_reportes} reportes)'), border=1, align='L', fill=True)
        pdf.cell(12, 7.5, str(total_reg), border=1, align='C', fill=True)
        pdf.cell(12, 7.5, str(total_ninos), border=1, align='C', fill=True)
        pdf.cell(12, 7.5, str(total_vis), border=1, align='C', fill=True)
        pdf.cell(12, 7.5, str(total_comp), border=1, align='C', fill=True)
        pdf.cell(14, 7.5, str(total_asis), border=1, align='C', fill=True)
        pdf.cell(18, 7.5, f'${total_usd:,.2f}', border=1, align='R', fill=True)
        pdf.cell(20, 7.5, f'{total_bs:,.2f}', border=1, align='R', fill=True)
        pdf.ln()

    return bytes(pdf.output())


def build_reportes_xlsx(reportes: list[dict]) -> bytes:
    """Genera libro Excel (.xlsx) consolidado de reportes con desglose y totales."""
    headers = [
        'Fecha',
        'Red',
        'Casa de Paz',
        'Líder',
        'Tema',
        'Regulares',
        'Niños',
        'Visitas',
        'Comprometidos',
        'Asistencia Total',
        'Reconciliaciones',
        'Confesiones',
        'Cesta de Amor',
        'Ofrendas ($ USD)',
        'Ofrendas (Bs)',
        'Observaciones',
    ]
    rows = []
    tot_reg = tot_ninos = tot_vis = tot_comp = tot_asis = tot_rec = tot_conf = 0
    tot_usd = 0.0
    tot_bs = 0.0

    for rep in reportes:
        reg = _to_int(rep.get('nro_regulares'))
        ninos = _to_int(rep.get('nro_niños', rep.get('nro_ninos', 0)))
        vis = _to_int(rep.get('nro_visitas'))
        comp = _to_int(rep.get('nro_comprometidos'))
        asis = _compute_asistencia(rep)
        rec = _to_int(rep.get('reconciliaciones'))
        conf = _to_int(rep.get('confesiones'))
        usd = _to_float(rep.get('ofrendas_usd'))
        bs = _to_float(rep.get('ofrendas_bs'))

        tot_reg += reg
        tot_ninos += ninos
        tot_vis += vis
        tot_comp += comp
        tot_asis += asis
        tot_rec += rec
        tot_conf += conf
        tot_usd = round(tot_usd + usd, 2)
        tot_bs = round(tot_bs + bs, 2)

        cdp_label = rep.get('cdp_codigo') or rep.get('cdp_nombre') or f"CDP #{rep.get('cdp_id', '')}"
        rows.append([
            _format_fecha(rep.get('fecha') or rep.get('fecha_formateada')),
            rep.get('red_nombre') or '',
            cdp_label,
            rep.get('lider_nombre') or '',
            rep.get('tema') or '',
            reg,
            ninos,
            vis,
            comp,
            asis,
            rec,
            conf,
            'Sí' if rep.get('cesta_amor') else 'No',
            usd,
            bs,
            rep.get('observaciones') or '',
        ])

    summary_row = [
        f'TOTALES ({len(reportes)} reportes)',
        '',
        '',
        '',
        '',
        tot_reg,
        tot_ninos,
        tot_vis,
        tot_comp,
        tot_asis,
        tot_rec,
        tot_conf,
        '',
        tot_usd,
        tot_bs,
        '',
    ]

    return build_xlsx(
        'Reportes Consolidados',
        headers,
        rows,
        summary_row=summary_row,
        int_columns={5, 6, 7, 8, 9, 10, 11},
        currency_usd_columns={13},
        currency_bs_columns={14},
    )


def build_reportes_csv(reportes: list[dict]) -> bytes:
    """Genera CSV UTF-8 con BOM de reportes consolidados."""
    headers = [
        'Fecha',
        'Red',
        'Casa de Paz',
        'Líder',
        'Tema',
        'Regulares',
        'Niños',
        'Visitas',
        'Comprometidos',
        'Asistencia Total',
        'Reconciliaciones',
        'Confesiones',
        'Cesta de Amor',
        'Ofrendas ($ USD)',
        'Ofrendas (Bs)',
        'Observaciones',
    ]
    rows = []
    tot_reg = tot_ninos = tot_vis = tot_comp = tot_asis = tot_rec = tot_conf = 0
    tot_usd = 0.0
    tot_bs = 0.0

    for rep in reportes:
        reg = _to_int(rep.get('nro_regulares'))
        ninos = _to_int(rep.get('nro_niños', rep.get('nro_ninos', 0)))
        vis = _to_int(rep.get('nro_visitas'))
        comp = _to_int(rep.get('nro_comprometidos'))
        asis = _compute_asistencia(rep)
        rec = _to_int(rep.get('reconciliaciones'))
        conf = _to_int(rep.get('confesiones'))
        usd = _to_float(rep.get('ofrendas_usd'))
        bs = _to_float(rep.get('ofrendas_bs'))

        tot_reg += reg
        tot_ninos += ninos
        tot_vis += vis
        tot_comp += comp
        tot_asis += asis
        tot_rec += rec
        tot_conf += conf
        tot_usd = round(tot_usd + usd, 2)
        tot_bs = round(tot_bs + bs, 2)

        cdp_label = rep.get('cdp_codigo') or rep.get('cdp_nombre') or f"CDP #{rep.get('cdp_id', '')}"
        rows.append([
            _format_fecha(rep.get('fecha') or rep.get('fecha_formateada')),
            rep.get('red_nombre') or '',
            cdp_label,
            rep.get('lider_nombre') or '',
            rep.get('tema') or '',
            reg,
            ninos,
            vis,
            comp,
            asis,
            rec,
            conf,
            'Sí' if rep.get('cesta_amor') else 'No',
            f'{usd:.2f}',
            f'{bs:.2f}',
            rep.get('observaciones') or '',
        ])

    rows.append([
        f'TOTALES ({len(reportes)} reportes)',
        '',
        '',
        '',
        '',
        tot_reg,
        tot_ninos,
        tot_vis,
        tot_comp,
        tot_asis,
        tot_rec,
        tot_conf,
        '',
        f'{tot_usd:.2f}',
        f'{tot_bs:.2f}',
        '',
    ])
    return build_csv(headers, rows)


def _usuarios_rows(usuarios: list[dict]) -> tuple[list[str], list[list[Any]]]:
    headers = ['Nombre', 'Apellido', 'Username', 'Rol', 'Estado', 'Red Asignada', 'Casa de Paz']
    rows = []
    for u in usuarios:
        rol_raw = u.get('tipo_usuario') or u.get('rol') or ''
        rows.append([
            u.get('nombre') or '',
            u.get('apellido') or '',
            u.get('username') or '',
            rol_raw,
            'Activo' if u.get('is_active', 1) else 'Inactivo',
            u.get('red_nombre') or '',
            u.get('cdp_codigo') or '',
        ])
    return headers, rows


def build_usuarios_xlsx(usuarios: list[dict]) -> bytes:
    headers, rows = _usuarios_rows(usuarios)
    return build_xlsx('Directorio Usuarios', headers, rows)


def build_usuarios_csv(usuarios: list[dict]) -> bytes:
    headers, rows = _usuarios_rows(usuarios)
    return build_csv(headers, rows)


def _lideres_rows(lideres: list[dict]) -> tuple[list[str], list[list[Any]]]:
    headers = ['Nombre', 'Apellido', 'Rol', 'Red', 'Casa de Paz', 'Teléfono', 'Estado']
    rows = []
    for l in lideres:
        rows.append([
            l.get('nombre') or '',
            l.get('apellido') or '',
            l.get('rol') or '',
            l.get('red_nombre') or '',
            l.get('cdp_codigo') or l.get('cdp_nombre') or '',
            l.get('telefono') or '',
            'Activo' if l.get('is_active', 1) else 'Inactivo',
        ])
    return headers, rows


def build_lideres_xlsx(lideres: list[dict]) -> bytes:
    headers, rows = _lideres_rows(lideres)
    return build_xlsx('Directorio Lideres', headers, rows, phone_columns={5})


def build_lideres_csv(lideres: list[dict]) -> bytes:
    headers, rows = _lideres_rows(lideres)
    return build_csv(headers, rows, phone_columns={5})


def _casas_rows(casas: list[dict]) -> tuple[list[str], list[list[Any]]]:
    headers = ['Código', 'Red', 'Anfitrión', 'Líder Principal', 'Teléfono', 'Dirección', 'Estado', 'Cumplimiento 7d']
    rows = []
    for c in casas:
        is_active = bool(c.get('is_active', 1))
        sin_rep = bool(c.get('sin_reporte_7d', False))
        cumplimiento = 'Pausada' if not is_active else ('Pendiente (>7d)' if sin_rep else 'Al día')
        rows.append([
            c.get('codigo') or '',
            c.get('red_nombre') or '',
            c.get('anfitrion') or '',
            c.get('lider_nombre') or c.get('lider') or '',
            c.get('telefono') or '',
            c.get('direccion') or '',
            'Activa' if is_active else 'Pausada',
            cumplimiento,
        ])
    return headers, rows


def build_casas_xlsx(casas: list[dict]) -> bytes:
    headers, rows = _casas_rows(casas)
    return build_xlsx('Casas de Paz', headers, rows, phone_columns={4})


def build_casas_csv(casas: list[dict]) -> bytes:
    headers, rows = _casas_rows(casas)
    return build_csv(headers, rows, phone_columns={4})


def export_reportes(reportes: list[dict], fmt: str, *, filters_summary: str = '') -> tuple[bytes, str, str]:
    today = date.today().strftime('%Y-%m-%d')
    fmt_clean = (fmt or '').strip().lower()
    if fmt_clean == 'pdf':
        return build_reportes_pdf(reportes, filters_summary=filters_summary), MIME_PDF, f'reportes_consolidado_{today}.pdf'
    if fmt_clean == 'xlsx':
        return build_reportes_xlsx(reportes), MIME_XLSX, f'reportes_consolidado_{today}.xlsx'
    if fmt_clean == 'csv':
        return build_reportes_csv(reportes), MIME_CSV, f'reportes_consolidado_{today}.csv'
    raise ValueError("Formato no soportado. Use 'pdf', 'xlsx' o 'csv'.")


def export_usuarios(usuarios: list[dict], fmt: str) -> tuple[bytes, str, str]:
    today = date.today().strftime('%Y-%m-%d')
    fmt_clean = (fmt or '').strip().lower()
    if fmt_clean == 'xlsx':
        return build_usuarios_xlsx(usuarios), MIME_XLSX, f'directorio_usuarios_{today}.xlsx'
    if fmt_clean == 'csv':
        return build_usuarios_csv(usuarios), MIME_CSV, f'directorio_usuarios_{today}.csv'
    raise ValueError("Formato no soportado para usuarios. Use 'xlsx' o 'csv'.")


def export_lideres(lideres: list[dict], fmt: str) -> tuple[bytes, str, str]:
    today = date.today().strftime('%Y-%m-%d')
    fmt_clean = (fmt or '').strip().lower()
    if fmt_clean == 'xlsx':
        return build_lideres_xlsx(lideres), MIME_XLSX, f'directorio_lideres_{today}.xlsx'
    if fmt_clean == 'csv':
        return build_lideres_csv(lideres), MIME_CSV, f'directorio_lideres_{today}.csv'
    raise ValueError("Formato no soportado para líderes. Use 'xlsx' o 'csv'.")


def export_casas(casas: list[dict], fmt: str) -> tuple[bytes, str, str]:
    today = date.today().strftime('%Y-%m-%d')
    fmt_clean = (fmt or '').strip().lower()
    if fmt_clean == 'xlsx':
        return build_casas_xlsx(casas), MIME_XLSX, f'directorio_casas_de_paz_{today}.xlsx'
    if fmt_clean == 'csv':
        return build_casas_csv(casas), MIME_CSV, f'directorio_casas_de_paz_{today}.csv'
    raise ValueError("Formato no soportado para Casas de Paz. Use 'xlsx' o 'csv'.")
