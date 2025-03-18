class MergeSerializer:
    """
    A utility class for merging a serializer-instance with serializer_data
    """

    @classmethod
    def merge_serialize(cls, instance, validated_data, metadata: dict = {}, **kwargs):
        data = dict()
        for field in cls.Meta.fields:

            if field in metadata.get("exclude", []):
                data[field] = getattr(instance, field)
                continue

            if field in validated_data:
                data[field] = validated_data[field]
                continue

            data[field] = getattr(instance, field)
        return cls(instance=instance, data=data, **kwargs)
