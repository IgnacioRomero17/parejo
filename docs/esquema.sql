-- =====================================================================
-- parejo · Esquema de base de datos (PostgreSQL)
-- Fuente: DER del TFG. Este archivo es la referencia técnica de tablas,
-- tipos, claves y restricciones. El significado de cada dato está en
-- docs/modelo-clases.md; las reglas de negocio, en docs/historias-de-usuario.md.
--
-- Django genera las tablas con sus migraciones: este archivo NO se ejecuta
-- en producción. Los modelos deben producir un esquema equivalente.
-- Convenciones:
--   * Valores de enumeraciones: códigos en MAYÚSCULAS (ver modelo-clases.md).
--   * Composición (UML) -> ON DELETE CASCADE. Resto -> ON DELETE RESTRICT.
--   * Las reglas que dependen de la fecha actual o de contar filas
--     (fecha no pasada, máximo 4 participantes, máximo 3 combinaciones)
--     se validan en el backend, no con CHECK.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Catálogo de localidades (cerrado; se carga con un fixture)
-- ---------------------------------------------------------------------
CREATE TABLE localidad (
    id_localidad  SERIAL       PRIMARY KEY,
    nombre        VARCHAR(80)  NOT NULL UNIQUE,
    latitud       NUMERIC(9,6) NOT NULL CHECK (latitud  BETWEEN -90  AND 90),
    longitud      NUMERIC(9,6) NOT NULL CHECK (longitud BETWEEN -180 AND 180)
);

-- ---------------------------------------------------------------------
-- Usuario (modelo de usuario personalizado de Django)
-- Los campos del perfil deportivo son NULL hasta completar el onboarding.
-- ---------------------------------------------------------------------
CREATE TABLE usuario (
    id_usuario                   SERIAL        PRIMARY KEY,
    email                        VARCHAR(254)  NOT NULL UNIQUE
                                 CHECK (email = LOWER(email)),
    password_hash                VARCHAR(128)  NOT NULL,
    nombre                       VARCHAR(60)   NOT NULL,
    apellido                     VARCHAR(60)   NOT NULL,
    edad                         SMALLINT      CHECK (edad BETWEEN 18 AND 99),
    genero                       VARCHAR(15)   CHECK (genero IN ('MASCULINO','FEMENINO','NO_DECLARA')),
    frecuencia_juego             VARCHAR(20)   CHECK (frecuencia_juego IN
                                 ('MENOS_1_SEMANA','1_SEMANA','2_3_SEMANA','4_MAS_SEMANA')),
    nivel_estimado               NUMERIC(2,1)  CHECK (nivel_estimado BETWEEN 1.0 AND 7.0
                                                      AND MOD(nivel_estimado * 10, 5) = 0),
    id_localidad                 INTEGER       REFERENCES localidad (id_localidad) ON DELETE RESTRICT,
    disponible_para_invitaciones BOOLEAN       NOT NULL DEFAULT FALSE,
    activo                       BOOLEAN       NOT NULL DEFAULT TRUE,
    fecha_registro               TIMESTAMPTZ   NOT NULL DEFAULT NOW()
    -- Columnas técnicas que agrega Django y no figuran en el DER:
    -- last_login, is_staff, is_superuser (y las tablas de grupos/permisos).
);

-- ---------------------------------------------------------------------
-- Preferencia (1 usuario : 0..1 preferencia) · composición
-- ---------------------------------------------------------------------
CREATE TABLE preferencia (
    id_preferencia  SERIAL      PRIMARY KEY,
    id_usuario      INTEGER     NOT NULL UNIQUE
                    REFERENCES usuario (id_usuario) ON DELETE CASCADE,
    tipo_encuentro  VARCHAR(12) NOT NULL CHECK (tipo_encuentro IN ('RECREATIVO','COMPETITIVO','INDIFERENTE')),
    lado_preferido  VARCHAR(12) NOT NULL CHECK (lado_preferido IN ('DRIVE','REVES','INDIFERENTE'))
);

-- ---------------------------------------------------------------------
-- Disponibilidad (1 usuario : 0..* franjas) · composición
-- dia_semana: 1 = lunes ... 7 = domingo (ISO 8601)
-- Franjas en pasos de 30 min, de al menos 60 min, sin cruzar medianoche.
-- La unión de franjas superpuestas o contiguas se hace en el backend.
-- ---------------------------------------------------------------------
CREATE TABLE disponibilidad (
    id_disponibilidad SERIAL   PRIMARY KEY,
    id_usuario        INTEGER  NOT NULL REFERENCES usuario (id_usuario) ON DELETE CASCADE,
    dia_semana        SMALLINT NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
    hora_inicio       TIME     NOT NULL,
    hora_fin          TIME     NOT NULL,
    CONSTRAINT disponibilidad_orden    CHECK (hora_fin > hora_inicio),
    CONSTRAINT disponibilidad_minimo   CHECK (hora_fin - hora_inicio >= INTERVAL '60 minutes'),
    CONSTRAINT disponibilidad_paso_30  CHECK (EXTRACT(SECOND FROM hora_inicio) = 0
                                          AND EXTRACT(SECOND FROM hora_fin) = 0
                                          AND EXTRACT(MINUTE FROM hora_inicio) IN (0, 30)
                                          AND EXTRACT(MINUTE FROM hora_fin)    IN (0, 30))
);
CREATE INDEX disponibilidad_usuario_dia ON disponibilidad (id_usuario, dia_semana);

