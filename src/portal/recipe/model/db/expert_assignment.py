import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_expert_assignment"

    id = pw.CharField(max_length=32, primary_key=True)
    target_type = pw.CharField(max_length=32, index=True)
    target_id = pw.CharField(max_length=32, index=True)
    expert_id = pw.CharField(max_length=32, index=True)
    status = pw.CharField(max_length=32, default="assigned", index=True)
    review_note = pw.TextField(default="")
    assigned_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    reviewed_at = pw.DateTimeField(null=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
