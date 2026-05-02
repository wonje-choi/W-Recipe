import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_edit_request"

    id = pw.CharField(max_length=32, primary_key=True)
    user_id = pw.CharField(max_length=32, index=True)
    recipe_version_id = pw.CharField(max_length=32, index=True)
    request_type = pw.CharField(max_length=32, index=True)
    content = pw.TextField(default="")
    attachment_url = pw.CharField(max_length=1024, default="")
    status = pw.CharField(max_length=32, default="open", index=True)
    admin_memo = pw.TextField(default="")
    handled_by = pw.CharField(max_length=32, default="")
    handled_at = pw.DateTimeField(null=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
