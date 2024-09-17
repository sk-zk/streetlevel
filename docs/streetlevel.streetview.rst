streetlevel.streetview: Google Street View
==========================================

Finding panoramas
-----------------
    .. autofunction:: streetlevel.streetview.find_panorama
    
    Usage sample::
    
      from streetlevel import streetview
      
      pano = streetview.find_panorama(45.59395, 24.631609)
      print(pano.id)
      print(pano.lat, pano.lon)
      print(pano.date)

    .. autofunction:: streetlevel.streetview.find_panorama_async
    
    Usage sample::
    
      from streetlevel import streetview
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await streetview.find_panorama_async(45.59395, 24.631609, session)
          print(pano.id)
          print(pano.lat, pano.lon)
          print(pano.date)
     
    .. autofunction:: streetlevel.streetview.find_panorama_by_id

    Usage sample::
    
      from streetlevel import streetview
      
      pano = await streetview.find_panorama_by_id("Py5vaKsLWJG16XyZosdYBQ")
      print(pano.id)
      print(pano.lat, pano.lon)
      print(pano.date)
    
    .. autofunction:: streetlevel.streetview.find_panorama_by_id_async
    
    Usage sample::
    
      from streetlevel import streetview
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await streetview.find_panorama_by_id_async("Py5vaKsLWJG16XyZosdYBQ", session)
          print(pano.id)
          print(pano.lat, pano.lon)
          print(pano.date)
    
    .. autofunction:: streetlevel.streetview.get_coverage_tile
    .. autofunction:: streetlevel.streetview.get_coverage_tile_async
    .. autofunction:: streetlevel.streetview.get_coverage_tile_by_latlon
    .. autofunction:: streetlevel.streetview.get_coverage_tile_by_latlon_async

Downloading panoramas
---------------------
    .. autofunction:: streetlevel.streetview.get_panorama
    .. autofunction:: streetlevel.streetview.get_panorama_async
    .. autofunction:: streetlevel.streetview.download_panorama
    
    Usage sample: ::
    
      from streetlevel import streetview

      pano = streetview.find_panorama(46.883958, 12.169002)
      streetview.download_panorama(pano, f"{pano.id}.jpg")
      
    .. autofunction:: streetlevel.streetview.download_panorama_async
    
    Usage sample::
    
      from streetlevel import streetview
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await streetview.find_panorama_async(46.883958, 12.169002, session)
          await streetview.download_panorama_async(pano, f"{pano.id}.jpg", session)

Data classes
------------
    .. autoclass:: streetlevel.streetview.panorama.Artwork
       :members:
    .. autoclass:: streetlevel.streetview.panorama.ArtworkLink
       :members:
    .. autoclass:: streetlevel.streetview.panorama.BusinessStatus
       :members:
       :member-order: bysource
    .. autoclass:: streetlevel.streetview.panorama.BuildingLevel
       :members:
    .. autoclass:: streetlevel.streetview.panorama.CaptureDate
       :members:
       :member-order: bysource
    .. autoclass:: streetlevel.streetview.panorama.DepthMap
       :members:
    .. autoclass:: streetlevel.streetview.panorama.LocalizedString
       :members:
    .. autoclass:: streetlevel.streetview.panorama.Place
       :members:
    .. autoclass:: streetlevel.streetview.panorama.StreetLabel
       :members:
    .. autoclass:: streetlevel.streetview.panorama.StreetViewPanorama
       :members:
    .. autoclass:: streetlevel.streetview.panorama.UploadDate
       :members:
       :member-order: bysource

Miscellaneous
-------------
    .. autofunction:: streetlevel.streetview.build_permalink
    .. autofunction:: streetlevel.streetview.util.is_third_party_panoid
