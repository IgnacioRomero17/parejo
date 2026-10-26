import { useCallback, useEffect, useState } from "react";

const CARGANDO = { cargando: true, error: null, datos: null };

// Carga datos al entrar a una página. `cargar` debe ser estable (definida fuera del
// componente): si cambia, se vuelve a pedir. Devuelve cargando, error, datos, reintentar (tras
// un error, pasando por "cargando") y recargar (vuelve a pedir dejando los datos a la vista).
export function useCargarDatos(cargar) {
  const [estado, setEstado] = useState(CARGANDO);
  const [intento, setIntento] = useState(0);
  const recargar = useCallback(
    () => setIntento((anterior) => anterior + 1),
    [],
  );

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

  return { ...estado, reintentar, recargar };
}
