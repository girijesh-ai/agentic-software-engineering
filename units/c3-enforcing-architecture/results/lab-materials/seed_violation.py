#!/usr/bin/env python3
"""Mutate backend/app/api/routes/items.py to reintroduce the exact inline
permission check the B2/B3 refactor removed from update_item(), for C3's
ablation. Run from the target repo root.

    python3 seed_violation.py backend/app/api/routes/items.py
"""

from __future__ import annotations

import sys
from pathlib import Path

OLD = '''@router.put("/{id}", response_model=ItemPublic)
def update_item(*, session: SessionDep, item: EditableItem, item_in: ItemUpdate) -> Any:
    """
    Update an item.
    """
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item'''

NEW = '''@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *, session: SessionDep, current_user: CurrentUser, id, item_in: ItemUpdate
) -> Any:
    """
    Update an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item'''


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "backend/app/api/routes/items.py")
    text = path.read_text(encoding="utf-8")
    if OLD not in text:
        print(f"ERROR: expected pattern not found in {path} - is the reference implementation applied?", file=sys.stderr)
        return 1
    path.write_text(text.replace(OLD, NEW), encoding="utf-8")
    print(f"seeded violation into {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
