import secrets
import string
from .. import models
from ..core.errors import ApplicationError, NotFoundError, PermissionDeniedError

class QrCodeGenerator:
    def __init__(self, repository):
        self.repository = repository

    def generate(self, length=4):
        return "B-" + "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))

    def unique(self):
        for _ in range(100):
            code = self.generate()
            if self.repository.by_qr(code) is None:
                return code
        raise ApplicationError("No se pudo generar un código QR disponible")

class RemumService:
    def __init__(self, records, reports, users, storage, unit_of_work):
        self.records = records
        self.reports = reports
        self.users = users
        self.storage = storage
        self.unit_of_work = unit_of_work
        self.qr_codes = QrCodeGenerator(records)

    def get(self, qr_code_id):
        record = self.records.by_qr(qr_code_id)
        if record is None:
            raise NotFoundError("Credencial REMUM no encontrada")
        return record

    def create(self, data, current_user=None, image=None, filename="image.jpg"):
        user = current_user or self.users.default_citizen()
        if user is None:
            raise ApplicationError("Se requiere un usuario para registrar la mascota")
        image_path = self.storage.save(image, filename) if image is not None else None
        try:
            with self.unit_of_work:
                record = self._create_record(user.id, data, image_path)
            return record
        except Exception:
            if image_path:
                self.storage.delete(image_path)
            raise

    def _create_record(self, user_id, data, image_path=None):
        return self.records.add(models.RemumRecord(
            **data.model_dump(), user_id=user_id, image_path=image_path, qr_code_id=self.qr_codes.unique()))

    def add_health_event(self, code, data):
        with self.unit_of_work:
            record = self.get(code)
            result = self.records.add_related(models.RemumHealthEvent(remum_record_id=record.id, **data.model_dump()))
        return result

    def add_godparent(self, code, data):
        with self.unit_of_work:
            record = self.get(code)
            if not record.is_community_pet:
                raise ApplicationError("Esta mascota no es comunitaria, no se le pueden asignar padrinos.")
            result = self.records.add_related(models.RemumGodparent(remum_record_id=record.id, **data.model_dump()))
        return result

    def panic(self, code, current_user, lat=None, lng=None):
        with self.unit_of_work:
            record = self.get(code)
            if record.user_id != current_user.id and current_user.role != models.UserRole.ADMIN:
                raise PermissionDeniedError("No tienes permiso para emitir alertas para esta mascota")
            self._create_alert(record, lat, lng)
        return record

    def _create_alert(self, record, lat=None, lng=None):
        record.status = models.RemumStatus.EXTRAVIADO
        self.reports.add(models.Report(
            user_id=record.user_id,
            description=f"¡ALERTA AUTOMÁTICA REMUM! {record.pet_name} se extravió en la zona de {record.address or 'Bolívar'}. Por favor prestar atención.",
            address=record.address,
            latitude=lat if lat is not None else record.latitude,
            longitude=lng if lng is not None else record.longitude,
            image_path=record.image_path or "", report_type=models.AnimalReportType.PERDIDO,
            pet_type=record.pet_type, pet_name=record.pet_name, pet_breed=record.pet_breed,
            color_description=record.color_description, health_status=models.PetHealthStatus.CON_COLLAR,
            contact_name=record.user.name if record.user else None, is_resolved=False,
            status=models.ReportStatus.REPORTADO, priority=models.ReportPriority.HIGH,
        ))

    def by_owner(self, user):
        return self.records.by_owner(user.id) if user else []

    def community(self):
        return self.records.community()
