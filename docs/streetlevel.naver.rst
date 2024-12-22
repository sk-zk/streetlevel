streetlevel.naver: Naver Street View
====================================

Finding panoramas
-----------------
    .. autofunction:: streetlevel.naver.find_panorama
    
    Usage sample::
    
      from streetlevel import naver

      pano = naver.find_panorama(37.4481486, 126.4509719)
      print(pano.lat, pano.lon)
      print(pano.id)
      print(pano.date)
      
    .. autofunction:: streetlevel.naver.find_panorama_async
    
    Usage sample::
    
      from streetlevel import naver
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await naver.find_panorama_async(37.4481486, 126.4509719, session)
          print(pano.lat, pano.lon)
          print(pano.id)
          print(pano.date)
    
    .. autofunction:: streetlevel.naver.find_panorama_by_id
    
    Usage sample::
    
      from streetlevel import naver

      pano = naver.find_panorama_by_id("hQ46n55JstD9C-tGdzZz2g")
      print(pano.lat, pano.lon)
      print(pano.date)
      print(pano.heading)
      
    .. autofunction:: streetlevel.naver.find_panorama_by_id_async
    
    Usage sample::
    
      from streetlevel import naver
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await naver.find_panorama_by_id_async("hQ46n55JstD9C-tGdzZz2g", session)
          print(pano.lat, pano.lon)
          print(pano.date)
          print(pano.heading)
          
    .. autofunction:: streetlevel.naver.get_depth
    .. autofunction:: streetlevel.naver.get_depth_async
    .. autofunction:: streetlevel.naver.get_historical
    .. autofunction:: streetlevel.naver.get_historical_async
    .. autofunction:: streetlevel.naver.get_neighbors
    .. autofunction:: streetlevel.naver.get_neighbors_async
    

Downloading panoramas
---------------------
    .. autofunction:: streetlevel.naver.get_panorama
    .. autofunction:: streetlevel.naver.get_panorama_async
    .. autofunction:: streetlevel.naver.download_panorama
    
    Usage sample::
    
      from streetlevel import naver
  
      pano = naver.find_panorama_by_id("hQ46n55JstD9C-tGdzZz2g")
      naver.download_panorama(pano, f"{pano.id}.jpg")

    .. autofunction:: streetlevel.naver.download_panorama_async
    
    Usage sample::
    
      from streetlevel import naver
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await naver.find_panorama_by_id_async("hQ46n55JstD9C-tGdzZz2g", session)
          await naver.download_panorama_async(pano, f"{pano.id}.jpg", session)
          
    .. autofunction:: streetlevel.naver.get_model
    .. autofunction:: streetlevel.naver.get_model_async

Data classes and Enums
----------------------
    .. autoclass:: streetlevel.naver.model.Model
      :members:
    .. autoclass:: streetlevel.naver.panorama.NaverPanorama
      :members:
    .. autoclass:: streetlevel.naver.panorama.Neighbors
      :members:
    .. autoclass:: streetlevel.naver.panorama.Overlay
      :members:
    .. autoclass:: streetlevel.naver.panorama.PanoramaType
      :members:
      :member-order: bysource

Miscellaneous
-------------
    .. autofunction:: streetlevel.naver.build_permalink