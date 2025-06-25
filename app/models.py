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
    predict_flag = models.BooleanField()
    train_flag = models.BooleanField()
 

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

class AccelerationStatTimeOptimized(models.Model):
    id = models.BigAutoField(primary_key=True)
    composite = models.CharField(max_length=150, blank=True, null=True)
    timestamp = models.DateTimeField()
    rms_axial = models.DecimalField(db_column='rms_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rms_vertical = models.DecimalField(db_column='rms_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rms_horizontal = models.DecimalField(db_column='rms_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    peak_axial = models.DecimalField(db_column='peak_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    peak_vertical = models.DecimalField(db_column='peak_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    peak_horizontal = models.DecimalField(db_column='peak_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    peak_to_peak_axial = models.DecimalField(db_column='peak_to_peak_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    peak_to_peak_vertical = models.DecimalField(db_column='peak_to_peak_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    peak_to_peak_horizontal = models.DecimalField(db_column='peak_to_peak_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    kurtosis_axial = models.DecimalField(db_column='kurtosis_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    kurtosis_vertical = models.DecimalField(db_column='kurtosis_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    kurtosis_horizontal = models.DecimalField(db_column='kurtosis_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    flag = models.BooleanField()
    rms_only = models.BooleanField()
    asset_id = models.CharField(max_length=150, blank=True, null=True)
    mount_id = models.CharField(max_length=150, blank=True, null=True)
    creation_date = models.DateTimeField()
    abs_energy_axial = models.DecimalField(db_column='abs_energy_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    abs_energy_horizontal = models.DecimalField(db_column='abs_energy_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    abs_energy_vertical = models.DecimalField(db_column='abs_energy_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    absolute_maximum_axial = models.DecimalField(db_column='absolute_maximum_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    absolute_maximum_horizontal = models.DecimalField(db_column='absolute_maximum_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    absolute_maximum_vertical = models.DecimalField(db_column='absolute_maximum_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    absolute_sum_of_changes_axial = models.DecimalField(db_column='absolute_sum_of_changes_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    absolute_sum_of_changes_horizontal = models.DecimalField(db_column='absolute_sum_of_changes_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    absolute_sum_of_changes_vertical = models.DecimalField(db_column='absolute_sum_of_changes_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    benford_correlation_axial = models.DecimalField(db_column='benford_correlation_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    benford_correlation_horizontal = models.DecimalField(db_column='benford_correlation_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    benford_correlation_vertical = models.DecimalField(db_column='benford_correlation_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    crest_factor_axial = models.DecimalField(db_column='crest_factor_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    crest_factor_horizontal = models.DecimalField(db_column='crest_factor_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    crest_factor_vertical = models.DecimalField(db_column='crest_factor_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    sample_entropy_axial = models.DecimalField(db_column='sample_entropy_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    sample_entropy_horizontal = models.DecimalField(db_column='sample_entropy_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    sample_entropy_vertical = models.DecimalField(db_column='sample_entropy_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    skewness_axial = models.DecimalField(db_column='skewness_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    skewness_horizontal = models.DecimalField(db_column='skewness_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    skewness_vertical = models.DecimalField(db_column='skewness_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    standard_deviation_axial = models.DecimalField(db_column='standard_deviation_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    standard_deviation_horizontal = models.DecimalField(db_column='standard_deviation_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    standard_deviation_vertical = models.DecimalField(db_column='standard_deviation_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    variance_axial = models.DecimalField(db_column='variance_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    variance_horizontal = models.DecimalField(db_column='variance_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    variance_vertical = models.DecimalField(db_column='variance_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    variation_coefficient_axial = models.DecimalField(db_column='variation_coefficient_Axial', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    variation_coefficient_horizontal = models.DecimalField(db_column='variation_coefficient_Horizontal', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    variation_coefficient_vertical = models.DecimalField(db_column='variation_coefficient_Vertical', max_digits=20, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cluster_flag = models.BooleanField() 

    class Meta:
        managed = False
        db_table = 'acceleration_stat_time_optimized'
        unique_together = (('timestamp', 'mount_id'),)