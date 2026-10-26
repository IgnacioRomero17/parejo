from decimal import ROUND_HALF_UP, Decimal

CUATRO_DECIMALES = Decimal("0.0001")


def redondear4(valor: float) -> Decimal:
    """Redondea un puntaje a 4 decimales, con la mitad hacia arriba.

    Usa `repr` para partir del float tal como se escribe (0.55 y no 0.55000000000000004…),
    así un puntaje igual al umbral no queda por debajo por un error de representación.
    """
    return Decimal(repr(valor)).quantize(CUATRO_DECIMALES, rounding=ROUND_HALF_UP)
