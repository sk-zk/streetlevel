streetlevel.streetside: Bing Streetside
=======================================


Finding panoramas
-----------------
    .. autofunction:: streetlevel.streetside.find_panoramas
    
    Usage sample::
    
      from streetlevel import streetside
      
      panos = streetside.find_panoramas(-17.831848, 31.046641)
      print(panos[0].lat, panos[0].lon)
      print(panos[0].id)
      print(panos[0].date)
    
    .. autofunction:: streetlevel.streetside.find_panoramas_async
    
    Usage sample::
    
      from streetlevel import streetside
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          panos = await streetside.find_panoramas_async(-17.831848, 31.046641, session)
          print(panos[0].lat, panos[0].lon)
          print(panos[0].id)
          print(panos[0].date)
          
    .. autofunction:: streetlevel.streetside.find_panoramas_in_bbox
    .. autofunction:: streetlevel.streetside.find_panoramas_in_bbox_async
    .. autofunction:: streetlevel.streetside.find_panorama_by_id
    
    Usage sample::
    
      from streetlevel import streetside
  
      pano = streetside.find_panorama_by_id(398611371)
      print(pano.lat, pano.lon)
      print(pano.date)
      print(pano.heading)

    .. autofunction:: streetlevel.streetside.find_panorama_by_id_async
    
    Usage sample::
    
      from streetlevel import streetside
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await streetside.find_panorama_by_id_async(398611371, session)
          print(pano.lat, pano.lon)
          print(pano.date)
          print(pano.heading)

Downloading panoramas
---------------------
    .. autofunction:: streetlevel.streetside.get_panorama
    .. autofunction:: streetlevel.streetside.get_panorama_async
    .. autofunction:: streetlevel.streetside.download_panorama
    
    Usage sample::
    
      from streetlevel import streetside
  
      pano = streetside.find_panorama_by_id(398611371)
      streetside.download_panorama(pano, f"{pano.id}.jpg")
    
    .. autofunction:: streetlevel.streetside.download_panorama_async
    
    Usage sample::
    
      from streetlevel import streetside
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await streetside.find_panorama_by_id_async(398611371, session)
          await streetside.download_panorama_async(pano, f"{pano.id}.jpg", session)

Data classes
------------
    .. autoclass:: streetlevel.streetside.panorama.StreetsidePanorama
      :members:

Miscellaneous
-------------
    .. autofunction:: streetlevel.streetside.build_permalink
    .. autofunction:: streetlevel.streetside.util.from_base4
    .. autofunction:: streetlevel.streetside.util.to_base4
