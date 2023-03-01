from fastapi import FastAPI

from v1_app.api.router import authentication_router, booking_router, event_router, admin_evet_router, profile_router

app = FastAPI()

app.include_router(authentication_router.router)
app.include_router(profile_router.router)
app.include_router(booking_router.router)
app.include_router(event_router.router)
app.include_router(admin_evet_router.router)


