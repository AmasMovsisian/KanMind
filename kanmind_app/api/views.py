from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from kanmind_app.models import Board, Task, Comment
from kanmind_app.api.serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    TaskSerializer,
    CommentSerializer
)
from kanmind_app.api.permissions import IsAuthenticatedOr401


class BoardListCreateView(APIView):
    permission_classes = [IsAuthenticatedOr401]

    def get(self, request):
        boards = Board.objects.filter(
            Q(owner=request.user) | Q(members=request.user)
        ).distinct()

        return Response(BoardSerializer(boards, many=True).data)

    def post(self, request):
        serializer = BoardSerializer(data=request.data)

        if serializer.is_valid():
            board = serializer.save(owner=request.user)
            board.members.add(request.user)

            return Response(
                BoardSerializer(board).data,
                status=201
            )

        return Response(serializer.errors, status=400)


class BoardDetailView(APIView):
    permission_classes = [IsAuthenticatedOr401]

    def get_object(self, pk):
        return get_object_or_404(Board, pk=pk)

    def check_access(self, board, user):
        return board.owner == user or user in board.members.all()

    def get(self, request, pk):
        board = self.get_object(pk)

        if not self.check_access(board, request.user):
            return Response({"detail": "Forbidden"}, status=403)

        return Response(BoardDetailSerializer(board).data)

    def patch(self, request, pk):
        board = self.get_object(pk)

        if not self.check_access(board, request.user):
            return Response({"detail": "Forbidden"}, status=403)

        serializer = BoardSerializer(
            board,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                BoardDetailSerializer(board).data
            )

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        board = self.get_object(pk)

        if board.owner != request.user:
            return Response(
                {"detail": "Only owner can delete"},
                status=403
            )

        board.delete()
        return Response(status=204)


class TasksAssignedToMeView(APIView):
    permission_classes = [IsAuthenticatedOr401]

    def get(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        return Response(TaskSerializer(tasks, many=True).data)


class TasksReviewingView(APIView):
    permission_classes = [IsAuthenticatedOr401]

    def get(self, request):
        tasks = Task.objects.filter(reviewer=request.user)
        return Response(TaskSerializer(tasks, many=True).data)


class TaskCreateView(APIView):
    permission_classes = [IsAuthenticatedOr401]

    def post(self, request):
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            board = serializer.validated_data["board"]

            if board.owner != request.user and request.user not in board.members.all():
                return Response(
                    {"detail": "Forbidden"},
                    status=403
                )

            assignee = serializer.validated_data.get("assignee")
            reviewer = serializer.validated_data.get("reviewer")

            def is_member(user):
                return user == board.owner or user in board.members.all()

            if assignee and not is_member(assignee):
                return Response(
                    {"assignee": "Must be board member"},
                    status=400
                )

            if reviewer and not is_member(reviewer):
                return Response(
                    {"reviewer": "Must be board member"},
                    status=400
                )

            task = serializer.save(created_by=request.user)

            return Response(
                TaskSerializer(task).data,
                status=201
            )

        return Response(serializer.errors, status=400)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticatedOr401]

    def get_object(self, pk):
        return get_object_or_404(Task, pk=pk)

    def check_access(self, task, user):
        board = task.board
        return board.owner == user or user in board.members.all()

    def get(self, request, pk):
        task = self.get_object(pk)

        if not self.check_access(task, request.user):
            return Response({"detail": "Forbidden"}, status=403)

        return Response(TaskSerializer(task).data)

    def patch(self, request, pk):
        task = self.get_object(pk)

        if not self.check_access(task, request.user):
            return Response({"detail": "Forbidden"}, status=403)

        if "board" in request.data:
            return Response(
                {"detail": "Board cannot be changed"},
                status=400
            )

        serializer = TaskSerializer(
            task,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        task = self.get_object(pk)

        if task.created_by != request.user and task.board.owner != request.user:
            return Response({"detail": "Forbidden"}, status=403)

        task.delete()
        return Response(status=204)


class CommentView(APIView):
    permission_classes = [IsAuthenticatedOr401]

    def get_task(self, task_id):
        return get_object_or_404(Task, id=task_id)

    def check_access(self, task, user):
        board = task.board
        return board.owner == user or user in board.members.all()

    def get(self, request, task_id):
        task = self.get_task(task_id)

        if not self.check_access(task, request.user):
            return Response({"detail": "Forbidden"}, status=403)

        comments = task.comments.all().order_by("created_at")

        return Response(
            CommentSerializer(comments, many=True).data
        )

    def post(self, request, task_id):
        task = self.get_task(task_id)

        if not self.check_access(task, request.user):
            return Response({"detail": "Forbidden"}, status=403)

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            comment = serializer.save(
                task=task,
                author=request.user
            )

            return Response(
                CommentSerializer(comment).data,
                status=201
            )

        return Response(serializer.errors, status=400)

    def delete(self, request, task_id, comment_id):
        task = self.get_task(task_id)

        if not self.check_access(task, request.user):
            return Response({"detail": "Forbidden"}, status=403)

        comment = get_object_or_404(Comment, id=comment_id, task=task)

        if comment.author != request.user:
            return Response({"detail": "Forbidden"}, status=403)

        comment.delete()
        return Response(status=204)