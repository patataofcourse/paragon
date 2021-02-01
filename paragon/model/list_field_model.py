from typing import Any

from PySide2 import QtCore
from PySide2.QtCore import QAbstractListModel, QModelIndex


# TODO: REORDERING
class ListFieldModel(QAbstractListModel):
    def __init__(self, gd, icons, rid, field_id):
        super().__init__()
        self.gd = gd
        self.icons = icons
        self.rid = rid
        self.field_id = field_id
        self.items = gd.items(rid, field_id)

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self.items)

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None
        rid = self.items[index.row()]
        if role == QtCore.Qt.DisplayRole:
            display = self.gd.display(rid)
            display = display if display else self.gd.key(rid)
            return display if display else f"Item {index.row()}"
        elif role == QtCore.Qt.DecorationRole:
            return self.icons.icon(rid)
        elif role == QtCore.Qt.UserRole:
            return rid
        return None

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        if row > self.rowCount():
            return False
        else:
            self.beginInsertRows(parent, row, row + count)
            for i in range(0, count):
                self.items.insert(
                    row, self.gd.list_insert(self.rid, self.field_id, row)
                )
            self.endInsertRows()
            return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        if row >= self.rowCount() or row + count > self.rowCount():
            return False
        else:
            self.beginRemoveRows(parent, row, row + count)
            for _ in range(0, count):
                self.gd.list_remove(self.rid, self.field_id, row)
            del self.items[row]
            self.endRemoveRows()
            return True

    def add_item(self):
        self.insertRow(self.rowCount())

    def delete_item(self, index):
        self.removeRow(index.row())