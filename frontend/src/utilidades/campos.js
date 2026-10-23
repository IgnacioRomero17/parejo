// id del mensaje que describe un control (ver MensajeCampo): el error o, si no hay, la ayuda.
export function idDescripcion(id, error, ayuda) {
  if (error) return `${id}-error`;
  if (ayuda) return `${id}-ayuda`;
  return undefined;
}
