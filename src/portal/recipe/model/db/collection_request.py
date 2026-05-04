import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_collection_request"

    id = pw.CharField(max_length=32, primary_key=True)
    target_type = pw.CharField(max_length=32, index=True)
    target_value = pw.TextField(default="")
    target_label = pw.CharField(max_length=300, default="")
    provider = pw.CharField(max_length=32, default="auto", index=True)
    status = pw.CharField(max_length=32, default="queued", index=True)
    max_items = pw.IntegerField(default=10)
    include_comments = pw.BooleanField(default=False)
    immediate = pw.BooleanField(default=True)
    result_count = pw.IntegerField(default=0)
    retry_count = pw.IntegerField(default=0)
    error_message = pw.TextField(default="")
    requested_by = pw.CharField(max_length=32, default="", index=True)
    started_at = pw.DateTimeField(null=True)
    completed_at = pw.DateTimeField(null=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
