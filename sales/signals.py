from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from sales.models import Sale, SaleItem
from doctors.services.financial_calculator import recalculate_doctor_financials


def _recalculate_for_sale_region(sale):
    if sale and sale.region_id:
        recalculate_doctor_financials(region_ids=[sale.region_id])


@receiver(post_save, sender=Sale)
def sale_saved(sender, instance, **kwargs):
    _recalculate_for_sale_region(instance)


@receiver(post_delete, sender=Sale)
def sale_deleted(sender, instance, **kwargs):
    _recalculate_for_sale_region(instance)


@receiver(post_save, sender=SaleItem)
def sale_item_saved(sender, instance, **kwargs):
    _recalculate_for_sale_region(instance.sale)


@receiver(post_delete, sender=SaleItem)
def sale_item_deleted(sender, instance, **kwargs):
    _recalculate_for_sale_region(instance.sale)

