
#Used as context for base template
def global_context(request):
    return {
        'user' : request.user
    }