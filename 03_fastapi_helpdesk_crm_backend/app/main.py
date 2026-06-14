from fastapi import FastAPI

from app.api import auth, tickets, users

app = FastAPI(
    title="Helpdesk CRM API",
    description="Backend for support tickets, comments, roles and JWT auth.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tickets.router)
