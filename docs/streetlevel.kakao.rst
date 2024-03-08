streetlevel.kakao: Kakao Road View
===================================

Finding panoramas
-----------------
    .. autofunction:: streetlevel.kakao.find_panoramas
    
    Usage sample::
    
      from streetlevel import kakao
  
      panos = kakao.find_panoramas(37.4481486, 126.4509719)
      print(panos[0].lat, panos[0].lon)
      print(panos[0].id)
      print(panos[0].date)
    
    .. autofunction:: streetlevel.kakao.find_panoramas_async
    
    Usage sample::
    
      from streetlevel import kakao
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          panos = await kakao.find_panoramas_async(37.4481486, 126.4509719, session)
          print(panos[0].lat, panos[0].lon)
          print(panos[0].id)
          print(panos[0].date)
          
    .. autofunction:: streetlevel.kakao.find_panorama_by_id
    
    Usage sample::
    
      from streetlevel import kakao
  
      pano = kakao.find_panorama_by_id(1168949345)
      print(pano.lat, pano.lon)
      print(pano.date)
      print(pano.address)
    
    .. autofunction:: streetlevel.kakao.find_panorama_by_id_async
    
    Usage sample::
    
      from streetlevel import kakao
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await kakao.find_panorama_by_id_async(1168949345, session)
          print(pano.lat, pano.lon)
          print(pano.date)
          print(pano.address)

Downloading panoramas
---------------------
    .. autofunction:: streetlevel.kakao.get_panorama
    .. autofunction:: streetlevel.kakao.get_panorama_async
    .. autofunction:: streetlevel.kakao.download_panorama
    
    Usage sample::
    
      from streetlevel import kakao

      pano = kakao.find_panorama_by_id(1168949345)
      kakao.download_panorama(pano, f"{pano.id}.jpg")
      
    .. autofunction:: streetlevel.kakao.download_panorama_async
    
    Usage sample::
    
      from streetlevel import kakao
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await kakao.find_panorama_by_id_async(1168949345, session)
          await kakao.download_panorama(pano, f"{pano.id}.jpg")
    
    .. autofunction:: streetlevel.kakao.get_depthmap
    .. autofunction:: streetlevel.kakao.get_depthmap_async
    .. autofunction:: streetlevel.kakao.download_depthmap
    .. autofunction:: streetlevel.kakao.download_depthmap_async

Data classes and enums
----------------------
    .. autoclass:: streetlevel.kakao.panorama.KakaoPanorama
      :members:
    .. autoclass:: streetlevel.kakao.panorama.PanoramaType
      :members:
      :member-order: bysource

Miscellaneous
-------------
    .. autofunction:: streetlevel.kakao.build_permalink
