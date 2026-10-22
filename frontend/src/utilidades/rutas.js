export function rutaOnboarding(paso) {
  return `/onboarding/${paso}`;
}

// Adónde va un usuario con sesión: al paso de onboarding pendiente o al panel principal.
export function rutaInicial(usuario) {
  return usuario.onboarding ? rutaOnboarding(usuario.onboarding) : "/inicio";
}
