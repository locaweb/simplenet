
class Auth(object)
    def auth(request):
        cas_ticket = request.query.get("ticket")
        if not cas_ticket:
            abort(403, "Null Authentication Ticket (CAS)")
        redis_db = RedisClient()
        auth_cache = redis_db.get_connection()
        m = hashlib.md5()
        m.update(cas_ticket)
        cas_hash = m.hexdigest()
        if (auth_cache.exists(cas_hash) == False):
            print "Not found " + cas_hash
            try:
                logger.info("Trying to validate CAS ticket '%s' on server '%s'" % (cas_ticket, servers[0]))
                user_info = CASClient(server=servers[0]).validate_ticket(ticket=cas_ticket, service=service)
            except CasError:
                logger.exception("CAS ticket validation failed")
                try:
                    logger.info("Trying to validate CAS-ticket '%s' on server '%s'" % (cas_ticket, servers[1]))
                    user_info = CASClient(server=servers[1]).validate_ticket(ticket=cas_ticket, service=service)
                except CasError:
                    logger.exception("CAS ticket validation failed")
                    abort(403, "Invalid Authentication Ticket (CAS)")
            auth_cache.hset(cas_hash, "user_info", user_info)
            auth_cache.expire(cas_hash, 60)
            request["authentication_info"] = user_info
            return f(*args, **kwargs)
        else:
            print "FOund " + cas_hash
            request["authentication_info"] = literal_eval(auth_cache.hget(cas_hash, "user_info"))
            return f(*args, **kwargs)

    def authorize(rolecfg=None, required_role=None):
        def proxy(f):
            def auth(*args, **kwargs):
                # TODO: Use CAS Authority for ACLs
                username = request["authentication_info"]["cn"][0].lower().replace(" ",".")
                if username not in rolecfg[required_role]:
                    abort(403, "Forbidden")
                return f(*args, **kwargs)
            return auth
        return proxy

class Load(Auth):
    pass
