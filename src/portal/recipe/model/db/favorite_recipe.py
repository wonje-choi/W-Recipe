import datetime
import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base("recipe")

class Model(base):
    class Meta:
        db_table = "recipe_favorite"
        indexes = (
            (("user_id", "recipe_version_id"), True),
        )

    id = pw.CharField(max_length=32, primary_key=True)
    user_id = pw.CharField(max_length=32, index=True)
    recipe_version_id = pw.CharField(max_length=32, index=True)
    created_at = pw.DateTimeField(default=datetime.datetime.now, index=True)
