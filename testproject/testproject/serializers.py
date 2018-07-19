

class ProductSerializer(HistoryMixin, WritableNestedModelSerializer):
    replacement_product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),  # pylint: disable=E1101
        pk_field=serializers.UUIDField(format="hex_verbose"),
        required=False,
        allow_null=True,
    )
    subcategory = serializers.PrimaryKeyRelatedField(
        queryset=Subcategory.objects.all(),  # pylint: disable=E1101
        pk_field=serializers.UUIDField(format="hex_verbose"),
        required=False
    )
    owning_organization = serializers.PrimaryKeyRelatedField(
        pk_field=serializers.UUIDField(format="hex_verbose"),
        read_only=True,
    )
    subcategory_data = SubcategorySerializer(
        source="subcategory", read_only=True)
    manufacturer_data = InlineManufacturerSerializer(
        source="manufacturer", read_only=True)
    feature_attributes = ProductFeatureAttributesSerializer(
        required=False, allow_null=True)
    is_custom = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("id", "created_at", "modified_at", "created_by",
                            "modified_by", )
