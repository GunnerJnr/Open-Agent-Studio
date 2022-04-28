#!/usr/bin/python
from Qt import QtCore, QtGui, QtWidgets

from NodeGraphQt.constants import (NODE_SEL_BORDER_COLOR,
                                   NODE_SEL_COLOR,
                                   PORT_FALLOFF)
from NodeGraphQt.qgraphics.node_base import NodeItem


class GroupNodeItem(NodeItem):
    """
    Group Node item.

    Args:
        name (str): name displayed on the node.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='group', parent=None):
        super(GroupNodeItem, self).__init__(name, parent)

    def paint(self, painter, option, widget):
        """
        Draws the node base not the ports or text.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        self.auto_switch_mode()

        painter.save()
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtCore.Qt.NoPen)

        # base background.
        margin = 6.0
        rect = self.boundingRect()
        rect = QtCore.QRectF(rect.left() + margin,
                             rect.top() + margin,
                             rect.width() - (margin * 2),
                             rect.height() - (margin * 2))

        # draw the base color
        offset = 3.0
        rect_1 = QtCore.QRectF(rect.x() + (offset / 2),
                               rect.y() + offset + 2.0,
                               rect.width(), rect.height())
        rect_2 = QtCore.QRectF(rect.x() - offset,
                               rect.y() - offset,
                               rect.width(), rect.height())
        poly = QtGui.QPolygonF()
        poly.append(rect_1.topRight())
        poly.append(rect_2.topRight())
        poly.append(rect_2.bottomLeft())
        poly.append(rect_1.bottomLeft())

        painter.setBrush(QtGui.QColor(*self.color).darker(180))
        painter.drawRect(rect_1)
        painter.drawPolygon(poly)

        painter.setBrush(QtGui.QColor(*self.color))
        painter.drawRect(rect_2)

        if self.selected:
            border_color = QtGui.QColor(*NODE_SEL_BORDER_COLOR)
            # light overlay on background when selected.
            painter.setBrush(QtGui.QColor(*NODE_SEL_COLOR))
            painter.drawRect(rect_2)
        else:
            border_color = QtGui.QColor(*self.border_color)

        # node name background
        padding = 2.0, 2.0
        text_rect = self._text_item.boundingRect()
        text_rect = QtCore.QRectF(rect_2.left() + padding[0],
                                  rect_2.top() + padding[1],
                                  rect.right() - (padding[0] * 2) - margin,
                                  text_rect.height() - (padding[1] * 2))
        if self.selected:
            painter.setBrush(QtGui.QColor(*NODE_SEL_COLOR))
        else:
            painter.setBrush(QtGui.QColor(0, 0, 0, 80))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(text_rect)

        # draw the outlines.
        pen = QtGui.QPen(border_color.darker(120), 0.8)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawLines([rect_1.topRight(), rect_2.topRight(),
                           rect_1.topRight(), rect_1.bottomRight(),
                           rect_1.bottomRight(), rect_1.bottomLeft(),
                           rect_1.bottomLeft(), rect_2.bottomLeft()])
        painter.drawLine(rect_1.bottomRight(), rect_2.bottomRight())

        pen = QtGui.QPen(border_color, 0.8)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.drawRect(rect_2)

        painter.restore()

    def align_ports(self, v_offset=0.0):
        """
        Align input, output ports in the node layout.

        Args:
            v_offset (float): port vertical offset.
        """
        width = self._width
        txt_offset = PORT_FALLOFF - 2
        spacing = 1

        # adjust input position
        inputs = [p for p in self.inputs if p.isVisible()]
        if inputs:
            port_width = inputs[0].boundingRect().width()
            port_height = inputs[0].boundingRect().height()
            port_x = port_width / 2 * -1
            port_x += 3.0
            port_y = v_offset
            for port in inputs:
                port.setPos(port_x, port_y)
                port_y += port_height + spacing
        # adjust input text position
        for port, text in self._input_items.items():
            if port.isVisible():
                txt_x = port.boundingRect().width() / 2 - txt_offset
                txt_x += 3.0
                text.setPos(txt_x, port.y() - 1.5)

        # adjust output position
        outputs = [p for p in self.outputs if p.isVisible()]
        if outputs:
            port_width = outputs[0].boundingRect().width()
            port_height = outputs[0].boundingRect().height()
            port_x = width - (port_width / 2)
            port_x -= 9.0
            port_y = v_offset
            for port in outputs:
                port.setPos(port_x, port_y)
                port_y += port_height + spacing
        # adjust output text position
        for port, text in self._output_items.items():
            if port.isVisible():
                txt_width = text.boundingRect().width() - txt_offset
                txt_x = port.x() - txt_width
                text.setPos(txt_x, port.y() - 1.5)

    def draw_node(self):
        """
        Re-draw the node item in the scene.
        (re-implemented for vertical layout design)
        """
        height = self._text_item.boundingRect().height()

        # setup initial base size.
        self._set_base_size(add_w=8.0, add_h=height + 10)
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # --- set the initial node layout ---
        # (do all the graphic item layout offsets here)

        # align label text
        self.align_label()
        # arrange icon
        self.align_icon(h_offset=2.0, v_offset=3.0)
        # arrange input and output ports.
        self.align_ports(v_offset=height)
        # arrange node widgets
        self.align_widgets(v_offset=height)

        self.update()


