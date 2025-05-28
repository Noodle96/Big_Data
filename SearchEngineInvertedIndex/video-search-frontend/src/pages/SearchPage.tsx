import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import './SearchPage.css';

const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';

  const [query, setQuery] = useState<string>(initialQuery);
  const [results, setResults] = useState<any[]>([]);
  const [totalMatches, setTotalMatches] = useState<number>(0);


  useEffect(() => {
    if (initialQuery) {
      handleSearch(initialQuery);
    }
  }, []);

  const handleSearch = async (customQuery?: string) => {
    const q = customQuery ?? query;
    setSearchParams({ q });

    try {
      const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      setResults(data.results ?? data);
      setTotalMatches(data.total_matches);
    } catch (err) {
      console.error('Error al buscar:', err);
    }
  };

  return (
    <div className="app-container">
      <h1>Buscador de Escenas</h1>

      <div className="search-bar">
        <input
          type="text"
          className="search-input"
          placeholder="Ej: person carrying object"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button onClick={() => handleSearch()} className="main-button">
          Buscar
        </button>
      </div>

      <div className="results-container">
        <h2>{totalMatches} resultados encontrados: </h2>
        {results.length === 0 ? (
          <p>No hay resultados todavía.</p>
        ) : (
          <ul>
            {results.map((item, index) => (
              <li key={index} className="result-item">
                <Link
                  to={`/clip/${item.clip_id}`}
                  state={{
                    clip_id: item.clip_id,
                    score: item.score,
                    match: item.match,
                    priority: item.priority,
                    query: query,
                  }}
                >
                  <strong>{item.clip_id}</strong>
                </Link>
                <br />
                Score: <strong>{item.score}</strong> | Match: {item.match} | Priority: {item.priority}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default SearchPage;
