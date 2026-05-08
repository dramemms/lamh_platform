# apps/core/permissions.py

def has_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def is_admin(user):
    return user.is_authenticated and (
        getattr(user, "role", None) == "ADMIN" or user.is_superuser
    )


def is_supervisor(user):
    return user.is_authenticated and (
        getattr(user, "role", None) == "SUPERVISOR"
        or has_group(user, "Supervisor")
    )


def is_project_manager(user):
    return user.is_authenticated and (
        getattr(user, "role", None) == "PROJECT_MANAGER"
        or has_group(user, "ProjectManager")
    )


# Alias temporaire pour ne pas casser l’ancien code
def is_program_manager(user):
    return is_project_manager(user)


def is_tech_validator(user):
    return user.is_authenticated and (
        getattr(user, "role", None) == "TECH_VALIDATOR"
        or has_group(user, "TechValidator")
        or has_group(user, "TechnicalValidator")
    )


def is_data_manager(user):
    return user.is_authenticated and (
        getattr(user, "role", None) == "DATA_MANAGER"
        or has_group(user, "DataManager")
    )


def is_data_entry(user):
    return user.is_authenticated and (
        getattr(user, "role", None) == "DATA_ENTRY"
        or has_group(user, "DataEntry")
    )


def can_view_accidents(user):
    return user.is_authenticated


def can_create_accident(user):
    return user.is_authenticated and any([
        is_admin(user),
        is_supervisor(user),
        is_project_manager(user),
        is_tech_validator(user),
        is_data_entry(user),
    ])


def can_edit_accident(user):
    return user.is_authenticated and any([
        is_admin(user),
        is_supervisor(user),
        is_project_manager(user),
        is_tech_validator(user),
    ])


def can_tech_validate(user):
    if not user.is_authenticated:
        return False

    return any([
        is_admin(user),
        is_supervisor(user),
        is_tech_validator(user),
    ])


def can_program_validate(user):
    return user.is_authenticated and any([
        is_admin(user),
        is_project_manager(user),
    ])


def can_approve(user):
    return user.is_authenticated and is_admin(user)


def can_manage_users(user):
    return is_admin(user)


def filter_accidents_for_user(queryset, user):
    if not user.is_authenticated:
        return queryset.none()

    if is_admin(user) or is_project_manager(user):
        return queryset

    user_region = getattr(user, "region", None)

    if (is_supervisor(user) or is_tech_validator(user)) and user_region:
        return queryset.filter(region=user_region)

    if is_data_entry(user):
        return queryset.filter(created_by=user)

    return queryset.none()