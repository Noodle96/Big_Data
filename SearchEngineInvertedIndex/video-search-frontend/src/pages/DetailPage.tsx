import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';

import './DetailsPage.css';

const DetailPage: React.FC = () => {
  const { clipId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const state = location.state as {
    score: number;
    match: number;
    priority: number;
    query: string;
  };

  const videoUrl = `/videos/${clipId}.mp4`;

  const [subclipData, setSubclipData] = useState<any>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const fetchSubclip = async () => {
      try {
        const res = await fetch(`/clip_details?clip_id=${clipId}`);
        console.log("print clipId", clipId);
        
        const data = await res.json();
        
        if (data.error) {
            console.log("print data.error", data.error);
            setError(data.error);
        } else {
            console.log("print data", data);
            setSubclipData(data);
        }
      } catch (err) {
        setError("Error al obtener datos del subclip.");
      }
    };

    fetchSubclip();
  }, [clipId]);


  return (
    <div className="detail-container">
      <h2>Detalle del Clip</h2>

      <p className="query-info">🔎 Consulta realizada: <strong>{state.query}</strong></p>

      <button onClick={() => navigate(-1)} className="main-button" style={{ marginBottom: '1rem' }}>
        ⬅️ Volver
      </button>

      <div className="detail-box">
        <div className="metric"><span className="label">Clip ID:</span> {clipId}</div>
        <div className="metric"><span className="label">Score:</span> {state.score}</div>
        <div className="metric"><span className="label">Match:</span> {state.match}</div>
        <div className="metric"><span className="label">Priority:</span> {state.priority}</div>

        <div className="video-section">
          <video width="100%" height="auto" controls>
            <source src={videoUrl} type="video/mp4" />
            Tu navegador no soporta el video.
          </video>
        </div>

        <div style={{ marginTop: '2rem' }}>
          <h3>Modo desarrollador- datos del Subclip (JSON)</h3>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          {subclipData ? (
            <pre className="json-box">{JSON.stringify(subclipData, null, 2)}</pre>
          ) : !error ? (
            <p>Cargando...</p>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default DetailPage;