-- ---------------------------------------------------------------------
-- Encuentro
-- El organizador también se registra como participante (el primero).
-- Hora de inicio en pasos de 30 min; termina a las 23:30 como máximo
-- (las franjas tampoco pueden pasar de 23:30, así siempre puede haber candidatos).
-- ---------------------------------------------------------------------
CREATE TABLE encuentro (
    id_encuentro     SERIAL       PRIMARY KEY,
    id_organizador   INTEGER      NOT NULL REFERENCES usuario (id_usuario) ON DELETE RESTRICT,
    fecha            DATE         NOT NULL,
    hora_inicio      TIME         NOT NULL,
    duracion_minutos SMALLINT     NOT NULL CHECK (duracion_minutos IN (60, 90, 120)),
    id_localidad     INTEGER      NOT NULL REFERENCES localidad (id_localidad) ON DELETE RESTRICT,
    ubicacion        VARCHAR(150) NOT NULL,
    tipo_encuentro   VARCHAR(12)  NOT NULL CHECK (tipo_encuentro IN ('RECREATIVO','COMPETITIVO','INDIFERENTE')),
    estado           VARCHAR(25)  NOT NULL DEFAULT 'CREADO'
                     CHECK (estado IN ('CREADO','BUSCANDO_PARTICIPANTES','COMPLETO','PROPUESTA_GENERADA')),
    fecha_creacion   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT encuentro_paso_30
        CHECK (EXTRACT(SECOND FROM hora_inicio) = 0 AND EXTRACT(MINUTE FROM hora_inicio) IN (0, 30)),
    CONSTRAINT encuentro_no_cruza_medianoche
        CHECK (EXTRACT(EPOCH FROM hora_inicio) / 60 + duracion_minutos <= 1410)
);

-- ---------------------------------------------------------------------
-- Invitación (1 encuentro : 0..* invitaciones) · composición
-- Un usuario no puede ser invitado dos veces al mismo encuentro.
-- ---------------------------------------------------------------------
CREATE TABLE invitacion (
    id_invitacion       SERIAL      PRIMARY KEY,
    id_encuentro        INTEGER     NOT NULL REFERENCES encuentro (id_encuentro) ON DELETE CASCADE,
    id_usuario_invitado INTEGER     NOT NULL REFERENCES usuario (id_usuario) ON DELETE RESTRICT,
    estado              VARCHAR(10) NOT NULL DEFAULT 'PENDIENTE'
                        CHECK (estado IN ('PENDIENTE','ACEPTADA','RECHAZADA')),
    fecha_envio         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_respuesta     TIMESTAMPTZ,
    CONSTRAINT invitacion_unica UNIQUE (id_encuentro, id_usuario_invitado),
    CONSTRAINT invitacion_respuesta
        CHECK ((estado = 'PENDIENTE') = (fecha_respuesta IS NULL))
);

-- ---------------------------------------------------------------------
-- Participante (1 encuentro : 0..4 participantes) · composición
-- El máximo de 4 se valida en el backend.
-- ---------------------------------------------------------------------
CREATE TABLE participante (
    id_participante    SERIAL      PRIMARY KEY,
    id_encuentro       INTEGER     NOT NULL REFERENCES encuentro (id_encuentro) ON DELETE CASCADE,
    id_usuario         INTEGER     NOT NULL REFERENCES usuario (id_usuario) ON DELETE RESTRICT,
    fecha_confirmacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT participante_unico UNIQUE (id_encuentro, id_usuario)
);

-- ---------------------------------------------------------------------
-- Combinación (1 encuentro : 0..3 combinaciones) · composición
-- Se crean las 3 juntas al formar parejas. Puntaje entre 0 y 1.
-- ---------------------------------------------------------------------
CREATE TABLE combinacion (
    id_combinacion     SERIAL       PRIMARY KEY,
    id_encuentro       INTEGER      NOT NULL REFERENCES encuentro (id_encuentro) ON DELETE CASCADE,
    puntaje_equilibrio NUMERIC(5,4) NOT NULL CHECK (puntaje_equilibrio BETWEEN 0 AND 1),
    fecha_evaluacion   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- Pareja (1 combinación : 2 parejas) · composición
-- ---------------------------------------------------------------------
CREATE TABLE pareja (
    id_pareja      SERIAL   PRIMARY KEY,
    id_combinacion INTEGER  NOT NULL REFERENCES combinacion (id_combinacion) ON DELETE CASCADE,
    numero         SMALLINT NOT NULL CHECK (numero IN (1, 2)),
    CONSTRAINT pareja_numero_unico UNIQUE (id_combinacion, numero)
);

-- ---------------------------------------------------------------------
-- Integrantes de cada pareja (2 participantes por pareja)
-- Clave primaria compuesta, como en el DER.
-- ---------------------------------------------------------------------
CREATE TABLE pareja_integrante (
    id_pareja       INTEGER NOT NULL REFERENCES pareja (id_pareja) ON DELETE CASCADE,
    id_participante INTEGER NOT NULL REFERENCES participante (id_participante) ON DELETE RESTRICT,
    PRIMARY KEY (id_pareja, id_participante)
);

-- ---------------------------------------------------------------------
-- Propuesta de encuentro (1 encuentro : 0..1 propuesta)
-- Apunta a la combinación elegida; el puntaje se lee de esa combinación.
-- ---------------------------------------------------------------------
CREATE TABLE propuesta_encuentro (
    id_propuesta     SERIAL      PRIMARY KEY,
    id_encuentro     INTEGER     NOT NULL UNIQUE REFERENCES encuentro (id_encuentro) ON DELETE CASCADE,
    id_combinacion   INTEGER     NOT NULL UNIQUE REFERENCES combinacion (id_combinacion) ON DELETE RESTRICT,
    fecha_generacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
