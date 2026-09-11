# Production container build

The production image installs application dependencies from the committed `uv.lock` file.

The Docker build uses `uv sync --locked --no-dev --no-editable`, so a stale lockfile fails the image build instead of silently resolving a different dependency graph.

The final image contains only the runtime environment and application source. Development dependencies are excluded, and the application still runs as the existing non-root `app` user.
