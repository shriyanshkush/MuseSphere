from app.api.routes import auth, bookings, events, exhibitions, misc, payments
routers=[auth.router, exhibitions.router, events.router, bookings.router, payments.router, misc.router]
