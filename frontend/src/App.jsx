import { BrowserRouter } from "react-router-dom";
import SesionProveedor from "./contexto/SesionContexto.jsx";
import Rutas from "./rutas.jsx";

function App() {
  return (
    <BrowserRouter>
      <SesionProveedor>
        <Rutas />
      </SesionProveedor>
    </BrowserRouter>
  );
}

export default App;
