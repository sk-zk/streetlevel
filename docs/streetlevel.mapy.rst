streetlevel.mapy: Mapy.cz Panorama
=======================================

Finding panoramas
-----------------
    .. autofunction:: streetlevel.mapy.find_panorama
    
    Usage sample::
    
      from streetlevel import mapy
  
      pano = mapy.find_panorama(50.704732, 14.404809)
      print(pano.lat, pano.lon)
      print(pano.id)
      print(pano.date)

    .. autofunction:: streetlevel.mapy.find_panorama_async
    
    Usage sample::
    
      from streetlevel import mapy
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await mapy.find_panorama_async(50.704732, 14.404809, session)
          print(pano.lat, pano.lon)
          print(pano.id)
          print(pano.date)
          
    .. autofunction:: streetlevel.mapy.find_panorama_by_id
    
    Usage sample::
    
      from streetlevel import mapy
      
      pano = mapy.find_panorama_by_id(82102772)
      print(pano.lat, pano.lon)
      print(pano.date)
      print(pano.heading)

    .. autofunction:: streetlevel.mapy.find_panorama_by_id_async
    
    Usage sample::
    
      from streetlevel import mapy
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await mapy.find_panorama_by_id_async(82102772, session)
          print(pano.lat, pano.lon)
          print(pano.date)
          print(pano.heading)
    
    .. autofunction:: streetlevel.mapy.get_links
    .. autofunction:: streetlevel.mapy.get_links_async

Downloading panoramas
---------------------
    .. autofunction:: streetlevel.mapy.get_panorama
    .. autofunction:: streetlevel.mapy.get_panorama_async
    .. autofunction:: streetlevel.mapy.download_panorama
    
    Usage sample::
    
      from streetlevel import mapy
      
      pano = mapy.find_panorama_by_id(82102772)
      mapy.download_panorama(pano, f"{pano.id}.jpg")
      
    .. autofunction:: streetlevel.mapy.download_panorama_async
    
    Usage sample::
    
      from streetlevel import mapy
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await mapy.find_panorama_by_id_async(82102772, session)
          await mapy.download_panorama_async(pano, f"{pano.id}.jpg", session)

Data classes
------------
    .. autoclass:: streetlevel.mapy.panorama.MapyPanorama
      :members:

Miscellaneous
-------------
    .. autofunction:: streetlevel.mapy.build_permalink
