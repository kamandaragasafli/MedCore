from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from prescriptions.models import PrescriptionItem
from doctors.services.financial_calculator import recalculate_doctor_financials


@receiver(post_save, sender=PrescriptionItem)
def prescription_item_saved(sender, instance, **kwargs):
    doctor_id = instance.prescription.doctor_id
    if doctor_id:
        recalculate_doctor_financials(doctor_ids=[doctor_id])


@receiver(post_delete, sender=PrescriptionItem)
def prescription_item_deleted(sender, instance, **kwargs):
    doctor_id = instance.prescription.doctor_id
    if doctor_id:
        recalculate_doctor_financials(doctor_ids=[doctor_id])

