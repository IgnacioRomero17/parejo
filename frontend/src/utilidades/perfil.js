export const GENEROS = [
  { valor: "MASCULINO", etiqueta: "Masculino" },
  { valor: "FEMENINO", etiqueta: "Femenino" },
  { valor: "NO_DECLARA", etiqueta: "Prefiero no decirlo" },
];

export const FRECUENCIAS_JUEGO = [
  { valor: "MENOS_1_SEMANA", etiqueta: "Menos de 1 vez por semana" },
  { valor: "1_SEMANA", etiqueta: "1 vez por semana" },
  { valor: "2_3_SEMANA", etiqueta: "2 o 3 veces por semana" },
  { valor: "4_MAS_SEMANA", etiqueta: "4 o más veces por semana" },
];

function textoDe(valor) {
  return valor === null || valor === undefined ? "" : String(valor);
}

// Pasa el perfil deportivo de la API a los valores del formulario: los controles nativos
// trabajan con texto y "" es "sin elegir"; el nivel queda como número o null.
export function formularioPerfilDeportivo(perfilDeportivo) {
  return {
    edad: textoDe(perfilDeportivo.edad),
    genero: textoDe(perfilDeportivo.genero),
    localidad: textoDe(perfilDeportivo.localidad),
    frecuencia_juego: textoDe(perfilDeportivo.frecuencia_juego),
    nivel_estimado: perfilDeportivo.nivel_estimado,
  };
}

function numeroONull(texto) {
  return texto.trim() === "" ? null : Number(texto);
}

// Inversa de formularioPerfilDeportivo, con el formato que espera `PATCH perfil`.
export function perfilDeportivoDeFormulario(valores) {
  return {
    edad: numeroONull(valores.edad),
    genero: valores.genero || null,
    localidad: numeroONull(valores.localidad),
    frecuencia_juego: valores.frecuencia_juego || null,
    nivel_estimado: valores.nivel_estimado,
  };
}

// Secciones editables de la pantalla 17 (la HU-005 suma "disponibilidad").
export const SECCIONES_PERFIL = ["datos_personales", "perfil_deportivo"];

// Valores del formulario de la pantalla 17 a partir de la respuesta de `GET perfil`.
export function formularioPerfil(perfil) {
  return {
    datos_personales: {
      nombre: perfil.datos_personales.nombre,
      apellido: perfil.datos_personales.apellido,
    },
    perfil_deportivo: formularioPerfilDeportivo(perfil.perfil_deportivo),
  };
}

export function seccionesModificadas(valores, guardados) {
  return SECCIONES_PERFIL.filter(
    (seccion) =>
      JSON.stringify(valores[seccion]) !== JSON.stringify(guardados[seccion]),
  );
}

// Cuerpo de `PATCH perfil` con solo las secciones indicadas.
export function cuerpoActualizacion(valores, secciones) {
  const cuerpo = {};
  if (secciones.includes("datos_personales")) {
    cuerpo.datos_personales = valores.datos_personales;
  }
  if (secciones.includes("perfil_deportivo")) {
    cuerpo.perfil_deportivo = perfilDeportivoDeFormulario(
      valores.perfil_deportivo,
    );
  }
  return cuerpo;
}

export function textoCamposPendientes(cantidad) {
  return cantidad === 1 ? "1 campo pendiente" : `${cantidad} campos pendientes`;
}
