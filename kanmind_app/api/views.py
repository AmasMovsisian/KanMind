from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from kanmind_app.models import Board, Task, Comment
from kanmind_app.api.serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
    TaskSerializer,
    CommentSerializer
)


class BoardListCreateView(APIView):
    """
    API endpoint for retrieving and creating boards.
    """

    def get(self, request):
        """
        Retrieves all boards accessible to the authenticated user.
        """
        boards = Board.objects.filter(
            Q(owner=request.user) | Q(members=request.user)
        ).distinct()
        return Response(BoardSerializer(boards, many=True).data)

    def post(self, request):
        """
        Creates a new board for the authenticated user and adds the creator as a member.
        """
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
    """
    API endpoint for retrieving, updating and deleting a single board.
    """


    def get_object(self, pk):
        """
        Retrieves a board instance by its primary key.
        """
        return get_object_or_404(Board, pk=pk)

    def check_access(self, board, user):
        """
        Checks whether a user has access to the given board.
        """
        return board.owner == user or user in board.members.all()

    def get(self, request, pk):
        """
        Retrieves a single board with detailed representation.
        """
        board = self.get_object(pk)
        if not self.check_access(board, request.user):
            return Response({"detail": "Forbidden"}, status=403)
        return Response(BoardDetailSerializer(board).data)

    def patch(self, request, pk):
        """
        Partially updates a board and returns the updated board data.
        """
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
            board.refresh_from_db()
            return Response(BoardUpdateSerializer(board).data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        """
        Deletes a board if the requesting user is the owner.
        """
        board = self.get_object(pk)
        if board.owner != request.user:
            return Response({"detail": "Only owner can delete"}, status=403)
        board.delete()
        return Response(status=204)


class TasksAssignedToMeView(APIView):
    """
    API endpoint for retrieving tasks assigned to the current user.
    """

    def get(self, request):
        """
        Retrieves all tasks assigned to the authenticated user.
        """
        tasks = Task.objects.filter(assignee=request.user)
        return Response(TaskSerializer(tasks, many=True).data)


class TasksReviewingView(APIView):
    """
    API endpoint for retrieving tasks the current user is reviewing.
    """

    def get(self, request):
        """
        Retrieves all tasks where the authenticated user is set as reviewer.
        """
        tasks = Task.objects.filter(reviewer=request.user)
        return Response(TaskSerializer(tasks, many=True).data)


class TaskCreateView(APIView):
    """
    API endpoint for creating a task inside a board.
    """

    def post(self, request):
        """
        Creates a new task inside a board if the user has access.
        """
        serializer = TaskSerializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            board = serializer.validated_data["board"]
            if (
                request.user != board.owner
                and request.user not in board.members.all()
            ):
                return Response({"detail": "Forbidden"}, status=403)
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
            return Response(TaskSerializer(task).data, status=201)
        return Response(serializer.errors, status=400)


class TaskDetailView(APIView):
    """
    API endpoint for retrieving, updating and deleting a task.
    """

    def get_object(self, pk):
        """
        Retrieves a task instance by its primary key.
        """
        return get_object_or_404(Task, pk=pk)

    def check_access(self, task, user):
        """
        Checks whether a user has access to a task via board membership.
        """
        board = task.board
        return board.owner == user or user in board.members.all()

    def get(self, request, pk):
        """
        Retrieves a single task.
        """
        task = self.get_object(pk)
        if not self.check_access(task, request.user):
            return Response({"detail": "Forbidden"}, status=403)
        return Response(TaskSerializer(task).data)

    def patch(self, request, pk):
        """
        Partially updates a task.
        """
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
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(TaskSerializer(task).data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        """
        Deletes a task if the user is allowed to do so.
        """
        task = self.get_object(pk)
        if (
            task.created_by != request.user
            and task.board.owner != request.user
        ):
            return Response({"detail": "Forbidden"}, status=403)
        task.delete()
        return Response(status=204)


class CommentListCreateView(APIView):
    """
    API endpoint for listing and creating comments on a task.
    """


    def get_task(self, task_id):
        """
        Retrieves a task by its ID.
        """
        return get_object_or_404(Task, id=task_id)

    def check_access(self, task, user):
        """
        Checks whether a user has access to a task via board membership.
        """
        board = task.board
        return board.owner == user or user in board.members.all()

    def get(self, request, task_id):
        """
        Retrieves all comments for a task.
        """
        task = self.get_task(task_id)
        if not self.check_access(task, request.user):
            return Response({"detail": "Forbidden"}, status=403)
        comments = task.comments.all().order_by("created_at")
        return Response(CommentSerializer(comments, many=True).data)

    def post(self, request, task_id):
        """
        Creates a new comment on a task.
        """
        task = self.get_task(task_id)
        if not self.check_access(task, request.user):
            return Response({"detail": "Forbidden"}, status=403)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(
                task=task,
                author=request.user
            )
            return Response(CommentSerializer(comment).data, status=201)
        return Response(serializer.errors, status=400)


class CommentDetailView(APIView):
    """
    API endpoint for retrieving and deleting a single comment.
    """

    def get_task(self, task_id):
        """
        Retrieves a task by ID.
        """
        return get_object_or_404(Task, id=task_id)

    def check_access(self, task, user):
        """
        Checks whether a user has access to a task via board membership.
        """
        board = task.board
        return board.owner == user or user in board.members.all()

    def get(self, request, task_id, comment_id):
        """
        Retrieves a single comment.
        """
        task = self.get_task(task_id)
        if not self.check_access(task, request.user):
            return Response({"detail": "Forbidden"}, status=403)
        comment = get_object_or_404(
            Comment,
            id=comment_id,
            task=task
        )
        return Response(CommentSerializer(comment).data)

    def delete(self, request, task_id, comment_id):
        """
        Deletes a comment if the requesting user is the author.
        """
        task = self.get_task(task_id)
        if not self.check_access(task, request.user):
            return Response({"detail": "Forbidden"}, status=403)
        comment = get_object_or_404(
            Comment,
            id=comment_id,
            task=task
        )
        if comment.author != request.user:
            return Response({"detail": "Forbidden"}, status=403)
        comment.delete()
        return Response(status=204)