from rest_framework import serializers
from kanmind_app.models import Board, Task, Comment
from django.contrib.auth import get_user_model

User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.ReadOnlyField(source="owner.id")

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
            "members",
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()

    def create(self, validated_data):
        members = validated_data.pop("members", [])

        board = Board.objects.create(**validated_data)
        board.members.set(members)

        return board


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.ReadOnlyField(source="owner.id")

    members = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]

    def get_members(self, obj):
        members = [
            {
                "id": obj.owner.id,
                "email": obj.owner.email,
                "fullname": obj.owner.fullname,
            }
        ]

        for member in obj.members.exclude(id=obj.owner.id):
            members.append(
                {
                    "id": member.id,
                    "email": member.email,
                    "fullname": member.fullname,
                }
            )

        return members

    def get_tasks(self, obj):
        return TaskSerializer(obj.tasks.all(), many=True).data


class TaskSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()

    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "assignee_id",
            "reviewer",
            "reviewer_id",
            "due_date",
            "comments_count",
        ]

    def get_assignee(self, obj):
        if not obj.assignee:
            return None

        return {
            "id": obj.assignee.id,
            "email": obj.assignee.email,
            "fullname": obj.assignee.fullname,
        }

    def get_reviewer(self, obj):
        if not obj.reviewer:
            return None

        return {
            "id": obj.reviewer.id,
            "email": obj.reviewer.email,
            "fullname": obj.reviewer.fullname,
        }

    def get_comments_count(self, obj):
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(
        source="author.fullname",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "created_at",
            "author",
            "content",
        ]
        read_only_fields = [
            "created_at",
            "author",
        ]