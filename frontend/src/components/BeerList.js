import React, { useState, useEffect, useCallback } from 'react';
import { beerApi, brandApi } from '../api';

const EMPTY_FORM = {
  name: '',
  brand: '',
  beer_type: 'lager',
  alcohol_content: '',
  ibu: '',
  description: '',
  image_url: '',
  is_active: true,
};

function BeerForm({ beer, brands, onClose, onSaved }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [types, setTypes] = useState([]);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (beer) {
      setForm({
        name: beer.name,
        brand: beer.brand,
        beer_type: beer.beer_type,
        alcohol_content: beer.alcohol_content,
        ibu: beer.ibu || '',
        description: beer.description || '',
        image_url: beer.image_url || '',
        is_active: beer.is_active,
      });
    } else {
      setForm(EMPTY_FORM);
    }
  }, [beer]);

  useEffect(() => {
    beerApi.getTypes()
      .then(({ data }) => setTypes(data))
      .catch(() => setTypes([]));
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);

    const payload = {
      ...form,
      brand: parseInt(form.brand, 10),
      alcohol_content: parseFloat(form.alcohol_content),
      ibu: form.ibu ? parseInt(form.ibu, 10) : null,
      image_url: form.image_url || '',
    };

    try {
      if (beer) {
        await beerApi.update(beer.id, payload);
      } else {
        await beerApi.create(payload);
      }
      onSaved();
    } catch (err) {
      const data = err.response?.data;
      if (data && typeof data === 'object') {
        setError(Object.entries(data).map(([k, v]) => `${k}: ${v}`).join(' | '));
      } else {
        setError('Error al guardar la cerveza');
      }
    } finally {
      setSaving(false);
    }
  };

  if (brands.length === 0) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h3 className="modal-title">Nueva Cerveza</h3>
            <button className="modal-close" onClick={onClose}>&times;</button>
          </div>
          <div className="alert alert-error">
            Primero debes crear al menos una marca en la pestaña "Marcas".
          </div>
          <button className="btn btn-secondary" onClick={onClose}>Entendido</button>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">{beer ? 'Editar Cerveza' : 'Nueva Cerveza'}</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="beer-name">Nombre *</label>
            <input
              id="beer-name"
              className="form-input"
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              required
              placeholder="Heineken Original, Guinness Draught..."
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="beer-brand">Marca *</label>
              <select
                id="beer-brand"
                className="form-input"
                name="brand"
                value={form.brand}
                onChange={handleChange}
                required
              >
                <option value="">Selecciona una marca</option>
                {brands.map((b) => (
                  <option key={b.id} value={b.id}>{b.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="beer-type">Tipo *</label>
              <select
                id="beer-type"
                className="form-input"
                name="beer_type"
                value={form.beer_type}
                onChange={handleChange}
              >
                {types.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="beer-abv">Alcohol (%) *</label>
              <input
                id="beer-abv"
                className="form-input"
                type="number"
                step="0.1"
                name="alcohol_content"
                value={form.alcohol_content}
                onChange={handleChange}
                required
                placeholder="5.0"
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="beer-ibu">IBU</label>
              <input
                id="beer-ibu"
                className="form-input"
                type="number"
                name="ibu"
                value={form.ibu}
                onChange={handleChange}
                placeholder="30"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="beer-image">URL de imagen</label>
            <input
              id="beer-image"
              className="form-input"
              type="url"
              name="image_url"
              value={form.image_url}
              onChange={handleChange}
              placeholder="https://..."
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="beer-description">Descripción</label>
            <textarea
              id="beer-description"
              className="form-input"
              name="description"
              value={form.description}
              onChange={handleChange}
              rows="3"
            />
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                name="is_active"
                checked={form.is_active}
                onChange={handleChange}
              />
              Activa
            </label>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function BeerList({ onBrandsChanged }) {
  const [beers, setBeers] = useState([]);
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [search, setSearch] = useState('');
  const [brandFilter, setBrandFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [types, setTypes] = useState([]);

  const loadBeers = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (search) params.search = search;
      if (brandFilter) params.brand = brandFilter;
      if (typeFilter) params.beer_type = typeFilter;

      const { data } = await beerApi.list(params);
      setBeers(data.results || data);
    } catch (err) {
      setError('No se pudieron cargar las cervezas. ¿El backend está corriendo?');
    } finally {
      setLoading(false);
    }
  }, [search, brandFilter, typeFilter]);

  const loadBrands = useCallback(async () => {
    try {
      const { data } = await brandApi.list();
      setBrands(data.results || data);
    } catch (err) {
      setBrands([]);
    }
  }, []);

  useEffect(() => {
    const t = setTimeout(loadBeers, 300);
    return () => clearTimeout(t);
  }, [loadBeers]);

  useEffect(() => {
    loadBrands();
    beerApi.getTypes()
      .then(({ data }) => setTypes(data))
      .catch(() => setTypes([]));
  }, [loadBrands]);

  const handleDelete = async (beer) => {
    if (!window.confirm(`¿Eliminar la cerveza "${beer.name}"?`)) return;
    try {
      await beerApi.delete(beer.id);
      loadBeers();
      loadBrands();
      onBrandsChanged && onBrandsChanged();
    } catch (err) {
      setError('No se pudo eliminar la cerveza');
    }
  };

  const handleSaved = () => {
    setShowForm(false);
    setEditing(null);
    loadBeers();
    loadBrands();
    onBrandsChanged && onBrandsChanged();
  };

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Cervezas</h2>
          <button className="btn btn-primary" onClick={() => { setEditing(null); setShowForm(true); }}>
            + Nueva Cerveza
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="form-row">
          <div className="form-group">
            <input
              className="form-input"
              type="text"
              placeholder="Buscar por nombre, marca o descripción..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="form-group">
            <select
              className="form-input"
              value={brandFilter}
              onChange={(e) => setBrandFilter(e.target.value)}
            >
              <option value="">Todas las marcas</option>
              {brands.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <select
              className="form-input"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="">Todos los tipos</option>
              {types.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : beers.length === 0 ? (
          <div className="empty-state">
            <p>No hay cervezas registradas.</p>
            <p>Crea la primera con el botón "+ Nueva Cerveza".</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Marca</th>
                  <th>Tipo</th>
                  <th>Alcohol</th>
                  <th>IBU</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {beers.map((beer) => (
                  <tr key={beer.id}>
                    <td><strong>{beer.name}</strong></td>
                    <td>{beer.brand_name}</td>
                    <td>
                      <span className={`badge badge-${beer.beer_type}`}>
                        {beer.beer_type.toUpperCase()}
                      </span>
                    </td>
                    <td>{beer.alcohol_content}%</td>
                    <td>{beer.ibu || '-'}</td>
                    <td>
                      <span className={`badge ${beer.is_active ? 'badge-active' : 'badge-inactive'}`}>
                        {beer.is_active ? 'Activa' : 'Inactiva'}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => { setEditing(beer); setShowForm(true); }}
                        >
                          Editar
                        </button>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDelete(beer)}
                        >
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showForm && (
        <BeerForm
          beer={editing}
          brands={brands}
          onClose={() => { setShowForm(false); setEditing(null); }}
          onSaved={handleSaved}
        />
      )}
    </div>
  );
}

export default BeerList;
