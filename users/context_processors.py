def profile_context(request):
    """Make the current user's profile and currency symbol available in every template."""
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        return {
            'user_profile': profile,
            'currency_symbol': profile.currency_symbol if profile else '₹',
            'dark_mode': profile.dark_mode if profile else False,
        }
    return {'user_profile': None, 'currency_symbol': '₹', 'dark_mode': False}
