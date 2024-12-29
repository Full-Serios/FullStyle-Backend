import redis
from datetime import timedelta

# Configuración de Redis
redis_client = redis.StrictRedis(host="localhost", port=5000, db=0, decode_responses=True)

class TokenBlockListModel:
    @staticmethod
    def block_token(jti, expires_in):
        #Bloquea un token con un tiempo de expiración
        redis_client.setex(jti, timedelta(seconds=expires_in), "blocked")

    @staticmethod
    def is_token_blocked(jti):
        #Verifica si un token está bloqueado
        return redis_client.exists(jti) == 1
