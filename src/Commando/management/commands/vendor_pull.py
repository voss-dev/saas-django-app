from django.core.management.base import BaseCommand
from django.conf import settings
from helpers.downloader import download_to_local
from pathlib import Path

# Dictionary mapping local filenames to CDN source URLS
VENDOR_STATIC_FILES = {
    "flowbite.min.css": "https://cdn.jsdelivr.net/npm/flowbite@4.0.1/dist/flowbite.min.css",
    "flowbite.min.js": "https://cdn.jsdelivr.net/npm/flowbite@4.0.1/dist/flowbite.min.js",
    "flowbite.min.js.map": "https://cdn.jsdelivr.net/npm/flowbite@4.0.1/dist/flowbite.min.js.map",
}

class Command(BaseCommand):

    help = "Pulls vender static files from CDNs into local static_files/vendors/"

    def handle(self, *args, **options):
        self.stdout.write("Donwloading vendor static files ...")

        # Target directory: src/static_files/"vendors"
        vendor_dir = Path(settings.STATICFILES_DIRS[0]) / "vendors"
        vendor_dir.mkdir(parents=True, exist_ok=True)

        completed_urls = []
        for filename, url in VENDOR_STATIC_FILES.items():
            outpath = vendor_dir / filename
            success = download_to_local(url, outpath)

            if success:
                completed_urls.append(url)

        if len(completed_urls) == len(VENDOR_STATIC_FILES):
            self.stdout.write(self.style.SUCCESS("Successfully updated all vendor static files."))
        else:
            self.stdout.write(self.style.ERROR("Some vemdor files failed to download."))    