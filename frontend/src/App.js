import React, { useState } from 'react';
import BrandList from './components/BrandList';
import BeerList from './components/BeerList';

function App() {
  const [tab, setTab] = useState('beers');
  const [version, setVersion] = useState(0);

  return (
    <div>
      <header className="header">
        <div className="header-content">
          <h1>Beer Manager</h1>
          <nav className="nav-tabs">
            <button
              className={`nav-tab ${tab === 'beers' ? 'active' : ''}`}
              onClick={() => setTab('beers')}
            >
              Cervezas
            </button>
            <button
              className={`nav-tab ${tab === 'brands' ? 'active' : ''}`}
              onClick={() => setTab('brands')}
            >
              Marcas
            </button>
          </nav>
        </div>
      </header>

      <main className="container">
        {tab === 'beers' ? (
          <BeerList onBrandsChanged={() => setVersion((v) => v + 1)} key={`beers-${version}`} />
        ) : (
          <BrandList />
        )}
      </main>
    </div>
  );
}

export default App;
