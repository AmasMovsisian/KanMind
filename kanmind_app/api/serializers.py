from rest_framework import serializers
from kanmind_app.models import Board, Task, Comment
from django.contrib.auth import get_user_model


User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )

    owner_id = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
        ]

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        board = Board.objects.create(**validated_data)
        board.members.set(members)

        return board


class TaskSerializer(serializers.ModelSerializer):

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
            "reviewer",
            "due_date",
            "created_by",
        ]
        read_only_fields = ["created_by"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]
        read_only_fields = ["author", "created_at"]

    def validate_content(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Content cannot be empty")
        return value
