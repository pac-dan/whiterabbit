# Running the Momentum Clips studio

The website is a Flask/Jinja application with plain JavaScript. There is no Node build step. Customers book as guests; public registration and the legacy account booking routes remain retired.

## Catalogue and payments

Sign in at `/auth/login`, then open `/admin/`. Packages, Films and Reviews support create, edit, hide/publish and delete. Package prices are EUR and are the exact prices sent to Stripe. Existing orders keep the price/name snapshot they purchased. Packages with orders cannot be deleted; deactivate them instead. Poster URLs must use HTTPS. Only publish real customer films/reviews with permission.

Each package can have its own Calendly event URL. Choose an event that actually matches its duration. If no calendar is set, the paid customer is directed to the team to arrange dates; no unrelated default event is substituted.

Set `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` in the deployment environment. Register `/payment/webhook` with Stripe for `checkout.session.completed` and `checkout.session.async_payment_succeeded`. The signature, order reference, currency, amount and paid status must all match. The browser return and webhook use the same idempotent verification function. Discounts are not enabled because the charged amount must match the purchased package snapshot. No card details pass through this app. See https://docs.stripe.com/checkout/fulfillment .

Missing or failing payment configuration sends visitors to contact with an honest explanation. It never unlocks a waiver. Existing legacy orders remain visible to staff; old unbound confirmation URLs are deliberately rejected. Staff should help customers with those older links after checking their payment in Stripe.

## Booking, waivers and delivery

Guest links are signed and bound to one order. A signed waiver is stored and linked to that order. Opening a return page is not proof of a Calendly booking: staff confirms the actual date/time in Bookings (UTC). Cancellation in this admin does not issue a financial refund; refunds remain in Stripe.

To deliver films, paste HTTPS links, one per line. The site records completion only after the delivery email succeeds. On email failure the links remain saved and the order remains incomplete; retry after fixing mail settings. A repeated submit does not resend unless Resend is checked. SMTP acceptance is not a guarantee of inbox delivery.

The walk-in waiver is at `/waiver/standalone`. Its legal text is unchanged. Signing it does not create or confirm a booking.

## Enquiries, subscribers and staff access

Contact submissions are stored in Enquiries. Staff can mark them resolved and reply using the email link. The form does not claim an email notification was sent; check the inbox regularly. Newsletter subscriptions are visible in Subscribers; no campaign-sending integration is supplied. Social publishing automation remains unconnected; Integrations links to the real channels and reports configuration presence only.

Configure `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME` and `MAIL_PASSWORD` for password recovery and delivery. Missing credentials fail safely. Password-reset links expire after an hour and become invalid when the password changes. There are no default admin credentials.

Create the first administrator against the intended persistent database using:

```powershell
C:/Users/Dan/dan_file/white-rabbit/.venv/Scripts/python.exe -m flask --app wsgi:app create-admin --email OWNER_EMAIL --name OWNER_NAME
```

This command prompts privately for a password and confirmation. Do not put a password in source control or a command argument. Run it in an interactive shell connected to the intended database; it refuses to replace an existing account.

## Preview and production dependencies

Use a persistent, separately configured preview database for editable admin/booking review. SQLite at `/tmp/preview.db` in Vercel is disposable, starts empty and is not a durable booking database. This implementation adds only the `package_schedules` and `inquiries` tables; existing tables and records are preserved. Startup uses the existing `db.create_all` workflow. Do not run destructive test fixtures against a real database.

Run `python -m flask --app wsgi:app service-readiness` to print configuration presence without secrets. It does not authenticate to providers. Production security still requires a real SECRET_KEY and DATABASE_URL; the existing configuration also requires mail and Anthropic variables. No project settings are changed by this task.

## Reproducible local verification

`python scripts/check_functional_site.py commerce`, `admin`, `forms`, and `regressions` save actual receipts under `.runs/2026-10-27-functional-site/evidence/`. Provider calls in unit tests are mocked: they do not prove a live charge or delivery.

`python scripts/serve_functional_check.py` serves an isolated in-memory fixture at https://127.0.0.1:5003 with production CSP/CSRF/secure cookies, a locally generated certificate, test-only staff credentials, seeded paid orders and suppressed SMTP. Payment creation is disabled. `node scripts/check_functional_site.mjs` checks customer/admin actions at four sizes and saves screenshots. The fixture must be restarted between complete runs to reset its data and normal rate limits. It is never deployed as the application entry point.

All production promotion remains the owner's decision. Preview build success, authenticated preview inspection, provider verification and production verification are separate claims.
