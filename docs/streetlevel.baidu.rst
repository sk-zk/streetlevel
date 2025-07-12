streetlevel.baidu: Baidu Panorama
=================================

Support for Baidu Panorama of Baidu Maps, covering many cities in the PRC. 

``find_panorama`` accepts WGS84, GCJ-02, BD09, or BD09MC. The positions of retrieved panoramas
are given as WGS84, GJC-02, and BD09MC.

Finding panoramas
-----------------
    .. autofunction:: streetlevel.baidu.find_panorama
    
    Usage sample::
    
      from streetlevel import baidu
      
      pano = baidu.find_panorama(22.2937592, 114.1692527)
      print(pano.id)
      print(pano.lat, pano.lon)
      print(pano.date)
      
    .. autofunction:: streetlevel.baidu.find_panorama_async
    
    Usage sample::
    
      from streetlevel import baidu
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await baidu.find_panorama_async(22.2937592, 114.1692527, session)
          print(pano.id)
          print(pano.lat, pano.lon)
          print(pano.heading)
          
    .. autofunction:: streetlevel.baidu.find_panorama_by_id
    
    Usage sample::
    
      from streetlevel import baidu
      
      pano = baidu.find_panorama_by_id("09024200121707301421572809B")
      print(pano.lat, pano.lon)
      print(pano.date)
       
    .. autofunction:: streetlevel.baidu.find_panorama_by_id_async
    
    Usage sample::
    
      from streetlevel import baidu
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await baidu.find_panorama_by_id_async("09024200121707301421572809B", session)
          print(pano.lat, pano.lon)
          print(pano.date)
          
    .. autofunction:: streetlevel.baidu.get_inter_metadata
    
    Usage sample::
    
      from streetlevel import baidu
      
      inter = baidu.get_inter_metadata("b60ec15c48587562843304bc")
      print(inter.name)
      print(inter.lat, inter.lon)
      for floor in inter.floors:
          print(floor.number, [p.id for p in floor.panos])
    
    .. autofunction:: streetlevel.baidu.get_inter_metadata_async
    
    Usage sample::
    
      from streetlevel import baidu
      
      async with ClientSession() as session:
          inter = await baidu.get_inter_metadata_async("b60ec15c48587562843304bc", session)
          print(inter.name)
          print(inter.lat, inter.lon)
          for floor in inter.floors:
              print(floor.number, [p.id for p in floor.panos])


Downloading panoramas
---------------------
    .. autofunction:: streetlevel.baidu.get_panorama
    .. autofunction:: streetlevel.baidu.get_panorama_async
    .. autofunction:: streetlevel.baidu.download_panorama
    
    Usage sample::
    
      from streetlevel import baidu
  
      pano = baidu.find_panorama_by_id("09024200121707301421572809B")
      baidu.download_panorama(pano, f"{pano.id}.jpg")
     
    .. autofunction:: streetlevel.baidu.download_panorama_async
    
    Usage sample::
    
      from streetlevel import baidu
      from aiohttp import ClientSession
      
      async with ClientSession() as session:
          pano = await baidu.find_panorama_by_id_async("09024200121707301421572809B", session)
          await baidu.download_panorama_async(pano, f"{pano.id}.jpg", session)


Data classes and Enums
----------------------
    .. autoclass:: streetlevel.baidu.Crs
      :members:
      :member-order: bysource
    .. autoclass:: streetlevel.baidu.panorama.BaiduPanorama
      :members:
    .. autoclass:: streetlevel.baidu.panorama.Floor
      :members:
    .. autoclass:: streetlevel.baidu.panorama.InteriorMetadata
      :members:
    .. autoclass:: streetlevel.baidu.panorama.InteriorPoint
      :members:
    .. autoclass:: streetlevel.baidu.panorama.PanoInteriorMetadata
      :members:
    .. autoclass:: streetlevel.baidu.panorama.PanoInteriorPoint
      :members:
    .. autoclass:: streetlevel.baidu.panorama.Provider
      :members:
    .. autoclass:: streetlevel.baidu.panorama.User
      :members:

Miscellaneous
-------------
    .. autofunction:: streetlevel.baidu.build_permalink
