from flask import Flask, request, jsonify
from flask_cors import CORS

from collections import defaultdict
from typing import Dict, List, Tuple, Set

import os
import json

# Tipado
InvertedIndexType = Dict[str, List[Tuple[str, int]]]
PriorityMapType = Dict[str, float]
ClipScoreType = Dict[str, Dict[str, float]]

# Globales
inverted_index: InvertedIndexType = defaultdict(list)
priority_map: PriorityMapType = {}
USE_AND_MODE:bool = True # Si se usa modo AND para la búsqueda

# Leer índice invertido
with open("invertedIndex.txt", "r") as f:
    for line in f:
        token, entries = line.strip().split("\t")
        for entry in entries.split(", "):
            clip_id, freq = entry.split(":")
            inverted_index[token].append((clip_id, int(freq)))

# Leer prioridades
with open("prioridad.txt", "r") as f:
    for line in f:
        scene_id, score = line.strip().split()
        priority_map[scene_id] = float(score)

# print("inverted_index:", len(inverted_index), "tokens")
# print(inverted_index)
# print("priority_map:", len(priority_map), "scenes")

app = Flask(__name__)
CORS(app)
# http://127.0.0.1:5000/search?q=person%20vehicle
@app.route("/search")
def search() -> str:
    query: str = request.args.get("q", "").lower().strip()
    tokens: List[str] = query.split()

    alpha: float = 0.7
    beta: float = 0.3
    clip_scores: ClipScoreType = {}

    # for token in tokens:
    #     for clip_id, freq in inverted_index.get(token, []):
    #         print("clip_id:", clip_id, "freq:", freq)

    #         scene_parts: List[str] = clip_id.split("|")
    #         print("scene_parts:", scene_parts)

    #         # scene_id: str = "_".join(scene_parts)
    #         scene_id: str = scene_parts[0]
    #         print("scene_id:", scene_id)

    #         priority: float = priority_map.get(scene_id, 1.0)
    #         print("priority:", priority)

    #         clip_id = scene_parts[1]

    #         if clip_id not in clip_scores:
    #             clip_scores[clip_id] = {"score": 0.0, "match": 0.0, "priority": priority}

    #         clip_scores[clip_id]["match"] += freq

    if USE_AND_MODE:
        # AND logic
        token_sets: List[Set[str]] = [
            {full_id for full_id, _ in inverted_index.get(token, [])}
            for token in tokens
        ]
        common_ids: Set[str] = set.intersection(*token_sets) if token_sets else set()

        for token in tokens:
            for full_id, freq in inverted_index.get(token, []):
                if full_id not in common_ids:
                    continue

                scene_id, clip_filename = full_id.split("|")
                priority: float = priority_map.get(scene_id, 1.0)

                if clip_filename not in clip_scores:
                    clip_scores[clip_filename] = {"score": 0.0, "match": 0.0, "priority": priority}
                clip_scores[clip_filename]["match"] += freq
    else:
        # OR logic
        for token in tokens:
            for full_id, freq in inverted_index.get(token, []):
                scene_id, clip_filename = full_id.split("|")
                priority: float = priority_map.get(scene_id, 1.0)

                if clip_filename not in clip_scores:
                    clip_scores[clip_filename] = {"score": 0.0, "match": 0.0, "priority": priority}
                clip_scores[clip_filename]["match"] += freq

    for clip_id, data in clip_scores.items():
        m: float = data["match"]
        p: float = data["priority"]
        data["score"] = alpha * m + beta * p;

    # top_k: List[Tuple[str, Dict[str, float]]] = sorted(
    #     clip_scores.items(), key=lambda x: x[1]["score"], reverse=True
    # )[:10]
    top_k: List[Tuple[str, Dict[str, float]]] = sorted(
        clip_scores.items(), key=lambda x: x[1]["score"], reverse=True
    )

    total_matches = len(clip_scores)

    

    # result = [
    #     {
    #         "clip_id": clip,
    #         "score": round(data["score"], 2),
    #         "match": int(data["match"]),
    #         "priority": round(data["priority"], 2)
    #     }
    #     for clip, data in top_k
    # ]

    # return jsonify(result)
    return jsonify({
        "total_matches": total_matches,
        "results": [
            {
                "clip_id": clip,
                "score": round(data["score"], 2),
                "match": int(data["match"]),
                "priority": round(data["priority"], 2)
            }
            for clip, data in top_k
        ]
    })


# http://localhost:5000/clip_details?clip_id=VIRAT_S_010200_03_000470_000567
@app.route("/clip_details")
def clip_details() -> str:
    clip_id = request.args.get("clip_id", "")
    print(f"⏩ Buscando clip: {clip_id}")
    if not clip_id:
        return jsonify({"error": "Missing clip_id"}), 400

    with open("all_scenes.jsonl", "r") as f:
        for line in f:
            scene_data = json.loads(line)
            for subclip in scene_data.get("subclips", []):
                if subclip.get("clip_id") == clip_id:
                    print("✅ Subclip encontrado.")
                    return jsonify(subclip)

    return jsonify({"error": f"Clip {clip_id} not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
