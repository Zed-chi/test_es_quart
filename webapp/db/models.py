from tortoise import fields
from tortoise.models import Model


class Document(Model):
    id = fields.IntField(pk=True)
    text = fields.TextField()
    rubrics = fields.TextField()
    created_date = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"self.id ={len(self.text)}-chr="
