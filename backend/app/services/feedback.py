from ..core.errors import ApplicationError, NotFoundError

class FeedbackService:
    def __init__(self, feedback, predictions, unit_of_work):
        self.feedback = feedback
        self.predictions = predictions
        self.unit_of_work = unit_of_work

    def submit(self, prediction_id, feedback, reviewer_id):
        if not feedback.correct and not feedback.correct_class:
            raise ApplicationError("Debe indicar la clase correcta cuando la predicción es incorrecta.")
        with self.unit_of_work:
            if self.predictions.get(prediction_id) is None:
                raise NotFoundError("Predicción no encontrada")
            result = self.feedback.upsert(prediction_id, feedback.correct,
                               feedback.correct_class if not feedback.correct else None, reviewer_id)
        return result

    def export(self):
        corrections = []
        for feedback in self.feedback.list():
            if feedback.correct or not feedback.correct_class or not feedback.prediction or not feedback.prediction.report:
                continue
            prediction = feedback.prediction
            report = prediction.report
            corrections.append({"report_id": report.id, "image_path": report.image_path,
                "description": report.description, "predicted_class": prediction.predicted_class,
                "correct_class": feedback.correct_class, "confidence": prediction.confidence,
                "reviewed_at": feedback.created_at.isoformat() if feedback.created_at else None})
        return {"total_corrections": len(corrections), "data": corrections,
                "note": "Estos pares imagen+etiqueta pueden agregarse al dataset para reentrenamiento supervisado."}

    def training_samples(self, image_directory, pending_only=False):
        from pathlib import Path
        samples = []
        for feedback in self.feedback.list(pending_only):
            if feedback.correct or not feedback.correct_class or not feedback.prediction or not feedback.prediction.report:
                continue
            report = feedback.prediction.report
            samples.append({"feedback_id": feedback.id, "report_id": report.id,
                "image": str(Path(image_directory) / Path(report.image_path).name),
                "text": report.description or "", "label": feedback.correct_class})
        return samples
