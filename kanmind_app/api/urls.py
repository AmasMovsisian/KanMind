from django.urls import path
from kanmind_app.api import views

urlpatterns = [
    # Boards
    path("boards/", views.BoardListCreateView.as_view(), name="board-list-create"),
    path("boards/<int:pk>/", views.BoardDetailView.as_view(), name="board-detail"),

    # Tasks
    path("tasks/assigned-to-me/", views.TasksAssignedToMeView.as_view(), name="tasks-assigned"),
    path("tasks/reviewing/", views.TasksReviewingView.as_view(), name="tasks-reviewing"),
    path("tasks/", views.TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task-detail"),


    # Comments (GET + POST)
    path("tasks/<int:task_id>/comments/", views.CommentView.as_view(), name="task-comments"),

    # Comments (DELETE)
    path("tasks/<int:task_id>/comments/<int:comment_id>/",views.CommentView.as_view(),name="task-comment-delete"),
]