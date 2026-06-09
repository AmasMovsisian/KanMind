from rest_framework import serializers
from kanmind_app.models import Board, Task, Comment
from django.contrib.auth import get_user_model

User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for board creation and listing.
    """

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
        """
        Returns number of members in the board.
        """
        return obj.members.count()

    def get_ticket_count(self, obj):
        """
        Returns total number of tasks in the board.
        """
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """
        Returns number of tasks with status 'to-do'.
        """
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        """
        Returns number of high priority tasks in the board.
        """
        return obj.tasks.filter(priority="high").count()

    def create(self, validated_data):
        """
        Creates a new board and assigns members.
        """
        members = validated_data.pop("members", [])
        board = Board.objects.create(**validated_data)
        board.members.set(members)
        return board

    def update(self, instance, validated_data):
        """
        Updates board fields and optionally replaces members list.
        """
        members = validated_data.pop("members", None)

        instance.title = validated_data.get("title", instance.title)
        instance.save()

        if members is not None:
            instance.members.set(members)

        return instance


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed board representation.
    """

    owner_id = serializers.ReadOnlyField(source="owner.id")
    members = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]

    def get_members(self, obj):
        """
        Returns list of board members including owner.
        """
        members = [
            {
                "id": obj.owner.id,
                "email": obj.owner.email,
                "fullname": obj.owner.fullname
            }
        ]

        for member in obj.members.exclude(id=obj.owner.id):
            members.append(
                {
                    "id": member.id,
                    "email": member.email,
                    "fullname": member.fullname
                }
            )

        return members

    def get_tasks(self, obj):
        """
        Returns all tasks belonging to the board.
        """
        from kanmind_app.api.serializers import TaskSerializer
        return TaskSerializer(obj.tasks.all(), many=True).data


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for board update response.
    """

    owner_data = serializers.SerializerMethodField()
    members_data = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data"]

    def get_owner_data(self, obj):
        """
        Returns structured owner information.
        """
        return {
            "id": obj.owner.id,
            "email": obj.owner.email,
            "fullname": obj.owner.fullname,
        }

    def get_members_data(self, obj):
        """
        Returns structured list of board members.
        """
        return [
            {
                "id": member.id,
                "email": member.email,
                "fullname": member.fullname,
            }
            for member in obj.members.all()
        ]


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for task operations.
    """

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
        """
        Returns serialized assignee user.
        """
        if not obj.assignee:
            return None

        return {
            "id": obj.assignee.id,
            "email": obj.assignee.email,
            "fullname": obj.assignee.fullname
        }

    def get_reviewer(self, obj):
        """
        Returns serialized reviewer user.
        """
        if not obj.reviewer:
            return None

        return {
            "id": obj.reviewer.id,
            "email": obj.reviewer.email,
            "fullname": obj.reviewer.fullname
        }

    def get_comments_count(self, obj):
        """
        Returns number of comments on the task.
        """
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comment operations.
    """

    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]
        read_only_fields = ["created_at", "author"]