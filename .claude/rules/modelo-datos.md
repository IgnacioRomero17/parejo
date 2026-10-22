---
paths:
  - "backend/apps/**/models.py"
  - "backend/apps/**/models/**"
  - "backend/apps/**/migrations/**"
  - "backend/apps/**/fixtures/**"
  - "backend/apps/**/admin.py"
---

# Modelo de datos (Django)

## Fuente de verdad
- Qué significa cada dato: `docs/modelo-clases.md` (leer solo la clase que se está tocando).
- Tipos, claves y restricciones exactas: la tabla correspondiente en `docs/esquema.sql`.
- Las migraciones deben producir un esquema equivalente al SQL. **No agregar ni quitar tablas, columnas ni relaciones** sin consultar al autor.

## Convenciones
- `class Meta: db_table = "<nombre del DER>"` en todos los modelos.
- Clave primaria con el nombre del DER: `id_usuario = models.AutoField(primary_key=True)`.
- `db_column` cuando el campo de Django se llama distinto que la columna (`password` → `password_hash`, `is_active` → `activo`) y en las claves foráneas (`organizador` → `id_organizador`).
- Enumeraciones con `models.TextChoices` o `IntegerChoices` (día de la semana), con los códigos y etiquetas de `modelo-clases.md`.
- Todo `CHECK` y `UNIQUE` del SQL se declara en `Meta.constraints` con `CheckConstraint` / `UniqueConstraint` y un nombre explícito (el mismo del SQL cuando lo tiene).
- `on_delete`: `CASCADE` donde el SQL dice `ON DELETE CASCADE`; `PROTECT` donde dice `RESTRICT`. Django aplica ese comportamiento desde la aplicación, así que las claves foráneas generadas no llevan `ON DELETE` en la base: es una diferencia aceptada con el SQL.
- Fechas y horas: `DateTimeField` con `USE_TZ = True`; `default=timezone.now` o `auto_now_add` según el SQL.
- `NUMERIC` → `DecimalField` con los mismos dígitos y decimales.
- `related_name` en español y en plural: `usuario.disponibilidades`, `encuentro.participantes`, `encuentro.invitaciones`, `encuentro.combinaciones`.

## Usuario personalizado
- `AUTH_USER_MODEL = "usuarios.Usuario"`, definido **antes** de la primera migración.
- Hereda de `AbstractBaseUser` y `PermissionsMixin`; `USERNAME_FIELD = "email"`; `REQUIRED_FIELDS = ["nombre", "apellido"]`.
- El manager normaliza el correo a minúsculas en `create_user` y `create_superuser`.
- Se aceptan las columnas técnicas de Django (`last_login`, `is_staff`, `is_superuser` y tablas de permisos).
- `perfil_completo` es una propiedad: nivel y localidad no nulos.

## Clave compuesta
`ParejaIntegrante` usa `pk = models.CompositePrimaryKey("pareja", "participante")` desde su primera migración. No se registra en el admin.

## Qué puede tener un modelo
- Propiedades y métodos de consulta simples sobre sus propios datos y sus objetos relacionados directos: `perfil_completo`, `Encuentro.lugares_libres()` (4 − participantes − invitaciones pendientes), `Encuentro.esta_completo()`. El promedio de nivel lo calcula el motor, no el modelo.
- **No**: reglas que cruzan varios modelos, cambios de estado, envío de correos ni llamadas al motor. Eso va en los servicios.
- No usar señales (`signals`) ni sobrescribir `save()` con lógica de negocio.

## Migraciones
- Generarlas con `makemigrations`, con nombre descriptivo (`--name`). Nunca editar una migración ya aplicada.
- Después de crear o cambiar modelos, revisar con `sqlmigrate` que tablas, columnas y restricciones coincidan con `esquema.sql` e informar cualquier diferencia.
- No fusionar (`squash`) ni borrar migraciones sin consultar.

## Datos iniciales
- `apps/localidades/fixtures/localidades.json` con el catálogo de `modelo-clases.md`.
- Los datasets de demostración y de evaluación no son fixtures de las apps: ver la regla de evaluación.

## Admin
Registrar Usuario (con su preferencia y franjas en línea), Localidad, Encuentro (con participantes e invitaciones en línea), Combinacion y PropuestaEncuentro, para cargar y revisar datos de demostración. Solo lectura para Combinacion y PropuestaEncuentro.
