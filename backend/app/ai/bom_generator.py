"""
GNN 기반 BOM 자동 생성
  - CAD 파싱 결과를 그래프로 모델링
  - GNN 추론 또는 규칙 기반 폴백으로 BOM 항목 생성
"""
from __future__ import annotations
from typing import Any
from pathlib import Path


def generate_bom_from_cad(parsed_objects: dict[str, Any], product_type: str = "LADDER_TRAY") -> list[dict]:
    """
    CAD 파싱 결과 → BOM 항목 리스트 반환.
    GNN 모델 미존재 시 규칙 기반 생성.
    """
    gnn_model_path = Path("./models/bom_gnn.pt")
    if gnn_model_path.exists():
        return _generate_bom_gnn(parsed_objects, str(gnn_model_path))
    return _generate_bom_rule_based(parsed_objects, product_type)


def _generate_bom_gnn(parsed: dict, model_path: str) -> list[dict]:
    """PyTorch Geometric GNN 추론 — 모델 학습 후 활성화"""
    # TODO:
    # 1. 파싱된 객체를 그래프 노드/엣지로 변환 (torch_geometric.data.Data)
    # 2. GNN 모델 로드 및 추론
    # 3. 예측된 BOM 항목 반환
    raise NotImplementedError("GNN 모델 학습 필요 — bom_gnn.pt 없음")


def _generate_bom_rule_based(parsed: dict, product_type: str) -> list[dict]:
    """규칙 기반 BOM 생성 (GNN 모델 미존재 시 폴백)"""
    bom_items = []
    seq = 1

    for obj in parsed.get("objects", []):
        obj_type = obj.get("type", "")
        count = obj.get("count", 1)
        length = obj.get("length_mm", 0)

        if obj_type == "CHANNEL":
            bom_items.append({
                "seq": seq, "item_code": "MAT-SS400-2T",
                "item_name": f"SS400 채널 {length}mm",
                "quantity": count, "unit": "EA",
                "material": obj.get("material", "SS400"),
            })
        elif obj_type == "RUNG":
            bom_items.append({
                "seq": seq, "item_code": "MAT-SS400-2T",
                "item_name": f"SS400 렁 {length}mm",
                "quantity": count, "unit": "EA",
                "material": obj.get("material", "SS400"),
            })
        elif obj_type == "BOLT":
            size = obj.get("size", "M10")
            bom_items.append({
                "seq": seq, "item_code": f"MAT-BOLT-{size}",
                "item_name": f"볼트 {size}",
                "quantity": count, "unit": "EA",
                "material": "Steel",
            })
        else:
            bom_items.append({
                "seq": seq, "item_code": f"MAT-{obj_type}-001",
                "item_name": obj_type,
                "quantity": count, "unit": "EA",
                "material": obj.get("material", "Steel"),
            })

        seq += 1

    # 용접 와이어 자동 추가 (렁 수 기준)
    rung_count = sum(o.get("count", 0) for o in parsed.get("objects", []) if o.get("type") == "RUNG")
    if rung_count > 0:
        bom_items.append({
            "seq": seq, "item_code": "MAT-WIRE-08",
            "item_name": "용접 와이어 0.8mm",
            "quantity": round(rung_count * 0.05, 2), "unit": "KG",
            "material": "Wire",
        })

    return bom_items
