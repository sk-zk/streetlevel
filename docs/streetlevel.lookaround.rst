streetlevel.lookaround: Apple Look Around
=========================================

Support for Apple Look Around. Note that, unlike with the other providers, the library
does not automatically stitch the images as Look Around does not serve one image broken up into tiles,
but rather six faces which form a sort-of-but-not-really cubemap.

Panoramas can be rendered by creating spherical quadliterals (rectangles on the surface of a sphere) for each face, centered on
phi=0, theta=0. ``fov_s`` is the phi size (width), ``fov_h`` is the theta size (height), and ``cy`` is an additional offset
which must be subtracted from phi. The resulting geometry for the face is then rotated by the given Euler angles. (The API
returns several other parameters, but they do not appear to be in use.)

Finding panoramas
-----------------
    .. autofunction:: streetlevel.lookaround.get_coverage_tile
    .. autofunction:: streetlevel.lookaround.get_coverage_tile_async
    .. autofunction:: streetlevel.lookaround.get_coverage_tile_by_latlon
    .. autofunction:: streetlevel.lookaround.get_coverage_tile_by_latlon_async

Downloading panoramas
---------------------
    .. autofunction:: streetlevel.lookaround.get_panorama_face
    .. autofunction:: streetlevel.lookaround.download_panorama_face

Data classes and Enums
----------------------
    .. autoclass:: streetlevel.lookaround.panorama.CameraMetadata
      :members:
      :member-order: bysource
    .. autoclass:: streetlevel.lookaround.panorama.CoverageType
      :members:
      :member-order: bysource
    .. autoclass:: streetlevel.lookaround.lookaround.Face
      :members:
      :member-order: bysource
    .. autoclass:: streetlevel.lookaround.panorama.LookaroundPanorama
      :members:
    .. autoclass:: streetlevel.lookaround.panorama.LensProjection
      :members:
      :member-order: bysource
    .. autoclass:: streetlevel.lookaround.panorama.OrientedPosition
      :members:
      :member-order: bysource

Authentication
--------------
    .. autoclass:: streetlevel.lookaround.auth.Authenticator
      :members:
