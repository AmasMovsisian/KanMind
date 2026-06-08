from rest_framework import serializers
from kanmind_app.models import Board, Task, Comment
from django.contrib.auth import get_user_model

User = get_user_model()



class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for Board model used for list and create operations.

    Provides aggregated statistics such as member count, task counts,
    and high-priority task metrics. Also supports assigning members on creation.
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
        Returns the total number of members assigned to the board.
        """
        return obj.members.count()

    def get_ticket_count(self, obj):
        """
        Returns the total number of tasks associated with the board.
        """
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """
        Returns the number of tasks with status 'to-do'.
        """
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        """
        Returns the number of tasks marked with high priority.
        """
        return obj.tasks.filter(priority="high").count()

    def create(self, validated_data):
        """
        Creates a new board instance and assigns members if provided.
        The requesting user is automatically set as the board owner.
        """
        members = validated_data.pop("members", [])
        user = self.context["request"].user
        board = Board.objects.create(owner=user, **validated_data)
        board.members.set(members)
        return board



class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Board representation.

    Includes full member list and all tasks belonging to the board.
    """

    owner_id = serializers.ReadOnlyField(source="owner.id")
    members = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]

    def get_members(self, obj):
        """
        Returns a structured list of all board members including the owner.
        """
        members = [
            {"id": obj.owner.id, "email": obj.owner.email, "fullname": obj.owner.fullname}
        ]
        for member in obj.members.exclude(id=obj.owner.id):
            members.append(
                {"id": member.id, "email": member.email, "fullname": member.fullname}
            )
        return members

    def get_tasks(self, obj):
        """
        Returns serialized task data for all tasks associated with the board.
        """
        from kanmind_app.api.serializers import TaskSerializer
        return TaskSerializer(obj.tasks.all(), many=True).data



class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model used for create, update, and retrieval operations.

    Supports nested representation of assignee and reviewer as well as
    writable primary key fields for assignment.
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
        Returns a lightweight representation of the assigned user.
        """
        if not obj.assignee:
            return None
        return {"id": obj.assignee.id, "email": obj.assignee.email, "fullname": obj.assignee.fullname}

    def get_reviewer(self, obj):
        """
        Returns a lightweight representation of the reviewer user.
        """
        if not obj.reviewer:
            return None
        return {"id": obj.reviewer.id, "email": obj.reviewer.email, "fullname": obj.reviewer.fullname}

    def get_comments_count(self, obj):
        """
        Returns the number of comments associated with the task.
        """
        return obj.comments.count()



class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.

    Provides read-only author representation and handles comment content creation.
    """

    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]
        read_only_fields = ["created_at", "author"]