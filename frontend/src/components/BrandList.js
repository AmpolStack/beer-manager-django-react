import React, { useState, useEffect, useCallback } from 'react';
import { brandApi } from '../api';

const EMPTY_FORM = {
  name: '',
  country: '',
  founded_year: '',
  description: '',
};

function BrandForm({ brand, onClose, onSaved }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (brand) {
      setForm({
        name: brand.name,
        country: brand.country || '',
        founded_year: brand.founded_year || '',
        description: brand.description || '',
      });
    } else {
      setForm(EMPTY_FORM);
    }
  }, [brand]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);

    const payload = {
      ...form,
      founded_year: form.founded_year ? parseInt(form.founded_year, 10) : null,
    };

    try {
      if (brand) {
        await brandApi.update(brand.id, payload);
      } else {
        await brandApi.create(payload);
      }
      onSaved();
    } catch (err) {
      const data = err.response?.data;
      if (data && typeof data === 'object') {
        setError(Object.entries(data).map(([k, v]) => `${k}: ${v}`).join(' | '));
      } else {
        setError('Error al guardar la marca');
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">{brand ? 'Editar Marca' : 'Nueva Marca'}</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="brand-name">Nombre *</label>
            <input
              id="brand-name"
              className="form-input"
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              required
              placeholder="Heineken, Corona, Guinness..."
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="brand-country">País</label>
              <input
                id="brand-country"
                className="form-input"
                type="text"
                name="country"
                value={form.country}
                onChange={handleChange}
                placeholder="País de origen"
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="brand-year">Año de fundación</label>
              <input
                id="brand-year"
                className="form-input"
                type="number"
                name="founded_year"
                value={form.founded_year}
                onChange={handleChange}
                placeholder="1864"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="brand-description">Descripción</label>
            <textarea
              id="brand-description"
              className="form-input"
              name="description"
              value={form.description}
              onChange={handleChange}
              rows="3"
            />
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

function BrandList() {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [search, setSearch] = useState('');

  const loadBrands = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await brandApi.list({ search: search || undefined });
      setBrands(data.results || data);
    } catch (err) {
      setError('No se pudieron cargar las marcas. ¿El backend está corriendo?');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    const t = setTimeout(loadBrands, 300);
    return () => clearTimeout(t);
  }, [loadBrands]);

  const handleDelete = async (brand) => {
    if (!window.confirm(`¿Eliminar la marca "${brand.name}"? Se borrarán sus cervezas.`)) {
      return;
    }
    try {
      await brandApi.delete(brand.id);
      loadBrands();
    } catch (err) {
      setError('No se pudo eliminar la marca');
    }
  };

  const handleSaved = () => {
    setShowForm(false);
    setEditing(null);
    loadBrands();
  };

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Marcas</h2>
          <button className="btn btn-primary" onClick={() => { setEditing(null); setShowForm(true); }}>
            + Nueva Marca
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="form-group">
          <input
            className="form-input"
            type="text"
            placeholder="Buscar marca o país..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : brands.length === 0 ? (
          <div className="empty-state">
            <p>No hay marcas registradas.</p>
            <p>Crea la primera con el botón "+ Nueva Marca".</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>País</th>
                  <th>Fundada</th>
                  <th>Cervezas</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {brands.map((brand) => (
                  <tr key={brand.id}>
                    <td><strong>{brand.name}</strong></td>
                    <td>{brand.country || '-'}</td>
                    <td>{brand.founded_year || '-'}</td>
                    <td>{brand.beers_count ?? '-'}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => { setEditing(brand); setShowForm(true); }}
                        >
                          Editar
                        </button>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDelete(brand)}
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
        <BrandForm
          brand={editing}
          onClose={() => { setShowForm(false); setEditing(null); }}
          onSaved={handleSaved}
        />
      )}
    </div>
  );
}

export default BrandList;
