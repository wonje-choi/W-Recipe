import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_ai_prompt_template"

    id = pw.CharField(max_length=32, primary_key=True)
    prompt_key = pw.CharField(max_length=64, index=True)
    version = pw.CharField(max_length=32, index=True)
    prompt_version = pw.CharField(max_length=100, unique=True, index=True)
    title = pw.CharField(max_length=160, default="")
    description = pw.TextField(default="")
    template = pw.TextField(default="")
    input_schema = pw.TextField(default="{}")
    output_schema = pw.TextField(default="{}")
    model_hint = pw.CharField(max_length=120, default="")
    is_active = pw.BooleanField(default=False, index=True)
    change_reason = pw.TextField(default="")
    created_by = pw.CharField(max_length=32, default="", index=True)
    updated_by = pw.CharField(max_length=32, default="", index=True)
    deactivated_at = pw.DateTimeField(null=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
