def _try_get(accessor):
    try:
        return accessor()
    except IndexError:
        return None
    except TypeError:
        return None
