from django.core.management.base import BaseCommand
from app.cron import run_model_prediction_cron 

class Command(BaseCommand):
    help = 'Run model prediction cron job manually'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mount-id',
            type=str,
            help='Process specific mount_id only',
        )

    def handle(self, *args, **options):
        mount_id = options.get('mount_id')
        
        if mount_id:
            self.stdout.write(f'Processing specific mount_id: {mount_id}')
            from app.cron import process_mount_id
            process_mount_id(mount_id)
        else:
            self.stdout.write('Running full model prediction cron job...')
            run_model_prediction_cron()
        
        self.stdout.write(
            self.style.SUCCESS('Model prediction cron job completed!')
        )