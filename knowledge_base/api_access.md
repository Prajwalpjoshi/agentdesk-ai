# API Access Troubleshooting

## Symptoms
Users may receive HTTP 401 Unauthorized, HTTP 403 Forbidden, or connection timeout errors when accessing an API.

## Troubleshooting
- HTTP 401: Verify that the API token is present, valid, and not expired.
- HTTP 403: Check the user's role and required API permissions.
- HTTP 429: Check rate limits and retry after the specified interval.
- Connection timeout: Check service availability, network connectivity, and endpoint configuration.
- HTTP 5xx: Check the service status and review application logs.

## Escalation
If the issue continues, record the endpoint, timestamp, HTTP status code, and request ID in a support ticket. Never include passwords, API tokens, or other secrets.
