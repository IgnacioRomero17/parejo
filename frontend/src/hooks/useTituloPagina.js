import { useEffect } from "react";

export function useTituloPagina(nombre) {
  useEffect(() => {
    document.title = `${nombre} · parejo`;
  }, [nombre]);
}
