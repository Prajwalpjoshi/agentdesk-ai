# Service Outage Troubleshooting

## Initial checks
Check the service health endpoint, recent deployment status, and available application logs before declaring an outage.

## Common symptoms
- HTTP 503: The service may be unavailable or overloaded.
- HTTP 500: The service encountered an internal error.
- High response latency: Check resource usage, dependency health, and recent changes.
- Repeated connection failures: Verify network connectivity and upstream service health.

## Incident handling
Record the affected service, approximate start time, observed errors, and impact. Escalate confirmed incidents to the responsible support team.

## Demo environment
AgentDesk uses simulated service-status data. Its responses do not indicate the health of any real production system.
