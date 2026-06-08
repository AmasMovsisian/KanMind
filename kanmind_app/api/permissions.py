from rest_framework.permissions import BasePermission
from kanmind_app.models import Board



class IsAuthenticatedOr401(BasePermission):
    """
    Permission class that allows access only to authenticated users.

    Returns False (unauthorized) if the user is not logged in.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated



class IsBoardMember(BasePermission):
    """
    Permission class that restricts access to board members only.

    A user is considered a board member if they are either:
    - The owner of the board
    - Included in the board's members list

    Supports both object-level and request-level validation.
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks whether the requesting user has access to a specific board object.
        """
        return obj.owner == request.user or request.user in obj.members.all()

    def has_permission(self, request, view):
        """
        Validates whether the requesting user has access based on the provided board ID.

        If a board ID is included in the request data, the user must be either
        the owner or a member of that board.
        """
        board_id = request.data.get("board")
        user = request.user
        if not board_id:
            return True
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return False
        return board.owner == user or user in board.members.all()



class IsBoardOwner(BasePermission):
    """
    Permission class that allows access only to the owner of a board or object.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user