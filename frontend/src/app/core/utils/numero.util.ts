export function aNumero(
  valor: number | string | null | undefined,
): number | null {
  if (valor === null || valor === undefined || valor === '') {
    return null;
  }
  const numero = typeof valor === 'number' ? valor : Number(valor);
  return Number.isFinite(numero) ? numero : null;
}

export function formatearPeso(valor: number | string | null | undefined): string {
  const numero = aNumero(valor);
  if (numero === null) {
    return '—';
  }
  return `${numero.toLocaleString('es-PE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} kg`;
}

export function formatearNumero(valor: number | string | null | undefined): string {
  const numero = aNumero(valor);
  return numero === null ? '—' : numero.toLocaleString('es-PE');
}

export function porcentaje(parte: number, total: number): number {
  if (!total) {
    return 0;
  }
  return Math.min(100, Math.max(0, (parte / total) * 100));
}
