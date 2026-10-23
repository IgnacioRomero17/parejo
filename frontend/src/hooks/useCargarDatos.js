import { useCallback, useEffect, useState } from "react";

const CARGANDO = { cargando: true, error: null, datos: null };

// Carga datos al entrar a una página. `cargar` debe ser estable (definida fuera del
// componente): si cambia, se vuelve a pedir. Devuelve cargando, error, datos y reintentar.
export function useCargarDatos(cargar) {
  const [estado, setEstado] = useState(CARGANDO);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    let vigente = true;
    cargar().then(
      (datos) => {
        if (vigente) setEstado({ cargando: false, error: null, datos });
      },
      (error) => {
        if (vigente) setEstado({ cargando: false, error, datos: null });
      },
    );
    return () => {
      vigente = false;
    };
  }, [cargar, intento]);

  const reintentar = useCallback(() => {
    setEstado(CARGANDO);
    setIntento((anterior) => anterior + 1);
  }, []);

  return { ...estado, reintentar };
}
