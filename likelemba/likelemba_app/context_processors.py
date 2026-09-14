from .models import Notification


def notifications_admin(request):
    if not request.user.is_authenticated:
        return {
            'notifications_non_lues': 0
        }

    if getattr(request.user, 'role', None) != 'ADMIN':
        return {
            'notifications_non_lues': 0
        }

    nombre_notification = Notification.objects.filter(
        destinataire=request.user,
        lu=False
    ).count()

    return {
        'notifications_non_lues': nombre_notification
    }