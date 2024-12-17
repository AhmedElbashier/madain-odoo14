def get_default_faculty(ctx):
    '''
    Returns the current user's company's ID if it's a faculty. Otherwise, returns
    None.
    '''
    return (
        ctx.env.user.company_id.id
        
    )
