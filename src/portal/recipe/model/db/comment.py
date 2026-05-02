import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_comment"

    id = pw.CharField(max_length=32, primary_key=True)
    user_id = pw.CharField(max_length=32, index=True)
    recipe_version_id = pw.CharField(max_length=32, index=True)
    content = pw.TextField(default="")
    status = pw.CharField(max_length=32, default="visible", index=True)
    report_count = pw.IntegerField(default=0)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
