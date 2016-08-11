"""Schema for the identity APIs objects."""

AUTH0_USER_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Auth0 user response',
    'description': 'JSON returned by Auth0 to describe a particular user',
    'type': 'object',
    'properties': {
        'user_id': {
            'description': 'The unique id assigned by Auth0 for this user',
            'type': 'string',
        },
        'name': {
            'description': 'The name of the user, as best extracted by Auth0',
            'type': 'string',
        },
        'picture': {
            'description': 'An URL with a picture for the user',
            'type': 'string',
        }
    },
    'required': ['user_id', 'name', 'picture'],
    'additionalProperties': True
}

USER = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'User',
    'description': 'Externally visible user info',
    'type': 'object',
    'properties': {
        'id': {
            'description': 'The id of the user',
            'type': 'integer'
        },
        'timeJoinedTs': {
            'description': 'The time the user joined, in UTC',
            'type': 'integer'
        },
        'name': {
            'description': 'The user\'s human name',
            'type': 'string'
        },
        'pictureUrl': {
            'description': 'An URL with a picture for the user',
            'type': 'string',
        }
    },
    'required': ['id', 'timeJoinedTs', 'name', 'pictureUrl'],
    'addtionalProperties': False
}

USER_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Users resouces response',
    'description': 'Response from the user resource',
    'type': 'object',
    'properties': {
        'user': USER,
    },
    'required': ['user'],
    'additionalProperties': False
}
