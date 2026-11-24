import { FieldTree } from '@angular/forms/signals';

/**
 * Marca como tocados el campo raíz y los campos con errores para que
 * Bootstrap muestre los mensajes de validación al intentar enviar.
 */
export function marcarTocados(formulario: FieldTree<unknown>): void {
  formulario().markAsTouched();
  for (const error of formulario().errorSummary()) {
    error.fieldTree().markAsTouched();
  }
}
