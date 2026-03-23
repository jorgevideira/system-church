# API Dependency Injection Functions

# Example Function

def get_db():
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()