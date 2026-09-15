

SINCRONIZACION DE INMUEBLES
La carpeta data/inmuebles.json se actualiza mediante GitHub Actions desde el perfil publico de PROJECT HOUSE en Idealista.
El workflow .github/workflows/sync-inmuebles.yml se ejecuta cada 6 horas y tambien puede lanzarse manualmente.
No edites inmuebles.html para añadir/quitar propiedades: la cartera se genera desde data/inmuebles.json.
