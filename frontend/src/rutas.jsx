import { Route, Routes } from "react-router-dom";
import RutaPublica from "./componentes/RutaPublica.jsx";
import Bienvenida from "./paginas/Bienvenida.jsx";
import Registro from "./paginas/Registro.jsx";

// Las rutas de las demás pantallas se agregan con su HU (ver docs/interfaces/README.md).
function Rutas() {
  return (
    <Routes>
      <Route element={<RutaPublica />}>
        <Route path="/" element={<Bienvenida />} />
        <Route path="/registro" element={<Registro />} />
      </Route>
    </Routes>
  );
}

export default Rutas;
