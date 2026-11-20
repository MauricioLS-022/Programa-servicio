import { describe, it, expect } from 'vitest';
import {
  normalizePhoneE164,
  formatWhatsappDigits,
  formatWhatsappUrl,
  formatTelUrl,
} from '../phone';

describe('phone E.164 & WhatsApp utilities', () => {
  it('normaliza formatos locales venezolanos a E.164 (+58...)', () => {
    expect(normalizePhoneE164('0414-1234567')).toEqual({
      valid: true,
      e164: '+584141234567',
      error: '',
    });
    expect(normalizePhoneE164('0412 123 4567')).toEqual({
      valid: true,
      e164: '+584121234567',
      error: '',
    });
    expect(normalizePhoneE164('4141234567')).toEqual({
      valid: true,
      e164: '+584141234567',
      error: '',
    });
  });

  it('preserva números internacionales explícitos válidos y respeta límite 15 chars', () => {
    const co = normalizePhoneE164('+57 300-1234567');
    expect(co.valid).toBe(true);
    expect(co.e164).toBe('+573001234567');
    expect(co.e164.length).toBeLessThanOrEqual(15);

    const us = normalizePhoneE164('+1 (305) 555-0199');
    expect(us.valid).toBe(true);
    expect(us.e164).toBe('+13055550199');
  });

  it('rechaza números cortos, con letras o que superan 15 caracteres', () => {
    expect(normalizePhoneE164('12345').valid).toBe(false);
    expect(normalizePhoneE164('abc-1234567').valid).toBe(false);
    expect(normalizePhoneE164('+1234567890123456').valid).toBe(false);
  });

  it('construye enlaces wa.me y tel: válidos para registros normalizados e históricos', () => {
    expect(formatWhatsappDigits('0414-1234567')).toBe('584141234567');
    expect(formatWhatsappUrl('0414-1234567')).toBe('https://wa.me/584141234567');
    expect(formatWhatsappUrl('+58 412-1234567')).toBe('https://wa.me/584121234567');
    expect(formatTelUrl('0414-1234567')).toBe('tel:+584141234567');
    expect(formatTelUrl('+57 300-1234567')).toBe('tel:+573001234567');
    expect(formatWhatsappUrl('')).toBe('');
    expect(formatTelUrl(null)).toBe('');
  });
});
