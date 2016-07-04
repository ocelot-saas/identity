"""Schema for the identity APIs objects."""

USER_CREATION_DATA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'User creation data',
    'description': 'A small set of data required to create a user, such as email, password etc.',
    'type': 'object',
    'properties': {
        'name': {
            'description': 'The user\'s human name',
            'type': 'string'
        },
        'emailAddress': {
            'description': 'The user\'s unique email address',
            'type': 'string'
        },
        'password': {
            'description': 'The password',
            'type': 'string'
        }
    },
    'required': ['name', 'emailAddress', 'password'],
}

USER = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'User',
    'description': 'Externally visible user info',
    'type': 'object',
    'properties': {
        'externalId': {
            'description': 'Externally visible id',
            'type': 'string'
        },
        'name': {
            'description': 'The user\'s human name',
            'type': 'string'
        },
        'timeJoinedTs': {
            'description': 'The time the user joined, in UTC',
            'type': 'integer'
        }
    },
    'required': ['externalId', 'name', 'timeJoinedTs']
}

AUTH_TOKEN = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'AuthToken',
    'description': 'The authentication token',
    'type': 'object',
    'properties': {
        'token': {
            'description': 'An opaque string, the actual token',
            'type': 'string'
        },
        'expiryTimeTs': {
            'description': 'The time the token expires, in UTC',
            'type': 'integer'
        }
    },
    'required': ['token', 'expiryTimeTs']
}

USERS_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Users resouces response',
    'description': 'Response from the users resource',
    'type': 'object',
    'properties': {
        'user': USER,
        'authToken': AUTH_TOKEN
    },
    'required': ['user', 'authToken']
}

CHECK_EMAIL_ADDRESS_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Check email address resource response',
    'description': 'Response from the check email address resource',
    'type': 'object',
    'properties': {
        'inUse': {
            'description': 'Whether the email address is in use or not',
            'type': 'boolean'
        }
    },
    'required': ['inUse']
}
