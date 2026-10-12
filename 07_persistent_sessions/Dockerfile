FROM postgres:17-alpine

# Set environment variables for PostgreSQL
ENV POSTGRES_USER=agent_user
ENV POSTGRES_PASSWORD=agent_password
ENV POSTGRES_DB=agent_sessions

# Expose PostgreSQL port
EXPOSE 5432

# Use the default postgres entrypoint and command
CMD ["postgres"]
