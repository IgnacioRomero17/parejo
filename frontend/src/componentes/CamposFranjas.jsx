import { Plus } from "lucide-react";
import {
  DIAS_SEMANA,
  franjaVacia,
  HORAS_FRANJA,
} from "../utilidades/disponibilidad.js";
import Boton from "./Boton.jsx";
import estilos from "./CamposFranjas.module.css";
import Desplegable from "./Desplegable.jsx";

// Filas de franjas horarias (pantallas 07b y 17). `errores` va por clave de fila;
// `onCambiar(franjas)` recibe la lista completa después de cada cambio.
function CamposFranjas({ franjas, errores, onCambiar }) {
  function cambiarFila(clave, campo, valor) {
    onCambiar(
      franjas.map((franja) =>
        franja.clave === clave ? { ...franja, [campo]: valor } : franja,
      ),
    );
  }

  function quitarFila(clave) {
    onCambiar(franjas.filter((franja) => franja.clave !== clave));
  }

  return (
    <div className={estilos.franjas}>
      {franjas.length > 0 && (
        <ul className={estilos.lista}>
          {franjas.map((franja, posicion) => {
            const errorDe = (campo) =>
              errores?.[franja.clave]?.[campo]?.join(" ");
            // Los rótulos se ven solo en la primera fila, como encabezado de columnas.
            const primera = posicion === 0;
            const campo = (nombre, etiqueta, opciones) => (
              <Desplegable
                id={`${franja.clave}-${nombre}`}
                etiqueta={etiqueta}
                etiquetaOculta={!primera}
                valor={franja[nombre]}
                opciones={opciones}
                onCambiar={(valor) => cambiarFila(franja.clave, nombre, valor)}
                error={errorDe(nombre)}
                requerido
              />
            );
            return (
              <li
                key={franja.clave}
                className={
                  primera
                    ? `${estilos.fila} ${estilos.conRotulos}`
                    : estilos.fila
                }
              >
                {campo("dia_semana", "Día", DIAS_SEMANA)}
                {campo("hora_inicio", "Desde", HORAS_FRANJA)}
                <span className={estilos.separador} aria-hidden="true">
                  a
                </span>
                {campo("hora_fin", "Hasta", HORAS_FRANJA)}
                <button
                  type="button"
                  className={estilos.quitar}
                  onClick={() => quitarFila(franja.clave)}
                  aria-label={`Quitar franja ${posicion + 1}`}
                >
                  Quitar
                </button>
              </li>
            );
          })}
        </ul>
      )}
      <div>
        <Boton
          variante="secundario"
          icono={Plus}
          onClick={() => onCambiar([...franjas, franjaVacia()])}
        >
          Agregar franja
        </Boton>
      </div>
    </div>
  );
}

export default CamposFranjas;
