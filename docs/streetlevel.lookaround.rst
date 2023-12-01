streetlevel.lookaround: Apple Look Around
=========================================

Support for Apple Look Around. Note that, unlike with the other providers, the library
does not automatically stitch the images - the side faces appear to be equirectangular with some overlap,
but the top and bottom face are ... something else. (Please contact me if you know which projection is being used.)

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
    .. autoclass:: streetlevel.lookaround.panorama.CoverageType
      :members:
      :member-order: bysource
    .. autoclass:: streetlevel.lookaround.lookaround.Face
      :members:
      :member-order: bysource
    .. autoclass:: streetlevel.lookaround.panorama.LookaroundPanorama
      :members:

Authentication
--------------
    .. autoclass:: streetlevel.lookaround.auth.Authenticator
      :members:
