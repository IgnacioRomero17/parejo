import { createContext } from "react";

export const ContextoSesion = createContext({
  cargando: true,
  usuario: null,
  establecerUsuario: () => {},
});
