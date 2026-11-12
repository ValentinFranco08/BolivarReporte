import enum


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"


class ReportStatus(str, enum.Enum):
    REPORTADO = "reportado"
    CLASIFICADO = "clasificado"
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"
    RECHAZADO = "rechazado"
    DUPLICADO = "duplicado"
    REQUIERE_INFORMACION = "requiere_informacion"


class ReportPriority(str, enum.Enum):
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"
    CRITICAL = "critica"


class AnimalReportType(str, enum.Enum):
    PERDIDO = "perdido"
    ENCONTRADO = "encontrado"
    ALERTA_CEBO = "alerta_cebo"
    EN_TRANSITO = "en_transito"
    ADOPCION = "adopcion"


class PetType(str, enum.Enum):
    PERRO = "perro"
    GATO = "gato"
    OTRO = "otro"


class PetHealthStatus(str, enum.Enum):
    SANO = "sano"
    LASTIMADO = "lastimado"
    SINTOMAS_ENVENENAMIENTO = "sintomas_envenenamiento"
    CON_COLLAR = "con_collar"


class RemumStatus(str, enum.Enum):
    A_SALVO = "a_salvo"
    EXTRAVIADO = "extraviado"


class HealthEventType(str, enum.Enum):
    ANTIRRABICA = "antirrabica"
    CASTRACION = "castracion"
    DESPARASITACION = "desparasitacion"
    OTRO = "otro"
