from storages.backends.s3boto3 import S3Boto3Storage


__all__ = (
  'S3DefaultStorage',
  'S3StaticStorage'
)

class S3DefaultStorage(S3Boto3Storage):
    default_acl = 'private'
    location = 'media'
    file_overwrite = False

class S3StaticStorage(S3Boto3Storage):
    default_acl = 'public-read'
    location = 'static'
    file_overwrite = False