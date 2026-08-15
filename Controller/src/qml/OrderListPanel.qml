import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import TrainView

Item {
    id: root

    property Train train

    implicitHeight: column.implicitHeight
    implicitWidth: 220

    ColumnLayout {
        id: column
        anchors.fill: parent
        spacing: 4
        enabled: root.train !== null

        RowLayout {
            Layout.fillWidth: true
            spacing: 6

            Text {
                text: "Current stop: " + (root.train ? root.train.current_order_index : 0)
                font.bold: true
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
            }

            Text {
                text: root.train && root.train.control_mode === Train.Automatic ? "Auto" : "Manual"
                font.bold: true
            }

            Switch {
                id: modeSwitch
                checked: root.train && root.train.control_mode === Train.Automatic
                onToggled: {
                    if (!root.train)
                        return
                    root.train.control_mode = checked ? Train.Automatic : Train.Manual
                }
            }
        }

        Text {
            visible: root.train && root.train.control_mode === Train.Automatic
            text: root.train && root.train.executor ? root.train.executor.status : ""
            font.pixelSize: 11
            color: palette.mid
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        ListView {
            id: orderView
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(
                160,
                Math.max(40, root.train ? root.train.orders.count * 36 : 40)
            )
            clip: true
            model: root.train ? root.train.orders : null
            spacing: 2

            delegate: RowLayout {
                width: orderView.width
                height: 34
                spacing: 2

                required property var object
                required property int index

                Text {
                    text: root.train && index === root.train.current_order_index ? "\u25B6" : " "
                    Layout.preferredWidth: 14
                }

                Rectangle {
                    property color nodeColor: network && object
                        ? network.color_for_node(object.target_node_id)
                        : "transparent"
                    visible: nodeColor.valid
                    color: nodeColor
                    border.width: 1
                    Layout.preferredWidth: 14
                    Layout.preferredHeight: 14
                }

                Text {
                    text: object ? object.target_node_id : ""
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }

                Text {
                    text: "wait"
                    font.pixelSize: 11
                    color: palette.mid
                }

                SpinBox {
                    id: waitSpin
                    from: 0
                    to: 999
                    editable: true
                    value: object ? Math.round(object.wait_seconds) : 0
                    Layout.preferredWidth: 72
                    ToolTip.visible: hovered
                    ToolTip.text: "Seconds to wait at this stop"
                    textFromValue: function(value, locale) { return value + "s" }
                    valueFromText: function(text, locale) {
                        return parseInt(String(text).replace("s", ""), 10) || 0
                    }
                    onValueModified: {
                        if (root.train)
                            root.train.set_wait(index, value)
                    }
                }

                Button {
                    text: "\u2191"
                    enabled: index > 0
                    Layout.preferredWidth: 28
                    onClicked: {
                        if (root.train)
                            root.train.move_order(index, index - 1)
                    }
                }

                Button {
                    text: "\u2193"
                    enabled: root.train && index < root.train.orders.count - 1
                    Layout.preferredWidth: 28
                    onClicked: {
                        if (root.train)
                            root.train.move_order(index, index + 1)
                    }
                }

                Button {
                    text: "X"
                    Layout.preferredWidth: 28
                    onClicked: {
                        if (root.train)
                            root.train.remove_order(index)
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 4

            // Color swatch outside ComboBox — native Windows style forbids
            // customizing ComboBox/ItemDelegate contentItem.
            Rectangle {
                property color nodeColor: markerPick.currentIndex >= 0 && network
                    ? network.color_for_node(markerPick.currentText)
                    : "transparent"
                visible: markerPick.currentIndex >= 0 && nodeColor.valid
                color: nodeColor
                border.width: 1
                Layout.preferredWidth: 12
                Layout.preferredHeight: 12
            }

            ComboBox {
                id: markerPick
                Layout.fillWidth: true
                model: network ? network.markerNodeIds : []
                enabled: count > 0
                currentIndex: count > 0 ? 0 : -1

                displayText: {
                    if (count === 0)
                        return "No markers"
                    if (currentIndex < 0)
                        return "Select marker…"
                    return currentText
                }

                delegate: ItemDelegate {
                    required property var modelData
                    required property int index
                    width: markerPick.width
                    text: modelData
                    highlighted: markerPick.highlightedIndex === index
                }
            }

            Button {
                text: "Add"
                enabled: root.train && markerPick.currentIndex >= 0 && markerPick.count > 0
                onClicked: {
                    if (root.train)
                        root.train.add_order(markerPick.currentText, 0)
                }
            }

            Button {
                text: "Clear"
                enabled: root.train && root.train.orders.count > 0
                onClicked: {
                    if (root.train)
                        root.train.clear_orders()
                }
            }
        }

        Text {
            visible: trains && trains.last_order_hint.length > 0
            text: trains ? trains.last_order_hint : ""
            font.pixelSize: 11
            color: palette.mid
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        Text {
            visible: !network || network.markerNodeIds.length === 0
            text: "Generate network to list markers"
            font.pixelSize: 11
            color: palette.mid
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
    }
}