class GroupNodeVerticalItem(NodeItem):
    """
    Vertical Group Node item.

    Args:
        name (str): name displayed on the node.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='group', parent=None):
        super(GroupNodeVerticalItem, self).__init__(name, parent)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.text_item.setFont(font)

    def paint(self, painter, option, widget):
        """
        Draws the node base not the ports or text.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        self.auto_switch_mode()

        painter.save()
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtCore.Qt.NoPen)

        # base background.
        margin = 6.0
        rect = self.boundingRect()
        rect = QtCore.QRectF(rect.left() + margin,
                             rect.top() + margin,
                             rect.width() - (margin * 2),
                             rect.height() - (margin * 2))

        # draw the base color
        offset = 3.0
        rect_1 = QtCore.QRectF(rect.x() + offset,
                               rect.y() + (offset / 2),
                               rect.width(), rect.height())
        rect_2 = QtCore.QRectF(rect.x() - offset,
                               rect.y() - offset,
                               rect.width(), rect.height())
        poly = QtGui.QPolygonF()
        poly.append(rect_1.topRight())
        poly.append(rect_2.topRight())
        poly.append(rect_2.bottomLeft())
        poly.append(rect_1.bottomLeft())

        painter.setBrush(QtGui.QColor(*self.color).dark(180))
        painter.drawRect(rect_1)
        painter.drawPolygon(poly)
        painter.setBrush(QtGui.QColor(*self.color))
        painter.drawRect(rect_2)

        if self.selected:
            border_color = QtGui.QColor(*NODE_SEL_BORDER_COLOR)
            # light overlay on background when selected.
            painter.setBrush(QtGui.QColor(*NODE_SEL_COLOR))
            painter.drawRect(rect_2)
        else:
            border_color = QtGui.QColor(*self.border_color)

        # top & bottom edge background.
        padding = 2.0
        height = 10
        if self.selected:
            painter.setBrush(QtGui.QColor(*NODE_SEL_COLOR))
        else:
            painter.setBrush(QtGui.QColor(0, 0, 0, 80))

        painter.setPen(QtCore.Qt.NoPen)
        for y in [rect_2.top() + padding, rect_2.bottom() - height - padding]:
            top_rect = QtCore.QRectF(rect.x() + padding - offset, y,
                                     rect.width() - (padding * 2), height)
            painter.drawRect(top_rect)

        # draw the outlines.
        pen = QtGui.QPen(border_color.darker(120), 0.8)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawLines([rect_1.topRight(), rect_2.topRight(),
                           rect_1.topRight(), rect_1.bottomRight(),
                           rect_1.bottomRight(), rect_1.bottomLeft(),
                           rect_1.bottomLeft(), rect_2.bottomLeft()])
        painter.drawLine(rect_1.bottomRight(), rect_2.bottomRight())

        pen = QtGui.QPen(border_color, 0.8)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.drawRect(rect_2)

        painter.restore()

    def align_icon(self, h_offset=0.0, v_offset=0.0):
        """
        Align node icon to the default top left of the node.

        Args:
            v_offset (float): vertical offset.
            h_offset (float): horizontal offset.
        """
        y = self._height / 2
        y -= self._icon_item.boundingRect().height()
        self._icon_item.setPos(self._width + h_offset, y + v_offset)

    def align_label(self, h_offset=0.0, v_offset=0.0):
        """
        Center node label text to the top of the node.

        Args:
            v_offset (float): vertical offset.
            h_offset (float): horizontal offset.
        """
        y = self._height / 2
        y -= self.text_item.boundingRect().height() / 2
        self._text_item.setPos(self._width + h_offset, y + v_offset)

    def align_ports(self, v_offset=0.0):
        """
        Align input, output ports in the node layout.

        Args:
            v_offset (float): port vertical offset.
        """
        # adjust input position
        inputs = [p for p in self.inputs if p.isVisible()]
        if inputs:
            port_width = inputs[0].boundingRect().width()
            port_height = inputs[0].boundingRect().height()
            half_width = port_width / 2
            delta = self._width / (len(inputs) + 1)
            port_x = delta
            port_y = -port_height / 2 + 3.0
            for port in inputs:
                port.setPos(port_x - half_width, port_y)
                port_x += delta

        # adjust output position
        outputs = [p for p in self.outputs if p.isVisible()]
        if outputs:
            port_width = outputs[0].boundingRect().width()
            port_height = outputs[0].boundingRect().height()
            half_width = port_width / 2
            delta = self._width / (len(outputs) + 1)
            port_x = delta
            port_y = self._height - (port_height / 2) - 9.0
            for port in outputs:
                port.setPos(port_x - half_width, port_y)
                port_x += delta

    def draw_node(self):
        """
        Re-draw the node item in the scene.
        (re-implemented for vertical layout design)
        """
        height = self._text_item.boundingRect().height()

        # setup initial base size.
        self._set_base_size(add_w=8.0)
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # --- set the initial node layout ---
        # (do all the graphic item layout offsets here)

        # align label text
        self.align_label(h_offset=7, v_offset=6)
        # align icon
        self.align_icon(h_offset=4, v_offset=-2)
        # arrange input and output ports.
        self.align_ports(v_offset=height + (height / 2))
        # arrange node widgets
        self.align_widgets(v_offset=height / 2)

        self.update()

    def add_input(self, name='input', multi_port=False, display_name=True,
                  locked=False, painter_func=None):
        """
        Adds a port qgraphics item into the node with the "port_type" set as
        IN_PORT

        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): (not used).
            locked (bool): locked state.
            painter_func (function): custom paint function.

        Returns:
            PortItem: port qgraphics item.
        """
        return super(GroupNodeVerticalItem, self).add_input(
            name, multi_port, False, locked, painter_func)

    def add_output(self, name='output', multi_port=False, display_name=True,
                   locked=False, painter_func=None):
        """
        Adds a port qgraphics item into the node with the "port_type" set as
        OUT_PORT

        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): (not used).
            locked (bool): locked state.
            painter_func (function): custom paint function.

        Returns:
            PortItem: port qgraphics item.
        """
        return super(GroupNodeVerticalItem, self).add_output(
            name, multi_port, False, locked, painter_func)
