class MergeSerializer:
    """
    A utility class for merging a serializer-instance with serializer_data
    """

    @classmethod
    def merge_serialize(cls, instance, req_data, metadata: dict = {}, **kwargs):
        """
        Merge the serializer instance with the serializer_data
        """

        payload = dict()
        for field in cls.Meta.fields:

            if field in metadata.get("exclude", []):
                payload[field] = getattr(instance, field)
                continue

            if field in req_data:
                payload[field] = req_data[field]
                continue

            payload[field] = getattr(instance, field)

        return cls(instance=instance, data=payload, **kwargs)
