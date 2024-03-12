streetlevel.ja: Já 360
====================================

Finding panoramas
-----------------
    .. autofunction:: streetlevel.ja.find_panorama
    
    Usage sample::
    
      from streetlevel import ja
      
      pano = ja.find_panorama(64.149726, -21.940347)
      print(pano.id)
      print(pano.lat, pano.lon)
      print(pano.heading)
      
    .. autofunction:: streetlevel.ja.find_panorama_async
    
    Usage sample::
    
      from streetlevel import ja
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await ja.find_panorama_async(64.149726, -21.940347, session)
          print(pano.id)
          print(pano.lat, pano.lon)
          print(pano.heading)
          
    .. autofunction:: streetlevel.ja.find_panorama_by_id
    
    Usage sample::
    
      from streetlevel import ja
      
      pano = ja.find_panorama_by_id(2962469)
      print(pano.lat, pano.lon)
      print(pano.date)
      print(pano.address)
       
    .. autofunction:: streetlevel.ja.find_panorama_by_id_async
    
    Usage sample::
    
      from streetlevel import ja
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await ja.find_panorama_by_id_async(2962469, session)
          print(pano.lat, pano.lon)
          print(pano.date)
          print(pano.address)


Downloading panoramas
---------------------
    .. autofunction:: streetlevel.ja.get_panorama
    .. autofunction:: streetlevel.ja.get_panorama_async
    .. autofunction:: streetlevel.ja.download_panorama
    
    Usage sample::
    
      from streetlevel import ja
  
      pano = ja.find_panorama_by_id(2962469)
      ja.download_panorama(pano, f"{pano.id}.jpg")
     
    .. autofunction:: streetlevel.ja.download_panorama_async
    
    Usage sample::
    
      from streetlevel import ja
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await ja.find_panorama_by_id_async(2962469, session)
          await ja.download_panorama_async(pano, f"{pano.id}.jpg", session)

Data classes
----------------------
    .. autoclass:: streetlevel.ja.panorama.Address
      :members:
    .. autoclass:: streetlevel.ja.panorama.CaptureDate
      :members:
    .. autoclass:: streetlevel.ja.panorama.JaPanorama
      :members:

Miscellaneous
-------------
    .. autofunction:: streetlevel.ja.build_permalink
