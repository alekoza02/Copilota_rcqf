# Copilota_rcqf

SUPPORTA:
---

viewport:
- Import modelli 3D .obj
- Abilitare / disabilitare i vari modelli presenti
- Visualizzare Point Cloud
- Visualizzare Wireframe
- Modificare POS / ROT / SCALE
- Modificare colore e materiale (roughness, glossiness, glass, metal, IOR, emissive)
- Aggiungere / Eliminare sfere
- Free camera movement

raytracer:
- Seemless transition from viewport to render (camera alignement)
- Multiprocessed progressive rendering
- Chunck subdivision of the work
- Multiple channels handles
    - Ambient Occlusion
    - Normal Map
    - Combined view
    - Basic shading (albedo)
    - Time map (average time per pixel)
    - Bounce map (average bounce per pixel)
- Percentage downscale
- Statistic info (start time, elapsed, ETA, samples rendered, ecc.)
- Ray - Sphere intersection
- Spehere CollisionBox
- Triangles handle 
- Triangles BVH (Sebastian Lague video)
- Rewrite main routines in C

TODO:
---
- Changable FOV
- Handle add / remove models in viewport
- BVH handles different models
- BVH optimization (child test & heuristics)