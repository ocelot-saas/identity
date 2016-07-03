"""Schema for the identity APIs objects."""

USER_CREATION_DATA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Info required to create a user',
    'description': 'A small set of data required to create a user, such as email, password etc.',
    'type': 'object',
    'properties': {
        'name': {
            'description': 'The user\'s human name',
            'type': 'string'
        },
        'email_address': {
            'description': 'The user\'s unique email address',
            'type': 'string'
        },
        'password': {
            'description': 'The password',
            'type': 'string'
        }
    }
}
