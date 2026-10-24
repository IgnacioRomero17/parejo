const FORMATO_NIVEL = new Intl.NumberFormat("es-AR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const FORMATO_FECHA_COMPACTA = new Intl.DateTimeFormat("es-AR", {
  timeZone: "America/Argentina/Cordoba",
  weekday: "short",
  day: "numeric",
  month: "short",
  year: "numeric",
});

// Niveles con coma decimal y siempre un decimal: "4,5", "4,0".
export function formatearNivel(nivel) {
  return FORMATO_NIVEL.format(nivel);
}

function sinPunto(texto) {
  return texto.replace(".", "");
}

// Fecha "AAAA-MM-DD" de la API como en encabezados y listas: "Sáb 3 oct 2026".
export function formatearFechaCompacta(fecha) {
  // Al mediodía de Córdoba: la medianoche UTC todavía es el día anterior en Córdoba.
  const instante = new Date(`${fecha}T12:00:00-03:00`);
  const partes = Object.fromEntries(
    FORMATO_FECHA_COMPACTA.formatToParts(instante).map((parte) => [
      parte.type,
      parte.value,
    ]),
  );
  const dia = sinPunto(partes.weekday);
  return `${dia.charAt(0).toUpperCase()}${dia.slice(1)} ${partes.day} ${sinPunto(partes.month)} ${partes.year}`;
}
