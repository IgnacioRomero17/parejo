from dataclasses import dataclass

TOLERANCIA_PESOS = 1e-9


@dataclass(frozen=True)
class Parametros:
    """Pesos, umbrales y distancias del motor: el único lugar con números.

    Valores iniciales, provisionales hasta calibrarlos con el dataset sintético. La evaluación
    puede crear otra instancia para probar valores distintos sin tocar el código.
    """

    dif_max_nivel: float = 1.0
    dist_max_km: float = 40.0
    umbral_minimo: float = 0.55
    peso_nivel: float = 0.60
    peso_geo: float = 0.30
    peso_tipo: float = 0.10
    valor_tipo_opuesto: float = 0.0
    d_max_equilibrio: float = 2.0
    peso_equilibrio_nivel: float = 0.80
    peso_equilibrio_lado: float = 0.20
    lugares_por_encuentro: int = 4
    radio_tierra_km: float = 6371.0

    def __post_init__(self) -> None:
        pesos_etapa1 = self.peso_nivel + self.peso_geo + self.peso_tipo
        if abs(pesos_etapa1 - 1) > TOLERANCIA_PESOS:
            raise ValueError("Los pesos de la etapa 1 deben sumar 1.")
        pesos_etapa2 = self.peso_equilibrio_nivel + self.peso_equilibrio_lado
        if abs(pesos_etapa2 - 1) > TOLERANCIA_PESOS:
            raise ValueError("Los pesos de la etapa 2 deben sumar 1.")
        maximos = {
            "dif_max_nivel": self.dif_max_nivel,
            "dist_max_km": self.dist_max_km,
            "d_max_equilibrio": self.d_max_equilibrio,
            "lugares_por_encuentro": self.lugares_por_encuentro,
            "radio_tierra_km": self.radio_tierra_km,
        }
        for nombre, valor in maximos.items():
            if valor <= 0:
                raise ValueError(f"{nombre} debe ser positivo.")


PARAMETROS = Parametros()
