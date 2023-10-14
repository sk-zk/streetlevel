streetlevel.streetview: Google Street View
==========================================


Finding panoramas
-----------------
    .. autofunction:: streetlevel.streetview.find_panorama
    .. autofunction:: streetlevel.streetview.find_panorama_async
    .. autofunction:: streetlevel.streetview.find_panorama_by_id
    .. autofunction:: streetlevel.streetview.find_panorama_by_id_async
    .. autofunction:: streetlevel.streetview.get_coverage_tile
    .. autofunction:: streetlevel.streetview.get_coverage_tile_async
    .. autofunction:: streetlevel.streetview.get_coverage_tile_by_latlon
    .. autofunction:: streetlevel.streetview.get_coverage_tile_by_latlon_async

Downloading panoramas
---------------------
    .. autofunction:: streetlevel.streetview.get_panorama
    .. autofunction:: streetlevel.streetview.get_panorama_async
    .. autofunction:: streetlevel.streetview.download_panorama
    .. autofunction:: streetlevel.streetview.download_panorama_async

Data classes
------------
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
    .. autoclass:: streetlevel.streetview.panorama.StreetViewPanorama
       :members:
    .. autoclass:: streetlevel.streetview.panorama.UploadDate
       :members:
       :member-order: bysource

Miscellaneous
-------------
    .. autofunction:: streetlevel.streetview.util.is_third_party_panoid
