(function () {
  const container = document.querySelector('.property-list');
  if (!container) return;

  const escapeHtml = (value) => String(value ?? '').replace(/[&<>'"]/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'
  }[c]));

  fetch('data/inmuebles.json', { cache: 'no-store' })
    .then(r => { if (!r.ok) throw new Error('No se pudo cargar la cartera'); return r.json(); })
    .then(data => {
      const properties = Array.isArray(data.properties) ? data.properties : [];
      if (!properties.length) throw new Error('Cartera vacía');
      container.innerHTML = properties.map(p => `
        <a class="property-card" href="${escapeHtml(p.url)}" target="_blank" rel="noopener">
          ${p.image ? `<img class="property-card-image" src="${escapeHtml(p.image)}" alt="${escapeHtml(p.title || p.location)}" loading="lazy">` : ''}
          <div class="meta">${escapeHtml(p.location)}</div>
          <h2>${escapeHtml(p.title)}</h2>
          <p class="small">${escapeHtml(p.type || 'Inmueble')} · ${escapeHtml(p.price || '')}${p.rooms ? ` · ${escapeHtml(p.rooms)}` : ''}${p.area ? ` · ${escapeHtml(p.area)}` : ''}</p>
          <span class="btn btn-outline" data-i18n="propertyView">Ver en Idealista</span>
        </a>
      `).join('');
    })
    .catch(err => {
      console.error('[Project House] Error cargando inmuebles:', err);
      // The existing page remains empty rather than showing stale hard-coded listings.
      container.innerHTML = '<p class="small" data-i18n="propertyLoading">La cartera se está actualizando. Vuelve a intentarlo en unos instantes.</p>';
    });
})();
