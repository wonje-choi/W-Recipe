import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_expert"

    id = pw.CharField(max_length=32, primary_key=True)
    name = pw.CharField(max_length=64, index=True)
    email = pw.CharField(max_length=190, default="", index=True)
    specialty = pw.CharField(max_length=128, default="")
    status = pw.CharField(max_length=16, default="active", index=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
