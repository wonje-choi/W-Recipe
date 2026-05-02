import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_admin_action_log"

    id = pw.CharField(max_length=32, primary_key=True)
    admin_user_id = pw.CharField(max_length=32, index=True)
    action_type = pw.CharField(max_length=64, index=True)
    target_type = pw.CharField(max_length=64, index=True)
    target_id = pw.CharField(max_length=32, default="", index=True)
    before_value = pw.TextField(default="{}")
    after_value = pw.TextField(default="{}")
    ip_address = pw.CharField(max_length=64, default="")
    user_agent = pw.CharField(max_length=512, default="")
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
