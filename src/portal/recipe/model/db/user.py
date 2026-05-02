import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_user"

    id = pw.CharField(max_length=32, primary_key=True)
    email = pw.CharField(max_length=190, unique=True, index=True)
    password_hash = pw.CharField(max_length=255)
    nickname = pw.CharField(max_length=64, default="")
    role = pw.CharField(max_length=16, default="user", index=True)
    status = pw.CharField(max_length=16, default="active", index=True)
    subscription_plan = pw.CharField(max_length=16, default="free", index=True)
    subscription_expires_at = pw.DateTimeField(null=True)
    login_failed_count = pw.IntegerField(default=0)
    last_login_at = pw.DateTimeField(null=True)
    locked_until = pw.DateTimeField(null=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)
