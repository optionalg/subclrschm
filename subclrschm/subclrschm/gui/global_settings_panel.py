"""Global settigns panel."""
from __future__ import unicode_literals
from . import gui
from . import grid_helper
from . import global_setting_dialog
from . import settings_codes as sc
from ..rgba import RGBA
import wx


class GlobalSettings(gui.GlobalSettingsPanel, grid_helper.GridHelper):

    """GlobalSettings."""

    def __init__(self, parent, scheme, update, reshow):
        """Initialize."""

        super(GlobalSettings, self).__init__(parent)
        self.setup_keybindings()
        self.parent = parent
        wx.EVT_MOTION(self.m_plist_grid.GetGridWindow(), self.on_mouse_motion)
        self.m_plist_grid.SetDefaultCellBackgroundColour(self.GetBackgroundColour())
        self.read_plist(scheme)
        self.reshow = reshow
        self.update_plist = update

    def read_plist(self, scheme):
        """Read plist to get global settings."""

        foreground = RGBA(scheme["settings"][0]["settings"].get("foreground", "#000000"))
        background = RGBA(scheme["settings"][0]["settings"].get("background", "#FFFFFF"))
        global BG_COLOR
        BG_COLOR = background
        global FG_COLOR
        FG_COLOR = foreground
        count = 0

        for k in sorted(scheme["settings"][0]["settings"].iterkeys()):
            v = scheme["settings"][0]["settings"][k]
            self.m_plist_grid.AppendRows(1)
            self.update_row(count, k, v)
            count += 1
        self.resize_table()

        self.go_cell(self.m_plist_grid, 0, 0)

    def resize_table(self):
        """Resize teh table."""

        self.m_plist_grid.BeginBatch()
        nb_size = self.parent.GetSize()
        total_size = 0
        for x in range(0, 2):
            self.m_plist_grid.AutoSizeColumn(x)
            total_size += self.m_plist_grid.GetColSize(x)
        delta = nb_size[0] - 20 - total_size
        if delta > 0:
            self.m_plist_grid.SetColSize(1, self.m_plist_grid.GetColSize(1) + delta)
        self.m_plist_grid.EndBatch()

    def update_row(self, count, k, v):
        """Update row."""

        try:
            bg = RGBA(v.strip())
            if k != "background":
                editor = self.GetParent().GetParent().GetParent()
                bg.apply_alpha(editor.m_style_settings.bg_color.get_rgb())
            fg = RGBA("#000000") if bg.luminance() > 128 else RGBA("#FFFFFF")
        except:
            bg = RGBA("#FFFFFF")
            fg = RGBA("#000000")

        self.m_plist_grid.SetCellValue(count, 0, k)
        self.m_plist_grid.SetCellValue(count, 1, v)

        b = self.m_plist_grid.GetCellBackgroundColour(count, 0)
        f = self.m_plist_grid.GetCellTextColour(count, 0)

        b.Set(bg.r, bg.g, bg.b)
        f.Set(fg.r, fg.g, fg.b)

        self.m_plist_grid.SetCellBackgroundColour(count, 0, b)
        self.m_plist_grid.SetCellBackgroundColour(count, 1, b)

        self.m_plist_grid.SetCellTextColour(count, 0, f)
        self.m_plist_grid.SetCellTextColour(count, 1, f)

    def set_object(self, key, value):
        """Set the object."""

        row = self.m_plist_grid.GetGridCursorRow()
        col = self.m_plist_grid.GetGridCursorCol()
        self.update_row(row, key, value)
        self.update_plist(sc.JSON_MODIFY, {"table": "global", "index": key, "data": value})
        if key == "background" or key == "foreground":
            self.reshow(row, col)
        self.resize_table()

    def delete_row(self):
        """Delete the row."""

        row = self.m_plist_grid.GetGridCursorRow()
        col = self.m_plist_grid.GetGridCursorCol()
        name = self.m_plist_grid.GetCellValue(row, 0)
        self.m_plist_grid.DeleteRows(row, 1)
        self.m_plist_grid.GetParent().update_plist(sc.JSON_DELETE, {"table": "global", "index": name})
        if name == "foreground" or name == "background":
            self.m_plist_grid.GetParent().reshow(row, col)

    def validate_name(self, name):
        """Validate the name."""

        valid = True
        editor = self.GetParent().GetParent().GetParent()
        for k in editor.scheme["settings"][0]["settings"]:
            if name == k:
                valid = False
                break
        return valid

    def insert_row(self):
        """Insert a new row."""

        new_name = "new_item"
        count = 0
        while not self.validate_name(new_name):
            new_name = "new_item_%d" % count
            count += 1

        editor = self.GetParent().GetParent().GetParent()
        global_setting_dialog.GlobalEditor(
            editor,
            editor.scheme["settings"][0]["settings"],
            new_name,
            "nothing",
            insert=True
        ).ShowModal()

    def edit_cell(self):
        """Edit the cell."""
        grid = self.m_plist_grid
        row = grid.GetGridCursorRow()
        editor = self.GetParent().GetParent().GetParent()
        global_setting_dialog.GlobalEditor(
            editor,
            editor.scheme["settings"][0]["settings"],
            grid.GetCellValue(row, 0),
            grid.GetCellValue(row, 1)
        ).ShowModal()

    def on_grid_label_left_click(self, event):
        """Handle grid label left click."""

        return

    def on_mouse_motion(self, event):
        """Handle mouse motion event."""

        self.mouse_motion(event)

    def on_edit_cell(self, event):
        """Handle edit cell event."""

        self.edit_cell()

    def on_grid_key_down(self, event):
        """Handle grid key down event."""

        self.grid_key_down(event)

    def on_grid_select_cell(self, event):
        """Handle grid select cell event."""

        self.grid_select_cell(event)

    def on_row_add_click(self, event):
        """Handle add row click event."""

        self.insert_row()

    def on_row_delete_click(self, event):
        """Handle delete row event."""

        self.delete_row()