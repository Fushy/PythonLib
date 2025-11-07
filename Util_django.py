import os
from typing import Optional

import django
from django.db import IntegrityError


# class SoundField(FileField):
#     description = "A field for handling sound/audio files"
#
#     def __init__(self, *args, **kwargs):
#         if 'upload_to' not in kwargs:
#             kwargs['upload_to'] = 'sounds/'
#         self.max_upload_size = kwargs.pop('max_upload_size', 10 * 1024 * 1024)
#         self.allowed_audio_types = kwargs.pop('allowed_audio_types', [
#             'audio/mpeg',  # MP3
#             'audio/wav',  # WAV
#             'audio/ogg',  # OGG
#             'audio/x-m4a',  # M4A
#             'audio/aac',  # AAC
#             'audio/flac',  # FLAC
#             'audio/x-ms-wma',  # WMA
#         ])
#         super().__init__(*args, **kwargs)
#
#     def clean(self, *args, **kwargs):
#         data = super().clean(*args, **kwargs)
#         if data:
#             file = data.file
#             if file.size > self.max_upload_size:
#                 raise ValidationError(
#                     f'Please keep filesize under {filesizeformat(self.max_upload_size)}. '
#                     f'Current filesize: {filesizeformat(file.size)}')
#             try:
#                 mime = magic.from_buffer(file.read(1024), mime=True)
#                 file.seek(0)
#                 if mime not in self.allowed_audio_types:
#                     raise ValidationError(f'File type ({mime}) is not supported. '
#                                           f'Allowed types are: {", ".join(self.allowed_audio_types)}')
#             except Exception as e:
#                 raise ValidationError(f'Error validating file type: {str(e)}')
#         return data
#
#     def deconstruct(self):
#         name, path, args, kwargs = super().deconstruct()
#         if self.max_upload_size != 10 * 1024 * 1024:
#             kwargs['max_upload_size'] = self.max_upload_size
#         if self.allowed_audio_types != ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/x-m4a', 'audio/aac', 'audio/flac', 'audio/x-ms-wma']:
#             kwargs['allowed_audio_types'] = self.allowed_audio_types
#         return name, path, args, kwargs
#
#
# class Song(Model):
#     """ settings.py
#     INSTALLED_APPS = [
#         ...
#         'django-magic',  # For MIME type detection
#     ]
#     # File upload settings
#     MEDIA_URL = '/media/'
#     MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
#     # URLs configuration (urls.py):
#     from django.conf import settings
#     from django.conf.urls.static import static
#     urlpatterns = [
#         ...
#     ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     """
#     title = CharField(max_length=100)
#     artist = CharField(max_length=100)
#     audio_file = SoundField(
#         max_upload_size=20 * 1024 * 1024,  # 20MB
#         allowed_audio_types=['audio/mpeg', 'audio/wav'],  # Only allow MP3 and WAV
#         help_text='Upload MP3 or WAV file (max 20MB)'
#     )
#     uploaded_at = DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.title} - {self.artist}"


def get_or_none(model_class, **kwargs) -> Optional:
    try:
        return model_class.objects.get(**kwargs)
    except model_class.DoesNotExist:
        return None
    except Exception as e:
        return e


def get_lookup_fields(model):
    lookup_fields = []

    def get_model_constraints(model_class):
        fields = []
        if hasattr(model_class._meta, 'constraints'):
            for constraint in model_class._meta.constraints:
                if hasattr(constraint, 'fields'):
                    fields.extend(constraint.fields)
        return fields

    lookup_fields.extend(get_model_constraints(model))
    for parent in model._meta.get_parent_list():
        lookup_fields.extend(get_model_constraints(parent))
    return list(dict.fromkeys(lookup_fields))


def get_defaults_lookup_fields(model, model_dict):
    mandatory_fields = get_lookup_fields(model)
    defaults = {key: value for key, value in model_dict.items() if key not in mandatory_fields}
    mandatory_fields = {key: value for key, value in model_dict.items() if key in mandatory_fields}
    return defaults, mandatory_fields


def get_updated_or_create(model, model_dict, base_model=None):
    """base_model peut etre omis est remplacé par une fonction qui cherche le model de base"""
    assert type(model_dict) is dict
    defaults, mandatory_fields = get_defaults_lookup_fields(model, model_dict)
    try:
        instance, created = model.objects.get_or_create(defaults=defaults, **mandatory_fields)
    except IntegrityError:
        """ IntegrityError happens when a submodel doesnt exists but the supermodel exists with the same key """
        base_instance = base_model.objects.get(**mandatory_fields)
        instance = model()
        for field in base_instance._meta.fields:
            setattr(instance, field.name, getattr(base_instance, field.name))
        for key, value in defaults.items():
            setattr(instance, key, value)
        instance.save()
        created = True
    if not created:
        for key, value in defaults.items():
            setattr(instance, key, value)
        instance.save()
    return instance


def get_relation_field(model):
    return [f.name for f in model._meta.get_fields() if f.is_relation is False]


def get_related_field_names(model, related_name, contains=None):
    related_field = model._meta.get_field(related_name)
    related_model = related_field.related_model
    return [f'{related_name}__{field.name}' for field in related_model._meta.get_fields()
            if not field.is_relation and (not contains or any(c in field.name for c in contains))]


def setup_django(package_path):
    package_path = package_path.replace("/", ".")
    package_path = package_path[:-1] if package_path[-1] == "." or package_path[-1] == "/" else package_path
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', package_path)
    django.setup()
