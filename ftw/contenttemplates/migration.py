PROFILE_ID = 'profile-ftw.contenttemplates:default'


def run_typeinfo_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
