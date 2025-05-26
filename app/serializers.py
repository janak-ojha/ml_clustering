from rest_framework import serializers
from .models import TestRawDataMaster,AssetOperatingModeMaster

class RawDataMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestRawDataMaster
        fields = [
            'timestamp',
              'fs', 
              'no_of_samples', 
              'raw_data', 
              'axis',
              'mount_id'
              ]


class AssetOperatingModeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetOperatingModeMaster
        fields = [
            'id',
            'composite',
            'timestamp',
            'mount_id',
            'asset_id',
            'operating_mode',
            'cluster_id',
            'creation_date'
        ]
