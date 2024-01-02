streetlevel.lookaround: Apple Look Around
=========================================

Support for Apple Look Around.

Note that, unlike with the other providers, this library does not automatically stitch the panoramas
since 1) Look Around does not serve one image broken up into tiles, but six faces which form a
sort-of-but-not-really cubemap, and 2) its image format is somewhat inconvenient to work with. 
A function to create an equirectangular image out of the panorama faces is available, but not exactly fast,
so it is recommended to display the faces unmodified.

Panoramas can be rendered by creating a spherical rectangle (meaning a rectangle on the surface of a sphere) for each face, centered on
phi=0, theta=0. ``fov_s`` is the phi size (width), ``fov_h`` is the theta size (height), and ``cy`` is an additional offset
which must be subtracted from phi. The resulting geometry for the face is then rotated by the given Euler angles. (The API
returns several other parameters, but they do not appear to be in use.) 

Finding panoramas
-----------------
    .. autofunction:: streetlevel.lookaround.get_coverage_tile
    
    Usage sample: ::
    
      from streetlevel import lookaround
      
      panos = lookaround.get_coverage_tile(109775, 56716)
      print(f"""
      Got {len(panos)} panoramas. Here's one of them:
      ID: {panos[0].id}\t\tBuild ID: {panos[0].build_id}
      Latitude: {panos[0].lat}\tLongitude: {panos[0].lon}
      Capture date: {panos[0].date}
      """)
    
    .. autofunction:: streetlevel.lookaround.get_coverage_tile_async
    .. autofunction:: streetlevel.lookaround.get_coverage_tile_by_latlon
    
     Usage sample: ::
    
      from streetlevel import lookaround
      
      panos = lookaround.get_coverage_tile_by_latlon(23.53239040648735, 121.5068719584602)
      print(f"""
      Got {len(panos)} panoramas. Here's one of them:
      ID: {panos[0].id}\t\tBuild ID: {panos[0].build_id}
      Latitude: {panos[0].lat}\tLongitude: {panos[0].lon}
      Capture date: {panos[0].date}
      """)
    
    .. autofunction:: streetlevel.lookaround.get_coverage_tile_by_latlon_async

Downloading panoramas
---------------------
    .. autofunction:: streetlevel.lookaround.get_panorama_face
    
    Usage sample: ::
    
      from streetlevel import lookaround
      
      panos = lookaround.get_coverage_tile_by_latlon(46.52943, 10.45544)
      
      auth = lookaround.Authenticator()
      faces = []
      zoom = 0
      for faceIdx in range(0, 6):
          face = lookaround.get_panorama_face(panos[0], faceIdx, zoom, auth)
          faces.append(face)
 
    .. autofunction:: streetlevel.lookaround.download_panorama_face
    
    Usage sample: ::
    
      from streetlevel import lookaround
      
      panos = lookaround.get_coverage_tile_by_latlon(46.52943, 10.45544)
      
      auth = lookaround.Authenticator()
      zoom = 0
      for face in range(0, 6):
          lookaround.download_panorama_face(panos[0], f"{panos[0].id}_{face}_{zoom}.heic",
            face, zoom, auth)

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

Reprojection
------------
    .. autofunction:: streetlevel.lookaround.reproject.to_equirectangular
    
    Usage sample: ::
      
      from streetlevel import lookaround

      panos = lookaround.get_coverage_tile_by_latlon(-42.907473, 171.559290)
      pano = panos[0]

      auth = lookaround.Authenticator()
      faces = []
      zoom = 2
      for faceIdx in range(0, 6):
          face_heic = lookaround.get_panorama_face(pano, faceIdx, zoom, auth)
          # Convert the face to a PIL image here.
          # This step is left to the user of the library, so that you can
          # choose whichever library performs best on your machine.
          faces.append(face)
      
      result = lookaround.to_equirectangular(faces, pano.camera_metadata)
      result.save(f"{pano.id}_{zoom}.jpg", options={"quality": 100})

Authentication
--------------
    .. autoclass:: streetlevel.lookaround.auth.Authenticator
      :members:
