from django.db import models


class RawDataMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField()
    fs = models.IntegerField()
    no_of_samples = models.IntegerField(blank=True, null=True)
    raw_data = models.TextField()  # This field type is a guess.
    axis = models.CharField(max_length=10)
    asset_id = models.CharField(max_length=150, blank=True, null=True)
    creation_date = models.DateField()
    composite = models.CharField(max_length=150, blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    mount_id = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'raw_data_master'

class TestRawDataMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    composite = models.CharField(max_length=150, blank=True, null=True)
    timestamp = models.DateTimeField()
    fs = models.IntegerField()
    no_of_samples = models.IntegerField(blank=True, null=True)
    raw_data = models.TextField()  # This field type is a guess.
    axis = models.CharField(max_length=10)
    asset_id = models.CharField(max_length=150, blank=True, null=True)
    flag = models.BooleanField()
    mount_id = models.CharField(max_length=150, blank=True, null=True)
    creation_date = models.DateField(auto_now=True)
    last_update = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'test_raw_data_master'


class AssetOperatingModeMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    composite = models.CharField(max_length=150, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    mount_id = models.CharField(max_length=150, blank=True, null=True)
    asset_id = models.CharField(max_length=150, blank=True, null=True)
    operating_mode = models.CharField(max_length=150, blank=True, null=True)
    cluster_id = models.CharField(max_length=150, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'asset_operating_mode_master'
