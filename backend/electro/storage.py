from django.core.files.storage import FileSystemStorage


class DeleteOldStorage(FileSystemStorage):

    def save(self, name, content, max_length=None):
        for ext in ('.jpg', '.jpeg', '.png', '.webp'):
            old_file_name = name.split('.')[0] + ext
            if self.exists(old_file_name):
                self.delete(old_file_name)
        return super().save(name, content, max_length=None)
