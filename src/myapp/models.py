from django.db import models

# Create your models here.

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='group_name_uniq'),
        ]
        db_table = 'group'


class User(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)
    code = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'user'


class GroupUserRelation(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'group_user_relation'


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'tag'
