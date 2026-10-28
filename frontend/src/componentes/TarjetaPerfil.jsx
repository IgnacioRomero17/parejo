import { Link } from "react-router-dom";
import { formatearNivel } from "../utilidades/formato.js";
import Etiqueta from "./Etiqueta.jsx";
import estilos from "./TarjetaPerfil.module.css";

// Tarjeta "Tu perfil" del panel principal. `perfil` es la respuesta de `GET perfil`; la
// localidad llega como id y su nombre se busca en el catálogo.
function TarjetaPerfil({ perfil, localidades }) {
  const { perfil_deportivo: deportivo, disponibilidad } = perfil;
  const localidad = localidades.find(
    (opcion) => opcion.id === deportivo.localidad,
  );
  const datos = [
    {
      rotulo: "Nivel estimado",
      valor: formatearNivel(deportivo.nivel_estimado),
    },
    { rotulo: "Localidad", valor: localidad?.nombre },
    { rotulo: "Franjas cargadas", valor: disponibilidad.franjas.length },
    {
      rotulo: "Recibir invitaciones",
      valor: disponibilidad.disponible_para_invitaciones ? (
        <Etiqueta color="verde">Disponible</Etiqueta>
      ) : (
        <Etiqueta>No disponible</Etiqueta>
      ),
    },
  ];

  return (
    <div className={estilos.tarjeta}>
      <dl className={estilos.datos}>
        {datos.map(({ rotulo, valor }) => (
          <div key={rotulo} className={estilos.fila}>
            <dt className={estilos.rotulo}>{rotulo}</dt>
            <dd className={estilos.valor}>{valor}</dd>
          </div>
        ))}
      </dl>
      <Link to="/perfil" className={estilos.enlace}>
        Editar perfil
      </Link>
    </div>
  );
}

export default TarjetaPerfil;
