import typing


def get_filtered_object(obj, filter_keys: typing.List[str] = [], include_private=False):
    state = obj.__dict__.copy()
    keys = list(state.keys())

    for key in keys:
        if state[key] is None or key in filter_keys:
            del state[key]
        elif key.startswith('_'):
            if include_private:
                val = state[key]
                del state[key]
                state[key[1:]] = val
            else:
                del state[key]

    return state
