

def jwt_guard(authorization: str = Header(...)) -> TokenDTO:
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    
    token = authorization[len(prefix):]
    try:
        header = jwt.get_unverified_header(token)
        kid = header['kid']
        public_key = get_key_from_jwks(kid)

        decoded_token = jwt.decode(token, public_key, audience="account")
        return TokenDTO(**decoded_token)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
        
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    except ValidationError as e:
        raise HTTPException(status_code=401, detail="Token payload validation failed")
