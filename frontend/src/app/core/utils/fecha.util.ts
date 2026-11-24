const FORMATO_FECHA_HORA = new Intl.DateTimeFormat('es-PE', {
  dateStyle: 'medium',
  timeStyle: 'short',
  timeZone: 'America/Lima',
});

const FORMATO_FECHA = new Intl.DateTimeFormat('es-PE', {
  dateStyle: 'long',
  timeZone: 'America/Lima',
});

function fechaValida(valor: string | null | undefined): Date | null {
  if (!valor) {
    return null;
  }
  const fecha = new Date(valor);
  return Number.isNaN(fecha.getTime()) ? null : fecha;
}

export function formatearFechaHora(valor: string | null | undefined): string {
  const fecha = fechaValida(valor);
  return fecha ? FORMATO_FECHA_HORA.format(fecha) : '—';
}

export function formatearFecha(valor: string | null | undefined): string {
  const fecha = fechaValida(valor);
  return fecha ? FORMATO_FECHA.format(fecha) : '—';
}

export function aISO(fechaLocal: string): string | null {
  const fecha = fechaValida(fechaLocal);
  return fecha ? fecha.toISOString() : null;
}

export function fechaMinimaInput(): string {
  const fecha = new Date(Date.now() + 60 * 60 * 1000);
  const pad = (numero: number) => String(numero).padStart(2, '0');
  return [
    `${fecha.getFullYear()}-${pad(fecha.getMonth() + 1)}-${pad(fecha.getDate())}`,
    `${pad(fecha.getHours())}:${pad(fecha.getMinutes())}`,
  ].join('T');
}

export function esFechaFutura(valor: string): boolean {
  const fecha = fechaValida(valor);
  return fecha !== null && fecha.getTime() > Date.now();
}
