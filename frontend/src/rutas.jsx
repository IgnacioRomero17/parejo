import { Route, Routes } from "react-router-dom";
import RutaConOnboarding from "./componentes/RutaConOnboarding.jsx";
import RutaPrivada from "./componentes/RutaPrivada.jsx";
import RutaPublica from "./componentes/RutaPublica.jsx";
import Bienvenida from "./paginas/Bienvenida.jsx";
import CrearEncuentro from "./paginas/CrearEncuentro.jsx";
import Ingreso from "./paginas/Ingreso.jsx";
import JugadoresRecomendados from "./paginas/JugadoresRecomendados.jsx";
import OnboardingDisponibilidad from "./paginas/OnboardingDisponibilidad.jsx";
import OnboardingPerfil from "./paginas/OnboardingPerfil.jsx";
import PanelPrincipal from "./paginas/PanelPrincipal.jsx";
import Perfil from "./paginas/Perfil.jsx";
import RecuperacionCorreo from "./paginas/RecuperacionCorreo.jsx";
import RecuperacionEnviado from "./paginas/RecuperacionEnviado.jsx";
import RecuperacionNueva from "./paginas/RecuperacionNueva.jsx";
import Registro from "./paginas/Registro.jsx";

// Las rutas de las demás pantallas se agregan con su HU (ver docs/interfaces/README.md).
// Las pantallas internas van dentro de RutaPrivada; las que piden el onboarding completo,
// además, dentro de RutaConOnboarding.
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
      <Route element={<RutaPrivada />}>
        <Route path="/onboarding/perfil" element={<OnboardingPerfil />} />
        <Route element={<RutaConOnboarding permitirPaso="disponibilidad" />}>
          <Route
            path="/onboarding/disponibilidad"
            element={<OnboardingDisponibilidad />}
          />
        </Route>
        <Route element={<RutaConOnboarding />}>
          <Route path="/inicio" element={<PanelPrincipal />} />
          <Route path="/encuentros/nuevo" element={<CrearEncuentro />} />
          <Route
            path="/encuentros/:id/recomendados"
            element={<JugadoresRecomendados />}
          />
          <Route path="/perfil" element={<Perfil />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default Rutas;
