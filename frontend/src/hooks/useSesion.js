import { useContext } from "react";
import { ContextoSesion } from "../contexto/contextoSesion.js";

export function useSesion() {
  return useContext(ContextoSesion);
}
