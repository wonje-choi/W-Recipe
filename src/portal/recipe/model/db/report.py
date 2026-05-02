import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_report"
        indexes = (
            (("reporter_user_id", "target_type", "target_id"), True),
        )

    id = pw.CharField(max_length=32, primary_key=True)
    reporter_user_id = pw.CharField(max_length=32, index=True)
    target_type = pw.CharField(max_length=32, index=True)
    target_id = pw.CharField(max_length=32, index=True)
    reason = pw.TextField(default="")
    detail = pw.TextField(default="")
    status = pw.CharField(max_length=32, default="open", index=True)
    admin_memo = pw.TextField(default="")
    handled_by = pw.CharField(max_length=32, default="")
    handled_at = pw.DateTimeField(null=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
