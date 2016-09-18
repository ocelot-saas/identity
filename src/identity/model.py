"""Model actions for the identity service."""

import sqlalchemy as sql


_metadata = sql.MetaData(schema='identity')

_user = sql.Table(
    'user', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('auth0_user_id_hash', sql.String(64), index=True),
    sql.Column('time_joined', sql.DateTime(timezone=True)))


class Error(Exception):
    pass


class UserAlreadgExistsError(Error):
    pass


class UserDoesNotExistError(Error):
    pass


class Model(object):
    def __init__(self, the_clock, sql_engine):
        self._the_clock = the_clock
        self._sql_engine = sql_engine

    def create_user(self, auth0_user_id_hash):
        right_now = self._the_clock.now()

        with self._sql_engine.begin() as conn:
            try:
                create_user = _user \
                    .insert() \
                    .returning(_user.c.id, _user.c.time_joined) \
                    .values(auth0_user_id_hash=auth0_user_id_hash, time_joined=right_now)
                
                result = conn.execute(create_user)
                user_row = result.fetchone()

                if user_row is None:
                    raise Error('Could not insert user')
                
                result.close()
            except sql.exc.IntegrityError as e:
                raise UserAlreadgExistsError() from e

        return {
            'id': user_row['id'],
            'timeJoinedTs': int(user_row['time_joined'].timestamp())
        }

    def get_user(self, auth0_user_id_hash):
        with self._sql_engine.begin() as conn:
            fetch_by_auth0_user_id_hash = sql.sql \
                .select([_user]) \
                .where(_user.c.auth0_user_id_hash == auth0_user_id_hash)

            result = conn.execute(fetch_by_auth0_user_id_hash)
            user_row = result.fetchone()
            result.close()

            if user_row is None:
                raise UserDoesNotExistError()

        return {
            'id': user_row['id'],
            'timeJoinedTs': int(user_row['time_joined'].timestamp())
        }
