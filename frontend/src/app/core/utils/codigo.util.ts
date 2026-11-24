export function normalizarCodigo(codigo: string): string {
  return codigo.trim().toUpperCase();
}

export function esCodigoValido(codigo: string): boolean {
  return /^RAEE-\d{4}-\d{4}$/.test(normalizarCodigo(codigo));
}
