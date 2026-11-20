/**
 * Utilidades puras de normalización telefónica E.164 y construcción de enlaces
 * directos WhatsApp (wa.me) y llamadas (tel:). Espejo exacto de backend/utils/validators.py.
 */

const ALLOWED_RAW_RE = /^\+?[0-9\s\-().]{7,25}$/;

export interface PhoneNormalizationResult {
  valid: boolean;
  e164: string;
  error: string;
}

/**
 * Normaliza y valida un teléfono a formato internacional estricto E.164
 * (+<código_país><número>, entre 8 y 14 dígitos, máximo 15 caracteres).
 */
export function normalizePhoneE164(
  phone: string | null | undefined,
  defaultCountryCode = '58'
): PhoneNormalizationResult {
  if (!phone || !phone.trim()) {
    return { valid: true, e164: '', error: '' };
  }

  const cleaned = phone.trim();
  if (!ALLOWED_RAW_RE.test(cleaned)) {
    return {
      valid: false,
      e164: '',
      error: 'Formato de teléfono inválido. Usa formato internacional E.164 (ej: +58 412-1234567 o 0412-1234567).',
    };
  }

  const digits = cleaned.replace(/\D/g, '');
  if (!digits) {
    return {
      valid: false,
      e164: '',
      error: 'El teléfono debe contener dígitos numéricos válidos.',
    };
  }

  let e164Digits = '';
  if (cleaned.startsWith('+')) {
    e164Digits = digits;
  } else if (cleaned.startsWith('00') && digits.length > 2) {
    e164Digits = digits.slice(2);
  } else if (digits.startsWith('0') && digits.length === 11) {
    e164Digits = `${defaultCountryCode}${digits.slice(1)}`;
  } else if (digits.length === 10 && (digits.startsWith('2') || digits.startsWith('4'))) {
    e164Digits = `${defaultCountryCode}${digits}`;
  } else if (digits.startsWith(defaultCountryCode) && digits.length >= 11 && digits.length <= 13) {
    e164Digits = digits;
  } else if (!digits.startsWith('0') && digits.length >= 8 && digits.length <= 14) {
    e164Digits = digits;
  } else {
    return {
      valid: false,
      e164: '',
      error: 'Formato de teléfono inválido. Indica el código de país (ej: +58 412-1234567).',
    };
  }

  if (e164Digits.startsWith('0') || e164Digits.length < 8 || e164Digits.length > 14) {
    return {
      valid: false,
      e164: '',
      error: "El teléfono E.164 debe tener entre 8 y 14 dígitos (máximo 15 caracteres incluyendo '+').",
    };
  }

  return { valid: true, e164: `+${e164Digits}`, error: '' };
}

/**
 * Extrae los dígitos internacionales sin '+' para https://wa.me/<digitos>.
 */
export function formatWhatsappDigits(
  phone: string | null | undefined,
  defaultCountryCode = '58'
): string {
  if (!phone) return '';
  const res = normalizePhoneE164(String(phone), defaultCountryCode);
  if (res.valid && res.e164) {
    return res.e164.slice(1);
  }
  const digits = String(phone).replace(/\D/g, '');
  if (digits.startsWith('0') && digits.length === 11) {
    return `${defaultCountryCode}${digits.slice(1)}`;
  }
  return digits.length >= 8 ? digits : '';
}

/**
 * Construye una URL válida de WhatsApp (https://wa.me/584121234567) o cadena vacía.
 */
export function formatWhatsappUrl(
  phone: string | null | undefined,
  defaultCountryCode = '58'
): string {
  const digits = formatWhatsappDigits(phone, defaultCountryCode);
  return digits ? `https://wa.me/${digits}` : '';
}

/**
 * Construye una URL válida de llamada telefónica (tel:+584121234567) o cadena vacía.
 */
export function formatTelUrl(
  phone: string | null | undefined,
  defaultCountryCode = '58'
): string {
  if (!phone) return '';
  const res = normalizePhoneE164(String(phone), defaultCountryCode);
  if (res.valid && res.e164) {
    return `tel:${res.e164}`;
  }
  const digits = formatWhatsappDigits(phone, defaultCountryCode);
  return digits ? `tel:+${digits}` : '';
}
