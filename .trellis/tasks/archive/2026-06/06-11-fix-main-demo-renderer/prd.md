# Fix main demo renderer fallback

## Goal

Make `privacy-display/main.py demo` runnable on machines where `moderngl` is installed but cannot create a standalone OpenGL context.

## What I already know

* The demo fails in `GPURenderer._init_gl()` with `Exception: cannot choose pixel format`.
* `create_renderer()` only falls back to `SoftwareRenderer` on `ImportError`, so runtime GL context failures escape.
* The intended behavior is already documented as "GPU rendering + software fallback".

## Requirements

* Keep the existing GPU-first behavior when a usable OpenGL context exists.
* Fall back to `SoftwareRenderer` when GPU renderer initialization fails.
* Avoid changing privacy algorithm behavior.
* Add a focused regression test for the fallback path.

## Acceptance Criteria

* [ ] `privacy-display/main.py demo` completes in the current environment.
* [ ] Unit tests pass.
* [ ] Renderer fallback test covers a non-ImportError GPU initialization failure.

## Out of Scope

* Replacing OpenGL with Metal/EGL.
* Implementing driver-level or compositor-level display injection.
* Changing mask, noise, or timing algorithms.

## Technical Notes

* Affected module: `privacy-display/src/gpu/renderer.py`.
* Existing tests live under `privacy-display/tests/`.
