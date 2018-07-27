import uuid

from django.db import models

ORGANIZATION_TYPE_CHOICES = (
    ("partner", "Partner"),
    ("facilitator", "Facilitator"),
    ("consultant", "Consultant"),
    ("supplier", "Supplier"),
)

# IDs only
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


# IDs only
class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    org_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPE_CHOICES)
    website = models.URLField("Organization URL", blank=True)

    class Meta:
        ordering = ["name", ]

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default="TBD")
    list_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    product_url = models.URLField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )
    replacement_product = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    manufacturer = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="manufactured_products"
    )
    spec_reviewed_date = models.DateField(null=True, blank=True)
    lead_time_days = models.IntegerField(null=True, blank=True) # number of days it takes to receive equipment after P.O. is issued, new field
    is_discontinued = models.NullBooleanField(default=None) # manufacturer stopped making this product

    class Meta:
        ordering = ["name", ]

    def __str__(self):
        return self.name

# nested
class ProductFeatureAttributes(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="feature_attributes"
    )
    seismic = models.BooleanField(default=False)
    ada = models.BooleanField(default=False)
    antimicrobial = models.BooleanField(default=False)
    green = models.BooleanField(default=False)
    opa = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = "product feature attributes"
