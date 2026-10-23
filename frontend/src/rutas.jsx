import { Route, Routes } from "react-router-dom";
import RutaPublica from "./componentes/RutaPublica.jsx";
import Bienvenida from "./paginas/Bienvenida.jsx";
import Ingreso from "./paginas/Ingreso.jsx";
import RecuperacionCorreo from "./paginas/RecuperacionCorreo.jsx";
import RecuperacionEnviado from "./paginas/RecuperacionEnviado.jsx";
import RecuperacionNueva from "./paginas/RecuperacionNueva.jsx";
import Registro from "./paginas/Registro.jsx";

// Las rutas de las demás pantallas se agregan con su HU (ver docs/interfaces/README.md).
// Las pantallas internas van dentro de RutaPrivada.
function Rutas() {
  return (
    <Routes>
      <Route element={<RutaPublica />}>
        <Route path="/" element={<Bienvenida />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/ingresar" element={<Ingreso />} />
      </Route>
      {/* Sin protección: la recuperación se usa con o sin sesión. */}
      <Route path="/recuperar" element={<RecuperacionCorreo />} />
      <Route path="/recuperar/enviado" element={<RecuperacionEnviado />} />
      <Route path="/recuperar/:uid/:token" element={<RecuperacionNueva />} />
    </Routes>
  );
}

export default Rutas;
