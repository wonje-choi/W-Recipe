import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_dish"

    id = pw.CharField(max_length=32, primary_key=True)
    name = pw.CharField(max_length=160, index=True)
    description = pw.TextField(default="")
    category = pw.CharField(max_length=64, default="", index=True)
    tags = pw.TextField(default="[]")
    thumbnail_url = pw.CharField(max_length=1024, default="")
    view_count = pw.IntegerField(default=0, index=True)
    status = pw.CharField(max_length=32, default="draft", index=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
