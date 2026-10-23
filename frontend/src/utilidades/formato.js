const FORMATO_NIVEL = new Intl.NumberFormat("es-AR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

// Niveles con coma decimal y siempre un decimal: "4,5", "4,0".
export function formatearNivel(nivel) {
  return FORMATO_NIVEL.format(nivel);
}
