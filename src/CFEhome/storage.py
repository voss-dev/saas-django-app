# Telling WhiteNoise to ignore input.css

from whitenoise.storage import CompressedManifestStaticFilesStorage

class CustomStaticFilesStorage(CompressedManifestStaticFilesStorage):
    def post_process(self, *args, **kwargs):
        files = super().post_process(*args, **kwargs)
        for name, hashed_name, processed in files:
            if name == "allauth_ui/input.css":
                continue
            yield name, hashed_name, processed