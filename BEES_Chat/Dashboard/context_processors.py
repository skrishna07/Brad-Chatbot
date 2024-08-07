# In your context_processors.py

def user_role(request):
    role = None
    if request.user.is_authenticated:
        if request.user.groups.filter(name='admin').exists():
            role = 'admin'
        elif request.user.groups.filter(name='user').exists():
            role = 'user'
        # Add more conditions as per your roles

    return {'user_role': role}
